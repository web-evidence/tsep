"""Synthetic counterexamples for bounded public observations; no external network."""
import copy
import hashlib
import json
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import unittest
from unittest.mock import patch
from urllib.parse import urlsplit
from conformance.public_probes import assess,digest
from conformance.http import encoded
from collectors.http import request_bytes
from collectors.anonymous_probe import collect

START='2026-10-26T00:00:00+00:00'
END='2026-10-26T00:00:05+00:00'
AGENT='TSEP-Probe/1'
URL='https://public.invalid/a/'
MISSING=URL+'tsep-check-'+'a'*32

def hop(url,status,location=None):
    headers='Content-Length: 0\r\n'+('Location: '+location+'\r\n' if location else '')
    return {'url':url,'complete':True,'request':encoded(request_bytes(url,AGENT,'identity')),'response':encoded(('HTTP/1.1 '+str(status)+' Test\r\n'+headers+'\r\n').encode())}

def target03(status=404):
    p={'profile':'public-probes-v1','control':'TS03','url':URL,'declared_at':START,'agent':AGENT,'generated_assumption':'expected-absent-not-proven','routes':[{'kind':'existing','url':URL},{'kind':'generated','url':MISSING}]}
    return {'url':URL,'observed_at':END,'intent':{'public_probe':p},'configuration':{'public_probe_sha256':digest(p)},'probe_documents':[{'url':u,'observed_at':END,'http':[hop(u,s)]} for u,s in [(URL,200),(MISSING,status)]]}

def target06(status=401,expectation='authentication'):
    p={'profile':'public-probes-v1','control':'TS06','url':URL,'declared_at':START,'agent':AGENT,'expectation':expectation,'login_url':'https://public.invalid/login'}
    r={'profile':'anonymous-http-redacted-v1','url':URL,'agent':AGENT,'method':'GET','cookies':False,'credentials':False,'plan_sha256':digest(p),'started_at':START,'finished_at':END,'complete':True,'status':status,'body_bytes':0,'body_retained':False,'redirect_followed':False,'authentication_schemes':['basic']}
    r.update({k:hashlib.sha256(b'').hexdigest() for k in ('response_sha256','headers_sha256','body_sha256')})
    return {'url':URL,'observed_at':END,'intent':{'public_probe':p},'configuration':{'public_probe_sha256':digest(p)},'anonymous_probe':r}

