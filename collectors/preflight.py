"""Reference preparation checks, distinct from TSEP rule outcomes. Apache-2.0."""
import hashlib
import json
import os
from conformance.evaluate import identity_text
from conformance.http import Unknown, body_digest
from conformance import source_markers
from experiments import source_http

VERSION = '5'


def marker_reader(options, policy):
    """Absence selects legacy; explicit null/unknown is a configuration error."""
    if 'identity_reader' not in options:
        return None
    if policy != 'markers' or options['identity_reader'] not in source_markers.READERS:
        raise ValueError('identity_reader requires markers policy and a supported html-tree-markers reader')
    return options['identity_reader']


def reference_check(headers, body, policy, required=(), forbidden=(), *, identity_reader=None):
    if identity_reader is not None:
        marker_reader({'identity_reader': identity_reader}, policy)
    result = {'preflight_version': VERSION, 'state': 'not-requested',
              'decoded_body_sha256': body_digest(body), 'content_type': headers.get('content-type', []),
              'scope': 'Preparation of supplied reference only; not TS01 assessment, human approval or semantic correctness.'}
    if policy != 'markers':
        result['reason'] = 'Digest/stable policy: reference markers were not requested.'
        return result
    if not isinstance(required, list) or not required or not isinstance(forbidden, list):
        raise ValueError('Reference markers require a positive required marker')
    if identity_reader is not None:
        marker_reader({'identity_reader': identity_reader}, policy)
        objective = {'required_markers': required, 'forbidden_markers': forbidden}
        # Validate bounds before any quadratic substring comparison or parsing.
        source_markers.reader.criteria(objective)
        try:
            runtime_probe = source_http.inventory(
                b'<!doctype html><html><head></head><body></body></html>',
                content_types=['text/html; charset=utf-8'], node=os.environ.get('TSEP_SOURCE_NODE'))['runtime']
        except (ValueError, OSError, KeyError, TypeError) as error:
            raise ValueError('Parsed-marker preparation requires a usable Node 24/parser runtime: '+str(error)) from error
        diagnostics = []
        outcome, reason = source_markers.assess(headers, body,
            dict(objective, identity_reader=identity_reader), diagnostics=diagnostics)
        record = diagnostics[0]
        measured_runtime = record.get('parser', {}).get('runtime')
        if measured_runtime is not None and measured_runtime != runtime_probe:
            raise ValueError('Parsed-marker runtime changed during reference preparation')
        contradictions = [mode for mode, reading in record.get('hypotheses', {}).items()
                          if reading.get('complete') is True and reading.get('outcome') == 'fail']
        result.update(state={'pass': 'matches', 'fail': 'contradiction', 'inconclusive': 'unavailable'}[outcome],
                      identity_reader=identity_reader, reason=reason[:4096], reason_truncated=len(reason) > 4096,
                      runtime_probe=runtime_probe, contradictory_hypotheses=contradictions,
                      diagnostic_sha256=hashlib.sha256(json.dumps(record, ensure_ascii=False,
                          sort_keys=True, separators=(',', ':')).encode('utf-8')).hexdigest(),
                      diagnostic_storage='Reconstructible from retained reference, criteria, exact tools and recorded runtime; not stored in full in this receipt.',
                      source_sha256=record.get('source_sha256'),
                      parser={key: record.get('parser', {}).get(key) for key in ('parser', 'runtime', 'bounds')},
                      hypotheses={mode: {key: reading.get(key) for key in ('outcome', 'complete')}
                          for mode, reading in record.get('hypotheses', {}).items()})
        for mode, reading in record.get('hypotheses', {}).items():
            for field in ('missing_required', 'present_forbidden'):
                values = reading.get(field)
                result['hypotheses'][mode][field+'_count'] = len(values) if isinstance(values, list) else None
        if contradictions:
            result.update(state='contradiction',
                          reason='Guided preparation refuses a complete contradiction in any hypothesis: '+', '.join(contradictions))
        return result
    for values in (required, forbidden):
        if not all(isinstance(v, str) and v.strip() for v in values) or len(values) != len(set(values)):
            raise ValueError('Invalid or duplicate reference markers')
    if any(bad in good for good in required for bad in forbidden):
        raise ValueError('Contradictory reference markers')
    try:
        segments = identity_text(headers, body)
    except Unknown as error:
        result.update(state='unavailable', reason=str(error))
        return result
    missing = [marker for marker in required if not any(marker in segment for segment in segments)]
    present = [marker for marker in forbidden if any(marker in segment for segment in segments)]
    result.update(state='contradiction' if missing or present else 'matches',
                  missing_required=missing, present_forbidden=present,
                  reason='Literal markers checked on the complete supported reference source; no digest shortcut.')
    return result


def media_comparison(before, after):
    """Compare fields of two parsed responses, including observed absence.

    An unavailable response is handled by the caller, never represented as an
    empty header dictionary. Empty lists here mean the field was absent.
    """
    left, right = before.get('content-type', []), after.get('content-type', [])
    return {'reference': left, 'evaluation': right,
            'raw_headers_differ': left != right,
            'scope': 'Observed Content-Type fields only; spelling/parameter differences may be benign. Draft.7 does not bind expected media type.'}
