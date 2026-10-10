#!/usr/bin/env python3
"""Compare two registered capture phases offline; NEVER issue a TSEP verdict."""
import argparse
from datetime import datetime
import hashlib
from html import escape
import json
from pathlib import Path, PurePosixPath
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from conformance.http import message, body_digest, text_body, raw_bytes, Unknown
from conformance.source_text import extract
from diagnostics.coverage import surface
from provenance.runtime import runtime_identity

VERSION = '1'
LIMIT = 16*1024*1024


def read(path):
    with path.open('rb') as handle:
        raw = handle.read(LIMIT+1)
    if len(raw) > LIMIT:
        raise ValueError('Campaign input size limit exceeded')
    return raw, json.loads(raw)


def stamp(value):
    result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if result.tzinfo is None:
        raise ValueError('Campaign timestamps require a timezone')
    return result


def phase(root):
    """Verify declared bytes, including the JSON/sidecar correspondence."""
    if (root/'SHA256SUMS').stat().st_size > 65536:
        raise ValueError('Campaign manifest size limit exceeded')
    manifest = (root/'SHA256SUMS').read_bytes()
    names = set()
    for line in manifest.decode('ascii').splitlines():
        sha, name = line.split('  ', 1)
        rel = PurePosixPath(name)
        if name in names or rel.is_absolute() or '..' in rel.parts or '\\' in name or rel.as_posix() != name:
            raise ValueError('Unsafe campaign manifest')
        path = root/name
        path.resolve().relative_to(root.resolve())
        if path.is_symlink() or not path.is_file() or path.stat().st_size > LIMIT:
            raise ValueError('Invalid campaign file')
        if hashlib.sha256(path.read_bytes()).hexdigest() != sha:
            raise ValueError('Campaign integrity mismatch: '+name)
        names.add(name)
    if 'capture.json' not in names:
        raise ValueError('Missing capture manifest entry')
    raw, data = read(root/'capture.json')
    targets = data['targets']
    if not isinstance(targets, list) or not 1 <= len(targets) <= 10:
        raise ValueError('Expected 1–10 captured targets')
    for i, target in enumerate(targets, 1):
        hops = target['http']
        if not isinstance(hops, list) or len(hops) > 6:
            raise ValueError('Too many capture hops')
        for j, hop in enumerate(hops, 1):
            for kind in ('request', 'response'):
                name = 'target-'+str(i)+'-hop-'+str(j)+'-'+kind+'.bin'
                if name not in names or raw_bytes(hop[kind]) != (root/name).read_bytes():
                    raise ValueError('Capture JSON/sidecar mismatch: '+name)
    return data, {'capture_sha256': hashlib.sha256(raw).hexdigest(),
                  'manifest_sha256': hashlib.sha256(manifest).hexdigest()}


def inspect(target):
    result = {'recorded_at': target['observed_at'], 'complete_response': False,
              'inventory': surface(target), 'inventory_exhaustive': False,
              'extraction': {'available': False},
              'extraction_scope': 'Bounded interpreter 5 source extractor: whole source or first refusal only, no marker verdict.'}
    try:
        hops = target['http']
        if not hops or hops[-1].get('complete') is not True or target.get('collection_error'):
            raise ValueError('No complete terminal response available')
        hop = hops[-1]
        status, headers, body = message(hop['response'], True)
        result.update(complete_response=True, final_recorded_url=hop['url'], status=status,
                      decoded_body_sha256=body_digest(body), decoded_bytes=len(body),
                      content_type=headers.get('content-type', []))
        if not result['inventory']['available']:
            raise ValueError(result['inventory'].get('unavailable_reason', 'HTML inventory unavailable'))
        source = text_body(body)
        if not re.search(r'</html\s*>\s*$', source, re.I):
            raise Unknown('Incomplete HTML document')
        segments = extract(source)
        result['extraction'] = {'available': True, 'segments': len(segments)}
    except (ValueError, KeyError, TypeError, AttributeError) as error:
        result['extraction'] = {'available': False, 'reason': str(error)}
    return result


