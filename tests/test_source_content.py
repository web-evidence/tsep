"""Retained content-tree integrity and resource limits, no implicit Node dependency."""
import copy
import json
import os
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

from experiments import source_content as reader
from scripts.source_http_check import fixture


class ContentObservation(unittest.TestCase):
    def example(self):
        case=next(c for c in fixture('source-content-v1.json')['cases'] if c['id']=='unicode-bom-byte-spans')
        raw=case['html'].encode('utf-8');source,decoding=reader.http.decode(raw,['text/html; charset=utf-8'])
        return fixture('source-content-observation-v1.json'),source,raw,decoding,case['ids']

    def test_original_byte_positions_include_bom_entities_and_astral_text(self):
        result,source,raw,decoding,ids=self.example()
        reader.validate_and_attribute(result,source,raw,decoding,ids)
        for reading in result['readings'].values():
            self.assertEqual(reading['selections'],fixture('source-content-v1.json')['cases'][6]['expected']['disabled'])
            located=[n for n in reading['nodes'] if n['source_span_utf16'] is not None]
            self.assertTrue(any(n['body_span_bytes'][0]>n['source_span_utf16'][0]+3 for n in located))
            for n in located:
                a,b=n['body_span_bytes'];self.assertEqual(raw[a:b].decode('utf-8'),n['raw_source'])

    def test_tampered_topology_positions_and_derived_selection_rejected(self):
        original,source,raw,decoding,ids=self.example()
        mutations=[
            lambda r:r['nodes'][0].update(id=True),
            lambda r:r['nodes'][0].update(child_count=0),
            lambda r:r['nodes'][1].update(parent=1),
            lambda r:r['nodes'][1].update(index=True),
            lambda r:r['nodes'][1].update(edge='template-content'),
            lambda r:r['nodes'][-1].update(raw_source='forged'),
            lambda r:r['nodes'][-1].update(source_span_utf16=[True,2]),
            lambda r:r['nodes'][-1].update(source_span_utf16=[0,999999]),
            lambda r:r.update(selections={'critical':[]}),
            lambda r:r['nodes'][-1].update(child_count=1),
            lambda r:r['nodes'][2].update(template_content=True),
        ]
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                result=copy.deepcopy(original);mutate(result['readings']['disabled'])
                with self.assertRaises(ValueError):reader.validate_and_attribute(result,source,raw,decoding,ids)

    def test_partial_tree_cannot_supply_empty_or_positive_selection(self):
        result,source,raw,decoding,ids=self.example()
        reading=result['readings']['disabled'];reading.update(complete=False,reason='synthetic limit')
        with self.assertRaisesRegex(ValueError,'Partial tree'):reader.validate_and_attribute(result,source,raw,decoding,ids)
        reading['nodes']=[]
        with self.assertRaisesRegex(ValueError,'Stored selection'):reader.validate_and_attribute(result,source,raw,decoding,ids)
        del reading['selections'];reader.validate_and_attribute(result,source,raw,decoding,ids)
        self.assertIsNone(reading['selections'])

    def test_literal_selectors_reject_ambiguous_or_unbounded_requests(self):
        for ids in (None,[],[''],['a','a'],['a b'],['a\n'],['x'*129],list(map(str,range(65)))):
            with self.subTest(ids=ids),self.assertRaises(ValueError):reader.selectors(ids)
        reader.selectors(['a:b','é😀'])

    def test_projection_bounds_duplicate_ids_and_repeated_text(self):
        original,*_=self.example()
        reading=original['readings']['disabled'];article=next(n for n in reading['nodes'] if n['name']=='article')
        # These constructed projection-only inputs are explicitly not complete
        # parser observations. Full validation is independently tested above.
        base=copy.deepcopy(reading['nodes'][:article['id']])
        copies=[]
        for i in range(513):
            n=copy.deepcopy(article);n.update(id=len(base)+i,child_count=0);copies.append(n)
        with self.assertRaisesRegex(ValueError,'match bound'):
            reader.projection(dict(complete=True,nodes=base+copies),['critical'])
        changed=copy.deepcopy(reading)
        next(n for n in changed['nodes'] if n['kind']=='text')['data']='x'*(2*1024*1024+1)
        with self.assertRaisesRegex(ValueError,'text bound'):reader.projection(changed,['critical'])

    def test_projection_record_limit_counts_empty_runs(self):
        original,*_=self.example();reading=original['readings']['disabled']
        article=next(n for n in reading['nodes'] if n['name']=='article')
        nodes=copy.deepcopy(reading['nodes'][:article['id']])
        parent=article['parent']
        for _ in range(128):
            node=copy.deepcopy(article);node.update(id=len(nodes),parent=parent)
            parent=node['id'];nodes.append(node)
        text=next(n for n in reading['nodes'] if n['kind']=='text')
        for _ in range(400):
            node=copy.deepcopy(text);node.update(id=len(nodes),parent=parent,data='')
            nodes.append(node)
        with self.assertRaisesRegex(ValueError,'record bound'):
            reader.projection(dict(complete=True,nodes=nodes),['critical'])

    def test_missing_runtime_and_timeout_have_no_fallback(self):
        args=dict(content_types=['text/html; charset=utf-8'],ids=['critical'])
        with self.assertRaisesRegex(ValueError,'unavailable'):reader.inventory(b'<p>x',node='/missing/node24',**args)
        with patch.object(reader.shutil,'which',return_value='/synthetic/node'), \
             patch.object(reader.subprocess,'run',side_effect=subprocess.TimeoutExpired('node',30)) as run, \
             patch.dict(os.environ,{'NODE_OPTIONS':'--import unexpected','NODE_PATH':'/unexpected'}):
            with self.assertRaisesRegex(ValueError,'deadline'):reader.inventory(b'<p>x',**args)
        self.assertFalse(any(k.startswith('NODE_') for k in run.call_args.kwargs['env']))
        self.assertIn('--permission',run.call_args.args[0])
        self.assertIn('--disallow-code-generation-from-strings',run.call_args.args[0])

    def test_declared_encoding_is_not_sniffed_or_repaired(self):
        for raw,ct in [(b'\xff',['text/html; charset=utf-8']),(b'<p>x',['text/html']),
                       (b'<p>x',['text/html; charset=iso-8859-1'])]:
            with self.assertRaises(reader.http.ProfileUnavailable):reader.inventory(raw,content_types=ct,ids=['critical'])


if __name__=='__main__':unittest.main()
