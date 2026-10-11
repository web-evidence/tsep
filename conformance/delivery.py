"""TS39 prior delivery matrix, native SEO signals and attributed cache evidence.

Apache-2.0. Supplied evidence only; no collection or real operator authentication.
"""
from copy import deepcopy
from datetime import timedelta
import hashlib
import json

import tsep
from conformance.agent_policy import digest, present, identifier, ERRORS
from conformance.agent_access import reviewed
from conformance.http import need, Unknown
from experiments import delivery_variants as dv

VERSION='1'
READER='delivery-evidence-v1'
NATIVE_RULES=('TS07-A01','TS07-A02','TS07-A03','TS10-A01')
ERRORS=ERRORS+(OSError,)


def unique(rows,key,value,limit=64):
    need(isinstance(rows,list) and len(rows)<=limit,'Missing/excessive supplied records')
    found=[r for r in rows if isinstance(r,dict) and r.get(key)==value]
    need(len(found)==1,'Missing or ambiguous '+key+': '+str(value))
    return found[0]


def observer_plan(t):
    p=t['intent']['delivery']
    return dict(declared_at=t['intent']['declared_at'],**{k:p[k] for k in ('window_start','window_end','cells','pairs')})


def header(t):
    need(len(json.dumps(t,ensure_ascii=False,allow_nan=False).encode())<=4*1024*1024,'Delivery target exceeds 4 MiB')
    p=t['intent']['delivery'];need(p['reader']==READER,'Unsupported delivery reader')
    dv.url(t['url']);observed=tsep.timestamp(t['observed_at'])
    need(type(t.get('delivery_synthetic')) is bool,'Explicit delivery evidence provenance required')
    need(all(present(t.get('context',{}).get(k)) for k in ('network','bounds','tool','tool_version')),'Missing collection context')
    dv.validate({'kind':'delivery-variants-input','version':'1','synthetic':t['delivery_synthetic'],
                 'plan':observer_plan(t),'observations':[]})
    need(tsep.timestamp(p['window_end'])<=observed and len(p['cells'])<=32 and len(p['pairs'])<=64,'Closed bounded matrix required')
    mechanisms=p['mechanisms']
    need(isinstance(mechanisms,list) and 0<len(mechanisms)<=5 and all(m in ('negotiation','geolocation','cache','device','edge-routing') for m in mechanisms)
         and len(set(mechanisms))==len(mechanisms),'Declared distinct supported variation mechanisms required')
    cells=p['cells'];ids={c['id'] for c in cells}
    need(any(c.get('request_fields',{}).get('accept-language','undeclared') is None for c in cells),'Declare at least one absent Accept-Language context')
    need(any(c.get('mode')=='representation' for c in cells),'At least one representation cell required')
    for c in cells:
        need(identifier(c.get('context_id')),'Explicit context ID required')
        e=c['expectation'];dv.url(e['final_url']);need(type(e['status']) is int,'Exact expected status required')
        if c['mode']=='representation':
            need(e['status']==200 and all(present(e.get(k)) for k in ('language','content')),'Representation policy requires 200, language and content reference')
            i=c['seo_intent'];need(i['crawler']==c['user_agent'] and tsep.timestamp(i['declared_at'])<=tsep.timestamp(t['intent']['declared_at']), 'Native client/intent differs from prior delivery policy')
            members=i['canonical']['members'];need(isinstance(members,list) and len(members)==1 and members[0]['url']==c['url'],'First delivery profile requires one canonical member per cell')
        else:
            need(c['mode']=='non-representation' and e['status'] in (401,403,404,410,451) and present(e.get('reason'))
                 and c.get('seo_intent')=={} and e.get('accessible_via') in ids and e['accessible_via']!=c['id'],'Qualified non-representation policy required')
            need(unique(cells,'id',e['accessible_via'])['mode']=='representation','Access route must be a representation cell')
    checks=p['cache_checks'];need(isinstance(checks,list) and len(checks)<=64,'Bounded cache checks required')
    need('cache' not in mechanisms or checks,'Declared cache mechanism requires a reuse check')
    need(not checks or 'cache' in mechanisms,'Cache checks require declared cache mechanism')
    seen=set()
    for c in checks:
        need(identifier(c.get('id')) and c['id'] not in seen and c.get('stored_cell') in ids and c.get('served_cell') in ids
             and c['stored_cell']!=c['served_cell'],'Invalid cache check population')
        seen.add(c['id']);need(identifier(c.get('layer')) and type(c.get('clock_skew_ms')) is int and 0<=c['clock_skew_ms']<=30000
             and c.get('transformation')=='none','Qualified cache layer, clock bound and no-transformation policy required')
    return p,observed


