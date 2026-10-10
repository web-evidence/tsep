#!/usr/bin/env python3
"""Unapplied lexical SEO signal inventory, NEVER a TS07/TS10 assessment. Apache-2.0."""
import argparse
import hashlib
import html
from html.entities import html5
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import tsep
from conformance import http, source_text
from experiments import noscript
from provenance import runtime

VERSION = '2'
MODULES = {'experiments/noscript.py': noscript, 'conformance/source_text.py': source_text,
           'conformance/http.py': http, 'provenance/runtime.py': runtime, 'tsep.py': tsep}
ATTRIBUTE_SCOPE = ('Attribute-context character references; literal CRLF/CR become LF in '
                   'attribute values only. Raw source/tag offsets stay unchanged. Boolean '
                   'attributes retain null. No URL resolution or browser/DOM equivalence.')
NUMERIC = re.compile(r'&#(?:[xX][0-9a-fA-F]+|[0-9]+);?')
ENTITY_BOUND = max(map(len, html5))


def attribute_value(raw):
    """Decode references in an attribute, preserving ambiguous ampersands.

    Named matches use the longest table entry. Unlike text decoding, a name
    without semicolon followed by ASCII alphanumeric or '=' remains literal.
    Numeric conversion is bounded even for thousands of leading zeros/digits.
    """
    raw = raw.replace('\r\n', '\n').replace('\r', '\n')
    out, i = [], 0
    while i < len(raw):
        if raw[i] != '&':
            out.append(raw[i]); i += 1
            continue
        number = NUMERIC.match(raw, i)
        if number:
            spelling = number[0][2:].rstrip(';')
            base = 16 if spelling[:1].lower() == 'x' else 10
            digits = (spelling[1:] if base == 16 else spelling).lstrip('0') or '0'
            value = int(digits, base) if len(digits) <= 7 else 0x110000
            if value == 0 or value > 0x10ffff or 0xd800 <= value <= 0xdfff:
                out.append('\ufffd')
            elif 0x80 <= value <= 0x9f:
                out.append(html.unescape('&#'+str(value)+';'))
            else:
                out.append(chr(value))
            i = number.end()
            continue
        name = next((raw[i+1:end] for end in range(min(len(raw), i+1+ENTITY_BOUND), i+1, -1)
                     if raw[i+1:end] in html5), None)
        if name is None:
            out.append('&'); i += 1
            continue
        after = i+1+len(name)
        following = raw[after:after+1]
        ambiguous = (not name.endswith(';') and
                     (following == '=' or (following.isascii() and following.isalnum())))
        out.append('&'+name if ambiguous else html5[name])
        i = after
    return ''.join(out)


def attributes(raw):
    """Read attributes of an already tag_at-validated start tag, without recovery."""
    i = source_text.NAME.match(raw, 1).end()
    attrs = {}
    while i < len(raw):
        while raw[i] in source_text.SPACE:
            i += 1
        if raw[i] == '>' or raw.startswith('/>', i):
            break
        start = i
        while raw[i] not in source_text.SPACE+'=/>':
            i += 1
        name = raw[start:i].lower()
        while raw[i] in source_text.SPACE:
            i += 1
        value = None
        if raw[i] == '=':
            i += 1
            while raw[i] in source_text.SPACE:
                i += 1
            if raw[i] in ('"', "'"):
                quote = raw[i]; i += 1; start = i
                i = raw.index(quote, i)
                value = raw[start:i]; i += 1
            else:
                start = i
                while raw[i] not in source_text.SPACE+'>':
                    i += 1
                value = raw[start:i]
        attrs[name] = attribute_value(value) if value is not None else None
    return attrs


