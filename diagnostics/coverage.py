#!/usr/bin/env python3
"""Offline construction inventory, NEVER a TSEP assessment. Apache-2.0.

HTMLParser supplies an exploratory inventory, not the TS01 extractor. No decision
code is imported. Candidate limits can be incomplete or imprecise on broken HTML.
"""
import argparse
from collections import Counter
import hashlib
from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from conformance.http import message, text_body, body_digest
from provenance.runtime import runtime_identity

VERSION = '1'
MAX_SOURCE = 8*1024*1024
MAX_EVENTS = 100000
MAX_DEPTH = 256
SPACE = ' \t\r\n\f'
VOID = set('area base br col embed hr img input link meta param source track wbr'.split())
UNSUPPORTED = set('math plaintext xmp noembed noframes iframe frameset frame listing '
                  'table caption colgroup tbody thead tfoot tr td th select option optgroup'.split())
SVG = set('svg g path rect circle ellipse line polyline polygon use symbol defs clippath mask '
          'lineargradient radialgradient stop animate animatetransform set'.split())


class Inventory(HTMLParser):
    # Treat these as raw spans for inventory only; no decoded text is emitted.
    CDATA_CONTENT_ELEMENTS = ('script', 'style', 'title', 'textarea', 'noscript', 'template')

    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.tags, self.findings, self.stack = Counter(), {}, []
        self.events = self.roots = 0

    def event(self):
        self.events += 1
        if self.events > MAX_EVENTS:
            raise ValueError('Diagnostic event limit reached')

    def flag(self, code):
        row = self.findings.setdefault(code, {'code': code, 'occurrences': 0,
                                            'first_line': self.getpos()[0], 'first_column': self.getpos()[1]})
        row['occurrences'] += 1

    def start(self, tag, attrs, closed):
        self.event()
        self.tags[tag] += 1
        if tag == 'html':
            self.roots += 1
        if tag in UNSUPPORTED:
            self.flag('context:'+tag)
        if (tag == 'svg' or 'svg' in self.stack) and tag not in SVG:
            self.flag('svg-context:'+tag)
        if len({key for key, _ in attrs}) != len(attrs):
            self.flag('duplicate-attribute')
        if closed and tag not in VOID and tag != 'svg' and 'svg' not in self.stack:
            self.flag('nonvoid-self-closing:'+tag)
        if not closed and tag not in VOID:
            self.stack.append(tag)
            if len(self.stack) > MAX_DEPTH:
                raise ValueError('Diagnostic depth limit reached')

    def handle_starttag(self, tag, attrs):
        self.start(tag, attrs, False)

    def handle_startendtag(self, tag, attrs):
        self.start(tag, attrs, True)

    def handle_endtag(self, tag):
        self.event()
        if not self.stack or self.stack[-1] != tag:
            self.flag('structural-recovery')
            # Recovery is exclusively diagnostic; observations after it are tentative.
            if tag in self.stack:
                self.stack = self.stack[:len(self.stack)-1-self.stack[::-1].index(tag)]
        else:
            self.stack.pop()

    def handle_data(self, data):
        self.event()
        tag = self.stack[-1] if self.stack else None
        if tag in ('textarea', 'noscript', 'template') and data.strip(SPACE):
            self.flag('nonempty:'+tag)
        if tag == 'script' and '<!--' in data:
            self.flag('escaped-script')
        if 'svg' in self.stack and data.strip(SPACE):
            self.flag('svg-text')
        if tag not in self.CDATA_CONTENT_ELEMENTS and '<' in data:
            self.flag('literal-less-than')
        if not self.stack and data.strip(SPACE):
            self.flag('text-outside-root')

    def handle_entityref(self, name):
        self.event()
        if 'svg' in self.stack:
            self.flag('svg-text')

    handle_charref = handle_entityref

    def handle_comment(self, data):
        self.event()
        if data.startswith(('>', '->')) or '--' in data or '<!' in data:
            self.flag('ambiguous-comment')

    def handle_decl(self, decl):
        self.event()
        if not re.fullmatch(r'doctype[ \t\r\n\f]+html[ \t\r\n\f]*', decl, re.I | re.ASCII):
            self.flag('declaration')

    def unknown_decl(self, data):
        self.flag('declaration')

    def handle_pi(self, data):
        self.flag('processing-instruction')


def inspect_source(source):
    if len(source) > MAX_SOURCE:
        raise ValueError('Diagnostic source limit reached')
    parser = Inventory()
    stopped = None
    try:
        parser.feed(source)
        parser.close()
    except (ValueError, AssertionError, RecursionError) as error:
        stopped = str(error)
    if parser.stack or parser.roots != 1 or not re.search(r'</html\s*>\s*$', source, re.I):
        parser.flag('incomplete-or-ambiguous-structure')
    if '\x00' in source:
        parser.flag('literal-nul')
    return {'scan_completed': stopped is None, 'scan_limit': stopped,
            'tag_counts': dict(sorted(parser.tags.items())),
            'candidate_limits': [parser.findings[key] for key in sorted(parser.findings)]}


def surface(record):
    result = {'available': False}
    try:
        hops = record.get('http', [])
        if not isinstance(hops, list) or not hops or hops[-1].get('complete') is not True:
            raise ValueError('No complete last recorded response')
        status, headers, body = message(hops[-1]['response'], True)
        media = headers.get('content-type', [])
        result.update(last_recorded_status=status, content_type=media, decoded_body_sha256=body_digest(body))
        if len(media) != 1 or not re.fullmatch(r'text/html\s*;\s*charset\s*=\s*(?:utf-8|"utf-8")\s*', media[0], re.I | re.ASCII):
            raise ValueError('Diagnostic requires one explicit text/html UTF-8 content type')
        result.update(inspect_source(text_body(body)), available=True)
    except (ValueError, KeyError, TypeError, AttributeError) as error:
        result['unavailable_reason'] = str(error)
    return result


