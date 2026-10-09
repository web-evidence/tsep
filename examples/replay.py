#!/usr/bin/env python3
"""Generate deterministic synthetic reports, never collect a live site. Apache-2.0."""
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import tsep

ROOT = Path(__file__).resolve().parent
TARGET = 'https://example.com/page'
DATE = '2026-10-09T10:00:00Z'


def fixture(folder, name, kind, content):
    path = folder / name
    path.write_text(content, encoding='utf-8')
    return {'id': kind, 'path': name, 'sha256': tsep.digest(path), 'kind': kind,
            'observed_at': DATE, 'targets': [TARGET], 'access': 'synthetic',
            'description': 'Synthetic fixture; no real network observation / Cas synthétique.'}


def generate():
    result = []
    for case, status, state, http_status in [
            ('pass', 'C', 'complete', 200), ('fail', 'NC', 'complete', 404),
            ('partial', 'NT', 'inconclusive', None)]:
        folder = ROOT / case
        folder.mkdir(exist_ok=True)
        report = tsep.initialize([TARGET], ['TS01'], 'custom',
                                 'Synthetic fixture author / Auteur des cas fictifs',
                                 'One synthetic URL / Une URL fictive',
                                 'Controlled demonstration, not a live site assessment / Démonstration contrôlée')
        report['issued_at'] = DATE
        report['scope']['exclusions'] = ['All other controls and every live site / Autres contrôles et sites réels']
        report['artifacts'] = [fixture(folder, 'intent.txt', 'intent',
            'Synthetic case: this public canonical page is expected to return the declared content with final HTTP 200.\n'
            'Cas fictif : cette page publique canonique doit retourner le contenu attendu en HTTP 200 final.\n')]
        if http_status:
            report['artifacts'].append(fixture(folder, 'http.txt', 'http',
                'SYNTHETIC FIXTURE / CAS SYNTHÉTIQUE\nGET ' + TARGET + '\n'
                + 'Final URL: ' + TARGET + '\nHTTP/1.1 ' + str(http_status) + '\n'
                + 'Content-Type: text/html; charset=utf-8\nRedirects: 0\n\n'
                + ('Expected page content / Contenu attendu' if http_status == 200 else 'Not found / Introuvable') + '\n'))
        reasons = {
            'pass': 'Declared synthetic target returns expected content with final 200; no inference beyond TS01 / Cible fictive et contenu attendus en 200 final, TS01 seulement.',
            'fail': 'Declared public canonical target returns 404 instead of 200 / Cible publique canonique fictive en 404 au lieu de 200.',
            'partial': 'Request was not completed; there is no HTTP evidence and no compliance conclusion / Requête non aboutie, aucune preuve HTTP ni conclusion de conformité.'}
        report['results'] = [{'control_id': 'TS01', 'status': status, 'evaluation_state': state,
                              'reason': reasons[case],
                              'procedure': 'Read the synthetic exchange against the declared intention / Comparer échange fictif et intention',
                              'evaluated_targets': [TARGET],
                              'evidence_ids': [a['id'] for a in report['artifacts']]}]
        summary = tsep.validate(report, folder)
        (folder / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        (folder / 'expected.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        (folder / 'earl.jsonld').write_text(json.dumps(tsep.earl(report, summary), ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        result.append({'case': case, 'status': status, 'decision': summary['decision']})
    print(json.dumps({'synthetic': True, 'network_requests': 0, 'cases': result}, indent=2))


if __name__ == '__main__':
    generate()