def document(d,observed):
    need(isinstance(d,dict) and present(d.get('source_uri')),'Missing source document URI')
    dv.url(d['source_uri']);raw=d.get('raw_text')
    need(isinstance(raw,str) and 0<len(raw.encode())<=256*1024,'Bounded retained source text required')
    need(hashlib.sha256(raw.encode()).hexdigest()==d.get('sha256'),'Retained source fingerprint mismatch')
    date=tsep.timestamp(d['observed_at']);need(date<=observed,'Source postdates evidence window')
    return date


def envelope(r,binding,earliest,latest):
    reviewed(r,binding,earliest,latest)
    need(r.get('complete') is True,'Supplied review incomplete')
    return {'reviewer':r['reviewer'],'review_provenance':r['provenance']}


def judgment(r,key,details=None):
    v=r.get(key);need(v in ('supported','contradiction'),'Supplied '+key+' judgment missing or unknown')
    return ('pass' if v=='supported' else 'fail','Supplied '+key+' judgment: '+v,details or {})


def plan_review(t,p,observed):
    acquired=document(t.get('delivery_configuration'),tsep.timestamp(p['window_start']))
    r=t.get('delivery_plan_review');info=envelope(r,digest({k:t.get(k) for k in ('url','intent','delivery_configuration')}),
        max(acquired,tsep.timestamp(t['intent']['declared_at'])),tsep.timestamp(p['window_start']))
    result=judgment(r,'judgment',info)
    if result[0]=='fail':return result
    need(r.get('representative') is True and r.get('operator_policy_supported') is True,'Matrix representativeness or Googlebot variant-access policy unqualified')
    return result


