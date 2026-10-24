"""TS25 supplied critical presence by prior stage policy. Apache-2.0.
No collection, executed JavaScript, authenticated human review or global conformity.
"""
from datetime import timedelta
import json
import os
import re
import tsep
from conformance.critical_content import Evidence as Engine, pointer_tokens
from conformance.agent_access import reviewed, origin
from conformance.agent_policy import digest, present, identifier
from experiments import source_content, jsonld_processing
from experiments.rendered_canonical import supported_url

VERSION = '3'
READER = 'critical-stage-presence-v1'
PREFIX = 'Supplied critical presence / présence critique fournie: '
ROLES = ('body-text','document-title','link','canonical','jsonld')
POLICIES = ('source-only','render-only','source-or-render','source-and-render')
def require(ok, reason):
    if not ok:
        raise ValueError(reason)


DIAGNOSTIC_LIMIT = 4 * 1024 * 1024
REVIEW_FIELD_LIMIT = 8192
REVIEW_OBJECT_LIMIT = 32768

def compact_bytes(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode('utf-8')

def review_budget(record):
    """Resource admission only; never authenticate or manufacture a review."""
    if type(record) is not dict:return
    for field in ('reviewer','assistance','reason'):
        value=record.get(field)
        if type(value) is str:
            require(len(value.encode('utf-8'))<=REVIEW_FIELD_LIMIT,'TS25 review field exceeds8192 UTF8 bytes: '+field)
    require(len(compact_bytes(record))<=REVIEW_OBJECT_LIMIT,'TS25 review object exceeds32768 compact UTF8 bytes')

def verify_review_budgets(target):
    review_budget(target.get('presence_plan_review'))
    records=target.get('presence_context_reviews')
    if type(records) is list:
        for record in records:review_budget(record)

def bounded_note(note):
    raw=compact_bytes(note)
    if len(raw)<=DIAGNOSTIC_LIMIT:return note
    failures=[row.get('item_id') for row in note.get('items',[]) if row.get('value')=='absent']
    return {'kind':READER,'version':VERSION,'rule':note['rule'],
            'value':'absent' if note.get('value')=='absent' or failures else 'unknown',
            'scope':'Resource boundary, not missing evidence. Original supplied input is unchanged; public adapter must refuse publication.',
            'diagnostic_limit_exceeded':True,'diagnostic_bytes':len(raw),
            'diagnostic_sha256':__import__('hashlib').sha256(raw).hexdigest(),
            'diagnostic_limit_bytes':DIAGNOSTIC_LIMIT,'qualified_absent_item_ids':failures,
            'reason':'TS25 diagnostic exceeds4MiB; no truncated success or public NT inferred.'}

def verify_public_diagnostic_budget(observations):
    totals={}
    for observation in observations:
        if not observation['rule_id'].startswith('TS25-'):continue
        require(not any(note.get('diagnostic_limit_exceeded') is True for note in observation['observations']),
                'TS25 diagnostic budget exceeded: native diagnostic above4MiB')
        # These are exactly the bytes written by the capture adapter below.
        payload=(json.dumps(observation,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
        target=observation['target'];totals[target]=totals.get(target,0)+len(payload)
        require(totals[target]<=DIAGNOSTIC_LIMIT,'TS25 diagnostic budget exceeded: combined public artifacts above4MiB')

def conjunction(values):
    if not values:
        return 'unknown'
    return 'absent' if 'absent' in values else 'present' if all(v == 'present' for v in values) else 'unknown'


def agreement(values):
    return values[0] if len(values) == 2 and values[0] == values[1] else 'unknown'


def either(source, rendered):
    return 'present' if 'present' in (source, rendered) else 'absent' if source == rendered == 'absent' else 'unknown'


def normalized(text):
    return re.sub(r'[\t\n\r\f ]+', ' ', text).strip(' ')


def raw_pointer(value, pointer):
    for part in pointer_tokens(pointer):
        if type(value) is dict:
            if part not in value:
                return None
            value = value[part]
        elif type(value) is list:
            require(re.fullmatch(r'0|[1-9][0-9]{0,8}', part), 'Noncanonical JSON array index')
            if int(part) >= len(value):
                return None
            value = value[int(part)]
        else:
            raise ValueError('JSON pointer crosses unsupported scalar')
    require(type(value) is str, 'Expected literal string identity at declared pointer')
    return value


def select(reading, plan, engine, final_url):
    require(reading['complete'] and not reading.get('parse_errors', []), 'Incomplete tree or source recovery')
    nodes = reading['nodes']
    paths, flags = source_content.contexts(nodes)
    matches = [n for n in nodes if n['kind'] == 'element' and source_content.attributes(n).get('id') == plan['selector_id']]
    if not matches:
        return {'value': 'absent', 'reason': 'No element at declared literal ID; not global content absence'}
    require(len(matches) == 1, 'Duplicate literal ID; no first match')
    selected = matches[0]
    context = set(flags[selected['id']])
    role = plan['role']
    allowed = {'head', 'body', 'script'} if role == 'jsonld' else {'head', 'body'}
    require(selected['namespace'] == source_content.HTML and context <= allowed, 'Unsupported context; visibility not inferred')
    require(not any(nodes[i].get('edge') == 'shadow' for i in paths[selected['id']]), 'Selected shadow tree outside profile')
    require(all(a['namespace'] is None for a in selected['attributes']), 'Namespaced selected attributes outside profile')
    attrs = source_content.attributes(selected)
    details = {'node_id': selected['id'], 'node_path': paths[selected['id']], 'namespace': selected['namespace'], 'element': selected['name'], 'role': role, 'expected': plan['expected']}

    def result(actual, reason):
        return dict(details, value='present' if actual == plan['expected'] else 'absent', actual=actual, reason=reason)

    head_direct = context == {'head'} and selected['parent'] is not None and nodes[selected['parent']]['name'] == 'head'
    if role == 'document-title' and not (selected['name'] == 'title' and head_direct):
        return result(None, 'Selected node is not a direct document-head title')
    if role == 'body-text':
        require(context == {'body'}, 'Body text requires body context')
    if role in ('link', 'canonical'):
        if role == 'link':
            require(selected['name'] != 'area', 'Area not supported by this link profile')
            if selected['name'] != 'a' or context != {'body'}:
                return result(None, 'Required ordinary body anchor not present at declared ID')
        elif selected['name'] != 'link' or not head_direct or 'canonical' not in re.split(r'[\t\n\r\f ]+', attrs.get('rel', '').lower()):
            return result(None, 'Required direct-head canonical relationship not present at declared ID')
        if not attrs.get('href'):
            return result(None, 'Declared native link has no nonempty href')
        has_base = any(n['kind'] == 'element' and n['namespace'] == source_content.HTML and n['name'] == 'base' and set(flags[n['id']]) == {'head'} and 'href' in source_content.attributes(n) for n in nodes)
        require(not has_base, 'Active explicit base outside this initial closed profile')
        actual = engine.url(attrs['href'], final_url)
        return result(actual, 'Exact resolved expected HTTP reference; no preference, discovery or indexability inferred')
    descendants = [n for n in nodes if selected['id'] in paths[n['id']]]
    require(not any(n.get('edge') == 'shadow' or n.get('shadow') == 'open' for n in descendants), 'Unqualified descendant shadow coverage')
    require(all(set(flags[n['id']]) == context for n in descendants if n['kind'] == 'text'), 'Selected text contains excluded contexts')
    raw = ''.join(n['data'] for n in descendants if n['kind'] == 'text')
    if role == 'jsonld':
        if selected['name'] != 'script':
            return result(None, 'Required script element not present at declared ID')
        require(context in ({'head', 'script'}, {'body', 'script'}), 'Unsupported script context')
        require(attrs.get('type', '').strip(' \t\r\n\f').lower() == 'application/ld+json', 'Unsupported declared JSON-LD MIME; parameters outside profile')
        require('src' not in attrs, 'External script payload not established by supplied inline bytes')
        require(len(raw.encode('utf-8')) <= 65536, 'Selected JSON block exceeds 64 KiB component bound')
        if not raw.strip(' \t\r\n'):
            return result(None, 'Known selected empty JSON block')
        try:
            document = jsonld_processing.strict_json(raw)
        except json.JSONDecodeError as error:
            return result(None, 'Invalid JSON syntax in complete selected raw script: ' + str(error))
        jsonld_processing.bounded(document)
        require(type(document) in (dict, list), 'Structured block requires an object or array')
        return result(raw_pointer(document, plan['json_pointer']), 'Strict raw JSON string comparison at prior pointer; no HTML decoding, JSON-LD expansion, vocabulary or semantic claim')
    actual = normalized(raw)
    details['expected'] = normalized(plan['expected'])
    return dict(details, value='present' if actual == normalized(plan['expected']) else 'absent', actual=actual, reason='Exact declared text marker comparison; no semantic truth or CSS visibility claim')


def safe(action):
    try:
        return action()
    except (ValueError, TypeError, KeyError, IndexError, AttributeError, OSError, RecursionError, UnicodeError) as error:
        return {'value': 'unknown', 'reason': str(error)}



def plan_binding(target):
    return digest({'url':target['url'],'intent':target['intent']})


def context_binding(target,item_id,state):
    return digest({'url':target['url'],'intent':target['intent'],'http':target.get('http'),'state':state,'item_id':item_id})


def header(target):
    p=target['intent']['critical_presence']
    require(p['reader']==READER,'Unsupported prior critical presence reader')
    declared=tsep.timestamp(target['intent']['declared_at']); observed=tsep.timestamp(target['observed_at'])
    start,end=tsep.timestamp(p['window_start']),tsep.timestamp(p['window_end'])
    require(declared<=start<end<=observed and end-start<=timedelta(days=1),'Prior intent and at most24h evidence window required')
    require(type(p['max_duration_ms']) is int and 1<=p['max_duration_ms']<=30000,'Request bound1–30000ms required')
    require(all(present(target.get('context',{}).get(k)) for k in ('network','bounds','tool','tool_version')),'Missing collection context')
    require(type(target['intent']['crawler']) is str and re.fullmatch(r'[\x20-\x7e]{1,2048}',target['intent']['crawler']),'Explicit complete HTTP client required')
    origins=p['origins']
    require(type(origins) is list and 1<=len(origins)<=16 and len(set(origins))==len(origins) and all(origin(o)==o for o in origins),'Bounded distinct exact origins required')
    require(all(supported_url(u) and origin(u) in origins for u in (target['url'],p['final_url'])),'Qualified prior page and final URLs required')
    items,states=p['items'],p['states']
    require(type(items) is list and 1<=len(items)<=32 and all(type(i) is dict and identifier(i.get('id')) for i in items) and len({i['id'] for i in items})==len(items),'1–32 distinct critical item IDs required')
    require(type(states) is list and len(states)<=16 and all(type(s) is dict and identifier(s.get('id')) for s in states) and len({s['id'] for s in states})==len(states),'0–16 distinct prior state IDs required')
    for s in states:
        require(set(s)=={'id','reason','browser','browser_version','conditions'} and all(present(s[k]) for k in ('reason','browser','browser_version','conditions')),'Prior state browser/conditions/reason required')
    return p,observed


def item_header(item,plan,engine,target):
    required={'id','role','reason','selector_id','expected','policy','states'}
    require(set(item)==required|({'json_pointer'} if item.get('role')=='jsonld' else set()),'Closed critical item fields required')
    require(item['role'] in ROLES and present(item['reason']) and item['policy'] in POLICIES,'Role, reason and prior stage policy required')
    require(type(item['expected']) is str and 0<len(item['expected'])<=1024 and normalized(item['expected']).strip('\u00a0'),'Nonempty bounded literal expected value required')
    source_content.selectors([item['selector_id']])
    states=item['states'];require(type(states) is list and len(states)<=16 and all(type(s) is str for s in states) and len(set(states))==len(states),'Distinct bounded item state IDs required')
    require((not states if item['policy']=='source-only' else bool(states)) and set(states)<={s['id'] for s in plan['states']},'State selection inconsistent with prior stage policy')
    if item['role'] in ('link','canonical'):
        require(engine.url(item['expected'],target['url'])==item['expected'],'Exact absolute expected HTTP URL required')
    if item['role']=='jsonld':pointer_tokens(item['json_pointer'])


def scope(target,plan,observed):
    require(present(plan.get('population')) and present(plan.get('scope_reason')),'Explicit population and scope reason required')
    roles=plan['roles'];require(type(roles) is list and len(roles)==5 and {r['role'] for r in roles}==set(ROLES),'Exactly five explicit role dispositions required')
    for row in roles:
        expected=[i['id'] for i in plan['items'] if i.get('role')==row['role']]
        require(set(row)=={'role','disposition','item_ids','reason'} and present(row['reason']),'Closed motivated role disposition required')
        require(type(row['item_ids']) is list and len(row['item_ids'])==len(set(row['item_ids'])) and set(row['item_ids'])==set(expected),'Role disposition does not cover the exact prior items')
        require(row['disposition']==('included' if expected else 'outside-declared-scope'),'Silent or inconsistent role coverage')
    require(all(i.get('role') in ROLES for i in plan['items']),'Unsupported item role cannot pass scope')
    r=target.get('presence_plan_review');review_budget(r);reviewed(r,plan_binding(target),tsep.timestamp(target['intent']['declared_at']),tsep.timestamp(plan['window_start']))
    require(r.get('complete') is True and r.get('judgment') in ('supported','contradiction'),'Complete supplied scope judgment required')
    return {'value':'present' if r['judgment']=='supported' else 'absent','reason':'Supplied bound prior scope judgment; reviewer not authenticated','review':r,'roles':roles}


def context_review(target,item,state,observed,when):
    records=target.get('presence_context_reviews');require(type(records) is list and len(records)<=1024,'Missing or excessive supplied context reviews')
    rows=[r for r in records if type(r) is dict and r.get('item_id')==item['id'] and r.get('state_id')==state['id']]
    require(len(rows)==1,'Missing, duplicate or contested item/state context reviews; no latest-wins selection')
    r=rows[0];review_budget(r);reviewed(r,context_binding(target,item['id'],state),when,observed)
    require(r.get('complete') is True and r.get('judgment') in ('supported','contradiction'),'Complete supplied item/context judgment required')
    return {'value':'present' if r['judgment']=='supported' else 'absent','reason':'Bound supplied visible/context judgment, not authenticated','review':r}


def unbounded_qualify(target,rule):
    note={'kind':READER,'version':VERSION,'rule':rule,'value':'unknown','scope':'Declared supplied population only. No execution, authenticated reviewer, CSS visibility from nodes, semantic truth, Google rendering, indexing or global conformity.','items':[],'inventories':{}}
    try:
        p,observed=header(target)
        note['declared_roles']=p.get('roles')
        note['population']=p.get('population')
        note['scope_reason']=p.get('scope_reason')
        if rule=='TS25-A01':
            note['scope_review']=safe(lambda:scope(target,p,observed));note['value']=note['scope_review']['value'];return note
        require(rule=='TS25-A02','Unsupported atomic rule')
        internal={k:p[k] for k in ('window_start','window_end','max_duration_ms','origins')}
        internal['representations']=[{'id':'page','url':target['url'],'final_url':p['final_url'],'format':'html'}]
        engine=Engine(target,internal,observed,note['inventories'])
        source_cache={}
        def source_tree():
            if not source_cache:
                try:
                    capture=engine.capture('page');require(capture['status']==200 and capture['final_url']==capture['expected_url'],'Expected final HTTP200 required')
                    ids=list(dict.fromkeys(i.get('selector_id') for i in p['items'] if type(i.get('selector_id')) is str))
                    # Invalid individual selectors do not erase a separately qualified item failure.
                    ids=[s for s in ids if safe(lambda s=s: {'value':'present','valid':source_content.selectors([s])})['value']=='present']
                    require(ids,'No qualified literal selector')
                    inv=source_content.inventory(capture['raw'],content_types=capture['headers'].get('content-type',[]),ids=ids,node=os.environ.get('TSEP_SOURCE_NODE'))
                    require(len(json.dumps(inv,ensure_ascii=False).encode())<=2*1024*1024,'Source inventory bound exceeded; no truncated absence claim')
                    source_cache['inventory']=inv
                    note['inventories']['source']={'body_sha256':__import__('hashlib').sha256(capture['raw']).hexdigest(),'source_sha256':inv.get('source_sha256'),'readings':{k:{'complete':v['complete'],'parse_errors':v.get('parse_errors',[]),'node_count':len(v['nodes'])} for k,v in inv['readings'].items()},'scope':'Two static hypotheses, no JavaScript executed; exact original retained'}
                except (ValueError,TypeError,KeyError,IndexError,AttributeError,OSError,RecursionError,UnicodeError) as e:source_cache['error']=str(e)
            require('error' not in source_cache,source_cache.get('error'))
            return source_cache['inventory']
        def source(item):
            inv=source_tree();readings={k:safe(lambda r=r:select(r,item,engine,p['final_url'])) for k,r in inv['readings'].items()}
            return {'value':agreement([readings[k]['value'] for k in ('enabled','disabled')]),'readings':readings,'reason':'Alternative static hypotheses must agree'}
        def rendered(item,sid):
            spec=next(s for s in p['states'] if s['id']==sid)
            states=target.get('render',{}).get('states',[]);matches=[s for s in states if type(s) is dict and s.get('id')==sid]
            require(len(matches)==1,'Missing or ambiguous required rendered state');state=matches[0]
            require(all(state.get(k)==spec[k] for k in ('browser','browser_version','conditions')),'Supplied state browser/conditions differ from prior declaration')
            reading,when=engine.render(sid);value=select(reading,item,engine,p['final_url'])
            if value['value']=='present' and item['role'] in ('body-text','link'):
                r=safe(lambda:context_review(target,item,state,observed,when));value=dict(value,value=r['value'],context_review=r)
            return value
        render_container=target.get('render',{})
        supplied=render_container.get('states',[]) if type(render_container) is dict else None
        population=safe(lambda:population_check(supplied,p))
        note['state_population']=population
        for item in p['items']:
            def assess_item():
                item_header(item,p,engine,target)
                a=safe(lambda:source(item))
                bs={sid:safe(lambda sid=sid:rendered(item,sid)) for sid in item['states']}
                b=conjunction([s['value'] for s in bs.values()]);av=a['value']
                value={'source-only':av,'render-only':b,'source-or-render':either(av,b),'source-and-render':conjunction([av,b])}[item['policy']]
                return {'value':value,'source':a,'rendered':{'value':b,'states':bs},'divergence':av in ('present','absent') and b in ('present','absent') and av!=b}
            result=safe(assess_item);note['items'].append(dict(result,item_id=item['id'],role=item.get('role'),policy=item.get('policy'),expected=item.get('expected')))
        note['value']=conjunction([population['value']]+[i['value'] for i in note['items']])
    except (ValueError,TypeError,KeyError,IndexError,AttributeError,OSError,RecursionError,UnicodeError,StopIteration) as error:
        note['value']='absent' if any(i.get('value')=='absent' for i in note['items']) else 'unknown';note['reason']=str(error)
    return note


def population_check(states,plan):
    require(type(states) is list and len(states)<=16 and all(type(s) is dict and identifier(s.get('id')) for s in states),'Unqualified supplied state population')
    ids=[s['id'] for s in states];require(len(ids)==len(set(ids)) and set(ids)<={s['id'] for s in plan['states']},'Duplicate or unplanned supplied states; coverage unknown')
    groups={}
    for s in states:
        h=s.get('structured_dom',{}).get('snapshot_sha256')
        if h:groups.setdefault(h,[]).append(s['id'])
    return {'value':'present','reason':'Supplied state IDs within prior population; required missing states assessed per item','shared_snapshots':[{'sha256':h,'states':ids} for h,ids in groups.items() if len(ids)>1]}


def qualify(target,rule):
    return bounded_note(unbounded_qualify(target,rule))


def assess(target,rule,*,diagnostics=None):
    value=qualify(target,rule)
    if diagnostics is not None:diagnostics.append(value)
    return {'present':'pass','absent':'fail','unknown':'inconclusive'}[value['value']],PREFIX+json.dumps(value,ensure_ascii=False,sort_keys=True)
