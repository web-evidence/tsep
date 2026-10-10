#!/usr/bin/env python3
"""Canonical record comparison candidate 1, NEVER a TSEP verdict. Apache-2.0."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import tsep
from experiments import rendered_metadata as metadata
from provenance import runtime

VERSION = '1'
INTENT_KEYS = {'format', 'version', 'mode', 'state_label', 'document_url',
               'preferred_url', 'html_canonical_required', 'known_integrity_issues',
               'record_sha256'}
MODES = ('authored-synthetic', 'retrospective')
C0_SPACE = ''.join(chr(i) for i in range(33))
LIMITATIONS = [
    'Experimental record comparison only; no TSEP outcome or search-engine inference',
    'Raw strings compared exactly; no URL equivalence or normalization',
    'DOM APIs, operator, named state and execution are not authenticated',
    'Coherently fabricated agreement or contradiction can evade these checks',
    'One recorded state only; complete traversal is not temporal stability',
    'HTTP Link, source HTML, robots, other states and URL families not assessed',
    'Frame documents, template fragments and closed shadow roots not assessed',
    'Page and extension origin unknown; no elements filtered by identity',
]


def encoded(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(',', ':'), allow_nan=False).encode('utf-8')


def digest(value):
    """Digest of the documented JSON representation, not original file bytes."""
    return hashlib.sha256(encoded(value)).hexdigest()


def sources():
    values = runtime.loaded_sources(ROOT, {
        'experiments/rendered_canonical.py': sys.modules[__name__],
        'experiments/rendered_metadata.py': metadata,
        'provenance/runtime.py': runtime, 'tsep.py': tsep})
    values[metadata.SCRIPT] = metadata.script_digest()
    return values


def supported_url(value):
    """Deliberately narrow reference syntax, not a Web URL validity test."""
    if not isinstance(value, str) or not value or len(value) > 4096:
        return False
    if re.search(r'[^\x21-\x7e]|[\\#<>"`{}|^]', value) or re.search(r'%(?![0-9a-fA-F]{2})', value):
        return False
    if not re.match(r'^https?://', value, re.I):
        return False
    try:
        parts = urlsplit(value)
        if not re.fullmatch(r'[A-Za-z0-9.-]+(?::[0-9]{1,5})?', parts.netloc):
            return False
        host = parts.hostname
        if not host or len(host) > 253 or any(not re.fullmatch(
                r'[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?', label)
                for label in host.split('.')):
            return False
        return parts.port is None or 1 <= parts.port <= 65535
    except ValueError:
        return False


def validate_intent(intent):
    if intent is None:
        return
    tsep.require(isinstance(intent, dict) and set(intent) == INTENT_KEYS, 'Invalid intent fields')
    tsep.require(intent['format'] == 'rendered-canonical-intent' and intent['version'] == VERSION
                 and intent['mode'] in MODES, 'Unsupported candidate intent contract/mode')
    for key in ('state_label', 'document_url', 'preferred_url', 'record_sha256'):
        tsep.require(intent[key] is None or isinstance(intent[key], str) and len(intent[key]) <= 4096,
                     'Invalid intent string: ' + key)
    tsep.require(intent['record_sha256'] is None or
                 re.fullmatch('[0-9a-f]{64}', intent['record_sha256']), 'Invalid record digest')
    tsep.require(intent['html_canonical_required'] is None or
                 type(intent['html_canonical_required']) is bool, 'Invalid presence requirement')
    issues = intent['known_integrity_issues']
    tsep.require(issues is None or isinstance(issues, list) and len(issues) <= 64 and
                 all(isinstance(x, str) and x.strip() and len(x) <= 4096 for x in issues),
                 'Invalid known integrity issues')


def http_prefix(raw):
    # Only classify a possible HTTP(S) prefix; never substitute this string in
    # either comparison. This is not a URL parser or equivalence calculation.
    probe = raw.strip(C0_SPACE).translate({9: None, 10: None, 13: None})
    return re.match(r'^https?://', probe, re.I) is not None


def assess(record, intent):
    """Interpret only the supplied record; preserve guards, diagnostics and scope."""
    tsep.require(isinstance(record, dict) and set(record) == {'script_sha256', 'tree'},
                 'Invalid snapshot fields')
    tsep.require(record['script_sha256'] == metadata.script_digest(), 'Different capture script')
    inventory = metadata.inventory(record['tree'])
    validate_intent(intent)
    record_hash = digest(record)
    tree = record['tree']
    guards = []
    if intent is None:
        guards.append('missing-intent')
    else:
        binding = intent['record_sha256']
        if binding is None:
            guards.append('missing-record-binding')
        elif binding != record_hash:
            guards.append('record-binding-mismatch')
        if not intent['state_label'] or not intent['state_label'].strip():
            guards.append('missing-state-label')
        if not supported_url(intent['document_url']):
            guards.append('unsupported-document-url')
        elif intent['document_url'] != tree['document_url']:
            guards.append('document-url-mismatch')
        if not supported_url(intent['preferred_url']):
            guards.append('unsupported-preferred-url')
        if intent['html_canonical_required'] is None:
            guards.append('missing-requirement')
        if intent['known_integrity_issues'] is None:
            guards.append('unknown-integrity-history')
        elif intent['known_integrity_issues']:
            guards.append('known-integrity-issue')
    if tree['api_errors']:
        guards.append('api-error')
    roots = [n['id'] for n in tree['nodes'] if n['type'] == 1 and n['parent'] == 0
             and n['namespace'] == metadata.HTML and n['name'] == 'html']
    heads = [n['id'] for n in tree['nodes'] if n['type'] == 1 and n['parent'] in roots
             and n['namespace'] == metadata.HTML and n['name'] == 'head']
    if len(heads) != 1:
        guards.append('ambiguous-document-head')

    signals = [x for x in inventory['metadata'] if x['kind'] == 'canonical']
    ordinary = [x for x in signals if x['position'] != 'open-shadow']
    shadow = [x for x in signals if x['position'] == 'open-shadow']
    diagnostics = []
    preferred = intent['preferred_url'] if intent is not None else None
    for signal in signals:
        raw, resolved = signal['raw_href'], signal['resolved_href']
        if resolved is None:
            guards.append('missing-resolved-href')
        elif raw is not None and http_prefix(raw) and raw != resolved:
            guards.append('absolute-raw-resolved-difference')
        if signal['position'] == 'open-shadow' or not supported_url(preferred):
            continue
        reason = ('raw-href-missing' if raw is None else 'raw-href-empty' if raw == ''
                  else 'raw-href-differs' if raw != preferred else None)
        if reason:
            diagnostics.append({'node_id': signal['node_id'], 'reason': reason,
                                'raw_href': raw, 'preferred_url': preferred,
                                'position': signal['position'], 'path': signal['path']})
    gaps = []
    if tree['ready_state'] == 'loading':
        gaps.append('document-parse-incomplete')
    if not tree['traversal_complete']:
        gaps.append('incomplete-tree')
    if any(x['position'] != 'head-direct' for x in ordinary):
        gaps.append('ambiguous-placement')
    if shadow:
        gaps.append('shadow-canonical')
    if guards:
        outcome, reasons = 'undetermined', guards
    elif diagnostics:
        outcome, reasons = 'contradiction-in-record', [x['reason'] for x in diagnostics]
    elif gaps:
        outcome, reasons = 'undetermined', gaps
    elif not signals:
        if intent['html_canonical_required']:
            outcome, reasons = 'contradiction-in-record', ['required-canonical-absent']
        else:
            outcome, reasons = 'no-declaration-in-record', ['optional-canonical-absent']
    else:
        outcome, reasons = 'agreement-in-record', ['exact-declarations-match']
    return copy.deepcopy({
        'kind': 'experimental-rendered-canonical-comparison', 'version': VERSION,
        'normative': False, 'outcome': outcome, 'reasons': list(dict.fromkeys(reasons)),
        'guards': list(dict.fromkeys(guards)), 'coverage_gaps': gaps,
        'mode': intent['mode'] if intent is not None else None,
        'intent': intent, 'record_sha256': record_hash,
        'script_sha256': record['script_sha256'],
        'coverage': {'traversal_complete': tree['traversal_complete'],
                     'stop_reason': tree['stop_reason'], 'ready_state': tree['ready_state'],
                     'closed_shadow': 'unknown', 'frame_documents': 'not-collected',
                     'template_fragments': 'not-collected', 'api_authenticity': 'not-established'},
        'diagnostics': diagnostics, 'canonical': signals,
        'other_metadata': [x for x in inventory['metadata'] if x['kind'] != 'canonical'],
        'boundaries': inventory['boundaries'], 'api_errors': tree['api_errors'],
        'limits': LIMITATIONS,
    })


def read_input(path, limit):
    with Path(path).open('rb') as stream:
        raw = stream.read(limit + 1)
    tsep.require(len(raw) <= limit, 'Input file bound')

    def pairs(items):
        value = {}
        for key, entry in items:
            tsep.require(key not in value, 'Duplicate JSON member: ' + key)
            value[key] = entry
        return value

    def nonfinite(value):
        raise ValueError('Non-finite JSON value: ' + value)

    return json.loads(raw, object_pairs_hook=pairs, parse_constant=nonfinite), hashlib.sha256(raw).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('snapshot')
    parser.add_argument('--intent', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    try:
        before = sources()
        record, record_file_hash = read_input(args.snapshot, 4 * 1024 * 1024)
        intent, intent_file_hash = read_input(args.intent, 64 * 1024)
        result = assess(record, intent)
        result.update(input_files_sha256={'snapshot': record_file_hash, 'intent': intent_file_hash},
                      source_files_sha256=before)
        tsep.require(sources() == before, 'Candidate sources changed during interpretation')
        with Path(args.output).open('x', encoding='utf-8') as stream:
            json.dump(result, stream, ensure_ascii=False, indent=2, allow_nan=False)
            stream.write('\n')
        return 0
    except (ValueError, KeyError, TypeError, OSError, RecursionError) as error:
        print(str(error), file=sys.stderr)
        return 64


if __name__ == '__main__':
    sys.exit(main())
