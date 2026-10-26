"""Authored Google-shaped records, never actual Google responses."""
import copy,hashlib,json,unittest
from conformance.access_evidence import assess
from conformance.evaluate import binding_digest
from conformance.http import Unknown

class AccessEvidence(unittest.TestCase):
    def target(self):
        request=json.dumps({'inspectionUrl':'https://site.invalid/a','siteUrl':'sc-domain:site.invalid'})
        response=json.dumps({'inspectionResult':{'indexStatusResult':{'lastCrawlTime':'2026-10-26T00:00:01Z','pageFetchState':'SUCCESSFUL','robotsTxtState':'ALLOWED'}}})
        return {'url':'https://site.invalid/a','observed_at':'2026-10-26T00:00:00Z','http':[], 'intent':{'access_evidence_profile':'ts07-access-evidence-v1'},'access_inspection':{'url':'https://site.invalid/a','provenance':'supplied-google-api','http_status':200,'complete':True,'authorized_property':'sc-domain:site.invalid','retrieved_at':'2026-10-26T00:00:02Z','request':{'raw_text':request,'sha256':hashlib.sha256(request.encode()).hexdigest()},'response':{'raw_text':response,'sha256':hashlib.sha256(response.encode()).hexdigest()}}}
    def test_recent_exact_authorized_inspection(self):self.assertEqual(assess(self.target())[0],'pass')
    def test_old_future_failed_fetch_or_robots(self):
        for k,v in [('lastCrawlTime','2026-10-25T23:59:59Z'),('lastCrawlTime','2026-10-26T00:00:03Z'),('pageFetchState','ACCESS_DENIED'),('robotsTxtState','DISALLOWED')]:
            t=self.target();r=t['access_inspection']['response'];data=json.loads(r['raw_text']);data['inspectionResult']['indexStatusResult'][k]=v;r['raw_text']=json.dumps(data);r['sha256']=hashlib.sha256(r['raw_text'].encode()).hexdigest()
            with self.assertRaises(Unknown):assess(t)
    def test_mismatch_and_incomplete(self):
        for k,v in [('url','https://site.invalid/b'),('authorized_property','sc-domain:else.invalid'),('complete',False),('http_status',403)]:
            t=self.target();t['access_inspection'][k]=v
            with self.assertRaises(Unknown):assess(t)
    def test_invalid_property_type_is_unknown(self):
        t=self.target();record=t['access_inspection']['request'];request=json.loads(record['raw_text']);request['siteUrl']=None
        record['raw_text']=json.dumps(request);record['sha256']=hashlib.sha256(record['raw_text'].encode()).hexdigest()
        with self.assertRaises(Unknown):assess(t)
    def test_observed_disallow_precedes_declaration(self):
        from conformance.evaluate import evaluate
        from pathlib import Path
        cases=json.loads((Path(__file__).resolve().parents[1]/'conformance/cases.json').read_text())['cases']
        data=copy.deepcopy(next(c['input'] for c in cases if c['id']=='complete-reference'))
        data['rules']=['TS07-A02'];t=data['targets'][0]
        t['intent']['access_evidence_profile']='ts07-access-evidence-v1'
        t['robots']['http'][0]['response']=t['robots']['http'][0]['response'].replace('Disallow:', 'Disallow: /')
        t['access_review'].update(provenance='user-declaration',source_http_sha256=binding_digest(t['http']),reason='I reviewed the displayed page and know of no rule blocking search crawlers')
        self.assertEqual(evaluate(data)[0]['outcome'],'fail')
    def test_fingerprint(self):
        t=self.target();t['access_inspection']['response']['raw_text']+=' '
        with self.assertRaises(Unknown):assess(t)
    def test_declaration_is_bound_and_explicit(self):
        t=self.target();t.pop('access_inspection');t['access_review']={'provenance':'user-declaration','outcome':'no-obstacle','reason':'I reviewed the displayed page and know of no rule blocking search crawlers','observed_at':'2026-10-26T00:00:01Z','source_http_sha256':binding_digest(t['http'])}
        self.assertEqual(assess(t)[0],'pass');self.assertIn('user declaration',assess(t)[1]);t['access_review']['source_http_sha256']='0'*64
        with self.assertRaises(Unknown):assess(t)

if __name__=='__main__':unittest.main()