def diagnose(raw):
    if len(raw) > 16*1024*1024:
        raise ValueError('Diagnostic input limit reached')
    data = json.loads(raw)
    targets = data.get('targets')
    if data.get('input_version') not in ('1', '2') or not isinstance(targets, list) or not 1 <= len(targets) <= 100:
        raise ValueError('Expected captures input v1/v2 with 1–100 targets')
    pages = []
    for target in targets:
        if not isinstance(target, dict) or not isinstance(target.get('url'), str):
            raise ValueError('Invalid diagnostic target')
        current = surface(target)
        prior = surface(target.get('reference', {}))
        comparable = 'content_type' in prior and 'content_type' in current
        pages.append({'url': target['url'], 'reference': prior, 'evaluation': current,
                      'content_type_headers_differ': prior['content_type'] != current['content_type'] if comparable else None})
    codes = sorted({item['code'] for page in pages for phase in ('reference', 'evaluation')
                    for item in page[phase].get('candidate_limits', [])})
    matrix = [{'construction': code, 'evaluation_pages': sum(any(i['code'] == code for i in page['evaluation'].get('candidate_limits', [])) for page in pages),
               'reference_pages': sum(any(i['code'] == code for i in page['reference'].get('candidate_limits', [])) for page in pages)} for code in codes]
    files = ('diagnostics/coverage.py', 'conformance/http.py', 'provenance/runtime.py', 'tsep.py')
    return {'kind': 'diagnostic-only', 'diagnostic_version': VERSION, 'coverage_reference': 'TS01 interpreter 4; inventory maintained separately',
            'input_sha256': hashlib.sha256(raw).hexdigest(), 'runtime': runtime_identity(),
            'source_sha256': {name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in files},
            'network_requests': 0, 'pages': pages, 'construction_matrix': matrix,
            'scope': 'Exploratory inventory of the last retained response only. No trace validation, marker test or TSEP verdict. Counts describe this sample only.',
            'limitations': 'HTMLParser may recover or tokenize differently from the interpreter. Candidates are not exhaustive; empty lists do not establish evaluability. Broken markup and runtime differences can affect inventory.'}


def render(data, language='fr'):
    fr = language == 'fr'
    title = 'Diagnostic de couverture HTML' if fr else 'HTML coverage diagnostic'
    note = ('Inventaire exploratoire, aucun verdict TSEP. Une liste vide ne prouve pas que la page est évaluable. '
            'Fréquences limitées aux captures fournies ; aucun nouvel accès réseau.' if fr else
            'Exploratory inventory, no TSEP verdict. An empty list does not establish evaluability. Frequencies describe supplied captures only; no new network access.')
    out = '<!doctype html><html lang="'+language+'"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'unsafe-inline\'"><title>'+title+'</title>'
    out += '<style>body{font:16px system-ui;max-width:1100px;margin:40px auto;padding:0 20px;color:#172b38;background:#f7f9fa}h1{font-size:32px}table{width:100%;border-collapse:collapse;background:white}th,td{border:1px solid #bdc9d0;padding:10px;text-align:left}pre{white-space:pre-wrap;overflow-wrap:anywhere}aside{padding:18px;border-left:5px solid #ad6800;background:#fff3d6}details{margin:16px 0}code{overflow-wrap:anywhere}summary{cursor:pointer;font-weight:600}</style><body><h1>'+title+'</h1><aside>'+note+'</aside>'
    out += '<p>SHA-256 · <code>'+data['input_sha256']+'</code></p><table><thead><tr><th>Construction</th><th>'+('Pages · référence' if fr else 'Pages · reference')+'</th><th>'+('Pages · mesure' if fr else 'Pages · evaluation')+'</th></tr></thead><tbody>'
    for row in data['construction_matrix']:
        out += '<tr><td>'+escape(row['construction'])+'</td><td>'+str(row['reference_pages'])+'</td><td>'+str(row['evaluation_pages'])+'</td></tr>'
    out += '</tbody></table><h2>'+('Détail des captures' if fr else 'Capture details')+'</h2>'
    for page in data['pages']:
        out += '<details><summary>'+escape(page['url'])+'</summary><pre>'+escape(json.dumps(page, ensure_ascii=False, indent=2))+'</pre></details>'
    out += '<details><summary>'+('Méthode et limites' if fr else 'Method and limits')+'</summary><pre>'+escape(json.dumps({k:v for k,v in data.items() if k not in ('pages','construction_matrix')},ensure_ascii=False,indent=2))+'</pre></details></body></html>'
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    try:
        with args.input.open('rb') as handle:
            raw = handle.read(16*1024*1024+1)
        data = diagnose(raw)
        args.output_dir.mkdir(exist_ok=False)
        files = {'input.json': raw, 'diagnostic.json': (json.dumps(data, ensure_ascii=False, indent=2)+'\n').encode()}
        files.update({'diagnostic-'+lang+'.html': render(data, lang).encode() for lang in ('fr', 'en')})
        for name, value in files.items():
            (args.output_dir/name).write_bytes(value)
        (args.output_dir/'SHA256SUMS').write_text(''.join(hashlib.sha256(files[name]).hexdigest()+'  '+name+'\n' for name in sorted(files)))
        print(json.dumps({'kind': data['kind'], 'pages': len(data['pages']), 'output': str(args.output_dir), 'input_sha256': data['input_sha256']}))
    except (ValueError, OSError, TypeError, AttributeError) as error:
        print(json.dumps({'error': str(error), 'kind': 'diagnostic-error'}), file=sys.stderr)
        return 64
    return 0


if __name__ == '__main__':
    sys.exit(main())
