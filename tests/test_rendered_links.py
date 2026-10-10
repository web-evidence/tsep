"""Authored records exercise refusals, not browser behavior or independent oracles."""
import copy
import http.client
import json
from pathlib import Path
import tempfile
import threading
import time
import unittest
from urllib.parse import urlsplit

from experiments import rendered_links as o
from examples import rendered_links_lab as lab


def authored(url='https://example.test/page'):
    facts=dict(url=url,base_uri=url,character_set='UTF-8',content_type='text/html',ready_state='complete')
    return dict(format='rendered-link-observation',version='1',limits=dict(o.LIMITS),coverage=dict(o.COVERAGE),
        document_before=facts,document_after=dict(facts),records=[],nodes_visited=1,
        traversal_complete=True,stop_reason=None,errors=[],elapsed_ms=0)


def record(data,href=None,property='',tag='a',namespace=o.HTML):
    attrs=[] if href is None else [dict(name='href',local_name='href',namespace=None,value=href)]
    r=dict(order=len(data['records']),visit=len(data['records'])+2,path=[len(data['records'])],ancestors=[],
           tag=tag,namespace=namespace,selected_reason='named-element',attributes=attrs,
           node_base_uri=data['document_before']['base_uri'],shadow_root='unexposed-or-absent',href_property=property)
    data['records'].append(r);data['nodes_visited']+=1;return r


class RenderedLinks(unittest.TestCase):
    def test_absence_empty_invalid_and_valid_href_are_not_conflated(self):
        data=authored()
        for raw,prop in [(None,''),('','https://example.test/page'),('http://[x','http://[x'),('https://example.test/x','https://example.test/x')]:
            record(data,raw,prop)
        before=copy.deepcopy(data);result=o.inventory(data)
        self.assertEqual([r['raw_href'] for r in result['records']],[None,'','http://[x','https://example.test/x'])
        self.assertEqual(data,before);self.assertEqual(result['normative_effect'],'none')
        self.assertFalse(any(k in result for k in ('pass','verdict','url_valid')))

    def test_foreign_attributes_and_ancestry_remain_separate(self):
        data=authored();r=record(data,'plain',None,namespace='http://www.w3.org/2000/svg')
        r['attributes'].append(dict(name='xlink:href',local_name='href',namespace=o.XLINK,value='legacy'))
        v=o.inventory(data)['records'][0];self.assertEqual((v['raw_href'],v['xlink_href']),('plain','legacy'))
        r['href_property']='https://example.test/plain'
        with self.assertRaisesRegex(ValueError,'Unsupported'):o.inventory(data)

    def test_partial_observation_retains_prefix_without_complete_claim(self):
        data=authored();record(data,'/a','https://example.test/a')
        data.update(traversal_complete=False,stop_reason='node-limit',errors=['node-limit'],document_after=None)
        v=o.inventory(data);self.assertFalse(v['traversal_complete']);self.assertFalse(v['document_facts_equal'])
        self.assertEqual(len(v['records']),1)
        data['traversal_complete']=True
        with self.assertRaises(ValueError):o.inventory(data)

    def test_base_change_does_not_become_stable_or_get_repaired(self):
        data=authored();data['document_after']['base_uri']='https://example.test/changed/'
        self.assertFalse(o.inventory(data)['document_facts_equal'])
        record(data,'x','https://example.test/x');data['records'][0]['node_base_uri']='https://example.test/other/'
        self.assertEqual(o.inventory(data)['records'][0]['node_base_uri'],'https://example.test/other/')

    def test_truncated_or_relabeled_records_refused(self):
        data=authored();record(data,'x','https://example.test/x')
        variants=[]
        for key,value in [('coverage',{}),('limits',{}),('nodes_visited',0),('records',{}),('traversal_complete',1)]:
            bad=copy.deepcopy(data);bad[key]=value;variants.append(bad)
        for key,value in [('attributes',[{'name':'href','value':'x'}]),('order',1),('visit',99),('path',[True]),('href_property',None),('selected_reason','ignored')]:
            bad=copy.deepcopy(data);bad['records'][0][key]=value;variants.append(bad)
        for bad in variants:
            with self.assertRaises(ValueError):o.inventory(bad)

    def test_unavailable_API_and_byte_budgets(self):
        data=authored();data.update(document_before=None,document_after=None,traversal_complete=False,
            stop_reason='unavailable-api',errors=['unavailable-api'],nodes_visited=0)
        self.assertFalse(o.inventory(data)['traversal_complete'])
        data=authored();record(data,'x'*(o.LIMITS['string_bytes']+1),'x')
        with self.assertRaisesRegex(ValueError,'bound'):o.inventory(data)

    def test_duplicate_path_attribute_or_label_is_refused(self):
        data=authored();a=record(data,'x','x');b=record(data,'y','y');b['path']=a['path']
        with self.assertRaisesRegex(ValueError,'Duplicate physical'):o.inventory(data)
        b['path']=[1];a['attributes']*=2
        with self.assertRaisesRegex(ValueError,'Duplicate attribute'):o.inventory(data)
        a['attributes']=a['attributes'][:1]
        for r in (a,b):r['attributes'].append(dict(name='data-probe',local_name='data-probe',namespace=None,value='same'))
        with self.assertRaisesRegex(ValueError,'Duplicate laboratory'):o.projection(data)

    def test_frozen_recipe_is_authored_not_a_generated_observation(self):
        recipe=o.recipes();self.assertEqual(len(recipe['cases']),26)
        self.assertEqual(sum(len(c['expected']) for c in recipe['cases']),36)
        self.assertTrue(recipe['synthetic']);self.assertEqual(recipe['normative_effect'],'none')


