"""Identity, normative expectations, coverage and media-type regression tests. Apache-2.0."""
import copy
import json
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import tsep
from conformance.evaluate import evaluate, media_type
from conformance.run import compare, run

CORPUS = tsep.read_json(ROOT/'conformance/cases.json')
CASES = {c['id']: c for c in CORPUS['cases']}


def identity_report(data, root):
    targets = [t['url'] for t in data['targets']]
    report = tsep.initialize(targets, ['TS01'], 'custom', 'Synthetic test', 'Synthetic identity cases',
                             'Declared synthetic inputs', 'automatic', {'name': 'TSEP bounded interpreter', 'version': CORPUS['protocol_version']})
    for kind in ('http', 'intent'):
        path = root/(kind+'.json')
        path.write_text(json.dumps([t[kind] for t in data['targets']]), encoding='utf-8')
        report['artifacts'].append({'id': kind, 'path': path.name, 'sha256': tsep.digest(path),
            'kind': kind, 'targets': targets, 'observed_at': '2026-10-09T10:00:01Z',
            'access': 'synthetic', 'description': 'Authored raw input; not a live observation'})
    atoms = [dict(r, evidence_ids=['http', 'intent']) for r in evaluate(data)]
    outcomes = [r['outcome'] for r in atoms]
    status = 'NC' if 'fail' in outcomes else 'NT' if 'inconclusive' in outcomes else 'C'
    report['results'][0].update(status=status, evaluation_state='inconclusive' if status=='NT' else 'complete',
        reason='Computed identity outcomes', procedure='Compare prior intent with retained complete bodies',
        evaluated_targets=targets, evidence_ids=['http', 'intent'], atomic_results=atoms)
    return report


