#!/usr/bin/env python3
"""Offline import of supplied browser DOM serializations; Apache-2.0.

Tool format 1; no browser, network, human review or new normative rule.
Navigation proof is restricted to an immutable, uncompressed laboratory response.
"""
import argparse
import copy
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import tsep
from adapters import captures
from collectors import ts01
from conformance import evaluate as evaluator
from conformance.http import raw_bytes
from provenance.runtime import loaded_sources, runtime_identity

VERSION = '1'
SCOPE = 'Controlled immutable synthetic laboratory; supplied records, not authenticated browser execution'
FILES = ['source.json', 'receipt.json', 'browser.json', 'input.json', 'association.json', 'result.json', 'requests.jsonl', 'bundle/SHA256SUMS']


def sources():
    result = captures.source_files()
    result.update(loaded_sources(ROOT, {'adapters/rendered.py': sys.modules[__name__], 'collectors/ts01.py': ts01}))
    for name in ('spec/protocol.json', 'schemas/report.schema.json'):
        result[name] = tsep.digest(ROOT/name)
    return result


def read(path):
    path = Path(path)
    tsep.require(path.is_file() and not path.is_symlink(), 'Expected regular input file')
    with path.open('rb') as handle:
        raw = handle.read(tsep.MAX_JSON_BYTES+1)
    return raw, tsep.parse_json(raw)


def fingerprint(raw):
    return hashlib.sha256(raw).hexdigest()


def registration(raw, prepared_at):
    data = tsep.parse_json(raw)
    tsep.require(isinstance(data, dict) and set(data) == {'input_version', 'rules', 'targets'}
                 and data['input_version'] in ('1', '2') and data['rules'] == ['TS07-A01', 'TS07-A02', 'TS07-A03']
                 and isinstance(data['targets'], list) and len(data['targets']) == 1, 'One explicit TS07 source target required')
    target = data['targets'][0]
    tsep.require(isinstance(target, dict) and not any(k in target for k in ('render', 'exemption_review', 'access_review')),
                 'Source must not contain render, exemption or access review; this tool does not establish human review')
    plan = target['intent']['rendering']
    tsep.require(plan['mode'] == 'required' and isinstance(plan['required_states'], list) and plan['required_states'], 'Required state plan missing')
    ids = []
    for item in plan['required_states']:
        tsep.require(isinstance(item, dict) and evaluator.text_present(item.get('id')) and evaluator.text_present(item.get('wait'))
                     and isinstance(item.get('interactions'), list) and all(evaluator.text_present(x) for x in item['interactions']), 'Invalid state plan')
        ids.append(item['id'])
    tsep.unique(ids, 'planned state')
    tsep.require(evaluator.text_present(target['context'].get('id')), 'Context ID required')
    tsep.require(target['intent']['crawler'] == 'googlebot', 'Bounded Googlebot directive subset only')
    final_url, status, _, _ = evaluator.trace(target['http'], target['url'], 'googlebot')
    tsep.require(status == 200 and final_url.startswith('http://127.0.0.1:'), 'Only complete loopback laboratory HTML responses are supported')
    stamp = tsep.timestamp
    tsep.require(stamp(target['intent']['declared_at']) <= stamp(target['observed_at']) <= stamp(prepared_at) <= stamp(ts01.now()), 'Invalid preparation chronology')
    return {'format_version': VERSION, 'scope': SCOPE, 'synthetic': True, 'prepared_at': prepared_at,
            'input_sha256': fingerprint(raw), 'source_http_sha256': evaluator.binding_digest(target['http']),
            'response_sha256': fingerprint(raw_bytes(target['http'][-1]['response'])),
            'url': final_url, 'context_id': target['context']['id'], 'plan': plan, 'source_files': sources()}


def prepare(source, output):
    raw, _ = read(source)
    receipt = registration(raw, ts01.now())
    ts01.save(output, receipt)
    return receipt


class Witness(HTMLParser):
    """Read laboratory DOM markers; duplicates/nested markup are not accepted."""
    IDS = {'state', 'js', 'agent', 'context', 'errors', 'event-time'}

    def __init__(self, dom):
        super().__init__(convert_charrefs=True)
        self.values = {}; self.current = None
        self.feed(dom); self.close()

    def handle_starttag(self, tag, attrs):
        if self.current is not None:
            raise ValueError('Nested laboratory witness')
        ids = [v for k,v in attrs if k == 'id']
        if any(v in self.IDS for v in ids):
            tsep.require(len(ids) == 1 and tag == 'span' and ids[0] not in self.values, 'Duplicate/invalid laboratory witness')
            self.current = ids[0]; self.values[self.current] = ''

    def handle_endtag(self, tag):
        if self.current is not None:
            tsep.require(tag == 'span', 'Invalid laboratory witness closing tag')
            self.current = None

    def handle_data(self, data):
        if self.current is not None:
            self.values[self.current] += data


