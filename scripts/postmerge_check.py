#!/usr/bin/env python3
"""Reuse complete PR qualification only for the identical merged tree. Apache-2.0."""
import argparse
import concurrent.futures
import datetime
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = '.github/workflows/verify.yml'
PROFILE = 'full-isolated-phases-v1'
NODE = 'v24.19.0'
ENVIRONMENTS = [('ubuntu-24.04', '3.9')] + [
    ('ubuntu-latest', '3.'+str(n)) for n in range(10, 15)] + [('macos-latest', '3.14')]
JOBS = {'verify ('+os_name+', '+python+')': python for os_name, python in ENVIRONMENTS}
CHECKS = {
    'contract and distribution inventory', 'synthetic examples outside source tree',
    'bounded HTTP regression cases', 'explicit distribution build', 'extracted contract',
    'extracted CLI', 'report and distribution tests', 'extracted report and atomic-rule cases',
    'raw-input conformance', 'extracted raw-input conformance', 'rebuild from extracted archive'}
MAX_AGE_SECONDS = 24*60*60
MAX_LOG_BYTES = 64*1024*1024


class Unqualified(ValueError):
    """Missing or contradictory evidence; full verification is required."""


def require(condition, reason):
    if not condition:
        raise Unqualified(reason)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'Duplicate JSON field')
        result[key] = value
    return result


def invalid_number(value):
    raise Unqualified('Nonfinite JSON number')


def finite_float(value):
    number = float(value)
    require(math.isfinite(number), 'Nonfinite JSON number')
    return number


DECODER = json.JSONDecoder(object_pairs_hook=unique_object, parse_constant=invalid_number, parse_float=finite_float)


def read_json(text):
    return DECODER.decode(text)


def identity_hash(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=True, separators=(',', ':')).encode()).hexdigest()


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, new_url):
        return None


class GitHub:
    """Bounded GET-only API. Credentials never follow a log-download redirect."""
    def __init__(self, repository, token, budget=180):
        require(re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repository), 'Invalid repository')
        self.base = 'https://api.github.com/repos/'+repository
        self.token = token
        self.deadline = time.monotonic()+budget
        self.opener = urllib.request.build_opener(NoRedirect)

    def download(self, url, authenticated, limit):
        remaining = self.deadline-time.monotonic()
        require(remaining > 0, 'Evidence lookup deadline exceeded')
        headers = {'Accept':'application/vnd.github+json', 'X-GitHub-Api-Version':'2022-11-28',
                   'User-Agent':'TSEP-postmerge-identity'}
        if authenticated:
            require(url.startswith(self.base+'/'), 'Credential destination refused')
            headers['Authorization'] = 'Bearer '+self.token
        request = urllib.request.Request(url, headers=headers, method='GET')
        try:
            with self.opener.open(request, timeout=min(20, remaining)) as response:
                data = response.read(limit+1)
            require(len(data) <= limit, 'Evidence response too large')
            return data
        except urllib.error.HTTPError as error:
            if authenticated and error.code == 302 and url.endswith('/logs'):
                target = error.headers.get('Location', '')
                parsed = urllib.parse.urlsplit(target)
                host = parsed.hostname or ''
                require(parsed.scheme == 'https' and parsed.port in (None, 443)
                        and not parsed.username and not parsed.password
                        and (host.endswith('.githubusercontent.com') or host.endswith('.blob.core.windows.net')),
                        'Log redirect destination refused')
                return self.download(target, False, limit)
            raise Unqualified('GitHub HTTP '+str(error.code)) from None
        except (urllib.error.URLError, TimeoutError, OSError):
            raise Unqualified('GitHub evidence unavailable') from None

    def json(self, path):
        require(path.startswith('/') and not path.startswith('//'), 'Invalid API path')
        return read_json(self.download(self.base+path, True, 8*1024*1024).decode('utf-8'))

    def log(self, job):
        require(type(job) is int and job > 0, 'Invalid job identity')
        return self.download(self.base+'/actions/jobs/'+str(job)+'/logs', True, MAX_LOG_BYTES)


