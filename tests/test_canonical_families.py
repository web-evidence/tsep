"""Computed TS10 outcomes, report boundaries and EARL; Apache-2.0."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import tsep
from conformance.evaluate import evaluate, binding_digest
from conformance.canonical import content_binding

CASES = {c['id']: c for c in tsep.read_json(ROOT/'conformance/cases.json')['cases']}


def assessed_report(data, root):
    """Test adapter only: all verdicts computed, never read from case expectations."""
    targets = [t['url'] for t in data['targets']]
    report = tsep.initialize(targets, ['TS10'], 'custom', 'Synthetic manual review author',
                             'Synthetic inventoried families', 'Declared synthetic populations only',
                             mode='manual', tool={'name': 'TSEP bounded interpreter',
                             'version': tsep.read_json(tsep.PROTOCOL_PATH)['version']})
    report['scope']['exclusions'] = ['Real sites, other controls, unlisted families and engine selection']
    refs = {}
    for number, target in enumerate(data['targets']):
        pieces = {'intent': {k: target.get(k) for k in ('intent', 'context', 'content_review')},
                  'http': target['documents'],
                  'html': [{'url': d['url'], 'source_response': d['http'][-1]['response'],
                            'exemption_review': d.get('exemption_review')} for d in target['documents']]}
        for kind in ('sitemaps', 'crawl'):
            if kind in target:
                pieces['sitemap' if kind == 'sitemaps' else kind] = target[kind]
        rendered = [d for d in target['documents'] + target.get('crawl', {}).get('documents', []) if 'render' in d]
        if rendered:
            pieces['render'] = rendered
        refs[target['url']] = []
        for kind, piece in pieces.items():
            aid = kind + '-' + str(number); path = root/(aid + '.json')
            path.write_text(json.dumps(piece, ensure_ascii=False), encoding='utf-8')
            report['artifacts'].append({'id': aid, 'path': path.name, 'sha256': tsep.digest(path),
                'kind': kind, 'targets': [target['url']], 'observed_at': target['observed_at'],
                'access': 'synthetic', 'description': 'SYNTHETIC raw fixture and supplied human judgments; not a live audit'})
            refs[target['url']].append(aid)
    atoms = [dict(a, evidence_ids=refs[a['target']]) for a in evaluate(data)]
    outcomes = [a['outcome'] for a in atoms]
    status = 'NC' if 'fail' in outcomes else 'NT' if 'inconclusive' in outcomes else 'C'
    report['results'][0].update(status=status, evaluation_state='inconclusive' if status == 'NT' else 'complete',
        reason='Computed synthetic family findings; supplied manual content judgments',
        procedure='Interpret raw captures and check binding/coverage of documented human review',
        evaluated_targets=targets, evidence_ids=[a['id'] for a in report['artifacts']], atomic_results=atoms)
    return report


class CanonicalFamilies(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def data(self, name='canonical-all-signals-agree'):
        return copy.deepcopy(CASES[name]['input'])

    def test_computed_reports_preserve_partial_and_positive_exemption(self):
        for name, status, decision in [('canonical-all-signals-agree','C','GO_WITH_RESERVATIONS'),
                ('canonical-content-review-missing','NT','INCOMPLETE'),
                ('canonical-links-missing-source-zero-is-unknown','NT','INCOMPLETE'),
                ('canonical-sitemap-positive-absence','C','GO_WITH_RESERVATIONS')]:
            with self.subTest(case=name):
                report = assessed_report(self.data(name), self.root)
                summary = tsep.validate(report, self.root)
                self.assertEqual(report['results'][0]['status'], status)
                self.assertEqual(summary['decision'], decision)
                self.assertEqual(summary['selected_controls'], 1)
                self.assertEqual(summary['protocol_controls'], 44)
                self.assertTrue(summary['synthetic_evidence'])

    def test_every_isolated_rule_cannot_pass_parent(self):
        for rule in self.data()['rules']:
            data = self.data(); data['rules'] = [rule]
            with self.subTest(rule=rule), self.assertRaisesRegex(tsep.Invalid, 'every atomic rule'):
                tsep.validate(assessed_report(data, self.root), self.root)

    def test_unknown_cannot_be_promoted_to_c(self):
        report = assessed_report(self.data('canonical-content-review-missing'), self.root)
        report['results'][0].update(status='C', evaluation_state='complete')
        with self.assertRaisesRegex(tsep.Invalid, 'cannot yield C'):
            tsep.validate(report, self.root)

    def test_all_passing_ts10_cannot_be_automatic(self):
        report = assessed_report(self.data(), self.root); report['assessor']['mode'] = 'automatic'
        with self.assertRaisesRegex(tsep.Invalid, 'every control rule'):
            tsep.validate(report, self.root)

    def test_per_rule_required_evidence_cannot_be_omitted(self):
        original = assessed_report(self.data(), self.root)
        control = next(c for c in tsep.read_json(tsep.PROTOCOL_PATH)['controls'] if c['id'] == 'TS10')
        for index, rule in enumerate(control['rules']):
            for kind in rule['required_inputs']:
                report = copy.deepcopy(original)
                report['results'][0]['atomic_results'][index]['evidence_ids'].remove(kind + '-0')
                with self.subTest(rule=rule['id'], kind=kind), self.assertRaisesRegex(tsep.Invalid, 'Missing atomic input'):
                    tsep.validate(report, self.root)

    def test_unknown_and_failure_remain_distinct_in_report_and_earl(self):
        data = self.data('canonical-content-review-missing')
        doc = data['targets'][0]['sitemaps']['documents'][0]
        doc['http'][0]['response'] = doc['http'][0]['response'].replace('/product</loc>', '/product?color=blue</loc>')
        report = assessed_report(data, self.root)
        summary = tsep.validate(report, self.root)
        self.assertEqual(summary['decision'], 'REVIEW')
        graph = tsep.earl(report, summary)['@graph']; parent = graph[2]
        self.assertEqual(parent['earl:result']['earl:outcome']['@id'], 'earl:failed')
        atoms = [a for a in graph if 'dct:isPartOf' in a]
        self.assertEqual(len(atoms), 4)
        self.assertEqual([a['earl:result']['earl:outcome']['@id'] for a in atoms],
                         ['earl:passed', 'earl:cantTell', 'earl:failed', 'earl:passed'])
        for atom in atoms:
            self.assertEqual(atom['dct:isPartOf']['@id'], parent['@id'])
            self.assertEqual(atom['earl:subject']['@id'], data['targets'][0]['url'])

    def test_atomic_sitemap_na_has_its_own_earl_assertion(self):
        report = assessed_report(self.data('canonical-sitemap-positive-absence'), self.root)
        graph = tsep.earl(report, tsep.validate(report, self.root))['@graph']
        self.assertEqual(graph[2]['earl:result']['earl:outcome']['@id'], 'earl:passed')
        atom = next(a for a in graph if a.get('earl:test', {}).get('@id', '').endswith('TS10-A03'))
        self.assertEqual(atom['earl:result']['earl:outcome']['@id'], 'earl:inapplicable')

    def test_two_families_do_not_share_a_result(self):
        rows = evaluate(self.data('canonical-two-families-separate'))
        self.assertEqual([r['outcome'] for r in rows], ['pass', 'fail'])
        self.assertNotEqual(rows[0]['target'], rows[1]['target'])

    def test_raw_mutations_change_findings_without_authored_outcomes(self):
        data = self.data(); target = data['targets'][0]; data['rules'] = ['TS10-A03']
        self.assertEqual(evaluate(data)[0]['outcome'], 'pass')
        target['sitemaps']['documents'][0]['http'][0]['response'] = target['sitemaps']['documents'][0]['http'][0]['response'].replace('/product</loc>', '/product?color=blue</loc>')
        self.assertEqual(evaluate(data)[0]['outcome'], 'fail')

    def test_review_is_bound_to_intent_context_and_exact_captures(self):
        for part in ('intent', 'context', 'documents'):
            data = self.data(); data['rules'] = ['TS10-A02']; t = data['targets'][0]
            if part == 'intent': t['intent']['canonical']['members'][1]['required_methods'] = ['http']
            elif part == 'context': t['context']['bounds'] = 'Changed bounds'
            else: t['documents'][1]['exemption_review']['reason'] = 'Different supplied review'
            with self.subTest(part=part):
                self.assertEqual(evaluate(data)[0]['outcome'], 'inconclusive')
                self.assertNotEqual(t['content_review']['source_sha256'], content_binding(t))

    def test_incomplete_or_unattributed_http_cannot_fail_destination(self):
        data = self.data('canonical-preferred-unfinished-redirect'); d = data['targets'][0]['documents'][0]
        self.assertEqual(evaluate(data)[0]['outcome'], 'fail')
        d['http'][0]['request'] = d['http'][0]['request'].replace('googlebot', 'otherbot')
        self.assertEqual(evaluate(data)[0]['outcome'], 'inconclusive')

    def test_malformed_optional_records_are_inconclusive(self):
        for field, value, rule in [('documents', None, 'TS10-A01'), ('content_review', None, 'TS10-A02'),
                                   ('sitemaps', None, 'TS10-A03'), ('crawl', None, 'TS10-A04')]:
            data = self.data(); data['targets'][0][field] = value; data['rules'] = [rule]
            with self.subTest(field=field): self.assertEqual(evaluate(data)[0]['outcome'], 'inconclusive')

    def test_repeated_identical_signals_are_retained_in_reason(self):
        row = evaluate(self.data('canonical-http-only-and-repeated-links'))[0]
        self.assertEqual(row['outcome'], 'pass')
        self.assertGreaterEqual(row['reason'].count("('https://example.com/product', True)"), 3)

    def test_all_declared_population_gaps_block_pass(self):
        for field, rule in [('documents','TS10-A01'), ('documents','TS10-A02'),
                             ('sitemaps','TS10-A03'), ('crawl','TS10-A04')]:
            data = self.data(); t = data['targets'][0]; data['rules'] = [rule]
            if field == 'documents': t[field].pop()
            else: t[field]['documents'].clear()
            with self.subTest(rule=rule): self.assertEqual(evaluate(data)[0]['outcome'], 'inconclusive')

    def test_retained_evidence_tampering_invalidates_report(self):
        report = assessed_report(self.data(), self.root)
        tsep.validate(report, self.root)
        (self.root/'intent-0.json').write_text('{}')
        with self.assertRaises(tsep.Invalid): tsep.validate(report, self.root)

    def test_rendered_canonical_requires_the_planned_states(self):
        data = self.data('canonical-content-dom-required'); t = data['targets'][0]
        self.assertEqual([a['outcome'] for a in evaluate(data)], ['pass'] * 4)
        t['documents'][1]['render']['states'].pop()
        review = t['content_review']; review['source_sha256'] = content_binding(t)
        self.assertEqual([a['outcome'] for a in evaluate(data)][:2], ['inconclusive'] * 2)


if __name__ == '__main__':
    unittest.main()
