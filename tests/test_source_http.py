"""Python-only decoding/attribution guards; actual Node qualification is separate."""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from experiments import source_http as reader
from scripts.source_http_check import fixture


class HTTPSourceProfile(unittest.TestCase):
    def test_prefrozen_decoding_and_rejection_frontiers(self):
        for case in fixture('source-http-decoding-v1.json')['cases']:
            with self.subTest(case=case['id']):
                raw = bytes.fromhex(case['body_hex']); expected = case['expected']
                if not expected['available']:
                    with self.assertRaises(reader.ProfileUnavailable) as ctx:reader.decode(raw, case['content_types'])
                    self.assertEqual(ctx.exception.code, expected['error'])
                else:
                    source, result = reader.decode(raw, case['content_types'])
                    self.assertEqual(source, expected['decoded'])
                    self.assertEqual(result['consumed_bom_bytes'], expected['bom_bytes'])
                    self.assertEqual(result['body_sha256'], reader.sha(raw))
                    self.assertEqual(result['parser_input_utf8_sha256'], reader.sha(source.encode()))
        for name in ('source-http-tree-v1.json', 'source-http-mode-v1.json'): fixture(name)

    def test_scalar_mapping_preserves_bom_non_bmp_and_crlf(self):
        self.assertEqual(reader.byte_positions('é😀\r\nx',3,{0,1,3,4,5,6}),{0:3,1:5,3:9,4:10,5:11,6:12})
        for invalid in ({2},{7},{-1},{True}):
            with self.assertRaises(ValueError):reader.byte_positions('é😀\r\nx',3,invalid)

    @staticmethod
    def authored_output(source):
        raw_tag = '<meta name="robots" content="noindex">'
        start = source.index(raw_tag)
        span = [len(source[:start].encode('utf-16-le'))//2,len(source[:start+len(raw_tag)].encode('utf-16-le'))//2]
        record = {'group':'robots','tag':'meta','namespace':'http://www.w3.org/1999/xhtml','context':'body',
                  'attributes':{'name':'robots','content':'noindex'},'ancestors':['#document','html','body'],
                  'template_indices':[],'source_span_utf16':span,'raw_tag':raw_tag}
        one = {'complete':True, 'document_mode':'no-quirks', 'inventory':{g:[] for g in reader.GROUPS},
               'template_signals':[], 'template_containers':[], 'encoding_declarations':[],
               'inventory_order':[{'group':'robots','index':0}], 'parse_errors':[], 'tree_nodes':5}
        one['inventory']['robots']=[record]
        return {'kind':'unapplied-http-source-tree','experiment_version':'1','normative_effect':'none',
                'readings':{m:copy.deepcopy(one) for m in ('enabled','disabled')},
                'comparisons':{g:'identical' for g in reader.GROUPS},
                'supplementary_comparisons':{g:'identical' for g in ('template_containers','template_signals','encoding_declarations')}}

    def test_attribution_rechecks_original_body_not_only_decoded_hash(self):
        raw = '\ufeffé😀\r\n<meta name="robots" content="noindex">'.encode()
        source, decoding = reader.decode(raw,['text/html; charset=utf-8'])
        result = self.authored_output(source);reader.validate_and_attribute(result,source,raw,decoding)
        self.assertEqual(result['readings']['enabled']['inventory']['robots'][0]['body_span_bytes'],[11,len(raw)])
        for field,value in [('raw_tag','<meta name="robots">'),('source_span_utf16',[2,12]),('template_indices',[0]),('context','template')]:
            changed=self.authored_output(source);changed['readings']['enabled']['inventory']['robots'][0][field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):reader.validate_and_attribute(changed,source,raw,decoding)

    def test_incomplete_inventory_and_unavailable_runtime_do_not_fallback(self):
        source='<meta name="robots" content="noindex">';raw=source.encode();_,decoded=reader.decode(raw,['text/html; charset=utf-8'])
        result=self.authored_output(source);result['readings']['enabled']['complete']=False
        with self.assertRaisesRegex(ValueError,'Partial'):reader.validate_and_attribute(result,source,raw,decoded)
        with self.assertRaisesRegex(ValueError,'unavailable'):reader.inventory(raw,content_types=['text/html; charset=utf-8'],node='/missing/runtime')
        with patch.object(reader,'MAX_BYTES',2),self.assertRaisesRegex(ValueError,'8 MiB'):reader.decode(raw,['text/html; charset=utf-8'])

    def test_deadline_and_no_ambient_node_preload(self):
        with patch.object(reader.shutil,'which',return_value='/synthetic/node'), \
             patch.object(reader.subprocess,'run',side_effect=subprocess.TimeoutExpired('node',30)) as run, \
             patch.dict(os.environ,{'NODE_OPTIONS':'--import malicious','NODE_PATH':'/not-allowed'}):
            with self.assertRaisesRegex(ValueError,'30-second'):reader.inventory(b'<p>test',content_types=['text/html; charset=utf-8'])
        self.assertEqual(run.call_args.kwargs['timeout'],30)
        self.assertFalse(any(k.startswith('NODE_') for k in run.call_args.kwargs['env']))
        self.assertIn('--permission',run.call_args.args[0])

    def test_cli_preserves_input_and_existing_output_on_refusal(self):
        with tempfile.TemporaryDirectory() as temp:
            source=Path(temp)/'source';source.write_bytes(b'\xff')
            out=Path(temp)/'result.json'
            command=[sys.executable,str(reader.ROOT/'experiments/source_http.py'),str(source),
                     '--content-type','text/html; charset=utf-8','--output',str(out)]
            result=subprocess.run(command,capture_output=True,text=True)
            self.assertEqual(result.returncode,64);self.assertEqual(json.loads(result.stderr)['error_code'],'invalid-utf8')
            self.assertFalse(out.exists());self.assertEqual(source.read_bytes(),b'\xff')
            out.write_text('keep');result=subprocess.run(command,capture_output=True,text=True)
            self.assertEqual(result.returncode,64);self.assertEqual(out.read_text(),'keep')


if __name__ == '__main__':unittest.main()
