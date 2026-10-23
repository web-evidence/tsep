#!/usr/bin/env python3
"""Prospective TS02 collection using prior owner approval and native HTTP. Apache-2.0."""
import argparse
import copy
from datetime import datetime, timezone
import hashlib
import ipaddress
import json
from pathlib import Path
import platform
import re
import ssl
import subprocess
import sys
import tempfile
import time
from urllib.parse import urljoin, urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import tsep
from adapters import redirect_plan as workflow
from adapters.package import inventory, json_bytes, publish, regular, seal
from collectors import http as transport
from conformance import http, redirects
from provenance.runtime import loaded_sources
from reports import html as renderer

VERSION = '2'
NAME = 'TSEP prospective TS02 collector'
MAX_TOTAL = 2 * 1024 * 1024


def now():
    return datetime.now(timezone.utc).isoformat()


def sources():
    return dict(workflow.source_files(), **loaded_sources(ROOT, {
        'collectors/ts02.py': sys.modules[__name__], 'collectors/http.py': transport,
        'reports/html.py': renderer}))


def origin(value):
    redirects.url(value)
    tsep.require(len(value) <= 4096, 'URL exceeds collector length bound')
    p = urlsplit(value)
    tsep.require(p.port is None or 1 <= p.port <= 65535, 'Invalid destination port')
    return p.scheme, p.hostname.lower(), p.port or (443 if p.scheme == 'https' else 80)


def validate_settings(settings, plan):
    keys = {'origins', 'accept_encoding', 'timeout', 'max_bytes', 'max_redirects',
            'max_total_bytes', 'max_seconds', 'allow_loopback'}
    tsep.require(type(settings) is dict and set(settings) == keys, 'Invalid TS02 collection settings')
    allowed = settings['origins']
    tsep.require(type(allowed) is list and 1 <= len(allowed) <= 20, 'Declare 1–20 origins')
    origins = [origin(u) for u in allowed]
    tsep.require(len(set(origins)) == len(origins), 'Duplicate origin')
    tsep.require(all(urlsplit(u).path in ('', '/') and not urlsplit(u).query for u in allowed),
                 'Allowed origins must not include paths or queries')
    tsep.require(type(settings['allow_loopback']) is bool, 'Explicit loopback setting required')
    tsep.require(plan['access'] in ('public', 'restricted', 'synthetic'), 'Invalid access classification')
    tsep.require(settings['allow_loopback'] == (plan['access'] == 'synthetic'),
                 'Loopback collection is restricted to explicit synthetic exercises')
    if settings['allow_loopback']:
        tsep.require(all(ipaddress.ip_address(o[1]).is_loopback for o in origins),
                     'Synthetic collector requires literal loopback origins only')
    tsep.require(settings['accept_encoding'] in ('identity', 'gzip, deflate'), 'Unsupported Accept-Encoding')
    for key, lo, hi in [('timeout', .1, 30), ('max_seconds', 1, 300)]:
        tsep.require(type(settings[key]) in (int, float) and lo <= settings[key] <= hi,
                     'Invalid '+key+' bound')
    for key, lo, hi in [('max_bytes', 1024, 1024*1024), ('max_total_bytes', 1024, MAX_TOTAL),
                        ('max_redirects', 0, 19)]:
        tsep.require(type(settings[key]) is int and lo <= settings[key] <= hi, 'Invalid '+key+' bound')
    tsep.require(1 <= len(plan['targets']) <= 10, 'Collector requires 1–10 planned targets')
    for row in plan['targets']:
        tsep.require(origin(row['url']) in origins and
                     origin(row['intent']['redirect_plan']['expected_final_url']) in origins,
                     'Source or expected destination outside declared origins')
        agent = row['intent']['crawler']
        tsep.require(type(agent) is str and agent.strip() and agent.isascii() and len(agent) <= 1000
                     and not re.search(r'[\x00-\x1f\x7f]', agent), 'Invalid planned User-Agent')
    return settings


def bounds_label(settings):
    return json.dumps(settings, ensure_ascii=True, sort_keys=True, separators=(',', ':'))


