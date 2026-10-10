"""Non-normative diagnostic boundaries and reference preflight counterexamples."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from collectors.preflight import reference_check, media_comparison
from diagnostics.coverage import diagnose, inspect_source, render
from tests.test_binary_http import response
from tests.test_html_report import Document

ROOT = Path(__file__).resolve().parents[1]
HEADERS = {'content-type': ['text/html; charset=utf-8']}


class ReferenceDiagnostics(unittest.TestCase):
    def codes(self, html):
        return {r['code'] for r in inspect_source(html)['candidate_limits']}

    def test_inventory_continues_after_first_candidate_and_never_emits_verdict(self):
        source = '<html><body><select><option>X</option></select><table><tr><td>X</td></tr></table><noscript><img></noscript></body></html>'
        result = inspect_source(source)
        self.assertTrue(result['scan_completed'])
        self.assertEqual(self.codes(source), {'context:select','context:option','context:table','context:tr','context:td','nonempty:noscript'})
        self.assertTrue({'outcome','decision','status','C','NC','NT'}.isdisjoint(result))

    def test_inventory_excludes_fake_tags_in_attributes_comments_and_inert_code(self):
        source = '<html><body><p title="<table>">X</p><!-- <select> --><script>"<table>"</script><style>/* <select> */</style><title><select></title></body></html>'
        result = inspect_source(source)
        self.assertNotIn('select', result['tag_counts'])
        self.assertNotIn('table', result['tag_counts'])

    def test_empty_inventory_is_not_a_guarantee_and_broken_markup_is_tentative(self):
        self.assertIn('structural-recovery', self.codes('<html><body><b>X</i></body></html>'))
        self.assertIn('nonvoid-self-closing:script', self.codes('<html><body><script/></body></html>'))
        self.assertIn('duplicate-attribute', self.codes('<html><body><p a="1" a="2">X</p></body></html>'))
        self.assertIn('incomplete-or-ambiguous-structure', self.codes('<html><body><p title="x'))
        with patch('diagnostics.coverage.MAX_EVENTS', 2):
            self.assertFalse(inspect_source('<html><body><p>X</p></body></html>')['scan_completed'])

    def test_svg_and_nonempty_raw_contexts_are_inventory_candidates(self):
        source='<html><body><svg><style>.x{}</style><text>X</text></svg><textarea>x</textarea><template><b>x</b></template><script><!--x--></script></body></html>'
        self.assertTrue({'svg-context:style','svg-context:text','svg-text','nonempty:textarea','nonempty:template','escaped-script'} <= self.codes(source))

    def input(self, content=b'<html><body><select></select></body></html>'):
        hop={'complete':True,'response':response(content, 'gzip', True)}
        return json.dumps({'input_version':'2','targets':[{'url':'https://example.com/','reference':{'http':[hop]},'http':[hop]}]}).encode()

    def test_supplied_bytes_are_not_changed_and_diagnostic_does_not_run_assessment(self):
        raw=self.input(); before=bytes(raw)
        with patch('conformance.evaluate.evaluate', side_effect=AssertionError('No rule execution')), \
                patch('socket.socket', side_effect=AssertionError('No network')):
            result=diagnose(raw)
        self.assertEqual(raw,before)
        self.assertEqual(result['kind'],'diagnostic-only')
        self.assertEqual(result['construction_matrix'][0]['evaluation_pages'],1)
        self.assertFalse(result['pages'][0]['content_type_headers_differ'])
        page=Document(render(result))
        self.assertFalse(any(tag in ('script','img','iframe','object') for tag,_ in page.tags))
        self.assertIn('aucun verdict TSEP',render(result))

    def test_unavailable_surface_retains_reason_without_inventing_evaluability(self):
        data=json.loads(self.input(b'\xff')); result=diagnose(json.dumps(data).encode())
        self.assertFalse(result['pages'][0]['evaluation']['available'])
        self.assertIn('UTF-8',result['pages'][0]['evaluation']['unavailable_reason'])
        data['targets'][0]['http'][0]['response']['sha256']='0'*64
        result=diagnose(json.dumps(data).encode())
        self.assertIn('fingerprint',result['pages'][0]['evaluation']['unavailable_reason'])

    def test_cli_has_no_decision_module_dependency_and_refuses_existing_output(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); source=root/'input.json';source.write_bytes(self.input())
            command=[sys.executable,'-I',str(ROOT/'diagnostics/coverage.py'),str(source),'--output-dir',str(root/'result')]
            result=subprocess.run(command,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            original=(root/'result/diagnostic.json').read_bytes()
            self.assertEqual(subprocess.run(command,capture_output=True).returncode,64)
            self.assertEqual((root/'result/diagnostic.json').read_bytes(),original)
            code='import sys;sys.path.insert(0,'+repr(str(ROOT))+');from diagnostics.coverage import diagnose;diagnose(open('+repr(str(source))+',"rb").read());assert "conformance.evaluate" not in sys.modules'
            self.assertEqual(subprocess.run([sys.executable,'-I','-c',code],capture_output=True).returncode,0)

    def test_preflight_checks_reference_despite_any_future_equal_digest(self):
        source='<html><body><p>Maintenance</p></body></html>'
        result=reference_check(HEADERS,source,'markers',['Expected'],['Maintenance'])
        self.assertEqual(result['state'],'contradiction')
        self.assertEqual(result['missing_required'],['Expected'])
        self.assertEqual(result['present_forbidden'],['Maintenance'])
        self.assertEqual(reference_check(HEADERS,source,'digest')['state'],'not-requested')

    def test_preflight_excludes_attributes_and_inert_text_and_never_uses_partial_prefix(self):
        source='<html><body><p title="Expected">Other</p><script>Expected</script></body></html>'
        self.assertEqual(reference_check(HEADERS,source,'markers',['Expected'],[])['state'],'contradiction')
        source='<html><body>Forbidden<select></select></body></html>'
        self.assertEqual(reference_check(HEADERS,source,'markers',['Expected'],['Forbidden'])['state'],'unavailable')
        with self.assertRaises(ValueError):reference_check(HEADERS,source,'markers',[],[])

    def test_media_comparison_is_observation_only(self):
        result=media_comparison(HEADERS,{'content-type':['text/plain; charset=utf-8']})
        self.assertTrue(result['raw_headers_differ'])
        self.assertNotIn('outcome',result)
        self.assertTrue(media_comparison({},HEADERS)['raw_headers_differ'])
        self.assertTrue(media_comparison(HEADERS,{})['raw_headers_differ'])
        self.assertFalse(media_comparison({},{})['raw_headers_differ'])


if __name__=='__main__':
    unittest.main()
