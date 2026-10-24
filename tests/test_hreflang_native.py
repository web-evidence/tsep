"""Prefrozen native TS23 contradictory interpretations; no network acquisition."""
import copy
import hashlib
import json
from pathlib import Path
import socket
import unittest
from unittest.mock import patch
import tsep
from conformance import hreflang_native as native

ROOT=Path(__file__).resolve().parents[1]
SHAS={'native':'495741cedc5ce2f711cf62390736ee5aeb5b9bddc57a9616c9d45a101c30dbee','review':'77d96b6fd668dc42da6379c4ac4a07cad714894d3847f64594c69fdd2361a1ba'}

def cases(name):
 raw=(ROOT/'tests/fixtures'/('hreflang-'+name+'-v1.json')).read_bytes()
 if hashlib.sha256(raw).hexdigest()!=SHAS[name]:raise ValueError('Changed preauthored expectations')
 return json.loads(raw)['cases']

class HreflangNative(unittest.TestCase):
 def test_native_and_review_cases_keep_authored_outcomes(self):
  count=0
  for name in SHAS:
   for c in cases(name):
    count+=1
    with self.subTest(case=c['id']),patch.object(socket,'socket',side_effect=AssertionError('No acquisition')):
     before=copy.deepcopy(c['input'])
     if c['expected']=='technical-refusal':
      with self.assertRaises(tsep.Invalid):native.assess(c['input'])
     else:
      result=native.assess(c['input']);self.assertEqual(result['outcome'],c['expected']);self.assertFalse(result.get('authenticates_evidence',False))
     self.assertEqual(c['input'],before)
  self.assertEqual(count,95)

 def test_missing_planned_document_has_explicit_diagnostic(self):
  c=copy.deepcopy(cases('native')[0]);missing=c['input']['documents'].pop()['url'];r=native.assess(c['input'])
  page=next(p for p in r['pages'] if p['url']==missing)
  self.assertEqual(page['outcome'],'NT')
  self.assertIn('Missing supplied original for planned page',page['reason'])
  self.assertIn('Original fourni absent pour la page prévue',page['reason'])
  self.assertIn(missing,page['reason'])

 def test_native_byte_offsets_and_observers_bind_exact_originals(self):
  c=next(x for x in cases('native') if x['id']=='non-BMP-prefix');result=native.assess(c['input']);self.assertEqual(result['outcome'],'C')
  for page,doc in zip(result['pages'],c['input']['documents']):
   channel=page['channels']['html'];binding=channel['source_bindings'];raw=doc['body'].encode()
   self.assertEqual(binding['body_sha256'],hashlib.sha256(raw).hexdigest())
   for reading in channel['hypotheses'].values():
    for row in reading['rows']:
     a,b=row['body_span_bytes'];self.assertEqual(raw[a:b].decode(),row['raw_tag'])
   self.assertIn('experiments/link_elements.py',binding['element_reader']);self.assertIn('experiments/source_head.py',binding['head_reader'])

 def test_secondary_complete_set_is_visible_without_repairing_primary(self):
  c=next(x for x in cases('native') if x['id']=='empty-primary-complete-secondary');r=native.assess(c['input'])
  self.assertEqual(r['outcome'],'NC')
  self.assertTrue(any(p['channels']['http-link']['decision']['complete_expected_set'] for p in r['pages']))
  self.assertTrue(any(h['decision']['missing'] for p in r['pages'] for h in p['channels']['html']['hypotheses'].values()))

if __name__=='__main__':unittest.main()