class Evidence:
    def __init__(self,t,p,observed):
        self.t,self.p,self.observed=t,p,observed
        self.views={}

    def cell(self,c):
        o=unique(self.t.get('delivery_observations'),'cell_id',c['id'],32)
        need(isinstance(o.get('http'),list) and len(o['http'])<=20,'Bounded HTTP chain required')
        view=dv.observe_cell(c,o,observer_plan(self.t));terminal=dv.terminal(view)
        need(terminal is not None and not view['issues'] and view['request_plan_matches'],'Missing attributable terminal response or context mismatch: '+str(view['issues']))
        return o,view,terminal

    def sources(self,r):
        refs=r.get('source_ids');need(isinstance(refs,list) and 0<len(refs)<=64 and all(identifier(v) for v in refs)
             and len(set(refs))==len(refs),'Distinct retained source references required')
        sources=[unique(self.t.get('delivery_sources'),'id',sid) for sid in refs]
        dates=[document(d,self.observed) for d in sources]
        return sources,max(dates)

    def semantic(self,c,key):
        o,v,h=self.cell(c);need(v['complete'],'Complete representation required for semantic review')
        r=unique(self.t.get('delivery_semantic_reviews'),'cell_id',c['id'],32)
        b={'url':self.t['url'],'intent':self.t['intent'],'cell':c,'observation':o}
        info=envelope(r,digest(b),tsep.timestamp(h['received_at']),self.observed)
        if c['mode']=='non-representation':
            other=unique(self.p['cells'],'id',c['expectation']['accessible_via'])
            _,route,terminal=self.cell(other)
            need(route['complete'] and terminal['status']==200,'Declared alternative access route not observed complete200')
        return judgment(r,key,info)

    def context(self,c,key):
        o,v,h=self.cell(c);need(v['complete'],'Complete context capture required')
        r=unique(self.t.get('delivery_context_reviews'),'cell_id',c['id'],32)
        sources,date=self.sources(r)
        b={'url':self.t['url'],'intent':self.t['intent'],'cell':c,'observation':o,'sources':sources}
        info=envelope(r,digest(b),max(date,tsep.timestamp(h['received_at'])),self.observed)
        if key=='operator_visit':
            need(type(r.get('claims_operator_visit')) is bool,'Explicit assessor-test attribution required')
            return ('fail' if r['claims_operator_visit'] else 'pass','Assessor test; actual operator visit remains unestablished',info)
        result=judgment(r,key,info)
        if key=='context' and result[0]=='pass':
            need(isinstance(r.get('actual_context'),dict),'Missing reviewed actual context')
            if r['actual_context']!=c['context_claims']:
                return 'fail','Reviewed actual context contradicts planned context',dict(info,planned=c['context_claims'],reviewed=r['actual_context'])
        return result

    def native(self,c,rule):
        from conformance.evaluate import evaluate_target
        o,v,h=self.cell(c);need(v['complete'],'Incomplete HTTP chain; native representation not qualified')
        n=o['native'];need(isinstance(n,dict) and n.get('url')==c['url'] and n.get('intent')==c['seo_intent']
            and n.get('http')==o['http'] and n.get('context',{}).get('id')==c['context_id'],'Native source/intent/context unbound')
        need(tsep.timestamp(h['received_at'])<=tsep.timestamp(n['observed_at'])<=tsep.timestamp(self.p['window_end']),'Native observation outside window')
        if rule=='TS10-A01':
            docs=n.get('documents');need(isinstance(docs,list) and len(docs)==1 and docs[0].get('url')==c['url']
                and docs[0].get('http')==o['http'],'Canonical source differs from observed cell')
        def dates(x):
            if isinstance(x,dict):
                for k,value in x.items():
                    if k in ('observed_at','sent_at','received_at'):
                        need(tsep.timestamp(self.p['window_start'])<=tsep.timestamp(value)<=tsep.timestamp(self.p['window_end']),'Native capture/review outside delivery window')
                    elif k!='intent':dates(value)
            elif isinstance(x,list):
                for child in x:dates(child)
        dates(n)
        result,reason=evaluate_target(n,rule)
        info={'native_rule':rule,'native_outcome':result,'native_reason':reason}
        if rule=='TS07-A03' and result=='not-applicable':
            return 'pass','Verified positive rendering exemption retained as native not-applicable',info
        need(result in ('pass','fail','inconclusive'),'Unqualified native exemption')
        return result,reason,info

    def cache(self,check,key):
        a=unique(self.p['cells'],'id',check['stored_cell']);b=unique(self.p['cells'],'id',check['served_cell'])
        _,av,ah=self.cell(a);_,bv,bh=self.cell(b)
        need(av['complete'] and bv['complete'] and ah['url']==bh['url'],'Complete comparable cache representations required')
        rec=unique(self.t.get('delivery_cache_records'),'id',check['id'])
        raw=rec['raw_jsonl'];need(isinstance(raw,str) and len(raw.encode())<=512*1024,'Bounded native cache journal required')
        need(hashlib.sha256(raw.encode()).hexdigest()==rec.get('sha256'),'Cache journal fingerprint mismatch')
        lines=raw.splitlines();need(len(lines)==2 and all(s.strip() for s in lines),'Exactly two linked cache events required')
        rows=[tsep.parse_json(s.encode()) for s in lines]
        ids=[];entries=[];times=[]
        for row,kind,c,h in zip(rows,('store','serve'),(a,b),(ah,bh)):
            need(isinstance(row,dict) and identifier(row.get('event_id')) and identifier(row.get('entry_id')),'Native event/entry IDs required')
            ids.append(row['event_id']);entries.append(row['entry_id']);when=tsep.timestamp(row['at']);times.append(when)
            need(row.get('kind')==kind and row.get('cell_id')==c['id'] and row.get('layer')==check['layer'],'Cache event/cell/layer unbound')
            need(all(row.get(k)==h[k] for k in ('request_sha256','response_sha256','body_sha256')),'Native cache event bytes unbound')
            skew=timedelta(milliseconds=check['clock_skew_ms'])
            need(tsep.timestamp(h['sent_at'])-skew<=when<=tsep.timestamp(h['received_at'])+skew,'Cache event outside request clock bound')
        need(len(set(ids))==2 and entries[0]==entries[1] and times[0]<=times[1],'Cache entry identity/order ambiguous')
        exported=tsep.timestamp(rec['exported_at']);need(times[-1]<=exported<=self.observed,'Cache export outside observed interval')
        r=rec.get('review');need(isinstance(r,dict),'Missing supplied cache attribution review')
        sources,date=self.sources(r)
        binding={'url':self.t['url'],'intent':self.t['intent'],'check':check,'record':{k:v for k,v in rec.items() if k!='review'},'sources':sources}
        info=envelope(r,digest(binding),max(exported,date),self.observed)
        if key in ('linkage','clock','no_transform'):return judgment(r,key,info)
        need(all(r.get(k)=='supported' for k in ('linkage','clock','no_transform')),'Cache cause remains unqualified')
        info.update(cache_check=check['id'],entry_id=entries[0],layer=check['layer'])
        if key=='freshness':return judgment(r,key,info)
        if key=='vary':
            result=dv.vary_match(ah,bh);info['vary']=result
            need(result['match'] in ('matching','unconstrained','nonmatching'),'Stored-side Vary comparison unqualified')
            return ('fail' if result['match']=='nonmatching' else 'pass','Attributed reuse: stored-side Vary request-field condition only',info)
        return ('pass' if ah['body_sha256']==bh['body_sha256'] else 'fail','Attributed reuse under reviewed no-transformation policy',info)


