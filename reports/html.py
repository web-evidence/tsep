"""Self-contained, read-only presentation of validated TSEP reports. Apache-2.0.

No network, JavaScript, HTML capture execution or new assessment. All outcomes
come from the supplied reports; integrity is checked again before embedding bytes.
"""
import base64
import hashlib
from html import escape
import json
from pathlib import Path

import tsep
from conformance.http import raw_bytes

VERSION = '2'
MAX_EMBED_BYTES = 32 * 1024 * 1024  # Per report, including all evidence and JSON.
ROOT = Path(__file__).resolve().parent

TEXT = {
    'fr': {
        'title': 'Rapport de preuves', 'subtitle': 'Des observations aux décisions, chaque résultat conserve ses preuves.',
        'offline': 'Document autonome · hors ligne', 'draft': 'Protocole expérimental',
        'overview': 'Vue d’ensemble', 'comparison': 'Comparaison', 'results': 'Résultats',
        'captures': 'Captures et intention', 'evidence': 'Pièces de preuve', 'method': 'Périmètre et méthode',
        'decision': 'Décision dans le périmètre', 'controls': 'Contrôles sélectionnés', 'targets': 'Cibles déclarées',
        'scope_only': 'La décision concerne uniquement les contrôles et les cibles déclarés.',
        'not_evaluated': 'contrôles hors sélection', 'artifact_count': 'pièces liées au rapport',
        'valid': 'Structure et empreintes vérifiées à la génération',
        'integrity_limit': 'Cette vérification établit la cohérence du rapport et l’intégrité des fichiers lus. Elle ne prouve ni leur authenticité, ni la justesse des jugements, ni l’indexation ou le classement.',
        'synthetic': 'Preuves synthétiques présentes', 'synthetic_note': 'Au moins une pièce est déclarée synthétique. Ce rapport ne doit pas être présenté comme un constat entièrement issu d’un site réel.',
        'restricted': 'Pièces déclarées restreintes incluses', 'restricted_note': 'Ce fichier autonome contient aussi les pièces restreintes du rapport. Conserver leurs restrictions d’accès lors de son partage.',
        'before': 'Rapport précédent', 'after': 'Rapport actuel', 'same_input': 'Même fichier de captures fourni',
        'same_input_note': 'Les deux rapports lient un fichier d’entrée fourni dont les octets sont identiques. Les résultats ci-dessous sont ceux des rapports conservés ; cet affichage ne réévalue pas les captures.',
        'other_input': 'Identité des captures non établie',
        'other_input_note': 'Les contrôles et cibles déclarés correspondent, mais aucun fichier d’entrée identique n’est établi. Ne pas attribuer les écarts au seul changement d’outil.',
        'rule': 'Règle', 'target': 'Cible', 'result': 'Résultat', 'reason': 'Motif conservé',
        'missing': 'Aucune observation fournie', 'changed': 'résultats atomiques différents',
        'assessor': 'Évaluateur déclaré', 'tool': 'Outil déclaré', 'issued': 'Émission du rapport',
        'mode': 'Mode d’évaluation', 'not_supplied': 'Non fourni', 'protocol': 'Protocole',
        'report_hash': 'SHA-256 du rapport JSON', 'download_report': 'Télécharger le rapport JSON original',
        'control_reason': 'Conclusion du contrôle', 'procedure': 'Procédure déclarée',
        'expectation': 'Attendu de la règle', 'limits': 'Limites de la règle', 'automation': 'Automatisation',
        'inputs': 'Types de preuve requis', 'linked': 'Preuves liées', 'unobserved': 'Observations absentes',
        'unobserved_note': 'Ces couples règle/cible ne figurent pas dans le rapport ; aucune réussite n’est ajoutée.',
        'intent': 'Intention préalable fournie', 'declared': 'Date de déclaration',
        'expected_url': 'URL finale attendue', 'expected_hash': 'Empreinte du corps attendue',
        'representation': 'Politique de représentation', 'markers': 'Marqueurs requis / interdits',
        'observed': 'Date d’observation déclarée', 'request_context': 'Contexte de la capture',
        'raw_response': 'Lire la réponse HTTP conservée', 'raw_request': 'Lire la requête conservée',
        'chain': 'Échanges fournis, dans leur ordre déclaré',
        'capture_note': 'Lecture des champs de l’entrée conservée, sans requête réseau ni nouvelle interprétation. Un statut visible dans une trace ne suffit pas à valider une règle.',
        'no_capture': 'Aucune entrée de captures liée sous la forme attendue ; consulter les pièces ci-dessous.',
        'download': 'Télécharger les octets d’origine', 'preview': 'Aperçu texte échappé',
        'binary': 'Pièce binaire : utiliser le téléchargement pour obtenir ses octets exacts.',
        'path': 'Chemin dans le paquet', 'access': 'Accès déclaré', 'description': 'Description conservée',
        'selection': 'Méthode de sélection', 'exclusions': 'Exclusions déclarées', 'profile': 'Profil',
        'none': 'Aucune', 'identity': 'Identité du rapport', 'source': 'Rapport source',
        'coverage_inventory': 'Couverture déclarée par l’outil', 'implemented': 'Pris en charge',
        'deferred': 'Différé — indéterminé', 'out-of-scope': 'Hors couverture',
        'footer': 'Présentation générée par TSEP HTML report', 'read_only': 'Aucune collecte, aucun recalcul de verdict, aucune ressource externe.',
        'skip': 'Aller au contenu', 'all_evidence': 'Ouvrir une pièce pour lire son contenu et vérifier son empreinte.',
        'C': 'Conforme dans le périmètre', 'NC': 'Non conforme dans le périmètre',
        'NT': 'Non établi', 'NA': 'Non applicable', 'pass': 'Réussi', 'fail': 'Échec',
        'inconclusive': 'Indéterminé', 'not-applicable': 'Non applicable',
        'GO_WITH_RESERVATIONS': 'Attendus satisfaits, réserves conservées',
        'NO_GO': 'Une cause bloquante demeure', 'INCOMPLETE': 'Évaluation incomplète', 'REVIEW': 'Décision à examiner',
    },
    'en': {
        'title': 'Evidence report', 'subtitle': 'From observations to decisions, every result retains its evidence.',
        'offline': 'Self-contained · offline', 'draft': 'Experimental protocol',
        'overview': 'Overview', 'comparison': 'Comparison', 'results': 'Results',
        'captures': 'Captures and intent', 'evidence': 'Evidence files', 'method': 'Scope and method',
        'decision': 'Decision within scope', 'controls': 'Selected controls', 'targets': 'Declared targets',
        'scope_only': 'The decision concerns only the declared controls and targets.',
        'not_evaluated': 'controls outside selection', 'artifact_count': 'files linked to this report',
        'valid': 'Structure and fingerprints checked at generation',
        'integrity_limit': 'This check establishes report consistency and the integrity of the files read. It does not establish their authenticity, the correctness of judgments, indexing or ranking.',
        'synthetic': 'Synthetic evidence present', 'synthetic_note': 'At least one file is declared synthetic. Do not present this report as observations entirely collected from a real site.',
        'restricted': 'Declared restricted evidence included', 'restricted_note': 'This self-contained file also embeds the report’s restricted evidence. Preserve its access restrictions when sharing it.',
        'before': 'Previous report', 'after': 'Current report', 'same_input': 'Same supplied captures file',
        'same_input_note': 'Both reports link a supplied input file with identical bytes. The results below are those in the retained reports; this presentation does not reassess the captures.',
        'other_input': 'Capture identity not established',
        'other_input_note': 'Selected controls and declared targets match, but no identical input file is established. Do not attribute differences to the tool change alone.',
        'rule': 'Rule', 'target': 'Target', 'result': 'Result', 'reason': 'Retained reason',
        'missing': 'No observation supplied', 'changed': 'different atomic outcomes',
        'assessor': 'Declared assessor', 'tool': 'Declared tool', 'issued': 'Report issued',
        'mode': 'Assessment mode', 'not_supplied': 'Not supplied', 'protocol': 'Protocol',
        'report_hash': 'Report JSON SHA-256', 'download_report': 'Download original report JSON',
        'control_reason': 'Control conclusion', 'procedure': 'Declared procedure',
        'expectation': 'Rule expectation', 'limits': 'Rule limitations', 'automation': 'Automation',
        'inputs': 'Required evidence kinds', 'linked': 'Linked evidence', 'unobserved': 'Absent observations',
        'unobserved_note': 'These rule/target pairs are absent from the report; no passing result is added.',
        'intent': 'Supplied prior intent', 'declared': 'Declaration date',
        'expected_url': 'Expected final URL', 'expected_hash': 'Expected body digest',
        'representation': 'Representation policy', 'markers': 'Required / forbidden markers',
        'observed': 'Declared observation date', 'request_context': 'Capture context',
        'raw_response': 'Read retained HTTP response', 'raw_request': 'Read retained request',
        'chain': 'Supplied exchanges in declared order',
        'capture_note': 'Fields read from the retained input, without network requests or new interpretation. A status visible in a trace is insufficient to validate a rule.',
        'no_capture': 'No linked captures input in the expected shape; consult the evidence below.',
        'download': 'Download original bytes', 'preview': 'Escaped text preview',
        'binary': 'Binary evidence: download the exact original bytes.',
        'path': 'Path within bundle', 'access': 'Declared access', 'description': 'Retained description',
        'selection': 'Selection method', 'exclusions': 'Declared exclusions', 'profile': 'Profile',
        'none': 'None', 'identity': 'Report identity', 'source': 'Source report',
        'coverage_inventory': 'Tool-declared coverage', 'implemented': 'Supported',
        'deferred': 'Deferred — inconclusive', 'out-of-scope': 'Outside coverage',
        'footer': 'Generated by TSEP HTML report', 'read_only': 'No collection, verdict recalculation or external resources.',
        'skip': 'Skip to content', 'all_evidence': 'Open a file to read its contents and inspect its fingerprint.',
        'C': 'Conforming in scope', 'NC': 'Nonconforming in scope', 'NT': 'Not established', 'NA': 'Not applicable',
        'pass': 'Pass', 'fail': 'Fail', 'inconclusive': 'Inconclusive', 'not-applicable': 'Not applicable',
        'GO_WITH_RESERVATIONS': 'Expectations met, reservations retained',
        'NO_GO': 'A blocking cause remains', 'INCOMPLETE': 'Incomplete assessment', 'REVIEW': 'Decision requires review',
    },
}


