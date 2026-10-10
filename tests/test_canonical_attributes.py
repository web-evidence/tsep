"""Bounded attribute coverage and correction of permissive structured readings."""
import copy
import hashlib
import json
from pathlib import Path
import unittest
from conformance.evaluate import evaluate
from conformance.canonical import html
from conformance.canonical_attributes import classification, check
from conformance.http import Unknown

ROOT=Path(__file__).resolve().parents[1]
FIXTURE=ROOT/'tests/fixtures/canonical-attributes-v1-cases.json'
SHA='fd828ad8994838b4e9cf6baa80ef6be3f38f53c371f1abb83f9ac8c7606fca49'

class CanonicalAttributes(unittest.TestCase):
 def test_prefrozen_cases_and_exact_corpus(self):
  self.assertEqual(hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),SHA)
  self.assertEqual(FIXTURE.with_suffix('.sha256').read_text().split()[0],SHA)
  cases=json.loads(FIXTURE.read_text())['cases'];self.assertEqual(len(cases),30)
  corpus={c['id']:c for c in json.loads((ROOT/'conformance/cases.json').read_text())['cases']}
  for c in cases:
   with self.subTest(case=c['id']):
    before=copy.deepcopy(c);actual=evaluate(c['input'])
    self.assertEqual([{k:r[k] for k in ('rule_id','target','outcome')} for r in actual],c['expected'])
    self.assertEqual(c,before);self.assertEqual(corpus[c['id']],c)
 def test_changes_from_retained_previous_tool_are_explicit(self):
  data=json.loads(FIXTURE.read_text());prior={r['id']:r['outcomes'] for r in data['prior_results']}
  changed=[r['id'] for r in data['cases'] if prior[r['id']]!=[e['outcome'] for e in r['expected']]]
  self.assertEqual(len(changed),15)
  self.assertIn('canonical-attributes-source-id',changed)
  self.assertIn('canonical-attributes-structured-media',changed)
 def test_legacy_serialized_dom_is_not_silently_extended(self):
  text='<html><head><link id="main" rel="canonical" href="https://example.com/"></head><body></body></html>'
  with self.assertRaisesRegex(Unknown,'Unsupported canonical attributes'):html(text)
  self.assertEqual(html(text,source=True).canonicals,[('https://example.com/',True)])
 def test_classification_is_closed_and_modifiers_are_distinct(self):
  row=classification(['rel','href','id','class','data-x','aria-label','lang','hreflang','media','type','itemprop','data-','xml:lang','onclick'])
  self.assertEqual(row['incidental'],['id','class','data-x','aria-label'])
  self.assertEqual(row['google_modifiers'],['lang','hreflang','media','type'])
  self.assertEqual(row['unsupported'],['itemprop','data-','xml:lang','onclick'])
  with self.assertRaisesRegex(Unknown,'Google policy'):check(['rel','href','media'])
 def test_duplicate_and_malformed_source_still_refused(self):
  for extra in ['id="one" ID="two"','href="https://example.com/other"','xml:lang="fr"','data-="x"']:
   with self.subTest(extra=extra),self.assertRaises(Unknown):
    html('<html><head><link '+extra+' rel="canonical" href="https://example.com/"></head><body></body></html>',source=True)
  with self.assertRaises(Unknown):html('<html><head><link id="x" rel="canonical" href="https://example.com/"></head><body><noscript>x</noscript></body></html>',source=True)
 def test_source_rel_uses_html_ascii_whitespace(self):
  def read(value):return html('<html><head><link id="x" rel="'+value+'" href="https://example.com/"></head><body></body></html>',source=True).canonicals
  self.assertEqual(len(read('alternate\tCANONICAL')),1)
  self.assertEqual(read('alternate\u00a0canonical'),[])
