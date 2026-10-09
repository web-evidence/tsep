"""Counterexamples for source-text identity and explicitly scoped conformance. Apache-2.0."""
import copy
import json
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import tsep
from adapters.captures import build
from conformance.evaluate import evaluate, identity_text
from conformance.run import compare, run

CORPUS = tsep.read_json(ROOT/'conformance/cases.json')
CASES = {c['id']:c for c in CORPUS['cases']}
SELECTED = ['TS01-A01', 'TS01-A02']


class Draft7(unittest.TestCase):
    def test_soft404_and_inert_markers_cannot_pass_adapter_gate(self):
        expected = [('identity-soft404-forbidden-only','NT'),
                    ('identity-soft404-required-missing','NC'),
                    ('identity-only-forbidden-present','NC'),
                    ('identity-required-only-comment','NC'),
                    ('identity-required-only-script','NC'),
                    ('identity-required-only-style','NC'),
                    ('identity-timestamp-markers','C')]
        for name,status in expected:
            with self.subTest(case=name), tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp);source=root/'input.json';source.write_text(json.dumps(CASES[name]['input']))
                summary=build(source,root/'bundle',assessor='Synthetic',label=name,
                              selection_method='Synthetic counterexample',access='synthetic',mode='automatic')
                report=tsep.read_json(root/'bundle/report.json')
                self.assertEqual(report['results'][0]['status'],status)
                self.assertEqual(summary['decision'],'GO_WITH_RESERVATIONS' if status=='C' else 'NO_GO')
                self.assertEqual(summary['blocking_causes'],[] if status=='C' else [{'control_id':'TS01','status':status}])
                self.assertEqual(compare(CASES[name]['expected'],report['results'][0]['atomic_results'])[1],[])

    def test_extraction_excludes_inert_content_and_preserves_text_boundaries(self):
        headers={'content-type':['Text/HTML; CHARSET=UTF-8']}
        source='<html><head><title>Title</title><script>Required</script><style>Required</style></head><body>Left<!-- Required -->right<p title="Required">A &amp; B &#233;</p><br/>tail</body></html>'
        self.assertEqual(identity_text(headers,source),['Title','Left','right','A & B é','tail'])
        self.assertEqual(identity_text({'content-type':['text/plain; charset=utf-8']},source),[source])
        for broken in ('<html><body><script/>Required</body></html>',
                       '<html><body>Required', '<html><body><![CDATA[Required]]></body></html>'):
            with self.subTest(source=broken), self.assertRaises(ValueError):identity_text(headers,broken)

    def test_matching_body_and_stability_precede_markers(self):
        data=copy.deepcopy(CASES['identity-identical-stable']['input'])
        data['targets'][0]['intent']['required_markers']=['absent marker']
        self.assertEqual(evaluate(data)[1]['outcome'],'pass')
        data=copy.deepcopy(CASES['identity-stable-overrides-markers']['input'])
        self.assertEqual(evaluate(data)[1]['outcome'],'fail')

    def test_scoped_reference_reports_exact_denominators_and_omissions(self):
        before=copy.deepcopy(CORPUS);result=run(CORPUS,rules=SELECTED[::-1])
        self.assertEqual(CORPUS,before);self.assertTrue(result['success'])
        self.assertEqual(result['rules'],SELECTED)
        self.assertEqual(result['claim'],'passes TSEP '+CORPUS['protocol_version']+' conformance for TS01-A01, TS01-A02')
        pairs=sum(r['rule_id'] in SELECTED for c in CORPUS['cases'] for r in c['expected'])
        self.assertEqual(result['rule_target_pairs'],pairs)
        self.assertEqual(result['agreements']+result['coverage']['reduced_pairs'],pairs)
        self.assertEqual(result['cases']+result['skipped_cases'],len(CORPUS['cases']))
        self.assertEqual(result['total_rule_target_pairs']-pairs,result['omitted_rule_target_pairs'])
        self.assertEqual(set(result['coverage']['by_rule']),set(SELECTED))
        self.assertEqual(sum(v['conclusive_expected'] for v in result['coverage']['by_rule'].values()),result['coverage']['conclusive_expected'])
        self.assertEqual(len(result['omitted_rules']),7)

    def test_selection_does_not_hide_corrupt_corpus(self):
        for mutation in ('empty','invalid','duplicate'):
            rules={'empty':[],'invalid':['TS99-A01'],'duplicate':['TS01-A01','TS01-A01']}[mutation]
            with self.subTest(mutation=mutation),self.assertRaises(tsep.Invalid):run(CORPUS,rules=rules)
        corrupt=copy.deepcopy(CORPUS)
        case=next(c for c in corrupt['cases'] if c['input']['rules']==['TS07-A03'])
        case['expected']=[]
        with self.assertRaises(tsep.Invalid):run(corrupt,rules=SELECTED)

    def test_extra_missing_and_foreign_pairs_are_not_filtered_from_actual(self):
        def wrong(data):
            rows=evaluate(data)
            return rows+[dict(rows[0],rule_id='TS07-A01')]
        with patch('conformance.run.evaluate',side_effect=wrong):
            result=run(CORPUS,rules=SELECTED)
            self.assertFalse(result['success']);self.assertIsNone(result['claim'])
        for mutation in ('missing','foreign','duplicate'):
            def changed(data):
                rows=evaluate(data)
                if mutation=='missing':return rows[1:]
                if mutation=='foreign':return rows+[dict(rows[0],target='https://example.com/foreign')]
                return rows+[rows[0]]
            with self.subTest(mutation=mutation),patch('conformance.run.evaluate',side_effect=changed):
                if mutation=='duplicate':
                    with self.assertRaises(tsep.Invalid):run(CORPUS,rules=SELECTED)
                else:self.assertFalse(run(CORPUS,rules=SELECTED)['success'])

    def test_ts01_external_adapter_passes_only_declared_subset_and_wrong_results_fail(self):
        with tempfile.TemporaryDirectory() as folder:
            adapter=Path(folder)/'partial.py'
            adapter.write_text('import json,sys\n'
                'sys.path.insert(0,'+repr(str(ROOT))+')\n'
                'from conformance.evaluate import evaluate\n'
                'data=json.load(sys.stdin)\n'
                'assert set(data)=={"input_version","rules","targets"}\n'
                'rows=[]\n'
                'for target in data["targets"]:\n'
                ' for rule in data["rules"]:\n'
                '  if rule.startswith("TS01-"):\n'
                '   row=evaluate(dict(data,targets=[target],rules=[rule]))[0]\n'
                '   if "--wrong" in sys.argv: row["outcome"]="fail"\n'
                '  else: row={"rule_id":rule,"target":target["url"],"outcome":"inconclusive","reason":"Not implemented"}\n'
                '  rows.append(row)\n'
                'print(json.dumps(rows))\n')
            command=shlex.join([sys.executable,str(adapter)])
            for scoped,wrong,code in [(True,False,0),(False,False,1),(True,True,1),(False,True,1)]:
                with self.subTest(scoped=scoped,wrong=wrong):
                    args=[sys.executable,str(ROOT/'conformance/run.py'),'--command',command+(' --wrong' if wrong else '')]
                    if scoped:args+=['--rules',','.join(SELECTED)]
                    result=subprocess.run(args,capture_output=True,text=True,timeout=90)
                    self.assertEqual(result.returncode,code,result.stdout+result.stderr)
                    summary=json.loads(result.stdout)
                    self.assertEqual(summary['rules'],SELECTED if scoped else summary['available_rules'])
                    if wrong:self.assertGreater(summary['coverage']['by_rule']['TS01-A01']['disagreements'],0)

    def test_cli_invalid_rule_selections_fail_before_execution(self):
        for value in ('','TS01','TS99-A01','TS01-A01,TS01-A01','TS01-A01,'):
            result=subprocess.run([sys.executable,str(ROOT/'conformance/run.py'),'--rules',value],capture_output=True,text=True)
            self.assertEqual(result.returncode,64,result.stdout+result.stderr)


if __name__=='__main__':unittest.main()