def log_bytes(path):
    path = Path(path)
    tsep.require(path.is_file() and not path.is_symlink(), 'Expected regular server log')
    with path.open('rb') as handle:
        raw = handle.read(tsep.MAX_JSON_BYTES+1)
    tsep.require(len(raw) <= tsep.MAX_JSON_BYTES, 'Server log exceeds bound')
    return raw


def derive(source_raw, receipt_raw, envelope, journal):
    receipt = tsep.parse_json(receipt_raw)
    tsep.require(receipt == registration(source_raw, receipt['prepared_at']), 'Source/receipt/tool binding mismatch')
    tsep.require(isinstance(envelope, dict) and envelope.get('capture_version') == VERSION
                 and envelope.get('receipt_sha256') == fingerprint(receipt_raw), 'Browser capture/receipt binding mismatch')
    method = envelope.get('method', {})
    tsep.require(isinstance(method, dict) and all(evaluator.text_present(method.get(k)) for k in ('name', 'version', 'description')), 'Explicit capture method required')
    tsep.require(envelope.get('server_log_sha256') == fingerprint(journal), 'Server log fingerprint mismatch')
    lines = journal.splitlines(keepends=True)
    items = envelope.get('states')
    tsep.require(isinstance(items, list) and all(isinstance(i, dict) and isinstance(i.get('state'), dict) for i in items), 'Malformed supplied state inventory')
    data, associations, states = tsep.parse_json(source_raw), [], []
    for item in items:
        state = copy.deepcopy(item['state'])
        reasons = []
        try:
            nav = item['navigation']
            index = item['log_index']
            tsep.require(type(index) is int and 0 <= index < len(lines), 'Invalid server log index')
            tsep.require(item['log_line_sha256'] == fingerprint(lines[index]) and tsep.parse_json(lines[index]) == nav, 'Navigation/server log mismatch')
            agent = envelope['browser']['user_agent']
            tsep.require(evaluator.text_present(agent) and agent.lower() != 'googlebot'
                         and nav.get('request_agent') == agent and nav.get('peer') == '127.0.0.1', 'Browser agent/peer mismatch')
            tsep.require(nav.get('url') == receipt['url'], 'Navigation URL differs from source')
            tsep.require(nav.get('complete') is True, 'Navigation response incomplete')
            tsep.require(fingerprint(raw_bytes(nav['response'])) == receipt['response_sha256'], 'Navigation response bytes differ from source')
            stamp = tsep.timestamp
            tsep.require(stamp(receipt['prepared_at']) <= stamp(nav['observed_at']) <= stamp(state['observed_at']) <= stamp(ts01.now()), 'Navigation/DOM chronology mismatch')
            tsep.require(state.get('source_http_sha256') == receipt['source_http_sha256'], 'Claimed trace binding mismatch')
            tsep.require(state.get('url') == receipt['url'] and state.get('context_id') == receipt['context_id'], 'DOM URL/context mismatch')
            witness = Witness(state['dom']).values
            tsep.require(witness.get('state') == state.get('id') and witness.get('context') == receipt['context_id']
                         and witness.get('agent') == agent, 'Laboratory DOM state/context/agent mismatch')
            tsep.require(witness.get('js') == 'executed' and state.get('javascript_enabled') is True, 'Laboratory JS witness missing')
            tsep.require(tsep.parse_json(witness['errors'].encode('utf-8')) == state.get('errors'), 'Laboratory error witness mismatch')
            tsep.require(stamp(nav['observed_at']) <= stamp(witness['event-time']) <= stamp(state['observed_at']), 'Laboratory event chronology mismatch')
        except (ValueError, KeyError, TypeError, AttributeError) as error:
            reasons.append(str(error))
        if reasons:
            # Preserve original in browser.json; explicitly revoke only this derived attribution.
            state.pop('source_http_sha256', None)
        states.append(state)
        associations.append({'id': state.get('id'), 'attributed': not reasons, 'reasons': reasons,
                             'original_source_http_sha256': item['state'].get('source_http_sha256')})
    data['targets'][0]['render'] = {'browser': copy.deepcopy(envelope.get('browser')), 'states': states}
    return data, {'scope': SCOPE, 'method': method, 'states': associations,
                  'transformation': 'Only unverified source bindings removed from derived states; original capture retained unchanged'}


def result_for(data):
    atoms = evaluator.evaluate(data)
    status = 'NC' if any(a['outcome'] == 'fail' for a in atoms) else 'NT'
    return {'atoms': atoms, 'status': status, 'scope': SCOPE, 'human_review_performed': False}


