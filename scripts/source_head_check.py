#!/usr/bin/env python3
"""Opt-in head/source qualification; observations, not TSEP decisions. Apache-2.0."""
import argparse
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from experiments import source_head, source_http
from scripts.source_http_check import fixture


def check(node, output_dir):
    output_dir.mkdir(parents=True,exist_ok=False)
    rows=[]; runtimes=[]
    for case in fixture('source-head-v1.json')['cases']:
        raw=case['html'].encode('utf-8')
        result=source_head.inventory(raw,content_types=['text/html; charset=utf-8'],node=node)
        baseline=source_http.inventory(raw,content_types=['text/html; charset=utf-8'],node=node,metadata=True)
        if result['runtime'] not in runtimes:runtimes.append(result['runtime'])
        (output_dir/(case['id']+'.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
        for mode,reading in result['readings'].items():
            actual=source_head.projection(reading)
            # Instrumentation must not change even one existing tree observation.
            old={k:v for k,v in reading.items() if k!='head_prefix'}
            same=old==baseline['readings'][mode]
            rows.append({'id':case['id'],'mode':mode,'expected':case['expected'][mode],'actual':actual,
                         'same_metadata_inventory':same,
                         'matches':reading['complete'] and actual==case['expected'][mode] and same})
    return {'kind':'source-head-qualification','synthetic':True,'normative_effect':'none',
            'source_sha256':source_head.identity(),'baseline_worker_sha256':source_http.sha((ROOT/'experiments/source_metadata.mjs').read_bytes()),
            'oracle_sha256':source_http.sha((ROOT/'tests/fixtures/source-head-v1.json').read_bytes()),
            'qualification_script_sha256':source_http.sha(Path(__file__).read_bytes()),'runtimes':runtimes,
            'matched':sum(r['matches'] for r in rows),'total':len(rows),'rows':rows,
            'scope':'Authored source/tree facts and unchanged metadata inventories in both static hypotheses. No SEO outcome, browser execution or Google observation.'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--node',required=True)
    parser.add_argument('--output-dir',type=Path,required=True)
    args=parser.parse_args()
    result=check(args.node,args.output_dir)
    (args.output_dir/'qualification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('rows','source_sha256')}))
    return 0 if result['matched']==result['total'] else 1


if __name__=='__main__':sys.exit(main())