def esc(value):
    return escape(str(value), quote=True)


def pretty(value):
    return json.dumps(value, ensure_ascii=False, indent=2)


def badge(value, words):
    # All status classes are validated enums; labels also retain their raw codes.
    return '<span class="badge ' + esc(value) + '">' + esc(value) + ' · ' + esc(words[value]) + '</span>'


def item(label, value, code=False):
    return '<dt>' + esc(label) + '</dt><dd' + (' class="mono"' if code else '') + '>' + esc(value) + '</dd>'


def download(raw, label, name):
    # application/octet-stream avoids rendering captured HTML as an active page.
    return '<a class="download" download="' + esc(name) + '" href="data:application/octet-stream;base64,' + base64.b64encode(raw).decode('ascii') + '">' + esc(label) + ' ↓</a>'


def load(path, root=None):
    path = Path(path)
    with path.open('rb') as handle:
        original = handle.read(tsep.MAX_JSON_BYTES + 1)
    report = tsep.parse_json(original)
    root = Path(root) if root is not None else path.parent
    summary = tsep.validate(report, root)
    files, size = {}, len(original)
    tsep.require(size <= MAX_EMBED_BYTES, 'HTML evidence exceeds 32 MiB per report; no partial embedding')
    for artifact in report['artifacts']:
        file = tsep.evidence_path(root, artifact['path'])
        with file.open('rb') as handle:
            raw = handle.read(MAX_EMBED_BYTES - size + 1)
        size += len(raw)
        tsep.require(size <= MAX_EMBED_BYTES, 'HTML evidence exceeds 32 MiB per report; no partial embedding')
        tsep.require(hashlib.sha256(raw).hexdigest() == artifact['sha256'],
                     'Evidence changed while preparing HTML: ' + artifact['id'])
        files[artifact['id']] = raw
    return {'report': report, 'summary': summary, 'raw': original, 'files': files,
            'sha256': hashlib.sha256(original).hexdigest()}


