#!/usr/bin/env python3
"""Unapplied noscript experiment: two bounded whole-source hypotheses, no TSEP verdict.

Apache-2.0. Derived from the lexical structure of conformance/source_text.py v5.
This deliberately separate reader must not be used by the normative interpreter.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from conformance.http import Unknown, need
from conformance.source_text import characters, tag_at, SPACE, VOID, SVG, CLOSE
from provenance.runtime import runtime_identity

VERSION = '2'
MAX_CHARS = 8*1024*1024
MAX_TOKENS = 100000
MAX_DEPTH = 256
HEAD = frozenset('base link meta title style script noscript'.split())
HEAD_NOSCRIPT = frozenset('link meta style'.split())
BODY = frozenset('a abbr address article aside audio b bdi bdo blockquote br button '
                 'canvas cite code data datalist dd del details dfn dialog div dl dt em '
                 'fieldset figcaption figure footer form h1 h2 h3 h4 h5 h6 header hgroup '
                 'hr i img input ins kbd label legend li link main map mark menu meta '
                 'meter nav noscript ol output p picture pre progress q rp rt ruby s '
                 'samp search section small source span strong style sub summary sup '
                 'script time track u ul var video wbr'.split()) - {'rp', 'rt', 'ruby'}
CLOSES_P = frozenset('address article aside blockquote details dialog div dl fieldset '
                     'figcaption figure footer form h1 h2 h3 h4 h5 h6 header hgroup hr '
                     'main menu nav ol p pre search section ul'.split())
HEADINGS = frozenset(('h1', 'h2', 'h3', 'h4', 'h5', 'h6'))
SOURCE_FILES = ('experiments/noscript.py', 'conformance/source_text.py',
                'conformance/http.py', 'provenance/runtime.py', 'tsep.py')


def reading(source, mode):
    """Return source ranges only after the whole bounded reading succeeds.

    Offsets are zero-based Python Unicode code points, with an exclusive end.
    They identify the source slice before entity decoding, not byte/DOM offsets.
    """
    need(mode in ('enabled', 'disabled'), 'Unknown experimental scripting hypothesis')
    segments, stack = [], []
    roots = tokens = i = 0
    doctype = head_seen = body_seen = False

    def append(start, end, decode=True):
        if end > start:
            value = source[start:end]
            segments.append({'start': start, 'end': end,
                             'text': characters(value) if decode else value,
                             'decoding': 'character-references' if decode else 'literal-rawtext'})

    try:
        need(isinstance(source, str) and len(source) <= MAX_CHARS, 'Experimental source size limit exceeded')
        need('\x00' not in source, 'NUL in source is unsupported')
        while i < len(source):
            tokens += 1
            need(tokens <= MAX_TOKENS, 'Experimental token limit exceeded')
            if source[i] != '<':
                end = source.find('<', i)
                end = len(source) if end < 0 else end
                value = characters(source[i:end])
                if not stack or stack == ['html'] or 'head' in stack or 'svg' in stack:
                    need(not value.strip(SPACE), 'Text requires unsupported structural processing')
                if stack:
                    append(i, end)
                i = end
                continue
            if source.startswith('<!--', i):
                end = source.find('-->', i+4)
                need(end >= 0, 'Unclosed comment')
                value = source[i+4:end]
                need(not value.startswith(('>', '->')) and '--' not in value and '<!' not in value,
                     'Ambiguous comment')
                i = end+3
                continue
            if source[i:i+9].lower() == '<!doctype':
                end = source.find('>', i+9)
                need(not doctype and roots == 0 and end >= 0 and
                     re.fullmatch(r'<!doctype[ \t\r\n\f]+html[ \t\r\n\f]*>', source[i:end+1], re.I | re.ASCII),
                     'Unsupported declaration')
                doctype, i = True, end+1
                continue
            need(not source.startswith(('<!', '<?'), i), 'Unsupported declaration')
            tag, closing, self_closing, end = tag_at(source, i)
            if closing:
                need(stack and stack[-1] == tag, 'Structural recovery at closing '+tag)
                stack.pop()
                i = end
                continue
            if tag == 'html':
                need(not stack and roots == 0, 'Ambiguous root')
                roots += 1
            elif tag == 'head':
                need(stack == ['html'] and not head_seen and not body_seen, 'Ambiguous head')
                head_seen = True
            elif tag == 'body':
                need(stack == ['html'] and head_seen and not body_seen, 'Ambiguous body')
                body_seen = True
            else:
                need('head' in stack or 'body' in stack, 'Element outside explicit head/body')
                if 'svg' in stack or tag == 'svg':
                    need('body' in stack and (tag in SVG or tag == 'style'), 'Unsupported foreign context: '+tag)
                elif 'head' in stack:
                    allowed = HEAD_NOSCRIPT if 'noscript' in stack else HEAD
                    need(tag in allowed, 'Unsupported head context: '+tag)
                else:
                    need(tag in BODY, 'Unsupported body context: '+tag)
                    need(not (tag in CLOSES_P and 'p' in stack), 'Implied paragraph closing is unsupported')
                    need(not (tag in ('a', 'button', 'form', 'nobr') and tag in stack),
                         'Repeated active context is unsupported: '+tag)
                    # A new nested list has its own item scope. An ancestor li
                    # beyond ul/ol/menu is valid, not an omitted sibling close.
                    list_start = max((j for j, t in enumerate(stack) if t in ('ul', 'ol', 'menu')), default=-1)
                    need(not (tag == 'li' and 'li' in stack[list_start+1:]),
                         'Unclosed item in the current list scope')
                    need(not (tag in ('dt', 'dd') and any(t in stack for t in ('dt', 'dd'))),
                         'Implied description-item closing is unsupported')
                    need(not (tag in HEADINGS and any(t in stack for t in HEADINGS)),
                         'Implied heading closing is unsupported')
                    need(not (tag == 'noscript' and 'noscript' in stack), 'Nested noscript is unsupported')
            foreign = tag == 'svg' or 'svg' in stack
            need(not self_closing or foreign or tag in VOID, 'Non-void self-closing element: '+tag)
            if tag in VOID or self_closing:
                i = end
                continue
            stack.append(tag)
            need(len(stack) <= MAX_DEPTH, 'Experimental nesting limit exceeded')
            raw = tag in ('script', 'style', 'title') or (tag == 'noscript' and mode == 'enabled')
            if not raw:
                i = end
                continue
            close = CLOSE[tag].search(source, end)
            need(close is not None, 'Unclosed text context: '+tag)
            stop = close.start()
            value = source[end:stop]
            if foreign and tag == 'style':
                need('<' not in value, 'Markup in SVG style is unsupported')
            elif tag == 'script':
                need('<!--' not in value, 'Escaped script data is unsupported')
            elif tag == 'title':
                append(end, stop)
            elif tag == 'noscript':
                append(end, stop, decode=False)
            name, is_end, slash, after = tag_at(source, stop)
            need(name == tag and is_end and not slash, 'Unsupported closing text context')
            stack.pop()
            i = after
        need(roots == 1 and head_seen and body_seen and not stack, 'Incomplete explicit document')
        return {'mode': mode, 'complete': True, 'segments': segments,
                'completeness_scope': 'Entire source within experimental lexical subset; not HTML5 tree/DOM completeness.'}
    except (Unknown, ValueError) as error:
        return {'mode': mode, 'complete': False, 'segments': [], 'reason': str(error),
                'refusal_context_offset': i,
                'completeness_scope': 'No partial prefix is eligible for candidate marker comparison.'}


def validate_criteria(criteria):
    need(isinstance(criteria, dict) and set(criteria) == {'required_markers', 'forbidden_markers'},
         'Expected exactly required_markers and forbidden_markers')
    for markers in criteria.values():
        need(isinstance(markers, list) and len(markers) <= 64 and
             all(isinstance(m, str) and m.strip() and len(m) <= 4096 for m in markers) and
             len(markers) == len(set(markers)), 'Invalid experimental markers')
    need(any(criteria.values()), 'No experimental marker criteria')
    need(not any(bad in good for good in criteria['required_markers'] for bad in criteria['forbidden_markers']),
         'Contradictory experimental markers')


def marker_candidate(reading_result, criteria):
    if not reading_result['complete']:
        return {'candidate': 'inconclusive', 'reason': 'Incomplete experimental reading'}
    evidence = {}
    for field, markers in criteria.items():
        evidence[field] = []
        for marker in markers:
            hits = [{'segment': i, 'text_start': s['text'].find(marker),
                     'text_end': s['text'].find(marker)+len(marker)}
                    for i, s in enumerate(reading_result['segments']) if marker in s['text']]
            evidence[field].append({'marker': marker, 'matches': hits})
    missing = [r['marker'] for r in evidence['required_markers'] if not r['matches']]
    forbidden = [r['marker'] for r in evidence['forbidden_markers'] if r['matches']]
    candidate = 'fail' if missing or forbidden else 'pass' if criteria['required_markers'] else 'inconclusive'
    return {'candidate': candidate, 'missing': missing, 'forbidden': forbidden, 'evidence': evidence}


def experiment(source, criteria=None):
    need(isinstance(source, str) and len(source) <= MAX_CHARS, 'Experimental source size limit exceeded')
    if criteria is not None:
        validate_criteria(criteria)
    readings = {mode: reading(source, mode) for mode in ('enabled', 'disabled')}
    consensus = None
    if criteria is not None:
        for item in readings.values():
            item['markers'] = marker_candidate(item, criteria)
        candidates = [r['markers']['candidate'] for r in readings.values()]
        consensus = candidates[0] if candidates[0] == candidates[1] and candidates[0] in ('pass', 'fail') else 'inconclusive'
    return {'kind': 'unapplied-noscript-experiment', 'experiment_version': VERSION,
            'normative_effect': 'none', 'source_utf8_sha256': hashlib.sha256(source.encode('utf-8')).hexdigest(),
            'source_characters': len(source), 'criteria': criteria, 'readings': readings,
            'candidate_consensus': consensus, 'runtime': runtime_identity(),
            'source_sha256': {name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in SOURCE_FILES},
            'network_requests': 0,
            'scope': 'Two global bounded lexical hypotheses over unchanged complete source. No HTTP identity, URL/digest precedence, browser execution, TSEP verdict, rendered visibility or certification.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--criteria', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        with args.source.open('rb') as handle:
            raw = handle.read(MAX_CHARS*4+1)
        need(len(raw) <= MAX_CHARS*4, 'UTF-8 input byte limit exceeded')
        criteria = None
        if args.criteria:
            with args.criteria.open('rb') as handle:
                criteria_raw = handle.read(1024*1024+1)
            need(len(criteria_raw) <= 1024*1024, 'Criteria byte limit exceeded')
            criteria = json.loads(criteria_raw)
        result = experiment(raw.decode('utf-8'), criteria)
        with args.output.open('x', encoding='utf-8') as handle:
            json.dump(result, handle, ensure_ascii=False, indent=2)
            handle.write('\n')
        print(json.dumps({'kind': result['kind'], 'candidate_consensus': result['candidate_consensus'],
                          'complete_readings': {k: v['complete'] for k, v in result['readings'].items()}}))
    except (ValueError, OSError) as error:
        print(json.dumps({'kind': 'experiment-error', 'error': str(error)}), file=sys.stderr)
        return 64
    return 0


if __name__ == '__main__':
    sys.exit(main())
