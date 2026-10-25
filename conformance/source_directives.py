"""Opt-in html-tree-directives-v1 policy over attributable static hypotheses.

No script execution, engine observation, automatic rendering exemption or fallback.
"""
import hashlib
import json
import os
from conformance.http import Unknown, need
from experiments import source_http

READER = 'html-tree-directives-v1'
VERSION = '1'
HTML = 'http://www.w3.org/1999/xhtml'
MAX_DIAGNOSTIC_BYTES = 4 * 1024 * 1024
ASCII_LOWER = str.maketrans('ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')


def lower(value):
    return value.translate(ASCII_LOWER)


def decide_reading(reading, headers, intent, combine):
    need(reading['complete'], 'Incomplete bounded source inventory')
    need(not reading['parse_errors'], 'Reported HTML parse error is outside this first policy')
    for template in reading['template_containers']:
        need(template['shadow_declaration']['value_state'] not in ('open', 'closed'),
             'Declarative shadow root is outside this source policy; attachment not inferred')
        need('for' not in template['attributes'], 'Streaming template declaration is outside this source policy')
    values = []
    for record in reading['metadata']:
        # These are alternative static trees, not executed template/script states.
        if record['template_indices']:
            continue
        attrs = record['attributes']
        name = lower(attrs.get('name', ''))
        equiv = lower(attrs.get('http-equiv', ''))
        pseudo = {'robots', 'googlebot', 'x-robots-tag'}
        need(equiv.strip() not in pseudo and name != 'x-robots-tag' and
             not (name.strip() in ('robots', 'googlebot') and name not in ('robots', 'googlebot')),
             'Unsupported robots-like metadata spelling or http-equiv; not interpreted as an HTTP header')
        if name not in ('robots', 'googlebot'):
            continue  # Other crawler names and ordinary metadata retained, outside this objective.
        need(record['namespace'] == HTML and record['context'] in ('head', 'body') and
             all(ns in (None, HTML) for ns in record['ancestor_namespaces']),
             'Robots metadata in foreign or unsupported tree context')
        need('content' in attrs, 'Missing robots meta content')
        need(not any(k in attrs for k in ('http-equiv', 'charset', 'itemprop')),
             'Mixed metadata roles require review')
        values.append(attrs['content'])
    return combine(headers, values, intent)


def consensus(results):
    outcomes = [results[mode]['outcome'] for mode in ('enabled', 'disabled')]
    return outcomes[0] if outcomes[0] == outcomes[1] and outcomes[0] in ('pass', 'fail') else 'inconclusive'


def assess(headers, body, intent, *, combine, diagnostics=None):
    record = {'reader': intent.get('source_reader'), 'policy_version': VERSION,
              'scope': 'Static source hypotheses only; not coexisting rendered states, HTML validity or Google behavior.'}
    try:
        need(intent.get('source_reader') == READER, 'Unsupported source_reader; no legacy fallback')
        raw = body if type(body) is bytes else body.encode('utf-8')
        record['body_sha256'] = hashlib.sha256(raw).hexdigest()
        # Validate the objective before running the optional parser. This does not yield a verdict.
        combine({}, [], intent)
        result = source_http.inventory(raw, content_types=headers.get('content-type', []),
                                       node=os.environ.get('TSEP_SOURCE_NODE'), metadata=True)
        # Retain every meta, its location and context; unrelated link inventories do not
        # enter this rule's artifact. No source record is removed to force agreement.
        record['inventory'] = {k:v for k,v in result.items() if k not in
                               ('readings', 'comparisons', 'supplementary_comparisons')}
        record['inventory']['readings'] = {mode:{k:v for k,v in reading.items() if k in
            ('complete', 'reason', 'metadata', 'template_containers', 'encoding_declarations',
             'parse_errors', 'tree_nodes', 'document_mode')} for mode,reading in result['readings'].items()}
        if len(json.dumps(record, ensure_ascii=False).encode('utf-8')) > MAX_DIAGNOSTIC_BYTES:
            record.pop('inventory')
            raise Unknown('Source metadata diagnostics exceed 4 MiB; no conclusive result or truncated absence claim')
        results = {}
        for mode, reading in result['readings'].items():
            try:
                if 'presentation_reader' in intent or 'directive_policy' in intent:
                    preview_notes = []
                    outcome, reason = decide_reading(reading, headers, intent,
                        lambda h, v, i: combine(h, v, i, diagnostics=preview_notes))
                    record.setdefault('directive_observations' if 'directive_policy' in intent else 'preview_observations', {})[mode] = preview_notes
                else:
                    outcome, reason = decide_reading(reading, headers, intent, combine)
            except (Unknown, KeyError, TypeError, ValueError) as error:
                outcome, reason = 'inconclusive', str(error)
            results[mode] = {'outcome':outcome, 'reason':reason}
        record['hypotheses'] = results
        outcome = consensus(results)
        reason = READER + ': ' + '; '.join(mode+'='+r['outcome']+' ('+r['reason']+')' for mode,r in results.items())
        reason += '; agreement of bounded alternatives only; no scripts executed or actual indexing inferred'
    except (Unknown, KeyError, TypeError, ValueError, OSError) as error:
        outcome, reason = 'inconclusive', str(error)
    record.update(outcome=outcome, reason=reason)
    # Decisions/reasons also occupy the retained artifact: enforce the bound after
    # they are attached, using its formatted representation, not only the inventory.
    if len(json.dumps(record, ensure_ascii=False, indent=2).encode('utf-8')) > MAX_DIAGNOSTIC_BYTES:
        outcome, reason = 'inconclusive', 'Final source metadata diagnostics exceed 4 MiB; full raw input retained, no truncated absence claim'
        record = {'reader':READER if intent.get('source_reader') == READER else '[unsupported; see retained input]',
                  'policy_version':VERSION, 'body_sha256':record.get('body_sha256'),
                  'outcome':outcome, 'reason':reason}
    if diagnostics is not None:
        diagnostics.append(record)
    return outcome, reason
