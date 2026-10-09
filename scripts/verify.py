#!/usr/bin/env python3
"""Verify the independent source tree, examples, HTTP probe and distribution. Apache-2.0."""
import hashlib
import json
import os
from pathlib import Path
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


def snapshot():
    return {p.relative_to(ROOT).as_posix(): tsep.digest(p) for p in maintain.release_sources()}


def run(command, directory, environment, label, checks):
    start = time.monotonic()
    result = subprocess.run(command, cwd=directory, env=environment, text=True,
                            encoding='utf-8', capture_output=True, timeout=120)
    checks.append({'name': label, 'exit': result.returncode,
                   'seconds': round(time.monotonic()-start, 3),
                   'stdout': result.stdout, 'stderr': result.stderr})
    tsep.require(result.returncode == 0, label + ' failed; see check output')


def main():
    checks = []
    report = {'success': False, 'python': sys.version.split()[0],
              'scope': 'Local report tests, synthetic examples, loopback HTTP and reproducible package. No external-site audit.',
              'checks': checks}
    before = None
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1')
    try:
        before = snapshot()
        with tempfile.TemporaryDirectory(prefix='tsep-verify-') as folder:
            temp = Path(folder)
            python = sys.executable
            run([python, 'maintain.py', 'check'], ROOT, environment, 'contract and distribution inventory', checks)
            run([python, '-m', 'unittest', 'discover', '-s', 'tests', '-v'], ROOT,
                environment, 'report and distribution tests', checks)
            run([python, 'examples/replay.py', '--output-dir', str(temp/'examples')], ROOT,
                environment, 'synthetic examples outside source tree', checks)
            for case in ('pass', 'fail', 'partial'):
                expected = {p.name: p.read_bytes() for p in (ROOT/'examples'/case).iterdir() if p.is_file()}
                actual = {p.name: p.read_bytes() for p in (temp/'examples'/case).iterdir() if p.is_file()}
                tsep.require(expected == actual, 'Generated example differs from canonical fixture: ' + case)
            http_environment = dict(environment, TSEP_HTTP_REPORT=str(temp/'http-cases.json'))
            run([python, 'tests/legacy_http_cases.py'], ROOT, http_environment, 'bounded HTTP regression cases', checks)
            report['http_cases'] = tsep.read_json(temp/'http-cases.json')['total']
            run([python, 'maintain.py', 'build', '--output', str(temp/'first.zip')], ROOT,
                environment, 'explicit distribution build', checks)
            with zipfile.ZipFile(temp/'first.zip') as archive:
                expected_names = {'tsep/' + name for name in before} | {'tsep/SHA256SUMS'}
                tsep.require(set(archive.namelist()) == expected_names, 'Unexpected archive entry')
                # Every name was checked against the explicit release inventory above.
                archive.extractall(temp/'extracted')
            extracted = temp/'extracted/tsep'
            run([python, 'maintain.py', 'check'], extracted, environment, 'extracted contract', checks)
            run([python, 'tsep.py', 'validate', 'examples/pass/report.json'], extracted,
                environment, 'extracted CLI', checks)
            run([python, '-m', 'unittest', 'discover', '-s', 'tests', '-v'], extracted,
                environment, 'extracted report and atomic-rule cases', checks)
            run([python, 'maintain.py', 'build', '--output', str(temp/'second.zip')], extracted,
                environment, 'rebuild from extracted archive', checks)
            report['archive_sha256'] = tsep.digest(temp/'first.zip')
            report['rebuild_sha256'] = tsep.digest(temp/'second.zip')
            tsep.require(report['archive_sha256'] == report['rebuild_sha256'], 'Archive is not reproducible')
            report['source_files'] = len(before)
        report['success'] = True
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        report['error'] = str(error)
    finally:
        if before is not None:
            after = snapshot()
            changed = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
            report['changed_source_files'] = changed
            if changed:
                report['success'] = False
                report['error'] = 'Verification changed source files'
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report['success'] else 1


if __name__ == '__main__':
    sys.exit(main())
