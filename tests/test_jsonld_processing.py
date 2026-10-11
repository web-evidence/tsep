"""Input/attribution/replay boundaries; actual Node qualification is separate.

The retained observations came from explicit Node 24 runs over authored fixtures.
These Python-only tests do not silently claim to re-execute the processor.
"""
import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from experiments import jsonld_processing as reader
from scripts.jsonld_processing_check import compare, fixture


class JsonLdProcessing(unittest.TestCase):
    def request(self, raw='{}'):
        return {'documents': [{'id': 'doc', 'base_iri': 'https://example.test/page',
                               'raw_json': raw, 'contexts': []}]}

    def observed(self, boundary=False):
        prefix = 'jsonld-processing-boundaries' if boundary else 'jsonld-processing'
        return fixture(prefix + '-observation-v1.json')[0]

    def test_frozen_documents_match_retained_actual_processing(self):
        for prefix, boundary, count in [('jsonld-processing', False, 40),
                                         ('jsonld-processing-boundaries', True, 8)]:
            cases, _ = fixture(prefix + '-v1.json')
            observed = self.observed(boundary)
            reader.validate(observed, reader.prepare(observed['input']))
            rows = compare(cases['cases'], observed)
            self.assertEqual(len(rows), count)
            self.assertTrue(all(c['matches'] for c in rows))
            self.assertEqual(observed['normative_effect'], 'none')

    def test_duplicate_keys_and_non_json_values_are_not_repaired(self):
        for raw in ['{"a":1,"a":2}', '{"a":{"b":1,"b":2}}',
                    '{"@value":NaN}', '{"@value":Infinity}', '/* x */ {}', '{']:
            with self.subTest(raw=raw):
                row = reader.prepare(self.request(raw))['documents'][0]
                self.assertEqual(row['pre_error']['status'], 'json-error')

    def test_unsafe_integer_and_nonfinite_exponent_are_not_rounded_into_evidence(self):
        for number in ['9007199254740992', '-9007199254740992', '1e999', '1e20', '-9e20']:
            row = reader.prepare(self.request('{"@value":' + number + '}'))['documents'][0]
            self.assertEqual(row['pre_error']['status'], 'unsupported-input')
        for number in ['9007199254740991', '-9007199254740991', '1.25', '1e3']:
            self.assertIsNone(reader.prepare(self.request('{"@value":' + number + '}'))['documents'][0]['pre_error'])

    def test_root_url_cannot_trigger_document_loader(self):
        for raw in ['"https://example.test/private"', 'null', '123', 'true']:
            self.assertEqual(reader.prepare(self.request(raw))['documents'][0]['pre_error']['status'], 'unsupported-input')

    def test_surrogates_in_keys_values_and_contexts_are_rejected(self):
        for raw in ['{"\\ud800":"x"}', '{"name":"\\udfff"}']:
            row = reader.prepare(self.request(raw))['documents'][0]
            self.assertEqual(row['pre_error']['status'], 'unsupported-input')
        request = self.request()
        raw = '{"@context":{"\\ud800":"https://schema.org/name"}}'
        request['documents'][0]['contexts'] = [{'url': 'https://example.test/context',
                                                'raw_json': raw, 'sha256': reader.sha(raw)}]
        with self.assertRaises(UnicodeError):
            reader.prepare(request)

    def test_depth_and_document_bounds_do_not_return_empty_success(self):
        deep = '[' * 66 + '0' + ']' * 66
        self.assertEqual(reader.prepare(self.request(deep))['documents'][0]['pre_error']['status'], 'unsupported-input')
        for raw in [' ' * (128 * 1024 + 1), 'é' * 65537]:
            with self.assertRaisesRegex(ValueError, 'byte bound'):
                reader.prepare(self.request(raw))

    def test_population_and_request_shape_are_explicit(self):
        original = self.request()
        for request in [{}, {'documents': []}, {'documents': original['documents'] * 2},
                        dict(original, ignored='x'), {'documents': original['documents'] * 65}]:
            with self.subTest(request=list(request)), self.assertRaises(ValueError):
                reader.prepare(request)
        for field in ['id', 'base_iri', 'raw_json', 'contexts']:
            request = self.request(); del request['documents'][0][field]
            with self.assertRaises(ValueError):reader.prepare(request)

    def test_declared_base_does_not_accept_ambiguous_urls(self):
        for value in ['relative', 'file:///tmp/context', 'https://user:pass@example.test/',
                      'https://example.test:bogus/', 'https://example.test/\x00x',
                      'https://example.test\\x/', 'https://example.test/a b']:
            request = self.request(); request['documents'][0]['base_iri'] = value
            with self.subTest(value=value), self.assertRaises(ValueError):reader.prepare(request)

    def test_context_fingerprint_population_and_json_are_checked_before_launch(self):
        request = self.request()
        context = {'url': 'https://example.test/context', 'raw_json': '{"@context":{}}',
                   'sha256': reader.sha('{"@context":{}}')}
        request['documents'][0]['contexts'] = [context]
        reader.prepare(request)
        for mode in ['hash', 'duplicate', 'missing-context-key', 'invalid-json']:
            changed = copy.deepcopy(request)
            if mode == 'hash':changed['documents'][0]['contexts'][0]['sha256'] = '0' * 64
            elif mode == 'duplicate':changed['documents'][0]['contexts'] *= 2
            else:
                raw = '{}' if mode == 'missing-context-key' else '{'
                changed['documents'][0]['contexts'][0].update(raw_json=raw, sha256=reader.sha(raw))
            with self.subTest(mode=mode), patch.object(reader.subprocess, 'run') as run:
                with self.assertRaises(ValueError):reader.observe(changed, node='/missing/node')
                run.assert_not_called()

    def test_context_budget_accepts_large_vocabulary_without_removing_bound(self):
        # Authored context larger than the observed 210,636-byte Schema.org file.
        # The actual downloaded file is qualified separately with retained bytes.
        request = self.request()
        raw = json.dumps({'@context': {'term' + str(i): 'https://example.test/term' + str(i)
                                      for i in range(6000)}})
        self.assertGreater(len(raw.encode()), 210636)
        context = {'url': 'https://example.test/context', 'raw_json': raw, 'sha256': reader.sha(raw)}
        request['documents'][0]['contexts'] = [context]
        reader.prepare(request)
        raw = json.dumps({'@context': {}}) + ' ' * (1024 * 1024)
        context.update(raw_json=raw, sha256=reader.sha(raw))
        with self.assertRaisesRegex(ValueError, 'Context byte bound'):reader.prepare(request)

    def test_raw_entity_text_and_repeated_id_values_remain_observations(self):
        rows = {r['id']: r for r in self.observed()['documents']}
        self.assertIn('A &amp; B', json.dumps(rows['raw-script-entity-remains-literal']['expanded']))
        names = rows['same-id-multiple-values']['flattened'][0]['https://schema.org/name']
        self.assertEqual(len(names), 2)
        self.assertNotIn('outcome', rows['same-id-multiple-values'])

    def test_same_context_url_does_not_cross_document_boundaries(self):
        rows = {r['id']: r for r in self.observed(True)['documents']}
        self.assertIn('https://schema.org/name', rows['cache-first-document']['expanded'][0])
        self.assertIn('https://example.test/label', rows['cache-changed-document']['expanded'][0])
        self.assertEqual(rows['cache-missing-document']['status'], 'unavailable')
        self.assertTrue(any(not c['supplied'] for c in rows['cache-missing-document']['context_loads']))

    def test_mutated_document_bindings_are_rejected(self):
        original = self.observed(); prepared = reader.prepare(original['input'])
        mutations = [lambda r:r.update(id='other'), lambda r:r.update(base_iri='https://other.test/'),
                     lambda r:r.update(raw_json_sha256='0' * 64), lambda r:r.update(contexts=[])]
        for mutate in mutations:
            changed = copy.deepcopy(original); mutate(changed['documents'][1])
            with self.assertRaises(ValueError):reader.validate(changed, prepared)

    def test_missing_context_is_not_laundered_into_success(self):
        original = self.observed(); prepared = reader.prepare(original['input'])
        changed = copy.deepcopy(original)
        row = next(r for r in changed['documents'] if r['id'] == 'missing-context')
        row.update(status='observed', expanded=[], flattened=[], error=None)
        with self.assertRaisesRegex(ValueError, 'unavailable context'):reader.validate(changed, prepared)

    def test_changed_context_trace_is_rejected(self):
        original = self.observed(); prepared = reader.prepare(original['input'])
        for change in [{'sha256': '0' * 64}, {'supplied': False}, {'url': 'https://wrong.test/'}, {'phase': 'other'}]:
            changed = copy.deepcopy(original); changed['documents'][1]['context_loads'][0].update(change)
            with self.assertRaises(ValueError):reader.validate(changed, prepared)

    def test_unavailable_and_pre_rejected_results_cannot_claim_graphs(self):
        original = self.observed(); prepared = reader.prepare(original['input'])
        for status in ['unavailable', 'json-error', 'unsupported-input', 'processor-error']:
            changed = copy.deepcopy(original)
            next(r for r in changed['documents'] if r['status'] == status)['expanded'] = []
            with self.subTest(status=status), self.assertRaises(ValueError):reader.validate(changed, prepared)

    def test_notice_and_error_boundaries_remain_explicit(self):
        original = self.observed(); prepared = reader.prepare(original['input'])
        changed = copy.deepcopy(original)
        row = next(r for r in changed['documents'] if r['notices'])
        row['notices'][0]['level'] = 'pass'
        with self.assertRaises(ValueError):reader.validate(changed, prepared)
        changed = copy.deepcopy(original)
        next(r for r in changed['documents'] if r['status'] == 'processor-error')['error'] = {'message': 'x'}
        with self.assertRaises(ValueError):reader.validate(changed, prepared)

    def test_full_request_hash_and_population_are_required(self):
        original = self.observed(); prepared = reader.prepare(original['input'])
        for mutation in [lambda r:r.update(request_sha256='0'*64), lambda r:r['documents'].pop(),
                         lambda r:r.update(normative_effect='pass'), lambda r:r['runtime'].update(node='v18.0.0')]:
            changed = copy.deepcopy(original); mutation(changed)
            with self.assertRaises(ValueError):reader.validate(changed, prepared)

    def test_pinned_archive_and_license_are_verified_without_installing(self):
        self.assertEqual(reader.sha(reader.package()), reader.MEMBER_SHA)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); target = root/'third_party/jsonld'
            shutil.copytree(reader.ROOT/'third_party/jsonld', target)
            (target/'LICENSE').write_text('changed')
            with self.assertRaisesRegex(ValueError, 'license differs'):reader.package(root)

    def test_corrupt_archive_and_inventory_are_refused(self):
        for mode in ['archive', 'manifest']:
            with tempfile.TemporaryDirectory() as folder:
                root = Path(folder); target = root/'third_party/jsonld'
                shutil.copytree(reader.ROOT/'third_party/jsonld', target)
                if mode == 'archive':(target/'jsonld-9.0.0.tgz').write_bytes(b'not the processor')
                else:
                    p = target/'packages.json'; value=json.loads(p.read_bytes())
                    del value['packages'][0]['files']['README.md']; p.write_text(json.dumps(value))
                with self.assertRaises(ValueError):reader.package(root)

    def test_missing_runtime_never_falls_back(self):
        with self.assertRaisesRegex(ValueError, 'unavailable'):
            reader.observe(self.request(), node='/nonexistent/jsonld-node24')

    def test_timeout_environment_and_permissions(self):
        with patch.object(reader.shutil, 'which', return_value='/synthetic/node'), \
             patch.object(reader.subprocess, 'run', side_effect=subprocess.TimeoutExpired('node', 30)) as run, \
             patch.dict(os.environ, {'NODE_OPTIONS': '--import unexpected', 'NODE_PATH': '/unexpected'}):
            with self.assertRaisesRegex(ValueError, 'deadline'):reader.observe(self.request(), node='node')
        self.assertFalse(any(k.startswith('NODE_') for k in run.call_args.kwargs['env']))
        self.assertIn('--permission', run.call_args.args[0])
        self.assertIn('--no-addons', run.call_args.args[0])
        self.assertIn('--disallow-code-generation-from-strings', run.call_args.args[0])
        self.assertEqual(run.call_args.kwargs['stdin'], subprocess.DEVNULL)

    def test_process_failure_retains_failure_without_fallback(self):
        with patch.object(reader.shutil, 'which', return_value='/synthetic/node'), \
             patch.object(reader.subprocess, 'run', return_value=subprocess.CompletedProcess('node', 1)):
            with self.assertRaisesRegex(ValueError, 'worker failed'):reader.observe(self.request(), node='node')

    def test_replay_requires_exact_sources_before_reexecution(self):
        observed = self.observed(); observed['source_sha256'] = {}
        with patch.object(reader, 'observe') as run:
            with self.assertRaisesRegex(ValueError, 'sources differ'):reader.replay(observed, node='node')
            run.assert_not_called()

    def test_structural_checks_alone_cannot_detect_fabricated_graph(self):
        observed = self.observed(); observed['source_sha256'] = reader.identity()
        tampered = copy.deepcopy(observed)
        tampered['documents'][0]['expanded'] = []
        # This is deliberately only a shape/attribution check, not authentication.
        reader.validate(tampered, reader.prepare(tampered['input']))
        with patch.object(reader, 'observe', return_value=observed):
            with self.assertRaisesRegex(ValueError, 'Recomputed observation differs'):
                reader.replay(tampered, node='node')

    def test_replay_does_not_silently_ignore_runtime_changes(self):
        observed = self.observed(); observed['source_sha256'] = reader.identity()
        changed = copy.deepcopy(observed); changed['runtime']['node'] = 'v24.99.0'
        with patch.object(reader, 'observe', return_value=changed):
            with self.assertRaisesRegex(ValueError, 'differs'):reader.replay(observed, node='node')

    def test_cli_refuses_existing_output_before_reading_input(self):
        with tempfile.TemporaryDirectory() as folder:
            output=Path(folder)/'existing.json'; output.write_text('keep')
            with patch('sys.argv', ['jsonld_processing', '/missing/input', '--node', '/missing/node', '--output', str(output)]), \
                 patch('sys.stderr'):
                self.assertEqual(reader.main(), 64)
            self.assertEqual(output.read_text(), 'keep')


if __name__ == '__main__':
    unittest.main()
