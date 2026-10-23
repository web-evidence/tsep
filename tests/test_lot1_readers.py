"""Lot 1: actual parser regressions and contradictory HTTP prefixes."""
import copy
import os
import unittest
from pathlib import Path
from experiments import source_markers as reader
from conformance import redirects,http
from conformance.evaluate import exchange
from tests.test_redirects import CASES


class StructuralWhitespace(unittest.TestCase):
    def parse(self,html):
        return reader.observe(html.encode(),content_types=['text/html; charset=utf-8'],
            objective={'required_markers':['Expected'],'forbidden_markers':['Forbidden']},
            node=os.environ.get('TSEP_SOURCE_NODE'))

    def test_real_parser_whitespace_preserves_bytes_and_nonblank_markers(self):
        for sep in ('','\n','\r\n','\t \n\f'):
            for bom in ('','\ufeff'):
                raw=bom+'<!doctype html><html><head><title>Example</title></head>'+sep+'<body><h1>Expected</h1>'+sep+'</body>'+sep+'</html>'+sep
                r=self.parse(raw)
                self.assertEqual(r['candidate_consensus'],'pass',(sep,r['readings']))
                for mode,row in r['readings'].items():
                    for s in row['segments']+row['excluded']:
                        a,b=s['body_span_bytes'];self.assertEqual(raw.encode()[a:b].decode(),s['raw_source'])
                self.assertEqual(self.parse(raw.replace('Expected','Expected Forbidden'))['candidate_consensus'],'fail')

    def test_nbsp_is_retained_and_noscript_modes_never_union(self):
        raw='<!doctype html><html><head></head>\u00a0<body><h1>Expected</h1><noscript><b>Forbidden</b></noscript></body></html>'
        r=self.parse(raw)
        self.assertTrue(all(any('\u00a0' in s['data'] for s in v['segments']) for v in r['readings'].values()))
        self.assertTrue(all(not any('\u00a0' in s['data'] for s in v['excluded']) for v in r['readings'].values()))
        self.assertEqual(r['candidate_consensus'],'fail')

    def test_significant_or_forged_structural_run_is_not_discarded(self):
        inv=self.parse('<!doctype html><html><head></head>\n<body>Expected</body></html>')['inventory']
        base=inv['readings']['enabled']
        for text in ('\u00a0','Forbidden'):
            r=copy.deepcopy(base);n=next(n for n in r['nodes'] if n['kind']=='text' and n['data']=='\n')
            n['data']=n['raw_source']=text
            with self.assertRaisesRegex(ValueError,'outside attributed'):reader.project(r,'enabled')

    def test_terminal_comments_and_bare_unicode_text_keep_exact_intervals(self):
        for tail in ('Expected</body>\n</html>\n<!-- cache Forbidden -->\n',
                     'Expected é😀</BODY>\r\n</HTML>\r\n',
                     'Expected Forbidden</body>\n</html>\n'):
            raw='<!doctype html><html><head></head><body><footer>Footer</footer>'+tail
            result=self.parse(raw)
            self.assertEqual(result['candidate_consensus'],'fail' if 'Expected Forbidden' in raw else 'pass')
            for row in result['readings'].values():
                for s in row['segments']+row['excluded']:
                    a,b=s['body_span_bytes'];self.assertEqual(raw.encode()[a:b].decode(),s['raw_source'])
                self.assertFalse(any('cache' in s['data'] for s in row['segments']))


