"""Offline capture-to-bundle workflow, truth preservation and delivery safety. Apache-2.0."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import tsep
from adapters.captures import build, NAME, VERSION
from conformance.evaluate import evaluate

CASES = {c['id']:c for c in tsep.read_json(ROOT/'conformance/cases.json')['cases']}


class CaptureAdapter(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory();self.root = Path(self.temp.name)
        self.input = self.root/'supplied.json'
        self.output = self.root/'bundle'
        self.options = dict(assessor='Synthetic reviewer',label='Synthetic captures',
                            selection_method='Declared synthetic cases only',access='synthetic')

    def tearDown(self):self.temp.cleanup()

    def data(self, name='identity-timestamp-markers'):
        return copy.deepcopy(CASES[name]['input'])

    def emit(self, data=None, **options):
        self.input.write_text(json.dumps(data or self.data(),ensure_ascii=False,indent=3)+'\n',encoding='utf-8')
        return build(self.input,self.output,**dict(self.options,**options))

    def test_all_raw_cases_retain_computed_outcomes_and_evidence(self):
        # End-to-end integrity across every existing raw scenario, including parser limits.
        # Expected verdicts are never supplied to this adapter.
        for name,case in CASES.items():
            with self.subTest(case=name):
                summary=self.emit(case['input'])
                report=tsep.read_json(self.output/'report.json')
                self.assertEqual(summary,tsep.validate(report,self.output))
                actual=[a for r in report['results'] for a in r.get('atomic_results',[])]
                self.assertEqual(sorted((a['rule_id'],a['target'],a['outcome']) for a in actual),
                                 sorted((a['rule_id'],a['target'],a['outcome']) for a in evaluate(case['input'])))
                self.assertEqual((self.output/'input.json').read_bytes(),self.input.read_bytes())
                self.assertTrue(summary['synthetic_evidence'])
                self.assertLessEqual(summary['selected_controls'],3)
                shutil.rmtree(self.output)

    def test_identity_unknown_failure_and_success_do_not_change_gate_policy(self):
        for name,status,gate in [('identity-timestamp-no-markers','NT','NO_GO'),
                ('identity-timestamp-markers','C','GO_WITH_RESERVATIONS'),
                ('identity-forbidden-marker','NC','NO_GO'),('identity-stable-changed','NC','NO_GO')]:
            with self.subTest(case=name):
                result=self.emit(self.data(name),mode='automatic')
                self.assertEqual(result['counts'][status],1);self.assertEqual(result['decision'],gate)
                report=tsep.read_json(self.output/'report.json')
                self.assertEqual(report['assessor']['tool'],{'name':NAME,'version':VERSION})
                shutil.rmtree(self.output)

    def test_omitted_rules_are_not_invented_or_promoted_to_c(self):
        data=self.data('complete-reference');data['rules']=['TS07-A01','TS07-A02']
        result=self.emit(data,mode='semiAuto')
        report=tsep.read_json(self.output/'report.json');metadata=tsep.read_json(self.output/'import.json')
        self.assertEqual(result['counts']['NT'],1);self.assertEqual(result['decision'],'NO_GO')
        self.assertEqual(len(report['results'][0]['atomic_results']),2)
        self.assertEqual(metadata['coverage']['TS07']['omitted_rules'],['TS07-A03'])
        self.assertEqual(len([a for a in tsep.read_json(self.output/'earl.jsonld')['@graph'] if 'dct:isPartOf' in a]),2)
        self.assertFalse(any(a['kind']=='render' for a in report['artifacts']))

    def test_observed_failure_survives_omitted_rules_and_unstarted_controls(self):
        data=self.data('identity-forbidden-marker');data['rules']=['TS01-A02']
        result=self.emit(data,selected=['TS01','TS02'])
        report=tsep.read_json(self.output/'report.json')
        self.assertEqual([r['status'] for r in report['results']],['NC','NT'])
        self.assertEqual(report['results'][1]['evaluation_state'],'not-started')
        self.assertEqual(report['results'][1]['evidence_ids'],[])
        self.assertEqual(result['decision'],'NO_GO')

    def test_manual_canonical_and_semi_auto_rendered_reports(self):
        for name,mode,status in [('canonical-all-signals-agree','manual','C'),
                                 ('render-all-states-compatible','semiAuto','C'),
                                 ('render-required-state-missing','semiAuto','NT'),
                                 ('canonical-content-review-missing','manual','NT')]:
            with self.subTest(case=name):
                self.assertEqual(self.emit(self.data(name),mode=mode)['counts'][status],1)
                shutil.rmtree(self.output)
        for name in ('canonical-all-signals-agree','render-all-states-compatible'):
            with self.subTest(case=name),self.assertRaises(tsep.Invalid):self.emit(self.data(name),mode='automatic')
            self.assertFalse(self.output.exists())

    def test_missing_source_and_positive_exemptions_keep_their_meaning(self):
        data=self.data();data['targets'][0].pop('http')
        self.assertEqual(self.emit(data)['counts']['NT'],1)
        report=tsep.read_json(self.output/'report.json')
        self.assertFalse(any(a['kind'] in ('http','html') for a in report['artifacts']))
        shutil.rmtree(self.output)
        self.assertEqual(self.emit(self.data('canonical-sitemap-positive-absence'))['counts']['C'],1)
        atom=next(a for a in tsep.read_json(self.output/'assessment.json') if a['rule_id']=='TS10-A03')
        self.assertEqual(atom['outcome'],'not-applicable')

    def test_invalid_dates_remain_unknown_and_import_dates_are_explicit(self):
        self.assertEqual(self.emit(self.data('render-invalid-date'))['counts']['NT'],1)
        render=tsep.read_json(self.output/'evidence/target-1-render.json')
        self.assertIn('import-time-only',render['date_basis'])
        self.assertIn('not-a-date',json.dumps(render))
        report=tsep.read_json(self.output/'report.json')
        artifact=next(a for a in report['artifacts'] if a['kind']=='render')
        self.assertEqual(artifact['observed_at'],report['issued_at'])
        shutil.rmtree(self.output)
        data=self.data();data['targets'][0].pop('observed_at')
        self.assertEqual(self.emit(data)['counts']['NT'],1)

    def test_future_dates_cannot_manufacture_prospective_pass(self):
        for where in ('target','review'):
            data=self.data('render-all-states-compatible')
            if where=='target': data['targets'][0]['observed_at']='2999-01-01T00:00:00Z'
            else:data['targets'][0]['access_review']['observed_at']='2999-01-01T00:00:00Z'
            with self.subTest(where=where),self.assertRaisesRegex(tsep.Invalid,'future'):self.emit(data)
            self.assertFalse(self.output.exists())

    def test_original_bytes_crlf_and_per_target_proofs_are_preserved(self):
        data=self.data('two-targets-must-stay-distinct')
        self.emit(data)
        self.assertEqual((self.output/'input.json').read_bytes(),self.input.read_bytes())
        report=tsep.read_json(self.output/'report.json')
        for index,target in enumerate(data['targets'],1):
            payload=tsep.read_json(self.output/('evidence/target-'+str(index)+'-http.json'))
            self.assertEqual(payload['record']['http'],target['http'])
        artifacts={a['id']:a for a in report['artifacts']}
        for r in report['results']:
            for atom in r['atomic_results']:
                for ref in atom['evidence_ids']:
                    self.assertIn(atom['target'],artifacts[ref]['targets'])
                    if ref.startswith('target-'):self.assertEqual(artifacts[ref]['targets'],[atom['target']])
        artifact=next(a for a in report['artifacts'] if a['kind']=='http')
        (self.output/artifact['path']).write_text('tampered')
        with self.assertRaises(tsep.Invalid):tsep.validate(report,self.output)

    def test_manifest_covers_every_delivered_file_and_bundle_is_portable(self):
        self.emit()
        manifest={name:digest for digest,name in (line.split('  ',1) for line in (self.output/'SHA256SUMS').read_text().splitlines())}
        self.assertEqual(set(manifest),{p.relative_to(self.output).as_posix() for p in self.output.rglob('*') if p.is_file()}-{'SHA256SUMS'})
        for name,digest in manifest.items():self.assertEqual(tsep.digest(self.output/name),digest)
        self.assertEqual(tsep.read_json(self.output/'earl.jsonld'),tsep.earl(tsep.read_json(self.output/'report.json'),tsep.read_json(self.output/'gate.json')))
        destination=self.root/'moved';shutil.copytree(self.output,destination);shutil.rmtree(self.output);self.input.unlink()
        self.assertEqual(tsep.validate(tsep.read_json(destination/'report.json'),destination)['counts']['C'],1)

    def test_existing_files_directories_and_symlinks_are_never_overwritten(self):
        self.emit();before={p.relative_to(self.output):p.read_bytes() for p in self.output.rglob('*') if p.is_file()}
        with self.assertRaisesRegex(tsep.Invalid,'already exists'):self.emit()
        self.assertEqual(before,{p.relative_to(self.output):p.read_bytes() for p in self.output.rglob('*') if p.is_file()})
        shutil.rmtree(self.output);self.output.symlink_to(self.root/'missing',target_is_directory=True)
        with self.assertRaises(tsep.Invalid):self.emit()
        self.assertTrue(self.output.is_symlink());self.assertFalse((self.root/'missing').exists())
        self.output.unlink();self.output.write_text('keep')
        with self.assertRaises(tsep.Invalid):self.emit()
        self.assertEqual(self.output.read_text(),'keep')

    def test_write_failure_leaves_no_delivered_partial_bundle(self):
        write=Path.open
        def fail(path,*args,**kwargs):
            if path.parent==self.output.resolve() and path.name=='report.json':raise OSError('Simulated disk failure')
            return write(path,*args,**kwargs)
        with patch.object(Path,'open',fail),self.assertRaisesRegex(OSError,'Simulated'):self.emit()
        self.assertFalse(self.output.exists());self.assertEqual(list(self.root.glob('.tsep-capture-*')),[])

    def test_no_conformance_expectations_unknown_rules_or_hidden_parent(self):
        for mutation in ('expected','unsupported','duplicate','foreign-parent'):
            data=self.data();options={}
            if mutation=='expected':data['expected']=[{'outcome':'pass'}]
            if mutation=='unsupported':data['rules']=['TS99-A01']
            if mutation=='duplicate':data['targets'].append(copy.deepcopy(data['targets'][0]))
            if mutation=='foreign-parent':options['selected']=['TS07']
            with self.subTest(mutation=mutation),self.assertRaises(tsep.Invalid):self.emit(data,**options)
            self.assertFalse(self.output.exists())

    def test_adapter_never_requests_network(self):
        with patch('socket.create_connection',side_effect=AssertionError('Network forbidden')):
            self.assertEqual(self.emit()['decision'],'GO_WITH_RESERVATIONS')

    def test_cli_conversion_success_is_separate_from_no_go_exit(self):
        self.input.write_text(json.dumps(self.data('identity-timestamp-no-markers')))
        args=[sys.executable,str(ROOT/'adapters/captures.py'),str(self.input),'--output-dir',str(self.output),
              '--assessor','Synthetic','--label','Synthetic','--selection-method','Synthetic','--access','synthetic','--json']
        result=subprocess.run(args,capture_output=True,text=True,timeout=15)
        self.assertEqual(result.returncode,0,result.stderr);self.assertEqual(json.loads(result.stdout)['decision'],'NO_GO')
        gate=subprocess.run([sys.executable,str(ROOT/'tsep.py'),'gate',str(self.output/'report.json')],capture_output=True)
        self.assertEqual(gate.returncode,1)
        self.assertEqual(subprocess.run(args,capture_output=True).returncode,64)


if __name__=='__main__':unittest.main()
