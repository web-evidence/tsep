"""Authored structured snapshots; browser execution is a separate recorded campaign."""
import copy
import json
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from experiments import rendered_metadata as m


def tree():
    return {'format':'rendered-metadata-tree','version':m.VERSION,'limits':dict(m.LIMITS),
            'document_url':'https://example.test/page','base_uri':'https://example.test/page',
            'ready_state':'complete','execution_context':'not-attested','scripting':'enabled-by-laboratory-plan',
            'closed_shadow_coverage':'unknown','frame_documents':'not-collected','template_fragments':'not-collected',
            'origin_attribution':'unknown','serialization':{'available':True,'html':'AUTHORED FIXTURE, NOT A BROWSER'},
            'nodes':[],'reported_node_count':0,'traversal_complete':True,'stop_reason':None,'api_errors':[],'elapsed_ms':0}


def add(t,parent,name,attributes=(),namespace=m.HTML,type_=1,edge='child',data=None,shadow=None,resolved=None):
    index=sum(n['parent']==parent and n['edge']=='child' for n in t['nodes']) if parent is not None else 0
    if parent is not None and edge=='child':t['nodes'][parent]['child_count']+=1
    n={'id':len(t['nodes']),'parent':parent,'edge':'root' if parent is None else edge,'index':0 if edge=='shadow' else index,
       'type':type_,'name':name,'namespace':namespace if type_==1 else None,
       'attributes':[dict(name=k,local_name=k,namespace=None,value=v) for k,v in attributes],
       'data':data,'child_count':0,'shadow':shadow or ('unexposed-or-absent' if type_==1 else 'not-element'),'resolved_href':resolved}
    t['nodes'].append(n);t['reported_node_count']=len(t['nodes']);return n['id']


def scaffold():
    t=tree();add(t,None,'#document',type_=9);add(t,0,'html');add(t,1,'head')
    return t