def attach(source, receipt, browser, output, *, server_log):
    source_raw, _ = read(source); receipt_raw, _ = read(receipt); browser_raw, envelope = read(browser)
    journal = log_bytes(server_log)
    data, association = derive(source_raw, receipt_raw, envelope, journal)
    result = result_for(data)
    output = Path(output)
    tsep.require(not output.exists() and not output.is_symlink() and output.parent.is_dir(), 'Choose a NEW output directory with existing parent')
    with tempfile.TemporaryDirectory(prefix='.tsep-render-', dir=output.parent) as temporary:
        stage = Path(temporary)
        for name, raw in [('source.json', source_raw), ('receipt.json', receipt_raw), ('browser.json', browser_raw), ('requests.jsonl', journal)]:
            (stage/name).write_bytes(raw)
        for name, value in [('input.json', data), ('association.json', association), ('result.json', result)]:
            ts01.save(stage/name, value)
        captures.build(stage/'input.json', stage/'bundle', assessor='Automated synthetic rendered laboratory; no human review',
                       label='SYNTHETIC TS07 rendered import', selection_method='Explicit prefrozen laboratory states only',
                       access='synthetic', mode='automatic', selected=['TS07'])
        tsep.require(tsep.read_json(stage/'bundle/report.json')['results'][0]['status'] == result['status'], 'Bundle status mismatch')
        tsep.require(sources() == tsep.parse_json(receipt_raw)['source_files'], 'Tool changed during import')
        ts01.manifest(stage, FILES)
        output.mkdir(mode=0o700)
        try:
            for child in stage.iterdir():
                shutil.move(str(child), str(output/child.name))
        except BaseException:
            shutil.rmtree(output); raise
    return result


def replay(root):
    root = Path(root)
    tsep.require(set(ts01.verify(root)) == set(FILES), 'Incomplete rendered import manifest')
    source_raw, _ = read(root/'source.json'); receipt_raw, _ = read(root/'receipt.json'); _, envelope = read(root/'browser.json')
    data, association = derive(source_raw, receipt_raw, envelope, log_bytes(root/'requests.jsonl'))
    result = result_for(data)
    for name, value in [('input.json', data), ('association.json', association), ('result.json', result)]:
        tsep.require(tsep.read_json(root/name) == value, 'Replayed '+name+' differs')
    ts01.verify(root/'bundle')
    tsep.require(read(root/'bundle/input.json')[1] == data, 'Bundle input mismatch')
    report = tsep.read_json(root/'bundle/report.json')
    gate = tsep.validate(report, root/'bundle')
    tsep.require(tsep.read_json(root/'bundle/assessment.json') == result['atoms'], 'Replayed assessment differs')
    tsep.require(tsep.read_json(root/'bundle/gate.json') == gate and tsep.read_json(root/'bundle/earl.jsonld') == tsep.earl(report, gate), 'Replayed report derivatives differ')
    tsep.require(report['assessor']['name'] == 'Automated synthetic rendered laboratory; no human review'
                 and report['scope']['label'] == 'SYNTHETIC TS07 rendered import'
                 and report['assessor']['mode'] == 'automatic' and all(a['access'] == 'synthetic' for a in report['artifacts']), 'Synthetic report identity mismatch')
    atoms = [{k:v for k,v in a.items() if k != 'evidence_ids'} for a in report['results'][0]['atomic_results']]
    tsep.require(atoms == result['atoms'] and report['results'][0]['status'] == result['status'], 'Replayed report differs')
    tsep.require(sources() == tsep.parse_json(receipt_raw)['source_files'], 'Tool changed during replay')
    return {'same_results': True, 'network_requests': 0, 'status': result['status'], 'runtime': runtime_identity()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    prep = sub.add_parser('prepare'); prep.add_argument('source'); prep.add_argument('--output', required=True)
    imp = sub.add_parser('import'); imp.add_argument('source'); imp.add_argument('--receipt', required=True); imp.add_argument('--browser', required=True); imp.add_argument('--server-log', required=True); imp.add_argument('--output', required=True)
    rep = sub.add_parser('replay'); rep.add_argument('folder')
    args = parser.parse_args()
    try:
        if args.command == 'prepare': value = prepare(args.source, args.output)
        elif args.command == 'import': value = attach(args.source, args.receipt, args.browser, args.output, server_log=args.server_log)
        else: value = replay(args.folder)
        print(json.dumps(value, ensure_ascii=False, indent=2))
    except (ValueError, KeyError, TypeError, OSError) as error:
        parser.exit(1, str(error)+'\n')


if __name__ == '__main__':
    main()
