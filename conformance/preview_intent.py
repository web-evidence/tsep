"""Prior bounded preview permissions, never Google display or content-use guarantees."""
import json
import re
from conformance.http import need

READER = 'google-preview-intent-v1'
VERSION = '1'
KEYS = ('max_snippet', 'max_video_preview', 'max_image_preview')
IMAGE = ('none', 'standard', 'large')
LIMIT = 2147483647
INF = LIMIT + 1
MAX_VALUES, MAX_BYTES, MAX_TOKENS = 128, 262144, 4096
LOWER = str.maketrans('ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')
NAMES = {'max-snippet', 'max-video-preview', 'max-image-preview', 'unavailable_after',
         'indexifembedded', 'index', 'noindex', 'follow', 'nofollow', 'all', 'none', 'nosnippet'}


def rank(key, value):
    if key == 'max_image_preview':
        need(type(value) is str and value in IMAGE, 'Invalid preview image bound')
        return IMAGE.index(value)
    need(type(value) is int and -1 <= value <= LIMIT, 'Preview bound must be an integer -1 or 0..2147483647')
    return INF if value == -1 else value


def external(key, value):
    return IMAGE[value] if key == 'max_image_preview' else (-1 if value == INF else value)


def goals(intent):
    need(intent.get('presentation_reader') == READER, 'Unknown presentation_reader; no fallback')
    need(intent.get('directive_crawler', intent.get('crawler')) == 'googlebot', 'Only Googlebot text-results semantics implemented')
    need(intent.get('indexing') in ('allow', 'exclude'), 'Missing indexing intent')
    need(intent.get('following', 'unspecified') in ('allow', 'disallow', 'unspecified'), 'Unknown link intent')
    obj = intent.get('presentation')
    need(type(obj) is dict and bool(obj) and set(obj) <= set(KEYS), 'Nonempty supported presentation objective required')
    result = {}
    for key, limits in obj.items():
        need(type(limits) is dict and bool(limits) and set(limits) <= {'minimum', 'maximum'}, 'Preview dimension requires minimum and/or maximum')
        lo = rank(key, limits['minimum']) if 'minimum' in limits else 0
        hi = rank(key, limits['maximum']) if 'maximum' in limits else (2 if key == 'max_image_preview' else INF)
        need(lo <= hi, 'Reversed preview intention interval')
        result[key] = (lo, hi)
    return result


def compare(possible, expected):
    low, high = possible
    minimum, maximum = expected
    if high < minimum or low > maximum:
        return 'fail'
    if low >= minimum and high <= maximum:
        return 'pass'
    return 'inconclusive'


