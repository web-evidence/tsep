"""Explicit source-only A04 policy; no activated navigation or inferred duplicates."""
import hashlib
import json
import os

from conformance.http import Unknown, need
from conformance.source_directives import consensus
from conformance.source_canonical import ambiguous_attributes
from experiments import link_elements, source_http, url_resolution

READER = 'html-tree-links-v1'
VERSION = '1'
HTML = link_elements.HTML
MAX_DIAGNOSTIC_BYTES = 4 * 1024 * 1024
attribute = link_elements.attribute
LOWER = str.maketrans('ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')
SCOPE = 'Declared-family convergence only; no link-presence, sufficiency or quality claim.'


def qualified(record, errors):
    need(record['namespace'] == HTML and all(n in (None, HTML) for n in record['ancestor_namespaces']),
         'Foreign-context HTML href is unqualified')
    need(record['context'] in ('head', 'body') and record['source_span_utf16'] is not None,
         'Source href lacks qualified context/byte attribution')
    need(not ambiguous_attributes(record, errors), 'Duplicate attributes on href element need review')


def decide_reading(reading, metadata, headers, fallback, family, preferred, exempt, resolve):
    need(reading['complete'], 'Incomplete element inventory; no partial absence or failure claim')
    errors = reading['parse_errors']
    unknowns = ['Reported HTML parse errors require review'] if errors else []
    for t in reading['templates']:
        shadow = attribute(t, 'shadowrootmode')
        if (shadow is not None and shadow.translate(LOWER) in ('open', 'closed')) or attribute(t, 'for') is not None:
            unknowns.append('Declared shadow/template attachment remains unknown')
    active = [r for r in reading['records'] if not r['template_indices']]
    bases = [r for r in active if r['namespace'] == HTML and r['tag'] == 'base' and attribute(r, 'href') is not None]
    base = fallback; basis = 'final-response-url'; base_unknowns = []
    if bases:
        first = bases[0]
        try: qualified(first, errors)
        except (Unknown, KeyError, TypeError, ValueError) as e: base_unknowns.append(str(e))
        if errors: base_unknowns.append('Base in a source with reported parse errors')
        if metadata is None or not metadata['complete']:
            base_unknowns.append('CSP metadata inventory unavailable')
        else:
            csp = [m for m in metadata['metadata'] if not m['template_indices'] and
                   m['attributes'].get('http-equiv', '').translate(LOWER).strip() == 'content-security-policy']
            if csp: base_unknowns.append('CSP meta with base: policy not modeled')
        if headers.get('content-security-policy'): base_unknowns.append('CSP response with base: policy not modeled')
        candidate = resolve([{'url': attribute(first, 'href'), 'base': fallback}])[0]
        if not candidate['ok']: basis = 'first-invalid-base-fallback'
        elif candidate['protocol'] in ('javascript:', 'data:'): basis = 'first-disallowed-base-fallback'
        else: base = candidate['href']; basis = 'first-base-href'
    links = []
    for r in active:
        if r['tag'] not in ('a', 'area'): continue
        href = attribute(r, 'href'); xlink = attribute(r, 'href', link_elements.XLINK)
        if r['namespace'] != HTML:
            if href is not None or xlink is not None: unknowns.append('Foreign hyperlink retained, not evaluated as HTML href')
            continue
        if href is None: continue  # Known lack of a static HTML href, not an empty URL.
        try: qualified(r, errors)
        except (Unknown, KeyError, TypeError, ValueError) as e:
            unknowns.append(str(e)); continue
        links.append({'node_index': r['node_index'], 'tag': r['tag'], 'href': href,
                      'body_span_bytes': r['body_span_bytes']})
    requests = [{'url': l['href'], 'base': base} for l in links] + [{'url': l['href'], 'base': None} for l in links]
    results = resolve(requests)
    counts = {'html_href_candidates': len(links), 'family_links': 0, 'outside_family_http': 0,
              'non_http': 0, 'unknown_links': 0, 'competing_links': 0, 'exceptions': 0}
    for i, link in enumerate(links):
        parsed, absolute = results[i], results[i + len(links)]
        # URL('https:variant') can succeed but still depend on a same-scheme base.
        independent = absolute['ok'] and absolute['protocol'] in ('http:', 'https:') and absolute['href'] == link['href']
        link['resolution'] = parsed; link['standalone_resolution'] = absolute
        link['base_independent_subset'] = independent
        if base_unknowns and not independent:
            link['classification'] = 'unknown-base'; counts['unknown_links'] += 1
            unknowns.append('Base-dependent href under unmodeled base conditions'); continue
        value = absolute if independent else parsed
        if not value['ok']:
            link['classification'] = 'unknown-url'; counts['unknown_links'] += 1
            unknowns.append('Href URL could not be resolved'); continue
        destination = value['without_fragment']; link['destination'] = destination
        if value['protocol'] not in ('http:', 'https:'):
            link['classification'] = 'non-http'; counts['non_http'] += 1
        elif destination not in family:
            link['classification'] = 'outside-declared-family'; counts['outside_family_http'] += 1
        else:
            counts['family_links'] += 1
            if destination == preferred: link['classification'] = 'preferred'
            elif destination in exempt:
                link['classification'] = 'documented-exception'; counts['exceptions'] += 1
            else:
                link['classification'] = 'competing'; counts['competing_links'] += 1
    outcome = 'fail' if counts['competing_links'] else 'inconclusive' if unknowns else 'pass'
    reason = SCOPE + ' Counts: ' + repr(counts)
    if counts['family_links'] == 0: reason += ' 0 links to the declared family observed in this source hypothesis.'
    reason += '; limits: ' + repr(unknowns)
    return {'outcome': outcome, 'reason': reason, 'counts': counts, 'links': links,
            'candidate_base': {'url': base, 'basis': basis, 'unknowns': base_unknowns}, 'unknowns': unknowns}


