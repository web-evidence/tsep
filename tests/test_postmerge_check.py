"""Adversarial identity/receipt cases for post-merge reuse, without network."""
import copy
import datetime
import io
import json
import os
import sys
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch, Mock
import urllib.error

from scripts import postmerge_check as check
from scripts import ci_qualify

MERGE, BASE, HEAD, TESTED, TREE = [c*40 for c in 'abcde']
NOW = datetime.datetime(2026, 10, 24, 16, tzinfo=datetime.timezone.utc)
REPO = 'example/tsep'


def fixture():
    ids, rules = ['case_one', 'case_two'], ['TS01-A01']
    inventory = {'format_version':1, 'tests':2, 'test_ids_sha256':check.identity_hash(ids),
                 'http_cases':1, 'http_case_ids_sha256':'http', 'conformance_case_ids_sha256':'cases',
                 'conformance_input_sha256':'inputs', 'conformance':{'cases':1, 'rule_target_pairs':1,
                 'disagreements':0, 'rules':1, 'rule_ids_sha256':check.identity_hash(rules), 'reduced_pairs':0}}
    expected = {'archive_sha256':'archive', 'source_inventory_sha256':'sources', 'source_files':1,
                'workflow_sha256':'workflow', 'qualification_inventory':inventory}
    suite = {'success':True, 'inventory_complete':True, 'expected':ids, 'completed':ids,
             'tests_run':2, 'skipped':[], 'errors':0, 'failures':0, 'unexpected_successes':0, 'expected_failures':0}
    conformance = {'success':True, 'synthetic':True, 'cases':1, 'rule_target_pairs':1, 'disagreements':0,
                   'rules':rules, 'coverage':{'reduced_pairs':0}, 'skipped_cases':0, 'omitted_rule_target_pairs':0}
    receipt = {'success':True, 'full_qualification':True, 'verification_profile':check.PROFILE,
               'jobs':2, 'step_timeout_seconds':7200, 'runtime':{'version':check.NODE}, 'python':'3.12.15',
               'archive_sha256':'archive', 'rebuild_sha256':'archive', 'source_inventory_sha256':'sources',
               'source_files':1, 'changed_source_files':[], 'qualification_inventory':inventory,
               'http_cases':1, 'http_case_ids_sha256':'http', 'conformance_case_ids_sha256':'cases',
               'conformance_input_sha256':'inputs', 'test_suites':{'source':copy.deepcopy(suite),'archive':copy.deepcopy(suite)},
               'checks':[{'name':name,'exit':0,'stdout':json.dumps(conformance)} for name in sorted(check.CHECKS)],
               'ci_identity':{'checkout':TESTED,'tree':TREE,'parents':[BASE,HEAD],
                              'workflow_sha256':'workflow','event':'pull_request'}}
    return expected, receipt


def log(receipt, checkout=TESTED):
    return ('##[group]Run actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1\n'
            '[command]/usr/bin/git log -1 --format=%H\n'+checkout+'\n'
            '##[group]Run actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97\n'
            +json.dumps(receipt,indent=2)+'\n').encode()


