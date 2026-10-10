#!/usr/bin/env python3
"""Observation CLI for the shared robots reader. Apache-2.0; no control verdict."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import tsep
from conformance import evaluate, http, robots as core
from conformance.robots import (RFC, GOOGLE, GOOGLE_FIELDS, MAX_BYTES, MAX_PATH, MAX_LINES, MAX_RULES,
                                MAX_STEPS, LIMITATION, address, normalized, matches, need)
from provenance.runtime import loaded_sources
VERSION = '3'


def body_policy(body, target, product_token, profile):
    return core.body_policy(body, target, product_token, profile)


def google_status(status):
    return core.google_status(status)


def inspect_capture(data):
    result = core.inspect_capture(data)
    result['observation_cli_version'] = VERSION
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    sources = loaded_sources(ROOT, {'experiments/robots_policy.py': sys.modules[__name__],
                                    'conformance/evaluate.py': evaluate, 'conformance/http.py': http,
                                    'conformance/robots.py': core,
                                    'tsep.py': tsep, 'provenance/runtime.py': sys.modules['provenance.runtime']})
    raw = args.input.read_bytes()
    need(len(raw) <= 16*1024*1024, 'Experimental input size bound exceeded')
    data = json.loads(raw, object_pairs_hook=tsep.unique_object)
    need(isinstance(data, dict), 'Observation input must be an object')
    result = inspect_capture(data)
    result.update(input_sha256=hashlib.sha256(raw).hexdigest(), source_files=sources)
    with args.output.open('x', encoding='utf-8') as handle:
        handle.write(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'decision': result['decision'], 'output': str(args.output), 'scope': 'experimental observation only'}))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(64)
