#!/usr/bin/env python3
"""Static content observation for TS44 development; no normative outcome. Apache-2.0."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from experiments import source_http as http
from experiments import source_tree as shared

need, sha = shared.need, shared.sha
HTML = 'http://www.w3.org/1999/xhtml'
MAX_OUTPUT, TIMEOUT = http.MAX_OUTPUT, http.TIMEOUT
BOUNDS = dict(source_bytes=8*1024*1024, tree_nodes=20000, tree_depth=128, parse_errors=1000)
EXCLUDED = {'head', 'template', 'script', 'style', 'foreign', 'frame'}


def identity(root=ROOT):
    need(Path(http.__file__).resolve() == ROOT/'experiments/source_http.py', 'Foreign HTTP supervisor')
    return dict(http.identity(root), **{name: sha((root/name).read_bytes()) for name in
                ('experiments/source_content.py', 'experiments/source_content.mjs')})


def selectors(ids):
    need(type(ids) is list and 1 <= len(ids) <= 64 and
         all(type(s) is str and s and len(s) <= 128 and not any(c in s for c in '\x00\t\n\r\f ') for s in ids),
         'Expected 1–64 literal nonblank IDs, each at most 128 characters')
    need(len(set(ids)) == len(ids), 'Duplicate requested ID')


def attributes(node):
    return {a['name']: a['value'] for a in node['attributes'] if a['namespace'] is None}


def contexts(nodes):
    paths, flags = [], []
    for node in nodes:
        parent = node['parent']
        path = paths[parent]+[node['id']] if parent is not None else [node['id']]
        context = set(flags[parent]) if parent is not None else set()
        if node['kind'] == 'element':
            attrs = attributes(node)
            if node['namespace'] != HTML: context.add('foreign')
            else:
                tag = node['name']
                if tag in ('body', 'head', 'script', 'style', 'noscript', 'details', 'dialog'):
                    context.add(tag)
                if tag == 'template': context.add('template')
                if tag in ('iframe', 'frame', 'frameset'): context.add('frame')
                for attr in ('hidden', 'inert'):
                    if attr in attrs: context.add(attr)
                if attrs.get('aria-hidden', '').lower() == 'true': context.add('aria-hidden')
                if 'style' in attrs: context.add('inline-style')
                if tag == 'template' and 'shadowrootmode' in attrs: context.add('shadow-declaration')
        paths.append(path); flags.append(sorted(context))
    return paths, flags


def projection(reading, ids):
    """Structural selection, never a truth, visibility, or availability test."""
    if not reading['complete']: return None
    nodes = reading['nodes']; paths, flags = contexts(nodes)
    selected = {key: [] for key in ids}; matches={}
    for node in nodes:
        key = attributes(node).get('id') if node['kind'] == 'element' else None
        if key not in selected: continue
        need(len(matches)<512,'Selected match bound exceeded')
        record=dict(name=node['name'],namespace=node['namespace'],context=flags[node['id']],
                    ordinary_text='',flagged_runs=[],excluded_text=[],links=[])
        selected[key].append(record); matches[node['id']]=(record,[])
    # One pass over bounded ancestry, not one whole-tree scan per duplicate ID.
    # Aggregate projection text is bounded independently of the source and tree.
    characters=0; records=0
    for child in nodes:
        context=flags[child['id']]; attrs=attributes(child)
        for ancestor in paths[child['id']]:
            if ancestor not in matches: continue
            record,text=matches[ancestor]
            if child['kind']=='text':
                records+=1; need(records<=50000,'Selected record bound exceeded')
                characters+=len(child['data'])
                need(characters<=2*1024*1024,'Selected text bound exceeded')
                run={'data':child['data'],'context':context}
                if EXCLUDED.intersection(context) or 'body' not in context: record['excluded_text'].append(run)
                else:
                    text.append(child['data'])
                    if set(context)-{'body'}: record['flagged_runs'].append(run)
            if child['kind']=='element' and child['name'] in ('a','link','area') and 'href' in attrs:
                records+=1; need(records<=50000,'Selected record bound exceeded')
                characters+=len(attrs['href'])
                need(characters<=2*1024*1024,'Selected text bound exceeded')
                record['links'].append(dict(name=child['name'],namespace=child['namespace'],href=attrs['href'],context=context))
    for record,text in matches.values():record['ordinary_text']=''.join(text)
    return selected


def validate_and_attribute(result, source, raw, decoding, ids):
    selectors(ids)
    need(result.get('kind') == 'unapplied-source-content-tree' and result.get('experiment_version') == '1' and
         result.get('normative_effect') == 'none' and result.get('bounds') == BOUNDS, 'Unexpected reader identity or bounds')
    need(result.get('parser') == {'name':'parse5','version':'8.0.1','dependency':'entities@8.0.0'}, 'Unexpected parser')
    need(result.get('parser_input_utf8_sha256') == decoding['parser_input_utf8_sha256'], 'Parser input identity differs')
    need(type(result.get('readings')) is dict and set(result['readings']) == {'enabled','disabled'}, 'Missing hypothesis')
    located, errors = [], []
    for reading in result['readings'].values():
        need(type(reading['complete']) is bool and type(reading['nodes']) is list and
             len(reading['nodes']) <= BOUNDS['tree_nodes'], 'Malformed bounded reading')
        need(reading['document_mode'] in ('no-quirks','limited-quirks','quirks') or
             (not reading['complete'] and reading['document_mode'] is None), 'Unknown document mode')
        need(type(reading['parse_errors']) is list and len(reading['parse_errors']) <= BOUNDS['parse_errors'], 'Parse error bound exceeded')
        if not reading['complete']:
            need(not reading['nodes'] and type(reading.get('reason')) is str and reading['reason'], 'Partial tree retained or unexplained')
        else:
            nodes=reading['nodes']; need(bool(nodes), 'Missing tree')
            children=[[] for _ in nodes]; fragments=[[] for _ in nodes]; paths=[]
            for i,n in enumerate(nodes):
                need(type(n['id']) is int and n['id']==i, 'Node order differs')
                p=n['parent']
                if i==0:
                    need(p is None and n['kind']=='document' and n['edge']=='root' and type(n['index']) is int and n['index']==0, 'Missing document root')
                    paths.append([i])
                else:
                    need(type(p) is int and 0<=p<i and n['edge'] in ('child','template-content'), 'Invalid parent/edge')
                    paths.append(paths[p]+[i]); need(len(paths[i])-1<=BOUNDS['tree_depth'], 'Tree depth bound exceeded')
                    need(nodes[p]['kind'] in ('document','element','fragment'), 'Leaf has children')
                    (children if n['edge']=='child' else fragments)[p].append(i)
                need(n['kind'] in ('document','doctype','fragment','element','text','comment') and
                     type(n['name']) is str and n['name'], 'Invalid node kind/name')
                if n['kind']=='element': need(type(n['namespace']) is str and n['namespace'], 'Missing element namespace')
                else:
                    need(n['namespace'] is None and not n['attributes'], 'Non-element attributes or namespace')
                    need(n['name']=={'document':'#document','doctype':'#documentType','fragment':'#document-fragment','text':'#text','comment':'#comment'}[n['kind']], 'Node kind/name mismatch')
                    need(n['kind']!='document' or i==0, 'Nested document')
                need(type(n['attributes']) is list and len(n['attributes']) <= 20000, 'Malformed attributes')
                seen=set()
                for a in n['attributes']:
                    need(set(a)=={'name','namespace','prefix','value'} and type(a['name']) is str and a['name'] and
                         type(a['value']) is str and all(a[k] is None or type(a[k]) is str for k in ('namespace','prefix')), 'Malformed attribute')
                    key=(a['namespace'],a['name']); need(key not in seen,'Duplicate parsed attribute'); seen.add(key)
                need(type(n['data']) is str if n['kind'] in ('text','comment') else n['data'] is None, 'Malformed node data')
                need(type(n['child_count']) is int and 0<=n['child_count']<=BOUNDS['tree_nodes'] and
                     type(n['template_content']) is bool, 'Malformed child count')
                span=n['source_span_utf16']
                if span is None:
                    need(n['raw_source'] is None, 'Missing location has invented source'); n['body_span_bytes']=None
                else:
                    need(type(span) is list and len(span)==2 and all(type(v) is int for v in span) and
                         0<=span[0]<span[1] and type(n['raw_source']) is str, 'Malformed source interval')
                    located.append(n)
            for i,n in enumerate(nodes):
                need(len(children[i])==n['child_count'] and [nodes[c]['index'] for c in children[i]]==list(range(n['child_count'])) and
                     all(type(nodes[c]['index']) is int for c in children[i]), 'Incomplete or misordered children')
                if n['template_content']:
                    need(n['kind']=='element' and n['namespace']==HTML and n['name']=='template' and
                         not children[i] and len(fragments[i])==1, 'Malformed template content')
                    frag=nodes[fragments[i][0]]
                    need(frag['kind']=='fragment' and type(frag['index']) is int and frag['index']==0, 'Invalid template fragment')
                else: need(not fragments[i], 'Undeclared template fragment')
                if n['kind']=='fragment': need(n['edge']=='template-content', 'Unexpected document fragment')
            # Require actual depth-first tree order, not just earlier parents.
            order=[]; stack=[0]
            while stack:
                i=stack.pop();order.append(i)
                stack.extend(reversed(children[i]+fragments[i]))
            need(order==list(range(len(nodes))), 'Non-preorder tree')
        for error in reading['parse_errors']:
            need(type(error) is dict and type(error.get('code')) is str, 'Malformed parse error')
            a,b=error.get('startOffset'),error.get('endOffset')
            if type(a) is int and type(b) is int and 0<=a<=b: errors.append(error)
            else: error['body_span_bytes']=None
    positions={p for n in located for p in n['source_span_utf16']}
    positions.update(p for e in errors for p in (e['startOffset'],e['endOffset']))
    mapped=http.byte_positions(source,decoding['consumed_bom_bytes'],positions)
    for n in located:
        a,b=[mapped[p] for p in n['source_span_utf16']]
        need(raw[a:b].decode('utf-8')==n['raw_source'], 'Located source differs from original body bytes')
        n['body_span_bytes']=[a,b]
    for e in errors:e['body_span_bytes']=[mapped[e['startOffset']],mapped[e['endOffset']]]
    for reading in result['readings'].values():
        selected=projection(reading,ids)
        if 'selections' in reading: need(reading['selections']==selected, 'Stored selection differs from tree')
        reading['selections']=selected


def inventory(raw, *, content_types, ids, node=None, root=ROOT):
    selectors(ids)
    source,decoding=http.decode(raw,content_types)
    node=shutil.which(node or 'node')
    need(node is not None,'Optional Node 24 runtime unavailable; no fallback reader')
    before=identity(root); dependencies=shared.packages(root)
    with tempfile.TemporaryDirectory(prefix='tsep-source-content-') as folder:
        work=Path(folder).resolve()
        for name,files in dependencies.items():
            for relative,data in files.items():
                destination=work/'node_modules'/name/relative
                destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(data)
        for name in ('source_content.mjs','source_tree_network_guard.mjs'):
            (work/name).write_bytes((root/'experiments'/name).read_bytes())
        (work/'source.bin').write_bytes(source.encode('utf-8'))
        command=[node,'--max-old-space-size=128','--no-addons','--disable-proto=throw',
                 '--disallow-code-generation-from-strings','--permission','--allow-fs-read='+str(work),str(work/'source_content.mjs')]
        env={k:v for k,v in os.environ.items() if not k.startswith('NODE_')}
        with (work/'stdout').open('wb') as out,(work/'stderr').open('wb') as err:
            try:
                completed=subprocess.run(command,cwd=work,env=env,stdin=subprocess.DEVNULL,stdout=out,stderr=err,timeout=TIMEOUT)
            except subprocess.TimeoutExpired as error: raise ValueError('Content reader exceeded 30-second process deadline') from error
        with (work/'stderr').open('rb') as handle:error_text=handle.read(4096).decode('utf-8',errors='replace')
        need(completed.returncode==0,'Content reader failed: '+error_text)
        with (work/'stdout').open('rb') as handle:output=handle.read(MAX_OUTPUT+1)
        need(len(output)<=MAX_OUTPUT,'Source result byte bound exceeded')
        result=json.loads(output)
    need(identity(root)==before,'Reader files changed during execution')
    validate_and_attribute(result,source,raw,decoding,ids)
    result.update(decoding=decoding,requested_ids=ids,source_sha256=before,
                  supervisor=dict(python_version=sys.version.split()[0],process_timeout_seconds=TIMEOUT,
                                  node_old_space_mib=128,output_byte_limit=MAX_OUTPUT))
    need(len(json.dumps(result,ensure_ascii=False).encode('utf-8'))<=MAX_OUTPUT,'Attributed result byte bound exceeded')
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('body',type=Path);parser.add_argument('--content-type',action='append',required=True)
    parser.add_argument('--id',action='append',required=True,dest='ids');parser.add_argument('--node',required=True)
    parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    try:
        need(not args.output.exists(),'Output already exists')
        with args.body.open('rb') as handle:raw=handle.read(http.MAX_BYTES+1)
        result=inventory(raw,content_types=args.content_type,ids=args.ids,node=args.node)
        with args.output.open('x',encoding='utf-8') as handle:json.dump(result,handle,ensure_ascii=False,indent=2);handle.write('\n')
        print(json.dumps({'normative_effect':'none','readings':{m:{'complete':r['complete'],'selections':r['selections']} for m,r in result['readings'].items()}},ensure_ascii=False))
    except (ValueError,KeyError,TypeError,OSError) as error:
        print(json.dumps({'kind':'content-observation-unavailable','reason':str(error),'normative_effect':'none'}),file=sys.stderr);return 64
    return 0


if __name__=='__main__':sys.exit(main())
