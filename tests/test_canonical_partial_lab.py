"""Authored transport clients/trees; these tests are not actual browser observations."""
import copy
import hashlib
import http.client
import json
import os
from pathlib import Path
import shutil
import tempfile
import threading
import time
import unittest
from unittest.mock import patch
from urllib.parse import urlsplit

import tsep
from adapters import package
from examples import canonical_partial_lab as lab
from experiments import rendered_metadata as metadata
from test_rendered_metadata import scaffold, add


class FamilyCapture:
    def __init__(self, root):
        self.root=Path(root);self.source=self.root/'source'
        self.server,self.info=lab.start(self.source,'127.0.0.1')
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start();self.running=True

    def stop(self):
        if self.running:
            self.server.shutdown();self.server.server_close();self.thread.join();self.running=False
            lab.close_record(self.source)

    def request(self,url,body=None,agent='AuthoredTransport/1',headers=None):
        parsed=urlsplit(url);conn=http.client.HTTPConnection(parsed.hostname,parsed.port,timeout=5)
        sent={'User-Agent':agent};sent.update(headers or {})
        if body:sent['Content-Type']='application/json'
        conn.request('POST' if body else 'GET',parsed.path+('?'+parsed.query if parsed.query else ''),body=body,headers=sent)
        response=conn.getresponse();raw=response.read();status=response.status;conn.close()
        for _ in range(100):
            if len(lab.logs(self.source))>=self.server.sequence:break
            time.sleep(.005)
        return status,raw

    def exercise(self):
        assert self.request(self.info['base']+'/calibrate')[0]==200
        plan=lab.seal(self.source,'AUTHORED HTTP CLIENT, NOT A BROWSER','1');observations={};locations=lab.urls(self.info)
        for task in plan['tasks']:
            started=lab.now();auxiliary=None
            for spec in task['responses']:
                status,raw=self.request(spec['url'])
                assert status in (200,302)
                if spec['url']==locations['sitemap']:
                    auxiliary={'url':spec['url'],'status':status,'body_sha256':hashlib.sha256(raw).hexdigest()}
            tree=scaffold();tree['document_url']=tree['base_uri']=task['final_url']
            canonical=locations['variant'] if task['role']=='variant' and 'canonical' in task['faults'] else locations['preferred']
            add(tree,2,'link',[('rel','canonical'),('href',canonical)],resolved=canonical)
            body=add(tree,1,'body')
            witness=add(tree,body,'span',[('id','lab-navigation')])
            add(tree,witness,'#text',type_=3,data=task['navigation_id'])
            if task['role']=='catalog':
                href=locations['variant'] if 'links' in task['faults'] else locations['preferred'];add(tree,body,'a',[('href',href)],resolved=href)
            data={'kind':'canonical-family-page','version':lab.VERSION,'context':self.info['token'],
                'task_id':task['id'],'navigation_id':task['navigation_id'],'url':task['final_url'],
                'user_agent':plan['agent'],'script_sha256':metadata.script_digest(),'capture_started_at':lab.now(),
                'captured_at':lab.now(),'errors':[],'tree':tree,'auxiliary':auxiliary}
            payload=json.dumps(data);raw=json.dumps({'payload':payload,'sha256':hashlib.sha256(payload.encode()).hexdigest()}).encode()
            status,answer=self.request(self.info['base']+'/capture',raw);assert status==200,answer
            observations[task['id']]={'navigation_started_at':started,'observed_at':lab.now(),'receipt':json.loads(answer)['receipt']}
        return plan,observations