def assess(t,rule,*,diagnostics=None):
    obs={'reader':READER,'rule':rule,'rows':[],'native_results':[],
         'limitation':'Supplied matrix, reviews, configuration and traces only; no reviewer, operator, geography, POP or production authentication. No whole-site coverage, indexing, ranking or cache cause beyond qualified linked evidence.'}
    def row(subject,fn):
        try:outcome,reason,details=fn()
        except ERRORS as error:outcome,reason,details='inconclusive',str(error),{}
        obs['rows'].append(dict(details,subject=subject,outcome=outcome,reason=reason))
        if 'native_rule' in details:obs['native_results'].append(dict(details,cell=subject.split(':')[0]))
    try:
        p,observed=header(t);e=Evidence(t,p,observed)
        if rule=='TS39-A01':row('prior-matrix-configuration',lambda:plan_review(t,p,observed))
        elif rule in ('TS39-A02','TS39-A03'):
            def population():
                records=t.get('delivery_observations');need(isinstance(records,list) and len(records)<=32,'Missing/bounded observation population required')
                ids=[o.get('cell_id') if isinstance(o,dict) else None for o in records]
                need(len(ids)==len(set(ids)) and set(ids)=={c['id'] for c in p['cells']},'Missing, duplicate or unplanned cells retained')
                return 'pass','Exact supplied cell population',{}
            row('cell-population',population)
            for c in p['cells']:
                if rule=='TS39-A03':
                    for key in ('context','mechanism','operator_policy','operator_visit'):
                        row(c['id']+':'+key,lambda c=c,key=key:e.context(c,key))
                    continue
                def status(c=c):
                    _,_,h=e.cell(c);expected=c['expectation']
                    out='pass' if h['status']==expected['status'] and h['url']==expected['final_url'] else 'fail'
                    return out,'Status and final URL versus prior policy',{'observed_status':h['status'],'final_url':h['url'],'expected':expected}
                row(c['id']+':status-url',status)
                if c['mode']=='representation':
                    def header_only(c=c):
                        from conformance.evaluate import directive_values
                        _,_,h=e.cell(c)
                        need(c['seo_intent'].get('indexing')=='allow','No independent header-only allow comparison selected')
                        intent={k:v for k,v in c['seo_intent'].items() if k in ('crawler','directive_crawler')}
                        intent.update(indexing='allow',following='unspecified')
                        result,reason=directive_values(h['response_headers'],[],intent)
                        return result,'HTTP directives only: '+reason,{'not_whole_representation':True}
                    # Independent additive exclusion only; excluding-policy absence cannot prove failure.
                    if c['seo_intent'].get('indexing')=='allow':
                        try:result,reason,details=header_only()
                        except ERRORS as error:result,reason,details='inconclusive',str(error),{}
                        observation=dict(details,subject=c['id']+':http-directives',outcome=result,reason=reason)
                        obs.setdefault('header_observations',[]).append(observation)
                        # This optional view can establish an additive exclusion, never whole-source completeness.
                        if result=='fail':obs['rows'].append(observation)
                    for native in NATIVE_RULES:row(c['id']+':'+native,lambda c=c,native=native:e.native(c,native))
                for key in (('language','content','accessibility') if c['mode']=='representation' else ('accessibility',)):
                    row(c['id']+':'+key,lambda c=c,key=key:e.semantic(c,key))
            if rule=='TS39-A03':
                def cache_population():
                    records=t.get('delivery_cache_records');need(isinstance(records,list) and len(records)<=64,'Bounded cache record population required')
                    ids=[r.get('id') if isinstance(r,dict) else None for r in records]
                    need(len(ids)==len(set(ids)) and set(ids)=={c['id'] for c in p['cache_checks']},'Missing, duplicate or unplanned cache checks')
                    return 'pass','Declared cache-check population retained',{}
                row('cache-population',cache_population)
                for check in p['cache_checks']:
                    for key in ('linkage','clock','no_transform','vary','body','freshness'):
                        row(check['id']+':'+key,lambda check=check,key=key:e.cache(check,key))
        else:raise Unknown('Unsupported delivery rule')
    except ERRORS as error:obs['rows'].append({'subject':'context','outcome':'inconclusive','reason':str(error)})
    states=[r['outcome'] for r in obs['rows']]
    result='fail' if 'fail' in states else 'inconclusive' if 'inconclusive' in states or not states else 'pass'
    obs['outcome']=result
    if diagnostics is not None:diagnostics.append(obs)
    return result,'Delivery evidence / preuves de diffusion: '+json.dumps(obs,ensure_ascii=False,sort_keys=True)
