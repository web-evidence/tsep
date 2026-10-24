"""Candidate native graph measurements; no acquisition or site completeness.

Reuse qualified TS16 technical source/DOM readers, retaining their limits.
"""
import json
import os
from datetime import timedelta
import tsep
from adapters.incoming_links_intake import verify_target
from conformance import incoming_links as links
from conformance.graph_bounds import read as bounds

PROFILE='supplied-graph-documents-v1'
ERRORS=(ValueError,TypeError,KeyError,OSError,AttributeError,OverflowError)
need=links.need
named=links.named


def plan_for(target):
    need(type(target) is dict,'Target object required')
    need(len(json.dumps(target,ensure_ascii=False,allow_nan=False).encode())<=8*1024*1024,'Bounded JSON input required')
    need(type(target.get('graph_synthetic')) is bool,'Explicit boolean synthetic provenance required')
    context=target.get('context');need(type(context) is dict and all(named(context.get(k)) for k in ('network','bounds','tool','tool_version')),'Named capture context required')
    intent=target.get('intent');need(type(intent) is dict and type(intent.get('graph')) is dict,'Prior graph plan required')
    plan=intent['graph'];need(plan.get('reader')==PROFILE and named(plan.get('selection_reason')) and named(intent.get('crawler')),'Named supported graph plan required')
    declared,start,end,observed=[tsep.timestamp(v) for v in (intent['declared_at'],plan['window_start'],plan['window_end'],target['observed_at'])]
    need(declared<=start<=end<=observed and end-start<=timedelta(hours=24),'Unqualified prior graph chronology')
    need(type(plan.get('max_duration_ms')) is int and 0<plan['max_duration_ms']<=30000,'Bounded capture duration required')
    node=os.environ.get('TSEP_SOURCE_NODE');need(named(node),'Explicit qualified Node runtime unavailable')
    origin=plan.get('origin');need(named(origin),'Exact origin required');links.exact_urls([origin+'/'],origin,node)
    sources=plan.get('sources');need(type(sources) is list and 1<=len(sources)<=16,'Bounded1..16document population required')
    total=0
    for s in sources:
        need(type(s) is dict and set(s)=={'url','final_url','states'} and s['url']==s['final_url'],'Initial graph profile requires exact requested/final document identity; no redirect equivalence')
        states=s['states'];need(type(states) is list and 1<=len(states)<=16,'Bounded declared states required')
        need(all(type(v) is dict and set(v)=={'id','browser','browser_version','scenario','interaction'} and all(named(x) for x in v.values()) and v['interaction'] in ('none','after-interaction') for v in states),'Named supported prior states required')
        need(len({v['id'] for v in states})==len(states) and any(v['interaction']=='none' for v in states),'Distinct prior states including no-interaction required');total+=len(states)
    need(total<=64,'Total planned state bound exceeded')
    nodes=[s['url'] for s in sources];need(all(type(u) is str for u in nodes) and len(set(nodes))==len(nodes),'Distinct document population required')
    links.exact_urls(nodes+[target['url']],origin,node)
    roots=plan.get('roots');need(type(roots) is list and 1<=len(roots)<=4 and all(type(r) is str and r in nodes for r in roots) and len(set(roots))==len(roots),'Distinct declared roots within population required')
    documents=target.get('graph_documents');need(type(documents) is list and len(documents)<=32 and all(type(d) is dict and type(d.get('url')) is str for d in documents),'Bounded supplied original document records required')
    return plan,nodes,roots,documents,start,end,node


def read(target):
    # Reuse transport self-integrity without changing the original target.
    # This guard applies even to unplanned documents and a missing graph plan.
    if type(target) is dict:
        verify_target({'incoming_links':{'documents':target.get('graph_documents')}},'2')
    result={'kind':PROFILE,'qualified':False,'authenticates_acquisition':False,'sources':[],
            'scope':'Declared document graph only; no complete crawl or site-wide orphan conclusion.',
            'source_content_identity':'Not assessed; an HTTP200 error template can supply navigation edges. No soft404 detection.'}
    try:
        plan,nodes,roots,documents,start,end,node=plan_for(target)
    except ERRORS as error:
        result['reason']=str(error);return result
    groups={}
    for document in documents:groups.setdefault(document['url'],[]).append(document)
    result['unplanned_documents']=sorted(set(groups)-set(nodes))
    pairs={};qualified_roots=[]
    # Helper receives exactly the supplied graph provenance under its established
    # technical parameter name; no fabricated acquisition or original changes.
    surface_target={**target,'incoming_links_synthetic':target['graph_synthetic']}
    for prior in plan['sources']:
        url=prior['url'];row={'url':url,'surfaces':[],'qualified_original':False};pairs[url]={u:'unknown' for u in nodes if u!=url}
        try:
            need(len(groups.get(url,[]))==1,'Source original missing or ambiguous')
            document=groups[url][0]
            captured=links.capture(surface_target,document,plan,start,end,node,required_final=url,source=True)
            row['qualified_original']=True
            row['http']={k:v for k,v in captured.items() if k not in ('headers','body')}
            if url in roots:qualified_roots.append(url)
            destinations=[u for u in nodes if u!=url]
            if destinations:
                row['surfaces']=[links.source_surface(captured,destinations)]+links.rendered_surfaces(surface_target,document,prior,captured,destinations,plan)
            for dest in destinations:
                eligible=[s['destinations'][dest] for s in row['surfaces'] if s.get('eligible',True)]
                outcomes=[s['outcome'] for s in eligible]
                pairs[url][dest]='present' if 'pass' in outcomes else 'absent' if outcomes and all(v=='fail' for v in outcomes) else 'unknown'
        except ERRORS as error:row['reason']=str(error)
        result['sources'].append(row)
    result['graph']=bounds({'nodes':nodes,'roots':roots,'pairs':pairs})
    result['pairs']=pairs;result['qualified_roots']=sorted(qualified_roots)
    result['qualified']=len(qualified_roots)==len(roots) and all(v!='unknown' for row in pairs.values() for v in row.values())
    result['reason']='All bounded graph measurements qualified' if result['qualified'] else 'Retained unknown original/surface/pair/root; intervals do not qualify the whole measurement'
    return result
