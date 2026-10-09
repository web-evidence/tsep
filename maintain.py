#!/usr/bin/env python3
"""Render/check the bilingual contract and build a deterministic release. Apache-2.0."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import zipfile
import tsep

ROOT = Path(__file__).resolve().parent


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
    return '\n'.join(lines)


def check():
    protocol = tsep.read_json(tsep.PROTOCOL_PATH)
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
    files = []
    for path in sorted(ROOT.rglob('*')):
        if path.is_file() and not any(p in ('__pycache__', '.git', '.DS_Store') for p in path.parts) \
                and path.suffix != '.pyc' and path.relative_to(ROOT).as_posix() != 'SHA256SUMS':
            tsep.require(not path.is_symlink(), 'Release must not contain symlinks')
            files.append(path)
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
        tsep.PROTOCOL_PATH.write_text(json.dumps(protocol, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        for lang in ('fr', 'en'):
            (ROOT / ('docs/controls.' + lang + '.md')).write_text(rendered(protocol, lang), encoding='utf-8')
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