def captures(bundle):
    artifact = next((a for a in bundle['report']['artifacts']
                     if a['id'] == 'supplied-input' and a['kind'] == 'operator-docs'), None)
    if artifact is not None:
        try:
            data = tsep.parse_json(bundle['files'][artifact['id']])
            if isinstance(data, dict) and data.get('input_version') in ('1', '2') and isinstance(data.get('targets'), list):
                return data
        except (ValueError, UnicodeError, RecursionError):
            pass
    return None


def report_identity(bundle, words, prefix):
    report = bundle['report']
    tool = report['assessor'].get('tool', {})
    return ('<dl>' + item(words['tool'], (tool.get('name', '') + ' ' + tool.get('version', '')).strip() or words['not_supplied'])
            + item(words['issued'], report['issued_at']) + item(words['protocol'], report['protocol']['version'])
            + item(words['report_hash'], bundle['sha256'], True) + '</dl>'
            + download(bundle['raw'], words['download_report'], prefix + '-report.json'))


def comparison(current, previous, words):
    old, new = previous['report'], current['report']
    tsep.require(old['protocol'] == new['protocol'] and old['profile'] == new['profile']
                 and set(old['controls']) == set(new['controls'])
                 and set(old['scope']['targets']) == set(new['scope']['targets']),
                 'HTML comparison requires identical protocol, profile, selected controls and target set')
    same = (captures(current) is not None and captures(previous) is not None
            and current['files']['supplied-input'] == previous['files']['supplied-input'])
    by_pair = lambda report: {(a['rule_id'], a['target']): a for r in report['results'] for a in r.get('atomic_results', [])}
    left, right = by_pair(old), by_pair(new)
    rows, changed = [], 0
    for key in sorted(set(left) | set(right)):
        before, after = left.get(key), right.get(key)
        changed += (before or {}).get('outcome') != (after or {}).get('outcome')
        cells = []
        for atom in (before, after):
            cells.append('<td>' + (badge(atom['outcome'], words) + '<p>' + esc(atom['reason']) + '</p>'
                                  if atom else esc(words['missing'])) + '</td>')
        rows.append('<tr><th scope="row"><code>' + esc(key[0]) + '</code></th><td class="target">' + esc(key[1]) + '</td>' + ''.join(cells) + '</tr>')
    label = 'same_input' if same else 'other_input'
    out = '<section id="comparison"><div class="section-head"><h2>' + esc(words['comparison']) + '</h2><span class="muted small">' + str(changed) + ' ' + esc(words['changed']) + '</span></div>'
    out += '<div class="card comparison"><h3>' + esc(words[label]) + '</h3><p class="comparison-intro">' + esc(words[label + '_note']) + '</p>'
    out += '<div class="two">'
    for bundle, side in ((previous, 'before'), (current, 'after')):
        out += '<div><p class="eyebrow">' + esc(words[side]) + '</p><p class="mono">' + esc(bundle['summary']['decision']) + '</p>' + report_identity(bundle, words, side) + '</div>'
    out += '</div></div><div class="table-scroll"><table><thead><tr>' + ''.join('<th scope="col">' + esc(words[x]) + '</th>' for x in ('rule', 'target', 'before', 'after')) + '</tr></thead><tbody>' + ''.join(rows) + '</tbody></table></div></section>'
    return out