class Draft6(unittest.TestCase):
    def test_identity_raw_outcomes_control_status_and_gate(self):
        for name, status in [('identity-timestamp-no-markers','NT'), ('identity-timestamp-markers','C'),
                             ('identity-forbidden-marker','NC'), ('identity-stable-changed','NC')]:
            with self.subTest(case=name), tempfile.TemporaryDirectory() as folder:
                report = identity_report(CASES[name]['input'], Path(folder))
                summary = tsep.validate(report, Path(folder))
                self.assertEqual(report['results'][0]['status'], status)
                self.assertEqual(summary['decision'], 'GO_WITH_RESERVATIONS' if status=='C' else 'NO_GO')
                self.assertEqual(summary['selected_controls'], 1)
                self.assertEqual(summary['blocking_causes'], [] if status=='C' else [{'control_id':'TS01','status':status}])
                for lang in ('fr', 'en'):
                    if status!='C': self.assertIn('TS01 ('+status+')', tsep.readable_summary(summary, lang))
                if status=='NT':
                    report['results'][0].update(status='C', evaluation_state='complete')
                    with self.assertRaises(tsep.Invalid): tsep.validate(report, Path(folder))

    def test_identity_precedence_and_invalid_intent_cases(self):
        for name, case in CASES.items():
            if name.startswith('identity-'):
                with self.subTest(case=name):
                    self.assertEqual([r['outcome'] for r in evaluate(case['input'])], [r['outcome'] for r in case['expected']])

    def test_partial_identity_cannot_pass_control(self):
        data = copy.deepcopy(CASES['identity-timestamp-markers']['input']);data['rules']=['TS01-A02']
        with tempfile.TemporaryDirectory() as folder, self.assertRaises(tsep.Invalid):
            tsep.validate(identity_report(data, Path(folder)), Path(folder))

    def test_changed_target_does_not_share_identity_verdict(self):
        data = copy.deepcopy(CASES['identity-timestamp-markers']['input'])
        second = copy.deepcopy(data['targets'][0]);second['url']='https://example.com/other'
        second['http'][0].update(url=second['url'], request=second['http'][0]['request'].replace('/page ', '/other '))
        data['targets'].append(second)
        outcomes = [r['outcome'] for r in evaluate(data) if r['rule_id']=='TS01-A02']
        self.assertEqual(outcomes, ['pass','fail'])

    def test_reference_limit_is_coverage_not_agreement(self):
        rows = CASES['unsupported-robots-wildcard']['expected']
        actual = evaluate(CASES['unsupported-robots-wildcard']['input'])
        agreed, differences, reduced = compare(rows, actual)
        self.assertEqual((len(agreed),len(differences),len(reduced)), (3,0,1))
        actual[-1]['outcome']='pass'
        self.assertEqual(tuple(map(len,compare(rows,actual))), (4,0,0))
        for wrong in ('fail','not-applicable'):
            actual[-1]['outcome']=wrong
            self.assertEqual(tuple(map(len,compare(rows,actual))), (3,1,0))
        actual[-1]['outcome']='inconclusive';actual[0]['outcome']='inconclusive'
        self.assertEqual(tuple(map(len,compare(rows,actual))), (2,1,1))

    def test_reference_limit_does_not_allow_omission_extra_or_duplicate(self):
        rows = CASES['unsupported-robots-wildcard']['expected'];actual = evaluate(CASES['unsupported-robots-wildcard']['input'])
        self.assertEqual(len(compare(rows, actual[:-1])[1]),1)
        self.assertEqual(len(compare(rows, actual+[dict(actual[0],target='https://example.com/foreign')])[1]),1)
        with self.assertRaises(tsep.Invalid): compare(rows, actual+[actual[0]])

    def test_normative_unknown_cannot_be_promoted_by_reference_limit(self):
        rows = CASES['embedding-context-unsupported']['expected'];actual = evaluate(CASES['embedding-context-unsupported']['input'])
        actual[2]['outcome']='pass'
        self.assertEqual(len(compare(rows,actual)[1]),1)

    def test_reference_coverage_counts_are_honest(self):
        result = run(CORPUS)
        self.assertTrue(result['success']);self.assertEqual(result['disagreements'],0)
        self.assertEqual(result['agreements']+result['coverage']['reduced_pairs'], result['rule_target_pairs'])
        self.assertGreater(result['coverage']['reduced_pairs'],0)
        self.assertLess(result['coverage']['percent'],100)
        self.assertEqual(sum(r['reduced_coverage'] for r in result['coverage']['by_rule'].values()), result['coverage']['reduced_pairs'])

    def test_content_type_variants_and_unsupported_encodings(self):
        for name, case in CASES.items():
            if name.startswith('media-'):
                with self.subTest(case=name):
                    self.assertEqual([r['outcome'] for r in evaluate(case['input'])], [r['outcome'] for r in case['expected']])

    def test_media_parser_preserves_other_parameter_values_and_rejects_ambiguity(self):
        self.assertEqual(media_type({'content-type':['Text/HTML; CHARSET="UtF-8"; profile="CaseSensitive;value"']}),
                         ('text/html',{'charset':'utf-8','profile':'CaseSensitive;value'}))
        for value in ([], ['text/html','text/html'], ['text/html; charset=utf-8; CHARSET=latin1'], ['text/html; charset="utf-8'], ['text/html garbage']):
            with self.subTest(value=value), self.assertRaises(ValueError):media_type({'content-type':value})

    def test_inline_record_short_receipts_json_and_atomic_safety(self):
        def cli(*args):
            return subprocess.run([sys.executable, str(ROOT/'tsep.py'), *map(str,args)],
                                  capture_output=True, text=True, encoding='utf-8', timeout=15)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder);path = root/'report.json'
            initial = cli('init','--target','https://example.com/page','--controls','TS01',
                          '--assessor','Synthetic','--label','CLI fixture','--selection-method','Synthetic only')
            self.assertEqual(initial.returncode,0,initial.stderr);path.write_text(initial.stdout)
            for kind in ('http','intent'):
                (root/(kind+'.txt')).write_bytes((ROOT/'examples/pass'/(kind+'.txt')).read_bytes())
                args = ['add-evidence',path,'--id',kind,'--path',kind+'.txt','--kind',kind,
                        '--target','https://example.com/page','--observed-at','2026-10-09T10:00:00Z',
                        '--access','synthetic','--description','Synthetic fixture']
                result = cli(*args, *(['--json'] if kind=='intent' else []))
                self.assertEqual(result.returncode,0,result.stderr)
                if kind=='intent': self.assertEqual(json.loads(result.stdout)['blocking_causes'],[{'control_id':'TS01','status':'NT'}])
                else:self.assertEqual(len(result.stdout.splitlines()),2)
            atoms = tsep.read_json(ROOT/'examples/pass/report.json')['results'][0]['atomic_results']
            args = ['record',path,'--control','TS01','--status','C','--reason','Synthetic passing findings',
                    '--procedure','Replay supplied judgments','--target','https://example.com/page',
                    '--evidence','http','--evidence','intent']
            inline = [arg for atom in atoms for arg in ('--atomic',json.dumps(atom))]
            result = cli(*args,*inline)
            self.assertEqual(result.returncode,0,result.stderr);self.assertEqual(len(result.stdout.splitlines()),2)
            gated = cli('gate',path,'--summary')
            self.assertEqual(gated.returncode,0,gated.stderr)
            self.assertIn('Targets: 1 | Selected controls: 1/44',gated.stdout)
            self.assertEqual(json.loads(cli(*args,*inline,'--json').stdout)['decision'],'GO_WITH_RESERVATIONS')
            before=path.read_bytes()
            for bad in ('{"rule_id":"TS01-A01","rule_id":"TS01-A02"}', 'NaN', 'null', '{'):
                rejected=cli(*args,'--atomic',bad)
                self.assertEqual(rejected.returncode,64,rejected.stderr)
                self.assertEqual(path.read_bytes(),before)
            self.assertEqual(cli(*args,*inline,'--atomic-results',root/'absent.json').returncode,2)
            self.assertEqual(path.read_bytes(),before)

    def test_earl_test_hierarchy_is_distinct_from_assertion_hierarchy(self):
        for name in ('identity-timestamp-markers','identity-timestamp-no-markers','identity-stable-changed'):
            with self.subTest(case=name), tempfile.TemporaryDirectory() as folder:
                report=identity_report(CASES[name]['input'],Path(folder))
                graph=tsep.earl(report,tsep.validate(report,Path(folder)))['@graph']
                parent=graph[2]
                self.assertEqual(parent['earl:test']['@type'],'earl:TestRequirement')
                for atom in graph[3:]:
                    self.assertEqual(atom['earl:test']['@type'],'earl:TestCase')
                    self.assertEqual(atom['earl:test']['dct:isPartOf']['@id'],parent['earl:test']['@id'])
                    self.assertEqual(atom['dct:isPartOf']['@id'],parent['@id'])


if __name__ == '__main__': unittest.main()
