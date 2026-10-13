"""TS31 native JSON-LD and bound supplied content review. Apache-2.0.

No collection, automatic semantic judgment, Google or vocabulary validation.
"""
import json
import os

import tsep
from conformance import inspection
from conformance.agent_policy import ERRORS, combine, digest, present
from conformance.http import need
from experiments import jsonld_rendered as native

VERSION = '1'
READER = 'jsonld-visible-content-v1'
PREFIX = 'Structured content evidence / preuves JSON-LD-contenu: '
RULES = ('TS31-A01', 'TS31-A02', 'TS31-A03')
MAX_BYTES = 8*1024*1024
MAX_NODES = 256
JUDGMENTS = ('visible_consistency', 'type_suitability', 'no_fabrication')


def stamp(value):
    return inspection.observer().stamp(value)


def text_record(record):
    raw = record['raw_text']
    need(type(raw) is str and bool(raw.strip()) and len(raw.encode('utf-8')) <= 512*1024,
         'Missing or excessive supplied text')
    need(record.get('sha256') == native.sha(raw), 'Supplied text fingerprint differs')
    return stamp(record['observed_at'])


def header(t):
    need(len(json.dumps(t, ensure_ascii=False, allow_nan=False).encode()) <= MAX_BYTES,
         'Structured-content input bound exceeded')
    need(type(t.get('structured_synthetic')) is bool, 'Explicit structured-data provenance required')
    need(all(present(t.get('context', {}).get(k)) for k in ('network','bounds','tool','tool_version')),
         'Missing structured-content context')
    c = t['intent']['structured_content']; p = t['jsonld']['plan']
    need(c.get('reader') == READER and c.get('important_properties') == 'all-supplied',
         'Explicit reader and all-supplied property scope required')
    need(all(present(c.get(k)) for k in ('selection_reason','population')), 'Missing prior scope')
    need(p.get('format') == 'jsonld-rendered-plan' and p.get('version') == '1', 'Unsupported prior plan')
    declared, start, end, observed = [stamp(v) for v in
        (p['declared_at'], p['window_start'], p['window_end'], t['observed_at'])]
    need(stamp(t['intent']['declared_at']) == declared and declared <= start <= end <= observed
         and end-start <= 86400*10**9, 'Plan/window/assessment chronology unqualified')
    need(t['url'] == p['start_url'] and present(p.get('crawler')), 'Target/client differs from plan')
    for key in ('start_url','final_url','source_base_iri'): native.processor.absolute(p[key])
    states = p['states']
    need(type(states) is list and 1 <= len(states) <= 16, 'Require 1–16 prior rendered states')
    ids = []
    for s in states:
        need(type(s) is dict and set(s) == {'id','browser','browser_version','scenario'}
             and all(native.named(v) for v in s.values()) and len(s['id']) <= 128,
             'Malformed prior state/scenario')
        ids.append(s['id'])
    need(len(set(ids)) == len(ids), 'Duplicate planned state')
    refs = c['guidance']; need(type(refs) is list and 1 <= len(refs) <= 16, 'Supplied type guidance required')
    for r in refs:
        native.processor.absolute(r['url']); need(text_record(r) <= declared, 'Guidance postdates plan')
    return c,p,declared,start,end,observed


def plan_binding(t):
    return digest(dict(url=t['url'],intent=t['intent'],plan=t['jsonld']['plan']))


def content_binding(t, sid, content, graph):
    q = t['jsonld']; states = [s for s in q['states'] if 'render:'+s['id'] == sid]
    need(not sid.startswith('render:') or len(states) == 1, 'Ambiguous review state')
    return digest(dict(url=t['url'],intent=t['intent'],plan=q['plan'],http=q['http'],
        http_received_at=q['http_received_at'],contexts=q['contexts'],surface_id=sid,
        state=states[0] if states else None,content=content,graph=graph))


