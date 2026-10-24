"""Opt-in TS01 parsed-source marker policy; no implicit migration or browser claim."""
import base64
import zlib
import hashlib
import json
import os

from conformance.http import Unknown, need
from experiments import source_markers as reader

READER = 'html-tree-markers-v1'
CONTENT_READER = 'html-tree-markers-v2'
CURRENT_CONTENT_READER = 'html-tree-markers-v3'
READERS = (READER, CONTENT_READER, CURRENT_CONTENT_READER)
VERSION = '3'
MAX_DIAGNOSTIC_BYTES = 4 * 1024 * 1024
MAX_PROJECTION_BYTES = 32 * 1024 * 1024


def observe(raw, *, content_types, objective=None, node=None, selected):
    """V2 excludes noscript from marker matching, including later rechecks."""
    need(selected in READERS, 'Unsupported identity_reader; no historical fallback')
    observed = reader.observe(raw, content_types=content_types, objective=objective, node=node,
                              content_profile=selected == CURRENT_CONTENT_READER)
    if selected == CONTENT_READER:
        for row in observed['readings'].values():
            if not row['complete']:
                continue
            kept = []
            for segment in row['segments']:
                if any(a['name'] == 'noscript' for a in segment['ancestors']):
                    row['excluded'].append(dict(segment, reason='V2: noscript excluded from content markers'))
                else:
                    kept.append(segment)
            row['segments'] = kept
            if objective is not None:
                row.update(reader.compare(kept, objective))
        outcomes = [observed['readings'][m]['candidate_outcome'] for m in reader.MODES]
        observed['candidate_consensus'] = (None if objective is None else outcomes[0]
            if outcomes[0] == outcomes[1] and outcomes[0] in ('pass', 'fail') else 'inconclusive')
    return observed


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
    if observed.get('projection_profile') == 'main-document-html-v3':
        result['compression_runtime']={'build':zlib.ZLIB_VERSION,'runtime':zlib.ZLIB_RUNTIME_VERSION}
        for row in result['hypotheses'].values():
            payload={k:row.pop(k) for k in ('segments','excluded','contexts')}
            raw=json.dumps(payload,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode('utf-8')
            need(len(raw)<=MAX_PROJECTION_BYTES,'Complete V3 projection exceeds 32 MiB; no partial diagnostic')
            row['projection']={'encoding':'zlib-json-v1','raw_bytes':len(raw),
                               'sha256':hashlib.sha256(raw).hexdigest(),
                               'data':base64.b64encode(zlib.compress(raw,9)).decode('ascii')}
    return result


def expand_projection(row):
    if 'projection' not in row:
        return row
    need(not any(k in row for k in ('segments','excluded','contexts')),'Mixed raw and compressed projection')
    p=row['projection']
    need(type(p) is dict and set(p)=={'encoding','raw_bytes','sha256','data'} and p['encoding']=='zlib-json-v1' and
         type(p['raw_bytes']) is int and 0<p['raw_bytes']<=MAX_PROJECTION_BYTES,
         'Invalid V3 projection envelope')
    need(type(p['data']) is str and len(p['data'])<=4*((MAX_DIAGNOSTIC_BYTES+2)//3),'Encoded projection exceeds bound')
    encoded=base64.b64decode(p['data'],validate=True)
    need(base64.b64encode(encoded).decode('ascii')==p['data'],'Noncanonical projection base64')
    need(len(encoded)<=MAX_DIAGNOSTIC_BYTES,'Compressed projection exceeds bound')
    decoder=zlib.decompressobj()
    try:raw=decoder.decompress(encoded,p['raw_bytes']+1)
    except zlib.error as error:raise ValueError('Invalid compressed projection') from error
    need(len(raw)==p['raw_bytes'] and decoder.eof and not decoder.unconsumed_tail and not decoder.unused_data and
         hashlib.sha256(raw).hexdigest()==p['sha256'],'Projection length, digest or compressed framing differs')
    def pairs(items):
        value={}
        for k,v in items:
            need(k not in value,'Duplicate projection JSON key');value[k]=v
        return value
    def invalid(value):raise ValueError('Nonfinite projection JSON value')
    payload=json.loads(raw,object_pairs_hook=pairs,parse_constant=invalid)
    need(json.dumps(payload,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode('utf-8')==raw,'Noncanonical projection JSON')
    need(type(payload) is dict and set(payload)=={'segments','excluded','contexts'},'Unexpected projection fields')
    return dict({k:v for k,v in row.items() if k!='projection'},**payload)


def verify_projection(observed, packed):
    """Check every retained record before admitting the compact diagnostic."""
    inventory=observed['inventory']
    expected={'observer_version':observed['experiment_version'],'source_sha256':observed['source_sha256'],
              'content_types':observed['content_types'],
              'parser':{k:v for k,v in inventory.items() if k not in ('readings','kind','normative_effect','source_sha256')}}
    permitted=set(expected)|{'hypotheses'}
    if observed.get('projection_profile')=='main-document-html-v3':permitted.add('compression_runtime')
    need(set(packed)==permitted and all(packed[k]==v for k,v in expected.items()),'Compact projection identity or parser metadata differs')
    if observed.get('projection_profile')=='main-document-html-v3':
        need(packed.get('compression_runtime')=={'build':zlib.ZLIB_VERSION,'runtime':zlib.ZLIB_RUNTIME_VERSION},'Projection compression runtime differs')
    need(set(packed['hypotheses']) == set(reader.MODES), 'Compact marker hypotheses differ')
    for mode in reader.MODES:
        original = observed['readings'][mode]
        need(('projection' in packed['hypotheses'][mode])==(observed.get('projection_profile')=='main-document-html-v3'),'Projection encoding differs from selected reader')
        row = expand_projection(packed['hypotheses'][mode])
        used_contexts=set()
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
                used_contexts.add(index)
                expanded = {k: v for k, v in record.items() if k != 'context_id'}
                expanded['ancestors'] = row['contexts'][index]
                need(expanded == expected, 'Compact projection differs from attributed record')
        need(used_contexts==set(range(len(row['contexts']))),'Unused compact projection contexts')
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
    need(json.dumps(packed,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False)==
         json.dumps(compact(observed),sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False),
         'Compact projection canonical representation differs')


def assess(headers, body, intent, *, diagnostics=None):
    """Preserve URL/hash/stability precedence; bound criteria before comparison."""
    selected = intent.get('identity_reader')
    record = {'kind': 'ts01-source-marker-assessment',
              'reader': selected if selected in READERS else '[unsupported; see supplied intent]',
              'policy_version': VERSION,
              'scope': 'Whole-document static alternatives; literal parsed segments, not visibility, '
                       'semantic sufficiency, actual DOM, browser or search-engine behavior.'}
    try:
        need(selected in READERS, 'Unsupported identity_reader; no historical fallback')
        objective = {k: intent.get(k, []) for k in ('required_markers', 'forbidden_markers')}
        reader.criteria(objective)
        need(objective['required_markers'] or objective['forbidden_markers'],
             'Body digest changed without stable policy or identity markers')
        raw = body if type(body) is bytes else body.encode('utf-8')
        record['body_sha256'] = hashlib.sha256(raw).hexdigest()
        observed = observe(raw, content_types=headers.get('content-type', []),
                           objective=objective, node=os.environ.get('TSEP_SOURCE_NODE'), selected=selected)
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
        reason = selected + ': ' + '; '.join(reasons)
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
