"""TS13/TS14 authored contradictions, evidence boundaries and RC1 preservation."""
import base64
import copy
import gzip
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
from conformance import sitemap_quality as reader
from conformance.corpus import expand
from conformance.evaluate import evaluate
from reports import html

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'tests/fixtures/sitemap-quality-v1.json'


def cases():
    return json.loads(FIXTURE.read_bytes())['cases']


def data(name='complete'):
    return copy.deepcopy(next(c['input'] for c in cases() if c['id'] == 'sitemap-quality-v1-' + name))


def native(raw, encoding='identity'):
    return dict(raw_base64=base64.b64encode(raw).decode(), sha256=hashlib.sha256(raw).hexdigest(),
                encoding=encoding, complete=True)


def rebind(target):
    for doc in target.get('documents', []):
        if 'quality_review' in doc:
            doc['quality_review']['evidence_sha256'] = reader.binding(target, {k:v for k,v in doc.items() if k != 'quality_review'})
    for event in target.get('change_history', []):
        if 'review' in event:
            event['review']['evidence_sha256'] = reader.binding(target, {k:v for k,v in event.items() if k != 'review'})


class SitemapQuality(unittest.TestCase):
    def test_authored_cases_offline_and_input_preservation(self):
        self.assertEqual(len(cases()), 55)
        with patch.dict(os.environ, {}, clear=True), patch.object(socket, 'socket', side_effect=AssertionError('No network')):
            for case in cases():
                original = copy.deepcopy(case['input'])
                with self.subTest(case=case['id']):
                    actual = evaluate(case['input'])
                    self.assertEqual([r['outcome'] for r in actual], [r['outcome'] for r in case['expected']])
                    self.assertEqual(original, case['input'])

    def test_fixture_fingerprint_and_explicit_input_correction(self):
        raw = FIXTURE.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), FIXTURE.with_suffix('.sha256').read_text().strip())
        correction = json.loads((ROOT/'provenance/sitemap-quality-v1-correction.json').read_bytes())
        self.assertEqual(hashlib.sha256(raw).hexdigest(), correction['current_fixture_sha256'])
        initial = (ROOT/correction['initial_fixture_path']).read_bytes()
        self.assertEqual(hashlib.sha256(initial).hexdigest(), correction['original_fixture_sha256'])
        old = json.loads(initial)
        for case, current in zip(old['cases'], json.loads(raw)['cases']):
            self.assertEqual(case['id'], current['id'])
            expected = copy.deepcopy(case['expected'])
            for amendment in correction['expected_outcome_amendments']:
                if amendment['case_id'] == case['id']:
                    atom = next(a for a in expected if a['rule_id'] == amendment['rule_id'])
                    self.assertEqual(atom['outcome'], amendment['before'])
                    atom['outcome'] = amendment['after']
            self.assertEqual(expected, current['expected'])
        for case in old['cases']:
            if case['id'] == correction['original_case']['id']:
                self.assertEqual(case, correction['original_case'])
                target = case['input']['targets'][0]
                doc = target['documents'][0]
                doc['quality_review']['evidence_sha256'] = reader.binding(target, {k:v for k,v in doc.items() if k!='quality_review'})
        intermediate = (json.dumps(old, ensure_ascii=False, indent=2)+'\n').encode()
        self.assertEqual(hashlib.sha256(intermediate).hexdigest(), correction['corrected_fixture_sha256'])
        corpus = expand(tsep.read_json(ROOT/'conformance/cases.json'))
        self.assertEqual([c for c in corpus['cases'] if c['id'].startswith('sitemap-quality-v1-')], cases())

    def test_rc1_controls_readers_tests_and_fixtures_preserved(self):
        frozen = tsep.read_json(ROOT/'provenance/v030-rc1-preservation.json')
        protocol = tsep.read_json(tsep.PROTOCOL_PATH)
        self.assertEqual(frozen['base_commit'], '7b60c20e7ac572574f756ad92531e0c46f7b83e7')
        self.assertEqual(protocol['version'], '0.3.0-draft.3')
        previous = tsep.read_json(ROOT/'provenance/v030-draft1-rule-baseline.json')['new_control_previous_versions']
        next_baseline = tsep.read_json(ROOT/'provenance/v030-draft2-rule-baseline.json')
        previous.update(next_baseline['new_control_previous_versions'])
        for control in protocol['controls']:
            if control['id'] not in ('TS13', 'TS14'):
                restored = copy.deepcopy(control)
                if control['id'] in previous:
                    restored.pop('rules')
                    restored['rule_version'] = previous[control['id']]
                    restored.update(next_baseline['previous_control_fields'].get(control['id'], {}))
                self.assertEqual(reader.digest(restored), frozen['control_sha256'][control['id']], control['id'])
            else:
                self.assertEqual(control['rule_version'], '0.3.0-draft.1')
        overlays = tsep.read_json(ROOT/'provenance/ts25-runtime-test-overlay-v1.json')['updates']
        overlays += tsep.read_json(ROOT/'provenance/v030-indexing-locale-integration-overlay.json')['updates']
        for name, sha in frozen['preserved_files'].items():
            raw = (ROOT/name).read_bytes()
            for update in overlays:
                if update['path'] == name:
                    self.assertEqual(hashlib.sha256(raw).hexdigest(), update['current_sha256'])
                    text = raw.decode('utf-8')
                    for change in reversed(update['replacements']):
                        self.assertEqual(text.count(change['after']), 1)
                        text = text.replace(change['after'], change['before'])
                    raw = text.encode('utf-8')
                    self.assertEqual(hashlib.sha256(raw).hexdigest(), update['base_sha256'])
            self.assertEqual(hashlib.sha256(raw).hexdigest(), sha, name)
        extension = tsep.read_json(ROOT/'provenance/v030-url-policy-integration-overlay.json')['updates']
        extension += tsep.read_json(ROOT/'provenance/v030-indexing-locale-integration-overlay.json')['updates']
        for update in frozen['integration_test_updates']:
            current = (ROOT/update['path']).read_text()
            for addition in reversed(extension):
                if addition['path'] == update['path']:
                    self.assertEqual(hashlib.sha256(current.encode()).hexdigest(), addition['current_sha256'])
                    for change in reversed(addition['replacements']):
                        self.assertEqual(current.count(change['after']), 1)
                        current = current.replace(change['after'], change['before'])
                    self.assertEqual(hashlib.sha256(current.encode()).hexdigest(), addition['base_sha256'])
            self.assertEqual(current.count(update['after']), 1)
            restored = current.replace(update['after'], update['before']).encode('utf-8')
            self.assertEqual(hashlib.sha256(restored).hexdigest(), update['base_sha256'])
        corpus = tsep.read_json(ROOT/'conformance/cases.json')
        self.assertEqual(reader.digest(corpus['cases']), frozen['core_cases_sha256'])
        refs = frozen['additional_case_files']
        self.assertEqual(corpus['additional_case_files'][:len(refs)], refs)
        methods = tsep.read_json(ROOT/'tests/fixtures/control-cases.json')
        self.assertEqual(reader.digest(methods['cases'][:frozen['method_cases_count']]), frozen['method_cases_sha256'])
        self.assertEqual(sum(len(c.get('rules', [])) for c in protocol['controls']), 85)

    def test_export_replay_c_nc_nt_and_partial_rules(self):
        scenarios = [('complete', 'C', 'C'), ('noindex', 'NC', 'C'),
                     ('missing-page', 'NT', 'C'), ('missing-history', 'C', 'NT'),
                     ('file-generation-only', 'C', 'NC'), ('no-lastmod', 'C', 'NT'),
                     ('contradiction-with-missing-file', 'NC', 'NC')]
        for name, ts13, ts14 in scenarios:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as folder:
                root = Path(folder); source = root/'input.json'
                source.write_text(json.dumps(data(name)))
                original = source.read_bytes()
                captures.build(source, root/'bundle', assessor='Fictional operator', label='SYNTHETIC TS13/TS14',
                               selection_method='Authored files only; no site audit', access='synthetic')
                report = tsep.read_json(root/'bundle/report.json')
                self.assertEqual({r['control_id']:r['status'] for r in report['results']}, {'TS13':ts13, 'TS14':ts14})
                self.assertEqual((root/'bundle/input.json').read_bytes(), original)
                self.assertTrue(tsep.decision(report)['synthetic_evidence'])
                self.assertIn('sitemap_quality_interpretation', tsep.decision(report))
                kinds = {a['kind'] for a in report['artifacts']}
                self.assertTrue({'sitemap','intent','change-history'} <= kinds)
                if name == 'missing-page':
                    self.assertNotIn('html', kinds)  # Never manufacture missing HTML.
                else:
                    self.assertTrue({'http','html'} <= kinds)
                with patch.object(socket, 'socket', side_effect=AssertionError('Offline replay')):
                    replayed = replay.replay(root/'bundle', root/'replayed')
                self.assertTrue(replayed['same_atomic_results']); self.assertTrue(replayed['same_gate'])
                for lang in ('fr', 'en'):
                    self.assertIn('TS13-A02', html.render(root/'bundle/report.json', language=lang))
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); source = root/'input.json'; payload = data(); payload['rules'] = ['TS13-A01']
            source.write_text(json.dumps(payload))
            captures.build(source, root/'partial', assessor='Fictional', label='Synthetic partial rule', selection_method='Authored', access='synthetic')
            self.assertEqual(tsep.read_json(root/'partial/report.json')['results'][0]['status'], 'NT')

    def test_integrity_and_synthetic_relabeling_refused_before_output(self):
        for component in ('file', 'event'):
            with self.subTest(component=component), tempfile.TemporaryDirectory() as folder:
                root = Path(folder); payload = data(); target = payload['targets'][0]
                record = target['sitemap_files'][0]['native'] if component == 'file' else target['change_history'][0]['event']
                record['sha256'] = '0'*64
                with self.assertRaises(tsep.Invalid): evaluate(payload)
                source = root/'input.json'; source.write_text(json.dumps(payload))
                with self.assertRaises(tsep.Invalid):
                    captures.build(source, root/'bad', assessor='Fictional', label='Synthetic corrupt', selection_method='Authored', access='synthetic')
                self.assertFalse((root/'bad').exists())
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); source = root/'input.json'; source.write_text(json.dumps(data()))
            with self.assertRaises(tsep.Invalid):
                captures.build(source, root/'relabel', assessor='Fictional', label='Cannot relabel', selection_method='Authored', access='public')
            self.assertFalse((root/'relabel').exists())

    def test_gzip_and_index_leaf_path(self):
        payload = data(); target = payload['targets'][0]
        original = target['sitemap_files'][0]
        leaf_url = 'https://synthetic.invalid/leaf.xml'
        leaf = copy.deepcopy(original); leaf['url'] = leaf_url
        raw = base64.b64decode(leaf['native']['raw_base64'])
        leaf['native'] = native(gzip.compress(raw, mtime=0), 'gzip')
        index = ('<sitemapindex xmlns="'+reader.sitemap_files.NS+'"><sitemap><loc>'+leaf_url+'</loc><lastmod>2000-01-01</lastmod></sitemap></sitemapindex>').encode()
        original['native'] = native(index)
        target['sitemap_files'].append(leaf)
        target['intent']['sitemap_files']['documents'].append(leaf_url)
        target['change_history'][0]['file_url'] = leaf_url
        rebind(target)
        self.assertEqual([r['outcome'] for r in evaluate(payload)], ['pass']*3)

    def test_entry_bound_and_unsupported_formats_never_pass(self):
        for count, expected in ((128, 'pass'), (129, 'inconclusive')):
            payload = data(); target = payload['targets'][0]; payload['rules'] = ['TS13-A01']
            raw = ('<urlset xmlns="'+reader.sitemap_files.NS+'">'+('<url><loc>https://synthetic.invalid/a</loc></url>'*count)+'</urlset>').encode()
            target['sitemap_files'][0]['native'] = native(raw)
            self.assertEqual(evaluate(payload)[0]['outcome'], expected)
        for value in (None, False, [], {}, 'unsupported'):
            for key in ('intent', 'context', 'sitemap_files'):
                target = data()['targets'][0]; target[key] = value
                for rule in reader.RULES:
                    with self.subTest(key=key, value=value, rule=rule):
                        self.assertEqual(reader.assess(target, rule)[0], 'inconclusive')

    def test_review_qualification_and_native_event_boundaries(self):
        for kind in ('quality_review', 'review'):
            for field, value in [('reviewer',''), ('reason',' '*10), ('reviewed_at','2026-10-15T07:00:00Z'),
                                 ('reviewed_at','2026-10-15T13:00:00Z'), ('reason','é'*4097), ('judgment','unknown')]:
                payload = data(); target = payload['targets'][0]
                record = target['documents'][0] if kind == 'quality_review' else target['change_history'][0]
                record[kind][field] = value
                rule = 'TS13-A02' if kind == 'quality_review' else 'TS14-A01'
                with self.subTest(kind=kind, field=field, value=str(value)[:30]):
                    self.assertEqual(reader.assess(target, rule)[0], 'inconclusive')
        for raw in (b'{}', b'false', b'[]', b'{invalid}', b'\xff', b' '*32769):
            target = data()['targets'][0]; target['change_history'][0]['event'] = native(raw); rebind(target)
            self.assertEqual(reader.assess(target, 'TS14-A01')[0], 'inconclusive')

    def test_http_contradiction_survives_missing_review_and_source(self):
        for name in ('noindex', 'other-canonical', 'redirect', 'not-found'):
            target = data(name)['targets'][0]; target['documents'][0].pop('quality_review')
            self.assertEqual(reader.assess(target, 'TS13-A02')[0], 'fail')
        target = data('http-noindex')['targets'][0]
        response = target['documents'][0]['http'][0]['response']
        body = '<html><head></head><body><template>unsupported</template></body></html>'
        head = response.split('\r\n\r\n')[0]
        import re
        head = re.sub(r'Content-Length: \d+', 'Content-Length: '+str(len(body)), head)
        target['documents'][0]['http'][0]['response'] = head+'\r\n\r\n'+body
        self.assertEqual(reader.assess(target, 'TS13-A02')[0], 'fail')

    def test_sources_bound_to_adapter(self):
        self.assertIn('conformance/sitemap_quality.py', captures.source_files())

    def test_unknown_date_precision_is_not_a_calendar_defect(self):
        for value in ('2026-10', '2026-10-14T14:00:00', '2026-10-14T14:00:00.123456789Z'):
            target = data()['targets'][0]
            record = target['sitemap_files'][0]
            raw = base64.b64decode(record['native']['raw_base64']).replace(b'<lastmod>2026-10-14</lastmod>', ('<lastmod>'+value+'</lastmod>').encode())
            record['native'] = native(raw); rebind(target)
            with self.subTest(value=value):
                self.assertEqual(reader.assess(target, 'TS14-A01')[0], 'inconclusive')

    def test_utc_day_is_not_capture_local_day(self):
        for captured, changed, day, expected in (
            ('2026-10-15T23:30:00-02:00', '2026-10-16T01:00:00Z', '2026-10-16', 'pass'),
            ('2026-10-16T00:30:00+02:00', None, '2026-10-16', 'fail'),
        ):
            target = data()['targets'][0]
            target['observed_at'] = '2026-10-16T12:00:00Z'
            target['intent']['declared_at'] = '2026-10-15T20:00:00Z'
            target['intent']['sitemap_files']['window_start'] = '2026-10-15T21:00:00Z'
            target['intent']['sitemap_files']['window_end'] = '2026-10-16T11:00:00Z'
            target['documents'][0]['observed_at'] = '2026-10-16T10:05:00Z'
            target['documents'][0]['quality_review']['reviewed_at'] = '2026-10-16T11:30:00Z'
            target['change_history'][0]['review']['reviewed_at'] = '2026-10-16T11:30:00Z'
            record = target['sitemap_files'][0]
            record['observed_at'] = captured
            raw = base64.b64decode(record['native']['raw_base64']).replace(b'2026-10-14', day.encode())
            record['native'] = native(raw)
            if changed is None:
                target['change_history'] = []
            else:
                event = target['change_history'][0]
                payload = json.loads(base64.b64decode(event['event']['raw_base64']))
                payload['changed_at'] = changed
                event['event'] = native(json.dumps(payload).encode())
            rebind(target)
            with self.subTest(captured=captured):
                self.assertEqual(reader.assess(target, 'TS14-A01')[0], expected)

    def test_review_follows_all_bound_files(self):
        target = data()['targets'][0]
        file = copy.deepcopy(target['sitemap_files'][0])
        file.update(url='https://synthetic.invalid/second.xml', observed_at='2026-10-15T10:55:00Z')
        target['sitemap_files'].append(file)
        for field in ('documents', 'roots'):
            target['intent']['sitemap_files'][field].append(file['url'])
        target['documents'][0]['quality_review']['reviewed_at'] = '2026-10-15T10:30:00Z'
        rebind(target)
        self.assertEqual(reader.assess(target, 'TS13-A02')[0], 'inconclusive')


if __name__ == '__main__':
    unittest.main()
