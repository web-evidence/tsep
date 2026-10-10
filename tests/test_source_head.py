"""Reject missing/tampered source evidence without requiring optional Node."""
import copy
import json
import os
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

from experiments import source_head as reader
from scripts.source_http_check import fixture


class HeadObservation(unittest.TestCase):
    def example(self):
        oracle=fixture('source-head-v1.json')
        case=next(c for c in oracle['cases'] if c['id']=='bom-and-unicode')
        saved=fixture('source-head-observation-v1.json')
        raw=case['html'].encode('utf-8')
        source,decoding=reader.http.decode(raw,['text/html; charset=utf-8'])
        return saved,source,raw,decoding

    def test_retained_unicode_positions_and_adversarial_mutations(self):
        result,source,raw,decoding=self.example()
        reader.attribute_prefix(result,source,raw,decoding)
        canonical=result['readings']['enabled']['inventory']['canonical'][0]
        start,end=canonical['body_span_bytes']
        self.assertEqual(raw[start:end].decode(),canonical['raw_tag'])
        self.assertGreater(start,canonical['source_span_utf16'][0])
        for mutate in (
            lambda tokens: tokens[0].update(raw='forged'),
            lambda tokens: tokens.pop(2),
            lambda tokens: tokens[1].update(source_span_utf16=[True,3]),
            lambda tokens: tokens[0].update(constructs_document_body=True),
            lambda tokens: tokens[-1].update(constructs_document_body=False),
        ):
            changed=copy.deepcopy(result)
            mutate(changed['readings']['enabled']['head_prefix']['tokens'])
            with self.assertRaises(ValueError):reader.attribute_prefix(changed,source,raw,decoding)

    def test_incomplete_prefix_cannot_claim_full_observation(self):
        result,source,raw,decoding=self.example()
        result['readings']['enabled']['head_prefix']['complete']=False
        with self.assertRaisesRegex(ValueError,'Incomplete'):reader.attribute_prefix(result,source,raw,decoding)
        result['readings']['enabled']['complete']=False
        with self.assertRaisesRegex(ValueError,'Partial'):reader.attribute_prefix(result,source,raw,decoding)

    def test_optional_runtime_missing_or_timed_out_never_falls_back(self):
        with self.assertRaisesRegex(ValueError,'unavailable'):
            reader.inventory(b'<p>x',content_types=['text/html; charset=utf-8'],node='/missing/node24')
        with patch.object(reader.shutil,'which',return_value='/synthetic/node'), \
             patch.object(reader.subprocess,'run',side_effect=subprocess.TimeoutExpired('node',30)) as run, \
             patch.dict(os.environ,{'NODE_OPTIONS':'--import unexpected','NODE_PATH':'/unexpected'}):
            with self.assertRaisesRegex(ValueError,'deadline'):
                reader.inventory(b'<p>x',content_types=['text/html; charset=utf-8'])
        self.assertFalse(any(k.startswith('NODE_') for k in run.call_args.kwargs['env']))
        self.assertIn('--permission',run.call_args.args[0])


if __name__=='__main__':unittest.main()