def prepare(plan_file, settings_file, output):
    plan = tsep.parse_json(regular(plan_file, tsep.MAX_JSON_BYTES))
    workflow.validate_plan(plan, now())
    settings = tsep.parse_json(regular(settings_file, tsep.MAX_JSON_BYTES))
    validate_settings(settings, plan)
    bound = {'version': VERSION, 'settings': settings, 'source_files': sources()}
    plan = copy.deepcopy(plan)
    for row in plan['targets']:
        row['intent']['redirect_reader'] = 'http-trajectory-headers-v1'
        row['context'].update(tool=NAME, tool_version=VERSION, bounds=bounds_label(settings),
                              collection=copy.deepcopy(bound))
    with tempfile.TemporaryDirectory(prefix='tsep-ts02-plan-') as folder:
        normalized = Path(folder)/'plan.json'
        normalized.write_bytes(json_bytes(plan))
        return workflow.prepare(normalized, output)


def reviewed_data(root):
    entries, request, plan = workflow.request_data(root, reviewed=True)
    root = Path(root)
    receipt = tsep.read_json(root/'receipt.json')
    tsep.require(receipt['kind'] == 'tsep-redirect-plan-import' and receipt['workflow_version'] == workflow.VERSION,
                 'Unsupported review receipt')
    tsep.require(receipt['request_sha256'] == entries['request.json'] and
                 receipt['response_sha256'] == entries['completed-response.json'] and
                 receipt['reviewed_plan_sha256'] == entries['reviewed-plan.json'], 'Changed receipt bindings')
    tsep.require(tsep.timestamp(receipt['imported_at']) <= tsep.timestamp(now()), 'Future review import')
    reviewed = workflow.answers(request, plan, tsep.read_json(root/'completed-response.json'),
                                entries['request.json'], receipt['imported_at'])
    tsep.require(reviewed == tsep.read_json(root/'reviewed-plan.json'), 'Reviewed plan differs from supplied response')
    tsep.require(all(t['intent']['redirect_review']['outcome'] == 'approved' for t in reviewed['targets']),
                 'Collection requires prior approval of every target; rejected plan retained without collection')
    bound = plan['targets'][0]['context'].get('collection')
    tsep.require(type(bound) is dict and set(bound) == {'version', 'settings', 'source_files'}
                 and bound['version'] == VERSION and bound['source_files'] == sources(),
                 'Collector binding absent or source files changed')
    validate_settings(bound['settings'], plan)
    for row in plan['targets']:
        context = row['context']
        tsep.require(context.get('collection') == bound and context.get('tool') == NAME
                     and context.get('tool_version') == VERSION and
                     context.get('bounds') == bounds_label(bound['settings']), 'Changed collector context')
    return plan, bound, receipt


def new_output(output, source):
    output, source = Path(output), Path(source).resolve()
    tsep.require(output.parent.is_dir() and not output.exists() and not output.is_symlink(),
                 'Choose a NEW output directory with an existing parent')
    tsep.require(source not in output.resolve().parents and output.resolve() != source,
                 'Output must be outside the source package')
    return output


def worker(url, agent, settings, directory, byte_budget, seconds):
    """Save native files in the durable attempt directory, including on timeout."""
    config = {k: settings[k] for k in ('accept_encoding', 'timeout', 'max_bytes', 'allow_loopback')}
    config.update(url=url, agent=agent, directory=str(directory),
                  max_bytes=min(settings['max_bytes'], byte_budget), timeout=min(settings['timeout'], seconds))
    metadata = {'started_at': now(), 'complete': False}
    failure = None
    try:
        run = subprocess.run([sys.executable, str(ROOT/'collectors/http.py')],
                             input=json.dumps(config), text=True, capture_output=True,
                             timeout=min(settings['timeout']+1, seconds))
        if run.returncode:
            failure = 'HTTP worker exited with code '+str(run.returncode)
    except subprocess.TimeoutExpired:
        failure = 'Supervisor deadline reached (including DNS)'
    if (directory/'metadata.json').is_file():
        try:
            metadata = tsep.parse_json(regular(directory/'metadata.json', 16384))
            tsep.require(type(metadata) is dict and type(metadata.get('complete')) is bool, 'Invalid worker metadata')
        except (ValueError, OSError, TypeError):
            metadata = {'complete': False, 'error': 'Worker metadata unavailable'}
    if metadata.get('stop_reason')=='response-byte-limit' and config['max_bytes']<settings['max_bytes']:
        metadata['stop_reason']='phase-byte-limit'
    if failure:
        metadata.update(complete=False, error=failure, stop_reason='supervisor-error')
    for name in ('request.bin', 'response.bin'):
        if not (directory/name).exists():
            (directory/name).write_bytes(b'')
            metadata.update(complete=False, error=metadata.get('error', 'Worker file unavailable'))
    metadata['finished_at'] = now()
    metadata['request_semantics'] = 'Prepared request bytes; server receipt is not established'
    (directory/'supervision.json').write_bytes(json_bytes(metadata))
    return metadata