class CanonicalPartialLaboratory(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();cls.root=Path(cls.temp.name)
        (cls.root/'campaign').mkdir();c=FamilyCapture(cls.root/'campaign')
        try:cls.plan,cls.observations=c.exercise()
        finally:c.stop()
        cls.source=c.source

    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()

    def clone(self,name):
        path=self.root/name;shutil.copytree(self.source,path);return path

    def reseal_log(self,path,rows):
        (path/'requests.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
        closed=tsep.read_json(path/'closed.json');closed['log_sha256']=tsep.digest(path/'requests.jsonl')
        (path/'closed.json').write_bytes(package.json_bytes(closed))

    def test_fixed_family_matrix_and_actual_trace_binding(self):
        self.assertEqual(tsep.digest(lab.ROOT/lab.RECIPE),'974988f197290076fe199466a619da0b24fa81e4f1a01699cb0cb862a4b671b6')
        with patch('socket.socket',side_effect=AssertionError('offline')):rows=lab.analyze(self.source,self.observations)
        self.assertEqual(len(rows),12)
        intents=[r['input']['targets'][0]['intent'] for r in rows];self.assertTrue(all(i==intents[0] for i in intents))
        self.assertEqual(len({t['url'] for t in self.plan['tasks']}),3)
        self.assertEqual(len({t['navigation_id'] for t in self.plan['tasks']}),36)
        redirected=rows[2]['input']['targets'][0]['documents'][0]
        self.assertEqual(len(redirected['http']),2)
        self.assertEqual(redirected['render']['states'][0]['source_http_sha256'],lab.binding_digest(redirected['http']))
        self.assertNotIn('content_review',rows[-1]['input']['targets'][0])
        self.assertEqual(rows[-1]['expected'],['pass','inconclusive','pass','pass'])

    def test_mismatches_and_missing_runtime_remain_visible_in_delivery(self):
        path=self.root/'observations.json';lab.save(path,self.observations);output=self.root/'delivery'
        with patch.dict(os.environ,{'TSEP_SOURCE_NODE':'/missing/node24'}),patch('socket.socket',side_effect=AssertionError('offline')):
            result=lab.finish(self.source,path,output)
            self.assertFalse(result['all_expected_matched'])
            self.assertTrue(lab.replay_delivery(output)['same_results'])
        response=tsep.read_json(output/'blank-review/response-template.json')
        self.assertTrue(all(r['reviewer']=='' and all(c['outcome'] is None for c in r['comparisons']) for r in response['responses']))

    def test_swapped_receipts_and_reordered_phase_times_are_refused(self):
        wrong=copy.deepcopy(self.observations);ids=list(wrong)
        wrong[ids[0]]['receipt']=wrong[ids[1]]['receipt']
        with self.assertRaisesRegex(tsep.Invalid,'receipt'):lab.analyze(self.source,wrong)
        wrong=copy.deepcopy(self.observations);wrong[ids[3]]['navigation_started_at']=wrong[ids[0]]['navigation_started_at']
        with self.assertRaisesRegex(tsep.Invalid,'chronology'):lab.analyze(self.source,wrong)

    def test_rehashed_response_still_must_equal_prior_bytes(self):
        path=self.clone('changed-response');rows=lab.logs(path);row=next(r for r in rows if r.get('kind')=='navigation')
        raw=path/(row['id']+'-response.bin');raw.write_bytes(raw.read_bytes()+b'changed');row['response_sha256']=tsep.digest(raw);self.reseal_log(path,rows)
        with self.assertRaisesRegex(tsep.Invalid,'frozen plan'):lab.analyze(path,self.observations)

    def test_changed_expectations_or_preference_cannot_be_resealed(self):
        path=self.clone('changed-plan');plan=tsep.read_json(path/'plan.json');plan['recipe']['phases'][0]['expected'][1]='pass'
        (path/'plan.json').write_bytes(package.json_bytes(plan));closed=tsep.read_json(path/'closed.json');closed['plan_sha256']=tsep.digest(path/'plan.json');(path/'closed.json').write_bytes(package.json_bytes(closed))
        with self.assertRaisesRegex(tsep.Invalid,'registration'):lab.analyze(path,self.observations)

    def test_wrong_sitemap_digest_retained_even_with_rehashed_receipt(self):
        path=self.clone('wrong-sitemap');rows=lab.logs(path);row=next(r for r in rows if r.get('kind')=='capture' and r['task_id'].endswith('-catalog'))
        p=path/(row['id']+'-request.bin');raw=p.read_bytes();header,body=raw.split(b'\r\n\r\n',1);envelope=json.loads(body);data=json.loads(envelope['payload'])
        data['auxiliary']['body_sha256']='0'*64;envelope['payload']=json.dumps(data);envelope['sha256']=hashlib.sha256(envelope['payload'].encode()).hexdigest();body=json.dumps(envelope).encode()
        import re
        header=re.sub(rb'Content-Length: [0-9]+',b'Content-Length: '+str(len(body)).encode(),header,flags=re.I)
        p.write_bytes(header+b'\r\n\r\n'+body);row['request_sha256']=tsep.digest(p);row['receipt']=hashlib.sha256(body).hexdigest()
        observation=copy.deepcopy(self.observations);observation[row['task_id']]['receipt']=row['receipt'];self.reseal_log(path,rows)
        with self.assertRaisesRegex(tsep.Invalid,'Sitemap fetch'):lab.analyze(path,observation)

    def test_missing_duplicate_and_unlisted_evidence_are_refused(self):
        short=copy.deepcopy(self.observations);short.pop(next(iter(short)))
        with self.assertRaisesRegex(tsep.Invalid,'inventory'):lab.analyze(self.source,short)
        path=self.clone('unlisted');(path/'extra.bin').write_bytes(b'extra')
        with self.assertRaisesRegex(tsep.Invalid,'Unlisted'):lab.analyze(path,self.observations)
        path=self.clone('duplicate');rows=lab.logs(path);rows.append(copy.deepcopy(next(r for r in rows if r.get('kind')=='navigation')));self.reseal_log(path,rows)
        with self.assertRaisesRegex(tsep.Invalid,'duplicate'):lab.analyze(path,self.observations)

    def test_old_phase_tree_refused_even_with_new_envelope_and_receipt(self):
        path=self.clone('old-phase');rows=lab.logs(path)
        posts=[r for r in rows if r.get('kind')=='capture' and r['task_id'].endswith('-preferred')]
        first,current=posts[:2]
        first_body=(path/(first['id']+'-request.bin')).read_bytes().split(b'\r\n\r\n',1)[1]
        old_tree=json.loads(json.loads(first_body)['payload'])['tree']
        p=path/(current['id']+'-request.bin');header,body=p.read_bytes().split(b'\r\n\r\n',1)
        envelope=json.loads(body);data=json.loads(envelope['payload']);data['tree']=old_tree
        # Same URL, valid new envelope IDs/times and rehashed outer receipts still must not accept the old DOM.
        envelope['payload']=json.dumps(data);envelope['sha256']=hashlib.sha256(envelope['payload'].encode()).hexdigest();body=json.dumps(envelope).encode()
        import re
        header=re.sub(rb'Content-Length: [0-9]+',b'Content-Length: '+str(len(body)).encode(),header,flags=re.I)
        p.write_bytes(header+b'\r\n\r\n'+body);current['request_sha256']=tsep.digest(p);current['receipt']=hashlib.sha256(body).hexdigest()
        observation=copy.deepcopy(self.observations);observation[current['task_id']]['receipt']=current['receipt'];self.reseal_log(path,rows)
        with self.assertRaisesRegex(tsep.Invalid,'DOM navigation witness'):lab.analyze(path,observation)

    def test_duplicate_dom_witness_and_absent_witness_are_refused(self):
        tree=scaffold();body=add(tree,1,'body')
        with self.assertRaisesRegex(tsep.Invalid,'witness'):lab.navigation_witness(tree,'phase-A')
        for _ in range(2):
            witness=add(tree,body,'span',[('id','lab-navigation')]);add(tree,witness,'#text',type_=3,data='phase-A')
        with self.assertRaisesRegex(tsep.Invalid,'duplicate'):lab.navigation_witness(tree,'phase-A')

    def test_empty_connections_retained_but_partial_http_still_refused(self):
        import socket
        path=self.root/'empty-connections';path.mkdir();c=FamilyCapture(path)
        try:
            sock=socket.create_connection(c.server.server_address,timeout=5);sock.close()
            for _ in range(100):
                rows=lab.logs(c.source)
                if rows:break
                time.sleep(.01)
            self.assertEqual(len(rows),1)
            self.assertTrue(lab.empty_connection(rows[0],c.source))
            self.assertEqual((c.source/(rows[0]['id']+'-request.bin')).read_bytes(),b'')
            plan,observations=c.exercise()
            c.stop()
            self.assertEqual(len(lab.analyze(c.source,observations)),12)
            forged=copy.deepcopy(rows[0]);raw=c.source/(forged['id']+'-request.bin')
            raw.write_bytes(b'G');forged['request_sha256']=tsep.digest(raw)
            self.assertFalse(lab.empty_connection(forged,c.source))
        finally:c.stop()

    def test_partial_http_on_wire_is_not_an_empty_connection(self):
        import socket
        path=self.root/'partial-http';path.mkdir();c=FamilyCapture(path)
        try:
            sock=socket.create_connection(c.server.server_address,timeout=5);sock.sendall(b'G');sock.close()
            for _ in range(100):
                rows=lab.logs(c.source)
                if rows:break
                time.sleep(.01)
            self.assertEqual(len(rows),1)
            self.assertFalse(lab.empty_connection(rows[0],c.source))
            self.assertEqual(c.request(c.info['base']+'/calibrate')[0],200)
            with self.assertRaisesRegex(tsep.Invalid,'calibration'):
                lab.seal(c.source,'Authored client','1')
        finally:c.stop()

    def test_live_order_agent_and_session_refusals_are_retained(self):
        path=self.root/'refusals';path.mkdir();c=FamilyCapture(path)
        try:
            self.assertEqual(c.request(c.info['base']+'/calibrate')[0],200)
            plan=lab.seal(c.source,'Authored client','1')
            self.assertEqual(c.request(plan['tasks'][1]['url'])[0],400)
            self.assertEqual(c.server.cursor,0)
            self.assertEqual(c.request(plan['tasks'][0]['url'],agent='OtherClient')[0],400)
            self.assertEqual(c.request(plan['tasks'][0]['url'])[0],200)
            self.assertEqual(c.request(plan['tasks'][1]['url'])[0],400)
            self.assertTrue(any('error' in r for r in lab.logs(c.source)))
        finally:c.stop()


if __name__=='__main__':unittest.main()
