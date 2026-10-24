"""Intake v2 rejects contradictory bindings without rewriting native evidence."""
import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import socket
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import tsep
from adapters import captures, inspection_intake, replay

ROOT=Path(__file__).resolve().parents[1]

class FixedClock(datetime):
    @classmethod
    def now(cls,tz=None):return cls(2026,10,10,12,tzinfo=timezone.utc)

class InspectionIntakeIntegrity(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup);self.root=Path(tmp.name)
        fixture=ROOT/'tests/fixtures/inspection-evidence-v2.json'
        self.assertEqual(tsep.digest(fixture),fixture.with_suffix('.sha256').read_text().strip())
        self.cases=json.loads(fixture.read_bytes())['cases']
        for module in (inspection_intake,captures):
            patched=patch.object(module,'datetime',FixedClock);patched.start();self.addCleanup(patched.stop)
        for obj,key in ((socket,'socket'),(subprocess,'Popen')):
            patched=patch.object(obj,key,side_effect=AssertionError('Offline integrity tests'));patched.start();self.addCleanup(patched.stop)

    def write(self,path,value):
        path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')

    def prepare(self,case='qualified-positive'):
        target=copy.deepcopy(next(c['input']['targets'][0] for c in self.cases if c['id']=='inspection-v1-'+case))
        record=target.pop('inspection_records')[0];reviews=target.pop('inspection_reviews',[])
        self.write(self.root/'plan.json',target)
        native=self.root/'native';native.mkdir()
        for key in ('request','response'):(native/(key+'.json')).write_bytes(record[key]['raw_text'].encode('utf-8'))
        self.write(native/'manifest.json',{'kind':'tsep-url-inspection-observation','format_version':'1','provenance':'synthetic-exercise','description':'Authored native files for integrity tests','retrieved_at':record['retrieved_at'],'http_status':record['http_status'],'change':None,'request_sha256':tsep.digest(native/'request.json'),'response_sha256':tsep.digest(native/'response.json')})
        self.prepared=self.root/'prepared'
        inspection_intake.prepare(self.root/'plan.json',[native],self.prepared)
        self.meta=tsep.read_json(self.prepared/'intake.json')
        self.supplied=tsep.read_json(self.prepared/'review-request.json')
        if reviews:
            reviews[0]['binding_sha256']=self.supplied['reviews'][0]['binding_sha256'];self.supplied['reviews']=reviews
        self.originals={p.name:p.read_bytes() for p in native.iterdir()}

    def build(self):
        self.write(self.prepared/'intake.json',self.meta)
        self.write(self.root/'supplied.json',self.supplied)
        return inspection_intake.build(self.prepared,self.root/'supplied.json',self.root/'bundle','Fictional test author')

    def refused(self,pattern):
        with self.assertRaisesRegex((ValueError,OSError),pattern):self.build()
        self.assertFalse((self.root/'bundle').exists())
        self.assertEqual(self.originals,{p.name:p.read_bytes() for p in (self.root/'native').iterdir()})

    def test_coherent_positive_and_replay_preserve_raw_bytes(self):
        self.prepare();self.build()
        self.assertEqual(tsep.read_json(self.root/'bundle/report.json')['results'][0]['status'],'C')
        self.assertTrue(replay.replay(self.root/'bundle',self.root/'replay')['replayed'])
        data=tsep.read_json(self.root/'bundle/input.json')
        for key in ('request','response'):
            self.assertEqual(data['targets'][0]['inspection_records'][0][key]['raw_text'].encode(),self.originals[key+'.json'])

    def test_missing_input_inventory_entry(self):
        self.prepare();del self.meta['files']['input.json'];self.refused('inventory')

    def test_missing_input_hash_and_changed_context(self):
        self.prepare();del self.meta['files']['input.json']
        data=tsep.read_json(self.prepared/'input.json');data['targets'][0]['context']['tool']='changed';self.write(self.prepared/'input.json',data)
        self.refused('inventory')

    def test_false_global_pointer_even_when_review_matches(self):
        self.prepare();self.meta['input_sha256']='0'*64;self.supplied['input_sha256']='0'*64;self.refused('raw input bytes')

    def test_unlisted_file(self):
        self.prepare();(self.prepared/'extra.txt').write_text('extra');self.refused('Unlisted')

    def test_native_file_removed_from_both_disk_and_inventory(self):
        self.prepare();name='originals/1/response.json';del self.meta['files'][name];(self.prepared/name).unlink();self.refused('Missing original')

    def test_path_aliases_and_escapes(self):
        self.prepare()
        for name in ('./input.json','INPUT.json','../input.json','originals/01/response.json','originals/1/caf\u00e9.json','originals/1/cafe\u0301.json'):
            with self.subTest(name=name):
                self.meta['files'][name]='0'*64;self.refused('Unsafe');del self.meta['files'][name]

    def test_noncanonical_digest(self):
        self.prepare();original=self.meta['files']['input.json']
        for value in (original.upper(),'sha256:'+original,original[:-1]):
            with self.subTest(value=value):
                self.meta['files']['input.json']=value;self.refused('digest')

    def test_symbolic_link_file(self):
        self.prepare();path=self.prepared/'originals/1/response.json';path.unlink();path.symlink_to(self.root/'native/response.json');self.refused('outside|symlink|regular')

    def test_symbolic_link_parent(self):
        self.prepare();shutil.move(str(self.prepared/'originals/1'),str(self.root/'outside'));(self.prepared/'originals/1').symlink_to(self.root/'outside',target_is_directory=True);self.refused('outside|symlink')

    def test_review_from_other_input(self):
        self.prepare();self.supplied['input_sha256']='0'*64;self.refused('Reviews do not bind')

    def test_v1_requires_explicit_new_preparation(self):
        self.prepare();self.meta['version']='1';self.refused('new v2')

    def test_rehashed_input_cannot_contradict_original_plan(self):
        self.prepare();data=tsep.read_json(self.prepared/'input.json');data['targets'][0]['context']['tool']='changed'
        self.write(self.prepared/'input.json',data);digest=tsep.digest(self.prepared/'input.json')
        self.meta['files']['input.json']=digest;self.meta['input_sha256']=digest;self.supplied['input_sha256']=digest
        self.refused('original plan')

    def test_rehashed_native_file_cannot_contradict_prepared_record(self):
        self.prepare();name='originals/1/response.json';(self.prepared/name).write_bytes(b'{}\n');self.meta['files'][name]=tsep.digest(self.prepared/name);self.refused('original response bytes')

    def test_input_read_once_hash_and_parse_use_same_buffer(self):
        self.prepare();original=inspection_intake.regular;reads=[]
        def once(path,*args):
            if Path(path).name=='input.json':
                reads.append(path)
                if len(reads)>1:raise AssertionError('Input reread after hashing')
            return original(path,*args)
        with patch.object(inspection_intake,'regular',side_effect=once):self.build()
        self.assertEqual(len(reads),1)

if __name__=='__main__':unittest.main()
