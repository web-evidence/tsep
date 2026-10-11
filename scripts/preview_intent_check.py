#!/usr/bin/env python3
"""Qualify frozen preview cases and preserve all 701 previous input/results exactly."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from conformance.evaluate import evaluate


def check(node=None):
    previous=os.environ.get('TSEP_SOURCE_NODE')
    if node is None:os.environ.pop('TSEP_SOURCE_NODE',None)
    else:os.environ['TSEP_SOURCE_NODE']=node
    try:
        p=ROOT/'tests/fixtures/preview-intent-v2.json';raw=p.read_bytes()
        if hashlib.sha256(raw).hexdigest()!=p.with_suffix('.sha256').read_text().strip():
            raise ValueError('Changed prefrozen preview expectations')
        cases=json.loads(raw)['cases'];rows=[]
        corpus=json.loads((ROOT/'conformance/cases.json').read_bytes())['cases']
        for case in cases:
            notes=[];actual=evaluate(case['input'],source_observations=notes)
            matches=len(actual)==len(case['expected']) and all(
                all(a[k]==e[k] for k in ('rule_id','target','outcome')) for a,e in zip(actual,case['expected']))
            reduced=not matches and node is None and all(e.get('reference_limit') for e in case['expected']) and all(a['outcome']=='inconclusive' for a in actual)
            rows.append(dict(id=case['id'],expected=case['expected'],actual=actual,observations=notes,
                             matches=matches and case in corpus,reduced_coverage=reduced))
        historical=[dict(id=c['id'],input=c['input'],results=evaluate(c['input'])) for c in corpus[:701]]
        digest=hashlib.sha256(json.dumps(historical,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        baseline=json.loads((ROOT/'provenance/preview-intent-v1.json').read_bytes())
        configuration='core' if node is None else 'node24'
        expected=next(b for b in baseline['historical_baselines'] if b['configuration']==configuration)
        return dict(kind='preview-intent-qualification',configuration=configuration,synthetic=True,
                    matched=sum(r['matches'] for r in rows),reduced=sum(r['reduced_coverage'] for r in rows),total=len(rows),
                    legacy_cases=len(historical),legacy_digest=digest,legacy_unchanged=digest==expected['sha256'],rows=rows,
                    scope='Finite authored raw inputs only. No Google display, actual browser campaign, owner review or site conclusion.')
    finally:
        if previous is None:os.environ.pop('TSEP_SOURCE_NODE',None)
        else:os.environ['TSEP_SOURCE_NODE']=previous


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--node');p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    if a.output.exists():raise ValueError('Choose a new output')
    result=check(a.node)
    with a.output.open('x') as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({k:v for k,v in result.items() if k!='rows'}))
    return 0 if result['matched']+result['reduced']==result['total'] and result['legacy_unchanged'] else 1


if __name__=='__main__':sys.exit(main())
