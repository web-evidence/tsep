"""Frozen normative rendered cases; authored fixtures, never browser execution."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import tsep
from adapters import captures, replay, review
from conformance.evaluate import binding_digest, evaluate

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT/'tests/fixtures/structured-rendering-v1-cases.json'
FROZEN = '9fab6a4deb08ce84f4957fb75bcf4cb5d2a7fe9e43657db872ae46750c9976bf'


class StructuredDOM(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = json.loads(FIXTURE.read_bytes())['cases']

    def data(self, name):
        return copy.deepcopy(next(r['input'] for r in self.rows if r['id'] == 'structured-' + name))

    def test_prefrozen_cases_and_unchanged_inputs(self):
        self.assertEqual(hashlib.sha256(FIXTURE.read_bytes()).hexdigest(), FROZEN)
        self.assertEqual(FIXTURE.with_suffix('.sha256').read_text().split()[0], FROZEN)
        self.assertEqual(len(self.rows), 39)
        for row in self.rows:
            with self.subTest(row=row['id']), patch('socket.socket', side_effect=AssertionError('offline')):
                before = copy.deepcopy(row)
                result = evaluate(row['input'])
                self.assertEqual([{k: r[k] for k in ('rule_id', 'target', 'outcome')} for r in result], row['expected'])
                self.assertEqual(row, before)

    def test_complete_corpus_contains_exact_frozen_cases(self):
        corpus = {r['id']: r for r in json.loads((ROOT/'conformance/cases.json').read_bytes())['cases']}
        for row in self.rows:
            self.assertEqual(corpus[row['id']], row)

    def test_structured_failure_cannot_be_hidden_by_good_serialization(self):
        data = self.data('ts07-added-noindex')
        state = data['targets'][0]['render']['states'][0]
        # The serialization companion is not reparsed to erase the tree's noindex.
        state['dom'] = state['structured_dom']['snapshot']['tree']['serialization']['html']
        self.assertEqual(evaluate(data)[0]['outcome'], 'fail')
        state['dom'] = '<html><head></head><body></body></html>'
        self.assertEqual(evaluate(data)[0]['outcome'], 'inconclusive')

    def test_same_navigation_is_explicit_unverified_attribution(self):
        data = self.data('ts07-compatible')
        acquisition = data['targets'][0]['render']['states'][0]['structured_dom']['acquisition']
        acquisition['kind'] = 'same-navigation'
        result = evaluate(data)[0]
        self.assertEqual(result['outcome'], 'pass')
        self.assertIn('acquisition=same-navigation', result['reason'])
        self.assertIn('not independently authenticated', result['reason'])
        acquisition['navigation_id'] = ''
        self.assertEqual(evaluate(data)[0]['outcome'], 'inconclusive')

    def test_input_retention_offline_replay_and_synthetic_boundary(self):
        for name, status in [('ts07-compatible', 'NT'), ('ts07-added-noindex', 'NC'),
                             ('canonical-conflict-and-missing', 'NC'), ('links-base-changed', 'NT')]:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as folder:
                root = Path(folder); source = root/'input.json'
                source.write_text(json.dumps(self.data(name)), encoding='utf-8')
                with patch('socket.socket', side_effect=AssertionError('offline')):
                    captures.build(source, root/'bundle', assessor='Synthetic test', label='SYNTHETIC DOM fixture',
                                   selection_method='Authored fixture only', access='synthetic', mode='automatic')
                    result = replay.replay(root/'bundle', root/'replay')
                report = tsep.read_json(root/'bundle/report.json')
                self.assertEqual(report['results'][0]['status'], status)
                self.assertEqual((root/'bundle/input.json').read_bytes(), source.read_bytes())
                self.assertTrue(result['replayed'])
                with self.assertRaisesRegex(tsep.Invalid, 'requires synthetic'):
                    captures.build(source, root/'bad', assessor='Test', label='Cannot relabel authored DOM',
                                   selection_method='Test', access='public', mode='automatic')

    def test_source_contradiction_survives_unusable_dom(self):
        data = self.data('canonical-compatible'); target = data['targets'][0]
        doc = target['documents'][0]
        doc['http'][0]['response'] = doc['http'][0]['response'].replace('href="https://example.com/product"',
                                                                         'href="https://example.com/other"')
        # The old DOM is now unbound. Its loss cannot erase the source contradiction.
        self.assertEqual(evaluate(data)[0]['outcome'], 'fail')

    def test_manual_review_is_bound_to_structured_inputs(self):
        data = self.data('manual-review-bound'); target = data['targets'][0]
        self.assertEqual(evaluate(data)[0]['outcome'], 'pass')
        state = target['documents'][0]['render']['states'][0]
        state['structured_dom']['acquisition']['navigation_id'] += '-changed'
        self.assertEqual(evaluate(data)[0]['outcome'], 'inconclusive')

    def test_review_names_tree_and_companion_without_prefilled_judgment(self):
        data = self.data('manual-review-bound')
        task = review.tasks(data)[0]
        state = data['targets'][0]['documents'][0]['render']['states'][0]
        record = state['structured_dom']['snapshot']
        identity = task['rendered_captures'][0]
        self.assertEqual(identity['snapshot_sha256'], binding_digest(record))
        self.assertEqual(identity['serialization_utf8_sha256'], hashlib.sha256(
            record['tree']['serialization']['html'].encode('utf-8')).hexdigest())
        self.assertEqual(identity['navigation_id'], 'synthetic-navigation')
        self.assertEqual(len(task['rendered_captures']), 2)
        self.assertTrue(all(row['outcome'] is None for row in review.response(task)['comparisons']))

    def test_unplanned_state_does_not_erase_attributable_structured_failure(self):
        data = self.data('canonical-conflict')
        states = data['targets'][0]['documents'][0]['render']['states']
        states.append(dict(copy.deepcopy(states[0]), id='unplanned'))
        # Make the second family member inconclusive too, so only this failure remains.
        data['targets'][0]['documents'][1].pop('render')
        result = evaluate(data)[0]
        self.assertEqual(result['outcome'], 'fail')
        self.assertIn('Unplanned DOM capture', result['reason'])


if __name__ == '__main__':
    unittest.main()
