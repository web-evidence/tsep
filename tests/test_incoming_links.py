"""TS16 frozen populations, transport integrity, exact originals and offline replay."""
import copy
import hashlib
import json
import os
from pathlib import Path
import socket
import tempfile
import unittest
from unittest.mock import patch

import tsep
from adapters import captures, replay
from adapters.incoming_links_intake import verify_target
from conformance import incoming_links as native
from conformance.evaluate import evaluate
from conformance.corpus import expand
from reports import html

ROOT = Path(__file__).resolve().parents[1]
SHAS = {
    'cases-v1': '7944049e3bd56fdf44b7121fb5b2e169d2ea9f2cf20c1390a433258fd824df1c',
    'boundaries-v1': '0c712aa82e8e52cbe3be734726103e4b3f120e23e0f552879c8b47a3765f14cd',
    'intake-v1': 'a394a9c8e736573f8ed0cede256780ef993c1b47947fc02fd47329f57729460b',
    'review-boundaries-v1': '70c8c38fcfcf062e9fe0ce88d690ce30cb026ffb2e7b2477dabedbb73473e6bc',
    'population-bound-v1': 'cda16f224ad44ca8a417bfcab2ee72f4adbf8d9ae520a16b37fe635ff99489d4',
}

def fixture(name):
    raw = (ROOT/'tests/fixtures'/('incoming-links-'+name+'.json')).read_bytes()
    if hashlib.sha256(raw).hexdigest() != SHAS[name]:
        raise ValueError('Changed prefrozen TS16 cases')
    return json.loads(raw)['cases']

def data(name='source-witness'):
    return copy.deepcopy(next(c['input'] for c in fixture('cases-v1') if c['id'] == name))

def build(root, value, access='synthetic', destination='bundle'):
    raw = (json.dumps(value, ensure_ascii=False, indent=2)+'\n').encode()
    (root/'input.json').write_bytes(raw)
    captures.build(root/'input.json', root/destination, assessor='Authored synthetic exercise',
                   label='Synthetic TS16', selection_method='Prior authored bounded population', access=access)
    return raw

