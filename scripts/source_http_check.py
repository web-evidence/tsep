#!/usr/bin/env python3
"""Opt-in Node qualification of bounded HTTP-source inventories. Apache-2.0."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from experiments import source_http


def fixture(name):
    path = ROOT/'tests/fixtures'/name
    raw = path.read_bytes()
    source_http.need(hashlib.sha256(raw).hexdigest() == path.with_suffix('.sha256').read_text().strip(), 'Changed fixture '+name)
    return json.loads(raw)


def projection(reading):
    return {
        'templates': [{'id':t['attributes'].get('id'), 'shadowrootmode':t['shadow_declaration']['value'],
                       'value_state':t['shadow_declaration']['value_state'], 'parent_tag':t['parent']['tag'],
                       'template_indices':t['template_indices']} for t in reading['template_containers']],
        'template_signal_paths': {s['attributes']['id']:s['template_indices'] for s in reading['template_signals']},
        'parse_error_codes': sorted({e['code'] for e in reading['parse_errors']}),
        'encoding_declaration_ids': [s['attributes'].get('id') for s in reading['encoding_declarations']]}


def check(node):
    rows = []
    for case in fixture('source-http-decoding-v1.json')['cases']:
        try:
            source, decoded = source_http.decode(bytes.fromhex(case['body_hex']), case['content_types'])
            actual = {'available':True, 'decoded':source, 'bom_bytes':decoded['consumed_bom_bytes']}
        except source_http.ProfileUnavailable as error:
            actual = {'available':False, 'error':error.code}
        rows.append({'group':'decoding', 'id':case['id'], 'expected':case['expected'], 'actual':actual, 'matches':actual == case['expected']})
    runtimes = []
    for case in fixture('source-http-tree-v1.json')['cases']:
        result = source_http.inventory(case['html'].encode(), content_types=['text/html; charset=utf-8'], node=node)
        if result['runtime'] not in runtimes: runtimes.append(result['runtime'])
        for mode, reading in result['readings'].items():
            actual = projection(reading)
            rows.append({'group':'templates', 'id':case['id'], 'mode':mode, 'expected':case['expected'][mode],
                         'actual':actual, 'matches':reading['complete'] and actual == case['expected'][mode]})
    for case in fixture('source-http-mode-v1.json')['cases']:
        result = source_http.inventory(case['html'].encode(), content_types=['text/html; charset=utf-8'], node=node)
        for mode, reading in result['readings'].items():
            expected = {'document_mode':case['expected_document_mode'], 'anchor_p_ancestor':case['expected_anchor_p_ancestor']}
            anchors = reading['inventory']['anchors']
            actual = {'document_mode':reading['document_mode'], 'anchor_p_ancestor':len(anchors) == 1 and 'p' in anchors[0]['ancestors']}
            rows.append({'group':'document-mode', 'id':case['id'], 'mode':mode, 'actual':actual, 'expected':expected,
                         'matches':reading['complete'] and actual == expected})
    return {'kind':'source-http-qualification', 'synthetic':True, 'normative_effect':'none',
            'source_sha256':source_http.identity(), 'runtimes':runtimes,
            'matched':sum(r['matches'] for r in rows), 'total':len(rows), 'rows':rows,
            'scope':'Authored finite expectations; Node actually invoked for 18 documents in both static hypotheses. Not browser/Google observations or TSEP outcomes.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--node', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    source_http.need(not args.output.exists(), 'Output already exists')
    result = check(args.node)
    with args.output.open('x', encoding='utf-8', newline='\n') as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2); handle.write('\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('rows', 'source_sha256')}))
    return 0 if result['matched'] == result['total'] else 1


if __name__ == '__main__':
    sys.exit(main())
