#!/usr/bin/env python3
"""Rehearse the TS08 application boundary using synthetic evidence only. Apache-2.0."""
import argparse
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import tsep
from adapters import captures, inspection_intake, replay
from adapters.package import json_bytes
from conformance.agent_policy import digest
from provenance.runtime import runtime_identity

VERSION = '1'
# Authored integration expectations, not derived from observed engine outcomes.
CASES = {
    'qualified-positive': ('C', ['pass', 'pass', 'pass']),
    'negative-explained-without-cause': ('C', ['pass', 'pass', 'pass']),
    'missing-plan-review': ('NT', ['inconclusive', 'pass', 'pass']),
    'missing-review': ('NT', ['pass', 'pass', 'inconclusive']),
    'claimed-wrong-verdict': ('NC', ['pass', 'pass', 'fail']),
    'old-crawl': ('NT', ['pass', 'inconclusive', 'pass']),
    'api-403': ('NT', ['pass', 'inconclusive', 'inconclusive']),
    'unknown-url-no-fields': ('NT', ['pass', 'inconclusive', 'inconclusive']),
    'independent-contradiction-survives-old-crawl': ('NC', ['pass', 'inconclusive', 'fail']),
    'current-page-claim': ('NC', ['pass', 'pass', 'fail']),
    'future-enum': ('NT', ['pass', 'inconclusive', 'pass']),
    'acquired-before-plan': ('NC', ['fail', 'inconclusive', 'inconclusive']),
    'two-selected-urls': ('C', ['pass', 'pass', 'pass']),
}
TIME_KEYS = {'observed_at', 'declared_at', 'retrieved_at', 'lastCrawlTime', 'due_at'}


def write(path, value):
    with path.open('xb') as handle:
        handle.write(value if isinstance(value, bytes) else json_bytes(value))


def fixture():
    path = ROOT / 'tests/fixtures/inspection-evidence-v2.json'
    raw = path.read_bytes()
    tsep.require(hashlib.sha256(raw).hexdigest() == path.with_suffix('.sha256').read_text().strip(),
                 'Frozen TS08 fixture changed')
    data = tsep.parse_json(raw)
    tsep.require(data['synthetic'] is True, 'Synthetic fixtures only')
    return {c['id'].removeprefix('inspection-v1-'): c for c in data['cases']}


def move_dates(value, delta):
    """Construct NEW synthetic examples relative to a disclosed run anchor."""
    if isinstance(value, dict):
        return {key: (tsep.timestamp(item) + delta).isoformat()
                if key in TIME_KEYS and isinstance(item, str) else move_dates(item, delta)
                for key, item in value.items()}
    if isinstance(value, list):
        return [move_dates(item, delta) for item in value]
    return value


def two_url_case(source):
    """Author a second explicitly fictional member; never mutate the frozen corpus."""
    case = deepcopy(source)
    case['id'] = 'app-rehearsal-two-selected-urls'
    target = case['input']['targets'][0]
    url = 'https://example.com/second'
    plan = target['intent']['inspection']
    plan['population'] = 'Two fictional pages, no site extrapolation'
    plan['selection_method'] = 'Explicit finite list of two fictional product pages'
    plan['members'][0]['selection_reason'] = 'First product URL in this authored scope'
    plan['members'].append(dict(plan['members'][0], url=url,
                                selection_reason='Second product URL in this authored scope'))
    record = deepcopy(target['inspection_records'][0])
    record['url'] = url
    request = tsep.parse_json(record['request']['raw_text'])
    request['inspectionUrl'] = url
    response = tsep.parse_json(record['response']['raw_text'])
    status = response['inspectionResult']['indexStatusResult']
    status['googleCanonical'] = status['userCanonical'] = url
    for key, value in (('request', request), ('response', response)):
        raw = json_bytes(value)
        record[key] = {'raw_text': raw.decode('utf-8'), 'sha256': hashlib.sha256(raw).hexdigest()}
    target['inspection_records'].append(record)
    review = deepcopy(target['inspection_reviews'][0])
    review['url'] = url
    target['inspection_reviews'].append(review)
    return case


def authored_target(case, anchor):
    source = case['input']['targets'][0]
    tsep.require(source['inspection_synthetic'] is True, 'Real captures are forbidden in this rehearsal')
    # Keep chronology/age differences; never refresh or rebind a real acquisition.
    delta = anchor - tsep.timestamp(source['observed_at'])
    target = move_dates(deepcopy(source), delta)
    for record in target['inspection_records']:
        tsep.require(record['provenance'] == 'synthetic-exercise', 'Synthetic records only')
        for name in ('request', 'response'):
            body = move_dates(tsep.parse_json(record[name]['raw_text']), delta)
            raw = json_bytes(body)
            record[name] = {'raw_text': raw.decode('utf-8'), 'sha256': hashlib.sha256(raw).hexdigest()}
    if target.get('inspection_plan_review'):
        review = target['inspection_plan_review']
        tsep.require(review['provenance'] == 'synthetic-exercise', 'Synthetic plan review only')
        review['binding_sha256'] = digest({'url': target['url'], 'intent': target['intent']})
    for review in target.get('inspection_reviews', []):
        tsep.require(review['provenance'] == 'synthetic-exercise', 'Synthetic interpretation only')
    return target


