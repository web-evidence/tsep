"""Reference preparation checks, distinct from TSEP rule outcomes. Apache-2.0."""
from conformance.evaluate import identity_text
from conformance.http import Unknown, body_digest

VERSION = '2'


def reference_check(headers, body, policy, required=(), forbidden=()):
    result = {'preflight_version': VERSION, 'state': 'not-requested',
              'decoded_body_sha256': body_digest(body), 'content_type': headers.get('content-type', []),
              'scope': 'Preparation of supplied reference only; not TS01 assessment, human approval or semantic correctness.'}
    if policy != 'markers':
        result['reason'] = 'Digest/stable policy: reference markers were not requested.'
        return result
    if not isinstance(required, list) or not required or not isinstance(forbidden, list):
        raise ValueError('Reference markers require a positive required marker')
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
