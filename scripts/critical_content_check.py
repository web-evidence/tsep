#!/usr/bin/env python3
"""Explicit Node qualification for TS44 frozen raw inputs. Apache-2.0."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from conformance.evaluate import evaluate
from adapters.captures import source_files
from provenance.runtime import runtime_identity


def check(node,output):
    output.mkdir(parents=True,exist_ok=False);os.environ['TSEP_SOURCE_NODE']=node
    rows=[];fixtures={};before=source_files();runtime=runtime_identity()
    for name in ('critical-content-v1.json','critical-content-boundaries-v1.json'):
        path=ROOT/'tests/fixtures'/name;raw=path.read_bytes();digest=hashlib.sha256(raw).hexdigest()
        if digest!=path.with_suffix('.sha256').read_text().strip():raise ValueError('Changed frozen fixture '+name)
        fixtures[name]=digest
        for case in json.loads(raw)['cases']:
            notes=[];actual=evaluate(case['input'],source_observations=notes)
            expected=[{k:r[k] for k in ('rule_id','target','outcome')} for r in case['expected']]
            projected=[{k:r[k] for k in ('rule_id','target','outcome')} for r in actual]
            (output/(case['id']+'.json')).write_text(json.dumps({'actual':actual,'observations':notes},ensure_ascii=False,indent=2)+'\n')
            rows.append(dict(id=case['id'],expected=expected,actual=projected,matches=expected==projected))
    if source_files()!=before or runtime_identity()!=runtime:raise ValueError('Sources/runtime changed during qualification')
    result=dict(kind='critical-content-qualification',synthetic=True,cases=len(rows),rule_target_pairs=sum(len(r['expected']) for r in rows),
                matched_cases=sum(r['matches'] for r in rows),fixtures=fixtures,source_sha256=before,runtime=runtime,rows=rows,
                scope='Authored HTTP/DOM and fictional reviews; actual offline interpretation, no live site or browser observation.')
    (output/'qualification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');return result


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--node',required=True);p.add_argument('--output-dir',type=Path,required=True);a=p.parse_args()
    r=check(a.node,a.output_dir);print(json.dumps({k:v for k,v in r.items() if k not in ('rows','source_sha256','runtime')}))
    return 0 if r['matched_cases']==r['cases'] else 1


if __name__=='__main__':sys.exit(main())