class PublicProbes(unittest.TestCase):
    def test_ts03_status_matrix(self):
        for status,want in [(404,'pass'),(410,'pass'),(200,'fail'),(401,'inconclusive'),(403,'inconclusive'),(429,'inconclusive'),(500,'inconclusive'),(206,'inconclusive'),(304,'inconclusive')]:
            with self.subTest(status=status):self.assertEqual(assess(target03(status),'TS03-A02')[0],want)
    def test_ts03_redirect200_is_fail(self):
        t=target03();t['probe_documents'][1]['http']=[hop(MISSING,301,URL),hop(URL,200)]
        self.assertEqual(assess(t,'TS03-A02')[0],'fail')
    def test_ts03_fail_survives_missing_or_duplicate(self):
        t=target03(200);t['probe_documents'].append(copy.deepcopy(t['probe_documents'][1]));t['probe_documents'].pop(0)
        self.assertEqual(assess(t,'TS03-A02')[0],'fail')
    def test_ts03_duplicate_pass_does_not_pass(self):
        t=target03();t['probe_documents'].append(copy.deepcopy(t['probe_documents'][1]))
        self.assertEqual(assess(t,'TS03-A02')[0],'inconclusive')
    def test_ts03_missing_binding_random_path_future_agent(self):
        changes=[lambda t:t['configuration'].clear(),lambda t:t['intent']['public_probe'].update(declared_at='2026-10-27T00:00:00Z'),lambda t:t['probe_documents'][1]['http'][0].update(request=encoded(request_bytes(MISSING,'Other/1','identity'))),lambda t:t['probe_documents'][1].update(http=[hop(MISSING,302,'https://else.invalid/'),hop('https://else.invalid/',404)])]
        for f in changes:
            t=target03();f(t);self.assertEqual(assess(t,'TS03-A02')[0],'inconclusive')
    def test_ts03_removed_route_not_assessed_by_generated_probe(self):
        t=target03();p=t['intent']['public_probe'];p['routes'].append({'kind':'removed','url':'https://public.invalid/old'})
        t['configuration']['public_probe_sha256']=digest(p)
        self.assertEqual(assess(t,'TS03-A02')[0],'inconclusive')
    def test_ts06_status_matrix(self):
        for status,want in [(401,'pass'),(403,'inconclusive'),(429,'inconclusive'),(500,'inconclusive'),(200,'fail'),(302,'inconclusive')]:
            with self.subTest(status=status):self.assertEqual(assess(target06(status),'TS06-A02')[0],want)
    def test_ts06_challenge_required(self):
        t=target06();t['anonymous_probe']['authentication_schemes']=[]
        self.assertEqual(assess(t,'TS06-A02')[0],'inconclusive')
    def test_ts06_exact_login_and_404(self):
        t=target06(302,'login');t['anonymous_probe']['location_origin_path_sha256']=hashlib.sha256(t['intent']['public_probe']['login_url'].encode()).hexdigest()
        self.assertEqual(assess(t,'TS06-A02')[0],'pass')
        t['anonymous_probe']['location_origin_path_sha256']='0'*64
        self.assertEqual(assess(t,'TS06-A02')[0],'inconclusive')
        self.assertEqual(assess(target06(404,'not-found'),'TS06-A02')[0],'inconclusive')
    def test_ts06_signed_url_refused(self):
        t=target06();t['url']+='?token=secret';t['intent']['public_probe']['url']=t['url'];t['configuration']['public_probe_sha256']=digest(t['intent']['public_probe'])
        self.assertEqual(assess(t,'TS06-A02')[0],'inconclusive')
    def test_ts06_no_positive_from_missing_or_retained_body(self):
        for key,value in [('complete',False),('cookies',True),('credentials',True),('body_retained',True),('body_sha256','bad'),('plan_sha256','0'*64)]:
            t=target06();t['anonymous_probe'][key]=value
            self.assertEqual(assess(t,'TS06-A02')[0],'inconclusive')
    def test_collector_redacts_private_body_and_headers(self):
        secret=b'SYNTHETIC PRIVATE BODY NEVER SAVE'
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.server.received=dict(self.headers);self.send_response(200);self.send_header('Content-Length',str(len(secret)));self.send_header('Set-Cookie','secret=fixture');self.end_headers();self.wfile.write(secret)
            def log_message(self,*args):pass
        server=ThreadingHTTPServer(('127.0.0.1',0),Handler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        try:
            p=target06()['intent']['public_probe'];p['url']='http://127.0.0.1:'+str(server.server_port)+'/'
            r=collect(p,allow_loopback=True)
            self.assertTrue(r['complete'],r);self.assertEqual(r['status'],200);self.assertEqual(r['body_sha256'],hashlib.sha256(secret).hexdigest())
            self.assertNotIn('PRIVATE',json.dumps(r));self.assertNotIn('fixture',json.dumps(r));self.assertNotIn('Cookie',server.received);self.assertNotIn('Authorization',server.received)
            r=collect(p);self.assertFalse(r['complete'])
        finally:server.shutdown();server.server_close();thread.join()
    def test_collector_redirect_query_redacted_and_bare_challenge(self):
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(302 if self.path=='/redirect' else 401)
                if self.path=='/redirect':self.send_header('Location','/login?returnTo=PRIVATE_TOKEN')
                else:self.send_header('WWW-Authenticate','Negotiate')
                self.send_header('Content-Length','0');self.end_headers()
            def log_message(self,*args):pass
        server=ThreadingHTTPServer(('127.0.0.1',0),Handler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        try:
            p=target06()['intent']['public_probe'];base='http://127.0.0.1:'+str(server.server_port)
            p['url']=base+'/redirect';r=collect(p,allow_loopback=True)
            self.assertTrue(r['complete']);self.assertEqual(r['location_origin_path_sha256'],hashlib.sha256((base+'/login').encode()).hexdigest())
            self.assertNotIn('PRIVATE_TOKEN',json.dumps(r));self.assertNotIn('returnTo',json.dumps(r))
            p['url']=base+'/private';r=collect(p,allow_loopback=True)
            self.assertTrue(r['complete']);self.assertEqual(r['authentication_schemes'],['negotiate'])
        finally:server.shutdown();server.server_close();thread.join()

if __name__=='__main__':unittest.main()
