"""Preview permissions, independent contradictions, prior intent and offline evidence."""
import copy
import hashlib
import json
from pathlib import Path
import socket
import tempfile
import unittest
from unittest.mock import patch
from conformance import preview_intent as preview
from conformance.evaluate import evaluate
from adapters import captures, replay
import tsep

ROOT = Path(__file__).resolve().parents[1]


def fixture():
    p = ROOT/'tests/fixtures/preview-intent-v2.json'
    raw = p.read_bytes()
    if hashlib.sha256(raw).hexdigest() != p.with_suffix('.sha256').read_text().strip():
        raise ValueError('Prefrozen preview fixture changed')
    return json.loads(raw)['cases']


class PreviewIntent(unittest.TestCase):
    def data(self, name):
        return copy.deepcopy(next(c['input'] for c in fixture() if c['id'] == 'preview-'+name))

    def test_original_freeze_and_metadata_only_correction(self):
        p=ROOT/'tests/fixtures/preview-intent-v1.json';raw=p.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),p.with_suffix('.sha256').read_text().strip())
        original=json.loads(raw)['cases'];corrected=fixture();changed=[]
        for old,new in zip(original,corrected):
            adjusted=copy.deepcopy(new)
            if old!=new:
                self.assertTrue(adjusted.pop('reference_limit'))
                changed.append(new['id'])
            self.assertEqual(old,adjusted)
        self.assertEqual(changed,['preview-source-tree-pass','preview-source-tree-fail'])

    def test_prefrozen_expectations_and_explicit_runtime_limits(self):
        rows = fixture(); self.assertEqual(len(rows), 74)
        corpus = json.loads((ROOT/'conformance/cases.json').read_text())['cases']
        for c in rows:
            with self.subTest(c['id']):
                self.assertIn(c, corpus)
                actual = evaluate(c['input'])
                for observed, expected in zip(actual, c['expected']):
                    if observed['outcome'] == 'inconclusive' and expected.get('reference_limit'):
                        self.assertIn('source reader', observed['reason'].lower())
                    else:
                        self.assertEqual(observed['outcome'], expected['outcome'])

    def test_raw_order_scopes_and_indices_retained(self):
        intent = self.data('header-order-1')['targets'][0]['intent']
        result = preview.assess({'x-robots-tag':['otherbot: nosnippet','googlebot: max-snippet:50']}, ['max-snippet:-1'], intent)
        self.assertEqual(result['outcome'], 'pass')
        self.assertEqual([(e['origin'],e['index']) for e in result['entries']], [('meta',0),('http',0),('http',1)])
        self.assertTrue(result['entries'][1]['excluded'])
        self.assertEqual(result['entries'][2]['raw'], 'googlebot: max-snippet:50')

    def test_unknown_dimension_does_not_erase_proven_conflict(self):
        intent = self.data('separate-dimension-conflict')['targets'][0]['intent']
        result = preview.assess({}, ['max-image-preview:none, max-snippet:abc'], intent)
        self.assertEqual(result['decisions']['max_image_preview']['outcome'], 'fail')
        self.assertEqual(result['decisions']['max_snippet']['outcome'], 'inconclusive')
        self.assertEqual(result['outcome'], 'fail')

    def test_nosnippet_and_zero_video_are_not_image_prohibitions(self):
        intent = self.data('image-large')['targets'][0]['intent']
        for token in ('nosnippet','max-video-preview:0','max-snippet:0'):
            self.assertEqual(preview.assess({}, [token+', max-image-preview:large'],intent)['outcome'], 'pass')

    def test_ambiguous_video_retains_range(self):
        intent = self.data('snippet-zero-video-five')['targets'][0]['intent']
        result = preview.assess({}, ['max-snippet:0, max-video-preview:5'],intent)
        self.assertEqual(result['decisions']['max_video_preview']['possible_cap'],[0,5])
        self.assertEqual(result['outcome'],'inconclusive')

    def test_bound_exhaustion_never_assesses_a_prefix(self):
        intent = self.data('nosnippet-protection')['targets'][0]['intent']
        for values in (['nosnippet']*(preview.MAX_VALUES+1), ['nosnippet,'*(preview.MAX_TOKENS+1)], ['x'*(preview.MAX_BYTES+1)]):
            with self.subTest(size=len(values[0])):
                with self.assertRaises(ValueError):preview.assess({},values,intent)

    def test_numbers_and_closed_intent_grammar(self):
        intent = self.data('nosnippet-protection')['targets'][0]['intent']
        for value in (True,False,None,1.0,2147483648,-2,'0'):
            with self.subTest(value=value):
                intent['presentation']['max_snippet']['maximum']=value
                with self.assertRaises(ValueError):preview.assess({},['nosnippet'],intent)

    def test_render_diagnostics_identify_state_and_trace(self):
        notes=[];data=self.data('rendered-compatible');actual=evaluate(data,source_observations=notes)
        self.assertEqual(actual[0]['outcome'],'pass')
        entries=notes[0]['observations']
        self.assertEqual(entries[0]['rendered_state_id'],'state-0')
        self.assertEqual(entries[0]['source_http_sha256'],data['targets'][0]['render']['states'][0]['source_http_sha256'])
        self.assertEqual(entries[-1]['surface'],'source')

    def test_profile_is_never_implicitly_selected(self):
        data=self.data('nosnippet-protection');del data['targets'][0]['intent']['presentation_reader']
        actual=evaluate(data)
        self.assertEqual(actual[0]['outcome'],'inconclusive')
        self.assertEqual(actual[0]['reason'],'Presentation restrictions require review')

    def test_bundle_replay_retains_observations_without_network(self):
        data=self.data('rendered-compatible')
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);p=root/'input.json';p.write_text(json.dumps(data))
            with patch.object(socket,'socket',side_effect=AssertionError('Network forbidden')):
                captures.build(p,root/'bundle',assessor='Synthetic test author',label='Synthetic preview',
                               selection_method='One authored scenario, no site assessment',access='synthetic')
                # Replay is exercised through its public API, preserving source observations.
                result=replay.replay(root/'bundle',root/'replayed')
            self.assertTrue(result['replayed'])
            self.assertTrue(result['same_source_observations'])
            report=tsep.read_json(root/'bundle/report.json')
            self.assertEqual(report['results'][0]['status'],'NT')
            self.assertIn('conformance/preview_intent.py',tsep.read_json(root/'bundle/import.json')['source_files'])


if __name__ == '__main__':unittest.main()
