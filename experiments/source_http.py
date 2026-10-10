#!/usr/bin/env python3
"""Optional HTTP-source inventory 1; no TSEP or search-engine outcome. Apache-2.0."""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from experiments import source_tree as shared

PROFILE = 'html-http-utf8-v1'
CONTENT_TYPE = re.compile(r'[ \t]*text/html[ \t]*;[ \t]*charset[ \t]*=[ \t]*(?:utf-8|"utf-8")[ \t]*', re.I | re.ASCII)
MAX_BYTES = 8 * 1024 * 1024
MAX_OUTPUT = 32 * 1024 * 1024
TIMEOUT = 30
GROUPS = shared.GROUPS
need, sha = shared.need, shared.sha


class ProfileUnavailable(ValueError):
    def __init__(self, code, reason):
        super().__init__(reason)
        self.code = code


def decode(raw, content_types):
    """A bounded declared profile, not a general MIME parser or browser decoder."""
    if type(raw) is not bytes or len(raw) > MAX_BYTES:
        raise ProfileUnavailable('source-bound', 'Expected at most 8 MiB of decompressed body bytes')
    if (type(content_types) is not list or len(content_types) != 1 or
            type(content_types[0]) is not str or len(content_types[0]) > 4096 or
            not CONTENT_TYPE.fullmatch(content_types[0])):
        raise ProfileUnavailable('unsupported-content-type', 'One text/html Content-Type with only an explicit UTF-8 charset is required')
    if raw.startswith((b'\xff\xfe', b'\xfe\xff', b'\x00\x00\xfe\xff')):
        raise ProfileUnavailable('unsupported-bom', 'A non-UTF-8 BOM is outside this profile')
    bom = 3 if raw.startswith(b'\xef\xbb\xbf') else 0
    try:
        source = raw[bom:].decode('utf-8', errors='strict')
    except UnicodeDecodeError as error:
        raise ProfileUnavailable('invalid-utf8', 'Invalid UTF-8 is not replaced or reinterpreted') from error
    return source, {
        'profile': PROFILE, 'content_types': content_types, 'body_sha256': sha(raw),
        'body_bytes': len(raw), 'consumed_bom_bytes': bom,
        'parser_input_utf8_sha256': sha(source.encode('utf-8')),
        'parser_input_utf16_units': len(source.encode('utf-16-le')) // 2,
        'scope': 'Already decompressed body; one initial UTF-8 BOM consumed. No charset sniffing, newline normalization or invalid-byte replacement. HTTP origin and completeness are caller evidence, not proved by this decoder.'}


def identity(root=ROOT):
    need(Path(shared.__file__).resolve() == ROOT/'experiments/source_tree.py', 'Foreign shared supervisor')
    return dict(shared.identity(root), **{
        name: sha((root/name).read_bytes()) for name in
        ('experiments/source_http.py', 'experiments/source_http.mjs')})


def byte_positions(source, bom, positions):
    """Map only requested scalar boundaries in one pass, never split a surrogate."""
    need(all(type(p) is int and p >= 0 for p in positions), 'Invalid UTF-16 position')
    positions = set(positions)
    mapped = {0: bom} if 0 in positions else {}
    units, byte = 0, bom
    for character in source:
        units += 2 if ord(character) > 0xffff else 1
        byte += len(character.encode('utf-8'))
        if units in positions:
            mapped[units] = byte
    need(set(mapped) == positions, 'Offset outside input or inside a UTF-16 surrogate pair')
    return mapped


def validate_and_attribute(result, source, raw, decoding):
    need(result.get('kind') == 'unapplied-http-source-tree' and
         result.get('experiment_version') == '1' and result.get('normative_effect') == 'none', 'Unexpected reader identity')
    need(set(result['readings']) == {'enabled', 'disabled'}, 'Missing scripting hypothesis')
    located, errors = [], []
    for reading in result['readings'].values():
        need(type(reading['complete']) is bool and set(reading['inventory']) == set(GROUPS), 'Malformed inventory')
        need(reading['document_mode'] in ('no-quirks', 'limited-quirks', 'quirks') or
             (not reading['complete'] and reading['document_mode'] is None), 'Unknown document mode')
        containers = reading['template_containers']
        records = [r for rows in reading['inventory'].values() for r in rows]
        records += reading['template_signals'] + containers + reading['encoding_declarations']
        if not reading['complete']:
            need(not records and not reading['inventory_order'], 'Partial reading supplied records')
        for index, template in enumerate(containers):
            need(template['template_index'] == index, 'Template order differs')
            need(all(type(i) is int and 0 <= i < index for i in template['template_indices']), 'Invalid template ancestry')
            value = template['attributes'].get('shadowrootmode')
            folded = value.translate(str.maketrans('ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')) if value is not None else None
            expected = 'absent' if value is None else folded if folded in ('open', 'closed') else 'invalid'
            need(template['shadow_declaration'] == {'value': value, 'value_state': expected, 'attachment': 'not-assessed'}, 'Shadow declaration differs')
        for record in records:
            path = record['template_indices']
            need(all(type(i) is int and 0 <= i < len(containers) for i in path) and
                 len(path) == len(set(path)), 'Invalid template reference')
            for pos, index in enumerate(path):
                need(containers[index]['template_indices'] == path[:pos], 'Broken template path')
            need(record['context'] in ('head', 'body', 'other', 'template') and
                 (record['context'] == 'template') == bool(path), 'Template context differs')
            span = record['source_span_utf16']
            if span is None:
                need(record['raw_tag'] is None, 'Missing position has invented tag')
                record['body_span_bytes'] = None
            else:
                need(len(span) == 2 and all(type(v) is int for v in span) and span[0] < span[1], 'Invalid source span')
                located.append(record)
        for error in reading['parse_errors']:
            a, b = error.get('startOffset'), error.get('endOffset')
            if type(a) is int and type(b) is int and 0 <= a <= b:
                errors.append(error)
            else:
                error['body_span_bytes'] = None
    positions = {p for r in located for p in r['source_span_utf16']}
    positions.update(p for e in errors for p in (e['startOffset'], e['endOffset']))
    mapped = byte_positions(source, decoding['consumed_bom_bytes'], positions)
    for record in located:
        a, b = (mapped[p] for p in record['source_span_utf16'])
        need(raw[a:b].decode('utf-8') == record['raw_tag'], 'Raw tag does not match original body bytes')
        record['body_span_bytes'] = [a, b]
    for error in errors:
        error['body_span_bytes'] = [mapped[error['startOffset']], mapped[error['endOffset']]]
    ready = all(r['complete'] for r in result['readings'].values())
    # Byte attribution is deterministic and does not change equality between hypotheses.
    expected = {g: ('identical' if result['readings']['enabled']['inventory'][g] ==
                    result['readings']['disabled']['inventory'][g] else 'different')
                if ready else 'unavailable' for g in GROUPS}
    need(result['comparisons'] == expected, 'Inventory comparison differs')
    expected_extra = {g: ('identical' if result['readings']['enabled'][g] ==
                          result['readings']['disabled'][g] else 'different')
                      if ready else 'unavailable' for g in ('template_containers', 'template_signals', 'encoding_declarations')}
    need(result['supplementary_comparisons'] == expected_extra, 'Supplementary comparison differs')


