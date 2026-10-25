"""Google Web Search indexing directives, explicit dated v1 profile.

Static response semantics only: never a claim about Google fetching or indexing.
"""
import datetime as dt
import email.utils
import re
import tsep
from conformance.http import need

PROFILE = 'google-indexing-2026-10-v1'
SOURCE = 'https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag'
IGNORED = {'noarchive', 'nocache', 'nositelinkssearchbox'}
BARE = {'all', 'index', 'follow', 'noindex', 'nofollow', 'none', 'nosnippet',
        'noimageindex', 'notranslate', 'indexifembedded'}
PARAMS = {'max-snippet', 'max-image-preview', 'max-video-preview', 'unavailable_after'}


def tokens(value):
    # A comma after a weekday is part of RFC 822 / RFC 850 dates.
    for part in re.split(r',(?!(?:\s*\d{1,2}[ -][A-Za-z]{3}))', value):
        part = part.strip()
        if ':' not in part:
            yield from part.split()
        elif part:
            yield part


def expiry(value, observed_at):
    try:
        try:
            date = dt.datetime.fromisoformat(value.replace('Z', '+00:00').replace('z', '+00:00'))
        except ValueError:
            date = email.utils.parsedate_to_datetime(value)
    except (ValueError, TypeError, OverflowError):
        return 'invalid'
    if observed_at is None:
        return 'unresolved'
    observed = tsep.timestamp(observed_at)
    if date.tzinfo is None:
        # Do not silently assign a zone. Only decide outside every +/-24h zone.
        date = date.replace(tzinfo=dt.timezone.utc)
        if abs((observed-date).total_seconds()) <= 86400:
            return 'unresolved'
    return 'expired' if date <= observed else 'future'


def facts(headers, values, observed_at=None):
    record = {'reader': PROFILE, 'source': SOURCE, 'source_checked': '2026-10-25',
              'observed_at': observed_at, 'tokens': [], 'ignored': [], 'unknown': [],
              'expires': [], 'excluded': False, 'nofollow': False, 'uncertain_expiry': False}
    scoped = [(v, False) for v in values] + [(v, True) for v in headers.get('x-robots-tag', [])]
    for value, is_header in scoped:
        need(isinstance(value, str), 'Malformed directive value')
        scope = 'googlebot'
        for raw in tokens(value):
            token = raw.strip().lower()
            match = re.match(r'^([a-z][a-z0-9_-]*):\s*(.*)$', token)
            if is_header and match and match[1] not in PARAMS:
                scope, token = match.groups()
            if scope not in ('googlebot', 'robots'):
                record['ignored'].append({'value': raw, 'reason': 'other-crawler', 'crawler': scope})
                continue
            # A scoped header may contain several space-separated bare rules.
            candidates = token.split() if ':' not in token else [token]
            for token in candidates:
                if not token:
                    continue
                if token in IGNORED:
                    record['ignored'].append({'value': token, 'reason': 'not-used-by-google'})
                elif token in BARE:
                    record['tokens'].append(token)
                elif re.fullmatch(r'max-(?:snippet|video-preview):\s*(?:-1|[0-9]+)', token) or re.fullmatch(r'max-image-preview:\s*(?:none|standard|large)', token):
                    record['tokens'].append(token)
                elif token.startswith('unavailable_after:'):
                    state = expiry(re.search(r'unavailable_after:\s*(.*)$', raw, re.I)[1], observed_at)
                    record['expires'].append({'value': raw, 'state': state})
                    record['excluded'] |= state == 'expired'
                    record['uncertain_expiry'] |= state == 'unresolved'
                    if state == 'invalid':
                        record['ignored'].append({'value': raw, 'reason': 'invalid-date'})
                else:
                    record['unknown'].append(token)
    record['excluded'] |= bool(set(record['tokens']) & {'noindex', 'none'})
    record['nofollow'] = bool(set(record['tokens']) & {'nofollow', 'none'})
    record['scope'] = 'Standalone page, Googlebot web-search rules on the supplied representation; not actual indexing or embedded-content indexing.'
    return record


def result(headers, values, intent, observed_at=None, diagnostics=None):
    need(intent.get('directive_policy') == PROFILE, 'Unsupported directive policy')
    need(intent.get('directive_crawler', intent.get('crawler')) == 'googlebot', 'Only Googlebot web-search rules supported')
    need(intent.get('indexing') in ('allow', 'exclude'), 'Missing indexing intent')
    following = intent.get('following', 'unspecified')
    need(following in ('allow', 'disallow', 'unspecified'), 'Unknown link intent')
    need('presentation' not in intent, 'Presentation restrictions require their explicit profile')
    record = facts(headers, values, observed_at)
    unknown = bool(record['unknown']) or record['uncertain_expiry']
    outcomes = []
    for observed, wanted, requested in ((record['excluded'], intent['indexing']=='exclude', True),
                                        (record['nofollow'], following=='disallow', following!='unspecified')):
        if requested:
            outcomes.append(('pass' if observed == wanted else 'fail') if observed or not unknown else 'inconclusive')
    outcome = 'fail' if 'fail' in outcomes else 'inconclusive' if 'inconclusive' in outcomes else 'pass'
    record['outcome'] = outcome
    if diagnostics is not None:
        diagnostics.append(record)
    reason = 'Googlebot standalone-page directives: ' + ('exclusion present' if record['excluded'] else 'no established exclusion')
    if record['unknown']: reason += '; unrecognized: ' + ', '.join(record['unknown'])
    if record['ignored']: reason += '; ignored: ' + ', '.join(x['value'] for x in record['ignored'])
    if record['expires']: reason += '; dated restrictions: ' + ', '.join(x['state'] for x in record['expires'])
    return outcome, reason + '; compared with declared intent; not actual index state'
