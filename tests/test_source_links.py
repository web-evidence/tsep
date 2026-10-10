"""Refuse malformed, unbound or unavailable calculations without optional Node."""
import copy,json,os,subprocess,unittest
from unittest.mock import patch
from experiments import source_links,url_resolution as urls
from scripts.source_http_check import fixture

class SourceLinks(unittest.TestCase):
    def test_frozen_oracles_are_separate_from_normative_results(self):
        self.assertEqual(len(fixture('url-resolution-v1.json')['cases']),50)
        cases=fixture('source-links-v1.json')['cases']
        self.assertEqual(len(cases),22)
        self.assertNotEqual(next(c for c in cases if c['id']=='noscript-base')['expected']['enabled'],
                            next(c for c in cases if c['id']=='noscript-base')['expected']['disabled'])
        self.assertEqual(fixture('source-links-v1.json')['normative_effect'],'none')

    def test_untrusted_input_is_bounded_before_runtime(self):
        for data in ({},[{'url':'x'}],[{'url':None,'base':None}],
                     [{'url':'x','base':None,'extra':True}],
                     [{'url':'x'*65537,'base':None}], [{'url':'x','base':None}]*50001):
            with self.assertRaises(ValueError):urls.validate_requests(data)
        with patch.object(urls,'MAX_INPUT',1):
            with self.assertRaisesRegex(ValueError,'input byte'):urls.validate_requests([])

    def test_output_cannot_omit_requests_or_change_fragment_projection(self):
        raw=urls.validate_requests([{'url':'https://example.test/p#x','base':None}])
        good={'kind':'unapplied-url-resolution','version':'1','normative_effect':'none',
            'request_sha256':urls.sha(raw),'runtime':{'node':'v24.synthetic'},'results':[
            {'ok':True,'href':'https://example.test/p#x','without_fragment':'https://example.test/p',
             'protocol':'https:','origin':'https://example.test'}]}
        urls.validate_result(good,raw,1)
        for mutate in (lambda r:r.update(request_sha256='wrong'),lambda r:r.update(results=[]),
            lambda r:r['results'][0].update(without_fragment='https://other.test/p'),
            lambda r:r['runtime'].update(node='v22.0.0'),lambda r:r['results'][0].update(ok=1)):
            r=copy.deepcopy(good);mutate(r)
            with self.assertRaises(ValueError):urls.validate_result(r,raw,1)

    def test_missing_runtime_or_timeout_cannot_fall_back(self):
        with self.assertRaisesRegex(ValueError,'unavailable'):urls.resolve([],node='/missing/node')
        with patch.object(urls.shutil,'which',return_value='/synthetic/node'), \
             patch.object(urls.subprocess,'run',side_effect=subprocess.TimeoutExpired('node',10)) as run, \
             patch.dict(os.environ,{'NODE_OPTIONS':'--import unrelated','NODE_PATH':'/unexpected'}):
            with self.assertRaisesRegex(ValueError,'deadline'):urls.resolve([])
        self.assertFalse(any(k.startswith('NODE_') for k in run.call_args.kwargs['env']))
        self.assertIn('--permission',run.call_args.args[0])

    def test_incomplete_tree_never_produces_partial_link_absence(self):
        result={'readings':{'enabled':{'complete':False}}}
        initial={'results':[{'ok':True,'protocol':'https:','href':'https://example.test/'}]}
        with patch.object(source_links.source_head,'inventory',return_value=result), \
             patch.object(source_links.url_resolution,'resolve',return_value=initial):
            with self.assertRaisesRegex(ValueError,'Incomplete source'):
                source_links.inventory(b'x',content_types=['text/html; charset=utf-8'],document_url='https://example.test/')

    def test_csp_input_refused_before_worker(self):
        with patch.object(source_links.source_head,'inventory',side_effect=AssertionError('must not run')):
            with self.assertRaisesRegex(ValueError,'CSP'):
                source_links.inventory(b'x',content_types=[],document_url='https://example.test/',csp_headers='base-uri none')

if __name__=='__main__':unittest.main()
