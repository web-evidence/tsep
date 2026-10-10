"""Bounded structured rendered-state reader; supplied evidence, never a browser.

Apache-2.0. Inventory 2 is retained unchanged as the structural transport contract.
No source HTML recovery, execution authentication, collection or engine inference.
"""
import hashlib
import re

from experiments import rendered_metadata as inventory
from experiments.rendered_canonical import http_prefix, supported_url
from conformance.evaluate import binding_digest, need, text_present

VERSION = '1'
READER = 'structured-inventory-v2'
LEGACY = 'legacy-serialized-v1'


def reader(plan, state):
    chosen = plan.get('dom_reader', LEGACY)
    need(chosen in (LEGACY, READER), 'Unknown predeclared DOM reader')
    need(chosen != LEGACY or 'structured_dom' not in state,
         'Structured DOM requires a predeclared reader; no legacy fallback')
    return chosen


class Surface:
    def __init__(self, state, final_url, http, crawler):
        value = state.get('structured_dom')
        need(isinstance(value, dict) and set(value) == {
            'snapshot', 'snapshot_sha256', 'known_integrity_issues', 'acquisition'},
            'Missing/malformed structured DOM envelope')
        record = value['snapshot']
        need(isinstance(record, dict) and set(record) == {'script_sha256', 'tree'},
             'Malformed structured snapshot')
        need(record['script_sha256'] == inventory.script_digest(), 'Different structured capture script')
        need(value['snapshot_sha256'] == binding_digest(record), 'Structured snapshot fingerprint mismatch')
        self.facts = inventory.inventory(record['tree'])
        self.tree = record['tree']
        need(value['known_integrity_issues'] == [], 'Unknown integrity history or known DOM API issue')
        need(self.tree['document_url'] == final_url, 'Structured document URL mismatch')
        need(self.tree['traversal_complete'] and not self.tree['api_errors']
             and self.tree['ready_state'] in ('interactive', 'complete'),
             'Incomplete/failed structured traversal or document still loading')
        serial = self.tree['serialization']
        need(isinstance(serial, dict) and serial.get('available') is True,
             'Missing complete serialization companion for review')
        need('dom' not in state or state['dom'] == serial['html'],
             'Conflicting serialized DOM companion')
        roots = [n['id'] for n in self.tree['nodes'] if n['type'] == 1
                 and n['parent'] == 0 and n['namespace'] == inventory.HTML and n['name'] == 'html']
        heads = [n['id'] for n in self.tree['nodes'] if n['type'] == 1
                 and n['parent'] in roots and n['namespace'] == inventory.HTML and n['name'] == 'head']
        need(len(roots) == len(heads) == 1, 'Ambiguous structured document head')
        acquisition = value['acquisition']
        need(isinstance(acquisition, dict), 'Missing acquisition attribution')
        kind = acquisition.get('kind')
        need(kind in ('authored-synthetic', 'same-navigation'),
             'Separate/unknown HTTP and DOM acquisitions cannot establish one rendered representation')
        need(text_present(acquisition.get('navigation_id'))
             and acquisition.get('http_sha256') == binding_digest(http), 'Navigation/HTTP binding mismatch')
        need(acquisition.get('user_agent') == crawler, 'Navigation agent differs from HTTP assessment agent')
        support = acquisition.get('support')
        need(isinstance(support, list) and 1 <= len(support) <= 16, 'Missing acquisition supporting record')
        for item in support:
            need(isinstance(item, dict) and text_present(item.get('name'))
                 and text_present(item.get('content')) and len(item['content'].encode('utf-8')) <= 65536
                 and item.get('sha256') == hashlib.sha256(item['content'].encode('utf-8')).hexdigest(),
                 'Missing/tampered acquisition supporting record')
        self.detail = ('structured-inventory-v2; acquisition=' + kind
                       + '; supplied attribution, APIs and navigation not independently authenticated; '
                       'one declared state, frames/templates/closed shadow outside coverage')

    @property
    def directives(self):
        rows = [r for r in self.facts['metadata'] if r['kind'] == 'robots']
        need(all(r['position'] == 'head-direct' for r in rows),
             'Rendered robots meta outside direct document head or in shadow requires review')
        need(all(isinstance(r['content'], str) for r in rows), 'Missing rendered robots content')
        return [r['content'] for r in rows]

    @property
    def canonicals(self):
        need(supported_url(self.tree['document_url']), 'Unsupported structured canonical document URL')
        rows = [r for r in self.facts['metadata'] if r['kind'] == 'canonical']
        values = []
        for row in rows:
            need(row['position'] != 'open-shadow', 'Shadow canonical interpretation not established')
            raw, resolved = row['raw_href'], row['resolved_href']
            need(isinstance(resolved, str), 'Missing resolved canonical URL')
            need(raw is None or not http_prefix(raw) or raw == resolved,
                 'Absolute raw/resolved canonical difference requires review; neither value substituted')
            values.append((raw, row['position'] == 'head-direct'))
        return values

    @property
    def anchors(self):
        # Inventory 2 records raw anchors but not their resolved href property.
        # Resolve only the declared legacy URL subset with unchanged document base.
        need(self.tree['base_uri'] == self.tree['document_url']
             and not any(r['kind'] == 'base' for r in self.facts['metadata']),
             'Changed/base URL requires a separately supported link-resolution method')
        values = []
        for row in self.facts['elements']:
            if row['namespace'] != inventory.HTML or row['local_name'] != 'a':
                continue
            attributes = {a['local_name']: a['value'] for a in row['attributes'] if a['namespace'] is None}
            if 'href' not in attributes:
                continue
            need(row['position'] != 'open-shadow', 'Shadow anchor interpretation not established')
            href = attributes['href']
            need(not re.search(r'[^\x21-\x7e]|[\\<>"`{}|^]', href)
                 and not re.search(r'%(?![0-9a-fA-F]{2})', href), 'Unsupported structured anchor syntax')
            values.append(href)
        return values
