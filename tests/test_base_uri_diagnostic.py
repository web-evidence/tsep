"""Authored records validate the harness, not actual browser semantics."""
import copy
import http.client
import json
from pathlib import Path
import tempfile
import threading
import time
import unittest
from urllib.parse import urlsplit
from examples import base_uri_diagnostic as lab
from tests.test_rendered_links import authored, record


class BaseURIDiagnostic(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.folder=Path(self.temp.name)/'diagnostic'
        self.server,self.info=lab.start(self.folder)
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start();self.running=True

    def stop(self):
        if self.running:
            self.server.shutdown();self.thread.join();lab.close(self.server);self.running=False

    def tearDown(self):
        self.stop();self.temp.cleanup()

    def request(self,url,payload=None):
        p=urlsplit(url);body=json.dumps(payload).encode() if payload else None
        c=http.client.HTTPConnection('127.0.0.1',p.port,timeout=5)
        c.request('POST' if body else 'GET',p.path,body=body,headers={'Host':p.netloc,'User-Agent':'AUTHORED-BASE-URI/1'})
        r=c.getresponse();raw=r.read();status=r.status;c.close()
        for _ in range(100):
            if len(lab.transport.logs(self.folder))>=self.server.sequence:break
            time.sleep(.005)
        self.assertEqual(status,200,raw);return raw

    def campaign(self):
        plan=json.loads((self.folder/'plan.json').read_bytes());self.request(self.info['base'])
        for task in plan['tasks']:
            case=next(c for c in plan['recipe']['cases'] if c['id']==task['case_id']);self.request(task['url']);phases=[]
            for phase in ('before','after'):
                started=lab.transport.now();expected=lab.links.replace(case['expected'][phase],task['url'],self.info['origin'])
                expected={k:v.replace('${CONTEXT}',task['context']) for k,v in expected.items()}
                obs=authored(task['url']);obs['document_before']['base_uri']=expected['base'];obs['document_after']['base_uri']=expected['base']
                a=record(obs,'x',expected['href']);a['attributes'].append(dict(name='id',local_name='id',namespace=None,value='anchor-probe'))
                direct=dict(document_url=task['url'],base_uri=expected['base'],anchor_base_uri=expected['base'],raw_href='x',href_property=expected['href'],bases=[],parsed_against_document={'ok':True},parsed_against_observed_base={'ok':True})
                phases.append(dict(phase=phase,started_at=started,observed_at=lab.transport.now(),observation=obs,direct=direct))
            value=dict(kind='base-uri-diagnostic-export',version='1',task_id=task['id'],token=self.info['token'],
                script_sha256=plan['source_files'][lab.observer.SCRIPT],context=task['context'],user_agent='AUTHORED-BASE-URI/1',phases=phases)
            self.request(self.info['base']+'/capture',value)
        self.stop()

    def change_export(self,edit):
        rows=lab.transport.logs(self.folder);row=next(r for r in rows if r['kind']=='capture')
        p=self.folder/(row['id']+'-request.bin');first,headers,body=lab.message(p.read_bytes());data=json.loads(body);edit(data);body=json.dumps(data).encode()
        raw=(first+'\r\n'+''.join(k+': '+v+'\r\n' for k,vs in headers.items() if k!='content-length' for v in vs)+
             'Content-Length: '+str(len(body))+'\r\n\r\n').encode()+body
        p.write_bytes(raw);row['request_sha256']=lab.sha(raw);row['receipt']=lab.sha(body)
        (self.folder/'requests.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
        p=self.folder/'closed.json';c=json.loads(p.read_bytes());c['log_sha256']=lab.sha((self.folder/'requests.jsonl').read_bytes());p.write_text(json.dumps(c))

    def test_authored_transport_replays_all_phases(self):
        self.campaign();r=lab.analyze(self.folder)
        self.assertEqual((r['matching'],r['total']),(24,24));self.assertEqual(r['normative_effect'],'none')
        self.assertEqual(r['user_agent'],'AUTHORED-BASE-URI/1')

    def test_missing_capture_refused(self):
        self.request(self.info['base']);self.stop()
        with self.assertRaisesRegex(ValueError,'Missing/duplicate'):lab.analyze(self.folder)

    def test_getter_and_collector_disagreement_refused(self):
        self.campaign();self.change_export(lambda d:d['phases'][0]['direct'].__setitem__('base_uri','about:blank'))
        with self.assertRaisesRegex(ValueError,'API reads disagree'):lab.analyze(self.folder)

    def test_changed_context_refused_even_with_new_fingerprints(self):
        self.campaign();self.change_export(lambda d:d.__setitem__('context','frame'))
        with self.assertRaisesRegex(ValueError,'binding'):lab.analyze(self.folder)

    def test_missing_phase_cannot_be_reconstructed(self):
        self.campaign();self.change_export(lambda d:d['phases'].pop())
        with self.assertRaisesRegex(ValueError,'phase'):lab.analyze(self.folder)

    def test_changed_prior_response_is_refused(self):
        self.campaign();p=self.folder/'planned/top-no-base.bin';p.write_bytes(p.read_bytes()+b'changed')
        with self.assertRaisesRegex(ValueError,'prior bytes'):lab.analyze(self.folder)


if __name__=='__main__':unittest.main()
