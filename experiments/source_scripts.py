#!/usr/bin/env python3
"""Optional attributed source-script inventory; not a browser or TSEP verdict.

Apache-2.0. Static HTML is parsed under two separate scripting hypotheses.
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from experiments import source_http as http
from experiments import source_tree as shared

need,sha=shared.need,shared.sha
HTML='http://www.w3.org/1999/xhtml'
BOUNDS=dict(source_bytes=8388608,tree_nodes=20000,tree_depth=128,parse_errors=1000,
            scripts=512,context_elements=512,payload_parts=20000,payload_bytes=8388608)
MAX_OUTPUT=http.MAX_OUTPUT


def identity(root=ROOT):
    need(Path(http.__file__).resolve()==ROOT/'experiments/source_http.py','Foreign decoding supervisor')
    return dict(http.identity(root),**{p:sha((root/p).read_bytes()) for p in
        ('experiments/source_scripts.py','experiments/source_scripts.mjs')})


def attributes(record):
    return {a['name']:a['value'] for a in record['attributes'] if a['namespace'] is None}


def validate_and_attribute(result,source,raw,decoding):
    """Validate bounds and byte bindings. Actual replay is needed to check extraction."""
    need(type(result) is dict and result.get('kind')=='unapplied-source-scripts'
        and result.get('version')=='1' and result.get('normative_effect')=='none','Unexpected script reader')
    need(result.get('bounds')==BOUNDS and result.get('parser')==
         dict(name='parse5',version='8.0.1',dependency='entities@8.0.0'),'Reader bounds or parser differ')
    need(result['runtime']['node'].startswith('v24.'),'Unqualified runtime')
    need(result['parser_input_utf8_sha256']==decoding['parser_input_utf8_sha256'],'Input binding differs')
    need(type(result['readings']) is dict and set(result['readings'])=={'enabled','disabled'},'Missing reading')
    locations=[];error_locations=[]
    for reading in result['readings'].values():
        need(type(reading['complete']) is bool and type(reading['visited_nodes']) is int
            and 0<=reading['visited_nodes']<=BOUNDS['tree_nodes'],'Malformed traversal')
        need(reading['document_mode'] in ('no-quirks','quirks','limited-quirks') or
            (not reading['complete'] and reading['document_mode'] is None),'Malformed document mode')
        for key,limit in [('scripts',BOUNDS['scripts']),('context_elements',BOUNDS['context_elements']),('parse_errors',BOUNDS['parse_errors'])]:
            need(type(reading[key]) is list and len(reading[key])<=limit,'Population bound exceeded')
        if not reading['complete']:
            need(not reading['scripts'] and not reading['context_elements'] and
                 type(reading.get('reason')) is str and reading['reason'],'Incomplete inventory retained or unexplained')
        seen=set();parts=0;payload_bytes=0
        for group in ('scripts','context_elements'):
            previous=-1
            for record in reading[group]:
                ident=record['node_id']
                need(type(ident) is int and previous<ident<reading['visited_nodes'] and ident not in seen,'Element order or identity differs')
                previous=ident;seen.add(ident)
                need(type(record['namespace']) is str and bool(record['namespace']),'Missing namespace')
                need(record['name']=='script' if group=='scripts' else
                     record['namespace']==HTML and record['name'] in ('base','meta'),'Unexpected element')
                ancestors=record['ancestors'];need(type(ancestors) is list and len(ancestors)<=BOUNDS['tree_depth'],'Ancestor bound exceeded')
                previous_ancestor=-1
                for ancestor in ancestors:
                    a=ancestor['node_id']
                    need(type(a) is int and previous_ancestor<a<ident and type(ancestor['name']) is str
                        and type(ancestor['namespace']) is str,'Malformed ancestry');previous_ancestor=a
                templates=record['template_path']
                need(type(templates) is list and templates==[a['node_id'] for a in ancestors
                    if a['namespace']==HTML and a['name']=='template'],'Template path differs')
                attrs=record['attributes'];need(type(attrs) is list and len(attrs)<=20000,'Attribute bound exceeded')
                keys=set()
                for a in attrs:
                    need(type(a) is dict and set(a)=={'name','namespace','prefix','value'} and type(a['name']) is str and a['name']
                        and type(a['value']) is str and all(a[k] is None or type(a[k]) is str for k in ('namespace','prefix')),'Malformed attribute')
                    key=(a['namespace'],a['name']);need(key not in keys,'Duplicate parsed attribute');keys.add(key)
                locations.extend(r for r in (record['start_tag'],record['end_tag']) if r is not None)
                if group=='scripts':
                    runs=record['payload_parts'];need(type(runs) is list,'Malformed payload parts');parts+=len(runs)
                    need(parts<=BOUNDS['payload_parts'],'Payload part bound exceeded')
                    last=ident
                    for run in runs:
                        need(type(run['node_id']) is int and last<run['node_id']<reading['visited_nodes']
                            and type(run['data']) is str,'Malformed payload text');last=run['node_id']
                        payload_bytes+=len(run['data'].encode('utf-8'))
                        need(payload_bytes<=BOUNDS['payload_bytes'],'Payload byte bound exceeded')
                        if run['location'] is not None:locations.append(run['location'])
                    need(record['payload']==''.join(r['data'] for r in runs),'Payload differs from text parts')
        for error in reading['parse_errors']:
            need(type(error) is dict and type(error.get('code')) is str,'Malformed parse error')
            a,b=error.get('startOffset'),error.get('endOffset')
            if type(a) is int and type(b) is int and 0<=a<=b:error_locations.append(error)
            else:error['body_span_bytes']=None
    for loc in locations:
        span=loc['source_span_utf16']
        need(type(span) is list and len(span)==2 and all(type(i) is int for i in span)
            and 0<=span[0]<span[1] and type(loc['raw_source']) is str,'Malformed location')
    positions={i for loc in locations for i in loc['source_span_utf16']}
    positions.update(i for e in error_locations for i in (e['startOffset'],e['endOffset']))
    mapped=http.byte_positions(source,decoding['consumed_bom_bytes'],positions)
    for loc in locations:
        a,b=[mapped[i] for i in loc['source_span_utf16']]
        need(raw[a:b].decode('utf-8')==loc['raw_source'],'Raw source differs from original bytes')
        if 'body_span_bytes' in loc:need(loc['body_span_bytes']==[a,b],'Stored byte position differs')
        loc['body_span_bytes']=[a,b]
    for error in error_locations:
        span=[mapped[error['startOffset']],mapped[error['endOffset']]]
        if 'body_span_bytes' in error:need(error['body_span_bytes']==span,'Stored error position differs')
        error['body_span_bytes']=span


def inventory(raw,*,content_types,node,root=ROOT):
    source,decoding=http.decode(raw,content_types)
    executable=shutil.which(node);need(executable is not None,'Optional Node 24 unavailable; no fallback')
    before=identity(root);packages=shared.packages(root)
    with tempfile.TemporaryDirectory(prefix='tsep-source-scripts-') as folder:
        work=Path(folder).resolve()
        for name,files in packages.items():
            for relative,data in files.items():
                dest=work/'node_modules'/name/relative;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
        for name in ('source_scripts.mjs','source_tree_network_guard.mjs'):(work/name).write_bytes((root/'experiments'/name).read_bytes())
        (work/'source.bin').write_bytes(source.encode('utf-8'))
        command=[executable,'--max-old-space-size=128','--no-addons','--disable-proto=throw',
            '--disallow-code-generation-from-strings','--permission','--allow-fs-read='+str(work),str(work/'source_scripts.mjs')]
        env={k:v for k,v in os.environ.items() if not k.startswith('NODE_')}
        with (work/'stdout').open('wb') as out,(work/'stderr').open('wb') as err:
            try:run=subprocess.run(command,cwd=work,env=env,stdin=subprocess.DEVNULL,stdout=out,stderr=err,timeout=http.TIMEOUT)
            except subprocess.TimeoutExpired as error:raise ValueError('Script inventory exceeded 30-second deadline') from error
        with (work/'stderr').open('rb') as f:error=f.read(4096).decode('utf-8',errors='replace')
        need(run.returncode==0,'Script worker failed: '+error)
        with (work/'stdout').open('rb') as f:output=f.read(MAX_OUTPUT+1)
        need(len(output)<=MAX_OUTPUT,'Inventory output bound exceeded');result=json.loads(output)
    need(identity(root)==before,'Script reader sources changed during execution')
    validate_and_attribute(result,source,raw,decoding)
    result.update(decoding=decoding,source_sha256=before,supervisor=dict(python=sys.version.split()[0],
        process_timeout_seconds=http.TIMEOUT,node_old_space_mib=128,output_byte_limit=MAX_OUTPUT),
        limitations=['Two static HTML hypotheses; no source JavaScript, browser, CSS visibility or search-engine reading.',
            'Template fragments and foreign scripts are inventoried separately; no shadow attachment or frame document extraction.',
            'Original bytes, parser text and locations are distinct; text normalization is not repaired or hidden.',
            'Source completeness and actual HTTP/navigation provenance must be established by separate capture evidence.',
            'Inventory only; no JSON-LD selection, graph, vocabulary validation or TSEP verdict.'])
    need(len(json.dumps(result,ensure_ascii=False).encode())<=MAX_OUTPUT,'Attributed inventory output bound exceeded')
    return result


def replay(observation,raw,*,content_types,node,root=ROOT):
    need(observation.get('source_sha256')==identity(root),'Retained reader sources differ')
    actual=inventory(raw,content_types=content_types,node=node,root=root)
    need(actual==observation,'Recomputed script inventory differs');return actual


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('body',type=Path);parser.add_argument('--content-type',action='append',required=True)
    parser.add_argument('--node',required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    try:
        need(not args.output.exists() and not args.output.is_symlink(),'Choose a new output path')
        with args.body.open('rb') as f:raw=f.read(http.MAX_BYTES+1)
        result=inventory(raw,content_types=args.content_type,node=args.node)
        with args.output.open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
        print(json.dumps({m:dict(complete=r['complete'],scripts=len(r['scripts'])) for m,r in result['readings'].items()}));return 0
    except (ValueError,KeyError,TypeError,OSError,RecursionError) as error:
        print(json.dumps(dict(kind='source-scripts-unavailable',reason=str(error),normative_effect='none')),file=sys.stderr);return 64


if __name__=='__main__':sys.exit(main())