class Surface:
    def __init__(self, headers, body, selection, family, preferred, exempt, *, document_url, requested_url, diagnostics=None):
        record = {'reader': selection, 'policy_version': VERSION, 'document_url': document_url,
                  'requested_url': requested_url, 'scope': SCOPE}
        try:
            need(selection == READER, 'Unsupported link source_reader; no legacy fallback')
            raw = body if type(body) is bytes else body.encode('utf-8')
            record['body_sha256'] = hashlib.sha256(raw).hexdigest(); runs = []; record['url_runs'] = runs
            node = os.environ.get('TSEP_SOURCE_NODE')
            def resolve(requests):
                run = url_resolution.resolve(requests, node=node); runs.append(run); return run['results']
            urls = list(family)
            initial = resolve([{'url': u, 'base': None} for u in urls] + [{'url': document_url, 'base': None}])
            need(all(r['ok'] and r['protocol'] in ('http:', 'https:') and r['href'] == u for u, r in zip(urls, initial)),
                 'Declared family URL must already equal its WHATWG serialization; no silent normalization')
            fallback = initial[-1]
            need(fallback['ok'] and fallback['protocol'] in ('http:', 'https:'), 'HTTP(S) final document URL required')
            inventory = link_elements.inventory(raw, content_types=headers.get('content-type', []), node=node)
            record['inventory'] = inventory; metadata = None
            if any(r['namespace'] == HTML and r['tag'] == 'base' and not r['template_indices'] and attribute(r, 'href') is not None
                   for v in inventory['readings'].values() for r in v['records']):
                full = source_http.inventory(raw, content_types=headers.get('content-type', []), node=node, metadata=True)
                metadata = {k: v for k, v in full.items() if k not in ('readings', 'comparisons', 'supplementary_comparisons')}
                metadata['readings'] = {mode: {k: v for k, v in r.items() if k in ('complete', 'reason', 'metadata', 'parse_errors')}
                                        for mode, r in full['readings'].items()}
                record['base_policy_metadata'] = metadata
            decisions = {}
            for mode, reading in inventory['readings'].items():
                try:
                    decisions[mode] = decide_reading(reading, metadata['readings'][mode] if metadata else None,
                        headers, fallback['href'], family, preferred, exempt, resolve)
                except (Unknown, KeyError, TypeError, ValueError, OSError) as error:
                    decisions[mode] = {'outcome': 'inconclusive', 'reason': str(error)}
            record['hypotheses'] = decisions; outcome = consensus(decisions)
            reason = READER + ': ' + '; '.join(m + '=' + d['outcome'] + ' (' + d['reason'] + ')' for m, d in decisions.items())
        except (Unknown, KeyError, TypeError, ValueError, OSError) as error:
            outcome, reason = 'inconclusive', READER + ': ' + str(error)
        record.update(outcome=outcome, reason=reason)
        if len(json.dumps(record, ensure_ascii=False, indent=2).encode()) > MAX_DIAGNOSTIC_BYTES:
            outcome, reason = 'inconclusive', READER + ': Source link diagnostic exceeds 4 MiB; no truncated decision'
            record = {'reader': READER if selection == READER else '[unsupported; see input]', 'policy_version': VERSION,
                      'document_url': document_url, 'requested_url': requested_url,
                      'body_sha256': record.get('body_sha256'), 'outcome': outcome, 'reason': reason}
        self.source_decision = (outcome, reason)
        if diagnostics is not None: diagnostics.append(record)