def inventory(raw, *, content_types, node=None, root=ROOT):
    source, decoding = decode(raw, content_types)
    node = shutil.which(node or 'node')
    need(node is not None, 'Optional Node 24 runtime unavailable; no fallback reader')
    before = identity(root)
    dependencies = shared.packages(root)
    with tempfile.TemporaryDirectory(prefix='tsep-source-http-') as folder:
        work = Path(folder).resolve()
        for name, files in dependencies.items():
            for relative, data in files.items():
                destination = work/'node_modules'/name/relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(data)
        for name in ('source_http.mjs', 'source_tree_network_guard.mjs'):
            (work/name).write_bytes((root/'experiments'/name).read_bytes())
        (work/'source.bin').write_bytes(source.encode('utf-8'))
        command = [node, '--max-old-space-size=128', '--no-addons', '--disable-proto=throw',
                   '--disallow-code-generation-from-strings', '--permission',
                   '--allow-fs-read='+str(work), str(work/'source_http.mjs')]
        env = {k: v for k, v in os.environ.items() if not k.startswith('NODE_')}
        with (work/'stdout').open('wb') as out, (work/'stderr').open('wb') as err:
            try:
                completed = subprocess.run(command, cwd=work, env=env, stdin=subprocess.DEVNULL,
                                           stdout=out, stderr=err, timeout=TIMEOUT)
            except subprocess.TimeoutExpired as error:
                raise ValueError('HTTP source reader exceeded 30-second process deadline') from error
        with (work/'stderr').open('rb') as handle:
            error_text = handle.read(4096).decode('utf-8', errors='replace')
        need(completed.returncode == 0, 'HTTP source reader failed: '+error_text)
        with (work/'stdout').open('rb') as handle:
            output = handle.read(MAX_OUTPUT+1)
        need(len(output) <= MAX_OUTPUT, 'Source result byte bound exceeded')
        result = json.loads(output)
    need(identity(root) == before, 'Reader files changed during execution')
    need(result.get('parser_input_utf8_sha256') == decoding['parser_input_utf8_sha256'], 'Parser input identity differs')
    validate_and_attribute(result, source, raw, decoding)
    result['decoding'] = decoding
    result['source_sha256'] = before
    result['supervisor'] = {'python_version': sys.version.split()[0], 'process_timeout_seconds': TIMEOUT,
                            'node_old_space_mib': 128, 'output_byte_limit': MAX_OUTPUT}
    need(len(json.dumps(result, ensure_ascii=False).encode('utf-8')) <= MAX_OUTPUT, 'Attributed result byte bound exceeded')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('body', type=Path)
    parser.add_argument('--content-type', action='append', required=True, help='Each retained Content-Type value; repeat if repeated')
    parser.add_argument('--node')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        need(not args.output.exists(), 'Output already exists')
        with args.body.open('rb') as handle:
            raw = handle.read(MAX_BYTES+1)
        result = inventory(raw, content_types=args.content_type, node=args.node)
        with args.output.open('x', encoding='utf-8', newline='\n') as handle:
            json.dump(result, handle, ensure_ascii=False, indent=2); handle.write('\n')
        print(json.dumps({'kind': result['kind'], 'comparisons': result['comparisons'], 'normative_effect': 'none'}))
    except (ValueError, KeyError, TypeError, OSError) as error:
        print(json.dumps({'kind': 'experiment-unavailable', 'error_code': getattr(error, 'code', None),
                          'error': str(error), 'normative_effect': 'none'}), file=sys.stderr)
        return 64
    return 0


if __name__ == '__main__':
    sys.exit(main())
