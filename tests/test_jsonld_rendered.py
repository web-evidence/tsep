"""Supplied rendered JSON-LD evidence boundaries. No implicit Node or browser."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from experiments import jsonld_rendered as reader
from scripts.jsonld_rendered_check import surface_projection
from scripts.source_http_check import fixture


class RenderedJSONLD(unittest.TestCase):
    def surfaces(self): return fixture('jsonld-rendered-surfaces-v1.json')['cases']
    def surface_input(self): return copy.deepcopy(self.surfaces()[0]['input'])
    def request(self): return copy.deepcopy(fixture('jsonld-rendered-workflow-v1.json')['cases'][0]['request'])
    def bind(self, x):
        dom = x['state']['structured_dom']; dom['snapshot_sha256'] = reader.evaluate.binding_digest(dom['snapshot'])

    def test_all_frozen_surface_facts_and_refusals(self):
        for c in self.surfaces():
            with self.subTest(c['id']):
                if c['expected']['usable_surface']:
                    self.assertEqual(surface_projection(reader.surface(c['input'])), c['expected'])
                else:
                    with self.assertRaises(ValueError): reader.surface(c['input'])

    def test_refusal_reasons_are_specific(self):
        checks = {'wrong-http-binding':'Navigation/HTTP', 'wrong-agent':'Navigation agent',
            'wrong-snapshot-sha':'fingerprint', 'missing-support':'supporting',
            'null-text-data':'character data', 'state-before-http':'chronology',
            'state-after-window':'chronology', 'wrong-collector':'capture script'}
        for c in self.surfaces():
            if c['id'] in checks:
                with self.subTest(c['id']), self.assertRaisesRegex(ValueError, checks[c['id']]): reader.surface(c['input'])

    def test_source_and_rendered_inputs_are_not_mutated(self):
        for c in self.surfaces():
            before = copy.deepcopy(c['input'])
            try: reader.surface(c['input'])
            except ValueError: pass
            self.assertEqual(c['input'], before)

    def test_support_change_even_with_snapshot_rebound_is_refused(self):
        x = self.surface_input(); x['state']['structured_dom']['acquisition']['support'][0]['content'] += 'changed'
        self.bind(x)
        with self.assertRaisesRegex(ValueError, 'supporting'): reader.surface(x)

    def test_null_comment_is_not_invented_as_empty(self):
        x = copy.deepcopy(self.surfaces()[1]['input'])
        for n in x['state']['structured_dom']['snapshot']['tree']['nodes']:
            if n['type'] == 8: n['data'] = None
        self.bind(x)
        with self.assertRaisesRegex(ValueError, 'character data'): reader.surface(x)

    def test_snapshot_base_is_not_substituted_by_document_url(self):
        c = next(c for c in self.surfaces() if c['id'] == 'changed-supplied-base')
        self.assertNotEqual(reader.surface(c['input'])['base_uri'], c['input']['final_url'])

    def test_namespace_and_shadow_boundaries_remain_explicit(self):
        for id, choice in [('open-shadow-separated','excluded-open-shadow'), ('foreign-script','excluded-foreign-namespace')]:
            c = next(c for c in self.surfaces() if c['id'] == id)
            r = reader.combine(reader.surface(c['input']))
            self.assertEqual(r['status'], 'absent'); self.assertEqual(r['diagnostics'][0]['selection'], choice)

    def test_template_and_frame_boundaries_are_retained(self):
        for id, kind in [('template-boundary','template'), ('frame-boundary','iframe')]:
            c = next(c for c in self.surfaces() if c['id'] == id)
            self.assertIn(kind, [b['kind'] for b in reader.surface(c['input'])['boundaries']])

    def test_duplicate_html_ids_do_not_collapse_scripts(self):
        c = next(c for c in self.surfaces() if c['id'] == 'duplicate-html-id')
        r = reader.combine(reader.surface(c['input']))
        self.assertEqual(r['selected_count'], 2); self.assertEqual(r['root_items'], 2)

    def test_native_http_fingerprint_and_agent_not_just_declarations(self):
        x = self.surface_input(); x['http'][0]['request'] = x['http'][0]['request'].replace('Authored-TSEP-Client/1','Forged/1')
        x['state']['structured_dom']['acquisition']['http_sha256'] = reader.evaluate.binding_digest(x['http'])
        with self.assertRaisesRegex(ValueError, 'crawler'): reader.surface(x)

    def test_partial_native_body_is_refused(self):
        x = self.surface_input(); x['http'][0]['complete'] = False
        x['state']['structured_dom']['acquisition']['http_sha256'] = reader.evaluate.binding_digest(x['http'])
        with self.assertRaisesRegex(ValueError, 'Incomplete HTTP'): reader.surface(x)

    def test_complete_tree_missing_a_declared_child_is_refused(self):
        x = self.surface_input(); x['state']['structured_dom']['snapshot']['tree']['nodes'][3]['child_count'] = 2
        self.bind(x)
        with self.assertRaisesRegex(ValueError, 'Incomplete declared'): reader.surface(x)

    def test_tree_byte_bound_and_node_bound(self):
        x = self.surface_input(); x['state']['structured_dom']['snapshot']['tree']['nodes'][4]['data'] = 'x'*524289; self.bind(x)
        with self.assertRaisesRegex(ValueError, 'Tree byte'): reader.surface(x)
        x = self.surface_input(); tree=x['state']['structured_dom']['snapshot']['tree'];tree['nodes'] *= 200;tree['reported_node_count']=len(tree['nodes']);self.bind(x)
        with self.assertRaisesRegex(ValueError, 'Node bound'): reader.surface(x)

    def test_preflight_refuses_late_plan_and_duplicate_ids(self):
        x = self.request(); x['plan']['declared_at'] = '2026-10-11T11:00:00Z'
        with self.assertRaisesRegex(ValueError, 'chronology'): reader.validate_request(x)
        x = self.request(); x['plan']['states'] *= 2
        with self.assertRaisesRegex(ValueError, 'repeated'): reader.validate_request(x)

    def test_preflight_refuses_extra_and_excessive_states(self):
        x = self.request(); x['extra'] = True
        with self.assertRaisesRegex(ValueError, 'fields'): reader.validate_request(x)
        x = self.request(); x['states'] *= 17
        with self.assertRaisesRegex(ValueError, 'population'): reader.validate_request(x)

    def test_replay_refuses_changed_input_or_source_before_node(self):
        x = dict(source_sha256={}, input=self.request(), input_sha256='bad')
        with patch.object(reader, 'observe', side_effect=AssertionError('must not execute')):
            with self.assertRaisesRegex(ValueError, 'sources differ'): reader.replay(x, node='unused')
            x['source_sha256'] = reader.identity()
            with self.assertRaisesRegex(ValueError, 'input differs'): reader.replay(x, node='unused')

    def test_output_tampering_not_hidden_by_input_and_source_hashes(self):
        x = dict(source_sha256=reader.identity(), input=self.request())
        x['input_sha256'] = reader.sha(reader.serialized(x['input'])); x['forged_result'] = 'green'
        with patch.object(reader, 'observe', return_value=dict(x, forged_result='unknown')):
            with self.assertRaisesRegex(ValueError, 'replay differs'): reader.replay(x, node='unused')

    def test_loaded_module_origin_is_checked(self):
        with patch.object(reader.structured_dom, '__file__', '/foreign/structured_dom.py'):
            with self.assertRaisesRegex(ValueError, 'origin differs'): reader.identity()

    def test_cli_refuses_overwrite_before_node(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'keep.json';path.write_text('keep')
            r=subprocess.run([sys.executable,str(ROOT/'experiments/jsonld_rendered.py'),str(path),
                '--node','unused','--output',str(path)],capture_output=True,text=True)
            self.assertEqual(r.returncode,64);self.assertEqual(path.read_text(),'keep')
            self.assertIn('new output path',r.stderr)

    def test_unexamined_outer_state_fields_are_not_accepted(self):
        x = self.surface_input(); x['state']['url'] = 'https://wrong.test/'
        with self.assertRaisesRegex(ValueError, 'state fields'): reader.surface(x)

    def test_malformed_http_member_has_a_bounded_refusal(self):
        x = self.request(); x['http'] = [None]
        with self.assertRaisesRegex(ValueError, 'trace member'): reader.validate_request(x)


if __name__ == '__main__': unittest.main()
