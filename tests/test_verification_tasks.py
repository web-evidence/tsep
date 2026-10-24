"""Execution failures, isolation and complete inventories remain fail-closed. Apache-2.0."""
import contextlib
import copy
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

from scripts import test_suite, verification_tasks as tasks
from scripts import verify


class IndependentPhases(unittest.TestCase):
    def test_environment_cannot_redirect_python_imports_and_temp_roots_are_distinct(self):
        checks=[]
        env=dict(os.environ, PYTHONPATH='/bad/source', PYTHONHOME='/bad/home', PYTHONINSPECT='1')
        command=[sys.executable,'-I','-B','-c',
                 'import json,os,tempfile;print(json.dumps([os.getenv("PYTHONPATH"),os.getenv("PYTHONHOME"),tempfile.gettempdir()]))']
        tasks.execute([(str(i),command,Path.cwd(),env) for i in range(2)],2,10,checks)
        values=[json.loads(c['stdout']) for c in checks]
        self.assertTrue(all(v[:2]==[None,None] for v in values))
        self.assertNotEqual(values[0][2],values[1][2])

    def test_successful_parent_cannot_leave_background_processes(self):
        with tempfile.TemporaryDirectory() as folder:
            script=('import subprocess,sys\n'
                    'subprocess.Popen([sys.executable,"-c","import time;time.sleep(20)"])\n')
            checks=[]
            with self.assertRaisesRegex(ValueError,'leaked descendants'):
                tasks.execute([('leak',[sys.executable,'-c',script],folder,os.environ)],1,10,checks)
            self.assertEqual(checks[0]['exit'],0)
            self.assertTrue(checks[0]['leaked_process_group'])

    def test_all_commands_run_once_in_serial_and_parallel(self):
        for workers in (1, 2, 4):
            with self.subTest(workers=workers), tempfile.TemporaryDirectory() as folder:
                checks=[]
                commands=[(str(i), [sys.executable, '-c',
                           'from pathlib import Path; import os; p=Path(os.environ["FILE"]); '
                           'p.open("x").write("once"); print(p.name)'], folder,
                           dict(os.environ, FILE=str(Path(folder)/str(i)))) for i in range(5)]
                tasks.execute(commands, workers, 10, checks)
                self.assertEqual([c['name'] for c in checks], list(map(str, range(5))))
                self.assertEqual([c['stdout'].strip() for c in checks], list(map(str, range(5))))
                self.assertTrue(all(c['exit']==0 for c in checks))
                self.assertEqual(len(list(Path(folder).iterdir())), 5)

    def test_independent_processes_really_overlap(self):
        with tempfile.TemporaryDirectory() as folder:
            script=('from pathlib import Path; import os,time\n'
                    'Path(os.environ["OWN"]).touch()\n'
                    'while not Path(os.environ["PEER"]).exists(): time.sleep(.01)\n')
            commands=[(str(i), [sys.executable,'-c',script],folder,
                       dict(os.environ, OWN=str(i), PEER=str(1-i))) for i in range(2)]
            checks=[];tasks.execute(commands, 2, 5, checks)
            self.assertEqual(len(checks),2)
            self.assertTrue(all(c['exit']==0 for c in checks))

    def test_failure_cancels_peers_and_does_not_run_pending_checks(self):
        with tempfile.TemporaryDirectory() as folder:
            commands=[('bad',[sys.executable,'-c','print("failure",flush=True);raise SystemExit(7)'],folder,os.environ),
                      ('peer',[sys.executable,'-c','import time; time.sleep(20)'],folder,os.environ),
                      ('pending',[sys.executable,'-c','raise AssertionError("must not run")'],folder,os.environ)]
            checks=[]
            with self.assertRaisesRegex(ValueError,'bad failed'):
                tasks.execute(commands,2,10,checks)
            self.assertEqual(checks[0]['exit'],7)
            self.assertIn('failure',checks[0]['stdout'])
            self.assertTrue(checks[1]['cancelled'])
            self.assertEqual(len(checks),2)

    def test_timeout_kills_descendant_and_retains_partial_output(self):
        with tempfile.TemporaryDirectory() as folder:
            script=('import subprocess,sys,time\n'
                    'subprocess.Popen([sys.executable,"-c",'
                    '"import time;from pathlib import Path;time.sleep(.7);Path(\'leaked\').touch()"] )\n'
                    'print("started",flush=True)\ntime.sleep(20)\n')
            checks=[]
            with self.assertRaisesRegex(ValueError,'timed out'):
                tasks.execute([('slow',[sys.executable,'-c',script],folder,os.environ)],1,.3,checks)
            self.assertTrue(checks[0]['timed_out']);self.assertIsNone(checks[0]['exit'])
            self.assertIn('started',checks[0]['stdout'])
            time.sleep(.8)
            self.assertFalse((Path(folder)/'leaked').exists())

    def test_keyboard_interrupt_cancels_active_checks(self):
        checks=[]
        with patch.object(tasks.time,'sleep',side_effect=KeyboardInterrupt), self.assertRaises(KeyboardInterrupt):
            tasks.execute([('interrupted',[sys.executable,'-c','import time;time.sleep(20)'],
                            Path.cwd(),os.environ)],1,10,checks)
        self.assertTrue(checks[0]['cancelled']);self.assertNotEqual(checks[0]['exit'],0)


