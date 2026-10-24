"""Candidate TS18 supplied graph reconciliation. Apache-2.0."""
import hashlib
import json
import re
import tsep
from conformance import incoming_links as links
from conformance import graph_documents as native_graph
from conformance import graph_inventories as originals
from conformance import graph_reviews

PROFILE='supplied-graph-reconciliation-v1'
ERRORS=(ValueError,TypeError,KeyError,OSError,AttributeError,OverflowError,UnicodeError)
need=links.need
named=links.named
binding=graph_reviews.binding


def transport(target):
    records=target.get('graph_inventories') if type(target) is dict else None
    if type(records) is dict:
        for record in records.values():
            try:originals.original(record)
            except originals.IntegrityError as error:raise tsep.Invalid('TS18 original integrity: '+str(error)) from error
            except originals.Unqualified:pass


def families(plan,nodes):
    values=plan.get('families');need(type(values) is list and 1<=len(values)<=8,'Bounded prior families required')
    mapping={}
    ids=set()
    for f in values:
        need(type(f) is dict and set(f)=={'id','urls','reason'} and type(f['id']) is str and re.fullmatch(r'[A-Za-z0-9_-]{1,64}',f['id']) and named(f['reason']),'Named prior family/rationale required')
        need(f['id'] not in ids,'Ambiguous family identifier');ids.add(f['id'])
        urls=f['urls'];need(type(urls) is list and urls and all(type(u) is str and u in nodes and u not in mapping for u in urls) and len(set(urls))==len(urls),'Family members ambiguous/outside population')
        for u in urls:mapping[u]=f['id']
    need(set(mapping)==set(nodes),'Every selected document needs exactly one prior family')
    return values,mapping


def production(role,p,roots,nodes):
    need(type(p) is dict and named(p.get('tool')) and named(p.get('tool_version')),'Named inventory production required')
    base_fields={'mode','derived_from','tool','tool_version'}
    need(set(p)==(base_fields|{'seed_roots','frontier_sha256'} if role=='crawl' else base_fields),'Closed production profile excludes undeclared supplementary seeds or modes')
    if role=='crawl':
        need(p.get('mode')=='follow-links' and p.get('derived_from')==[],'List-seeded/dependent crawl is not a qualified link-following inventory')
        need(p.get('seed_roots')==roots and p.get('frontier_sha256')==binding({'nodes':nodes,'roots':roots}),'Crawl roots/frontier differ from prior graph')
    elif role=='cms':need(p.get('mode')=='native-export' and p.get('derived_from')==[],'Unsupported CMS lineage')
    else:
        need((p.get('mode')=='cms-generated' and p.get('derived_from')==['cms']) or (p.get('mode')=='native-export' and p.get('derived_from')==[]),'Sitemap production/lineage missing or unsupported')


def scope(target,plan,nodes,roots,start,end,node):
    result={'outcome':'inconclusive','inventories':{},'families':[],'rows':[],
            'scope':'Membership within the prior population; outside URLs unevaluated, never orphan candidates.',
            'production_authenticity':'Production and lineage are supplied declarations, not independently authenticated.'}
    records=target.get('graph_inventories');records=records if type(records) is dict else {}
    reference_ok=False
    try:
        record=records.get('reference');raw=originals.original(record)
        need(tsep.timestamp(record['observed_at'])<=tsep.timestamp(target['intent']['declared_at']),'Reference inventory postdates plan')
        need(hashlib.sha256(raw).hexdigest()==plan.get('reference_sha256'),'Reference inventory not bound to prior plan')
        text=raw.decode('utf-8');body=text[:-1] if text.endswith('\n') else text
        need(body.split('\n')==nodes,'Reference lines differ from exact ordered prior population')
        reference_ok=True
    except ERRORS as error:result['reference_reason']=str(error)
    result['reference_qualified']=reference_ok
    try:
        result['families'],mapping=families(plan,nodes);family_ok=True
    except ERRORS as error:
        result['family_reason']=str(error);mapping={};family_ok=False
    configs=plan.get('inventory_sources');configs=configs if type(configs) is dict else {}
    for role in ('crawl','cms','sitemap'):
        row={'qualified':False,'urls':[],'outside_population':[]}
        try:
            config=configs.get(role);record=records.get(role)
            if type(record) is dict:row['observed_at']=record.get('observed_at')
            need(type(config) is dict and type(record) is dict,'Declared inventory config and original missing')
            need(start<=tsep.timestamp(record['observed_at'])<=end,'Inventory outside prior capture window')
            production(role,config.get('production'),roots,nodes)
            if config.get('format')=='csv' and role in ('crawl','cms'):
                reading=originals.read(record,'csv',config.get('csv'))
            elif config.get('format')=='sitemap-urlset' and role=='sitemap':
                reading=originals.read(record,'sitemap',{'encoding':config.get('encoding')})
            else:raise ValueError('Inventory format outside declared role profile')
            row['reading']=reading
            need(reading['qualified'],reading.get('reason','Unqualified original inventory'))
            urls=reading['urls'];links.exact_urls(urls,plan['origin'],node)
            if role=='crawl':need(set(roots)<=set(urls),'Crawl original does not retain declared roots')
            row.update(qualified=True,urls=urls,outside_population=sorted(set(urls)-set(nodes)),production=config['production'])
        except ERRORS as error:row['reason']=str(error)
        result['inventories'][role]=row
    for url in nodes:
        membership={'reference':True if reference_ok else None}
        membership.update({k:(url in v['urls'] if v['qualified'] else None) for k,v in result['inventories'].items()})
        known={v for v in membership.values() if v is not None}
        result['rows'].append({'url':url,'family':mapping.get(url),'membership':membership,'known_difference':len(known)>1})
    if reference_ok and family_ok and all(v['qualified'] for v in result['inventories'].values()):result['outcome']='pass'
    result['reason']='Complete scoped original reconciliation, not independent proof of site completeness' if result['outcome']=='pass' else 'Missing/unqualified scope, original or declared production; matching subsets do not cure it'
    return result


