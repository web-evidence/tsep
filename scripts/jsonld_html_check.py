#!/usr/bin/env python3
"""Explicit Node qualification of frozen authored HTML JSON-LD cases. Apache-2.0."""
import argparse
import base64
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from experiments import source_scripts as scripts
from experiments import jsonld_html as workflow
from scripts.source_http_check import fixture


def save(path,value):
    with path.open('x',encoding='utf-8') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')


def request(case):
    return dict(body_base64=base64.b64encode(case['html'].encode('utf-8')).decode(),
                content_types=['text/html; charset=utf-8'],base_iri=case['base_iri'],contexts=case['contexts'])


def graph(observation,mode):
    index=observation['readings'][mode]['processing_index']
    return observation['processing']['documents'][index]['flattened'] if index is not None else None


def projection(reading):
    return [dict(id=scripts.attributes(s).get('id'),type=scripts.attributes(s).get('type'),
        payload=s['payload'],template=bool(s['template_path']),namespace=s['namespace']) for s in reading['scripts']]


def check(node,output_dir):
    output_dir.mkdir(parents=True,exist_ok=False)
    rows=[];replays=[];failures=[]
    for name in ('source-scripts-v1.json','jsonld-html-v1.json','jsonld-html-graphs-v1.json'):
        oracle=fixture(name);save(output_dir/name,oracle)
        for case in oracle['cases']:
            stem=('source-' if name.startswith('source') else 'graph-')+case['id']
            try:
                if name.startswith('source'):
                    raw=case['html'].encode('utf-8');types=['text/html; charset=utf-8']
                    actual=scripts.inventory(raw,content_types=types,node=node)
                    save(output_dir/(stem+'.json'),actual)
                    for mode,reading in actual['readings'].items():
                        value=projection(reading)
                        rows.append(dict(id=stem,mode=mode,expected=case['expected'][mode],actual=value,
                            matches=reading['complete'] and value==case['expected'][mode]))
                    scripts.replay(actual,raw,content_types=types,node=node)
                else:
                    req=request(case);save(output_dir/(stem+'-input.json'),req)
                    actual=workflow.observe(req,node=node);save(output_dir/(stem+'.json'),actual)
                    for mode,reading in actual['readings'].items():
                        value=dict(status=reading['status'],selected_count=reading['selected_count'],flattened=graph(actual,mode))
                        rows.append(dict(id=stem,mode=mode,expected=case['expected'],actual=value,matches=value==case['expected']))
                    workflow.replay(actual,node=node)
                replays.append(dict(id=stem,matches=True))
            except (ValueError,KeyError,TypeError,OSError,RecursionError) as error:
                failure=dict(id=stem,reason=str(error));failures.append(failure);save(output_dir/(stem+'-failure.json'),failure)
    # Declared resource boundaries: failure must clear populations, never imply absence.
    limits=[]
    for name,html in [('depth','<div>'*140+'<script>{}</script>'+'</div>'*140),
        ('nodes','<p>x</p>'*10001),('scripts','<script>{}</script>'*513),
        ('context-elements','<meta name=x>'*513),('parse-errors','\x00'*1002)]:
        try:
            actual=scripts.inventory(('<!doctype html><body>'+html).encode(),content_types=['text/html; charset=utf-8'],node=node)
            save(output_dir/('limit-'+name+'.json'),actual)
            for mode,reading in actual['readings'].items():
                limits.append(dict(id=name,mode=mode,reason=reading.get('reason'),matches=
                    not reading['complete'] and not reading['scripts'] and not reading['context_elements']))
        except (ValueError,KeyError,TypeError,OSError) as error:failures.append(dict(id='limit-'+name,reason=str(error)))
    result=dict(kind='html-jsonld-qualification',synthetic=True,normative_effect='none',
        source_sha256=workflow.identity(),qualification_sha256=scripts.sha(Path(__file__).read_bytes()),
        matched=sum(r['matches'] for r in rows),total=len(rows),expected_total=126,
        replayed=len(replays),expected_replays=63,limit_matched=sum(r['matches'] for r in limits),limit_total=len(limits),expected_limits=10,
        rows=rows,replays=replays,limits=limits,failures=failures,
        scope='34 source inventories, 24 initial and five additional graph scenarios under explicit supplied-base hypotheses; all authored. No browser, full validator, Edikka assessment or TSEP verdict.')
    save(output_dir/'qualification.json',result);return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--node',required=True);parser.add_argument('--output-dir',type=Path,required=True);args=parser.parse_args()
    result=check(args.node,args.output_dir)
    print(json.dumps({k:v for k,v in result.items() if k not in ('source_sha256','rows','replays','limits')}))
    return 0 if not result['failures'] and result['matched']==result['total']==126 and result['replayed']==63 and result['limit_matched']==result['limit_total']==10 else 1


if __name__=='__main__':sys.exit(main())
