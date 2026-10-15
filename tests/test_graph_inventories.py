"""Prefrozen native inventory cases with independent expected URL lists."""
import copy
import hashlib
import json
from pathlib import Path
import socket
import unittest
from unittest.mock import patch
from conformance.graph_inventories import read, IntegrityError
from conformance import sitemap_files

P=Path(__file__).resolve().parent/'fixtures'

class GraphInventories(unittest.TestCase):
    def test_35_prefrozen_native_and_transport_cases(self):
        raw=(P/'ts18-inventory-component-cases-r1.json').read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),'1d8db7ae16f025681c1168342d37147e764b9f8962777f8a22a55af65ab1c419')
        cases=json.loads(raw)['cases'];self.assertEqual(len(cases),35)
        for case in cases:
            with self.subTest(case=case['id']), patch.object(socket,'socket',side_effect=AssertionError('No acquisition')):
                before=copy.deepcopy(case)
                if case['expected']=='technical-refusal':
                    with self.assertRaises(IntegrityError):read(case['record'],case['format'],case['policy'])
                else:
                    value=read(case['record'],case['format'],case['policy'])
                    self.assertEqual(value['qualified'],case['expected']=='qualified',value)
                    self.assertEqual(value['urls'],case['urls'] if case['expected']=='qualified' else [])
                    self.assertFalse(value['authenticates_origin']);self.assertFalse(value['url_semantics_checked'])
                    if case['format']=='sitemap' and value['qualified']:
                        self.assertEqual(value['reader']['sha256'],hashlib.sha256(Path(sitemap_files.__file__).read_bytes()).hexdigest())
                self.assertEqual(case,before)

if __name__=='__main__':unittest.main()