def proof_links(refs, prefix):
    return '<div class="proof-links">' + ''.join('<a href="#' + prefix + '-evidence-' + esc(ref) + '">' + esc(ref) + '</a>' for ref in refs) + '</div>'


def results(bundle, controls, words, language):
    report = bundle['report']
    out = '<section id="results"><div class="section-head"><h2>' + esc(words['results']) + '</h2></div>'
    for result in report['results']:
        cid = result['control_id']
        control = controls[cid]
        rules = {r['id']: r for r in control.get('rules', [])}
        out += '<article class="card control"><div class="row"><div><span class="eyebrow">' + esc(cid) + '</span><h3 class="control-title">' + esc(control['title'][language]) + '</h3></div>' + badge(result['status'], words) + '</div>'
        out += '<p class="reason">' + esc(result['reason']) + '</p><details><summary>' + esc(words['procedure']) + '</summary><p class="small">' + esc(result['procedure']) + '</p>' + proof_links(result['evidence_ids'], 'current') + '</details>'
        seen = set()
        for atom in result.get('atomic_results', []):
            rule = rules[atom['rule_id']]
            seen.add((atom['rule_id'], atom['target']))
            out += '<div class="rule"><div class="row"><h4><code>' + esc(atom['rule_id']) + '</code> · ' + esc(rule['title'][language]) + '</h4>' + badge(atom['outcome'], words) + '</div>'
            out += '<p class="rule-target">' + esc(atom['target']) + '</p><p class="reason">' + esc(atom['reason']) + '</p>' + proof_links(atom['evidence_ids'], 'current')
            out += '<details><summary>' + esc(words['expectation']) + '</summary><dl>' + item(words['expectation'], rule['acceptance'][language]) + item(words['automation'], rule['automation']) + item(words['inputs'], ', '.join(rule['required_inputs'])) + item(words['limits'], rule['limitations'][language]) + '</dl></details></div>'
        missing = [(rid, target) for rid in rules for target in report['scope']['targets'] if (rid, target) not in seen]
        if missing:
            out += '<details class="notice"><summary>' + esc(words['unobserved']) + ' (' + str(len(missing)) + ')</summary><p>' + esc(words['unobserved_note']) + '</p><ul>' + ''.join('<li><code>' + esc(rid) + '</code> · ' + esc(target) + '</li>' for rid, target in missing) + '</ul></details>'
        out += '</article>'
    return out + '</section>'


