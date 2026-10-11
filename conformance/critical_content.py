"""TS44 prior critical scope, no-JS delivery and representation coherence.

Apache-2.0. Supplied evidence only; no provider ingestion or factual truth claim.
"""
from datetime import timedelta
import json
import os
import re
from urllib.parse import urlsplit

import tsep
from conformance.agent_policy import digest, present, identifier, combine, ERRORS
from conformance.agent_access import reviewed, origin
from conformance.http import need, Unknown, body_digest
from experiments import source_content, url_resolution
from experiments.rendered_canonical import supported_url

VERSION = '1'
READER = 'critical-content-nojs-v1'
ERRORS = ERRORS + (OSError,)
HTML = source_content.HTML


def plan_binding(target):
    return digest({'url': target['url'], 'intent': target['intent']})


def content_binding(target, subject):
    if subject.startswith('render:'):
        raw = unique(target['render']['states'], 'id', subject.split(':', 1)[1])
        source = target['http']
    else:
        raw = target['http'] if subject == 'page' else unique(target['documents'], 'id', subject)
        source = None
    return digest({'url': target['url'], 'intent': target['intent'], 'subject': subject,
                   'raw': raw, 'source_http': source})


def unique(rows, field, value):
    need(isinstance(rows, list) and len(rows) <= 64, 'Missing or excessive supplied records')
    found = [r for r in rows if isinstance(r, dict) and r.get(field) == value]
    need(len(found) == 1, 'Missing or ambiguous '+str(field)+': '+str(value))
    return found[0]


def text(value):
    need(isinstance(value, str) and len(value) <= 65536, 'Bounded string content required')
    return re.sub(r'[\t\n\r\f ]+', ' ', value).strip(' ')


def pointer_tokens(value):
    need(isinstance(value, str) and len(value) <= 1024 and
         (value == '' or value.startswith('/')) and not re.search(r'~(?![01])', value),
         'Unsupported JSON Pointer syntax; URI fragment form not selected')
    tokens = [s.replace('~1', '/').replace('~0', '~') for s in value.split('/')[1:]]
    need(len(tokens) <= 64, 'JSON Pointer depth exceeds bound')
    return tokens


def pointer(document, value):
    current = document
    for part in pointer_tokens(value):
        if type(current) is dict:
            if part not in current: return None
            current = current[part]
        elif type(current) is list:
            need(re.fullmatch(r'0|[1-9][0-9]{0,8}', part), 'Unqualified JSON array index')
            if int(part) >= len(current): return None
            current = current[int(part)]
        else:
            raise Unknown('JSON Pointer crosses a scalar; structure unqualified')
    need(isinstance(current, str), 'First JSON content profile requires string leaves')
    return text(current)