class IncomingLinks(unittest.TestCase):
    def test_frozen_native_population_expectations(self):
        count = 0
        with patch.object(socket, 'socket', side_effect=AssertionError('Offline supplied originals only')):
            for name in ('cases-v1', 'boundaries-v1', 'review-boundaries-v1', 'population-bound-v1'):
                for case in fixture(name):
                    if case['expected'] == 'technical-refusal': continue
                    count += 1
                    with self.subTest(case=case['id']):
                        before = copy.deepcopy(case['input'])
                        result = native.assess_target(case['input']['targets'][0])
                        self.assertEqual(result['outcome'], case['expected'])
                        self.assertFalse(result['authenticates_evidence'])
                        self.assertEqual(before, case['input'])
                        if 'expected_destination_outcomes' in case:
                            self.assertEqual({d['url']: d['outcome'] for d in result['destinations']}, case['expected_destination_outcomes'])
                        if 'required_witness_fields' in case:
                            witnesses = [w for d in result['destinations'] for w in d['witnesses']]
                            self.assertTrue(witnesses)
                            self.assertTrue(all(set(case['required_witness_fields']) <= set(w) for w in witnesses))
        self.assertEqual(count, 64)

    def test_corpus_is_derived_from_authored_expectations(self):
        expanded = expand(tsep.read_json(ROOT/'conformance/cases.json'))['cases']
        rows = [c for c in expanded if c['id'].startswith('incoming-links-v1-')]
        authored = [c for n in ('cases-v1', 'boundaries-v1', 'review-boundaries-v1', 'population-bound-v1') for c in fixture(n) if c['expected'] != 'technical-refusal']
        self.assertEqual(len(rows), 64)
        for row, original in zip(rows, authored):
            self.assertEqual(row['input'], original['input'])
            self.assertEqual(row['expected'][0]['outcome'], original['expected'])

    def test_intake_refuses_corruption_before_creating_output(self):
        rows = fixture('cases-v1')+fixture('boundaries-v1')+fixture('intake-v1')
        count = 0
        for case in rows:
            expected = case.get('expected_intake', case.get('expected'))
            if expected != 'technical-refusal': continue
            count += 1
            with self.subTest(case=case['id']), tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                with patch.object(socket, 'socket', side_effect=AssertionError('No collection')):
                    with self.assertRaises(tsep.Invalid): build(root, case['input'])
                self.assertFalse((root/'bundle').exists())
                self.assertEqual(tsep.read_json(root/'input.json'), case['input'])
        self.assertEqual(count, 14)

    def test_missing_evidence_and_association_are_not_corrupt_transport(self):
        rows = [c for c in fixture('intake-v1') if c['expected_intake'] != 'technical-refusal']
        self.assertEqual(len(rows), 14)
        for case in rows:
            with self.subTest(case=case['id']):
                before = copy.deepcopy(case['input'])
                verify_target(case['input']['targets'][0], '2')
                self.assertEqual(evaluate(case['input'])[0]['outcome'], 'inconclusive')
                self.assertEqual(before, case['input'])

    def test_actual_bundles_originals_html_and_exact_replay(self):
        for name, status in [('source-witness','C'), ('load-dom-witness','C'),
                             ('bounded-absence-destination-original-missing','NC'),
                             ('missing-source-without-witness','NT')]:
            with self.subTest(case=name), tempfile.TemporaryDirectory() as folder:
                root = Path(folder); d = data(name)
                with patch.object(socket, 'socket', side_effect=AssertionError('Offline adapter and replay')):
                    raw = build(root, d)
                    report = tsep.read_json(root/'bundle/report.json')
                    self.assertEqual(report['results'][0]['status'], status)
                    self.assertTrue(tsep.decision(report)['synthetic_evidence'])
                    self.assertIn('incoming_links_interpretation', tsep.decision(report))
                    self.assertEqual((root/'bundle/input.json').read_bytes(), raw)
                    result = replay.replay(root/'bundle', root/'replayed')
                    self.assertTrue(result['same_atomic_results']); self.assertTrue(result['same_gate'])
                for language in ('fr','en'):
                    text = html.render(root/'bundle/report.json', language=language)
                    self.assertIn(html.TEXT[language]['incoming_note'], text)
                    self.assertIn(html.TEXT[language]['incoming_title'], text)
                    if status == 'NC':
                        self.assertIn(html.TEXT[language]['incoming_missing_original'], text)
                        self.assertIn(html.TEXT[language]['incoming_absence'], text)
                pieces = captures.pieces(d['targets'][0])
                self.assertEqual(pieces['inventory'], d['targets'][0]['incoming_links']['inventory'])
                self.assertEqual(pieces['http']['incoming_link_documents'], d['targets'][0]['incoming_links']['documents'])
                self.assertNotIn('http', d['targets'][0])

    def test_provenance_missing_plan_runtime_and_existing_output(self):
        for absent_plan in (False, True):
            for flag, access in [(True,'public'), (False,'synthetic'), ('yes','synthetic')]:
                with self.subTest(absent_plan=absent_plan, flag=flag, access=access), tempfile.TemporaryDirectory() as folder:
                    root=Path(folder);d=data();d['targets'][0]['incoming_links_synthetic']=flag
                    if absent_plan:d['targets'][0]['intent'].pop('incoming_links')
                    with self.assertRaises(tsep.Invalid):build(root,d,access)
                    self.assertFalse((root/'bundle').exists())
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(evaluate(data())[0]['outcome'], 'inconclusive')
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);(root/'bundle').mkdir();(root/'bundle/untouched').write_bytes(b'original')
            with self.assertRaises(tsep.Invalid):build(root,data())
            self.assertEqual((root/'bundle/untouched').read_bytes(),b'original')

    def test_html_escapes_retained_diagnostic_without_recalculation(self):
        note={'sources':[], 'destinations':[{'url':'<img src=x onerror=alert(1)>','outcome':'fail',
              'bounded_absence':True,'original':{'qualified':False,'reason':'<script>x</script>'},'witnesses':[]}]}
        for language in ('fr','en'):
            with patch.object(native,'assess_target',side_effect=AssertionError('No reevaluation')):
                text=html.incoming_links_values({'reason':native.PREFIX+json.dumps(note)},html.TEXT[language])
            self.assertNotIn('<img ',text);self.assertNotIn('<script>',text)
            self.assertIn('&lt;img ',text);self.assertIn('&lt;script&gt;',text)
            self.assertIn(html.TEXT[language]['incoming_missing_original'],text)

    def test_reader_and_intake_sources_are_fingerprinted(self):
        files=captures.source_files()
        for name in ('conformance/incoming_links.py','adapters/incoming_links_intake.py'):
            self.assertIn(name,files)

if __name__ == '__main__': unittest.main()
