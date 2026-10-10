#!/usr/bin/env python3
"""Optional attributed link-element facts, independent of active TSEP decisions."""
import argparse,json,os,re,shutil,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from experiments import source_http as http,source_tree as shared
HTML='http://www.w3.org/1999/xhtml';SVG='http://www.w3.org/2000/svg';XLINK='http://www.w3.org/1999/xlink'
need,sha=shared.need,shared.sha
SELECTED={'a','area','link','base','form'}
MAX_OUTPUT=32*1024*1024
TIMEOUT=30

def identity(root=ROOT):
    return dict(http.identity(root),**{n:sha((root/n).read_bytes()) for n in
        ('experiments/link_elements.py','experiments/link_elements.mjs')})

def attribute(record,name,namespace=None):
    return next((a['value'] for a in record['attributes'] if a['local_name']==name and a['namespace']==namespace),None)

def classification(record):
    ns,tag=record['namespace'],record['tag']
    if ns==HTML:
        kind='html-'+tag if tag in SELECTED else 'html-form-override'
    elif ns==SVG and tag=='a':kind='svg-a'
    else:kind='foreign-'+tag
    rel=attribute(record,'rel') or ''
    lower=rel.translate(str.maketrans('ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'))
    return {'id':attribute(record,'id'),'kind':kind,'href':attribute(record,'href'),
        'xlink_href':attribute(record,'href',XLINK),'template_depth':len(record['template_indices']),
        'foreign_ancestry':any(ns not in (None,HTML) for ns in record['ancestor_namespaces']),
        'rel_tokens':[v for v in re.split(r'[\t\n\f\r ]+',lower) if v]}