def header(target):
    p = target['intent']['critical_content']
    need(p['reader'] == READER and p.get('javascript') is False,
         'An explicit no-JavaScript reference is required; declared JS support cannot waive it')
    declared = tsep.timestamp(target['intent']['declared_at']); observed = tsep.timestamp(target['observed_at'])
    start, end = tsep.timestamp(p['window_start']), tsep.timestamp(p['window_end'])
    need(declared <= start < end <= observed and end-start <= timedelta(days=1), 'Prior intent and bounded evidence window required')
    need(type(p.get('max_duration_ms')) is int and 1 <= p['max_duration_ms'] <= 60000, 'Declare request duration bound')
    ua = target['intent']['crawler']
    need(isinstance(ua, str) and re.fullmatch(r'[\x20-\x7e]{1,2048}', ua), 'Complete reference HTTP client required')
    need(all(present(target.get('context', {}).get(k)) for k in ('network', 'bounds', 'tool', 'tool_version')), 'Missing collection context')
    consumers = p['consumers']
    need(isinstance(consumers, list) and 1 <= len(consumers) <= 16 and all(isinstance(c, dict)
         and c.get('basis') == 'reference-no-js' and present(c.get('name')) and present(c.get('reason')) for c in consumers),
         'Name intended consumers and the reference limitation without inventing provider capabilities')
    origins = p['origins']
    need(isinstance(origins, list) and 1 <= len(origins) <= 16 and len(set(origins)) == len(origins)
         and all(origin(o) == o for o in origins), 'Distinct exact origins required')
    items = p['items']
    need(isinstance(items, list) and 1 <= len(items) <= 32, 'Declare 1–32 critical items')
    ids = []
    for item in items:
        need(identifier(item.get('id')) and item.get('role') in ('title', 'fact', 'citation', 'updated', 'version', 'link')
             and isinstance(item.get('expected'), str) and 0 < len(item['expected']) <= 1024 and text(item['expected']),
             'Critical item needs ID, role and explicit bounded expected text/URL')
        if item['role'] in ('citation', 'link'): need(supported_url(item['expected']), 'Qualified absolute critical reference URL required')
        ids.append(item['id'])
    need(len(set(ids)) == len(ids) and {'title','fact','citation','updated'} <= {i['role'] for i in items},
         'Distinct items must cover title, fact, citation and update date')
    reps = p['representations']; states = p['states']
    need(isinstance(reps, list) and 1 <= len(reps) <= 8 and isinstance(states, list) and 1 <= len(states) <= 8,
         'Declare bounded representations and required rendered states')
    need(all(identifier(r.get('id')) for r in reps+states) and len({r['id'] for r in reps}) == len(reps)
         and len({s['id'] for s in states}) == len(states), 'Distinct representation/state identifiers required')
    page = unique(reps, 'id', 'page')
    need(page['url'] == target['url'] and page['format'] == 'html' and 'discovery' not in page, 'Main page must be declared HTML at the target URL')
    delivery = unique(reps, 'id', p['delivery'])
    for rep in reps:
        need(rep['format'] in ('html', 'json') and all(supported_url(rep[k]) and origin(rep[k]) in origins for k in ('url','final_url')),
             'Unsupported representation format/URL/origin')
        if rep['id'] != 'page':
            d = rep['discovery']; need(d['from'] == 'page', 'First profile permits one declared discovery hop from the page')
            source_content.selectors([d['element_id']])
    for rep in reps+states:
        rendered = rep in states
        if rendered: need(rep.get('dom_reader') == 'structured-inventory-v2' and present(rep.get('reason')), 'Declared structured rendered state required')
        selectors = rep['selectors']
        need(isinstance(selectors, dict) and set(selectors) <= set(ids), 'Selector outside critical inventory')
        if rendered or rep is delivery: need(set(selectors) == set(ids), 'Delivery and each rendered state must cover the complete critical inventory')
        for key, s in selectors.items():
            need(isinstance(s, dict) and set(s) == {'kind','value'}, 'Explicit literal selector required')
            if not rendered and rep['format'] == 'json':
                need(s['kind'] == 'json-pointer', 'JSON resource requires JSON Pointer'); pointer_tokens(s['value'])
            else:
                role = next(i['role'] for i in items if i['id'] == key)
                need(s['kind'] == ('id-href' if role in ('citation','link') else 'id-text'), 'HTML selector type differs from critical role')
                source_content.selectors([s['value']])
    return p, observed


def scope_review(target, plan, observed):
    r = target.get('critical_plan_review')
    reviewed(r, plan_binding(target), tsep.timestamp(target['intent']['declared_at']), tsep.timestamp(plan['window_start']))
    need(r.get('complete') is True, 'Critical scope review incomplete')
    need(r.get('judgment') in ('supported','contradiction','unknown'), 'Missing critical scope judgment')
    need(r['judgment'] != 'unknown', 'Critical scope remains unknown')
    return ('pass' if r['judgment'] == 'supported' else 'fail',
            'Supplied prior critical-scope judgment: '+r['judgment'], {'review_provenance':r['provenance'],'reviewer':r['reviewer']})


