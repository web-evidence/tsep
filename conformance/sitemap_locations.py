"""Bounded sitemap page-location reader, not an extension validator. Apache-2.0.

The optional profile is selected in prior intent. No URL normalization, fetching,
schema loading or inference about hreflang, images or engine processing.
"""
import io
import json
import re
import xml.etree.ElementTree as ET

from conformance.evaluate import Unknown, need, text_body, url_parts

VERSION = '1'
PROFILE = 'sitemap-locations-v1'
NS = '{http://www.sitemaps.org/schemas/sitemap/0.9}'
XHTML = '{http://www.w3.org/1999/xhtml}'
IMAGE = '{http://www.google.com/schemas/sitemap-image/1.1}'
SCHEMA_LOCATION = '{http://www.w3.org/2001/XMLSchema-instance}schemaLocation'
XML_SPACE = ' \t\r\n'
MAX_BYTES, MAX_NODES, MAX_DEPTH = 8 * 1024 * 1024, 200000, 8
MAX_ENTRIES, MAX_IMAGES = 50000, 1000


def whitespace(value):
    return value is None or not value.strip(XML_SPACE)


def leaf(element):
    need(not element.attrib and not len(element), 'Unsupported sitemap leaf structure')
    return element.text or ''


def read(body):
    text = text_body(body)
    need(len(text.encode('utf-8')) <= MAX_BYTES, 'Sitemap decoded-byte limit exceeded')
    need(not re.search(r'<!\s*(DOCTYPE|ENTITY)', text, re.I), 'DTD/entities unsupported')
    root, depth, nodes = None, 0, 0
    try:
        # Enforce tree bounds while parsing, before structural interpretation.
        for event, element in ET.iterparse(io.StringIO(text), events=('start', 'end')):
            if event == 'start':
                depth += 1; nodes += 1
                need(depth <= MAX_DEPTH and nodes <= MAX_NODES, 'Sitemap tree limit exceeded')
                if root is None:
                    root = element
            else:
                depth -= 1
                need(whitespace(element.tail), 'Unsupported sitemap mixed tail text')
    except ET.ParseError as error:
        raise Unknown('Incomplete/malformed sitemap XML: ' + str(error))
    need(root is not None and root.tag in (NS+'urlset', NS+'sitemapindex'),
         'Unsupported sitemap root/namespace')
    need(set(root.attrib) <= {SCHEMA_LOCATION} and whitespace(root.text),
         'Unsupported sitemap root attributes/text')
    index = root.tag == NS+'sitemapindex'
    need(len(root) <= MAX_ENTRIES, 'Sitemap entry limit exceeded')
    locations, annotations = [], []
    if SCHEMA_LOCATION in root.attrib:
        annotations.append({'entry_index': None, 'tag': SCHEMA_LOCATION,
                            'value': root.attrib[SCHEMA_LOCATION]})
    optional = {'lastmod'} if index else {'lastmod', 'changefreq', 'priority'}
    for position, entry in enumerate(root):
        need(entry.tag == NS+('sitemap' if index else 'url') and not entry.attrib
             and whitespace(entry.text), 'Unsupported sitemap entry structure')
        fields, images = {}, 0
        for child in entry:
            if child.tag in {NS+name for name in optional | {'loc'}}:
                need(child.tag not in fields, 'Duplicate sitemap base field')
                fields[child.tag] = leaf(child)
                if child.tag != NS+'loc':
                    annotations.append({'entry_index': position, 'tag': child.tag,
                                        'value': fields[child.tag]})
            elif not index and child.tag == XHTML+'link':
                need(set(child.attrib) == {'rel', 'hreflang', 'href'}
                     and child.attrib['rel'] == 'alternate'
                     and all(not whitespace(value) for value in child.attrib.values())
                     and not len(child) and whitespace(child.text),
                     'Unsupported XHTML sitemap annotation')
                annotations.append({'entry_index': position, 'tag': child.tag,
                                    'attributes': dict(child.attrib)})
            elif not index and child.tag == IMAGE+'image':
                images += 1
                need(images <= MAX_IMAGES, 'Sitemap image annotation limit exceeded')
                need(not child.attrib and whitespace(child.text), 'Unsupported image annotation structure')
                values = {}
                for item in child:
                    need(item.tag in {IMAGE+n for n in ('loc', 'caption', 'geo_location', 'title', 'license')}
                         and item.tag not in values, 'Unsupported/duplicate image annotation field')
                    values[item.tag] = leaf(item)
                need(IMAGE+'loc' in values and not whitespace(values[IMAGE+'loc']),
                     'Missing image annotation loc')
                annotations.append({'entry_index': position, 'tag': child.tag, 'fields': values})
            else:
                raise Unknown('Unsupported sitemap extension/element: ' + child.tag)
        need(NS+'loc' in fields and not whitespace(fields[NS+'loc']), 'Missing sitemap loc')
        location = fields[NS+'loc'].strip(XML_SPACE)
        url_parts(location)
        locations.append(location)
    return {'reader': PROFILE, 'reader_version': VERSION, 'index': index,
            'locations': locations, 'annotations': annotations,
            'scope': 'Direct base loc only; annotation values retained, not validated; no engine observation.'}


def summary(result):
    """Bounded report preview; complete values remain in the source and reader output."""
    rows = result['annotations']
    previews = []
    for row in rows[:16]:
        value = json.dumps(row, ensure_ascii=False, sort_keys=True)
        previews.append(value if len(value) <= 160 else value[:160]+' [truncated]')
    return (PROFILE + ': ' + str(len(result['locations'])) + ' direct base loc; '
            + str(len(rows)) + ' annotations retained outside page-location assessment; '
            + ' | '.join(previews)
            + ('; '+str(len(rows)-16)+' additional annotations not previewed' if len(rows)>16 else '')
            + '; no hreflang/image/value validation or engine-selection inference')
