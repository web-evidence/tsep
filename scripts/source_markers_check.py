#!/usr/bin/env python3
"""Qualify authored source-marker hypotheses with explicit Node; no TSEP outcome."""
import argparse
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from experiments import source_markers as reader

def fixture(name):
    path=ROOT/'tests/fixtures'/name
    raw=path.read_bytes(); digest,listed=path.with_suffix('.sha256').read_text().strip().split('  ',1)
    reader.need(listed==name and reader.sha(raw)==digest,'Changed fixture '+name)
    return json.loads(raw)


def check(node,output_dir):
    output_dir.mkdir(parents=True,exist_ok=False)
    oracle=fixture('source-markers-v1.json');amendment=fixture('source-markers-v1-amendment.json');rows=[];runtimes=[]
    assert amendment['original_sha256']==reader.sha((ROOT/'tests/fixtures/source-markers-v1.json').read_bytes())
    contexts=fixture('source-markers-contexts-v1.json')
    context_amendment=fixture('source-markers-contexts-v1-amendment.json')
    assert context_amendment['original_sha256']==reader.sha((ROOT/'tests/fixtures/source-markers-contexts-v1.json').read_bytes())
    corrections={r['case_id']:r for r in (amendment,context_amendment)}
    replay_count=0
    for case in oracle['cases']+contexts['cases']:
        result=reader.observe(case['html'].encode(),content_types=['text/html; charset=utf-8'],objective=case['criteria'],node=node)
        (output_dir/(case['id']+'.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
        if result['inventory']['runtime'] not in runtimes:runtimes.append(result['inventory']['runtime'])
        reader.replay(result,case['html'].encode(),node=node);replay_count+=1
        for mode,r in result['readings'].items():
            corrected=case['id'] in corrections
            expected=corrections.get(case['id'],case)['expected'][mode]
            expected_consensus=corrections.get(case['id'],case)['candidate_consensus']
            actual={'complete':r['complete'],'segments':None if r['segments'] is None else [s['data'] for s in r['segments']],
                    'candidate_outcome':r['candidate_outcome']}
            if case['id']==amendment['case_id']:
                assert amendment['additional_parsed_text_expectation'] in [n['data'] for n in result['inventory']['readings'][mode]['nodes'] if n['kind']=='text']
            if case['id']==context_amendment['case_id']:
                assert not result['inventory']['readings'][mode]['parse_errors']
                assert any(n['kind']=='element' and n['name']=='p' and n['namespace']==reader.HTML for n in result['inventory']['readings'][mode]['nodes'])
            rows.append({'id':case['id'],'mode':mode,'actual':actual,'expected':expected,
                         'original_expected':case['expected'][mode],'explicit_amendment':corrected,
                         'reason':r.get('reason'),'candidate_consensus':result['candidate_consensus'],
                         'matches_original':actual==case['expected'][mode] and result['candidate_consensus']==case['candidate_consensus'],
                         'matches':actual==expected and result['candidate_consensus']==expected_consensus})
    result={'kind':'source-markers-qualification','version':'1','synthetic':True,'normative_effect':'none',
            'oracle_sha256':reader.sha((ROOT/'tests/fixtures/source-markers-v1.json').read_bytes()),
            'context_oracle_sha256':reader.sha((ROOT/'tests/fixtures/source-markers-contexts-v1.json').read_bytes()),
            'source_sha256':reader.identity(),'script_sha256':reader.sha(Path(__file__).read_bytes()),'runtimes':runtimes,
            'amendment_sha256':reader.sha((ROOT/'tests/fixtures/source-markers-v1-amendment.json').read_bytes()),
            'context_amendment_sha256':reader.sha((ROOT/'tests/fixtures/source-markers-contexts-v1-amendment.json').read_bytes()),
            'matches':sum(r['matches'] for r in rows),'matches_original':sum(r['matches_original'] for r in rows),'total':len(rows),'rows':rows,
            'exact_replays':replay_count,
            'scope':'Actual offline parsing of authored documents; no browser/site acquisition, prior real owner intent or TS01 assessment'}
    (output_dir/'qualification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--node',required=True);p.add_argument('--output-dir',type=Path,required=True);a=p.parse_args()
    r=check(a.node,a.output_dir);print(json.dumps({k:v for k,v in r.items() if k not in ('rows','source_sha256')}))
    return 0 if r['matches']==r['total'] else 1


if __name__=='__main__':sys.exit(main())
