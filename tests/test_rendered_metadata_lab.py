"""Loopback transport tests with AUTHORED snapshots; no browser execution."""
import copy
import json
from pathlib import Path
import shutil
import socket
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from urllib.request import Request, urlopen

import tsep
from collectors import ts01
from examples import rendered_metadata_lab as lab
from experiments import rendered_metadata as metadata
from test_rendered_metadata import tree


class MetadataLaboratory(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();cls.root=Path(cls.temp.name)
        cls.source=cls.root/'source'
        servers,threads,reg=lab.start(cls.source)
        cls.records={}
        try:
            for env in reg['environments']:
                records={};agent='Authored-unit-client/'+env
                for task in reg['tasks']:
                    started=ts01.now()
                    with urlopen(Request(task['url'],headers={'User-Agent':agent}),timeout=3) as response:response.read()
                    if task['id'] in ('frame-same-origin','frame-cross-origin'):
                        url=reg['frames'][0 if task['id']=='frame-same-origin' else 1]
                        with urlopen(Request(url,headers={'User-Agent':agent}),timeout=3) as response:response.read()
                    t=tree();t.update(document_url=task['url'],base_uri=None,serialization=None,
                                     traversal_complete=False,stop_reason='api-error',api_errors=['AUTHORED missing API'])
                    records[task['id']]={'script_sha256':metadata.script_digest(),'navigation_started_at':started,
                        'observed_at':ts01.now(),'url':task['url'],'context':reg['token'],'state':'loaded',
                        'errors':[],'devLogs':[],'tree':t,
                        'browser':{'name':'AUTHORED TEST CLIENT, NOT BROWSER','version':'unit fixture','user_agent':agent}}
                cls.records[env]=records
        finally:lab.stop(servers,threads)
        cls.observations=cls.root/'observations.json';ts01.save(cls.observations,cls.records)

    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()

    def test_partial_observations_stay_unmatched_and_replay_without_network(self):
        output=self.root/'delivery'
        result=lab.finish(self.source,self.observations,output)
        self.assertEqual(result['observations'],48);self.assertEqual(result['server_requests'],78)
        self.assertFalse(result['all_recipe_checks_matched'])
        with patch.object(socket,'socket',side_effect=AssertionError('network forbidden')), \
             patch.object(socket,'getaddrinfo',side_effect=AssertionError('DNS forbidden')), \
             patch.object(subprocess,'run',side_effect=AssertionError('subprocess forbidden')):
            self.assertTrue(lab.replay(output)['same_inventory'])
        with self.assertRaisesRegex(ValueError,'NEW output'):lab.finish(self.source,self.observations,output)
        (output/'unexpected.txt').write_text('not declared')
        with self.assertRaisesRegex(ValueError,'Unexpected file'):lab.replay(output)

    def test_missing_environment_or_task_rejected(self):
        for records in ({'integrated':self.records['integrated']},copy.deepcopy(self.records)):
            if 'chrome' in records:del records['chrome']['corrected']
            with self.assertRaisesRegex(ValueError,'Missing'):lab.analyze(self.source,records)

    def test_changed_script_or_chronology_rejected(self):
        for field,value in [('script_sha256','0'*64),('navigation_started_at','2000-01-01T00:00:00Z')]:
            records=copy.deepcopy(self.records);records['integrated']['corrected'][field]=value
            with self.assertRaises(ValueError):lab.analyze(self.source,records)

    def test_rehashed_raw_sidecar_disagreement_rejected(self):
        source=self.root/'tampered-sidecar';shutil.copytree(self.source,source)
        phase=source/'source-1';entries=ts01.verify(phase)
        p=phase/'target-1-hop-1-response.bin';p.write_bytes(p.read_bytes()+b'changed')
        (phase/'SHA256SUMS').unlink();ts01.manifest(phase,list(entries))
        receipt=tsep.read_json(source/'receipt.json');receipt['phases']['source-1']=tsep.digest(phase/'SHA256SUMS')
        (source/'receipt.json').write_text(json.dumps(receipt))
        with self.assertRaisesRegex(ValueError,'sidecar'):lab.analyze(source,self.records)

    def test_rehashed_recipe_edit_rejected(self):
        source=self.root/'tampered-recipe';shutil.copytree(self.source,source)
        reg=tsep.read_json(source/'registration.json');reg['cases'][0]['expected']={}
        (source/'registration.json').write_text(json.dumps(reg))
        receipt=tsep.read_json(source/'receipt.json');receipt['registration_sha256']=tsep.digest(source/'registration.json')
        (source/'receipt.json').write_text(json.dumps(receipt))
        with self.assertRaisesRegex(ValueError,'scope'):lab.analyze(source,self.records)

    def test_frame_identity_mismatch_rejected(self):
        source=self.root/'tampered-frame';shutil.copytree(self.source,source)
        rows=[json.loads(x) for x in (source/'requests.jsonl').read_text().splitlines()]
        row=next(r for r in rows if r['url'].endswith('/frame.html') and r['agent']!=lab.AGENT)
        row['agent']='different-client'
        (source/'requests.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
        with self.assertRaisesRegex(ValueError,'frame request'):lab.analyze(source,self.records)