class FakeAPI:
    def __init__(self):
        self.expected, self.receipt = fixture()
        self.run = {'id':10,'event':'pull_request','path':check.WORKFLOW,'workflow_id':20,'head_sha':HEAD,
                    'repository':{'full_name':REPO},'run_attempt':1,'status':'completed',
                    'conclusion':'success','updated_at':'2026-10-24T15:00:00Z'}
        self.jobs = [{'id':n,'name':name,'run_id':10,'status':'completed','conclusion':'success',
                      'steps':[{'name':step,'conclusion':'success'} for step in
                      ('Verify contract, evidence and reproducible distribution',
                       'Check that verification preserved the checkout')]} for n,name in enumerate(check.JOBS, 1)]
        self.data = {
            '/git/commits/'+MERGE:{'sha':MERGE,'tree':{'sha':TREE},'parents':[{'sha':BASE},{'sha':HEAD}]},
            '/git/commits/'+TESTED:{'sha':TESTED,'tree':{'sha':TREE},'parents':[{'sha':BASE},{'sha':HEAD}]},
            '/commits/main':{'sha':MERGE},
            '/commits/'+MERGE+'/pulls?per_page=100':[{'number':4,'merged_at':'today','merge_commit_sha':MERGE}],
            '/pulls/4':{'number':4,'merged':True,'merge_commit_sha':MERGE,'base':{'ref':'main','repo':{'full_name':REPO}},'head':{'sha':HEAD}},
            '/actions/workflows/verify.yml':{'id':20,'path':check.WORKFLOW},
            '/actions/runs?event=pull_request&head_sha='+HEAD+'&per_page=100':{'total_count':1,'workflow_runs':[self.run]},
            '/actions/runs/10':self.run,
            '/actions/runs/10/jobs?per_page=100':{'total_count':7,'jobs':self.jobs}}
        self.log_override = None
        self.calls = []

    def json(self, path):
        self.calls.append(path)
        return copy.deepcopy(self.data[path])

    def log(self, job):
        if self.log_override is not None:
            return self.log_override
        receipt = copy.deepcopy(self.receipt)
        name = next(j['name'] for j in self.jobs if j['id'] == job)
        receipt['python'] = check.JOBS[name]+'.99'
        return log(receipt)