def population(rows, key, wanted):
    need(type(rows) is list and len(rows) <= 256, 'Missing or excessive review population')
    actual = [r.get(key) if isinstance(r,dict) else None for r in rows]
    need(all(type(v) is type(wanted[0]) for v in actual) if wanted else not actual,
         'Malformed review population')
    need(len(set(actual)) == len(actual) and set(actual) == set(wanted),
         'Missing, duplicate or unplanned review population')
    return 'pass','Exact supplied review population',{}


def one(rows, key, value):
    need(type(rows) is list and len(rows) <= 256, 'Missing or excessive supplied reviews')
    found = [r for r in rows if isinstance(r,dict) and r.get(key) == value]
    need(len(found) == 1, 'Missing or ambiguous supplied review: '+str(value))
    return found[0]


class Evidence:
    def __init__(self, target, notes):
        self.t = target; self.notes = notes
        node = os.environ.get('TSEP_SOURCE_NODE')
        need(present(node), 'Explicit TSEP_SOURCE_NODE / Node 24 unavailable; no fallback')
        self.o = native.observe(target['jsonld'], node=node)
        notes['native'] = self.o

    def surfaces(self):
        q = self.t['jsonld']; source = self.o['source']
        for mode in ('enabled','disabled'):
            reading = source['readings'][mode] if source else None
            inv = source['source']['readings'][mode] if source else None
            proc = None
            if reading and reading['processing_index'] is not None:
                proc = source['processing']['documents'][reading['processing_index']]
            yield dict(id='source:'+mode, reading=reading, inventory=inv, processing=proc,
                       observed_at=q['http_received_at'], reason=self.o['source_error'])
        for s in self.o['states']:
            proc = next((v['observation']['documents'][0] for v in self.o['processing']
                         if v['state_id'] == s['id'] and v['observation']), None)
            yield dict(id='render:'+s['id'], reading=s['reading'], inventory=s['inventory'], processing=proc,
                       observed_at=s['inventory']['observed_at'] if s['inventory'] else None, reason=s['reason'])

    def qualify(self, s):
        r, inv = s['reading'], s['inventory']
        need(r and inv and inv.get('complete') is True, s['reason'] or 'Unavailable surface inventory')
        if s['id'].startswith('source:'):
            need(not inv['parse_errors'], 'HTML recovery prevents qualified source attribution')
        else:
            need(inv['authored'] == self.t['structured_synthetic'], 'DOM/target provenance differs')
        # The strict parser also rejects ambiguous duplicate keys. Those are unknown,
        # not proof of invalid JSON syntax. Only JSONDecodeError establishes this failure.
        scripts = {v['node_id']:v for v in inv['scripts']}
        for d in r['diagnostics']:
            if d['selection'] == 'selected' and d['status'] == 'json-error':
                try: native.processor.strict_json(scripts[d['node_id']]['payload'])
                except json.JSONDecodeError:
                    return 'fail','Invalid JSON syntax in an attributed selected script',{'surface':s['id'],'node_id':d['node_id']}
                except (ValueError,RecursionError): pass
        if r['status'] == 'absent':
            return 'pass','No selected script on this surface; not whole-page absence or NA',{'surface':s['id'],'nodes':0}
        need(r['status'] == 'processed' and s['processing'], 'Incomplete JSON-LD processing: '+r['status'])
        p = s['processing']
        need(p['status'] == 'observed' and not p['notices'], 'Unavailable processing or unresolved notices')
        graph = p['flattened']
        need(type(graph) is list and 1 <= len(graph) <= MAX_NODES, 'Empty or excessive flattened graph')
        return 'pass','Complete bounded processing; semantic/type review remains separate',{
            'surface':s['id'],'nodes':len(graph),'graph_sha256':digest(graph),'base_iri':p['base_iri']}


