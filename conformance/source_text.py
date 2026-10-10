"""Bounded TS01 source-text extraction, not an HTML DOM or visibility engine.

Apache-2.0. Explicit lexical states; HTMLParser and TS07 are not involved.
Unsupported syntax aborts the whole extraction before any marker comparison.
"""
import html
import re

from conformance.http import Unknown, need

SPACE = ' \t\r\n\f'
MAX_CHARS = 8 * 1024 * 1024
MAX_TAG = 65536
MAX_DEPTH = 256
MAX_TOKENS = 100000
NAME = re.compile(r'[A-Za-z][A-Za-z0-9:_-]*', re.ASCII)
VOID = frozenset('area base br col embed hr img input link meta param source track wbr'.split())
# These contexts require tree-construction, scripting or unresolved text semantics.
UNSUPPORTED = frozenset('math plaintext xmp noembed noframes iframe frameset frame listing '
                        'table caption colgroup tbody thead tfoot tr td th select option optgroup'.split())
SVG = frozenset('svg g path rect circle ellipse line polyline polygon use symbol defs '
                'clippath mask lineargradient radialgradient stop animate animatetransform set'.split())
RAW = frozenset(('script', 'style', 'title', 'textarea', 'noscript', 'template'))
CLOSE = {tag: re.compile(r'</'+tag+r'(?=[ \t\r\n\f/>])', re.I | re.ASCII) for tag in RAW}
CHARREF = re.compile(r'&(?:#[0-9]+;?|#[xX][0-9a-fA-F]+;?|[^\t\n\f <&#;]{1,32};?)')


def characters(value):
    """Decode references without dropping numeric controls/noncharacters.

    html.unescape removes some numeric code points that HTML tokenization retains.
    Keep those exact characters; replace only NUL, surrogates and overflow.
    """
    def decode(match):
        token = match[0]
        if not token.startswith('&#'):
            return html.unescape(token)
        digits = token[2:].rstrip(';')
        base = 16 if digits.startswith(('x', 'X')) else 10
        digits = (digits[1:] if base == 16 else digits).lstrip('0') or '0'
        number = int(digits, base) if len(digits) <= (6 if base == 16 else 7) else 0x110000
        if number == 0 or number > 0x10ffff or 0xd800 <= number <= 0xdfff:
            return '\ufffd'
        if 0x80 <= number <= 0x9f:
            return html.unescape('&#'+str(number)+';')
        return chr(number)
    return CHARREF.sub(decode, value)


def tag_at(source, offset):
    """Parse one bounded tag; no attribute value is returned as source text."""
    endtag = source.startswith('</', offset)
    i = offset + (2 if endtag else 1)
    match = NAME.match(source, i)
    need(match is not None, 'Unsupported HTML tag syntax at character '+str(offset))
    name, i = match[0].lower(), match.end()
    attributes = set()
    while i < len(source):
        need(i-offset <= MAX_TAG, 'HTML tag size limit exceeded')
        before = i
        while i < len(source) and source[i] in SPACE:
            i += 1
        need(i < len(source), 'Incomplete HTML tag: '+name)
        if source[i] == '>':
            need(i-offset <= MAX_TAG, 'HTML tag size limit exceeded')
            return name, endtag, False, i+1
        if source.startswith('/>', i):
            need(not endtag, 'Self-closing end tag: '+name)
            need(i+1-offset <= MAX_TAG, 'HTML tag size limit exceeded')
            return name, False, True, i+2
        need(not endtag, 'Attributes on an HTML end tag: '+name)
        need(i > before, 'Missing whitespace before HTML attribute: '+name)
        start = i
        while i < len(source) and source[i] not in SPACE+'=/>':
            need(source[i] not in '<\"\'`', 'Unsupported HTML attribute name: '+name)
            i += 1
            need(i-offset <= MAX_TAG, 'HTML tag size limit exceeded')
        need(i > start, 'Empty HTML attribute name: '+name)
        attribute_end = i
        attribute = source[start:i].lower()
        need(attribute not in attributes, 'Duplicate HTML attribute: '+attribute)
        attributes.add(attribute)
        while i < len(source) and source[i] in SPACE:
            i += 1
        if i < len(source) and source[i] == '=':
            i += 1
            while i < len(source) and source[i] in SPACE:
                i += 1
            need(i < len(source), 'Incomplete HTML attribute: '+name)
            if source[i] in '\"\'':
                quote = source[i]
                end = source.find(quote, i+1, min(len(source), offset+MAX_TAG+1))
                need(end >= 0, 'Incomplete or excessive quoted HTML attribute: '+name)
                i = end+1
            else:
                start = i
                while i < len(source) and source[i] not in SPACE+'>':
                    need(source[i] not in '<\"\'`=', 'Unsupported unquoted HTML attribute: '+name)
                    i += 1
                    need(i-offset <= MAX_TAG, 'HTML tag size limit exceeded')
                need(i > start, 'Empty unquoted HTML attribute: '+name)
        else:
            # Leave the separator for the next attribute iteration.
            i = attribute_end
    raise Unknown('Incomplete HTML tag: '+name)