class PostmergeCheck(unittest.TestCase):
    def evaluate(self, api=None, before=BASE):
        api = api or FakeAPI()
        return check.evaluate(api, REPO, MERGE, api.expected, NOW, before)

    def test_identical_tree_reuses_all_seven_actual_checkouts(self):
        result = self.evaluate()
        self.assertTrue(result['reuse'])
        self.assertFalse(result['new_tests_executed'])
        self.assertEqual(len(result['jobs']), 7)
        self.assertEqual({r['checkout'] for r in result['jobs']}, {TESTED})
        self.assertEqual(result['parents'], [BASE, HEAD])

    def test_tree_parent_main_and_pr_changes_require_full_verification(self):
        for path, field, value in [
            ('/git/commits/'+TESTED,'tree',{'sha':'f'*40}),
            ('/git/commits/'+TESTED,'parents',[{'sha':HEAD},{'sha':BASE}]),
            ('/git/commits/'+MERGE,'parents',[{'sha':BASE}]),
            ('/commits/main','sha','f'*40),('/pulls/4','head',{'sha':'f'*40}),
            ('/pulls/4','merged',False)]:
            with self.subTest(path=path,field=field):
                api=FakeAPI();api.data[path][field]=value
                with self.assertRaises(check.Unqualified): self.evaluate(api)
        with self.assertRaises(check.Unqualified): self.evaluate(before='f'*40)

    def test_incomplete_failed_retried_stale_and_foreign_runs_are_refused(self):
        for field,value in [('status','in_progress'),('conclusion','failure'),('run_attempt',2),
                            ('event','push'),('workflow_id',21),('head_sha','f'*40),
                            ('repository',{'full_name':'foreign/repo'}),
                            ('updated_at','2026-10-22T15:00:00Z'),('updated_at','2026-10-25T15:00:00Z')]:
            with self.subTest(field=field,value=value):
                api=FakeAPI();api.run[field]=value
                with self.assertRaises(check.Unqualified): self.evaluate(api)

    def test_ambiguous_run_or_merged_pr_is_refused(self):
        api=FakeAPI();api.data['/actions/runs?event=pull_request&head_sha='+HEAD+'&per_page=100']['workflow_runs'].append(copy.deepcopy(api.run))
        with self.assertRaises(check.Unqualified): self.evaluate(api)
        api=FakeAPI();api.data['/commits/'+MERGE+'/pulls?per_page=100'] *= 2
        with self.assertRaises(check.Unqualified): self.evaluate(api)

    def test_missing_duplicate_failed_or_skipped_environment_is_refused(self):
        mutations = [lambda jobs:jobs.pop(),lambda jobs:jobs.append(copy.deepcopy(jobs[0])),
                     lambda jobs:jobs[0].update(conclusion='skipped'),lambda jobs:jobs[0].update(conclusion='failure'),
                     lambda jobs:jobs[0].update(run_id=11),lambda jobs:jobs[0]['steps'].pop()]
        for mutation in mutations:
            api=FakeAPI();mutation(api.jobs)
            with self.assertRaises(check.Unqualified): self.evaluate(api)

    def test_complete_receipt_inventory_and_archive_are_required(self):
        for field,value in [('success',False),('full_qualification',False),('verification_profile','quick'),
                            ('jobs',1),('archive_sha256','different'),('rebuild_sha256','different'),
                            ('source_inventory_sha256','different'),('source_files',2),
                            ('changed_source_files',['changed']),('http_cases',2),
                            ('conformance_input_sha256','different')]:
            with self.subTest(field=field):
                api=FakeAPI();api.receipt[field]=value
                with self.assertRaises(check.Unqualified): self.evaluate(api)

    def test_missing_duplicated_skipped_and_expected_failure_tests_are_refused(self):
        for field,value in [('completed',['case_one']),('completed',['case_one','case_one']),
                            ('expected',['wrong']),('inventory_complete',False),('tests_run',1),
                            ('skipped',['case_one']),('expected_failures',1),('errors',1),('failures',1)]:
            api=FakeAPI();api.receipt['test_suites']['archive'][field]=value
            with self.assertRaises(check.Unqualified): self.evaluate(api)

    def test_missing_timed_out_and_leaked_phases_are_refused(self):
        for field,value in [('exit',1),('exit',False),('timed_out',True),('cancelled',True),('leaked_process_group',True)]:
            api=FakeAPI();api.receipt['checks'][0][field]=value
            with self.assertRaises(check.Unqualified): self.evaluate(api)
        api=FakeAPI();api.receipt['checks'].pop()
        with self.assertRaises(check.Unqualified): self.evaluate(api)

    def test_partial_or_contradictory_conformance_is_refused(self):
        for field,value in [('success',False),('synthetic',False),('disagreements',1),('skipped_cases',1),
                            ('omitted_rule_target_pairs',1),('rules',['wrong'])]:
            api=FakeAPI();entry=next(c for c in api.receipt['checks'] if c['name']=='raw-input conformance')
            payload=json.loads(entry['stdout']);payload[field]=value;entry['stdout']=json.dumps(payload)
            with self.assertRaises(check.Unqualified): self.evaluate(api)

    def test_structured_receipt_is_bound_to_real_checkout_and_workflow(self):
        for field,value in [('checkout','f'*40),('tree','f'*40),('parents',[HEAD,BASE]),
                            ('workflow_sha256','different'),('event','push')]:
            api=FakeAPI();api.receipt['ci_identity'][field]=value
            with self.assertRaises(check.Unqualified): self.evaluate(api)

    def test_log_cannot_substitute_a_checkout_from_test_output(self):
        _,receipt=fixture()
        data=log(receipt, checkout='f'*40)+('[command]/usr/bin/git log -1 --format=%H\n'+TESTED+'\n').encode()
        checkout,_=check.receipt_from_log(data)
        self.assertEqual(checkout,'f'*40)
        api=FakeAPI();api.log_override=data
        with self.assertRaises((check.Unqualified,KeyError)): self.evaluate(api)

    def test_duplicate_truncated_and_nonfinite_receipts_are_refused(self):
        _,receipt=fixture();data=log(receipt)
        for broken in [data+json.dumps(receipt,indent=2).encode(),data[:-30],
                       data.replace(b'"success": true,',b'"success": true, "success": true,',1),
                       data.replace(b'"jobs": 2',b'"jobs": NaN'),
                       data.replace(b'"jobs": 2',b'"jobs": 1e999')]:
            with self.assertRaises((check.Unqualified,ValueError)): check.receipt_from_log(broken)

    def test_main_change_during_lookup_is_refused(self):
        api=FakeAPI();original=api.json
        def changing(path):
            result=original(path)
            if path=='/commits/main' and api.calls.count(path)==2: result['sha']='f'*40
            return result
        api.json=changing
        with self.assertRaises(check.Unqualified): self.evaluate(api)

    def test_api_failure_is_not_a_qualification(self):
        api=FakeAPI();api.log=Mock(side_effect=check.Unqualified('GitHub evidence unavailable'))
        with self.assertRaises(check.Unqualified): self.evaluate(api)

    def test_cli_failure_emits_false_without_exposing_secret(self):
        with tempfile.TemporaryDirectory() as folder:
            output=Path(folder)/'decision.json';github_output=Path(folder)/'output';summary=Path(folder)/'summary'
            env={'GITHUB_EVENT_NAME':'workflow_dispatch','GITHUB_TOKEN':'never-print-this',
                 'GITHUB_OUTPUT':str(github_output),'GITHUB_STEP_SUMMARY':str(summary)}
            captured=io.StringIO()
            with patch.dict(os.environ,env,clear=True),patch.object(sys,'argv',['postmerge','--output',str(output)]),patch('sys.stdout',captured):
                self.assertEqual(check.main(),0)
            self.assertFalse(json.loads(output.read_text())['reuse'])
            self.assertEqual(github_output.read_text(),'reuse=false\n')
            self.assertNotIn('never-print-this',captured.getvalue()+summary.read_text())

    def test_log_download_never_forwards_credentials_to_storage(self):
        api=check.GitHub(REPO,'secret-token')
        error=urllib.error.HTTPError(api.base+'/actions/jobs/1/logs',302,'redirect',
                                   {'Location':'https://proof.blob.core.windows.net/log?signature=example'},None)
        response=Mock();response.__enter__=Mock(return_value=response);response.__exit__=Mock(return_value=False)
        response.read.return_value=b'log'
        api.opener.open=Mock(side_effect=[error,response])
        self.assertEqual(api.log(1),b'log')
        first,second=[entry.args[0] for entry in api.opener.open.call_args_list]
        self.assertEqual(first.get_header('Authorization'),'Bearer secret-token')
        self.assertIsNone(second.get_header('Authorization'))

    def test_unsafe_log_redirect_and_oversized_log_are_refused(self):
        for target in ['http://proof.blob.core.windows.net/x','https://localhost/log','https://evil.example/log']:
            api=check.GitHub(REPO,'secret')
            api.opener.open=Mock(side_effect=urllib.error.HTTPError(api.base+'/actions/jobs/1/logs',302,'redirect',{'Location':target},None))
            with self.assertRaises(check.Unqualified): api.log(1)
        with patch.object(check,'MAX_LOG_BYTES',3):
            with self.assertRaises(check.Unqualified): check.receipt_from_log(b'four')

    def test_ci_wrapper_binds_receipt_and_propagates_failure(self):
        identity={'checkout':TESTED,'tree':TREE,'parents':[BASE,HEAD],'workflow_sha256':'workflow','event':'pull_request'}
        for success,exit_code in [(True,0),(False,1)]:
            with patch.object(ci_qualify,'checkout_identity',return_value=identity),patch.object(ci_qualify.subprocess,'run',return_value=Mock(stdout=json.dumps({'success':success}),returncode=exit_code)),patch('sys.stdout',new_callable=io.StringIO) as output:
                self.assertEqual(ci_qualify.main(),exit_code)
                self.assertEqual(json.loads(output.getvalue())['ci_identity'],identity)

    def test_ci_wrapper_rejects_checkout_change(self):
        with patch.object(ci_qualify,'checkout_identity',side_effect=[{'tree':'before'},{'tree':'after'}]),patch.object(ci_qualify.subprocess,'run',return_value=Mock(stdout='{"success":true}',returncode=0)):
            with self.assertRaises(check.Unqualified): ci_qualify.main()
