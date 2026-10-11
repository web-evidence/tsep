#!/usr/bin/env python3
"""Explicit Node qualification of frozen authored JSON-LD cases; no TSEP verdict."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from experiments import jsonld_processing as reader


def fixture(name):
    path = ROOT / 'tests/fixtures' / name
    raw = path.read_bytes()
    digest = reader.sha(raw)
    reader.need(digest == path.with_suffix('.sha256').read_text().strip(),
                'Frozen expectations changed: ' + name)
    return reader.strict_json(raw), digest


def compare(cases, observation):
    reader.need(len(cases) == len(observation['documents']), 'Wrong observation population')
    checks = []
    for case, row in zip(cases, observation['documents']):
        reader.need(case['id'] == row['id'], 'Wrong observed document')
        differences = []
        for key, expected in case['expected'].items():
            actual = (sorted(set(n['code'] for n in row['notices']))
                      if key == 'notice_codes' else row[key])
            if actual != expected:
                differences.append({'field': key, 'expected': expected, 'actual': actual})
        checks.append({'id': case['id'], 'matches': not differences, 'differences': differences})
    return checks


def write(path, value):
    with path.open('x', encoding='utf-8', newline='\n') as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write('\n')


def qualify(node, output):
    reader.need(not output.exists() and not output.is_symlink(), 'Choose a new output directory')
    output.mkdir(parents=True)
    runs = []
    try:
        for name in ('jsonld-processing-v1.json', 'jsonld-processing-boundaries-v1.json'):
            cases, digest = fixture(name)
            request = {'documents': [dict(c['document'], id=c['id'], contexts=c['contexts'])
                                     for c in cases['cases']]}
            prefix = name.removesuffix('.json')
            write(output / (prefix + '-input.json'), request)
            observation = reader.observe(request, node=node)
            write(output / (prefix + '-observation.json'), observation)
            checks = compare(cases['cases'], observation)
            reader.replay(observation, node=node)
            runs.append({'fixture': name, 'sha256': digest, 'checks': checks,
                         'exact_replay': True, 'runtime': observation['runtime']})
    except (ValueError, KeyError, TypeError, OSError) as error:
        write(output / 'failure.json', {'reason': str(error), 'completed_runs': runs})
        raise
    result = {'kind': 'optional-jsonld-processing-qualification', 'normative_effect': 'none',
              'observed_at': datetime.now(timezone.utc).isoformat(),
              'source_sha256': reader.identity(), 'runs': runs,
              'cases': sum(len(r['checks']) for r in runs),
              'matched': sum(c['matches'] for r in runs for c in r['checks']),
              'scope': 'Actual processor executions over frozen authored documents; no HTML/browser observation, '
                       'Schema.org validation, visible facts, entity truth or TSEP outcome.'}
    write(output / 'qualification.json', result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--node', required=True)
    parser.add_argument('--output-dir', required=True, type=Path)
    args = parser.parse_args()
    try:
        result = qualify(args.node, args.output_dir)
        print(json.dumps({k: result[k] for k in ('kind', 'cases', 'matched')}))
        return 0 if result['cases'] == result['matched'] else 1
    except (ValueError, KeyError, TypeError, OSError) as error:
        print(json.dumps({'qualification': 'unavailable', 'reason': str(error)}), file=sys.stderr)
        return 64


if __name__ == '__main__':
    sys.exit(main())
