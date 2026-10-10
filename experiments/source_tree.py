#!/usr/bin/env python3
"""Optional static source-tree experiment; no TSEP verdicts. Apache-2.0."""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[1]
VERSION = '1'
MAX_BYTES = 8 * 1024 * 1024
MAX_OUTPUT = 32 * 1024 * 1024
TIMEOUT = 30
GROUPS = ('robots', 'canonical', 'anchors', 'bases')
PINNED_ARCHIVES = {
    'parse5': 'd94ec8606e3cef24b8ec001ac121df5d7938f015be69615da27b53a082f86832',
    'entities': '8e8b16388e19c12fc80f9f75f518a0f83d99428be6765a38f04c264a078cc25b',
}


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def packages(root=ROOT):
    """Verify the complete shipped archives and every regular member before use."""
    base = root/'third_party/source-tree'
    manifest = json.loads((base/'packages.json').read_bytes())
    need(manifest['format_version'] == 1, 'Unsupported package manifest')
    rows = manifest['packages']
    need([(x['name'], x['version']) for x in rows] ==
         [('parse5', '8.0.1'), ('entities', '8.0.0')], 'Unexpected parser dependencies')
    result = {}
    for row in rows:
        name = row['name']
        need(row['archive'] == name+'-'+row['version']+'.tgz', 'Unexpected archive path')
        raw = (base/row['archive']).read_bytes()
        need(len(raw) <= 1024*1024 and sha(raw) == row['sha256'] == PINNED_ARCHIVES[name],
             'Package archive changed')
        files, total = {}, 0
        with tarfile.open(fileobj=io.BytesIO(raw), mode='r:gz') as archive:
            for member in archive:
                path = PurePosixPath(member.name)
                need(member.isfile() and not member.issym() and not member.islnk(),
                     'Only regular package files are supported')
                need(path.parts[:1] == ('package',) and len(path.parts) > 1 and
                     not path.is_absolute() and '..' not in path.parts and
                     '\\' not in member.name and member.name == path.as_posix(),
                     'Unsafe package member')
                relative = '/'.join(path.parts[1:])
                need(relative not in files and relative in row['files'], 'Unexpected package member')
                total += member.size
                need(0 <= member.size <= 2*1024*1024 and total <= 8*1024*1024 and
                     len(files) < 200, 'Package extraction bound exceeded')
                data = archive.extractfile(member).read(member.size+1)
                need(len(data) == member.size and sha(data) == row['files'][relative],
                     'Package member changed')
                files[relative] = data
        need(set(files) == set(row['files']), 'Incomplete package archive')
        result[name] = files
    return result


def identity(root=ROOT):
    names = ['experiments/source_tree.py', 'experiments/source_tree.mjs',
             'experiments/source_tree_network_guard.mjs', 'third_party/source-tree/packages.json',
             'third_party/source-tree/parse5-8.0.1.tgz', 'third_party/source-tree/entities-8.0.0.tgz']
    return {name: sha((root/name).read_bytes()) for name in names}


def validate_projection(result, source):
    """Check source attribution and recompute comparisons outside Node."""
    need(result.get('kind') == 'unapplied-static-source-tree' and
         result.get('experiment_version') == VERSION and result.get('normative_effect') == 'none',
         'Unexpected experiment identity')
    need(set(result['readings']) == {'enabled', 'disabled'}, 'Missing source hypothesis')
    utf16 = source.encode('utf-16-le')
    for reading in result['readings'].values():
        need(type(reading['complete']) is bool and set(reading['inventory']) == set(GROUPS),
             'Malformed source inventory')
        records = [r for rows in reading['inventory'].values() for r in rows] + reading['template_signals']
        if not reading['complete']:
            need(not records, 'A partial reading must not supply signals')
        for record in records:
            need(record['context'] in ('head', 'body', 'other', 'template'), 'Unknown tree context')
            location = record['source_span_utf16']
            if location is None:
                need(record['raw_tag'] is None, 'Implicit node has invented source')
                continue
            start, end = location
            need(type(start) is int and type(end) is int and 0 <= start < end <= len(utf16)//2,
                 'Invalid UTF-16 source span')
            need(utf16[2*start:2*end].decode('utf-16-le') == record['raw_tag'], 'Source span differs')
    ready = all(r['complete'] for r in result['readings'].values())
    expected = {g: ('identical' if result['readings']['enabled']['inventory'][g] ==
                    result['readings']['disabled']['inventory'][g] else 'different')
                if ready else 'unavailable' for g in GROUPS}
    need(result['comparisons'] == expected, 'Source comparison differs')


