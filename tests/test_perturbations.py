import copy
import json
from pathlib import Path
import socket
import tempfile
import unittest
from unittest.mock import patch

from experiments import perturbations as p


class Perturbations(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source = '<html><head><title>Test</title></head><body>Expected\r\n<form><input></form></body></html>'
        self.raw = self.source.encode()
        (self.root/'source.txt').write_bytes(self.raw)
        self.criteria = {'required_markers': ['Expected'], 'forbidden_markers': ['Forbidden']}
        (self.root/'criteria.json').write_text(json.dumps(self.criteria))
        def case(name, edits, a, b, c):
            return {'id':name, 'label':name, 'explanation':'Synthetic authored test', 'synthetic':bool(edits),
                    'edits':edits, 'expected':dict(enabled=a, disabled=b, consensus=c)}
        end = self.source.index('</body>')
        self.plan = {'format_version':1,'recorded_at':'2026-10-10T00:00:00Z','source_sha256':p.digest(self.raw),
                     'criteria_sha256':p.digest((self.root/'criteria.json').read_bytes()),'cases':[
            case('observed', [], 'pass','pass','pass'),
            case('forbidden', [dict(start=end,end=end,before='',after='<p>Forbidden</p>')], 'fail','fail','fail'),
            case('ambiguous', [dict(start=end,end=end,before='',after='<noscript><img alt="Forbidden"></noscript>')], 'fail','pass','inconclusive')]}
        self.save()

    def tearDown(self):
        self.temp.cleanup()

    def save(self):
        (self.root/'plan.json').write_text(json.dumps(self.plan))

    def run_trial(self, name='output'):
        with patch.object(socket, 'socket', side_effect=AssertionError('No network')), \
                patch.object(socket, 'getaddrinfo', side_effect=AssertionError('No DNS')):
            return p.run(self.root/'source.txt', self.root/'criteria.json', self.root/'plan.json', self.root/name)

    def test_exact_body_and_three_outcomes_replay_offline(self):
        a = self.run_trial()
        self.assertTrue(a['all_expectations_matched'])
        self.assertEqual(a, self.run_trial('replay'))
        self.assertEqual((self.root/'output/observed.source.txt').read_bytes(), self.raw)
        self.assertIn(b'\r\n', (self.root/'output/forbidden.source.txt').read_bytes())
        self.assertEqual([r['actual']['consensus'] for r in a['cases']], ['pass','fail','inconclusive'])
        self.assertEqual(a['normative_effect'], 'none')

    def test_wrong_authored_expectation_is_retained_not_rewritten(self):
        self.plan['cases'][0]['expected']['consensus'] = 'fail';self.save()
        result = self.run_trial()
        self.assertFalse(result['all_expectations_matched'])
        self.assertEqual(result['cases'][0]['expected']['consensus'], 'fail')
        self.assertEqual(result['cases'][0]['actual']['consensus'], 'pass')
        self.assertTrue((self.root/'output/SHA256SUMS').is_file())

    def test_changed_source_and_criteria_rejected_before_output(self):
        for name in ('source.txt','criteria.json'):
            path=self.root/name;old=path.read_bytes();path.write_bytes(old+b' ')
            with self.assertRaisesRegex(ValueError, 'binding mismatch'):self.run_trial()
            self.assertFalse((self.root/'output').exists());path.write_bytes(old)

    def test_false_original_slice_and_overlapping_ranges_rejected(self):
        with self.assertRaisesRegex(ValueError, 'original source'):
            p.mutate(self.source,[dict(start=0,end=1,before='X',after='Y')])
        edit=dict(start=0,end=1,before='<',after='x')
        with self.assertRaisesRegex(ValueError, 'nonoverlapping'):
            p.mutate(self.source,[edit,edit])

    def test_synthetic_label_and_case_paths_cannot_lie(self):
        original=copy.deepcopy(self.plan)
        for kind in ('synthetic','path','duplicate'):
            self.plan=copy.deepcopy(original)
            if kind=='synthetic':self.plan['cases'][1]['synthetic']=False
            elif kind=='path':self.plan['cases'][0]['id']='../escape'
            else:self.plan['cases'][1]['id']='observed'
            self.save()
            with self.assertRaises(ValueError):self.run_trial()
            self.assertFalse((self.root/'output').exists())

    def test_existing_output_never_replaced(self):
        self.run_trial()
        old=(self.root/'output/results.json').read_bytes()
        with self.assertRaisesRegex(ValueError, 'new output'):self.run_trial()
        self.assertEqual((self.root/'output/results.json').read_bytes(),old)


if __name__ == '__main__':unittest.main()
