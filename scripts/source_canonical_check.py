#!/usr/bin/env python3
"""Qualify prior canonical source decisions with an explicitly supplied Node 24."""
import argparse,hashlib,json,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from conformance.evaluate import evaluate

def fixture():
    p=ROOT/'tests/fixtures/source-canonical-v1.json';raw=p.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=p.with_suffix('.sha256').read_text().strip():
        raise ValueError('Canonical source oracle changed')
    result=json.loads(raw)
    extra=ROOT/'tests/fixtures/source-canonical-extra-v1.json';encoded=extra.read_bytes()
    if hashlib.sha256(encoded).hexdigest()!=extra.with_suffix('.sha256').read_text().strip():raise ValueError('Changed independent-signal oracle')
    result['cases'].extend(json.loads(encoded)['cases'])
    levels=ROOT/'tests/fixtures/source-canonical-levels-v1.json';encoded=levels.read_bytes()
    if hashlib.sha256(encoded).hexdigest()!=levels.with_suffix('.sha256').read_text().strip():raise ValueError('Changed aggregation oracle')
    result['cases'].extend(json.loads(encoded)['cases'])
    return result

def check(node):
    previous=os.environ.get('TSEP_SOURCE_NODE');os.environ['TSEP_SOURCE_NODE']=node
    rows=[]
    try:
        for case in fixture()['cases']:
            observations=[];actual=evaluate(case['input'],source_observations=observations)
            wanted=case['expected'][0]['outcome']
            rows.append({'id':case['id'],'expected':wanted,'actual':actual,'observations':observations,
                         'matches':len(actual)==1 and actual[0]['outcome']==wanted})
        cases=json.loads((ROOT/'conformance/cases.json').read_text())['cases'][:488]
        historical=[{'id':c['id'],'input':c['input'],'results':evaluate(c['input'])} for c in cases]
        digest=hashlib.sha256(json.dumps(historical,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
        baseline=json.loads((ROOT/'tests/fixtures/source-canonical-legacy.json').read_text())
    finally:
        if previous is None:os.environ.pop('TSEP_SOURCE_NODE',None)
        else:os.environ['TSEP_SOURCE_NODE']=previous
    return {'kind':'source-canonical-qualification','synthetic':True,'matched':sum(r['matches'] for r in rows),
            'total':len(rows),'legacy_cases':len(historical),'legacy_digest':digest,
            'legacy_unchanged':digest==baseline['sha256'],'rows':rows,
            'scope':'Finite authored decisions; actual optional Node execution, no real browser, human review or Google observation.'}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--node',required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    if a.output.exists():raise ValueError('Choose a new output')
    r=check(a.node)
    with a.output.open('x',encoding='utf-8') as f:json.dump(r,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({k:v for k,v in r.items() if k!='rows'}))
    return 0 if r['matched']==r['total'] and r['legacy_unchanged'] else 1

if __name__=='__main__':sys.exit(main())