def capture_input(root, plan, ledger):
    """Reconstruct only from inventoried raw files; no precomputed verdict accepted."""
    root = Path(root)
    records = ledger['targets']
    tsep.require(type(records) is list and len(records) == len(plan['targets']), 'Different collection population')
    targets = []
    for number, (expected, record) in enumerate(zip(plan['targets'], records), 1):
        tsep.require(record['url'] == expected['url'] and type(record['hops']) is list
                     and len(record['hops']) <= 20, 'Invalid collected target')
        row = copy.deepcopy(expected)
        row.update(observed_at=record['observed_at'], http=[])
        for index, hop in enumerate(record['hops'], 1):
            directory = root/'raw'/('target-'+str(number)+'-hop-'+str(index))
            meta = tsep.parse_json(regular(directory/'supervision.json', 16384))
            tsep.require(type(meta.get('complete')) is bool, 'Invalid completion metadata')
            row['http'].append(dict(meta, url=hop['url'],
                request=http.encoded(regular(directory/'request.bin', 16384)),
                response=http.encoded(regular(directory/'response.bin', 1024*1024))))
        targets.append(row)
    return {'input_version': '2', 'rules': workflow.RULES, 'targets': targets}


def collect(reviewed_dir, output):
    plan, bound, receipt = reviewed_data(reviewed_dir)
    output = new_output(output, reviewed_dir)
    source_digest = tsep.digest(Path(reviewed_dir)/'SHA256SUMS')
    output.mkdir(mode=0o700)
    publish(reviewed_dir, output/'reviewed')
    # Recheck the copied package before acquisition to avoid mixing a concurrent edit.
    copied_plan, copied_bound, _ = reviewed_data(output/'reviewed')
    tsep.require(copied_plan == plan and copied_bound == bound and
                 tsep.digest(output/'reviewed/SHA256SUMS') == source_digest, 'Review package changed during copy')
    settings = bound['settings']
    started = now()
    deadline = time.monotonic()+settings['max_seconds']
    ledger = {'kind': 'tsep-ts02-collection', 'collector_version': VERSION, 'state': 'collecting',
              'started_at': started, 'source_files': bound['source_files'],
              'reviewed_manifest_sha256': source_digest, 'targets': [], 'response_bytes': 0,
              'worker_attempts': 0, 'access': plan['access'],
              'environment': {'python': platform.python_version(), 'openssl': ssl.OPENSSL_VERSION},
              'scope': 'Declared HTTP trajectories only; no authenticated human identity or server receipt.'}
    (output/'raw').mkdir()
    (output/'collection.json').write_bytes(json_bytes(ledger))
    allowed = {origin(u) for u in settings['origins']}
    try:
        for number, target in enumerate(plan['targets'], 1):
            record = {'url': target['url'], 'hops': [], 'limits': []}
            ledger['targets'].append(record)
            current, visited = target['url'], set()
            for hop_index in range(settings['max_redirects']+1):
                remaining = deadline-time.monotonic()
                budget = settings['max_total_bytes']-ledger['response_bytes']
                if remaining <= 0 or budget <= 0:
                    record['limits'].append('Total time/response byte budget reached; no further request')
                    break
                tsep.require(tsep.digest(ROOT/'collectors/http.py') == bound['source_files']['collectors/http.py'],
                             'Transport source changed before request')
                directory = output/'raw'/('target-'+str(number)+'-hop-'+str(hop_index+1))
                directory.mkdir()
                ledger['worker_attempts'] += 1
                meta = worker(current, target['intent']['crawler'], settings, directory, budget, remaining)
                response = regular(directory/'response.bin', settings['max_bytes'])
                ledger['response_bytes'] += len(response)
                record['hops'].append({'url': current})
                visited.add(current)
                if not meta['complete']:
                    record['limits'].append(meta.get('error', 'Incomplete transport'))
                    break
                try:
                    status, headers, _ = http.message(http.encoded(response), True)
                    if status not in redirects.REDIRECTS:
                        break
                    locations = headers.get('location', [])
                    if len(locations) != 1 or not locations[0]:
                        raise ValueError('Missing or ambiguous Location; next hop not fetched')
                    location = locations[0]
                    tsep.require(not re.search(r'[^\x21-\x7e]|[\\<>"#]', location), 'Location outside supported syntax')
                    destination = urljoin(current, location)
                    dest_origin = origin(destination)
                    tsep.require(destination not in visited, 'Loop retained; URL not revisited')
                    tsep.require(dest_origin in allowed, 'Redirect outside declared origins; destination not fetched')
                    tsep.require(not (urlsplit(current).scheme == 'https' and dest_origin[0] != 'https'),
                                 'HTTPS downgrade refused')
                    tsep.require(hop_index < settings['max_redirects'], 'Collection redirect bound reached')
                    current = destination
                except ValueError as error:
                    record['limits'].append(str(error))
                    break
            record['observed_at'] = now()
            (output/'collection.json').write_bytes(json_bytes(ledger))
        tsep.require(sources() == bound['source_files'], 'Collector sources changed during collection')
        captures = json_bytes(capture_input(output, plan, ledger))
        tsep.require(len(captures) <= tsep.MAX_JSON_BYTES, 'Capture input exceeds adapter bound; raw attempts retained')
        (output/'captures.json').write_bytes(captures)
        ledger.update(state='complete', finished_at=now(), captures_sha256=hashlib.sha256(captures).hexdigest())
        (output/'collection.json').write_bytes(json_bytes(ledger))
        seal(output)
        inventory(output)
    except BaseException as error:
        ledger.update(state='failed', finished_at=now(), failure=type(error).__name__+': '+str(error))
        (output/'collection.json').write_bytes(json_bytes(ledger))
        seal(output)
        raise
    return {'collected': True, 'targets': len(plan['targets']), 'worker_attempts': ledger['worker_attempts'],
            'response_bytes': ledger['response_bytes'], 'limits': [r['limits'] for r in ledger['targets']],
            'human_decisions_created': 0, 'output': str(output)}