class RenderedMetadata(unittest.TestCase):
    def test_transport_truncation_is_refused_even_for_partial_capture(self):
        t=scaffold();t['traversal_complete']=False;t['stop_reason']='node-limit'
        t['reported_node_count']+=1
        with self.assertRaisesRegex(ValueError,'Transport'):m.inventory(t)

    def test_unavailable_api_is_not_inferred_or_called_complete(self):
        t=tree();t['base_uri']=None;t['serialization']=None
        t['traversal_complete']=False;t['stop_reason']='api-error';t['api_errors']=['Unavailable DOM API: document.baseURI']
        result=m.inventory(t)
        self.assertIsNone(result['base_uri']);self.assertFalse(result['traversal_complete'])
        self.assertEqual(result['metadata'],[])
        t['api_errors']=[]
        with self.assertRaisesRegex(ValueError,'API error'):m.inventory(t)

    def test_missing_attribute_namespace_cannot_be_reconstructed(self):
        t=scaffold();add(t,2,'link',[('rel','canonical')]);del t['nodes'][3]['attributes'][0]['namespace']
        with self.assertRaisesRegex(ValueError,'attribute'):m.inventory(t)

    def test_non_html_document_cannot_gain_head_classification(self):
        t=scaffold();t['nodes'][1]['namespace']='http://www.w3.org/2000/svg'
        with self.assertRaisesRegex(ValueError,'document element'):m.inventory(t)

    def test_relative_is_not_replaced_by_resolved_and_attributes_stay_ordered(self):
        t=scaffold();add(t,2,'link',[('id','x'),('rel','canonical'),('href','../product'),('data-x','a&b')],resolved='https://example.test/product')
        add(t,1,'body');before=copy.deepcopy(t);v=m.inventory(t)['metadata'][0]
        self.assertEqual(v['raw_href'],'../product');self.assertEqual(v['resolved_href'],'https://example.test/product')
        self.assertEqual([a['name'] for a in v['attributes']],['id','rel','href','data-x'])
        self.assertEqual(v['position'],'head-direct');self.assertEqual(t,before)

    def test_auxiliary_and_custom_subtrees_never_hide_canonical(self):
        t=scaffold();add(t,1,'body');x=add(t,1,'div',[('id','codex-agent-overlay-root')]);c=add(t,x,'x-custom')
        add(t,c,'link',[('rel','canonical'),('href','https://example.test/bad')])
        v=m.inventory(t)['metadata'];self.assertEqual(len(v),1);self.assertEqual(v[0]['position'],'outside-head-body')

    def test_foreign_names_are_not_html_metadata(self):
        t=scaffold();add(t,1,'body');s=add(t,3,'svg',namespace='http://www.w3.org/2000/svg')
        add(t,s,'link',[('rel','canonical'),('href','x')],namespace='http://www.w3.org/2000/svg')
        self.assertEqual(m.inventory(t)['metadata'],[])

    def test_shadow_open_has_own_path_and_closed_exposure_remains_unknown(self):
        t=scaffold();add(t,1,'body');host=add(t,3,'div',shadow='open')
        root=add(t,host,'#document-fragment',type_=11,edge='shadow')
        add(t,root,'link',[('rel','canonical'),('href','https://example.test/shadow')])
        v=m.inventory(t)['metadata'][0];self.assertEqual(v['position'],'open-shadow');self.assertIn('shadow:0',v['path'])
        bad=copy.deepcopy(t);bad['closed_shadow_coverage']='absent'
        with self.assertRaisesRegex(ValueError,'coverage'):m.inventory(bad)

    def test_frames_templates_noscript_are_not_reparsed(self):
        t=scaffold();add(t,1,'body');add(t,3,'iframe',[('srcdoc','<link rel=canonical href=x>')])
        add(t,3,'template');n=add(t,3,'noscript');add(t,n,'#text',type_=3,data='<meta name=robots content=noindex>')
        v=m.inventory(t);self.assertFalse(v['metadata']);self.assertEqual(len(v['boundaries']),2)

    def test_fake_head_in_body_does_not_become_document_head(self):
        t=scaffold();body=add(t,1,'body');h=add(t,body,'head');add(t,h,'meta',[('name','robots'),('content','noindex')])
        self.assertEqual(m.inventory(t)['metadata'][0]['position'],'body')

    def test_duplicate_and_conflicting_metadata_remain_in_order(self):
        t=scaffold()
        for href in ('https://example.test/a','https://example.test/a','https://example.test/b'):
            add(t,2,'link',[('rel','canonical'),('href',href)])
        for content in ('index','noindex'):add(t,2,'meta',[('name','googlebot'),('content',content)])
        add(t,1,'body');v=m.inventory(t)['metadata']
        self.assertEqual(len(v),5);self.assertEqual([x['content'] for x in v[-2:]],['index','noindex'])

    def test_bad_parent_duplicate_id_duplicate_attribute_and_missing_child_refused(self):
        t=scaffold();add(t,2,'link',[('rel','canonical')]);add(t,1,'body')
        variants=[]
        for field,value in [('parent',99),('id',1),('index',7)]:
            b=copy.deepcopy(t);b['nodes'][3][field]=value;variants.append(b)
        b=copy.deepcopy(t);b['nodes'][3]['attributes']*=2;variants.append(b)
        b=copy.deepcopy(t);b['nodes'][2]['child_count']+=1;variants.append(b)
        for bad in variants:
            with self.assertRaises(ValueError):m.inventory(bad)

    def test_partial_traversal_preserves_prefix_but_declares_gap(self):
        t=scaffold();add(t,2,'link',[('rel','canonical')]);t['nodes'][2]['child_count']=10
        t['traversal_complete']=False;t['stop_reason']='node-limit'
        v=m.inventory(t);self.assertFalse(v['traversal_complete']);self.assertEqual(len(v['metadata']),1)
        t['traversal_complete']=True;t['stop_reason']=None
        with self.assertRaisesRegex(ValueError,'children'):m.inventory(t)

    def test_bound_and_unplanned_coverage_claims_are_rejected(self):
        t=scaffold();add(t,1,'body')
        for key,value in [('limits',{}),('frame_documents','collected'),('traversal_complete',1),('api_errors',['error'])]:
            bad=copy.deepcopy(t);bad[key]=value
            with self.assertRaises(ValueError):m.inventory(bad)
        bad=copy.deepcopy(t);bad['serialization']['html']='x'*(m.LIMITS['serialization_utf8_bytes']+1)
        with self.assertRaises(ValueError):m.inventory(bad)

    def test_no_normative_fields_or_evaluator_imports_or_network(self):
        t=scaffold();add(t,1,'body')
        with patch.object(socket,'socket',side_effect=AssertionError('No network')):
            result=m.inventory(t)
        self.assertTrue({'outcome','status','decision','rules','atomic_results'}.isdisjoint(result))
        code='import sys;sys.path.insert(0,'+repr(str(m.ROOT))+');import experiments.rendered_metadata;assert "conformance.evaluate" not in sys.modules'
        self.assertEqual(subprocess.run([sys.executable,'-I','-c',code],capture_output=True).returncode,0)

    def test_changed_script_cannot_be_compared(self):
        t=scaffold();add(t,1,'body');a={'script_sha256':m.script_digest(),'tree':t}
        b=copy.deepcopy(a);b['script_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'script'):m.compare(a,b)
        self.assertEqual(m.compare(a,a)['causal_attribution'],'not-established')

    def test_frozen_recipes_cover_browser_design_cases_and_keep_two_bridge_cases(self):
        recipe=m.recipes();plan=json.loads((m.ROOT/'tests/fixtures/rendered-metadata-plan-v2.json').read_text())
        ids={c['id'] for c in recipe['cases']}
        self.assertEqual(ids,{c['id'] for c in plan['cases']}-{'broken-path','same-script'}|{'js-canonical','corrected'})
        self.assertEqual(len(ids),24)

    def test_cli_refuses_existing_output_without_changing_original(self):
        t=scaffold();add(t,1,'body')
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder);(p/'capture.json').write_text(json.dumps({'script_sha256':m.script_digest(),'tree':t}))
            command=[sys.executable,'-I',str(m.ROOT/'experiments/rendered_metadata.py'),str(p/'capture.json'),'--output',str(p/'result.json')]
            self.assertEqual(subprocess.run(command,capture_output=True).returncode,0)
            before=(p/'result.json').read_bytes()
            self.assertEqual(subprocess.run(command,capture_output=True).returncode,64)
            self.assertEqual((p/'result.json').read_bytes(),before)


if __name__=='__main__':unittest.main()