def assess(headers, values, intent):
    expected = goals(intent)
    need(type(values) is list and all(type(v) is str for v in values), 'Malformed metadata values')
    fields = headers.get('x-robots-tag', [])
    need(type(fields) is list and all(type(v) is str for v in fields), 'Malformed X-Robots-Tag values')
    need(len(values) + len(fields) <= MAX_VALUES, 'Preview field count exceeds bound')
    need(sum(len(v.encode('utf-8')) for v in values + fields) <= MAX_BYTES, 'Preview values exceed byte bound')
    entries, issues = [], []
    caps = {key: [] for key in KEYS}
    uncertain = set()
    index_unknown = follow_unknown = False
    tokens = set()
    count = 0

    def unknown(reason, dimensions=KEYS, index=False, following=False):
        nonlocal index_unknown, follow_unknown
        uncertain.update(dimensions)
        index_unknown = index_unknown or index
        follow_unknown = follow_unknown or following
        issues.append(reason)

    for origin, supplied in (('meta', values), ('http', fields)):
        for number, raw in enumerate(supplied):
            entry = {'origin': origin, 'index': number, 'raw': raw, 'scope': 'unscoped', 'tokens': []}
            entries.append(entry)
            value = raw.translate(LOWER).strip(' \t')
            if any(ord(c) < 32 and c != '\t' or ord(c) == 127 for c in value):
                unknown('Unsupported control character', index=True, following=True)
                continue
            parts = value.split(',')
            count += len(parts)
            need(count <= MAX_TOKENS, 'Preview token count exceeds bound')
            # A combined field cannot silently discard a later crawler scope.
            later_scope = any(re.match(r'^\s*([a-z][a-z0-9_-]*):', p) and
                              re.match(r'^\s*([a-z][a-z0-9_-]*):', p)[1] not in NAMES for p in parts[1:])
            if later_scope:
                unknown('Inline or repeated crawler scope is unsupported', index=True, following=True)
                entry['scope'] = 'unknown'
                continue
            if origin == 'http':
                scope = re.match(r'^([a-z][a-z0-9_-]*):[ \t]*(.*)$', value)
                if scope and scope[1] not in NAMES:
                    entry['scope'] = scope[1]
                    if scope[1] != 'googlebot':
                        entry['excluded'] = True
                        continue
                    parts = scope[2].split(',')
            for part in parts:
                token = part.strip(' \t')
                if not token:
                    continue
                entry['tokens'].append(token)
                if token in ('index', 'noindex', 'follow', 'nofollow', 'all', 'none', 'nosnippet'):
                    tokens.add(token)
                    continue
                name, separator, parameter = token.partition(':')
                if name in ('max-snippet', 'max-video-preview', 'max-image-preview'):
                    key = name.replace('-', '_')
                    parameter = parameter.strip(' \t')
                    if key == 'max_image_preview':
                        valid = separator and parameter in IMAGE
                        number_value = IMAGE.index(parameter) if valid else None
                    else:
                        valid = separator and bool(re.fullmatch(r'-1|[0-9]{1,10}', parameter))
                        number_value = int(parameter) if valid else None
                        valid = valid and -1 <= number_value <= LIMIT
                        if valid and number_value == -1:
                            number_value = INF
                    if valid:
                        caps[key].append(number_value)
                    else:
                        unknown('Unqualified ' + name + ' parameter', (key,))
                elif name in ('indexifembedded', 'unavailable_after'):
                    unknown('Embedding/time context not assessed', (), index=True)
                else:
                    unknown('Unknown directive; see retained raw entry', index=True, following=True)

    excluded = bool(tokens & {'noindex', 'none'})
    nofollow = bool(tokens & {'nofollow', 'none'})
    nosnippet = 'nosnippet' in tokens
    if nosnippet:
        caps['max_snippet'].append(0)
        caps['max_video_preview'].append(0)
    ambiguous_video = 0 in caps['max_snippet'] and not nosnippet
    intervals = {}
    for key in KEYS:
        high = min(caps[key]) if caps[key] else (2 if key == 'max_image_preview' else INF)
        is_unknown = key in uncertain or (key == 'max_image_preview' and not caps[key]) or (key == 'max_video_preview' and ambiguous_video)
        intervals[key] = (0 if is_unknown else high, high)
    decisions = {'indexing': {'outcome': 'inconclusive' if index_unknown else ('pass' if excluded == (intent['indexing'] == 'exclude') else 'fail')},
                 'following': {'outcome': 'not-assessed' if intent.get('following', 'unspecified') == 'unspecified' else ('inconclusive' if follow_unknown else ('pass' if nofollow == (intent['following'] == 'disallow') else 'fail'))}}
    for key, wanted in expected.items():
        actual = intervals[key]
        decisions[key] = {'outcome': 'inconclusive' if excluded else compare(actual, wanted),
                          'possible_cap': [external(key, n) for n in actual],
                          'intended_cap': dict(intent['presentation'][key])}
        if excluded:
            decisions[key]['limitation'] = 'noindex/none present; preview applicability not established'
        if key == 'max_video_preview' and ambiguous_video:
            decisions[key]['limitation'] = 'max-snippet:0 video interaction unresolved; both documented readings retained'
        if key == 'max_image_preview' and not caps[key]:
            decisions[key]['limitation'] = 'Image default is not mapped to standard or large'
    outcomes = [v['outcome'] for v in decisions.values()]
    outcome = 'fail' if 'fail' in outcomes else ('inconclusive' if 'inconclusive' in outcomes else 'pass')
    return {'reader': READER, 'policy_version': VERSION, 'outcome': outcome, 'decisions': decisions,
            'entries': entries, 'issues': issues,
            'scope': 'Declared directive permissions for supplied client representation only. No actual display, image availability, indexing, licensed/structured-data use, data-nosnippet or Google receipt assessment.'}


def result(headers, values, intent, diagnostics=None):
    record = assess(headers, values, intent)
    if diagnostics is not None:
        diagnostics.append(record)
    detail = {k: record[k] for k in ('decisions', 'scope')}
    detail['unqualified_items'] = len(record['issues'])
    return record['outcome'], READER + ': ' + json.dumps(detail, sort_keys=True, ensure_ascii=False)