def inventory(source, mode):
    validated = noscript.reading(source, mode)
    if not validated['complete']:
        return {k: v for k, v in validated.items() if k != 'segments'} | {'signals': []}
    # A second lexical walk observes tags only after the complete source passed
    # the unchanged experiment. It mirrors its raw-context boundaries, not a DOM.
    stack, signals, i = [], [], 0
    while i < len(source):
        if source[i] != '<':
            end = source.find('<', i)
            i = len(source) if end < 0 else end
            continue
        if source.startswith('<!--', i):
            i = source.index('-->', i+4)+3
            continue
        if source[i:i+9].lower() == '<!doctype':
            i = source.index('>', i)+1
            continue
        tag, closing, self_closing, end = source_text.tag_at(source, i)
        if closing:
            http.need(stack and stack[-1] == tag, 'Inventory/validator stack mismatch')
            stack.pop()
            i = end
            continue
        if tag in ('meta', 'link'):
            raw = source[i:end]
            attrs = attributes(raw)
            kind = None
            if tag == 'meta' and (attrs.get('name') or '').lower() in ('robots', 'googlebot'):
                kind = 'robots-meta'
            elif tag == 'link' and 'canonical' in re.split('[ \t\r\n\f]+', (attrs.get('rel') or '').lower()):
                kind = 'canonical-link'
            if kind:
                signals.append({'kind': kind, 'start': i, 'end': end, 'raw_tag': raw,
                                'attributes': attrs, 'lexical_ancestors': list(stack)})
        if tag in source_text.VOID or self_closing:
            i = end
            continue
        stack.append(tag)
        if tag in ('script', 'style', 'title', 'textarea') or (tag == 'noscript' and mode == 'enabled'):
            close = source_text.CLOSE[tag].search(source, end)
            http.need(close is not None, 'Inventory/validator raw boundary mismatch')
            name, is_end, slash, after = source_text.tag_at(source, close.start())
            http.need(name == tag and is_end and not slash, 'Inventory/validator closing mismatch')
            stack.pop()
            i = after
        else:
            i = end
    http.need(not stack, 'Inventory/validator final stack mismatch')
    return {'mode': mode, 'complete': True, 'signals': signals,
            'completeness_scope': validated['completeness_scope']}


def experiment(source):
    http.need(isinstance(source, str) and len(source) <= noscript.MAX_CHARS,
              'Experimental source size limit exceeded')
    files = runtime.loaded_sources(ROOT, MODULES)
    files['experiments/seo_signals.py'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    readings = {mode: inventory(source, mode) for mode in ('enabled', 'disabled')}
    comparison = 'unavailable'
    if all(r['complete'] for r in readings.values()):
        comparison = ('identical' if readings['enabled']['signals'] == readings['disabled']['signals']
                      else 'different')
    http.need(runtime.loaded_sources(ROOT, MODULES) == {k: v for k, v in files.items()
                                                      if k != 'experiments/seo_signals.py'},
              'Reader sources changed during inventory')
    return {'kind': 'unapplied-seo-signal-inventory', 'experiment_version': VERSION,
            'reader_experiment_version': noscript.VERSION, 'normative_effect': 'none',
            'source_utf8_sha256': hashlib.sha256(source.encode('utf-8')).hexdigest(),
            'source_characters': len(source), 'readings': readings, 'inventory_comparison': comparison,
            'attribute_decoding_scope': ATTRIBUTE_SCOPE, 'runtime': runtime.runtime_identity(),
            'source_sha256': files, 'network_requests': 0,
            'scope': 'Lexical observations in two whole-source hypotheses. Python Unicode offsets, '
                     'zero-based, exclusive end. Ancestors are not DOM positions. Identical empty '
                     'inventories are not success. No directive effect, HTTP headers, robots access, '
                     'rendered state, canonical validity, TSEP outcome or engine behavior established.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        with args.source.open('rb') as handle:
            raw = handle.read(noscript.MAX_CHARS*4+1)
        http.need(len(raw) <= noscript.MAX_CHARS*4, 'UTF-8 input byte limit exceeded')
        result = experiment(raw.decode('utf-8'))
        with args.output.open('x', encoding='utf-8', newline='\n') as handle:
            json.dump(result, handle, ensure_ascii=False, indent=2)
            handle.write('\n')
        print(json.dumps({'kind': result['kind'], 'inventory_comparison': result['inventory_comparison'],
                          'complete_readings': {k: v['complete'] for k, v in result['readings'].items()}}))
    except (ValueError, OSError) as error:
        print(json.dumps({'kind': 'experiment-error', 'error': str(error)}), file=sys.stderr)
        return 64
    return 0


if __name__ == '__main__':
    sys.exit(main())
