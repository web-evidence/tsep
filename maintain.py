#!/usr/bin/env python3
"""Render/check the bilingual contract and build a deterministic release. Apache-2.0."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys
import zipfile
import tsep

ROOT = Path(__file__).resolve().parent


def release_sources(root=ROOT):
    """Only explicit, reviewed regular files may enter a distribution."""
    manifest = tsep.read_json(root / 'release-files.json')
    tsep.require(set(manifest) == {'format_version', 'files'} and manifest['format_version'] == 1,
                 'Invalid release inventory')
    names = manifest['files']
    tsep.require(isinstance(names, list) and names and all(isinstance(n, str) for n in names),
                 'Release inventory must be a nonempty list of paths')
    tsep.unique(names, 'release path')
    tsep.require('release-files.json' in names, 'Distribution must contain its release inventory')
    files = []
    for name in names:
        relative = PurePosixPath(name)
        tsep.require(re.fullmatch(r'[A-Za-z0-9_./-]+', name) and not relative.is_absolute()
                     and '..' not in relative.parts and relative.as_posix() == name,
                     'Unsafe release path: ' + name)
        parts = [part.lower() for part in relative.parts]
        forbidden = {'.git', '.ssh', '.aws', '.codex', '.vscode', '.local', 'node_modules',
                     '__pycache__', 'sha256sums', '.tsep-local.json'}
        tsep.require(not any(part in forbidden or part.startswith('.env') for part in parts)
                     and relative.suffix.lower() not in ('.pem', '.key', '.p12', '.pfx', '.db', '.sqlite', '.sql'),
                     'Private or generated file forbidden in release: ' + name)
        path = root / name
        tsep.require(path.is_file(), 'Missing release file: ' + name)
        for parent in (path, *path.parents):
            if parent == root:
                break
            tsep.require(not parent.is_symlink(), 'Symlink forbidden in release: ' + name)
        tsep.require(root.resolve() in path.resolve().parents, 'Release path escapes root')
        files.append(path)
    return sorted(files)


def rendered(protocol, language):
    labels = {'en': ['Controls', 'Applicability', 'Method', 'Acceptance', 'Evidence',
                      'When NA is allowed', 'Limits', 'Required inputs', 'Severity', 'Unit',
                      'References', 'Source scope'],
              'fr': ['Contrôles', 'Applicabilité', 'Méthode', 'Attendus', 'Preuves',
                      'Conditions de NA', 'Limites', 'Entrées requises', 'Sévérité', 'Unité',
                      'Références', 'Portée des sources']}[language]
    lines = ['# TSEP ' + protocol['version'] + ' — ' + labels[0], '',
             'Generated from `spec/protocol.json` / Généré depuis `spec/protocol.json`.', '',
             'Draft / Version de travail. See / Voir [contract](contract.' + language + '.md).', '']
    for control in protocol['controls']:
        lines += ['## ' + control['id'] + ' — ' + control['title'][language], '',
                  '**' + labels[8] + '**: ' + control['severity'] + '. **' + labels[9]
                  + '**: ' + control['unit'] + '.', '',
                  '**' + labels[7] + '**: ' + ', '.join(control['required_inputs']) + '.', '']
        for key, index in [('applicability', 1), ('procedure', 2), ('acceptance', 3),
                           ('evidence', 4), ('non_applicability', 5), ('limitations', 6)]:
            lines += ['**' + labels[index] + '.** ' + control[key][language], '']
        lines += [control['acceptance_note'][language], '',
                  '**' + labels[11] + '.** ' + control['source_scope'][language], '']
        lines += ['**' + labels[10] + '**: ' + ('; '.join('[' + url + '](' + url + ')'
                              for url in control['references']) or 'TSEP / Edikka method.'), '']
        for rule in control.get('rules', []):
            lines += ['### ' + rule['id'] + ' — ' + rule['title'][language], '',
                      '`TSEP@' + control['rule_version'] + ':' + rule['id'] + '`', '',
                      '**' + labels[7] + '**: ' + ', '.join(rule['required_inputs']) + '.', '']
            if rule['na_inputs']:
                label = 'Entrées pour exemption atomique' if language == 'fr' else 'Atomic exemption inputs'
                lines += ['**' + label + '**: ' + ', '.join(rule['na_inputs']) + '.', '']
            fields = [('applicability', labels[1]), ('procedure', labels[2]),
                      ('acceptance', labels[3]), ('evidence', labels[4]),
                      ('assumptions', 'Hypothèses' if language == 'fr' else 'Assumptions'),
                      ('inconclusive', 'Indéterminé' if language == 'fr' else 'Inconclusive'),
                      ('non_applicability', labels[5]), ('limitations', labels[6])]
            for key, label in fields:
                lines += ['**' + label + '.** ' + rule[key][language], '']
    return '\n'.join(lines)


def check():
    release_sources()
    protocol = tsep.read_json(tsep.PROTOCOL_PATH)
    schema = tsep.read_json(ROOT/'schemas/report.schema.json')
    known_inputs = schema['properties']['artifacts']['items']['properties']['kind']['enum']
    tsep.require(schema['properties']['protocol']['properties']['version']['const'] == protocol['version'],
                 'Schema/protocol version mismatch')
    controls = protocol['controls']
    tsep.require([c['id'] for c in controls] == ['TS%02d' % n for n in range(1, 45)],
                 'Exactly TS01–TS44 required in order')
    fields = ['title', 'domain', 'applicability', 'procedure', 'acceptance',
              'non_applicability', 'evidence', 'limitations', 'acceptance_note', 'source_scope']
    for control in controls:
        for field in fields:
            tsep.require(set(control[field]) == {'fr', 'en'} and
                         all(isinstance(x, str) and x.strip() for x in control[field].values()),
                         'Missing bilingual text: ' + control['id'] + '.' + field)
        tsep.require(control['required_inputs'] and control['unit'], 'Missing contract inputs')
        if 'rules' in control:
            tsep.require(control['id'] in ('TS01', 'TS07', 'TS10') and control['rules'],
                         'Unexpected atomic rule scope')
            tsep.require(control['rule_version'] == protocol['version'], 'Stale atomic rule version')
            tsep.unique([r['id'] for r in control['rules']], 'atomic rule')
            for n, rule in enumerate(control['rules'], 1):
                tsep.require(rule['id'] == control['id'] + '-A%02d' % n, 'Unstable atomic ID')
                for field in ('title', 'applicability', 'procedure', 'acceptance', 'evidence',
                              'assumptions', 'inconclusive', 'non_applicability', 'limitations'):
                    tsep.require(set(rule[field]) == {'fr', 'en'} and
                                 all(isinstance(x, str) and x.strip() for x in rule[field].values()),
                                 'Missing bilingual atomic text: ' + rule['id'] + '.' + field)
                tsep.require(rule['required_inputs'] and
                             set(rule['required_inputs'] + rule['na_inputs']) <= set(known_inputs),
                             'Invalid atomic input kind')
    tsep.require({c['id'] for c in controls if 'rules' in c} == {'TS01', 'TS07', 'TS10'},
                 'Missing atomic control')
    for upstream in protocol['upstream']:
        tsep.require(tsep.digest(ROOT / upstream['path']) == upstream['sha256'],
                     'Historical source changed: ' + upstream['path'])
    for document in protocol['normative_documents']:
        tsep.require(tsep.digest(ROOT / document['path']) == document['sha256'],
                     'Normative document changed without rebinding: ' + document['path'])
    profiles = protocol['profiles']
    tsep.require([p['id'] for p in profiles] == ['TSEP-1','TSEP-2','TSEP-3'], 'Wrong profiles')
    known = {c['id'] for c in controls}
    previous = set()
    for profile in profiles:
        ids = set(profile['controls'])
        tsep.unique(profile['controls'], 'profile control')
        tsep.require(previous <= ids <= known, 'Invalid or non-nested profile')
        previous = ids
    tsep.require(previous == known, 'TSEP-3 must include all controls')
    for lang in ('fr', 'en'):
        file = ROOT / ('docs/controls.' + lang + '.md')
        tsep.require(file.read_text(encoding='utf-8') == rendered(protocol, lang),
                     'Stale generated documentation: ' + str(file))
    print(json.dumps({'controls': len(controls), 'languages': ['fr', 'en'],
                      'profiles': {p['id']: len(p['controls']) for p in profiles},
                      'upstream_hashes': 'verified'}))


def build(output):
    check()
    destination = Path(output).resolve()
    tsep.require(ROOT not in destination.parents, 'Archive output must be outside the package')
    tsep.require(not destination.exists(), 'Refusing to overwrite an existing release archive')
    files = release_sources()
    manifest = '\n'.join(tsep.digest(path) + '  ' + path.relative_to(ROOT).as_posix()
                         for path in files) + '\n'
    with zipfile.ZipFile(destination, 'x', compression=zipfile.ZIP_STORED) as archive:
        entries = [(p.relative_to(ROOT).as_posix(), p.read_bytes()) for p in files]
        entries.append(('SHA256SUMS', manifest.encode('utf-8')))
        for name, data in sorted(entries):
            info = zipfile.ZipInfo('tsep/' + name, (2026, 10, 9, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)
    print(json.dumps({'archive': str(destination), 'files': len(files) + 1,
                      'sha256': tsep.digest(destination)}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['render', 'check', 'build'])
    parser.add_argument('--output')
    args = parser.parse_args()
    if args.command == 'render':
        protocol = tsep.read_json(tsep.PROTOCOL_PATH)
        protocol['normative_documents'] = [{'path': name, 'sha256': tsep.digest(ROOT / name)}
            for name in ('schemas/report.schema.json', 'docs/contract.en.md', 'docs/contract.fr.md')]
        tsep.PROTOCOL_PATH.write_bytes((json.dumps(protocol, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))
        for lang in ('fr', 'en'):
            (ROOT / ('docs/controls.' + lang + '.md')).write_bytes(rendered(protocol, lang).encode('utf-8'))
    elif args.command == 'build':
        tsep.require(args.output, '--output is required')
        build(args.output)
    else:
        check()


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
