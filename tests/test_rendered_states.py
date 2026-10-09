"""Raw DOM interpretation, provenance boundaries and whole-control truth; Apache-2.0."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import tsep
from conformance.evaluate import evaluate

CASES={c['id']:c for c in tsep.read_json(ROOT/'conformance/cases.json')['cases']}


def assessed_report(data, root):
    """Test adapter: use computed outcomes, never copy expected verdicts into reports."""
    targets=[t['url'] for t in data['targets']]
    report=tsep.initialize(targets,['TS07'],'custom','Synthetic review author','Synthetic TS07 cases',
                           'Declared synthetic contexts only',mode='semiAuto',
                           tool={'name':'TSEP bounded conformance interpreter','version':tsep.read_json(tsep.PROTOCOL_PATH)['version']})
    report['scope']['exclusions']=['All real sites, engine rendering, other controls and unlisted states']
    refs={}
    for number,target in enumerate(data['targets']):
        pieces={'intent':{'intent':target['intent'],'context':target['context'],
                          'exemption_review':target.get('exemption_review')},
                'http':target['http'], 'html':target['http'][-1]['response'].split('\r\n\r\n',1)[1]}
        for kind in ('robots','render'):
            if kind in target:pieces[kind]=target[kind]
        refs[target['url']]=[]
        for kind,piece in pieces.items():
            aid=kind+'-'+str(number);path=root/(aid+'.json')
            path.write_text(json.dumps(piece,ensure_ascii=False),encoding='utf-8')
            report['artifacts'].append({'id':aid,'path':path.name,'sha256':tsep.digest(path),'kind':kind,
                'targets':[target['url']],'observed_at':'2026-10-09T10:00:03Z','access':'synthetic',
                'description':'Authored raw source/DOM fixture; not a browser execution or engine observation'})
            refs[target['url']].append(aid)
    atoms=[dict(a,evidence_ids=refs[a['target']]) for a in evaluate(data)]
    outcomes=[a['outcome'] for a in atoms]
    status='NC' if 'fail' in outcomes else 'NT' if 'inconclusive' in outcomes else 'C'
    report['results'][0].update(status=status,evaluation_state='inconclusive' if status=='NT' else 'complete',
        reason='Computed source/DOM results, within declared synthetic scope',
        procedure='Compare supplied raw captures with the prior plan; no JavaScript executed',
        evaluated_targets=targets,evidence_ids=[a['id'] for a in report['artifacts']],atomic_results=atoms)
    return report


class RenderedStates(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)

    def tearDown(self):self.temp.cleanup()

    def data(self,name='render-all-states-compatible'):
        return copy.deepcopy(CASES[name]['input'])

    def test_computed_ts07_reports_retain_partial_and_adverse_outcomes(self):
        cases={'render-all-states-compatible':'C','render-required-state-missing':'NT',
               'render-script-added-noindex':'NC','render-initial-noindex-removed':'NC',
               'render-exemption-documented-stability':'C'}
        for name,status in cases.items():
            with self.subTest(case=name):
                report=assessed_report(self.data(name),self.root)
                summary=tsep.validate(report,self.root)
                self.assertEqual(report['results'][0]['status'],status)
                self.assertEqual(summary['selected_controls'],1)
                self.assertEqual(summary['protocol_controls'],44)
                self.assertTrue(summary['synthetic_evidence'])
                self.assertEqual(summary['decision'],'GO_WITH_RESERVATIONS' if status=='C' else 'NO_GO')

    def test_render_alone_cannot_pass_parent(self):
        data=self.data();data['rules']=['TS07-A03']
        report=assessed_report(data,self.root)
        with self.assertRaisesRegex(tsep.Invalid,'every atomic rule'):
            tsep.validate(report,self.root)

    def test_unknown_render_cannot_be_promoted_to_c(self):
        report=assessed_report(self.data('render-required-state-missing'),self.root)
        report['results'][0].update(status='C',evaluation_state='complete')
        with self.assertRaisesRegex(tsep.Invalid,'cannot yield C'):
            tsep.validate(report,self.root)

    def test_render_source_and_dom_proofs_required_per_atomic_pass(self):
        original=assessed_report(self.data(),self.root)
        for kind in ('http','html','render','intent'):
            report=copy.deepcopy(original)
            report['results'][0]['atomic_results'][2]['evidence_ids'].remove(kind+'-0')
            with self.subTest(kind=kind),self.assertRaisesRegex(tsep.Invalid,'Missing atomic input'):
                tsep.validate(report,self.root)

    def test_all_passing_ts07_remains_semi_auto(self):
        report=assessed_report(self.data(),self.root);report['assessor']['mode']='automatic'
        with self.assertRaisesRegex(tsep.Invalid,'every control rule'):
            tsep.validate(report,self.root)

    def test_missing_dom_does_not_mask_other_state_failure(self):
        result=evaluate(self.data('render-failure-preserved-with-missing-state'))[0]
        self.assertEqual(result['outcome'],'fail')
        self.assertIn('Missing or duplicate capture',result['reason'])

    def test_unrelated_dom_failure_cannot_be_attributed(self):
        result=evaluate(self.data('render-unrelated-failure-not-attributed'))[0]
        self.assertEqual(result['outcome'],'inconclusive')

    def test_malformed_render_records_are_inconclusive(self):
        for field,value in [('render',None),('render',{'browser':None}),
                            ('render',{'browser':{'name':'Synthetic','version':'1'},'states':None})]:
            data=self.data();data['rules']=['TS07-A03'];data['targets'][0][field]=value
            with self.subTest(value=value):self.assertEqual(evaluate(data)[0]['outcome'],'inconclusive')

    def test_exemption_cannot_be_inferred_from_no_scripts(self):
        data=self.data();data['rules']=['TS07-A03'];target=data['targets'][0]
        target.pop('render');target['intent']['rendering']={'mode':'exempt','basis':'reviewed-stable','reason':'No JS'}
        self.assertEqual(evaluate(data)[0]['outcome'],'inconclusive')

    def test_dom_mutation_changes_computed_outcome(self):
        data=self.data();data['rules']=['TS07-A03']
        self.assertEqual(evaluate(data)[0]['outcome'],'pass')
        state=data['targets'][0]['render']['states'][1]
        state['dom']=state['dom'].replace('<title>','<meta name="robots" content="noindex"><title>')
        self.assertEqual(evaluate(data)[0]['outcome'],'fail')

    def test_render_atomic_earl_preserves_unknown_and_parent_nc(self):
        report=assessed_report(self.data('render-initial-noindex-removed'),self.root)
        graph=tsep.earl(report,tsep.validate(report,self.root))['@graph']
        self.assertEqual(graph[2]['earl:result']['earl:outcome']['@id'],'earl:failed')
        atom=next(a for a in graph if a.get('earl:test',{}).get('@id','').endswith(':TS07-A03'))
        self.assertEqual(atom['earl:result']['earl:outcome']['@id'],'earl:cantTell')
        self.assertEqual(atom['dct:isPartOf']['@id'],graph[2]['@id'])


if __name__=='__main__':unittest.main()