class Evidence:
    def __init__(self, target, plan, observed, notes):
        self.t, self.p, self.observed, self.notes = target, plan, observed, notes
        self.captures, self.parsed, self.urls, self.failed = {}, {}, {}, {}

    def capture(self, rid):
        if rid in self.captures: return self.captures[rid]
        from conformance.evaluate import trace
        rep = unique(self.p['representations'], 'id', rid)
        record = self.t if rid == 'page' else unique(self.t.get('documents'), 'id', rid)
        need(record['url'] == rep['url'], 'Representation URL differs from plan')
        hops = record['http']; final, status, headers, body = trace(hops, rep['url'], self.t['intent']['crawler'])
        previous = tsep.timestamp(self.p['window_start'])
        for hop in hops:
            sent, received = tsep.timestamp(hop['sent_at']), tsep.timestamp(hop['received_at'])
            need(previous <= sent <= received <= tsep.timestamp(self.p['window_end']) and
                 received-sent <= timedelta(milliseconds=self.p['max_duration_ms']) and origin(hop['url']) in self.p['origins'],
                 'Exchange origin/time/order outside prior evidence window')
            previous = received
        value = dict(final_url=final, status=status, headers=headers, raw=body if type(body) is bytes else body.encode(),
                     received_at=previous, http=hops, expected_url=rep['final_url'], format=rep['format'])
        self.captures[rid] = value
        return value

    def available(self, rid):
        v = self.capture(rid)
        info = dict(representation=rid, final_url=v['final_url'], status=v['status'], body_sha256=body_digest(v['raw']))
        if v['status'] != 200 or v['final_url'] != v['expected_url']:
            return 'fail', 'Declared public representation did not return the expected final URL and HTTP 200', info
        return 'pass', 'Complete anonymous reference-client response; content evaluated separately', info

    def preserve(self, key, value):
        proposed = dict(self.notes, **{key:value})
        need(len(json.dumps(proposed,ensure_ascii=False).encode()) <= 2*1024*1024, 'Combined interpretation inventory exceeds 2 MiB; no truncated absence claim')
        self.notes[key] = value

    def source(self, rid):
        if rid in self.failed: raise Unknown(self.failed[rid])
        try: return self._source(rid)
        except ERRORS as error:
            self.failed[rid]=str(error)
            raise

    def _source(self, rid):
        if rid in self.parsed: return self.parsed[rid]
        rep = unique(self.p['representations'], 'id', rid); v = self.capture(rid)
        need(v['status'] == 200 and v['final_url'] == v['expected_url'], 'No expected available representation to interpret')
        if rep['format'] == 'json':
            from conformance.evaluate import media_type
            kind,params=media_type(v['headers'])
            need(kind=='application/json' and params in ({},{'charset':'utf-8'}), 'Unqualified JSON media type')
            need(len(v['raw']) <= 1024*1024 and not v['raw'].startswith(b'\xef\xbb\xbf'), 'JSON resource byte/BOM bound')
            value = tsep.parse_json(v['raw'])
            self.preserve(rid, dict(kind='strict-json-string-content',body_sha256=body_digest(v['raw']),scope='Whole native JSON retained in raw input; duplicate keys/nonfinite values rejected; no schema or meaning inferred.'))
        else:
            ids = [s['value'] for s in rep['selectors'].values()]
            if rid == 'page': ids += [r['discovery']['element_id'] for r in self.p['representations'] if r['id'] != 'page']
            ids = list(dict.fromkeys(ids)) or ['__tsep_unused_inventory_id__']
            value = source_content.inventory(v['raw'],content_types=v['headers'].get('content-type',[]),ids=ids,node=os.environ.get('TSEP_SOURCE_NODE'))
            self.preserve(rid, value)
            reading = value['readings']['disabled']
            need(reading['complete'] and not reading['parse_errors'], 'Incomplete source tree or reported HTML recovery is unqualified')
            value = reading
        self.parsed[rid] = value
        return value

    def url(self, raw, base, has_base=False):
        key = (raw,base,has_base)
        if key in self.urls: return self.urls[key]
        need(isinstance(raw,str) and len(raw) <= 4096 and raw, 'Empty/excessive href cannot establish a critical reference')
        result = url_resolution.resolve([{'url':raw,'base':None},{'url':raw,'base':base}],node=os.environ.get('TSEP_SOURCE_NODE'))
        independent,relative = result['results']
        same = independent['ok'] and independent['href'] == raw and independent['protocol'] in ('http:','https:')
        need(same or not has_base, 'Base-dependent href under an unqualified explicit base')
        selected = independent if same else relative
        need(selected['ok'] and supported_url(selected['href']), 'Reference URL outside qualified HTTP syntax')
        self.preserve('url-'+str(len(self.urls)),result)
        self.urls[key] = selected['href']; return selected['href']

    def selection(self, reading, selector, final_url, *, discovery=False):
        nodes = reading['nodes']; paths, flags = source_content.contexts(nodes)
        matches = [n for n in nodes if n['kind']=='element' and source_content.attributes(n).get('id') == selector['value']]
        if not matches: return None
        need(len(matches)==1, 'Duplicate literal ID; no first-match selection')
        n=matches[0]; context=set(flags[n['id']]); a=source_content.attributes(n)
        need(not any(nodes[i].get('edge')=='shadow' for i in paths[n['id']]), 'Selected content is inside an unqualified shadow tree')
        allowed={'body','noscript'}
        if discovery and n['name']=='link':
            allowed={'head'}
            need('alternate' in re.split(r'[\t\n\r\f ]+',a.get('rel','').lower()), 'Head discovery link lacks rel=alternate')
        need(n['namespace']==HTML and context and context<=allowed and ('head' in context if allowed=={'head'} else 'body' in context),
             'Selected content is in an unqualified hidden, head, inert, foreign or template context')
        descendants=[x for x in nodes if n['id'] in paths[x['id']]]
        need(not any(x.get('edge')=='shadow' or x.get('shadow')=='open' for x in descendants), 'Selected content has unqualified shadow coverage')
        if selector['kind']=='id-href':
            need(n['name'] in (('a','link') if discovery else ('a','area')), 'Selected reference is not a qualified link element')
            if 'href' not in a: return None
            has_base=any(x['kind']=='element' and x['namespace']==HTML and x['name']=='base' and
                         'href' in source_content.attributes(x) and 'template' not in flags[x['id']] for x in nodes)
            return self.url(a['href'],final_url,has_base)
        need(all(set(flags[x['id']])<=allowed for x in descendants if x['kind']=='text'), 'Text includes a context outside the qualified no-JS body profile')
        return text(''.join(x['data'] for x in descendants if x['kind']=='text'))

    def item(self, rid, item):
        rep=unique(self.p['representations'],'id',rid);selector=rep['selectors'][item['id']]
        data=self.source(rid)
        if rep['format']=='json':
            value=pointer(data,selector['value'])
            if value is not None and item['role'] in ('citation','link'):
                need(supported_url(value), 'JSON critical reference is not a qualified absolute URL')
            return value
        return self.selection(data,selector,self.capture(rid)['final_url'])

    def discovery(self, rid):
        if rid=='page':return 'pass','Direct main-page route declared',{}
        rep=unique(self.p['representations'],'id',rid)
        access=self.available('page')
        if access[0]=='fail':return access
        source=self.source('page')
        actual=self.selection(source,{'kind':'id-href','value':rep['discovery']['element_id']},self.capture('page')['final_url'],discovery=True)
        info={'actual':actual,'expected':rep['url'],'representation':rid}
        return ('pass','Explicit page link resolves to the declared public resource',info) if actual==rep['url'] else ('fail','Declared resource is not discovered at its planned link',info)

    def semantic(self, subject):
        if subject.startswith('render:'):
            _,date=self.render(subject.split(':',1)[1])
        else:
            self.source(subject);date=self.capture(subject)['received_at']
        record=unique(self.t.get('critical_reviews'),'representation_id',subject)
        reviewed(record,content_binding(self.t,subject),date,self.observed)
        need(record.get('complete') is True and record.get('judgment') in ('supported','contradiction'), 'Whole critical-context semantic review missing, incomplete or unknown')
        return ('pass' if record['judgment']=='supported' else 'fail',
                'Bound supplied semantic judgment: '+record['judgment']+'; reviewer and truth not authenticated',
                {'representation':subject,'review_provenance':record['provenance'],'reviewer':record['reviewer']})

    def render(self, sid):
        key='render:'+sid
        if key in self.parsed:return self.parsed[key]
        from conformance.structured_dom import Surface
        v=self.capture('page');need(v['status']==200 and v['final_url']==v['expected_url'], 'Rendered comparison lacks expected main-page HTTP')
        state=unique(self.t.get('render',{}).get('states'),'id',sid)
        when=tsep.timestamp(state['observed_at'])
        need(v['received_at']<=when<=tsep.timestamp(self.p['window_end']) and state.get('complete') is True and
             state.get('errors')==[] and state.get('javascript_enabled') is True and
             present(state.get('browser')) and present(state.get('browser_version')), 'Rendered date, completion or browser context unqualified')
        surface=Surface(state,v['final_url'],v['http'],self.t['intent']['crawler'])
        need(surface.tree['base_uri']==v['final_url'], 'Changed rendered base remains unqualified')
        converted=[]
        for n in surface.tree['nodes']:
            converted.append(dict(n,kind={1:'element',3:'text',8:'comment',9:'document',10:'doctype',11:'fragment'}[n['type']],
                attributes=[dict(name=a['local_name'],namespace=a['namespace'],prefix=None,value=a['value']) for a in n['attributes']]))
        reading={'complete':True,'nodes':converted}
        self.preserve(key,{'snapshot_sha256':state['structured_dom']['snapshot_sha256'],'acquisition':state['structured_dom']['acquisition']['kind'],
                          'scope':surface.detail,'authored_label':'DOM rédigé, non observé dans un navigateur' if state['structured_dom']['acquisition']['kind']=='authored-synthetic' else 'Supplied same-navigation attribution, not authenticated'})
        self.parsed[key]=(reading,when);return reading,when