def extract(source):
    """Return exact textual segments or Unknown. Never return a partial prefix."""
    need(isinstance(source, str) and len(source) <= MAX_CHARS, 'HTML source size limit exceeded')
    need('\x00' not in source, 'NUL in HTML source is unsupported')
    segments, stack = [], []
    roots = tokens = i = 0
    doctype = False
    while i < len(source):
        tokens += 1
        need(tokens <= MAX_TOKENS, 'HTML token limit exceeded')
        if source[i] != '<':
            end = source.find('<', i)
            end = len(source) if end < 0 else end
            value = source[i:end]
            need(stack or not value.strip(SPACE), 'Text outside HTML root')
            if stack:
                if 'svg' in stack:
                    need(not value.strip(SPACE), 'Text in SVG is unsupported')
                segments.append(characters(value))
            i = end
            continue
        if source.startswith('<!--', i):
            end = source.find('-->', i+4)
            need(end >= 0, 'Unclosed HTML comment')
            value = source[i+4:end]
            need(not value.startswith(('>', '->')) and '--' not in value and '<!' not in value,
                 'Ambiguous HTML comment is unsupported')
            i = end+3
            continue
        if source[i:i+9].lower() == '<!doctype':
            end = source.find('>', i+9)
            need(not doctype and roots == 0 and end >= 0 and
                 re.fullmatch(r'<!doctype[ \t\r\n\f]+html[ \t\r\n\f]*>', source[i:end+1], re.I | re.ASCII),
                 'Unsupported HTML declaration')
            doctype, i = True, end+1
            continue
        need(not source.startswith(('<!', '<?'), i), 'Unsupported HTML declaration or processing instruction')
        tag, closing, self_closing, end = tag_at(source, i)
        if closing:
            need(stack and stack[-1] == tag, 'HTML requires structural recovery at closing '+tag)
            stack.pop()
            i = end
            continue
        need(tag not in UNSUPPORTED, 'Unsupported HTML context: '+tag)
        if tag == 'html':
            need(not stack and roots == 0, 'Ambiguous HTML root')
            roots += 1
        else:
            need(stack, 'Element outside HTML root: '+tag)
        if tag in ('head', 'body'):
            need(stack == ['html'], 'Unsupported HTML structural context: '+tag)
        foreign = tag == 'svg' or 'svg' in stack
        if foreign:
            need(tag in SVG or tag == 'style', 'Unsupported SVG context: '+tag)
            if tag == 'style':
                need('body' in stack and 'head' not in stack,
                     'SVG style outside explicit HTML body is unsupported')
        need(not self_closing or foreign or tag in VOID, 'Non-void self-closing HTML: '+tag)
        if tag in VOID or self_closing:
            i = end
            continue
        stack.append(tag)
        need(len(stack) <= MAX_DEPTH, 'HTML nesting limit exceeded')
        if tag in RAW:
            # Delimiter-aware closing, not a JavaScript/CSS string parser. Inert
            # script escape/double-escape states remain deliberately unsupported.
            close = CLOSE[tag].search(source, end)
            need(close is not None, 'Unclosed HTML text context: '+tag)
            stop = close.start()
            value = source[end:stop]
            if foreign and tag == 'style':
                # SVG style uses foreign-content tokenization, not HTML RAWTEXT.
                # Reject every literal '<' before the closing tag: markup can
                # break out of SVG, even inside CSS strings/comments. CDATA and
                # HTML comments remain outside this deliberately small subset.
                need('<' not in value, 'Markup in SVG style is unsupported')
            elif tag == 'script':
                need('<!--' not in value, 'Escaped script data is unsupported')
            elif tag == 'title':
                if value:
                    segments.append(characters(value))
            elif tag in ('textarea', 'noscript', 'template'):
                need(not value.strip(SPACE), 'Nonempty HTML context is unsupported: '+tag)
                if value:
                    segments.append(value)
            name, is_end, slash, after = tag_at(source, stop)
            need(name == tag and is_end and not slash, 'Unsupported closing text context: '+tag)
            stack.pop()
            i = after
        else:
            i = end
    need(roots == 1 and not stack, 'Incomplete HTML structure')
    return segments