class RenderedLinkLaboratory(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.folder=Path(self.temp.name)/'lab'
        self.server,self.server_record=lab.start(self.folder)
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start();self.running=True

    def stop(self):
        if self.running:
            self.server.shutdown();self.thread.join();lab.close(self.server);self.running=False

    def tearDown(self):
        self.stop();self.temp.cleanup()

    def request(self,url,body=None):
        p=urlsplit(url);conn=http.client.HTTPConnection('127.0.0.1',p.port,timeout=5)
        conn.request('POST' if body else 'GET',p.path,body=body,headers={'Host':p.netloc,'User-Agent':'AUTHORED-TRANSPORT/1'})
        response=conn.getresponse();raw=response.read();status=response.status;conn.close()
        for _ in range(100):
            if len(lab.transport.logs(self.folder))>=self.server.sequence:break
            time.sleep(.005)
        self.assertEqual(status,200,raw);return raw

    def campaign(self):
        plan=json.loads((self.folder/'plan.json').read_bytes());self.request(self.server_record['base']);results=[]
        for task,case in zip(plan['tasks'],plan['recipe']['cases']):
            started=lab.transport.now();self.request(task['url']);data=authored(task['url'])
            base=lab.replace(case['expected_base'],task['url'],self.server_record['origin'])
            data['document_before']['base_uri']=base;data['document_after']['base_uri']=base
            for key,value in lab.replace(case['expected'],task['url'],self.server_record['origin']).items():
                r=record(data,value['raw_href'],value['href_property'],value['tag'],value['namespace'])
                r['attributes'].append(dict(name='data-probe',local_name='data-probe',namespace=None,value=key))
                if value.get('xlink_href') is not None:r['attributes'].append(dict(name='xlink:href',local_name='href',namespace=o.XLINK,value=value['xlink_href']))
                if value.get('in_shadow'):r['path']=['shadow']+r['path']
                if value.get('foreign_ancestor'):r['ancestors']=[dict(tag='svg',namespace='http://www.w3.org/2000/svg')]
                if value['tag'] in ('input','button'):
                    r['selected_reason']='form-override';r['attributes'].append(dict(name='formaction',local_name='formaction',namespace=None,value='/synthetic'))
            results.append(dict(id=task['id'],url=task['url'],started_at=started,observed_at=lab.transport.now(),observation=data))
        payload=dict(kind='rendered-link-browser-campaign',version='1',token=self.server_record['token'],
            plan_sha256=lab.sha((self.folder/'plan.json').read_bytes()),controller_url=self.server_record['base'],
            user_agent='AUTHORED-TRANSPORT/1',results=results,errors=[],complete=True)
        self.request(self.server_record['base']+'/capture',json.dumps(payload).encode());self.stop()

    def test_authored_transport_binds_all_prior_responses(self):
        self.campaign();r=lab.analyze(self.folder)
        self.assertEqual((r['matching'],r['total']),(26,26));self.assertEqual(r['user_agent'],'AUTHORED-TRANSPORT/1')

    def test_missing_export_refused(self):
        self.request(self.server_record['base']);self.stop()
        with self.assertRaisesRegex(ValueError,'Missing/duplicate'):lab.analyze(self.folder)

    def test_response_changed_even_with_updated_log_hash_is_refused(self):
        self.campaign();rows=lab.transport.logs(self.folder);row=next(r for r in rows if r['kind']=='case')
        path=self.folder/(row['id']+'-response.bin');path.write_bytes(path.read_bytes()+b'changed');row['response_sha256']=lab.sha(path.read_bytes())
        (self.folder/'requests.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
        p=self.folder/'closed.json';closed=json.loads(p.read_bytes());closed['log_sha256']=lab.sha((self.folder/'requests.jsonl').read_bytes());p.write_text(json.dumps(closed))
        with self.assertRaisesRegex(ValueError,'prior bytes'):lab.analyze(self.folder)


if __name__=='__main__':unittest.main()
