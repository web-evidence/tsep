"""Prefrozen sitemap cases, scope boundaries and reproducible evidence. Apache-2.0."""
import copy
import hashlib
import json
from pathlib import Path
import socket
import tempfile
import unittest
from unittest.mock import patch

import tsep
from adapters.captures import build, source_files
from adapters.replay import replay
from conformance import sitemap_locations as reader
from conformance.evaluate import evaluate, Unknown
from reports.html import render

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT/'tests/fixtures'
DIGESTS = {
    'sitemap-locations-body-v1-cases': 'be901fdafb75110c59da61219812df112df7dd7cb8cd546a0f61e9dd9642e83a',
    'sitemap-locations-control-v1-cases': 'ec24ede6848245594db911a8d619cb3e6df9ac2a0e43d1e601aa81cc7f398560',
}
BODY = tsep.read_json(FIX/'sitemap-locations-body-v1-cases.json')['cases']
CASES = tsep.read_json(FIX/'sitemap-locations-control-v1-cases.json')['cases']


class SitemapLocations(unittest.TestCase):
    def test_frozen_body_cases(self):
        for stem, digest in DIGESTS.items():
            self.assertEqual(tsep.digest(FIX/(stem+'.json')), digest)
            self.assertEqual((FIX/(stem+'.sha256')).read_text().split()[0], digest)
        self.assertEqual(len(BODY), 52)
        for case in BODY:
            with self.subTest(case=case['id']):
                if case['expected']['kind'] == 'inconclusive':
                    with self.assertRaises(Unknown): reader.read(case['body'])
                else:
                    value = reader.read(case['body'])
                    actual = {'kind':'supported','index':value['index'],
                              'locations':value['locations'],'annotations':len(value['annotations'])}
                    self.assertEqual(actual,case['expected'])

    def test_frozen_control_cases_and_input_preservation(self):
        corpus = {c['id']:c for c in tsep.read_json(ROOT/'conformance/cases.json')['cases']}
        self.assertEqual(len(CASES),24)
        for case in CASES:
            with self.subTest(case=case['id']):
                before = copy.deepcopy(case)
                actual = [{k:r[k] for k in ('rule_id','target','outcome')} for r in evaluate(case['input'])]
                self.assertEqual(actual,case['expected'])
                self.assertEqual(case,before)
                self.assertEqual(case,corpus[case['id']])

    def test_427_historical_inputs_and_full_results_unchanged(self):
        prior = [{'case':c,'rows':evaluate(c['input'])}
                 for c in tsep.read_json(ROOT/'conformance/cases.json')['cases']
                 if not c['id'].startswith(('sitemap-locations-', 'source-directives-', 'source-canonical-'))]
        self.assertEqual(len(prior),427)
        raw = json.dumps(prior,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),
                         '228691dd7b9e5f972fc57c80f3a7e67d2633373f618221d2deb98ddb9274e2db')

    def test_declared_bounds_are_enforced_before_return(self):
        plain = BODY[0]['body']
        self.assertEqual((reader.MAX_BYTES,reader.MAX_NODES,reader.MAX_DEPTH,
                          reader.MAX_ENTRIES,reader.MAX_IMAGES),(8388608,200000,8,50000,1000))
        # Small injected budgets exercise exact boundaries without enormous fixtures.
        for limit, low, valid in [('MAX_BYTES',len(plain.encode())-1,len(plain.encode())),
                                  ('MAX_NODES',2,3),('MAX_DEPTH',2,3),('MAX_ENTRIES',0,1)]:
            with self.subTest(limit=limit):
                with patch.object(reader,limit,low), self.assertRaisesRegex(Unknown,'limit'):
                    reader.read(plain)
                with patch.object(reader,limit,valid):
                    self.assertEqual(len(reader.read(plain)['locations']),1)
        image = next(c['body'] for c in BODY if c['id']=='image-is-not-page')
        with patch.object(reader,'MAX_IMAGES',0), self.assertRaisesRegex(Unknown,'limit'):
            reader.read(image)
        with patch.object(reader,'MAX_IMAGES',1):
            self.assertEqual(len(reader.read(image)['annotations']),1)

    def test_schema_location_never_fetches_and_values_are_retained(self):
        with patch.object(socket,'socket',side_effect=AssertionError('No network')):
            schema = reader.read(next(c['body'] for c in BODY if c['id']=='schema-location-no-fetch'))
            values = reader.read(next(c['body'] for c in BODY if c['id']=='annotation-values-not-assessed'))
        self.assertEqual(schema['annotations'][0]['value'],'https://no-fetch.example/schema.xsd')
        self.assertEqual(values['annotations'][0]['attributes']['hreflang'],'bad language')
        self.assertEqual(values['annotations'][1]['fields'][reader.IMAGE+'loc'],'relative')
        self.assertIn('not validated',values['scope'])

    def test_bounded_preview_keeps_raw_evidence_and_escapes_html(self):
        data=copy.deepcopy(CASES[0]['input'])
        hop=data['targets'][0]['sitemaps']['documents'][0]['http'][0]
        payload='&lt;script&gt;alert(1)&lt;/script&gt;'+'x'*300
        annotations=''.join('<x:link rel="alternate" hreflang="fr" href="'+payload+'"/>' for _ in range(18))
        xml='<urlset xmlns="'+reader.NS[1:-1]+'" xmlns:x="'+reader.XHTML[1:-1]+'"><url><loc>https://example.com/product</loc>'+annotations+'</url></urlset>'
        hop['response']=hop['response'].split('\r\n\r\n')[0]+'\r\n\r\n'+xml
        reading=reader.read(xml)
        self.assertEqual(len(reading['annotations']),18)
        self.assertEqual(reading['annotations'][-1]['attributes']['href'],'<script>alert(1)</script>'+'x'*300)
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);source=root/'input.json';source.write_text(json.dumps(data))
            build(source,root/'bundle',assessor='Synthetic author',label='Synthetic sitemap',
                  selection_method='Authored cases',access='synthetic')
            self.assertEqual(tsep.read_json(root/'bundle/input.json'),data)
            reason=tsep.read_json(root/'bundle/assessment.json')[0]['reason']
            self.assertIn('2 additional annotations',reason)
            self.assertIn('[truncated]',reason)
            html=render(root/'bundle/report.json',language='fr')
            self.assertNotIn('<script>alert(1)</script>',html)
            self.assertIn('&lt;script&gt;',html)

    def test_partial_control_and_contradiction_survive_offline_replay(self):
        for name,status in [('combined-preferred','NT'),('competitor-survives-missing-branch','NC')]:
            case=next(c for c in CASES if c['id']=='sitemap-locations-'+name)
            with self.subTest(case=name),tempfile.TemporaryDirectory() as folder:
                root=Path(folder);source=root/'input.json';source.write_text(json.dumps(case['input']))
                with patch.object(socket,'socket',side_effect=AssertionError('No network')):
                    result=build(source,root/'bundle',assessor='Synthetic author',label='Synthetic sitemap',
                        selection_method='Authored cases',access='synthetic')
                    self.assertEqual(result['counts'][status],1)
                    self.assertTrue(replay(root/'bundle',root/'replay')['replayed'])
                for language in ('fr','en'):
                    self.assertIn(reader.PROFILE,render(root/'bundle/report.json',language=language))

    def test_source_inventory_pins_reader(self):
        self.assertEqual(source_files()['conformance/sitemap_locations.py'],tsep.digest(ROOT/'conformance/sitemap_locations.py'))


if __name__=='__main__': unittest.main()
