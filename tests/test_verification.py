"""Configurable verification deadlines fail visibly and never skip checks. Apache-2.0."""
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import verify
import tsep


class VerificationDeadline(unittest.TestCase):
    def test_default_override_and_invalid_timeout(self):
        self.assertEqual(verify.step_timeout({}),120)
        self.assertEqual(verify.step_timeout({verify.TIMEOUT_ENV:'300'}),300)
        self.assertEqual(verify.step_timeout({verify.TIMEOUT_ENV:'0.25'}),0.25)
        for value in ('','bad','0','-1','NaN','inf','-inf','86401','1e309'):
            with self.subTest(value=value),self.assertRaises(tsep.Invalid):
                verify.step_timeout({verify.TIMEOUT_ENV:value})

    def test_configured_deadline_is_used_and_partial_output_is_retained(self):
        environment=dict(os.environ,**{verify.TIMEOUT_ENV:'2.5'})
        checks=[]
        with patch.object(verify.subprocess,'run',side_effect=subprocess.TimeoutExpired(
                ['fixture'],2.5,output=b'partial\xff',stderr=b'fixture diagnostic')) as child:
            with self.assertRaisesRegex(tsep.Invalid,'fixture timed out after 2.5'):
                verify.run(['fixture'],ROOT,environment,'fixture',checks)
        self.assertEqual(child.call_args.kwargs['timeout'],2.5)
        self.assertEqual(checks[0]['stdout'],'partial\ufffd')
        self.assertEqual(checks[0]['stderr'],'fixture diagnostic')
        self.assertIsNone(checks[0]['exit']);self.assertTrue(checks[0]['timed_out'])

    def test_real_child_timeout_is_an_explicit_failure(self):
        checks=[];environment=dict(os.environ,**{verify.TIMEOUT_ENV:'0.05'})
        with self.assertRaisesRegex(tsep.Invalid,'timed out'):
            verify.run([sys.executable,'-c','import time; time.sleep(10)'],ROOT,environment,'slow fixture',checks)
        self.assertEqual(checks[0]['name'],'slow fixture')
        self.assertEqual(checks[0]['timeout_seconds'],0.05)
        self.assertTrue(checks[0]['timed_out'])

    def test_invalid_configuration_fails_cli_without_starting_checks(self):
        result=subprocess.run([sys.executable,str(ROOT/'scripts/verify.py')],
                              env=dict(os.environ,**{verify.TIMEOUT_ENV:'0'}),
                              text=True,capture_output=True,timeout=10)
        self.assertEqual(result.returncode,1,result.stdout+result.stderr)
        report=json.loads(result.stdout)
        self.assertFalse(report['success']);self.assertEqual(report['checks'],[])
        self.assertIn(verify.TIMEOUT_ENV,report['error'])


if __name__=='__main__':unittest.main()
