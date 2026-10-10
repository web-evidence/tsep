"""Authored transport records test the harness; they are NOT browser measurements."""
import copy
import http.client
import json
from pathlib import Path
import tempfile
import threading
import time
import unittest
from urllib.parse import urlsplit

from examples import source_browser_lab as lab


class SourceBrowserLaboratory(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.folder=Path(self.temp.name)/'source'
        self.server,self.record=lab.start(self.folder)
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
        self.running=True

    def stop(self):
        if self.running:
            self.server.shutdown();self.thread.join();lab.close(self.server);self.running=False

    def tearDown(self):
        self.stop();self.temp.cleanup()

    def request(self,url,body=None):
        parts=urlsplit(url);conn=http.client.HTTPConnection('127.0.0.1',parts.port,timeout=5)
        conn.request('POST' if body else 'GET',parts.path,body=body,headers={
            'Host':parts.netloc,'User-Agent':'SYNTHETIC-TRANSPORT/1','Content-Type':'application/json'})
        response=conn.getresponse();data=response.read();status=response.status;conn.close()
        for _ in range(100):
            if len(lab.transport.logs(self.folder))>=self.server.sequence:break
            time.sleep(.005)
        self.assertEqual(status,200,data)
        return data

    def authored_campaign(self):
        plan=json.loads((self.folder/'plan.json').read_bytes());self.request(self.record['base']);results=[]
        for task in plan['tasks']:
            started=lab.transport.now();self.request(task['url'])
            expected = ({k:[] for k in ('head','body','template','shadow')} if task['id']=='calibration' else
              next(c for c in plan['recipe']['cases'] if c['id']==task['id'])['expected_browser'][task['mode']])
            tree={'url':task['url'],'ready_state':'complete','character_set':'UTF-8','content_type':'text/html',
                  'signals':[{'id':id,'context':key} for key,ids in expected.items() for id in ids],
                  'html':'AUTHORED TEST RECORD, NOT A BROWSER OBSERVATION'}
            row={'id':task['id'],'mode':task['mode'],'url':task['url'],
                 'sandbox':plan['recipe']['modes'][task['mode']],'started_at':started,
                 'observed_at':lab.transport.now(),'tree':tree}
            if task['id']=='calibration':row['calibration']=plan['recipe']['calibration'][task['mode']]
            results.append(row)
        data={'kind':'synthetic-source-browser-observation','version':'1','token':self.record['token'],
              'plan_sha256':lab.sha((self.folder/'plan.json').read_bytes()),'user_agent':'SYNTHETIC-TRANSPORT/1',
              'controller_url':self.record['base'],'observed_at':lab.transport.now(),'results':results,
              'errors':[],'complete':True}
        self.request(self.record['base']+'/capture',json.dumps(data).encode());self.stop();return plan,data

    def change_export(self,change):
        rows=lab.transport.logs(self.folder);capture=next(r for r in rows if r['kind']=='capture')
        path=self.folder/(capture['id']+'-request.bin');first,headers,body=lab.message(path.read_bytes())
        data=json.loads(body);change(data);body=json.dumps(data).encode()
        raw=(first+'\r\n'+''.join(k+': '+v+'\r\n' for k,values in headers.items() if k!='content-length'
              for v in values)+'Content-Length: '+str(len(body))+'\r\n\r\n').encode()+body
        path.write_bytes(raw);capture['request_sha256']=lab.sha(raw);capture['receipt']=lab.sha(body)
        (self.folder/'requests.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
        path=self.folder/'closed.json';closed=json.loads(path.read_bytes());closed['log_sha256']=lab.sha((self.folder/'requests.jsonl').read_bytes());path.write_text(json.dumps(closed))

    def test_frozen_bytes_and_comparison_with_authored_records(self):
        self.authored_campaign();result=lab.analyze(self.folder)
        self.assertEqual(result['matching'],72);self.assertEqual(result['normative_effect'],'none')
        self.assertEqual(result['user_agent'],'SYNTHETIC-TRANSPORT/1')

    def test_missing_and_duplicate_observations_are_rejected(self):
        self.authored_campaign()
        self.change_export(lambda d:d['results'].__setitem__(-1,copy.deepcopy(d['results'][0])))
        with self.assertRaisesRegex(ValueError,'Missing/duplicate'):lab.analyze(self.folder)

    def test_calibration_and_mode_cannot_be_forged_by_changing_checksum(self):
        self.authored_campaign()
        self.change_export(lambda d:d['results'][0]['calibration'].__setitem__('script','ran'))
        with self.assertRaisesRegex(ValueError,'Calibration'):lab.analyze(self.folder)

    def test_changed_prior_response_is_not_hidden_by_a_new_log_digest(self):
        self.authored_campaign();rows=lab.transport.logs(self.folder);row=next(r for r in rows if r['kind']=='frame')
        path=self.folder/(row['id']+'-response.bin');path.write_bytes(path.read_bytes()+b'changed');row['response_sha256']=lab.sha(path.read_bytes())
        (self.folder/'requests.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
        p=self.folder/'closed.json';closed=json.loads(p.read_bytes());closed['log_sha256']=lab.sha((self.folder/'requests.jsonl').read_bytes());p.write_text(json.dumps(closed))
        with self.assertRaisesRegex(ValueError,'prior bytes'):lab.analyze(self.folder)


if __name__=='__main__':unittest.main()