def local_identity(root):
    """Rebuild only the distribution; do not execute a second test matrix."""
    environment = {k:v for k,v in os.environ.items() if k not in ('GITHUB_TOKEN', 'GH_TOKEN')}
    environment.update(PYTHONUTF8='1', PYTHONDONTWRITEBYTECODE='1')
    with tempfile.TemporaryDirectory(prefix='tsep-postmerge-') as folder:
        archive = Path(folder)/'current.zip'
        result = subprocess.run([sys.executable, '-B', '-X', 'utf8', 'maintain.py', 'build', '--output', str(archive)],
                                cwd=root, env=environment, capture_output=True, timeout=45)
        require(result.returncode == 0, 'Current distribution could not be built')
        manifest = read_json((root/'release-files.json').read_text(encoding='utf-8'))
        snapshot = {name:hashlib.sha256((root/name).read_bytes()).hexdigest() for name in manifest['files']}
        return {'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),
                'workflow_sha256':hashlib.sha256((root/WORKFLOW).read_bytes()).hexdigest(),
                'source_inventory_sha256':hashlib.sha256(json.dumps(snapshot, sort_keys=True).encode()).hexdigest(),
                'source_files':len(snapshot),
                'qualification_inventory':read_json((root/'scripts/qualification-inventory.json').read_text(encoding='utf-8'))}


def receipt_from_log(data):
    require(len(data) <= MAX_LOG_BYTES, 'Log too large')
    text = re.sub(r'^\d{4}-\d\d-\d\dT\S+\s?', '', data.decode('utf-8-sig'), flags=re.M)
    # Only the pinned checkout action's section can supply this independent SHA.
    begin = '##[group]Run actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1\n'
    end = '##[group]Run actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97\n'
    require(text.count(begin) == text.count(end) == 1 and text.index(begin) < text.index(end),
            'Checkout section missing or ambiguous')
    section = text[text.index(begin):text.index(end)]
    checkouts = re.findall(r'^\[command\].*git log -1 --format=%H\n([0-9a-f]{40})\s*$', section, re.M)
    starts = list(re.finditer(r'^\{\n\s+"success":', text, re.M))
    require(len(checkouts) == 1 and len(starts) == 1, 'Missing or ambiguous checkout/receipt')
    receipt, _ = DECODER.raw_decode(text[starts[0].start():])
    return checkouts[0], receipt


def validate_receipt(receipt, expected, python):
    require(receipt['success'] is True and receipt['full_qualification'] is True, 'Not a full passing receipt')
    require(receipt['verification_profile'] == PROFILE and receipt['jobs'] == 2
            and receipt['step_timeout_seconds'] == 7200, 'Qualification profile differs')
    require(receipt['runtime']['version'] == NODE and receipt['python'].startswith(python+'.'), 'Runtime differs')
    for key in ('archive_sha256', 'source_inventory_sha256', 'source_files', 'qualification_inventory'):
        require(receipt[key] == expected[key], 'Current '+key+' differs from qualification')
    require(receipt['rebuild_sha256'] == expected['archive_sha256']
            and receipt['changed_source_files'] == [], 'Distribution changed or not reproducible')
    inventory = expected['qualification_inventory']
    for key in ('http_cases', 'http_case_ids_sha256', 'conformance_case_ids_sha256', 'conformance_input_sha256'):
        require(receipt[key] == inventory[key], 'Input inventory differs')
    require(set(receipt['test_suites']) == {'source', 'archive'}, 'Both suites required')
    for suite in receipt['test_suites'].values():
        require(suite['success'] is True and suite['inventory_complete'] is True, 'Incomplete test suite')
        require(suite['skipped'] == [] and all(type(suite[key]) is int and suite[key] == 0
                for key in ('errors','failures','unexpected_successes','expected_failures')), 'Tests skipped or failed')
        require(suite['expected'] == suite['completed'] and len(set(suite['completed'])) == inventory['tests']
                and len(suite['completed']) == inventory['tests'] and suite['tests_run'] == inventory['tests']
                and identity_hash(suite['completed']) == inventory['test_ids_sha256'], 'Test identities differ')
    checks = receipt['checks']
    require(len(checks) == len(CHECKS) and {c['name'] for c in checks} == CHECKS, 'Qualification phases differ')
    for check in checks:
        require(type(check['exit']) is int and check['exit'] == 0
                and not any(check.get(k) for k in ('timed_out', 'cancelled', 'leaked_process_group')), 'Phase did not pass')
        if check['name'] in ('raw-input conformance', 'extracted raw-input conformance'):
            value = read_json(check['stdout'])
            actual = {k:value[k] for k in ('cases', 'rule_target_pairs', 'disagreements')}
            actual.update(rules=len(value['rules']), rule_ids_sha256=identity_hash(value['rules']),
                          reduced_pairs=value['coverage']['reduced_pairs'])
            require(value['success'] is True and value['synthetic'] is True
                    and actual == inventory['conformance']
                    and value['skipped_cases'] == value['omitted_rule_target_pairs'] == 0,
                    'Conformance evidence differs')


