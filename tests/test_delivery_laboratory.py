"""Actual cache/origin experiments and offline evidence tampering checks."""
import json
from pathlib import Path
import shutil
import socket
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import tsep
from collectors import ts01
from conformance.http import encoded, raw_bytes, message
from examples import delivery_laboratory as lab
from examples import delivery_cache_transport as transport


class DeliveryLaboratory(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(); cls.addClassCleanup(cls.temp.cleanup)
        cls.original = Path(cls.temp.name) / 'experiment'
        with patch.object(socket, 'getaddrinfo', side_effect=AssertionError('DNS forbidden')), \
             patch.object(socket, 'getfqdn', side_effect=AssertionError('DNS forbidden')):
            cls.result = lab.run(cls.original)

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'copy'; shutil.copytree(self.original, self.root)

    def rehash(self, root=None):
        root = root or self.root
        names = [line.split('  ', 1)[1] for line in (root / 'SHA256SUMS').read_text().splitlines()]
        (root / 'SHA256SUMS').unlink(); ts01.manifest(root, names)

    def change(self, name, fn):
        path = self.root / name; data = tsep.read_json(path); fn(data)
        path.write_text(json.dumps(data, ensure_ascii=False) + '\n'); self.rehash()

    def offline(self):
        with patch.object(socket, 'socket', side_effect=AssertionError('No network')), \
             patch.object(socket, 'getaddrinfo', side_effect=AssertionError('No DNS')), \
             patch.object(subprocess, 'Popen', side_effect=AssertionError('No process')), \
             patch.object(transport, 'purge', side_effect=AssertionError('No cache operation')):
            return lab.replay(self.root)

    def rows(self, name):
        return [r for r in tsep.read_json(self.root / 'edge.json') if r['phase'] == name and r['url'].endswith('/page')]

    def test_actual_population_and_prefrozen_expectations(self):
        result = self.result
        self.assertEqual((result['actual_edge_requests'], result['actual_origin_requests'], result['actual_total_http_requests']), (24, 14, 38))
        self.assertTrue(result['all_expectations_matched'])
        self.assertEqual([r['actual']['control_status'] for r in result['cases']], ['C', 'NC', 'NC', 'C', 'NC', 'C', 'NT', 'C'])
        rows = tsep.read_json(self.root / 'edge.json')
        self.assertEqual([sum(r['action'] == a for r in rows) for a in ('store', 'serve', 'bypass')], [11, 10, 3])
        self.assertFalse(result['human_review_performed']); self.assertFalse(result['browser_observed'])
        self.assertFalse(result['actual_operator_visit_established'])
        self.assertEqual(tsep.digest(lab.ROOT / lab.FIXTURE), '566d00ae63234985d89c4d4f8217d15129c74666e3d7c4c6afa52fa7dfa62e44')

    def test_offline_exact_replay_without_network_process_or_cache_operation(self):
        replay = self.offline()
        self.assertTrue(replay['same_observations_and_results']); self.assertTrue(replay['all_expectations_matched'])
        self.assertEqual((replay['cases'], replay['network_requests']), (8, 0))

    def test_bad_reuse_can_fail_with_identical_body(self):
        rows = self.rows('identical-body-bad-reuse')
        self.assertEqual(message(rows[0]['response'], True)[2], message(rows[1]['response'], True)[2])
        self.assertEqual([r['action'] for r in rows], ['store', 'serve'])
        self.assertEqual(rows[0]['entry_id'], rows[1]['entry_id'])
        self.assertNotEqual(rows[0]['request'], rows[1]['request'])
        actual = next(c['actual'] for c in self.result['cases'] if c['id'] == 'identical-body-bad-reuse')
        self.assertEqual(actual['atomic_outcomes'], ['pass', 'pass', 'fail'])

    def test_origin_error_and_wrong_cached_language_have_distinct_causes(self):
        wrong = self.rows('wrong-language'); origin = self.rows('origin-canonical-error')
        self.assertEqual(sum(r['origin_exchange'] is not None for r in wrong), 1)
        self.assertIn(b'lang="de"', message(wrong[1]['response'], True)[2])
        self.assertNotIn(b'Accept-Language:', raw_bytes(wrong[1]['request']))
        self.assertEqual([r['action'] for r in origin], ['bypass', 'bypass'])
        for row in origin:
            self.assertEqual(row['response'], row['origin_exchange']['response'])
            self.assertIn(b'/wrong', message(row['response'], True)[2])

    def test_repair_records_old_entry_configuration_change_and_explicit_purge(self):
        operations = tsep.read_json(self.root / 'operations.json')
        config, purge = [r for r in operations if r['phase'] == 'repair-purged']
        self.assertTrue(config['before']); self.assertEqual(config['before'], config['after'])
        self.assertEqual(json.loads(config['previous_raw'])['mode'], 'ignore-vary')
        self.assertEqual(json.loads(config['new_raw'])['mode'], 'honor')
        self.assertEqual(purge['before'], config['after']); self.assertEqual(purge['after'], [])
        self.assertEqual(purge['reason'], 'explicit-repair-purge')
        self.assertEqual({r['url'] for r in self.rows('wrong-language')}, {r['url'] for r in self.rows('repair-purged')})
        self.assertEqual([r['action'] for r in self.rows('repair-purged')], ['store', 'store', 'serve'])

    def test_gzip_etag_difference_is_legitimate_with_same_decoded_body(self):
        rows = self.rows('encoding-variants'); first, third = rows[0], rows[2]
        _, f1, body1 = message(first['response'], True); _, f3, body3 = message(third['response'], True)
        self.assertEqual(body1, body3); self.assertNotEqual(f1['etag'], f3['etag'])
        self.assertNotEqual(raw_bytes(first['response']).split(b'\r\n\r\n', 1)[1], raw_bytes(third['response']).split(b'\r\n\r\n', 1)[1])
        self.assertEqual(f3['content-encoding'], ['gzip']); self.assertNotIn('content-encoding', f1)

    def test_withheld_linkage_remains_unknown_despite_retained_laboratory_trace(self):
        name = 'linkage-withheld'; target = tsep.read_json(self.root / name / 'input.json')['targets'][0]
        self.assertEqual(target['delivery_cache_records'], [])
        self.assertEqual([s['id'] for s in target['delivery_sources']], ['configuration'])
        self.assertEqual([r['action'] for r in self.rows(name)], ['store', 'serve'])
        result = next(c for c in self.result['cases'] if c['id'] == name)
        self.assertTrue(result['cache_evidence_withheld']); self.assertEqual(result['actual']['control_status'], 'NT')

    def test_received_cookie_rejected_even_with_matching_client_and_server_hashes(self):
        def poison(d):
            r = d['phases'][0]['http'][0]
            r['request'] = encoded(raw_bytes(r['request']).replace(b'Connection:', b'Cookie: injected=1\r\nConnection:'))
        self.change('exchanges.json', poison)
        request = tsep.read_json(self.root / 'exchanges.json')['phases'][0]['http'][0]['request']
        self.change('edge.json', lambda d: d[1].update(request=request))
        with self.assertRaisesRegex(ValueError, 'exact closed request'): self.offline()

    def test_origin_bytes_rejected_after_consistent_forwarded_hash_change(self):
        origin = tsep.read_json(self.root / 'origin.json')
        raw = raw_bytes(origin[0]['response']).replace(b'Disallow:', b'Xisallow:')
        changed = encoded(raw)
        self.change('origin.json', lambda d: d[0].update(response=changed))
        self.change('edge.json', lambda d: d[0]['origin_exchange'].update(response=changed))
        with self.assertRaisesRegex(ValueError, 'Origin bytes'): self.offline()

    def test_robots_response_must_be_the_forwarded_origin_response(self):
        rows = tsep.read_json(self.root / 'edge.json')
        changed = encoded(raw_bytes(rows[0]['response']).replace(b'Disallow:', b'Xisallow:'))
        self.change('edge.json', lambda d: d[0].update(response=changed))
        self.change('exchanges.json', lambda d: d['robots'].update(response=changed))
        reg = tsep.read_json(self.root / 'registration.json')
        with self.assertRaisesRegex(ValueError, 'Robots exchange'):
            lab.check_capture(reg, tsep.read_json(self.root / 'exchanges.json'), tsep.read_json(self.root / 'edge.json'),
                tsep.read_json(self.root / 'origin.json'), tsep.read_json(self.root / 'operations.json'), tsep.read_json(self.root / 'receipt.json'))

    def test_reuse_entry_link_cannot_be_rewritten(self):
        self.change('edge.json', lambda d: d[2]['cache_event'].update(entry_id='invented-entry'))
        with self.assertRaisesRegex(ValueError, 'Cache event/entry/bytes'): self.offline()

    def test_age_cannot_be_rewritten_even_with_root_rehash(self):
        self.change('edge.json', lambda d: d[2]['cache_event'].update(current_age_ns=0))
        with self.assertRaisesRegex(ValueError, 'Cache event/entry/bytes'): self.offline()

    def test_missing_purge_rejected(self):
        self.change('operations.json', lambda d: d.pop(7))
        with self.assertRaisesRegex(ValueError, 'Configuration/purge population'): self.offline()

    def test_late_configuration_rejected(self):
        self.change('operations.json', lambda d: d[6].update(started_at='2099-01-01T00:00:00Z'))
        with self.assertRaisesRegex(ValueError, 'Configuration/purge chronology'): self.offline()

    def test_unplanned_extra_file_or_symlink_rejected(self):
        extra = self.root / 'unlisted.txt'; extra.write_text('extra')
        with self.assertRaisesRegex(ValueError, 'Extra or symlink'): self.offline()
        extra.unlink(); extra.symlink_to(self.root / 'results.json')
        with self.assertRaises(ValueError): self.offline()

    def test_source_and_prior_plan_changes_are_rejected(self):
        with patch.object(lab, 'sources', return_value=dict(lab.sources(), **{'examples/delivery_laboratory.py': '0'*64})):
            with self.assertRaisesRegex(ValueError, 'source or provenance'): self.offline()
        self.change('registration.json', lambda d: d['plans']['vary-correct']['intent']['delivery']['cells'][0]['expectation'].update(language='de'))
        with self.assertRaisesRegex(ValueError, 'Registered delivery plans'): self.offline()

    def test_authored_report_cannot_be_relabeled_human(self):
        folder = self.root / 'vary-correct' / 'bundle'; report = tsep.read_json(folder / 'report.json')
        report['assessor']['name'] = 'Invented human approver'; (folder / 'report.json').write_text(json.dumps(report) + '\n')
        self.rehash(folder); self.rehash()
        with self.assertRaisesRegex(ValueError, 'Synthetic report identity'): self.offline()

    def test_foreign_destination_rejected_before_connection(self):
        with patch.object(socket, 'socket', side_effect=AssertionError('No socket')):
            for base in ['https://example.test', 'http://localhost:80', 'http://127.0.0.1:80@evil.test', 'http://127.0.0.1:65536']:
                with self.subTest(base=base), self.assertRaises(ValueError): transport.fetch(base, '/page')

    def test_interruption_retains_completed_http_and_refuses_success_manifest(self):
        original = transport.fetch
        def interrupted(base, path, language=None, encoding='identity'):
            if path == '/page': raise OSError('Injected interruption after robots')
            return original(base, path, language, encoding)
        output = Path(self.tmp.name) / 'interrupted'
        with patch.object(transport, 'fetch', side_effect=interrupted), self.assertRaisesRegex(OSError, 'Injected interruption'):
            lab.run(output)
        self.assertEqual(len(tsep.read_json(output / 'edge.json')), 1)
        self.assertEqual(len(tsep.read_json(output / 'origin.json')), 1)
        self.assertFalse(tsep.read_json(output / 'failure.json')['complete'])
        self.assertFalse((output / 'SHA256SUMS').exists())

    def test_existing_output_refused_before_network(self):
        with patch.object(socket, 'socket', side_effect=AssertionError('No socket')), self.assertRaises(ValueError):
            lab.run(self.root)


if __name__ == '__main__': unittest.main()