def assess(collection, output):
    collection = Path(collection)
    inventory(collection)
    ledger = tsep.read_json(collection/'collection.json')
    tsep.require(ledger['kind'] == 'tsep-ts02-collection' and ledger['collector_version'] == VERSION
                 and ledger['state'] == 'complete' and ledger['source_files'] == sources(),
                 'Incomplete or incompatible collection')
    plan, bound, receipt = reviewed_data(collection/'reviewed')
    tsep.require(tsep.digest(collection/'reviewed/SHA256SUMS') == ledger['reviewed_manifest_sha256']
                 and tsep.timestamp(receipt['imported_at']) <= tsep.timestamp(ledger['started_at'])
                 <= tsep.timestamp(ledger['finished_at']) <= tsep.timestamp(now()), 'Changed collection binding/chronology')
    raw = regular(collection/'captures.json', tsep.MAX_JSON_BYTES)
    tsep.require(hashlib.sha256(raw).hexdigest() == ledger['captures_sha256'] and
                 raw == json_bytes(capture_input(collection, plan, ledger)), 'Captures differ from retained native files')
    output = new_output(output, collection)
    with tempfile.TemporaryDirectory(prefix='.tsep-ts02-assess-', dir=output.parent) as folder:
        stage = Path(folder)
        result = workflow.attach(collection/'reviewed', collection/'captures.json', stage/'assessment')
        for lang in ('fr', 'en'):
            renderer.write(stage/'assessment/bundle/report.json', stage/('report-'+lang+'.html'), language=lang)
        (stage/'collection-receipt.json').write_bytes(json_bytes({
            'collector_version': VERSION, 'collection_manifest_sha256': tsep.digest(collection/'SHA256SUMS'),
            'source_files': bound['source_files'], 'network_requests': 0,
            'scope': 'Assessment uses retained native collection; retain the complete collection alongside this report.'}))
        seal(stage)
        inventory(stage)
        publish(stage, output)
    return {'assessed': True, 'decision': result['decision'], 'network_requests': 0,
            'bundle': str(output/'assessment/bundle'), 'output': str(output)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ('prepare', 'collect', 'assess'):
        command = sub.add_parser(name)
        command.add_argument('source', type=Path)
        command.add_argument('--output', type=Path, required=True)
        if name == 'prepare':
            command.add_argument('--settings', type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == 'prepare':
            result = prepare(args.source, args.settings, args.output)
        elif args.command == 'collect':
            result = collect(args.source, args.output)
        else:
            result = assess(args.source, args.output)
        print(json_bytes(result).decode(), end='')
        return 0
    except (ValueError, OSError, KeyError, TypeError, AttributeError) as error:
        print(str(error), file=sys.stderr)
        return 64


if __name__ == '__main__':
    sys.exit(main())