class HeaderTrajectories(unittest.TestCase):
    def target(self,head=None,body=None):
        t=copy.deepcopy(CASES['redirect-direct']['input']['targets'][0])
        t['intent']['redirect_reader']=redirects.HEADER_READER
        t['context']['collection']={'version':'2','settings':{'max_bytes':65536}}
        head=head or b'HTTP/1.1 200 OK\r\nContent-Length: 100000\r\n\r\n'
        raw=head+(body if body is not None else b'x'*65536)
        raw=raw[:65536]
        t['http'][-1].update(complete=False,response=http.encoded(raw),bytes_received=len(raw),
            stop_reason='response-byte-limit',response_limit=65536,overflow_bytes=1)
        return t

    def result(self,t):return redirects.assess(t,'TS02-A02')[0]

    def test_64k_terminal_prefix_reads_headers_but_body_rules_stay_unknown(self):
        t=self.target();self.assertEqual(self.result(t),'pass')
        self.assertIn('corps',redirects.assess(t,'TS02-A02')[1])
        with self.assertRaisesRegex(ValueError,'Incomplete HTTP'):exchange(t['http'][-1],t['url'],t['intent']['crawler'])
        del t['intent']['redirect_reader'];self.assertEqual(self.result(t),'inconclusive')

    def test_timeout_eof_missing_proof_or_incomplete_headers_never_pass(self):
        for key,value in [('stop_reason','timeout'),('overflow_bytes',0),('bytes_received',65535),('complete',True),('response_limit',True)]:
            t=self.target();t['http'][-1][key]=value;self.assertEqual(self.result(t),'inconclusive',key)
        t=self.target();t['context']['collection']['version']='1';self.assertEqual(self.result(t),'inconclusive')
        t=self.target(head=b'HTTP/1.1 200 OK\r\nX: '+b'x'*65536);self.assertEqual(self.result(t),'inconclusive')

    def test_ambiguous_and_contradictory_framing_stays_unknown(self):
        for headers in (b'Content-Length: 1',b'Content-Length: 100000\r\nContent-Length: 100000',
                        b'Transfer-Encoding: chunked\r\nContent-Length: 100000',b'Transfer-Encoding: gzip',
                        b'Transfer-Encoding: chunked\r\nTransfer-Encoding: chunked'):
            self.assertEqual(self.result(self.target(head=b'HTTP/1.1 200 OK\r\n'+headers+b'\r\n\r\n')),'inconclusive')
        for body in (b'BAD!\r\n',b'0\r\n\r\n',b'1\r\nxXX'):
            self.assertEqual(self.result(self.target(head=b'HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n\r\n',body=body+b'x'*65536)),'inconclusive')

    def test_chunked_or_gzip_body_is_not_misrepresented_as_decoded_content(self):
        self.assertEqual(self.result(self.target(head=b'HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n\r\n',body=b'100000\r\n'+b'x'*65536)),'pass')
        self.assertEqual(self.result(self.target(head=b'HTTP/1.1 200 OK\r\nContent-Encoding: gzip\r\nContent-Length: 100000\r\n\r\n')),'pass')

    def test_wrong_terminal_status_still_fails_without_inventing_review(self):
        t=self.target(head=b'HTTP/1.1 500 Error\r\nContent-Length: 100000\r\n\r\n')
        self.assertEqual(self.result(t),'fail')
        self.assertEqual(redirects.assess(self.target(),'TS02-A01')[0],'inconclusive')

    def test_phase_limit_old_metadata_and_chunk_extensions_have_specific_reasons(self):
        t=self.target();t['context']['collection']['settings']['max_bytes']=100000
        self.assertIn('No attributable collector',redirects.assess(t,'TS02-A02')[1])
        t=self.target();t['http'][-1]['stop_reason']='phase-byte-limit'
        self.assertIn('No attributable collector',redirects.assess(t,'TS02-A02')[1])
        t=self.target();del t['http'][-1]['overflow_bytes']
        self.assertIn('No attributable collector',redirects.assess(t,'TS02-A02')[1])
        t=self.target(head=b'HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n\r\n',body=b'100000;extension\r\n'+b'x'*65536)
        self.assertIn('Unsupported chunk-size prefix',redirects.assess(t,'TS02-A02')[1])

    def test_native_aggregation_and_offline_replay_keep_missing_review_unknown(self):
        import json,tempfile
        from adapters import captures,replay
        from conformance.redirects import review_binding
        import tsep
        for supplied in (False,True):
            t=self.target()
            if supplied:t['intent']['redirect_review']['plan_sha256']=review_binding(t)
            else:t['intent'].pop('redirect_review',None)
            with tempfile.TemporaryDirectory() as temp:
                root=Path(temp);p=root/'input.json'
                p.write_text(json.dumps({'input_version':'2','rules':['TS02-A01','TS02-A02'],'targets':[t]}))
                captures.build(p,root/'bundle',assessor='Authored synthetic fixture',label='Bounded prefix fixture',
                               selection_method='Fixed synthetic case',access='synthetic',mode='semiAuto')
                self.assertEqual(tsep.read_json(root/'bundle/report.json')['results'][0]['status'],'C' if supplied else 'NT')
                self.assertTrue(replay.replay(root/'bundle',root/'replay')['replayed'])


if __name__=='__main__':unittest.main()