def assess(target, rule, *, diagnostics=None):
    obs={'reader':READER,'version':VERSION,'rule':rule,'rows':[],'inventories':{},
         'limitation':'Declared no-JS reference and supplied exact representations/reviews; no actual agent visit, ingestion, factual truth, citation or indexing claim.'}
    rows=obs['rows']
    def row(subject, action):
        try: outcome,reason,details=action()
        except ERRORS as error: outcome,reason,details='inconclusive',str(error),{}
        rows.append(dict(details,subject=subject,outcome=outcome,reason=reason))
    try:
        plan,observed=header(target);engine=Evidence(target,plan,observed,obs['inventories'])
        if rule=='TS44-A01':row('critical-scope',lambda:scope_review(target,plan,observed))
        elif rule=='TS44-A02':
            rid=plan['delivery'];row('discovery:'+rid,lambda:engine.discovery(rid));row('http:'+rid,lambda:engine.available(rid))
            for item in plan['items']:
                def presence(item=item):
                    actual=engine.item(rid,item)
                    return ('pass','Critical element is structurally present; meaning assessed separately',{'actual':actual}) if actual else ('fail','Required critical element absent/empty in the qualified representation',{'actual':actual})
                row(rid+':'+item['id'],presence)
        elif rule=='TS44-A03':
            states=target.get('render',{}).get('states')
            if isinstance(states,list) and any(not isinstance(s,dict) or s.get('id') not in {p['id'] for p in plan['states']} for s in states):
                rows.append({'subject':'render-scope','outcome':'inconclusive','reason':'Supplied rendered state outside the prior plan; completeness not established'})
            def compare(subject,item,get):
                actual=get();need(actual is not None and actual!='','No qualified critical value to compare')
                expected=item['expected'] if item['role'] in ('citation','link') else text(item['expected'])
                info={'representation':subject,'item':item['id'],'actual':actual,'expected':expected}
                if subject.startswith('render:'):
                    info.update({k:v for k,v in engine.notes[subject].items() if k in ('acquisition','authored_label')})
                return ('pass' if actual==expected else 'fail','Exact declared critical-value comparison; not factual truth',info)
            for rep in plan['representations']:
                if not rep['selectors']:continue
                rid=rep['id']
                for item in plan['items']:
                    if item['id'] in rep['selectors']:row(rid+':'+item['id'],lambda rid=rid,item=item:compare(rid,item,lambda:engine.item(rid,item)))
                row(rid+':review',lambda rid=rid:engine.semantic(rid))
            for state in plan['states']:
                sid=state['id'];subject='render:'+sid
                for item in plan['items']:
                    row(subject+':'+item['id'],lambda sid=sid,subject=subject,item=item,state=state:compare(subject,item,
                        lambda:engine.selection(engine.render(sid)[0],state['selectors'][item['id']],engine.capture('page')['final_url'])))
                row(subject+':review',lambda subject=subject:engine.semantic(subject))
        else: raise Unknown('Unsupported critical-content rule')
    except ERRORS as error:rows.append({'subject':'scope','outcome':'inconclusive','reason':str(error)})
    outcome=combine(rows);obs['outcome']=outcome
    reason='Critical content evidence / preuves contenu critique: '+json.dumps({k:v for k,v in obs.items() if k!='inventories'},ensure_ascii=False,sort_keys=True)
    if diagnostics is not None:diagnostics.append(obs)
    return outcome,reason