def capture_view(bundle, words):
    data = captures(bundle)
    out = '<section id="captures"><div class="section-head"><h2>' + esc(words['captures']) + '</h2></div><p class="muted small">' + esc(words['capture_note']) + '</p>'
    if data is None:
        return out + '<p class="empty">' + esc(words['no_capture']) + '</p></section>'
    for target in data['targets']:
        if not isinstance(target, dict):
            continue
        out += '<article class="card target-card"><h3>' + esc(target.get('url', words['not_supplied'])) + '</h3>'
        intent = target.get('intent', {})
        if isinstance(intent, dict):
            fields = [('declared', 'declared_at'), ('expected_url', 'expected_final_url'),
                      ('expected_hash', 'expected_body_sha256'), ('representation', 'representation')]
            out += '<details><summary>' + esc(words['intent']) + '</summary><dl class="context">'
            out += ''.join('<div>' + item(words[label], intent.get(key, words['not_supplied']), key == 'expected_body_sha256') + '</div>' for label, key in fields)
            out += '</dl><pre>' + esc(pretty(intent)) + '</pre></details>'
        out += '<p class="small muted">' + esc(words['observed']) + ' · ' + esc(target.get('observed_at', words['not_supplied'])) + '</p>'
        hops = target.get('http', [])
        if isinstance(hops, list) and hops:
            out += '<p class="eyebrow">' + esc(words['chain']) + '</p><ol class="chain">'
            for hop in hops:
                if not isinstance(hop, dict):
                    continue
                response = hop.get('response', '')
                if isinstance(response, dict):
                    try:
                        response = raw_bytes(response).split(b'\r\n', 1)[0].decode('latin-1')
                    except ValueError:
                        response = words['not_supplied']
                out += '<li><span class="hop-status mono">' + esc(response.split('\r\n', 1)[0] if isinstance(response, str) else words['not_supplied']) + '</span><p>' + esc(hop.get('url', '')) + '</p>'
                for key, label in [('request', 'raw_request'), ('response', 'raw_response')]:
                    if isinstance(hop.get(key), str):
                        out += '<details><summary>' + esc(words[label]) + '</summary><pre>' + esc(hop[key]) + '</pre></details>'
                    elif isinstance(hop.get(key), dict):
                        out += '<details><summary>' + esc(words[label]) + '</summary>'
                        try:
                            raw = raw_bytes(hop[key])
                            out += '<p class="hash">SHA-256 · ' + esc(hashlib.sha256(raw).hexdigest()) + '</p>'
                            out += download(raw, words['download'], key+'-'+hashlib.sha256(raw).hexdigest()[:12]+'.bin')
                            out += '<pre>' + esc(raw.split(b'\r\n\r\n', 1)[0].decode('latin-1')) + '</pre>'
                            out += '<p class="small muted">' + esc(words['binary']) + '</p>'
                        except ValueError:
                            out += '<pre>' + esc(pretty(hop[key])) + '</pre>'
                        out += '</details>'
                out += '</li>'
            out += '</ol>'
        out += '<details><summary>' + esc(words['request_context']) + '</summary><pre>' + esc(pretty(target.get('context', {}))) + '</pre></details></article>'
    return out + '</section>'