def inventory(raw, *, encoding, node=None, root=ROOT):
    need(type(raw) is bytes and len(raw) <= MAX_BYTES, 'Source byte bound exceeded')
    need(encoding == 'utf-8', 'Explicit UTF-8 decoding declaration required')
    source = raw.decode('utf-8', errors='strict')  # Retains U+FEFF; never guesses HTTP encoding.
    node = shutil.which(node or 'node')
    need(node is not None, 'Optional Node 24 runtime unavailable; no fallback reader')
    before = identity(root)
    dependencies = packages(root)
    with tempfile.TemporaryDirectory(prefix='tsep-source-tree-') as folder:
        work = Path(folder).resolve()
        for name, files in dependencies.items():
            for relative, data in files.items():
                destination = work/'node_modules'/name/relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(data)
        for name in ('source_tree.mjs', 'source_tree_network_guard.mjs'):
            (work/name).write_bytes((root/'experiments'/name).read_bytes())
        (work/'source.bin').write_bytes(raw)
        command = [node, '--max-old-space-size=128', '--no-addons', '--disable-proto=throw',
                   '--disallow-code-generation-from-strings', '--permission',
                   '--allow-fs-read='+str(work), str(work/'source_tree.mjs')]
        # No ambient NODE_OPTIONS/NODE_PATH/preload or user package installation.
        env = {k: v for k, v in os.environ.items() if not k.startswith('NODE_')}
        with (work/'stdout').open('wb') as out, (work/'stderr').open('wb') as err:
            try:
                completed = subprocess.run(command, cwd=work, env=env, stdin=subprocess.DEVNULL,
                                           stdout=out, stderr=err, timeout=TIMEOUT)
            except subprocess.TimeoutExpired as error:
                raise ValueError('Source reader exceeded 30-second process deadline') from error
        with (work/'stderr').open('rb') as handle:
            error_text = handle.read(4096).decode('utf-8', errors='replace')
        need(completed.returncode == 0, 'Source reader failed: '+error_text)
        with (work/'stdout').open('rb') as handle:
            output = handle.read(MAX_OUTPUT+1)
        need(len(output) <= MAX_OUTPUT, 'Source result byte bound exceeded')
        result = json.loads(output)
    need(identity(root) == before, 'Reader files changed during execution')
    need(result.get('source_utf8_sha256') == sha(raw), 'Source identity differs')
    validate_projection(result, source)
    result['source_sha256'] = before
    result['supervisor'] = {'python_version': sys.version.split()[0], 'process_timeout_seconds': TIMEOUT,
                            'node_old_space_mib': 128, 'output_byte_limit': MAX_OUTPUT}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--encoding', choices=['utf-8'], required=True)
    parser.add_argument('--node', help='Optional Node 24 executable; otherwise node on PATH')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        need(not args.output.exists(), 'Output already exists')
        with args.source.open('rb') as handle:
            raw = handle.read(MAX_BYTES+1)
        result = inventory(raw, encoding=args.encoding, node=args.node)
        with args.output.open('x', encoding='utf-8', newline='\n') as handle:
            json.dump(result, handle, ensure_ascii=False, indent=2)
            handle.write('\n')
        print(json.dumps({'kind': result['kind'], 'comparisons': result['comparisons'],
                          'normative_effect': 'none'}))
    except (ValueError, KeyError, TypeError, OSError, tarfile.TarError) as error:
        print(json.dumps({'kind': 'experiment-unavailable', 'error': str(error),
                          'normative_effect': 'none'}), file=sys.stderr)
        return 64
    return 0


if __name__ == '__main__':
    sys.exit(main())
