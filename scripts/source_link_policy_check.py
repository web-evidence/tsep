#!/usr/bin/env python3
"""Qualify the selected A04 source profile with actual optional Node24 execution."""
import argparse,hashlib,json,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from conformance.evaluate import evaluate
def fixture():
    p=ROOT/'tests/fixtures/source-link-policy-v2.json';raw=p.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=p.with_suffix('.sha256').read_text().strip():raise ValueError('Source link oracle changed')
    return json.loads(raw)
def check(node):
    previous=os.environ.get('TSEP_SOURCE_NODE');os.environ['TSEP_SOURCE_NODE']=node;rows=[]
    try:
        for c in fixture()['cases']:
            notes=[];actual=evaluate(c['input'],source_observations=notes);wanted=c['expected'][0]['outcome']
            rows.append({'id':c['id'],'expected':wanted,'actual':actual,'observations':notes,
                'matches':len(actual)==1 and actual[0]['outcome']==wanted})
        cases=json.loads((ROOT/'conformance/cases.json').read_bytes())['cases'][:543]
        historical=[{'id':c['id'],'input':c['input'],'results':evaluate(c['input'])} for c in cases]
        digest=hashlib.sha256(json.dumps(historical,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
        baseline=json.loads((ROOT/'tests/fixtures/source-link-policy-legacy.json').read_bytes())
    finally:
        if previous is None:os.environ.pop('TSEP_SOURCE_NODE',None)
        else:os.environ['TSEP_SOURCE_NODE']=previous
    return {'kind':'source-link-policy-qualification','synthetic':True,'matched':sum(r['matches'] for r in rows),
        'total':len(rows),'legacy_cases':len(historical),'legacy_digest':digest,'legacy_unchanged':digest==baseline['sha256'],'rows':rows,
        'scope':'Finite authored source decisions and supplied synthetic reviews/DOMs; no observed human review, browser navigation or Google behavior.'}
def main():
    p=argparse.ArgumentParser();p.add_argument('--node',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise ValueError('Choose a new output')
    r=check(a.node)
    with a.output.open('x') as f:json.dump(r,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({k:v for k,v in r.items() if k!='rows'}));return 0 if r['matched']==r['total'] and r['legacy_unchanged'] else 1
if __name__=='__main__':sys.exit(main())