def evidence_view(bundle, words, prefix):
    out = ''
    for artifact in bundle['report']['artifacts']:
        raw = bundle['files'][artifact['id']]
        out += '<details class="evidence" id="' + prefix + '-evidence-' + esc(artifact['id']) + '"><summary>' + esc(artifact['id']) + ' <span class="badge neutral">' + esc(artifact['kind']) + '</span><span class="path">' + esc(artifact['path']) + '</span></summary>'
        out += '<dl class="context"><div>' + item(words['description'], artifact['description']) + item(words['targets'], ', '.join(artifact['targets'])) + '</div><div>' + item('SHA-256', artifact['sha256'], True) + item(words['observed'], artifact['observed_at']) + item(words['access'], artifact['access']) + '</div></dl>'
        out += download(raw, words['download'], prefix + '-' + artifact['id'] + '.bin')
        try:
            text = raw.decode('utf-8')
            # NULs in valid UTF-8 may still indicate a binary file.
            if '\x00' in text:
                raise ValueError('binary')
            out += '<details><summary>' + esc(words['preview']) + '</summary><pre>' + esc(text) + '</pre></details>'
        except (UnicodeDecodeError, ValueError):
            out += '<p class="small muted">' + esc(words['binary']) + '</p>'
        out += '</details>'
    return out


