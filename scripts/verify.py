#!/usr/bin/env python3
"""Verify the independent source tree, examples, HTTP probe and distribution. Apache-2.0."""
import hashlib
import argparse
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import zipfile

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import maintain
import tsep
from conformance.corpus import expand
from scripts.runtime import node24
from scripts.test_suite import cpu_seconds
from scripts.verification_tasks import execute, clean_environment

TIMEOUT_ENV = 'TSEP_VERIFY_STEP_TIMEOUT'
DEFAULT_STEP_TIMEOUT = 7200
MAX_STEP_TIMEOUT = 86400


def step_timeout(environment):
    """A positive finite duration up to one day; no unbounded/disabled mode."""
    try:
        seconds = float(environment.get(TIMEOUT_ENV, str(DEFAULT_STEP_TIMEOUT)))
    except (ValueError, TypeError):
        raise tsep.Invalid(TIMEOUT_ENV + ' must be a positive finite number of seconds')
    tsep.require(math.isfinite(seconds) and 0 < seconds <= MAX_STEP_TIMEOUT,
                 TIMEOUT_ENV + ' must be > 0 and <= 86400 finite seconds')
    return seconds


def snapshot():
    return {p.relative_to(ROOT).as_posix(): tsep.digest(p) for p in maintain.release_sources()}


def identity_hash(values):
    return hashlib.sha256(json.dumps(values, ensure_ascii=True, separators=(',', ':')).encode()).hexdigest()


def qualification_inventory(report, expected):
    """Explicit reviewed inventory: discovery alone cannot authorize omissions."""
    for suite in report['test_suites'].values():
        tsep.require(suite['success'] and suite['inventory_complete'] and not suite['skipped']
                     and not suite['expected_failures'], 'Incomplete or failed test inventory')
        tsep.require(suite['tests_run'] == expected['tests'] and
                     identity_hash(suite['completed']) == expected['test_ids_sha256'],
                     'Test inventory differs from qualification manifest')
    tsep.require(report['http_cases'] == expected['http_cases'], 'HTTP qualification inventory differs')
    for key in ('http_case_ids_sha256', 'conformance_case_ids_sha256', 'conformance_input_sha256'):
        tsep.require(report[key] == expected[key], key+' differs from qualification manifest')
    observed = []
    for check in report['checks']:
        if check['name'] in ('raw-input conformance', 'extracted raw-input conformance'):
            value = json.loads(check['stdout'])
            actual = {key:value[key] for key in ('cases','rule_target_pairs','disagreements')}
            actual.update(rules=len(value['rules']), rule_ids_sha256=identity_hash(value['rules']),
                          reduced_pairs=value['coverage']['reduced_pairs'])
            tsep.require(value['success'] and actual == expected['conformance'],
                         'Conformance qualification inventory differs')
            observed.append(actual)
    tsep.require(len(observed) == 2, 'Both conformance runs are required')
    report['qualification_inventory'] = expected


