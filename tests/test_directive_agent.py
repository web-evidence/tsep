"""Prefrozen distinctions between transport agent and directive semantics."""
import copy
import hashlib
import json
from pathlib import Path
import unittest
from conformance.evaluate import evaluate

ROOT=Path(__file__).resolve().parents[1]
FILES={'directive-agent-v1-cases':'ba2498ddf49e49a29a50f312baa11a8b1117289dac5bc6cb654affe2a77d8e33',
       'directive-agent-access-v1-cases':'2cda096b204d051b62a8d9d2a9bbfeaf1e8d35c4d465706fa27633f3b7498826'}
class DirectiveAgent(unittest.TestCase):
 def test_frozen_cases_and_corpus(self):
  corpus={c['id']:c for c in json.loads((ROOT/'conformance/cases.json').read_text())['cases']}
  total=0
  for name,sha in FILES.items():
   p=ROOT/'tests/fixtures'/(name+'.json');self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),sha)
   self.assertEqual(p.with_suffix('.sha256').read_text().split()[0],sha)
   for case in json.loads(p.read_text())['cases']:
    with self.subTest(case=case['id']):
     before=copy.deepcopy(case);actual=evaluate(case['input'])
     self.assertEqual([{k:r[k] for k in ('rule_id','target','outcome')} for r in actual],case['expected'])
     self.assertEqual(case,before);self.assertEqual(corpus[case['id']],case);total+=1
  self.assertEqual(total,15)
 def test_explicit_scope_is_not_an_engine_observation(self):
  data=json.loads((ROOT/'tests/fixtures/directive-agent-v1-cases.json').read_text())['cases'][0]['input']
  result=evaluate(data)[0];self.assertIn('not evidence of what Googlebot receives',result['reason'])
 def test_missing_or_wrong_policy_cannot_fall_back_to_http_agent(self):
  data=json.loads((ROOT/'tests/fixtures/directive-agent-access-v1-cases.json').read_text())['cases'][0]['input']
  for policy in (None,{}, {'product_token':None},{'product_token':'Chrome'}):
   modified=copy.deepcopy(data);modified['targets'][0]['intent']['robots_policy']=policy
   self.assertEqual(evaluate(modified)[0]['outcome'],'inconclusive')