def render(report_path, *, evidence_root=None, language='en', compare=None, compare_root=None):
    tsep.require(language in TEXT, 'Unknown HTML language')
    words = TEXT[language]
    current = load(report_path, evidence_root)
    previous = load(compare, compare_root) if compare is not None else None
    report, summary = current['report'], current['summary']
    protocol = tsep.read_json(tsep.PROTOCOL_PATH)
    controls = {c['id']: c for c in protocol['controls']}
    css = (ROOT/'report.css').read_text(encoding='utf-8')
    css_hash = base64.b64encode(hashlib.sha256(css.encode()).digest()).decode('ascii')
    csp = "default-src 'none'; style-src 'sha256-" + css_hash + "'; base-uri 'none'; form-action 'none'"
    out = '<!doctype html><html lang="' + language + '"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="' + esc(csp) + '"><meta name="referrer" content="no-referrer"><title>TSEP · ' + esc(words['title']) + ' · ' + esc(report['scope']['label']) + '</title><style>' + css + '</style></head><body>'
    out += '<a class="skip" href="#main">' + esc(words['skip']) + '</a><header class="top"><div class="wrap masthead"><div class="brand">TSEP<span class="muted"> /</span></div><div class="small muted">' + esc(words['offline']) + '</div></div><div class="wrap hero"><p class="eyebrow">' + esc(words['title']) + '</p><h1>' + esc(words['subtitle']) + '</h1><p class="scope-label">' + esc(report['scope']['label']) + '</p><div class="hero-foot"><span class="pill">' + esc(report['protocol']['version']) + '</span><span class="pill">' + esc(words['draft']) + '</span><span class="small muted">' + esc(report['issued_at']) + '</span></div></div></header>'
    sections = ['overview'] + (['comparison'] if previous else []) + ['results', 'captures', 'evidence', 'method']
    out += '<nav class="nav" aria-label="' + esc(words['title']) + '"><div class="wrap">' + ''.join('<a href="#' + s + '">' + esc(words[s]) + '</a>' for s in sections) + '</div></nav><main id="main" class="wrap">'
    state = 'negative' if summary['counts']['NC'] else ('unknown' if summary['counts']['NT'] else '')
    out += '<section id="overview"><div class="metrics"><div class="card decision-card ' + state + '"><span class="eyebrow">' + esc(words['decision']) + '</span><p class="metric code mono">' + esc(summary['decision']) + '</p><p>' + esc(words[summary['decision']]) + '</p><p class="small"><strong>' + esc(', '.join(report['controls'])) + ' · ' + str(len(report['scope']['targets'])) + ' ' + esc(words['targets'].lower()) + '</strong></p><p class="small muted">' + esc(words['scope_only']) + '</p></div>'
    out += '<div class="card"><span class="eyebrow">' + esc(words['controls']) + '</span><p class="metric">' + str(summary['selected_controls']) + ' <span class="muted">/ ' + str(summary['protocol_controls']) + '</span></p><p class="small muted">' + str(len(summary['unevaluated_controls'])) + ' ' + esc(words['not_evaluated']) + '</p></div>'
    out += '<div class="card"><span class="eyebrow">' + esc(words['targets']) + '</span><p class="metric">' + str(len(report['scope']['targets'])) + '</p><p class="small muted">' + str(len(report['artifacts'])) + ' ' + esc(words['artifact_count']) + '</p></div></div>'
    out += '<div class="notice"><strong>' + esc(words['valid']) + '</strong>' + esc(words['integrity_limit']) + '</div>'
    for access, label in [('synthetic', 'synthetic'), ('restricted', 'restricted')]:
        if any(a['access'] == access for bundle in (current, previous) if bundle
               for a in bundle['report']['artifacts']):
            out += '<div class="notice synthetic"><strong>' + esc(words[label]) + '</strong>' + esc(words[label + '_note']) + '</div>'
    out += '</section>'
    metadata = current['files'].get('import-record')
    if metadata:
        try:
            inventory = tsep.parse_json(metadata).get('coverage_inventory', [])
            if isinstance(inventory, list) and inventory:
                out += '<section class="card"><h2>' + esc(words['coverage_inventory']) + '</h2><ul>'
                for entry in inventory:
                    if isinstance(entry, dict) and entry.get('state') in ('implemented', 'deferred', 'out-of-scope'):
                        out += '<li><strong>' + esc(words[entry['state']]) + '</strong> · ' + esc(entry.get(language, '')) + '</li>'
                out += '</ul></section>'
        except (ValueError, AttributeError):
            pass
    if previous:
        out += comparison(current, previous, words)
    out += results(current, controls, words, language) + capture_view(current, words)
    out += '<section id="evidence"><div class="section-head"><h2>' + esc(words['evidence']) + '</h2></div><p class="muted small">' + esc(words['all_evidence']) + '</p><div class="card">' + evidence_view(current, words, 'current') + '</div>'
    if previous:
        out += '<details class="card"><summary>' + esc(words['before']) + ' · ' + esc(words['evidence']) + '</summary>' + evidence_view(previous, words, 'previous') + '</details>'
    out += '</section><section id="method"><div class="section-head"><h2>' + esc(words['method']) + '</h2></div><div class="card meta-grid"><div><h3>' + esc(words['selection']) + '</h3><p class="small">' + esc(report['scope']['selection_method']) + '</p><dl>' + item(words['profile'], report['profile']) + item(words['exclusions'], '; '.join(report['scope']['exclusions']) or words['none']) + '</dl></div>'
    out += '<div><h3>' + esc(words['assessor']) + '</h3><dl>' + item(words['assessor'], report['assessor']['name']) + item(words['mode'], report['assessor']['mode']) + item(words['controls'], ', '.join(report['controls'])) + '</dl></div>'
    out += '<div><h3>' + esc(words['identity']) + '</h3>' + report_identity(current, words, 'current') + '</div></div></section></main>'
    out += '<footer class="footer"><div class="wrap"><p>' + esc(words['footer']) + ' ' + VERSION + ' · ' + esc(words['read_only']) + '</p><p class="hash">' + esc(words['protocol']) + ' SHA-256 · ' + esc(report['protocol']['sha256']) + '</p></div></footer></body></html>\n'
    return out


def write(report_path, output, **options):
    """Validate everything before creating a new output; never replace a file."""
    output = Path(output)
    tsep.require(not output.exists() and not output.is_symlink(), 'HTML output already exists; choose a new file')
    document = render(report_path, **options)
    handle = output.open('x', encoding='utf-8', newline='\n')
    try:
        with handle:
            handle.write(document)
    except OSError:
        output.unlink()
        raise
    return {'html': str(output), 'sha256': tsep.digest(output), 'renderer_version': VERSION}
