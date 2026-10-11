#!/usr/bin/env python3
"""Explicit Node qualification of authored content cases, no TS44 outcome. Apache-2.0."""
import argparse
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from experiments import source_content as reader
from scripts.source_http_check import fixture


def check(node, output_dir):
    output_dir.mkdir(parents=True,exist_ok=False)
    oracle=fixture('source-content-v1.json'); rows=[]; runtimes=[]
    for case in oracle['cases']:
        result=reader.inventory(case['html'].encode('utf-8'),content_types=['text/html; charset=utf-8'],ids=case['ids'],node=node)
        if result['runtime'] not in runtimes:runtimes.append(result['runtime'])
        (output_dir/(case['id']+'.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
        for mode,reading in result['readings'].items():
            actual=reading['selections']
            errors=sorted({e['code'] for e in reading['parse_errors']})
            rows.append(dict(id=case['id'],mode=mode,expected=case['expected'][mode],actual=actual,
                             parse_errors=errors,required_parse_errors=case['required_parse_errors'],
                             matches=reading['complete'] and actual==case['expected'][mode] and
                             set(case['required_parse_errors'])<=set(errors)))
    # Adversarial resource limits are observed separately, never ordinary absence.
    limits=[]
    for name,body in [('depth','<div>'*140+'<p id="critical">x</p>'+'</div>'*140),
                      ('node-count','<p>x</p>'*10001),('parse-errors','\x00'*1002)]:
        result=reader.inventory(('<!doctype html><body>'+body).encode(),content_types=['text/html; charset=utf-8'],ids=['critical'],node=node)
        (output_dir/(name+'.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
        for mode,reading in result['readings'].items():
            limits.append(dict(id=name,mode=mode,complete=reading['complete'],reason=reading.get('reason'),
                               matches=not reading['complete'] and reading['nodes']==[] and reading['selections'] is None))
    return dict(kind='source-content-qualification',synthetic=True,normative_effect='none',
                source_sha256=reader.identity(),oracle_sha256=reader.sha((ROOT/'tests/fixtures/source-content-v1.json').read_bytes()),
                qualification_script_sha256=reader.sha(Path(__file__).read_bytes()),runtimes=runtimes,
                matched=sum(r['matches'] for r in rows),total=len(rows),rows=rows,
                limit_matched=sum(r['matches'] for r in limits),limit_total=len(limits),limit_rows=limits,
                scope='Authored structural expectations and bounded failure cases. Node parser invoked; no scripts, browser, network capture, semantic review, agent visit or TS44 verdict.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--node',required=True);parser.add_argument('--output-dir',type=Path,required=True);args=parser.parse_args()
    result=check(args.node,args.output_dir)
    (args.output_dir/'qualification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('rows','limit_rows','source_sha256')}))
    return 0 if result['matched']==result['total'] and result['limit_matched']==result['limit_total'] else 1


if __name__=='__main__':sys.exit(main())