def subjects_for(target,plan,nodes,roots,scope_result,graph_result):
    if not scope_result['families']:return []
    graph_nodes={r['node']:r for r in graph_result.get('graph',{}).get('nodes',[])}
    membership={r['url']:r for r in scope_result['rows']}
    root_ready=set(graph_result.get('qualified_roots',[]))==set(roots)
    records=target.get('graph_inventories',{});records=records if type(records) is dict else {}
    original_hashes={k:r.get('sha256') for k,r in records.items() if type(r) is dict}
    common={'profile':PROFILE,'plan_sha256':binding(target['intent']),'original_inventories':original_hashes,'inventory_records_sha256':binding(records),
            'graph_originals_sha256':binding(target.get('graph_documents'))}
    result=[]
    def add(id,ready,material):
        result.append({'id':id,'qualified':bool(ready),'binding_material':{**common,'subject':id,'measurements':material},'earliest_review_at':plan['window_end']})
    def ready(url):
        row=graph_nodes.get(url,{})
        return root_ready and row.get('depth_state') in ('exact','unreachable') and row.get('incoming_lower')==row.get('incoming_upper')
    for family in scope_result['families']:
        values=[{'membership':membership[u],'graph':graph_nodes.get(u)} for u in family['urls']]
        add('family:'+family['id'],scope_result['outcome']=='pass' and all(ready(u) for u in family['urls']),{'family':family,'rows':values})
    for url in nodes:
        member=membership[url];row=graph_nodes.get(url,{})
        if member['known_difference']:
            add('difference:'+url,True,member)
        if row.get('bounded_orphan_candidate'):
            add('orphan:'+url,root_ready and row.get('incoming_lower')==row.get('incoming_upper')==0,row)
        if url not in roots and row.get('depth_state')=='unreachable':
            add('unreachable:'+url,root_ready,row)
    return sorted(result,key=lambda s:s['id'])


def measure(target):
    transport(target)
    graph=native_graph.read(target)
    result={'kind':PROFILE,'synthetic':target.get('graph_synthetic') if type(target) is dict else None,
            'layers':{'TS18-A01':{'outcome':'inconclusive'},'TS18-A02':{'outcome':'pass' if graph['qualified'] else 'inconclusive','measurement':graph}},'subjects':[],
            'candidate_normative_profile':'0.1.0-draft.38','authenticates_evidence':False}
    try:plan,nodes,roots,documents,start,end,node=native_graph.plan_for(target)
    except ERRORS as error:
        result['layers']['TS18-A01']['reason']=str(error);return result
    sc=scope(target,plan,nodes,roots,start,end,node);result['layers']['TS18-A01']=sc
    result['subjects']=subjects_for(target,plan,nodes,roots,sc,graph)
    return result


def assess_target(target):
    value=measure(target)
    review=graph_reviews.read(value['subjects'],target.get('graph_reviews'),target.get('observed_at'),target.get('graph_synthetic'))
    value['layers']['TS18-A03']=review
    outcomes=[value['layers'][r]['outcome'] for r in ('TS18-A01','TS18-A02','TS18-A03')]
    value['outcome']='fail' if 'fail' in outcomes else 'inconclusive' if 'inconclusive' in outcomes else 'pass'
    return value


PREFIX='Supplied graph / graphe fourni: '
RULES=('TS18-A01','TS18-A02','TS18-A03')


def assess(target,rule,*,diagnostics=None,assessment=None):
    value=assess_target(target) if assessment is None else assessment
    if len(json.dumps(value,ensure_ascii=False).encode('utf-8'))>4*1024*1024:
        value={'kind':PROFILE,'layers':{r:{'outcome':'inconclusive','reason':'Diagnostic exceeds bounded profile; no truncated conclusion'} for r in RULES}}
    layer=value['layers'].get(rule,{'outcome':'inconclusive','reason':'Unsupported graph rule'})
    note={'kind':PROFILE,'rule':rule,'measurement':layer,'scope':'Supplied declared graph only; no site-wide orphan or authenticated review/acquisition.'}
    if diagnostics is not None:diagnostics.append(note)
    return layer['outcome'],PREFIX+json.dumps(note,ensure_ascii=False,sort_keys=True)
