"""Deterministic synthetic recipe materialization; expectations are authored data."""
import copy, hashlib, json

def compact(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode('utf-8')

def materialize(row, fixtures):
    data=copy.deepcopy(next(x['input'] for x in fixtures if x['id']==row.get('base','five-roles-complete')))
    target=data['targets'][0];mutation=row['mutation']
    if mutation=='review-text':
        review=target['presence_plan_review'] if row.get('review','plan')=='plan' else target['presence_context_reviews'][0]
        review['reason']=row.get('prefix','')+row.get('character','S')*row['repeat']+row.get('suffix','')
    elif mutation=='review-object':
        review=target['presence_plan_review'];review['extra_note']=''
        review['extra_note']='S'*(row['object_bytes']-len(compact(review)))
    elif mutation=='scope-padding':
        target['intent']['critical_presence']['scope_reason']='Declared synthetic scope.'+' '*row['padding']
        target['presence_plan_review']['reason']+='S'*row.get('review_extra',0)
        if row.get('contradiction'):target['presence_plan_review']['judgment']='contradiction'
    elif mutation=='review-amplification':
        for review in target['presence_context_reviews']:review['reason']='S'*row['repeat']
    elif mutation=='unused-review':
        extra=copy.deepcopy(target['presence_context_reviews'][0]);extra['item_id']='unused';extra['reason']='S'+' '*row['repeat'];target['presence_context_reviews'].append(extra)
    else:raise ValueError('Unknown authored mutation')
    # Bind changed prior intent without generating reviews, judgments or expected outcomes.
    target['presence_plan_review']['binding_sha256']=hashlib.sha256(compact({'url':target['url'],'intent':target['intent']})).hexdigest()
    states={s['id']:s for s in target.get('render',{}).get('states',[])}
    for review in target.get('presence_context_reviews',[]):
        state=states[review['state_id']]
        review['binding_sha256']=hashlib.sha256(compact({'url':target['url'],'intent':target['intent'],'http':target.get('http'),'state':state,'item_id':review['item_id']})).hexdigest()
    return data

import os,sys,tempfile,unittest,socket
from pathlib import Path
from unittest.mock import patch
import tsep
from adapters import captures,replay
from conformance.evaluate import evaluate
from conformance import critical_presence as native
from ts25_runtime_fixtures import historical_expectation
ROOT=Path(__file__).resolve().parents[1]
class CriticalPresenceBudgets(unittest.TestCase):
    def test_authored_byte_boundaries_and_public_refusals(self):
        p=ROOT/'tests/fixtures/critical-presence-budget-v3.json';raw=p.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),p.with_suffix('.sha256').read_text().strip())
        rows=json.loads(raw)['cases'];self.assertEqual(len(rows),19)
        fixtures=json.loads((ROOT/'tests/fixtures/critical-presence-cases-v1.json').read_text())['cases']
        for row in rows:
            with self.subTest(case=row['id']),tempfile.TemporaryDirectory() as td,patch.object(socket,'socket',side_effect=AssertionError('No network collection')):
                root=Path(td);data=materialize(row,fixtures);raw=(json.dumps(data,ensure_ascii=False,indent=2)+'\n').encode()
                self.assertEqual(hashlib.sha256(raw).hexdigest(),row['input_sha256'])
                path=root/'input.json';path.write_bytes(raw);out=root/'bundle'
                notes=[];values=evaluate(data,source_observations=notes);self.assertEqual([x['outcome'] for x in values],row['expected_native'])
                for value in values:
                    note=json.loads(value['reason'][len(native.PREFIX):]);self.assertLessEqual(len(compact(note)),4194304)
                expected_public, expected_size=historical_expectation(row,notes)
                args=dict(assessor='Authored synthetic exercise',label='Synthetic TS25 byte budget',selection_method='Prior finite five-role population',access='synthetic')
                if expected_public=='technical-refusal':
                    with self.assertRaises(tsep.Invalid) as ctx:captures.build(path,out,**args)
                    self.assertIn('TS25',str(ctx.exception));self.assertFalse(out.exists())
                else:
                    captures.build(path,out,**args);report=tsep.read_json(out/'report.json')
                    self.assertEqual(report['results'][0]['status'],expected_public)
                    self.assertEqual((out/'input.json').read_bytes(),raw)
                    size=sum(p.stat().st_size for p in (out/'observations').glob('*.json'));self.assertLessEqual(size,4194304)
                    if expected_size is not None:self.assertEqual(size,expected_size)
                    replayed=replay.replay(out,root/'replay');self.assertTrue(replayed['same_atomic_results']);self.assertTrue(replayed['same_gate'])
                self.assertEqual(path.read_bytes(),raw)
if __name__=='__main__':unittest.main()
