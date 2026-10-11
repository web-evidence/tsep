"""Opt-in TS01 parsed-source marker policy; no implicit migration or browser claim."""
import hashlib
import json
import os

from conformance.http import Unknown, need
from experiments import source_markers as reader

READER = 'html-tree-markers-v1'
VERSION = '1'
MAX_DIAGNOSTIC_BYTES = 4 * 1024 * 1024


def compact(observed):
    """Retain every projected record, interning only identical ancestor contexts.

    Full trees can be reconstructed from the retained input and exact tools;
    they are not duplicated alongside the attributed projection in the bundle.
    """
    inventory = observed['inventory']
    result = {'observer_version': observed['experiment_version'],
              'source_sha256': observed['source_sha256'],
              'content_types': observed['content_types'],
              'parser': {k: v for k, v in inventory.items()
                         if k not in ('readings', 'kind', 'normative_effect', 'source_sha256')},
              'hypotheses': {}}
    for mode in reader.MODES:
        reading = observed['readings'][mode]
        row = {k: v for k, v in reading.items()
               if k not in ('segments', 'excluded', 'candidate_outcome')}
        row['outcome'] = reading['candidate_outcome']
        contexts, registry = [], {}
        for kind in ('segments', 'excluded'):
            row[kind] = None
            if reading[kind] is None:
                continue
            records = []
            for segment in reading[kind]:
                context = segment['ancestors']
                key = json.dumps(context, sort_keys=True, ensure_ascii=False)
                if key not in registry:
                    registry[key] = len(contexts)
                    contexts.append(context)
                records.append(dict({k: v for k, v in segment.items() if k != 'ancestors'},
                                    context_id=registry[key]))
            row[kind] = records
        row['contexts'] = contexts
        tree = inventory['readings'][mode]
        row['tree'] = {k: v for k, v in tree.items() if k != 'nodes'}
        row['tree']['node_count'] = len(tree['nodes'])
        result['hypotheses'][mode] = row
    return result


def verify_projection(observed, packed):
    """Check every retained record before admitting the compact diagnostic."""
    need(set(packed['hypotheses']) == set(reader.MODES), 'Compact marker hypotheses differ')
    for mode in reader.MODES:
        original = observed['readings'][mode]
        row = packed['hypotheses'][mode]
        for kind in ('segments', 'excluded'):
            if original[kind] is None:
                need(row[kind] is None, 'Unavailable projection cannot become compact records')
                continue
            need(type(row[kind]) is list and len(row[kind]) == len(original[kind]),
                 'Compact projection record count differs')
            for record, expected in zip(row[kind], original[kind]):
                index = record['context_id']
                need(type(index) is int and 0 <= index < len(row['contexts']),
                     'Compact projection context reference is invalid')
                expanded = {k: v for k, v in record.items() if k != 'context_id'}
                expanded['ancestors'] = row['contexts'][index]
                need(expanded == expected, 'Compact projection differs from attributed record')
        expected_metadata = {k: v for k, v in original.items()
                             if k not in ('segments', 'excluded', 'candidate_outcome')}
        actual_metadata = {k: v for k, v in row.items()
                           if k not in ('segments', 'excluded', 'contexts', 'tree', 'outcome')}
        need(actual_metadata == expected_metadata and row['outcome'] == original['candidate_outcome'],
             'Compact projection outcome or metadata differs')
        tree = observed['inventory']['readings'][mode]
        expected_tree = {k: v for k, v in tree.items() if k != 'nodes'}
        expected_tree['node_count'] = len(tree['nodes'])
        need(row['tree'] == expected_tree, 'Compact tree state or errors differ')


def assess(headers, body, intent, *, diagnostics=None):
    """Preserve URL/hash/stability precedence; bound criteria before comparison."""
    selected = intent.get('identity_reader')
    record = {'kind': 'ts01-source-marker-assessment',
              'reader': READER if selected == READER else '[unsupported; see supplied intent]',
              'policy_version': VERSION,
              'scope': 'Whole-document static alternatives; literal parsed segments, not visibility, '
                       'semantic sufficiency, actual DOM, browser or search-engine behavior.'}
    try:
        need(selected == READER, 'Unsupported identity_reader; no historical fallback')
        objective = {k: intent.get(k, []) for k in ('required_markers', 'forbidden_markers')}
        reader.criteria(objective)
        need(objective['required_markers'] or objective['forbidden_markers'],
             'Body digest changed without stable policy or identity markers')
        raw = body if type(body) is bytes else body.encode('utf-8')
        record['body_sha256'] = hashlib.sha256(raw).hexdigest()
        observed = reader.observe(raw, content_types=headers.get('content-type', []),
                                  objective=objective, node=os.environ.get('TSEP_SOURCE_NODE'))
        packed = compact(observed)
        verify_projection(observed, packed)
        record.update(packed)
        outcome = observed['candidate_consensus']
        reasons = []
        for mode in reader.MODES:
            reading = observed['readings'][mode]
            detail = reading.get('reason', '')
            if reading['complete']:
                detail += '; ' + json.dumps({'missing_required': reading['missing_required'],
                                             'present_forbidden': reading['present_forbidden']},
                                            ensure_ascii=False)
            reasons.append(mode + '=' + reading['candidate_outcome'] + ' (' + detail + ')')
        reason = READER + ': ' + '; '.join(reasons)
        reason += '; agreement of complete static alternatives only; source text is not rendered visibility'
    except (Unknown, KeyError, TypeError, ValueError, OSError) as error:
        outcome, reason = 'inconclusive', str(error)
    record.update(outcome=outcome, reason=reason)
    if len(json.dumps(record, ensure_ascii=False, indent=2).encode('utf-8')) > MAX_DIAGNOSTIC_BYTES:
        outcome = 'inconclusive'
        reason = 'Source marker diagnostics exceed 4 MiB; original input retained, no partial projection or conclusive outcome'
        record = {k: record[k] for k in ('kind', 'reader', 'policy_version', 'scope')}
        record.update(outcome=outcome, reason=reason)
    if diagnostics is not None:
        diagnostics.append(record)
    return outcome, reason
