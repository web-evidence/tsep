"""Prefrozen source/DOM transport cases, not whole-control results."""
import copy
import hashlib
import json
import os
from pathlib import Path
import socket
import unittest
from unittest.mock import patch
import tsep
from conformance.graph_documents import read
P=Path(__file__).resolve().parent/'fixtures'
class NativeGraph(unittest.TestCase):
    def test_39_native_cases(self):
        raw=(P/'ts18-native-graph-component-cases-r1.json').read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),'cd8415839bd992ad1365c53654b52bbbe1b4b2e81c513be6cec59b563d59db10')
        cases=json.loads(raw)['cases'];self.assertEqual(len(cases),39)
        for c in cases:
            with self.subTest(case=c['id']), patch.object(socket,'socket',side_effect=AssertionError('No actual crawl')):
                original=copy.deepcopy(c['input'])
                if c['expected']=='technical-refusal':
                    with self.assertRaises(tsep.Invalid):read(c['input'])
                else:
                    v=read(c['input']);self.assertEqual(v['qualified'],c['expected']=='qualified',v)
                    self.assertFalse(v['authenticates_acquisition'])
                    for a, row in c['pairs'].items():
                        for b,status in row.items():self.assertEqual(v['pairs'][a][b],status)
                    for n,depth in c['depths'].items():
                        row=next(row for row in v['graph']['nodes'] if row['node']==n);self.assertEqual([row['lower'],row['upper']],depth)
                self.assertEqual(original,c['input'])
    def test_missing_runtime_is_not_qualified(self):
        c=json.loads((P/'ts18-native-graph-component-cases-r1.json').read_text())['cases'][0]
        with patch.dict(os.environ,{},clear=True):self.assertFalse(read(c['input'])['qualified'])
if __name__=='__main__':unittest.main()
