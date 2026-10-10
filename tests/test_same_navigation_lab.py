"""Transport clients below are authored tests, NOT actual browsers or human review."""
import copy
import hashlib
import http.client
import json
from pathlib import Path
import tempfile
import threading
import time
import unittest
from unittest.mock import patch
from urllib.parse import urlsplit

import tsep
from examples import same_navigation_lab as lab
from adapters import package
from experiments import rendered_metadata as metadata
from test_rendered_metadata import scaffold, add

class SameNavigation(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);self.source=self.root/'source'
  self.server,self.info=lab.start(self.source);self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start();self.running=True
 def stop(self):
  if self.running:
   self.server.shutdown();self.server.server_close();self.thread.join();self.running=False
   lab.save(self.source/'closed.json',{'closed_at':lab.now(),'source_files':lab.sources(),'plan_sha256':tsep.digest(self.source/'plan.json'),'log_sha256':tsep.digest(self.source/'requests.jsonl')})
 def tearDown(self):
  if self.running:self.server.shutdown();self.server.server_close();self.thread.join()
  self.temp.cleanup()
 def request(self,url,body=None,agent='SyntheticTransportClient/1',extra_headers=None):
  p=urlsplit(url);conn=http.client.HTTPConnection(p.hostname,p.port,timeout=5)
  headers={'User-Agent':agent,'Content-Type':'application/json'} if body else {'User-Agent':agent}
  headers.update(extra_headers or {})
  conn.request('POST' if body else 'GET',p.path,body=body,headers=headers)
  response=conn.getresponse();data=response.read();status=response.status;conn.close()
  # Wait only for this known running handler's retained response record.
  for _ in range(100):
   rows=lab.logs(self.source)
   if len(rows)>=self.server.sequence:break
   time.sleep(.005)
  return status,data
 def calibrate(self):
  self.assertEqual(self.request(self.info['base']+'/calibrate')[0],200)
  return lab.seal(self.source,'SYNTHETIC transport client; not browser','1')
 def exercise(self):
  plan=self.calibrate();observations={}
  for task in plan['tasks']:
   started=lab.now();self.assertEqual(self.request(task['url'])[0],200)
   t=scaffold();t['document_url']=t['base_uri']=task['url'];t['serialization']['html']='AUTHORED TEST TREE, NOT BROWSER OUTPUT'
   href=task['url']+('/other' if task['mutation']=='canonical' else '')
   add(t,2,'link',[('rel','canonical'),('href',href)],resolved=href)
   if task['mutation']=='noindex':add(t,2,'meta',[('name','robots'),('content','noindex')])
   b=add(t,1,'body');add(t,b,'a',[('href',task['url']+('?variant=1' if task['mutation']=='links' else ''))])
   if task['mutation']=='node-limit':t.update(traversal_complete=False,stop_reason='node-limit')
   payload={'kind':'same-navigation-page','version':lab.VERSION,'context':self.info['token'],'task_id':task['id'],'navigation_id':task['navigation_id'],'url':task['url'],
    'user_agent':plan['agent'],'script_sha256':metadata.script_digest(),'capture_started_at':lab.now(),'captured_at':lab.now(),'errors':[],'tree':t}
   text=json.dumps(payload);raw=json.dumps({'payload':text,'sha256':hashlib.sha256(text.encode()).hexdigest()}).encode()
   status,answer=self.request(self.info['base']+'/capture',raw);self.assertEqual(status,200)
   observations[task['id']]={'navigation_started_at':started,'observed_at':lab.now(),'receipt':json.loads(answer)['receipt']}
  return plan,observations
 def test_exact_wire_and_offline_native_replay(self):
  plan,observations=self.exercise();self.stop();path=self.root/'observations.json';lab.save(path,observations)
  with patch('socket.socket',side_effect=AssertionError('offline')):
   result=lab.finish(self.source,path,self.root/'delivery');self.assertTrue(result['all_expected_matched'])
   self.assertTrue(lab.replay_delivery(self.root/'delivery')['same_results'])
  rows=lab.logs(self.source);self.assertEqual(len(rows),13)
  get=next(r for r in rows if r.get('kind')=='navigation');raw=(self.source/(get['id']+'-request.bin')).read_bytes()
  self.assertIn(b'User-Agent: SyntheticTransportClient/1\r\n',raw)
  self.assertEqual(hashlib.sha256(raw).hexdigest(),get['request_sha256'])
 def test_duplicate_navigation_is_retained_and_refused(self):
  plan,observations=self.exercise();self.request(plan['tasks'][0]['url']);self.stop()
  with self.assertRaisesRegex(tsep.Invalid,'duplicate'):lab.analyze(self.source,observations)
 def test_stale_or_other_navigation_receipt_is_refused(self):
  plan,observations=self.exercise();self.stop();observations[plan['tasks'][0]['id']]['receipt']='0'*64
  with self.assertRaisesRegex(tsep.Invalid,'receipt'):lab.analyze(self.source,observations)
 def test_changed_observed_wire_cannot_be_hidden_by_rehashing_log(self):
  plan,observations=self.exercise();self.stop();rows=lab.logs(self.source);row=next(r for r in rows if r.get('kind')=='navigation')
  path=self.source/(row['id']+'-response.bin');path.write_bytes(path.read_bytes()+b'changed');row['response_sha256']=tsep.digest(path)
  (self.source/'requests.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows));closed=tsep.read_json(self.source/'closed.json');closed['log_sha256']=tsep.digest(self.source/'requests.jsonl');(self.source/'closed.json').write_bytes(package.json_bytes(closed))
  with self.assertRaisesRegex(tsep.Invalid,'prior bytes'):lab.analyze(self.source,observations)
 def test_wrong_agent_and_clock_do_not_become_new_attempts(self):
  plan,observations=self.exercise();self.stop();bad=copy.deepcopy(observations);bad[plan['tasks'][0]['id']]['navigation_started_at']='2099-01-01T00:00:00Z'
  with self.assertRaisesRegex(tsep.Invalid,'chronology'):lab.analyze(self.source,bad)
  record=tsep.read_json(self.source/'plan.json');record['agent']='Different';(self.source/'plan.json').write_bytes(package.json_bytes(record));closed=tsep.read_json(self.source/'closed.json');closed['plan_sha256']=tsep.digest(self.source/'plan.json');(self.source/'closed.json').write_bytes(package.json_bytes(closed))
  with self.assertRaisesRegex(tsep.Invalid,'calibration'):lab.analyze(self.source,observations)

 def test_recipe_is_prefrozen_and_unlisted_file_is_refused(self):
  self.assertEqual(tsep.digest(lab.ROOT/lab.RECIPE),'eb41bfe824d86d5f6c9f2c6c15316544ae77d0814f81ba0866204eecf1690811')
  plan,observations=self.exercise();self.stop();(self.source/'unlisted.bin').write_bytes(b'not an allowed capture')
  with self.assertRaisesRegex(tsep.Invalid,'unlisted'):lab.analyze(self.source,observations)

 def test_session_calibration_is_retained_and_cannot_be_sealed(self):
  self.assertEqual(self.request(self.info['base']+'/calibrate',extra_headers={'Cookie':'authored=test-only'})[0],200)
  with self.assertRaisesRegex(tsep.Invalid,'session headers'):lab.seal(self.source,'Authored HTTP client','1')
  self.assertFalse((self.source/'plan.json').exists())
  self.assertIn(b'Cookie: authored=test-only',next(self.source.glob('*-request.bin')).read_bytes())

 def test_isolated_origin_binds_loopback_and_uses_new_hostname(self):
  server,record=lab.start(self.root/'isolated','isolated-localhost')
  try:
   self.assertEqual(server.server_address[0],'127.0.0.1')
   self.assertEqual(urlsplit(record['origin']).hostname,record['token']+'.localhost')
  finally:server.server_close()

 def repair_server(self):
  self.server.shutdown();self.server.server_close();self.thread.join()
  self.source=self.root/'repair'
  self.server,self.info=lab.start(self.source,recipe_file=lab.REPAIR_RECIPE)
  self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()

 def test_preplanned_repair_sequence_uses_same_url_and_offline_replay(self):
  self.assertEqual(tsep.digest(lab.ROOT/lab.REPAIR_RECIPE),'83d644bb2adbe7915dea3df7d8853e33c8593ba7af6cc7e99487731d5523c4fc')
  self.repair_server();plan,observations=self.exercise();self.stop()
  self.assertEqual(len(plan['tasks']),9)
  for offset in (0,3,6):
   tasks=plan['tasks'][offset:offset+3]
   self.assertEqual([t['phase'] for t in tasks],['baseline','fault','repaired'])
   self.assertEqual(len({t['url'] for t in tasks}),1)
   self.assertEqual(len({t['navigation_id'] for t in tasks}),3)
  path=self.root/'observations.json';lab.save(path,observations)
  with patch('socket.socket',side_effect=AssertionError('offline')):
   self.assertTrue(lab.finish(self.source,path,self.root/'delivery')['all_expected_matched'])
   self.assertEqual(lab.replay_delivery(self.root/'delivery')['observations'],9)
  self.assertEqual(len(lab.logs(self.source)),19)

 def test_repair_sequence_refuses_wrong_resource_before_visit(self):
  self.repair_server();plan=self.calibrate()
  self.assertEqual(self.request(plan['tasks'][3]['url'])[0],400)
  self.assertEqual(self.server.navigation_index,0)
  self.assertIn('Out-of-order',lab.logs(self.source)[-1]['error'])

 def test_repair_sequence_requires_export_before_next_phase(self):
  self.repair_server();plan=self.calibrate()
  self.assertEqual(self.request(plan['tasks'][0]['url'])[0],200)
  self.assertEqual(self.request(plan['tasks'][1]['url'])[0],400)
  self.assertEqual(self.server.navigation_index,1)
  self.assertIn('Previous export missing',lab.logs(self.source)[-1]['error'])
