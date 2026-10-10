"""Element namespace, provenance and refusal guards without optional Node."""
import copy,os,subprocess,unittest
from unittest.mock import patch
from experiments import link_elements as reader
from scripts.source_http_check import fixture

class LinkElements(unittest.TestCase):
    def saved(self):
        c=next(c for c in fixture('link-elements-v1.json')['cases'] if c['id']=='unicode-entity')
        raw=b'\xef\xbb\xbf'+c['html'].encode('utf-8')
        source,decoding=reader.http.decode(raw,['text/html; charset=utf-8'])
        return fixture('link-elements-observation-v1.json'),source,raw,decoding

    def test_bom_unicode_original_bytes_and_tamper_refusal(self):
        r,source,raw,d=self.saved();reader.validate_and_attribute(r,source,raw,d)
        tag=r['readings']['enabled']['records'][0];a,b=tag['body_span_bytes']
        self.assertEqual(raw[a:b].decode(),tag['raw_tag']);self.assertGreater(a,tag['source_span_utf16'][0]+3)
        for mutate in (lambda x:x.update(raw_tag='forged'),lambda x:x.update(source_span_utf16=[True,2]),
            lambda x:x['attributes'].append(copy.deepcopy(x['attributes'][0])),
            lambda x:x.update(node_index=-1),lambda x:x.update(template_indices=[0]),
            lambda x:x.update(ancestor_namespaces=[]),lambda x:x.update(context='template'),
            lambda x:x.update(tag='button')):
            broken=copy.deepcopy(r);mutate(broken['readings']['enabled']['records'][0])
            with self.assertRaises(ValueError):reader.validate_and_attribute(broken,source,raw,d)

    def test_namespace_keeps_href_and_xlink_href_distinct(self):
        r,_,_,_=self.saved();record=r['readings']['enabled']['records'][0]
        record['attributes']+=[{'local_name':'href','prefix':'xlink','namespace':reader.XLINK,'value':'/other'}]
        self.assertNotEqual(reader.attribute(record,'href'),reader.attribute(record,'href',reader.XLINK))
        self.assertEqual(reader.classification(record)['xlink_href'],'/other')

    def test_partial_records_never_support_absence(self):
        r,source,raw,d=self.saved();r['readings']['enabled']['complete']=False
        with self.assertRaisesRegex(ValueError,'Partial'):reader.validate_and_attribute(r,source,raw,d)

    def test_missing_runtime_and_deadline_never_fall_back(self):
        with self.assertRaisesRegex(ValueError,'unavailable'):
            reader.inventory(b'x',content_types=['text/html; charset=utf-8'],node='/missing/node')
        with patch.object(reader.shutil,'which',return_value='/synthetic/node'), \
             patch.object(reader.subprocess,'run',side_effect=subprocess.TimeoutExpired('node',30)) as run, \
             patch.dict(os.environ,{'NODE_OPTIONS':'--import unrelated'}):
            with self.assertRaisesRegex(ValueError,'deadline'):reader.inventory(b'x',content_types=['text/html; charset=utf-8'])
        self.assertFalse(any(k.startswith('NODE_') for k in run.call_args.kwargs['env']))

    def test_frozen_oracle_is_not_a_runtime_golden_output(self):
        cases=fixture('link-elements-v1.json')['cases'];self.assertEqual(len(cases),31)
        self.assertFalse(any('source_sha256' in c for c in cases))
        nofollow=next(c for c in cases if c['id']=='rel-annotations')['expected']['enabled'][0]
        self.assertEqual(nofollow['rel_tokens'],['nofollow','sponsored','nofollow'])

if __name__=='__main__':unittest.main()
