#!/usr/bin/env python3
"""Qualify prior source-links-v2 and preserve the full 601-case historical result."""
import argparse,hashlib,json,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from conformance.evaluate import evaluate

def fixture():
    p=ROOT/'tests/fixtures/source-link-invalid-base-v2.json';raw=p.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=p.with_suffix('.sha256').read_text().strip():raise ValueError('Changed frozen invalid-base oracle')
    return json.loads(raw)

def check(node):
    previous=os.environ.get('TSEP_SOURCE_NODE');os.environ['TSEP_SOURCE_NODE']=node;rows=[]
    try:
        for case in fixture()['cases']:
            notes=[];actual=evaluate(case['input'],source_observations=notes)
            expected=[{k:r[k] for k in ('rule_id','target','outcome')} for r in case['expected']]
            observed=[{k:r[k] for k in ('rule_id','target','outcome')} for r in actual]
            rows.append(dict(id=case['id'],expected=expected,actual=actual,observations=notes,matches=observed==expected))
        historical=[dict(id=c['id'],input=c['input'],results=evaluate(c['input'])) for c in json.loads((ROOT/'conformance/cases.json').read_bytes())['cases'][:601]]
        digest=hashlib.sha256(json.dumps(historical,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        baseline=json.loads((ROOT/'tests/fixtures/source-link-invalid-base-legacy.json').read_bytes())
    finally:
        if previous is None:os.environ.pop('TSEP_SOURCE_NODE',None)
        else:os.environ['TSEP_SOURCE_NODE']=previous
    return dict(kind='source-link-invalid-base-v2-qualification',synthetic=True,matched=sum(r['matches'] for r in rows),total=len(rows),
        legacy_cases=len(historical),legacy_digest=digest,legacy_unchanged=digest==baseline['sha256'],rows=rows,
        scope='Frozen authored expectations; actual optional Node24 source execution, synthetic supplied reviews/DOMs. No observed human review, site repair or browser/Google outcome.')

def main():
    p=argparse.ArgumentParser();p.add_argument('--node',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise ValueError('Choose a new output')
    r=check(a.node)
    with a.output.open('x') as f:json.dump(r,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({k:v for k,v in r.items() if k!='rows'}));return 0 if r['matched']==r['total'] and r['legacy_unchanged'] else 1
if __name__=='__main__':sys.exit(main())