def compare(registration, first, second):
    raw, reg = read(registration)
    if reg.get('kind') != 'diagnostic-registration' or reg.get('phases') != 2:
        raise ValueError('Expected two-phase diagnostic registration')
    urls = reg['settings']['urls']
    if not isinstance(urls, list) or not 1 <= len(urls) <= 10 or len(set(urls)) != len(urls):
        raise ValueError('Invalid registered target list')
    gap = reg['minimum_gap_seconds']
    if type(gap) not in (int, float) or not 0 <= gap <= 86400:
        raise ValueError('Invalid minimum gap')
    a, a_hash = phase(first)
    b, b_hash = phase(second)
    for data in (a, b):
        if data['settings'] != reg['settings'] or [t['url'] for t in data['targets']] != urls:
            raise ValueError('Capture differs from registered settings/URL order')
        if data.get('sources_unchanged_during_collection') is not True:
            raise ValueError('Collector source continuity not established')
        if stamp(data['finished_at']) < stamp(data['started_at']):
            raise ValueError('Reversed phase timestamps')
        if any(not stamp(data['started_at']) <= stamp(t['observed_at']) <= stamp(data['finished_at']) for t in data['targets']):
            raise ValueError('Observation outside phase timestamps')
    if stamp(reg['registered_at']) > stamp(a['started_at']):
        raise ValueError('Registration is later than phase A')
    elapsed = (stamp(b['started_at'])-stamp(a['finished_at'])).total_seconds()
    if elapsed < gap:
        raise ValueError('Registered minimum gap not met')
    if a['source_files'] != b['source_files'] or a['collector_version'] != b['collector_version']:
        raise ValueError('Collector changed between phases')
    pages = []
    for left, right in zip(a['targets'], b['targets']):
        prior, current = inspect(left), inspect(right)
        comparable = (prior['complete_response'] and current['complete_response'] and
                      prior['status'] == current['status'] == 200 and
                      prior['final_recorded_url'] == current['final_recorded_url'])
        change = ('changed' if prior['decoded_body_sha256'] != current['decoded_body_sha256'] else 'unchanged') if comparable else 'unresolved'
        pages.append({'url': left['url'], 'body_comparison': change, 'first': prior, 'second': current,
                      'media_headers_differ': prior['content_type'] != current['content_type'] if prior['complete_response'] and current['complete_response'] else None})
    codes = sorted({c['code'] for p in pages for phase_name in ('first', 'second') for c in p[phase_name]['inventory'].get('candidate_limits', [])})
    matrix = []
    for code in codes:
        matched = [p for p in pages if any(c['code'] == code for c in p['second']['inventory'].get('candidate_limits', []))]
        matrix.append({'construction': code, 'pages_second_phase': len(matched), 'changed_pages_second_phase': sum(p['body_comparison'] == 'changed' for p in matched)})
    files = ('diagnostics/campaign.py', 'diagnostics/coverage.py', 'conformance/http.py', 'conformance/source_text.py', 'provenance/runtime.py', 'tsep.py')
    return {'kind': 'diagnostic-campaign-only', 'campaign_version': VERSION,
            'registration_sha256': hashlib.sha256(raw).hexdigest(), 'phase_a': a_hash, 'phase_b': b_hash,
            'gap_seconds': elapsed, 'collector_version': a['collector_version'], 'pages': pages,
            'counts': {key: sum(p['body_comparison'] == key for p in pages) for key in ('changed', 'unchanged', 'unresolved')},
            'changed_pages_with_complete_extraction': sum(p['body_comparison'] == 'changed' and p['second']['extraction']['available'] for p in pages),
            'construction_matrix': matrix, 'runtime': runtime_identity(),
            'source_sha256': {name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in files},
            'network_requests': 0,
            'scope': 'Last complete recorded 200 responses at the same recorded final URL; no trace validation, intent, marker test, TSEP outcome or semantic identity assessment.',
            'limitations': 'Two moments and a convenience sample only. Changed means different complete decoded bytes, not an SEO defect. Unchanged does not establish general stability. Inventory 1 is exploratory and references interpreter 4: SVG style/text candidates may overlap and need not block interpreter 5. Extraction availability probes the bounded source extractor only; it does not validate HTML, a whole trace or marker relevance. Recorded times and source hashes do not authenticate collection.'}