def run(command, directory, environment, label, checks):
    timeout = step_timeout(environment)
    start = time.monotonic()
    print('[verify] start: ' + label, file=sys.stderr, flush=True)
    try:
        result = subprocess.run(command, cwd=directory, env=environment, text=True,
                                encoding='utf-8', capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired as error:
        def captured(value):
            return value.decode('utf-8', errors='replace') if isinstance(value, bytes) else value or ''
        checks.append({'name': label, 'exit': None, 'timed_out': True, 'timeout_seconds': timeout,
                       'seconds': round(time.monotonic()-start, 3),
                       'stdout': captured(error.stdout), 'stderr': captured(error.stderr)})
        print('[verify] timeout: ' + label, file=sys.stderr, flush=True)
        raise tsep.Invalid(label + ' timed out after ' + str(timeout) + ' seconds; see check output') from error
    checks.append({'name': label, 'exit': result.returncode,
                   'seconds': round(time.monotonic()-start, 3),
                   'stdout': result.stdout, 'stderr': result.stderr})
    print('[verify] end: ' + label + '; exit=' + str(result.returncode)
          + '; seconds=' + str(checks[-1]['seconds']), file=sys.stderr, flush=True)
    tsep.require(result.returncode == 0, label + ' failed; see check output')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--quick',action='store_true',help='Targeted regression check only; not full qualification')
    parser.add_argument('--jobs', type=int, choices=(1, 2, 4), default=2,
                        help='Independent full-check processes (default 2); each unittest suite stays serial')
    args=parser.parse_args()
    start, cpu_start = time.monotonic(), cpu_seconds()
    checks = []
    report = {'success': False, 'python': sys.version.split()[0],
              'scope': 'Local report tests, synthetic examples, loopback HTTP and reproducible package. No external-site audit.',
              'checks': checks}
    report['jobs'] = 1 if args.quick else args.jobs
    report['verification_profile'] = 'targeted-lot1' if args.quick else 'full-isolated-phases-v1'
    before = None
    environment = clean_environment(os.environ)
    def interrupted(signum, frame):
        raise KeyboardInterrupt('Verification interrupted by signal '+str(signum))
    previous_term = signal.signal(signal.SIGTERM, interrupted)
    try:
        report['step_timeout_seconds'] = step_timeout(environment)
        report['runtime']=node24(environment)
        environment['TSEP_SOURCE_NODE']=report['runtime']['path']
        report['full_qualification']=not args.quick
        before = snapshot()
        report['source_inventory_sha256'] = hashlib.sha256(
            json.dumps(before, sort_keys=True).encode('utf-8')).hexdigest()
        with tempfile.TemporaryDirectory(prefix='tsep-verify-') as folder:
            temp = Path(folder)
            python = sys.executable
            run([python, 'maintain.py', 'check'], ROOT, environment, 'contract and distribution inventory', checks)
            if args.quick:
                run([python,'-m','unittest','tests.test_lot1_readers','tests.test_source_markers',
                     'tests.test_redirects','tests.test_verification','tests.test_lot1_runtime'],ROOT,
                    environment,'targeted lot 1 regressions (not full qualification)',checks)
            else:
                corpus = expand(tsep.read_json(ROOT/'conformance/cases.json'))
                report['conformance_case_ids_sha256'] = identity_hash([case['id'] for case in corpus['cases']])
                report['conformance_input_sha256'] = identity_hash(corpus)
                expected_inventory = tsep.read_json(ROOT/'scripts/qualification-inventory.json')
                for key in ('conformance_case_ids_sha256', 'conformance_input_sha256'):
                    tsep.require(report[key] == expected_inventory[key], key+' differs before execution')
                run([python, 'examples/replay.py', '--output-dir', str(temp/'examples')], ROOT,
                    environment, 'synthetic examples outside source tree', checks)
                for case in ('pass', 'fail', 'partial', 'captures'):
                    expected = {p.name: p.read_bytes() for p in (ROOT/'examples'/case).iterdir() if p.is_file()}
                    actual = {p.name: p.read_bytes() for p in (temp/'examples'/case).iterdir() if p.is_file()}
                    tsep.require(expected == actual, 'Generated example differs from canonical fixture: ' + case)
                http_environment = dict(environment, TSEP_HTTP_REPORT=str(temp/'http-cases.json'))
                run([python, 'tests/legacy_http_cases.py'], ROOT, http_environment, 'bounded HTTP regression cases', checks)
                http_report = tsep.read_json(temp/'http-cases.json')
                report['http_cases'] = http_report['total']
                report['http_case_ids_sha256'] = identity_hash([row['case'] for row in http_report['cases']])
                run([python, 'maintain.py', 'build', '--output', str(temp/'first.zip')], ROOT,
                    environment, 'explicit distribution build', checks)
                with zipfile.ZipFile(temp/'first.zip') as archive:
                    expected_names = {'tsep/' + name for name in before} | {'tsep/SHA256SUMS'}
                    tsep.require(len(archive.namelist()) == len(expected_names)
                                 and set(archive.namelist()) == expected_names, 'Unexpected archive entry')
                    # Every name was checked against the explicit release inventory above.
                    archive.extractall(temp/'extracted')
                extracted = temp/'extracted/tsep'
                run([python, 'maintain.py', 'check'], extracted, environment, 'extracted contract', checks)
                run([python, 'tsep.py', 'validate', 'examples/pass/report.json'], extracted,
                    environment, 'extracted CLI', checks)
                tasks = [
                    ('report and distribution tests',
                     [python, '-I', '-B', '-X', 'utf8', 'scripts/test_suite.py', '--report', str(temp/'source-tests.json')], ROOT, environment),
                    ('extracted report and atomic-rule cases',
                     [python, '-I', '-B', '-X', 'utf8', 'scripts/test_suite.py', '--report', str(temp/'archive-tests.json')], extracted, environment),
                    ('raw-input conformance', [python, '-I', '-B', '-X', 'utf8', 'conformance/run.py'], ROOT, environment),
                    ('extracted raw-input conformance', [python, '-I', '-B', '-X', 'utf8', 'conformance/run.py'], extracted, environment),
                ]
                execute(tasks, args.jobs, report['step_timeout_seconds'], checks)
                report['test_suites'] = {name: tsep.read_json(temp/(name+'-tests.json'))
                                        for name in ('source', 'archive')}
                for suite in report['test_suites'].values():
                    tsep.require(suite['success'] and suite['inventory_complete'] and not suite['skipped'],
                                 'Incomplete or failed test inventory')
                tsep.require(report['test_suites']['source']['expected'] == report['test_suites']['archive']['expected'],
                             'Source and archive test inventories differ')
                qualification_inventory(report, expected_inventory)
                run([python, 'maintain.py', 'build', '--output', str(temp/'second.zip')], extracted,
                    environment, 'rebuild from extracted archive', checks)
                report['archive_sha256'] = tsep.digest(temp/'first.zip')
                report['rebuild_sha256'] = tsep.digest(temp/'second.zip')
                tsep.require(report['archive_sha256'] == report['rebuild_sha256'], 'Archive is not reproducible')
                report['source_files'] = len(before)
        report['success'] = True
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError, KeyboardInterrupt) as error:
        report['error'] = str(error)
    finally:
        signal.signal(signal.SIGTERM, previous_term)
        if before is not None:
            after = snapshot()
            changed = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
            report['changed_source_files'] = changed
            if changed:
                report['success'] = False
                report['error'] = 'Verification changed source files'
        report['seconds'] = round(time.monotonic()-start, 3)
        report['cpu_seconds'] = round(cpu_seconds()-cpu_start, 3)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report['success'] else 1


if __name__ == '__main__':
    sys.exit(main())