class CompleteInventory(unittest.TestCase):
    def result_for(self, method, duplicate=False, fixture=None):
        class Fixture(unittest.TestCase):
            test_case=method
        if fixture:
            Fixture.setUpClass=classmethod(fixture)
        suite=unittest.defaultTestLoader.loadTestsFromTestCase(Fixture)
        if duplicate:
            suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(Fixture))
        with contextlib.redirect_stderr(io.StringIO()):
            return test_suite.run_suite(suite)

    def test_success_records_exact_inventory_and_timing(self):
        result=self.result_for(lambda case: case.assertTrue(True))
        self.assertTrue(result['success']);self.assertEqual(result['tests_run'],1)
        self.assertEqual(result['expected'],result['completed'])
        self.assertEqual(result['timings'][0]['id'],result['expected'][0])
        self.assertGreaterEqual(result['cpu_seconds'],0)

    def test_missing_skipped_or_duplicated_execution_is_not_green(self):
        def broken_setup(cls):
            raise RuntimeError('fixture failed before tests')
        for options in ({'method':lambda case:case.skipTest('missing runtime')},
                        {'method':lambda case:None,'duplicate':True},
                        {'method':lambda case:None,'fixture':broken_setup}):
            with self.subTest(options=list(options)):
                self.assertFalse(self.result_for(**options)['success'])

    def test_failed_subtest_is_not_hidden_by_completed_inventory(self):
        def bad(case):
            with case.subTest(value='contradiction'):
                case.assertEqual('pass','fail')
        result=self.result_for(bad)
        self.assertTrue(result['inventory_complete'])
        self.assertFalse(result['success']);self.assertEqual(result['failures'],1)

    def test_expected_failure_and_failed_import_are_not_green(self):
        method=unittest.expectedFailure(lambda case:case.fail('known failure'))
        self.assertFalse(self.result_for(method)['success'])
        suite=unittest.defaultTestLoader.loadTestsFromName('missing_verification_fixture_module')
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertFalse(test_suite.run_suite(suite)['success'])

    def test_reference_manifest_blocks_removed_cases_and_missing_conformance(self):
        suite={'success':True,'inventory_complete':True,'skipped':[], 'expected_failures':0,
               'tests_run':2,'completed':['a','b']}
        value={'success':True,'cases':3,'rule_target_pairs':4,'disagreements':0,
               'rules':['TS01-A01'],'coverage':{'reduced_pairs':1}}
        report={'test_suites':{'source':copy.deepcopy(suite),'archive':copy.deepcopy(suite)},
                'http_cases':48,'checks':[{'name':name,'stdout':json.dumps(value)} for name in
                  ('raw-input conformance','extracted raw-input conformance')]}
        expected={'tests':2,'test_ids_sha256':verify.identity_hash(['a','b']),'http_cases':48,
                  'conformance':{'cases':3,'rule_target_pairs':4,'disagreements':0,'rules':1,
                                 'rule_ids_sha256':verify.identity_hash(['TS01-A01']),'reduced_pairs':1}}
        for key in ('http_case_ids_sha256','conformance_case_ids_sha256','conformance_input_sha256'):
            report[key]=expected[key]='reviewed-fixture-fingerprint'
        verify.qualification_inventory(report,expected)
        for mutation in ('removed_test','changed_id','http','conformance_count','missing_conformance','case_id'):
            changed=copy.deepcopy(report)
            if mutation=='removed_test':changed['test_suites']['source']['tests_run']=1
            if mutation=='changed_id':changed['test_suites']['source']['completed']=['a','c']
            if mutation=='http':changed['http_cases']=47
            if mutation=='conformance_count':changed['checks'][0]['stdout']=json.dumps(dict(value,cases=2))
            if mutation=='missing_conformance':changed['checks'].pop()
            if mutation=='case_id':changed['conformance_case_ids_sha256']='substituted-case'
            with self.subTest(mutation=mutation),self.assertRaises(ValueError):
                verify.qualification_inventory(changed,expected)