def assess(target, rule, *, diagnostics=None):
    obs = dict(reader=READER,version=VERSION,rule=rule,rows=[],inventories={},
        limitation='Supplied selected-page evidence/reviews only; no authenticated visibility, factual truth, Schema.org validation, rich result, indexing or ranking.')
    rows = obs['rows']
    def row(subject, fn):
        try:
            value = fn(); outcome,reason = value[:2]; detail = value[2] if len(value)>2 else {}
        except ERRORS + (OSError,) as error:
            outcome,reason,detail = 'inconclusive',str(error),{}
        rows.append(dict(detail,subject=subject,outcome=outcome,reason=reason))
    try:
        c,p,declared,start,end,observed = header(target)
        if rule == 'TS31-A01':
            review = inspection.review(target.get('structured_plan_review'),plan_binding(target),declared,start,target['structured_synthetic'])
            for key in ('scope','source_base','guidance'): row('plan:'+key,lambda key=key:inspection.judgment(review,key))
        elif rule in ('TS31-A02','TS31-A03'):
            e = Evidence(target,obs['inventories']); surfaces = list(e.surfaces())
            if e.o['unexpected_states']:
                rows.append(dict(subject='states',outcome='inconclusive',reason='Unplanned supplied states'))
            count = 0
            for s in surfaces:
                if rule == 'TS31-A02':
                    row(s['id'],lambda s=s:e.qualify(s))
                    if s['processing'] and s['processing']['flattened']: count += 1
                    continue
                try:
                    outcome,reason,detail = e.qualify(s)
                    need(outcome == 'pass', 'No complete graph for semantic review; syntax handled by A02')
                    if s['reading']['status'] == 'absent': continue
                    graph = s['processing']['flattened']; count += 1
                    record = one(target.get('structured_reviews'),'surface_id',s['id'])
                    content = record['content']; when = text_record(content)
                    need(content.get('kind') == 'supplied-visible-content-transcript' and present(content.get('method')),
                         'Supplied visible-content transcript/method required; no inferred CSS visibility')
                    need(stamp(s['observed_at']) <= when <= end, 'Content evidence outside surface/window chronology')
                    review = inspection.review(record.get('review'),content_binding(target,s['id'],content,graph),
                        when,observed,target['structured_synthetic'])
                    row(s['id']+':coverage',lambda review=review:inspection.judgment(review,'coverage'))
                    entities = record.get('entities')
                    row(s['id']+':population',lambda:population(entities,'index',list(range(len(graph)))))
                    for index,node in enumerate(graph):
                        def bound(index=index,node=node):
                            entity = one(entities,'index',index)
                            need(type(entity['index']) is int and entity.get('node_sha256') == digest(node), 'Entity review does not bind exact graph node')
                            return entity
                        try: entity = bound()
                        except ERRORS as error:
                            rows.append(dict(subject=s['id']+':entity:'+str(index),outcome='inconclusive',reason=str(error)));continue
                        for key in JUDGMENTS:
                            def judge(entity=entity,key=key):
                                v = entity[key]; need(present(v.get('reason')), 'Missing property qualification reason')
                                result = inspection.judgment(v,'value')
                                return result[0],result[1],dict(qualification=key,node_sha256=entity['node_sha256'],review_reason=v['reason'])
                            row(s['id']+':entity:'+str(index)+':'+key,judge)
                except ERRORS as error:
                    rows.append(dict(subject=s['id'],outcome='inconclusive',reason=str(error)))
            if count == 0: rows.append(dict(subject='applicability',outcome='inconclusive',reason='No nonempty qualified graph; absence is not NA'))
            if rule == 'TS31-A03':
                def review_scope():
                    records=target.get('structured_reviews');need(type(records) is list and len(records)<=18, 'Missing/excessive surface review population')
                    ids=[r.get('surface_id') if isinstance(r,dict) else None for r in records]
                    need(all(type(i) is str and i in {s['id'] for s in surfaces} for i in ids) and len(set(ids))==len(ids), 'Duplicate/unplanned surface review')
                    return 'pass','Supplied review identities fit prior surfaces'
                row('review-scope',review_scope)
        else: need(False,'Unsupported structured-content rule')
    except ERRORS + (OSError,) as error:
        rows.append(dict(subject='scope',outcome='inconclusive',reason=str(error)))
    obs['outcome'] = combine(rows)
    note = {k:v for k,v in obs.items() if k != 'inventories'}
    if diagnostics is not None: diagnostics.append(obs)
    return obs['outcome'],PREFIX+json.dumps(note,ensure_ascii=False,sort_keys=True)
