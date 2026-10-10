"""Shared bounded canonical-attribute classification; no HTML or engine execution."""
import re
from conformance.http import need

VERSION = '1'
DECLARATION = frozenset(('rel', 'href'))
INCIDENTAL = frozenset(('id', 'class'))
GOOGLE_MODIFIERS = frozenset(('lang', 'hreflang', 'media', 'type'))
CUSTOM = re.compile(r'(?:data|aria)-[a-z][a-z0-9_.-]*\Z')


def classification(names):
    """Names are already HTML-lowercased; namespaced attributes never use this path."""
    result = {'declaration': [], 'incidental': [], 'google_modifiers': [], 'unsupported': []}
    for name in names:
        kind = ('declaration' if name in DECLARATION else 'incidental'
                if name in INCIDENTAL or CUSTOM.fullmatch(name) else 'google_modifiers'
                if name in GOOGLE_MODIFIERS else 'unsupported')
        result[kind].append(name)
    return result


def check(names, *, historical_reason=False):
    names = list(names)
    need(len(names) == len(set(names)), 'Duplicate canonical attributes')
    result = classification(names)
    # Source refusal wording is retained for historical raw-case/reason stability.
    need(not result['google_modifiers'], 'Unsupported canonical attributes' if historical_reason else
         'Canonical modifiers not used by the documented Google policy; bounded interpretation remains inconclusive: ' + ', '.join(result['google_modifiers']))
    need(not result['unsupported'], 'Unsupported canonical attributes' if historical_reason else
         'Unsupported structured canonical attributes: ' + ', '.join(result['unsupported']))
    return result
