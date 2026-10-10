"""Local evidence-package I/O, without network or archive extraction. Apache-2.0."""
import json
from pathlib import Path, PurePosixPath
import re
import shutil

import tsep

MAX_FILES = 1024
MAX_FILE_BYTES = 32 * 1024 * 1024
MAX_PACKAGE_BYTES = 128 * 1024 * 1024


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def regular(path, limit=MAX_FILE_BYTES):
    path = Path(path)
    tsep.require(path.is_file() and not path.is_symlink(), 'Expected a regular file: '+str(path))
    with path.open('rb') as handle:
        raw = handle.read(limit+1)
    tsep.require(len(raw) <= limit, 'File exceeds workflow size bound')
    return raw


def inventory(root):
    root = Path(root)
    tsep.require(root.is_dir() and not root.is_symlink(), 'Expected a regular package directory')
    raw = regular(root/'SHA256SUMS', 256*1024)
    entries = {}
    total = 0
    for line in raw.decode('utf-8').splitlines():
        parts = line.split('  ', 1)
        tsep.require(len(parts) == 2, 'Malformed package manifest')
        digest, name = parts
        p = PurePosixPath(name)
        tsep.require(re.fullmatch('[a-f0-9]{64}', digest) and name not in entries
                     and name not in ('', '.', 'SHA256SUMS') and not p.is_absolute()
                     and '..' not in p.parts and p.as_posix() == name and '\\' not in name,
                     'Unsafe or duplicate package entry')
        tsep.require(len(entries) < MAX_FILES, 'Package file-count bound exceeded')
        path = tsep.evidence_path(root, name)
        payload = regular(path)
        total += len(payload)
        tsep.require(total <= MAX_PACKAGE_BYTES, 'Package byte bound exceeded')
        tsep.require(tsep.digest(path) == digest, 'Package integrity mismatch: '+name)
        entries[name] = digest
    tsep.require(entries, 'Empty package manifest')
    # Unknown files or symlink directories cannot hide outside the manifest.
    found = set()
    for index, path in enumerate(root.rglob('*')):
        tsep.require(index < MAX_FILES*4, 'Package directory-entry bound exceeded')
        tsep.require(not path.is_symlink(), 'Package symlink is unsupported')
        if path.is_file():
            found.add(path.relative_to(root).as_posix())
            tsep.require(len(found) <= MAX_FILES+1, 'Package file-count bound exceeded')
    tsep.require(found == set(entries) | {'SHA256SUMS'}, 'Unlisted or missing package files')
    return entries


def seal(root):
    root = Path(root)
    files = sorted(p for p in root.rglob('*') if p.is_file() and p != root/'SHA256SUMS')
    (root/'SHA256SUMS').write_text(''.join(tsep.digest(p)+'  '+p.relative_to(root).as_posix()+'\n'
                                       for p in files), encoding='utf-8')


def publish(stage, output):
    output = Path(output)
    tsep.require(output.parent.is_dir() and not output.exists() and not output.is_symlink(),
                 'Choose a NEW output directory with an existing parent')
    output.mkdir(mode=0o700)
    try:
        for path in sorted(Path(stage).rglob('*')):
            relative = path.relative_to(stage)
            if path.is_dir():
                (output/relative).mkdir(exist_ok=True)
            else:
                with (output/relative).open('xb') as handle:
                    handle.write(regular(path))
    except BaseException:
        shutil.rmtree(output)
        raise
    return output
