#!/usr/bin/env python3
"""Closed historical runtime distributions, version 1. Apache-2.0.

No normative evaluation or collection. No source or native-report rewriting.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
import zipfile

sys.dont_write_bytecode = True
VERSION = '1'
DEFINITIONS_SHA256 = 'd365bdcd67ec436024b2707605dde533c0273ee85fe8aa67eaf611417691b334'
MAX_FILES = 2048
MAX_FILE_BYTES = 16 * 1024 * 1024
MAX_TOTAL_BYTES = 128 * 1024 * 1024
README = '''TSEP runtime distribution 1 / Distribution d'exécution TSEP 1

EN: This is an explicitly reduced historical distribution, not a complete source
archive. The unchanged engine files retain their original identity. Exactly one
non-runtime historical diagnostic is absent; its name, digest and bilingual reason
are in runtime-profiles.json. The full source inventory
in runtime-profiles.json is the origin reference. runtime/release-files.json and
runtime/SHA256SUMS, when present in the historical import, remain historical
references, not inventories of this reduced tree. Use the separate
closed runtime inventory in distribution.json and the verifier below. Full-source
maintain check/build and scripts/verify.py are unsupported on this reduced tree.
Historical native reports and runtime fingerprints must not be rewritten. A new
transport receipt identifies this distribution in addition to the original engine.
No real Google/Edikka observation, certification or author authentication is implied.

FR : Distribution historique explicitement réduite, pas une archive source complète.
Les octets du moteur et son identité initiale sont conservés. Un seul diagnostic
historique non exécutable est absent ; nom, empreinte et raison bilingue figurent
dans runtime-profiles.json. L'inventaire
complet de runtime-profiles.json est la référence d'origine. release-files.json
et SHA256SUMS, si présent dans l'import historique, restent des références
historiques, pas des inventaires de cet arbre réduit. Utiliser
l'inventaire fermé de distribution.json et son vérificateur. Les commandes source
complète maintain check/build et scripts/verify.py ne s'appliquent pas à cet arbre.
Ne pas réécrire les anciens rapports natifs ni leurs empreintes moteur. Un nouveau
reçu de transport identifie cette distribution en plus du moteur original.
Aucun constat Google/Edikka réel, certification ou authentification d'auteur déduit.

Check / Vérifier : python3 -I -B runtime_distribution.py check --root .
Run native tools from runtime/ only after a successful check. Execute historical
replay with its original anchor; a new assessment is a distinct operation.
Exécuter les outils natifs de runtime/ après vérification ; garder l'ancre historique
du rejeu. Une nouvelle évaluation reste une opération distincte.

Verify the whole archive digest against an independently trusted delivery before
running any included code. Internal hashes prove consistency only. Modifying the
checker and all its claims is outside this self-consistency check's trust boundary.
Comparer l'empreinte de l'archive à une livraison de confiance avant exécution.
Les empreintes internes établissent une cohérence, pas une origine authentifiée.
'''


class Invalid(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise Invalid(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encode(value):
    return (json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True) + '\n').encode('ascii')


def inventory_digest(value):
    return digest(json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(',', ':')).encode('ascii'))


def safe_name(name):
    require(isinstance(name, str) and name and len(name) <= 240, 'Invalid relative name')
    require(re.fullmatch(r'[A-Za-z0-9_.\-/]+', name) is not None, 'Noncanonical relative name')
    require(all(x not in ('', '.', '..') for x in name.split('/')), 'Noncanonical relative path')
    return name


def regular_bytes(path):
    before = path.lstat()
    require(stat.S_ISREG(before.st_mode) and before.st_size <= MAX_FILE_BYTES, 'Expected bounded regular file')
    fd = os.open(path, os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0))
    with os.fdopen(fd, 'rb') as stream:
        opened = os.fstat(stream.fileno())
        raw = stream.read(MAX_FILE_BYTES + 1)
        after = os.fstat(stream.fileno())
    def identity(s):
        return s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns
    require(identity(before) == identity(opened) == identity(after) == identity(path.lstat()), 'File changed while reading')
    require(len(raw) == before.st_size, 'Unstable or oversized input')
    return raw


def snapshot(root, expected):
    root = Path(root)
    require(stat.S_ISDIR(root.lstat().st_mode), 'Expected a real directory')
    require(0 < len(expected) <= MAX_FILES, 'Invalid file count')
    allowed_dirs = set()
    for name in expected:
        safe_name(name)
        allowed_dirs.update('/'.join(name.split('/')[:i]) for i in range(1, len(name.split('/'))))
    actual = set()
    for parent, dirs, names in os.walk(root, followlinks=False):
        for name in dirs:
            path = Path(parent) / name
            rel = path.relative_to(root).as_posix()
            require(rel in allowed_dirs and stat.S_ISDIR(path.lstat().st_mode), 'Unexpected or symbolic directory')
        for name in names:
            rel = (Path(parent) / name).relative_to(root).as_posix()
            safe_name(rel)
            actual.add(rel)
            require(len(actual) <= MAX_FILES, 'Excess file count')
    require(actual == set(expected), 'Missing, extra or excluded file')
    result = {}
    total = 0
    for name, value in expected.items():
        require(re.fullmatch('[0-9a-f]{64}', value) is not None, 'Invalid expected digest')
        raw = regular_bytes(root / name)
        total += len(raw)
        require(total <= MAX_TOTAL_BYTES, 'Excess total bytes')
        require(digest(raw) == value, 'File digest mismatch: ' + name)
        result[name] = raw
    return result


def definitions_path():
    here = Path(__file__).resolve().parent
    local = here / 'runtime-profiles.json'
    return local if local.exists() else here.parent / 'distribution/runtime-profiles.json'


def definitions():
    raw = regular_bytes(definitions_path())
    require(digest(raw) == DEFINITIONS_SHA256, 'Closed profile definitions changed')
    value = json.loads(raw)
    require(value['version'] == VERSION, 'Unknown profile version')
    return raw, value['closed_profiles']


def select_profile(profile_id):
    raw, profiles = definitions()
    selected = [p for p in profiles if p['id'] == profile_id]
    require(len(selected) == 1, 'Unknown closed profile')
    profile = selected[0]
    require(inventory_digest(profile['full_source_files']) == profile['source_inventory_sha256'], 'Source inventory contradiction')
    return raw, profile


def excluded_names(profile):
    return set(profile['excluded'])


def package_metadata(profile_id):
    raw, p = select_profile(profile_id)
    retained = {n: h for n, h in p['full_source_files'].items() if n not in excluded_names(p)}
    payload = {
        'runtime-profiles.json': raw,
        'runtime_distribution.py': regular_bytes(Path(__file__)),
        'RUNTIME-DISTRIBUTION.txt': README.encode('utf-8'),
    }
    included = {'runtime/' + n: h for n, h in retained.items()}
    included.update({n: digest(b) for n, b in payload.items()})
    descriptor = {
        'kind': 'tsep-closed-runtime-distribution', 'version': VERSION,
        'profile_id': profile_id, 'protocol_version': p['protocol_version'],
        'source_commit': p['source_commit'],
        'full_source_inventory_sha256': p['source_inventory_sha256'],
        'runtime_inventory_sha256': inventory_digest(retained),
        'profile_definitions_sha256': DEFINITIONS_SHA256,
        'excluded_files': p['excluded'],
        'original_inventory_role': 'Full source map in runtime-profiles.json; runtime/release-files.json and any runtime/SHA256SUMS are historical references, not included-tree inventories',
        'files': included,
    }
    payload['distribution.json'] = encode(descriptor)
    return p, retained, payload, descriptor


def build(source, output, profile_id):
    source = Path(source)
    output = Path(output)
    require(output.resolve() != source.resolve() and source.resolve() not in output.resolve().parents, 'Output must be outside source tree')
    p, retained, payload, descriptor = package_metadata(profile_id)
    raw = snapshot(Path(source), p['full_source_files'])
    payload.update({'runtime/' + n: raw[n] for n in retained})
    output = Path(output)
    # Exclusive creation; never replace a historical source or delivered archive.
    with output.open('xb') as stream:
        with zipfile.ZipFile(stream, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for name in sorted(payload):
                info = zipfile.ZipInfo(name, date_time=(2020, 1, 1, 0, 0, 0))
                info.create_system = 3
                info.external_attr = (stat.S_IFREG | 0o644) << 16
                info.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(info, payload[name], compresslevel=9)
    return {'profile_id': profile_id, 'archive_sha256': digest(regular_bytes(output)),
            'runtime_files': len(retained), 'package_files': len(payload),
            'distribution_sha256': digest(payload['distribution.json']),
            'runtime_inventory_sha256': descriptor['runtime_inventory_sha256']}


def check(root):
    root = Path(root)
    # Read only the bounded descriptor to choose one compiled-in closed profile.
    descriptor_raw = regular_bytes(root / 'distribution.json')
    supplied = json.loads(descriptor_raw)
    p, retained, payload, expected = package_metadata(supplied.get('profile_id'))
    require(descriptor_raw == payload['distribution.json'], 'Distribution descriptor contradiction')
    inventory = dict(expected['files'], **{'distribution.json': digest(descriptor_raw)})
    snapshot(root, inventory)
    return {'success': True, 'profile_id': p['id'], 'runtime_files': len(retained),
            'package_files': len(inventory), 'distribution_sha256': digest(descriptor_raw),
            'runtime_inventory_sha256': expected['runtime_inventory_sha256'],
            'scope': 'Closed byte consistency only; not a native replay, normative outcome or authentication'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    builder = sub.add_parser('build')
    builder.add_argument('--source', type=Path, required=True)
    builder.add_argument('--output', type=Path, required=True)
    builder.add_argument('--profile', required=True)
    checker = sub.add_parser('check')
    checker.add_argument('--root', type=Path, required=True)
    args = parser.parse_args()
    try:
        result = build(args.source, args.output, args.profile) if args.command == 'build' else check(args.root)
        print(json.dumps(result, ensure_ascii=True, sort_keys=True))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        # No host path or raw input diagnostics in portable errors.
        message = str(error) if isinstance(error, Invalid) else 'Unreadable or invalid distribution input'
        print(json.dumps({'success': False, 'error': message}), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