def render(data, language):
    fr = language == 'fr'
    title = 'Campagne réelle · diagnostic uniquement' if fr else 'Real capture campaign · diagnostic only'
    note = ('Deux captures par URL. Aucun verdict TSEP, aucune conformité globale. « Changé » décrit les octets décodés, pas un défaut SEO.' if fr else 'Two captures per URL. No TSEP verdict or global conformity. Changed describes decoded bytes, not an SEO defect.')
    out = '<!doctype html><html lang="'+language+'"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'unsafe-inline\'"><title>'+title+'</title><style>body{font:16px system-ui;max-width:1100px;margin:40px auto;padding:0 20px;color:#172b38;background:#f7f9fa}table{width:100%;border-collapse:collapse;background:white}th,td{border:1px solid #bdc9d0;padding:10px;text-align:left;overflow-wrap:anywhere}aside{padding:18px;background:#fff3d6;border-left:5px solid #ad6800}pre{white-space:pre-wrap;overflow-wrap:anywhere}details{margin:16px 0}summary{cursor:pointer;font-weight:600}</style><body><h1>'+title+'</h1><aside>'+note+'</aside>'
    out += '<p>'+escape(json.dumps(data['counts']))+'</p><table><tr><th>URL</th><th>'+('Corps' if fr else 'Body')+'</th><th>'+('Extraction complète · phase B' if fr else 'Complete extraction · phase B')+'</th></tr>'
    labels = {'changed': 'Changé', 'unchanged': 'Identique', 'unresolved': 'Indéterminé'} if fr else {}
    for page in data['pages']:
        e = page['second']['extraction']
        out += '<tr><td>'+escape(page['url'])+'</td><td>'+labels.get(page['body_comparison'], page['body_comparison'])+'</td><td>'+escape(('Disponible' if fr else 'Available') if e['available'] else e['reason'])+'</td></tr>'
    out += '</table><h2>'+('Constructions observées · inventaire exploratoire v1' if fr else 'Observed constructions · exploratory inventory v1')+'</h2><p>'+('Ces candidats ne sont pas tous des blocages de l’extracteur actuel ; styles SVG et texte SVG peuvent se recouvrir.' if fr else 'These candidates do not all block the current extractor; SVG style/text may overlap.')+'</p><table><tr><th>Construction</th><th>Pages</th><th>'+('Pages changées' if fr else 'Changed pages')+'</th></tr>'
    for row in data['construction_matrix']:
        out += '<tr><td>'+escape(row['construction'])+'</td><td>'+str(row['pages_second_phase'])+'</td><td>'+str(row['changed_pages_second_phase'])+'</td></tr>'
    out += '</table>'
    for page in data['pages']:
        out += '<details><summary>'+escape(page['url'])+'</summary><pre>'+escape(json.dumps(page, ensure_ascii=False, indent=2))+'</pre></details>'
    out += '<details><summary>'+('Méthode et limites' if fr else 'Method and limitations')+'</summary><pre>'+escape(json.dumps({k:v for k,v in data.items() if k not in ('pages','construction_matrix')},ensure_ascii=False,indent=2))+'</pre></details></body></html>'
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('registration', type=Path)
    parser.add_argument('phase_a', type=Path)
    parser.add_argument('phase_b', type=Path)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    try:
        data = compare(args.registration, args.phase_a, args.phase_b)
        args.output_dir.mkdir(exist_ok=False)
        files = {'campaign.json': json.dumps(data, ensure_ascii=False, indent=2)+'\n',
                 'campaign-fr.html': render(data, 'fr'), 'campaign-en.html': render(data, 'en')}
        for name, value in files.items():
            (args.output_dir/name).write_text(value, encoding='utf-8')
        (args.output_dir/'SHA256SUMS').write_text(''.join(hashlib.sha256(value.encode()).hexdigest()+'  '+name+'\n' for name, value in sorted(files.items())))
        print(json.dumps({'kind': data['kind'], 'counts': data['counts'], 'network_requests': 0}))
    except (ValueError, OSError, KeyError, TypeError, AttributeError) as error:
        print(json.dumps({'kind': 'diagnostic-campaign-error', 'error': str(error)}), file=sys.stderr)
        return 64
    return 0


if __name__ == '__main__':
    sys.exit(main())