def command(args, directory, log, *, failure=None):
    argv = [sys.executable, *map(str, args)]
    result = subprocess.run(argv, cwd=ROOT, text=True, encoding='utf-8', capture_output=True,
                            timeout=120, env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1'))
    entry = {'argv': argv, 'exit': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr}
    log.append(entry)
    write(directory / ('command-%02d.json' % len(log)), entry)
    if failure is None:
        tsep.require(result.returncode == 0, 'CLI failed: ' + result.stderr)
    else:
        tsep.require(result.returncode != 0 and failure in result.stderr,
                     'Expected refusal not observed: ' + failure)
    return result


def rehearsal(output):
    output = Path(output).absolute()
    tsep.require(output.parent.is_dir() and not output.exists() and not output.is_symlink(),
                 'Choose a NEW output directory with an existing parent')
    cases = fixture()
    cases['two-selected-urls'] = two_url_case(cases['qualified-positive'])
    # Before any child CLI runs, so fixture review dates are never future dates.
    anchor = datetime.now(timezone.utc) - timedelta(minutes=1)
    pins = dict(captures.source_files(), **{
        'spec/protocol.json': tsep.digest(ROOT / 'spec/protocol.json'),
        'adapters/inspection_intake.py': tsep.digest(ROOT / 'adapters/inspection_intake.py'),
        'adapters/replay.py': tsep.digest(ROOT / 'adapters/replay.py'),
        'adapters/package.py': tsep.digest(ROOT / 'adapters/package.py'),
        'adapters/replay_comparison.py': tsep.digest(ROOT / 'adapters/replay_comparison.py'),
        'reports/html.py': tsep.digest(ROOT / 'reports/html.py'),
        'scripts/inspection_app_check.py': tsep.digest(Path(__file__)),
        'tests/fixtures/inspection-evidence-v2.json': tsep.digest(ROOT / 'tests/fixtures/inspection-evidence-v2.json'),
    })
    result = {'kind': 'tsep-inspection-app-rehearsal', 'version': VERSION, 'synthetic': True,
              'success': False, 'generated_at': datetime.now(timezone.utc).isoformat(),
              'synthetic_time_anchor': anchor.isoformat(), 'source_sha256': pins,
              'protocol_version': tsep.read_json(ROOT / 'spec/protocol.json')['version'],
              'intake_version': inspection_intake.VERSION, 'adapter_version': captures.VERSION,
              'replay_version': replay.VERSION, 'runtime': runtime_identity(),
              'scope': 'Actual offline CLI executions over authored synthetic files/reviews; '
                       'no Google account, OAuth, HTTP acquisition, application hosting or real assessment.',
              'cases': [], 'refusals': []}
    output.mkdir(mode=0o700)
    try:
        for name, (status, outcomes) in CASES.items():
            folder = output / name
            folder.mkdir()
            target = authored_target(cases[name], anchor)
            records = target.pop('inspection_records')
            supplied = target.pop('inspection_reviews', [])
            write(folder / 'plan.json', target)
            natives = []
            inspection_args = []
            for index, record in enumerate(records, 1):
                native = folder / ('observation' if index == 1 else 'observation-' + str(index))
                native.mkdir()
                natives.append(native)
                inspection_args.extend(['--inspection', native])
                for key in ('request', 'response'):
                    write(native / (key + '.json'), record[key]['raw_text'].encode('utf-8'))
                write(native / 'manifest.json', {
                    'kind': 'tsep-url-inspection-observation', 'format_version': '1',
                    'provenance': 'synthetic-exercise', 'description': 'Authored app rehearsal, no Google access',
                    'retrieved_at': record['retrieved_at'], 'http_status': record['http_status'], 'change': None,
                    'request_sha256': record['request']['sha256'], 'response_sha256': record['response']['sha256']})
            log = []
            prepared, bundle = folder / 'prepared', folder / 'bundle'
            command(['adapters/inspection_intake.py', 'prepare', folder / 'plan.json',
                     *inspection_args, '--output', prepared], folder, log)
            request = tsep.read_json(prepared / 'review-request.json')
            tsep.require(len(request['reviews']) == len(records), 'Incomplete review coverage')
            tsep.require(all(r['complete'] is False and r['reviewer'] is None for r in request['reviews']),
                         'Intake fabricated a review')
            for review in supplied:
                review['binding_sha256'] = next(r['binding_sha256'] for r in request['reviews'] if r['url'] == review['url'])
            request['reviews'] = supplied
            write(folder / 'synthetic-reviews.json', request)
            command(['adapters/inspection_intake.py', 'build', prepared, '--reviews', folder / 'synthetic-reviews.json',
                     '--assessor', 'Fictional app rehearsal author', '--output', bundle], folder, log)
            report = tsep.read_json(bundle / 'report.json')
            observed = report['results'][0]
            actual = [r['outcome'] for r in observed['atomic_results']]
            tsep.require(observed['status'] == status and actual == outcomes, 'Unexpected result: ' + name)
            tsep.require(all(a['access'] == 'synthetic' for a in report['artifacts']), 'Evidence relabelled as real')
            command(['tsep.py', 'validate', bundle / 'report.json'], folder, log)
            for language in ('fr', 'en'):
                command(['tsep.py', 'html', bundle / 'report.json', '--lang', language,
                         '--output', folder / ('report-' + language + '.html')], folder, log)
            replay_run = command(['adapters/replay.py', bundle, '--output', folder / 'replay'], folder, log)
            replay_result = json.loads(replay_run.stdout)
            tsep.require(replay_result['replayed'] and replay_result['same_source_observations'], 'Replay differed')
            for index, native in enumerate(natives, 1):
                for key in ('request', 'response'):
                    tsep.require((native / (key + '.json')).read_bytes() ==
                                 (prepared / 'originals' / str(index) / (key + '.json')).read_bytes(),
                                 'Original bytes changed')
            result['cases'].append({'id': name, 'expected_status': status, 'observed_status': observed['status'],
                                    'selected_url_count': len(records),
                                    'expected_atomic': outcomes, 'observed_atomic': actual,
                                    'blank_review_created': True, 'exact_replay': True, 'native_bytes_retained': True,
                                    'reports': [name + '/report-fr.html', name + '/report-en.html']})

        base = output / 'qualified-positive'
        folder = output / 'refusals'
        folder.mkdir()
        log = []
        tampered = folder / 'changed-observation'
        shutil.copytree(base / 'observation', tampered)
        with (tampered / 'response.json').open('ab') as handle:
            handle.write(b' ')
        command(['adapters/inspection_intake.py', 'prepare', base / 'plan.json', '--inspection', tampered,
                 '--output', folder / 'invalid-bytes'], folder, log, failure='Changed response bytes')
        result['refusals'].append('native-byte-change')
        missing = tsep.read_json(base / 'plan.json')
        members = missing['intent']['inspection']['members']
        members.append(dict(members[0], url='https://example.com/uncollected'))
        write(folder / 'missing-member-plan.json', missing)
        command(['adapters/inspection_intake.py', 'prepare', folder / 'missing-member-plan.json',
                 '--inspection', base / 'observation', '--output', folder / 'invalid-selection'], folder, log,
                failure='Import exactly one inspection per selected URL')
        result['refusals'].append('omitted-selected-url')
        wrong = tsep.read_json(base / 'synthetic-reviews.json')
        wrong['input_sha256'] = '0' * 64
        write(folder / 'wrong-input-reviews.json', wrong)
        command(['adapters/inspection_intake.py', 'build', base / 'prepared', '--reviews', folder / 'wrong-input-reviews.json',
                 '--assessor', 'Fictional author', '--output', folder / 'invalid-binding'], folder, log,
                failure='Reviews do not bind this intake input')
        result['refusals'].append('reviews-from-other-input')
        before = {p.relative_to(base / 'prepared').as_posix(): tsep.digest(p)
                  for p in (base / 'prepared').rglob('*') if p.is_file()}
        command(['adapters/inspection_intake.py', 'prepare', base / 'plan.json', '--inspection', base / 'observation',
                 '--output', base / 'prepared'], folder, log, failure='Choose a NEW output directory')
        after = {p.relative_to(base / 'prepared').as_posix(): tsep.digest(p)
                 for p in (base / 'prepared').rglob('*') if p.is_file()}
        tsep.require(before == after, 'Existing intake was changed')
        result['refusals'].append('overwrite-existing-intake')
        tsep.require(not any((folder / name).exists() for name in
                            ('invalid-bytes', 'invalid-selection', 'invalid-binding')), 'Refused output was published')
        tsep.require(all(tsep.digest(ROOT / name) == sha for name, sha in pins.items()), 'Source changed during rehearsal')
        result['success'] = True
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        result['error'] = str(error)
    finally:
        write(output / 'rehearsal.json', result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    try:
        result = rehearsal(args.output_dir)
        print(json.dumps({'success': result['success'], 'cases': len(result['cases']),
                          'refusals': len(result['refusals']), 'error': result.get('error'),
                          'output': str(args.output_dir)}, ensure_ascii=False))
        return 0 if result['success'] else 1
    except (OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 64


if __name__ == '__main__':
    sys.exit(main())
