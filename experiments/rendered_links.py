"""Strict observation transport reader. No evaluator, URL parser or network."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = 'collectors/rendered_links.js'
RECIPE = 'tests/fixtures/rendered-links-v1.json'
HTML = 'http://www.w3.org/1999/xhtml'
XLINK = 'http://www.w3.org/1999/xlink'
LIMITS = dict(nodes=65536, depth=128, records=8192, record_bytes=262144,
              records_bytes=4194304, string_bytes=262144, attributes=256, cooperative_ms=2000)
COVERAGE = dict(frames='not-entered', templates='not-entered', closed_shadow='unknown',
                slots='not-expanded', order='physical-light-then-open-shadow', origin='unknown',
                execution_context='not-attested', atomicity='not-attested')
TOP = set(('format version limits coverage document_before document_after records nodes_visited '
           'traversal_complete stop_reason errors elapsed_ms').split())
RECORD = set(('order visit path ancestors tag namespace selected_reason attributes node_base_uri '
              'shadow_root href_property').split())
FACTS = set('url base_uri character_set content_type ready_state'.split())
STOPS = set(('time-limit depth-limit node-limit repeated-node unavailable-api string-limit '
             'record-limit attribute-limit record-byte-limit records-byte-limit api-error').split())


def require(ok, message):
    if not ok:
        raise ValueError(message)


def encoded(value):
    # Match JSON.stringify UTF-8 accounting; surrogate escapes stay data, not repair.
    return json.dumps(value, ensure_ascii=False, separators=(',', ':')).encode('utf-8')


def string(value, nullable=False):
    if nullable and value is None:
        return
    require(isinstance(value, str), 'Unavailable string API')
    try:
        require(len(value.encode('utf-8')) <= LIMITS['string_bytes'], 'String byte bound')
    except UnicodeError as error:
        raise ValueError('Unpaired surrogate outside transport profile') from error


def attribute(record, name, namespace=None):
    return next((a['value'] for a in record['attributes']
                 if a['local_name'] == name and a['namespace'] == namespace), None)


def inventory(data):
    require(isinstance(data, dict) and set(data) == TOP, 'Observation fields')
    require(data['format'] == 'rendered-link-observation' and data['version'] == '1', 'Observation version')
    require(data['limits'] == LIMITS and data['coverage'] == COVERAGE, 'Unplanned limits/coverage')
    require(type(data['traversal_complete']) is bool, 'Complete flag')
    complete = data['traversal_complete']
    require(type(data['nodes_visited']) is int and 0 <= data['nodes_visited'] <= LIMITS['nodes'], 'Node count')
    require(type(data['elapsed_ms']) is int and data['elapsed_ms'] >= 0, 'Elapsed time')
    require(isinstance(data['errors'], list) and len(data['errors']) <= 1 and
            all(isinstance(e, str) and len(e) <= 256 for e in data['errors']), 'Error record')
    require((complete and data['stop_reason'] is None and not data['errors']) or
            (not complete and data['stop_reason'] in STOPS and len(data['errors']) == 1), 'Interruption state')
    for key in ('document_before', 'document_after'):
        facts = data[key]
        if facts is None:
            require(not complete, 'Missing document facts'); continue
        require(isinstance(facts, dict) and set(facts) == FACTS, 'Document fields')
        for value in facts.values():
            string(value)
        require(facts['ready_state'] in ('loading', 'interactive', 'complete'), 'Document ready state')
    records = data['records']
    require(isinstance(records, list) and len(records) <= LIMITS['records'], 'Record count')
    total = 2; paths = set(); last_visit = 0
    for i, record in enumerate(records):
        require(isinstance(record, dict) and set(record) == RECORD, 'Element fields')
        require(type(record['order']) is int and record['order'] == i and
                type(record['visit']) is int and last_visit < record['visit'] <= data['nodes_visited'], 'Record order')
        last_visit = record['visit']
        path = record['path']
        require(isinstance(path, list) and 0 < len(path) <= LIMITS['depth'] and
                all(p == 'shadow' if isinstance(p, str) else type(p) is int and 0 <= p < LIMITS['nodes'] for p in path), 'Physical path')
        require(tuple(path) not in paths, 'Duplicate physical path'); paths.add(tuple(path))
        require(isinstance(record['ancestors'], list) and len(record['ancestors']) <= len(path), 'Ancestors')
        for ancestor in record['ancestors']:
            require(isinstance(ancestor, dict) and set(ancestor) == {'tag', 'namespace'}, 'Ancestor fields')
            string(ancestor['tag']); string(ancestor['namespace'], True)
        string(record['tag']); string(record['namespace'], True); string(record['node_base_uri'])
        require(record['shadow_root'] in ('open', 'unexposed-or-absent'), 'Shadow label')
        attrs = record['attributes']; keys = set()
        require(isinstance(attrs, list) and len(attrs) <= LIMITS['attributes'], 'Attribute count')
        for a in attrs:
            require(isinstance(a, dict) and set(a) == {'name', 'local_name', 'namespace', 'value'}, 'Attribute fields')
            for key in ('name', 'local_name', 'value'):
                string(a[key])
            string(a['namespace'], True)
            key = (a['namespace'], a['local_name'])
            require(key not in keys, 'Duplicate attribute'); keys.add(key)
        named = record['tag'] in ('a', 'area', 'link', 'base', 'form', 'template', 'iframe', 'frame')
        override = record['namespace'] == HTML and record['tag'] in ('input', 'button') and attribute(record, 'formaction') is not None
        reason = 'named-element' if named else 'form-override' if override else 'open-shadow-host'
        require((named or override or record['shadow_root'] == 'open') and record['selected_reason'] == reason, 'Selection reason')
        href_api = record['namespace'] == HTML and record['tag'] in ('a', 'area', 'link', 'base')
        if href_api:
            string(record['href_property'])
        else:
            require(record['href_property'] is None, 'Unsupported href API')
        count = len(encoded(record))+1; total += count
        require(count <= LIMITS['record_bytes'] and total <= LIMITS['records_bytes'], 'Record byte bound')
    stable = data['document_before'] is not None and data['document_before'] == data['document_after']
    return dict(kind='rendered-link-inventory', version='1', normative_effect='none',
                traversal_complete=complete, document_facts_equal=stable,
                scope='Observed properties only; no validity, activation, origin authentication or TSEP verdict.',
                records=[dict(r, raw_href=attribute(r, 'href'), xlink_href=attribute(r, 'href', XLINK),
                              in_shadow='shadow' in r['path'],
                              foreign_ancestor=any(a['namespace'] != HTML for a in r['ancestors'])) for r in records])


def recipes():
    path = ROOT/RECIPE
    require(hashlib.sha256(path.read_bytes()).hexdigest() == path.with_suffix('.sha256').read_text().split()[0], 'Changed frozen recipe')
    return json.loads(path.read_bytes())


def projection(data):
    """Laboratory labels only; not a source-to-DOM node correspondence method."""
    result = {}
    for r in inventory(data)['records']:
        key = attribute(r, 'data-probe')
        if key is not None:
            require(key not in result, 'Duplicate laboratory label')
            result[key] = {k:r[k] for k in ('tag', 'namespace', 'raw_href', 'href_property', 'xlink_href', 'in_shadow', 'foreign_ancestor')}
    return result