def evaluate(api, repository, merge_sha, expected, now, push_before):
    require(re.fullmatch('[0-9a-f]{40}', merge_sha or ''), 'Invalid merge commit')
    merged = api.json('/git/commits/'+merge_sha)
    require(merged['sha'] == merge_sha, 'Wrong merge object')
    parents = [p['sha'] for p in merged['parents']]
    require(len(parents) == 2, 'Merge with two parents required; full check for squash/direct push')
    require(push_before == parents[0], 'Push includes a different first-parent range')
    require(api.json('/commits/main')['sha'] == merge_sha, 'Main advanced')
    tree = merged['tree']['sha']
    prs = api.json('/commits/'+merge_sha+'/pulls?per_page=100')
    require(len(prs) < 100, 'Pull request discovery truncated')
    prs = [p for p in prs if p.get('merged_at') and p.get('merge_commit_sha') == merge_sha]
    require(len(prs) == 1, 'Unique merged pull request required')
    pr = api.json('/pulls/'+str(prs[0]['number']))
    require(pr['merged'] is True and pr['merge_commit_sha'] == merge_sha and pr['base']['ref'] == 'main'
            and pr['base']['repo']['full_name'].lower() == repository.lower()
            and pr['head']['sha'] == parents[1], 'Pull request identity differs')
    workflow = api.json('/actions/workflows/verify.yml')
    require(workflow['path'] == WORKFLOW, 'Wrong qualification workflow')
    listing = api.json('/actions/runs?event=pull_request&head_sha='+parents[1]+'&per_page=100')
    runs = listing['workflow_runs']
    require(listing['total_count'] == len(runs), 'Qualification discovery truncated')
    runs = [r for r in runs if r['workflow_id'] == workflow['id']]
    require(len(runs) == 1, 'Unique qualification run required')
    run = api.json('/actions/runs/'+str(runs[0]['id']))
    require(run['event'] == 'pull_request' and run['path'] == WORKFLOW and run['workflow_id'] == workflow['id']
            and run['head_sha'] == parents[1] and run['repository']['full_name'].lower() == repository.lower()
            and run['run_attempt'] == 1 and run['status'] == 'completed' and run['conclusion'] == 'success',
            'Qualification run incomplete, rerun or different')
    recorded_at = datetime.datetime.fromisoformat(run['updated_at'].replace('Z', '+00:00'))
    age = (now-recorded_at).total_seconds()
    require(0 <= age <= MAX_AGE_SECONDS, 'Qualification expired or timestamp invalid')
    listing = api.json('/actions/runs/'+str(run['id'])+'/jobs?per_page=100')
    jobs = listing['jobs']
    require(listing['total_count'] == len(jobs), 'Job discovery truncated')
    selected = [j for j in jobs if j['name'] in JOBS]
    require(len(selected) == 7 and {j['name'] for j in selected} == set(JOBS), 'Seven exact environments required')
    for job in selected:
        require(job['run_id'] == run['id'] and job['status'] == 'completed' and job['conclusion'] == 'success',
                'Environment not successfully qualified')
        for name in ('Verify contract, evidence and reproducible distribution', 'Check that verification preserved the checkout'):
            steps = [s for s in job['steps'] if s['name'] == name]
            require(len(steps) == 1 and steps[0]['conclusion'] == 'success', 'Verification step did not pass')
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        logs = list(pool.map(api.log, [j['id'] for j in selected]))
    commits, proofs = {}, []
    for job, data in zip(selected, logs):
        checkout, receipt = receipt_from_log(data)
        if checkout not in commits:
            commits[checkout] = api.json('/git/commits/'+checkout)
        obj = commits[checkout]
        require(obj['sha'] == checkout and obj['tree']['sha'] == tree
                and [p['sha'] for p in obj['parents']] == parents, 'Actually tested tree or parents differ')
        identity = receipt.get('ci_identity')
        require(identity == {'checkout':checkout, 'tree':tree, 'parents':parents,
                             'workflow_sha256':expected['workflow_sha256'], 'event':'pull_request'},
                'Structured qualification identity differs')
        validate_receipt(receipt, expected, JOBS[job['name']])
        proofs.append({'job':job['id'], 'environment':job['name'], 'checkout':checkout,
                       'python':receipt['python'], 'node':receipt['runtime']['version'],
                       'log_sha256':hashlib.sha256(data).hexdigest()})
    # Refuse a mutable main/head or a rerun appearing during the lookup.
    require(api.json('/commits/main')['sha'] == merge_sha, 'Main advanced during verification')
    fresh = api.json('/actions/runs/'+str(run['id']))
    require(fresh['run_attempt'] == 1 and fresh['conclusion'] == 'success'
            and fresh['updated_at'] == run['updated_at'], 'Qualification changed during verification')
    return {'reuse':True, 'mode':'qualified-identical-tree', 'merge':merge_sha, 'tree':tree,
            'parents':parents, 'pull_request':pr['number'], 'run':run['id'], 'jobs':proofs,
            'archive_sha256':expected['archive_sha256'], 'qualification_inventory':expected['qualification_inventory'],
            'qualified_at':run['updated_at'], 'new_tests_executed':False,
            'scope':'Reuses seven complete PR qualifications in their recorded environments; not a new main matrix.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    started = time.monotonic()
    result = {'reuse':False, 'mode':'full-required', 'reason':'Evidence unavailable'}
    try:
        repo = os.environ.get('GITHUB_REPOSITORY', '')
        sha = os.environ.get('GITHUB_SHA', '')
        require(os.environ.get('GITHUB_EVENT_NAME') == 'push' and os.environ.get('GITHUB_REF') == 'refs/heads/main',
                'Only a main push can reuse qualification')
        require(os.environ.get('GITHUB_WORKFLOW_REF') == repo+'/'+WORKFLOW+'@refs/heads/main', 'Workflow context differs')
        event = read_json(Path(os.environ['GITHUB_EVENT_PATH']).read_text(encoding='utf-8'))
        require(event['after'] == sha and event['ref'] == 'refs/heads/main'
                and event.get('forced') is False and event.get('deleted') is False,
                'Push event differs, is forced or deletes the branch')
        actual = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True, timeout=10).strip()
        require(actual == sha, 'Local checkout differs')
        require(not subprocess.check_output(['git','status','--porcelain','--untracked-files=all'], cwd=ROOT,
                                            text=True, timeout=10).strip(), 'Local checkout is dirty')
        token = os.environ.get('GITHUB_TOKEN', '')
        require(bool(token), 'Read-only GitHub token missing')
        api = GitHub(repo, token)
        result = evaluate(api, repo, sha, local_identity(ROOT), datetime.datetime.now(datetime.timezone.utc), event['before'])
        require(not subprocess.check_output(['git','status','--porcelain','--untracked-files=all'], cwd=ROOT,
                                            text=True, timeout=10).strip(), 'Identity check changed sources')
    except Exception as error:
        # Never print request bodies, authorization headers or signed download URLs.
        reason = str(error) if isinstance(error, Unqualified) else 'Unreadable evidence ('+type(error).__name__+')'
        result = {'reuse':False, 'mode':'full-required', 'reason':reason}
    result['seconds'] = round(time.monotonic()-started, 3)
    args.output.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))
    if os.environ.get('GITHUB_OUTPUT'):
        with open(os.environ['GITHUB_OUTPUT'], 'a', encoding='utf-8') as handle:
            handle.write('reuse='+str(result['reuse']).lower()+'\n')
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a', encoding='utf-8') as handle:
            handle.write('### Post-merge qualification\n\n')
            if result['reuse']:
                handle.write('Reused seven full PR qualifications: identical complete Git tree and ordered parents. '
                             'No new full test run claimed.\n\nRun: '+str(result['run'])+'; tree: `'+result['tree']+'`.\n')
            else:
                handle.write('Full verification required. No qualification reused. Reason: '
                             +result['reason']+'\n')
    return 0  # Missing evidence selects the full matrix, never a passing qualification.


if __name__ == '__main__':
    sys.dont_write_bytecode = True
    sys.exit(main())