def validate_and_attribute(result,source,raw,decoding):
    need(result.get('kind')=='unapplied-link-elements' and result.get('version')=='1'
         and result.get('normative_effect')=='none','Unexpected element observer identity')
    need(result.get('parser_input_utf8_sha256')==decoding['parser_input_utf8_sha256'],'Source binding mismatch')
    need(set(result['readings'])=={'enabled','disabled'},'Missing source alternative')
    located=[];encoded=source.encode('utf-16-le')
    for reading in result['readings'].values():
        need(type(reading['complete']) is bool and type(reading['records']) is list
             and type(reading['templates']) is list,'Malformed element inventory')
        need(type(reading['tree_nodes']) is int and 0<=reading['tree_nodes']<=200001,'Tree count bound')
        need(type(reading['parse_errors']) is list and len(reading['parse_errors'])<=1000,'Parse error bound')
        if not reading['complete']:need(not reading['records'] and not reading['templates'],'Partial element records forbidden')
        allrows=reading['records']+reading['templates'];need(len(allrows)<=50000,'Record bound')
        seen=set()
        for is_template,rows in ((False,reading['records']),(True,reading['templates'])):
            previous=-1
            for r in rows:
                need(type(r['node_index']) is int and previous<r['node_index']<reading['tree_nodes']
                     and r['node_index'] not in seen,'Invalid element tree order')
                previous=r['node_index'];seen.add(r['node_index'])
                need(type(r['tag']) is str and type(r['namespace']) is str,'Invalid element identity')
                if is_template:need(r['tag']=='template' and r['namespace']==HTML,'Foreign template container')
                else:need(r['tag'] in SELECTED or (r['namespace']==HTML and r['tag'] in ('button','input')),'Unexpected inventoried element')
                need(type(r['attributes']) is list,'Malformed element attributes');keys=set()
                for a in r['attributes']:
                    need(set(a)=={'local_name','prefix','namespace','value'} and type(a['local_name']) is str
                         and bool(a['local_name']) and type(a['value']) is str
                         and (a['prefix'] is None or type(a['prefix']) is str)
                         and (a['namespace'] is None or type(a['namespace']) is str),'Malformed namespaced attribute')
                    key=(a['namespace'],a['local_name']);need(key not in keys,'Duplicate parsed attribute');keys.add(key)
                if not is_template and r['tag'] not in SELECTED:
                    need(attribute(r,'formaction') is not None,'Form override without formaction')
                need(type(r['ancestors']) is list and type(r['ancestor_namespaces']) is list
                     and len(r['ancestors'])==len(r['ancestor_namespaces'])<=256,'Invalid ancestor path')
                need(all(type(a) is str for a in r['ancestors']) and all(n is None or type(n) is str for n in r['ancestor_namespaces']), 'Malformed namespace ancestry')
                need(r['context'] in ('head','body','template','other'),'Unknown source context')
                indices=r['template_indices'];need(type(indices) is list and all(type(i) is int and 0<=i<len(reading['templates']) for i in indices),'Bad template path')
                need((r['context']=='template')==bool(indices),'Template context/path mismatch')
                need(len(set(indices))==len(indices),'Repeated template nesting')
                for level,i in enumerate(indices):
                    t=reading['templates'][i];need(t['template_index']==i and t['node_index']<r['node_index']
                        and t['template_indices']==indices[:level],'Unbound template ancestry')
                span=r['source_span_utf16']
                if span is None:need(r['raw_tag'] is None,'Raw tag without location');r['body_span_bytes']=None
                else:
                    need(type(span) is list and len(span)==2 and all(type(v) is int for v in span)
                         and 0<=span[0]<=span[1]<=len(encoded)//2,'Invalid source span')
                    need(encoded[2*span[0]:2*span[1]].decode('utf-16-le')==r['raw_tag'],'Source tag mismatch');located.append(r)
        for i,t in enumerate(reading['templates']):need(t['template_index']==i,'Invalid template index')
    positions=http.byte_positions(source,decoding['consumed_bom_bytes'],{p for r in located for p in r['source_span_utf16']})
    for r in located:
        a,b=[positions[p] for p in r['source_span_utf16']];need(raw[a:b].decode('utf-8')==r['raw_tag'],'Original bytes mismatch');r['body_span_bytes']=[a,b]

def inventory(raw,*,content_types,node=None,root=ROOT):
    source,decoding=http.decode(raw,content_types);before=identity(root)
    selected=shutil.which(node or 'node');need(selected is not None,'Optional Node24 unavailable; no fallback')
    dependencies=shared.packages(root)
    with tempfile.TemporaryDirectory(prefix='tsep-link-elements-') as folder:
        work=Path(folder).resolve()
        for name,files in dependencies.items():
            for relative,data in files.items():
                dest=work/'node_modules'/name/relative;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
        for name in ('link_elements.mjs','source_tree_network_guard.mjs'):(work/name).write_bytes((root/'experiments'/name).read_bytes())
        (work/'source.bin').write_bytes(source.encode('utf-8'))
        env={k:v for k,v in os.environ.items() if not k.startswith('NODE_')}
        command=[selected,'--max-old-space-size=128','--no-addons','--disable-proto=throw','--disallow-code-generation-from-strings',
            '--permission','--allow-fs-read='+str(work),str(work/'link_elements.mjs')]
        with (work/'stdout').open('wb') as out,(work/'stderr').open('wb') as err:
            try:r=subprocess.run(command,cwd=work,env=env,stdin=subprocess.DEVNULL,stdout=out,stderr=err,timeout=TIMEOUT)
            except subprocess.TimeoutExpired as error:raise ValueError('Element worker exceeded 30-second deadline') from error
        with (work/'stderr').open('rb') as f:errors=f.read(4096).decode('utf-8',errors='replace')
        need(r.returncode==0,'Element worker failed: '+errors)
        with (work/'stdout').open('rb') as f:output=f.read(MAX_OUTPUT+1)
        need(len(output)<=MAX_OUTPUT,'Element output byte bound exceeded');result=json.loads(output)
    need(identity(root)==before,'Element tools changed during calculation')
    validate_and_attribute(result,source,raw,decoding)
    for reading in result['readings'].values():
        reading['classification']=[classification(r) for r in reading['records']]
    result['decoding']=decoding;result['source_sha256']=before
    result['supervisor']={'python':sys.version.split()[0],'deadline_seconds':TIMEOUT,'old_space_mib':128,'output_byte_limit':MAX_OUTPUT}
    need(len(json.dumps(result,ensure_ascii=False,indent=2).encode())<=MAX_OUTPUT,'Formatted element output bound exceeded')
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('body',type=Path);p.add_argument('--content-type',required=True,action='append')
    p.add_argument('--node',required=True);p.add_argument('--output',required=True,type=Path);a=p.parse_args()
    need(not a.output.exists(),'Choose a new output')
    with a.body.open('rb') as f:raw=f.read(http.MAX_BYTES+1)
    r=inventory(raw,content_types=a.content_type,node=a.node)
    with a.output.open('x') as f:json.dump(r,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'normative_effect':'none','counts':{m:len(v['records']) for m,v in r['readings'].items()}}))
if __name__=='__main__':main()
