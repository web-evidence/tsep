#!/usr/bin/env python3
"""Replay declared source mutations with unchanged marker criteria; no TSEP verdict."""
import argparse
import hashlib
import importlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import tsep
from experiments import noscript
from provenance.runtime import loaded_sources, runtime_identity

VERSION = '1'
need = tsep.require


def sources():
    modules = {name: importlib.import_module(name[:-3].replace('/', '.')) for name in noscript.SOURCE_FILES}
    modules['experiments/perturbations.py'] = sys.modules[__name__]
    return loaded_sources(ROOT, modules)


def read(path, limit):
    with Path(path).open('rb') as handle:
        raw = handle.read(limit+1)
    need(len(raw) <= limit, 'Input exceeds size limit')
    return raw


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def save(path, value):
    with path.open('x', encoding='utf-8', newline='\n') as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write('\n')


def mutate(source, edits):
    need(isinstance(edits, list) and len(edits) <= 8, 'Expected at most eight edits')
    last_end = -1
    for edit in edits:
        need(isinstance(edit, dict) and set(edit) == {'start', 'end', 'before', 'after'}, 'Invalid edit fields')
        start, end = edit['start'], edit['end']
        need(type(start) is int and type(end) is int and 0 <= start <= end <= len(source), 'Invalid Unicode source range')
        need(start > last_end, 'Edits must be ordered, separate and nonoverlapping')
        need(isinstance(edit['before'], str) and isinstance(edit['after'], str) and source[start:end] == edit['before'], 'Edit does not match original source')
        need(edit['before'] != edit['after'], 'No-op edit')
        last_end = end
    for edit in reversed(edits):
        source = source[:edit['start']] + edit['after'] + source[edit['end']:]
    need(len(source) <= noscript.MAX_CHARS, 'Mutated source exceeds experiment limit')
    return source


def run(source_path, criteria_path, plan_path, output):
    before = sources()
    raw = read(source_path, noscript.MAX_CHARS*4)
    source = raw.decode('utf-8')
    need(len(source) <= noscript.MAX_CHARS, 'Source exceeds experiment limit')
    criteria_raw = read(criteria_path, 1024*1024)
    criteria = json.loads(criteria_raw)
    noscript.validate_criteria(criteria)
    plan_raw = read(plan_path, 16*1024*1024)
    plan = json.loads(plan_raw)
    need(plan['format_version'] == 1 and plan['source_sha256'] == digest(raw) and
         plan['criteria_sha256'] == digest(criteria_raw), 'Plan/source/criteria binding mismatch')
    tsep.timestamp(plan['recorded_at'])
    cases = plan['cases']
    need(isinstance(cases, list) and 1 <= len(cases) <= 12, 'Expected one to twelve cases')
    prepared, ids = [], set()
    for case in cases:
        identifier = case['id']
        need(isinstance(identifier, str) and re.fullmatch('[a-z][a-z0-9-]{0,63}', identifier) and identifier not in ids, 'Invalid/duplicate case ID')
        ids.add(identifier)
        need(all(isinstance(case[k], str) and 0 < len(case[k]) <= 4096 for k in ('label', 'explanation')), 'Invalid case description')
        changed = mutate(source, case['edits'])
        need(type(case['synthetic']) is bool and case['synthetic'] == bool(case['edits']), 'Synthetic label must match declared edits')
        expected = case['expected']
        need(isinstance(expected, dict) and set(expected) == {'enabled', 'disabled', 'consensus'} and
             all(x in ('pass', 'fail', 'inconclusive') for x in expected.values()), 'Invalid authored expectations')
        prepared.append((case, changed))
    output = Path(output)
    need(not output.exists() and not output.is_symlink() and output.parent.is_dir(), 'Use a new output directory with an existing parent')
    output.mkdir(mode=0o700)
    rows, files = [], []
    for case, changed in prepared:
        result = noscript.experiment(changed, criteria)
        actual = {mode: result['readings'][mode]['markers']['candidate'] for mode in ('enabled', 'disabled')}
        actual['consensus'] = result['candidate_consensus']
        body = changed.encode('utf-8')
        need(result['source_utf8_sha256'] == digest(body), 'Experiment/body binding mismatch')
        body_name, result_name = case['id']+'.source.txt', case['id']+'.result.json'
        with (output/body_name).open('xb') as handle:
            handle.write(body)
        save(output/result_name, result)
        files.extend((body_name, result_name))
        rows.append({'id': case['id'], 'label': case['label'], 'explanation': case['explanation'],
                     'synthetic': case['synthetic'], 'edits': case['edits'], 'expected': case['expected'],
                     'actual': actual, 'matches_authored_expectations': actual == case['expected'],
                     'source_file': body_name, 'result_file': result_name, 'source_sha256': digest(body),
                     'result_sha256': tsep.digest(output/result_name), 'source_bytes': len(body)})
    need(sources() == before, 'Sources changed during execution; outputs retained')
    summary = {'kind': 'unapplied-source-perturbations', 'version': VERSION, 'normative_effect': 'none',
               'source_sha256': digest(raw), 'criteria_sha256': digest(criteria_raw), 'plan_sha256': digest(plan_raw),
               'criteria': criteria, 'source_files': before, 'runtime': runtime_identity(), 'cases': rows,
               'all_expectations_matched': all(r['matches_authored_expectations'] for r in rows),
               'network_requests': 0, 'scope': 'Declared local source mutations and authored expectations. No HTTP capture, browser rendering, functional test, independent oracle or normative promotion.'}
    save(output/'results.json', summary)
    files.append('results.json')
    with (output/'SHA256SUMS').open('x') as handle:
        handle.write(''.join(tsep.digest(output/name)+'  '+name+'\n' for name in sorted(files)))
    return summary


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('source', 'criteria', 'plan', 'output'):
        p.add_argument('--'+name, type=Path, required=True)
    args = p.parse_args()
    try:
        result = run(args.source, args.criteria, args.plan, args.output)
        print(json.dumps({'cases': len(result['cases']), 'all_expectations_matched': result['all_expectations_matched'], 'normative_effect': 'none'}))
        return 0 if result['all_expectations_matched'] else 1
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(json.dumps({'error': str(error)}), file=sys.stderr)
        return 64


if __name__ == '__main__':
    sys.exit(main())
