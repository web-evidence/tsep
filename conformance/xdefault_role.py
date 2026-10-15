"""TS24 supplied x-default role; no collection or judgment creation. Apache-2.0."""
import datetime
import hashlib
import json
import os
from pathlib import Path
from conformance import hreflang_native as native
from conformance import hreflang_reciprocity as transport
from conformance.evaluate import trace
from conformance.http import message, raw_bytes

PROFILE='xdefault-role-v1'
POLICY={'reader','recorded_at','hreflang_plan_sha256','target','requirement','role','variant',
        'distinct_from_variants','reviewer','accept_language','accept','context_reason'}
REVIEW={'subject','binding_sha256','reviewer','reviewed_at','disposition','rationale','synthetic'}
need=native.need

def binding(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode()).hexdigest()

def named(value):return type(value)is str and 0<len(value.strip())<=4096

def reader_sources():
    return {'conformance/'+m.__name__.split('.')[-1]+'.py':hashlib.sha256(Path(m.__file__).read_bytes()).hexdigest() for m in (native,transport)}

def binding_material(target,policy):
    return {'profile':PROFILE,'reader_sources':reader_sources(),'policy':policy,
            'hreflang_plan':target['intent']['hreflang'],'request_context':target['context'],
            'crawler':target['intent']['crawler'],'original_documents':target.get('hreflang_documents'),
            'unsupported_originals':target.get('hreflang_unsupported_channels',[])}

def request_context(document,target,policy):
    out={'qualified':False,'url':document.get('url') if type(document)is dict else None}
    try:
        need(type(document)is dict,'Destination original absent')
        hops=document.get('http');need(type(hops)is list and len(hops)==1,'One non-redirect original exchange required')
        hop=hops[0];need(type(hop)is dict,'Original exchange object required')
        final,status,headers,body=trace(hops,document['url'],target['intent']['crawler'])
        need(final==document['url'],'Requested/final identity differs')
        request=raw_bytes(hop['request']);response=raw_bytes(hop['response'])
        _,fields,_=message(hop['request'])
        need(set(fields)<= {'host','user-agent','accept-language','accept'},'Request headers outside declared closed context')
        for name,key in [('accept-language','accept_language'),('accept','accept')]:
            expected=[] if policy[key]is None else [policy[key]]
            need(fields.get(name,[])==expected,'Request '+name+' differs from prior context')
        p=target['intent']['hreflang'];start,end,sent,received=[native.stamp(x)for x in [p['window_start'],p['window_end'],hop['sent_at'],hop['received_at']]]
        need(start<=sent<=received<=end and received-sent<=datetime.timedelta(milliseconds=p['max_duration_ms']), 'Original outside prior window or duration')
        out.update(qualified=True,status=status,received_at=hop['received_at'],requested_url=document['url'],final_url=final,
                   request_sha256=hashlib.sha256(request).hexdigest(),response_sha256=hashlib.sha256(response).hexdigest(),
                   context_headers={k:fields.get(k,[])for k in ('user-agent','accept-language','accept')})
    except (ValueError,TypeError,KeyError,OSError,OverflowError) as error:out['reason']=str(error)
    return out

def channel_facts(channel,kind):
    """Retain native rows, not native whole-control verdicts. No lexical fallback."""
    if kind=='http-link':
        if type(channel)is not dict:return [],False
        return channel.get('rows',[]),not channel.get('absence_blocked',True) and not channel.get('unknowns')
    if type(channel)is not dict or not channel.get('active'):return [],False
    hypotheses=channel.get('hypotheses',{})
    if set(hypotheses)!= {'enabled','disabled'}:return [],False
    readings=[]
    for mode in ('enabled','disabled'):
        h=hypotheses[mode]
        if h.get('global_unqualified'):return [],False
        readings.append(h.get('rows',[]))
    # Equality of projected exact annotations, keeping both raw attributed readings.
    sets=[{(r['code'],r['url'])for r in rows} for rows in readings]
    if sets[0]!=sets[1]:return [],False
    complete=all(not h.get('absence_blocked',True) and not h.get('unknowns')for h in hypotheses.values())
    return readings[0],complete

def read_review(target,policy,destination,has_target):
    reviews=target.get('xdefault_reviews')
    out={'outcome':'NT','authenticates_reviewer':False,'adjudicates_rationale':False,'supplied':reviews,
         'scope':'Supplied documentary role judgment only; no inferred approval.'}
    try:
        need(destination.get('qualified')is True and destination.get('status')==200 and has_target,'Role review lacks an observed target and qualified original200')
        need(type(reviews)is list and len(reviews)<=8,'Bounded supplied review list required')
        need(len(reviews)==1,'Missing or contested role review; every supplied disposition remains visible, no implicit replacement')
        review=reviews[0];need(type(review)is dict and set(review)==REVIEW,'Supplied role review outside closed profile')
        need(review['subject']=='x-default-role','Wrong review subject')
        expected=binding(binding_material(target,policy));out['expected_binding_sha256']=expected
        need(review['binding_sha256']==expected,'Review does not bind current originals, policy, context and exact reader sources')
        need(named(review['reviewer']) and review['reviewer']==policy['reviewer'],'Supplied reviewer differs from prior named authority')
        need(named(review['rationale']),'Supplied role rationale required')
        need(type(review['synthetic'])is bool and review['synthetic']==target['xdefault_synthetic'],'Review provenance differs from original dossier')
        start=native.stamp(target['intent']['hreflang']['window_end']);end=native.stamp(target['observed_at']);at=native.stamp(review['reviewed_at'])
        need(start<=at<=end,'Review outside post-capture/pre-assessment window')
        need(review['disposition']in ('consistent','defect','unresolved'),'Unsupported supplied role disposition')
        out.update(outcome={'consistent':'C','defect':'NC','unresolved':'NT'}[review['disposition']],reason='Bound supplied judgment, not authenticated authority or semantic review by this tool')
    except (ValueError,TypeError,KeyError,OSError,OverflowError,UnicodeError) as error:out['reason']=str(error)
    return out

def qualify(data):
    result={'profile':PROFILE,'outcome':'NT','candidate_normative_profile':'0.1.0-draft.41','pages':[],'failures':[],'unknowns':[],
            'authenticates_evidence':False,'creates_review':False,'scope':'Prior supplied group and explicitly motivated exact request context only; no representative audience, universal availability, semantic neutrality, indexing or certification.',
            'semantic_limit':{'fr':'HTTP200 ne détecte pas une page d’erreur ou soft404. Rôle et contenu reposent sur un jugement fourni, non authentifié ; aucun comportement du public, langue ou géolocalisation inféré.',
                              'en':'HTTP200 does not detect an error page or soft404. Role and content depend on a supplied unauthenticated judgment; no audience behavior, language or geolocation is inferred.'}}
    if type(data)is not dict:return dict(result,reason='Original input object required')
    # A present corrupted original is refused even if policy or review is absent.
    transport.integrity(data)
    try:
        need(len(json.dumps(data,ensure_ascii=False,allow_nan=False).encode())<=8*1024*1024,'Input bound exceeded')
        t=data['target'];need(type(t)is dict,'Target object required')
        need(type(t.get('xdefault_synthetic'))is bool and t['xdefault_synthetic']==t.get('hreflang_synthetic'),'Explicit consistent original provenance required')
        intent=t['intent'];p=intent['xdefault'];need(type(p)is dict and set(p)==POLICY and p['reader']==PROFILE,'Closed prior role policy required')
        hp=intent['hreflang'];need(type(hp)is dict and p['hreflang_plan_sha256']==binding(hp),'Role policy does not bind current prior group/channels')
        need(native.stamp(p['recorded_at'])<=native.stamp(hp['window_start']),'Role policy must precede captures')
        need(p['requirement']in ('required','optional') and p['role']in ('selector','default-variant'),'Unsupported prior requirement or role')
        need(type(p['distinct_from_variants'])is bool and named(p['reviewer']),'Explicit distinctness and supplied reviewer required')
        need(named(p['context_reason']),'Explicit prior request-context rationale required; no audience representativeness inferred')
        for k in ('accept_language','accept'):need(p[k]is None or (named(p[k]) and '\r'not in p[k] and '\n'not in p[k]),'Unsupported prior request-context field')
        node=os.environ.get('TSEP_SOURCE_NODE');need(bool(node),'Explicit qualified Node24 runtime required')
        need(type(p['target'])is str and native.url_table([p['target']],node)[p['target']],'Exact absolute prior destination required')
        planned=hp['pages'];need(type(planned)is list and 1<=len(planned)<=16,'Prior bounded pages required')
        need(p['target']in [x['url']for x in planned],'Expected destination must belong to the prior group')
        mappings={native.code(c):u for c,u in hp['mappings']}
        need('x-default'not in mappings or mappings['x-default']==p['target'],'Conflicting prior group and role target declarations')
        if p['role']=='default-variant':need(type(p['variant'])is str and native.code(p['variant'])!='x-default' and mappings.get(native.code(p['variant']))==p['target'] and p['distinct_from_variants']is False,'Default-variant policy does not identify its mapped exact destination')
        else:need(p['variant']is None,'Selector policy cannot silently name a default variant')
        measured=transport.qualify(data);result['native_hreflang']=measured
        pages=measured.get('pages',[]);need(len(pages)==len(planned),'Native observations unavailable for the complete declared group')
        docs=t.get('hreflang_documents');need(type(docs)is list and len(docs)<=48,'Bounded originals required')
        by={}
        for d in docs:
            need(type(d)is dict and type(d.get('url'))is str and d['url']not in by,'Absent or duplicated original identity');by[d['url']]=d
        destination=request_context(by.get(p['target']),t,p);result['destination']=destination;result['policy']=p
        seen_expected=False;known_variant_identity=False
        for page in pages:
            row={'url':page['url'],'primary':page['primary'],'unknowns':[],'failures':[],'xdefault_targets':[]}
            ctx=request_context(by.get(page['url']),t,p);row['request_context']=ctx
            if not ctx.get('qualified'):
                row['unknowns'].append('Unqualified source request context');result['pages'].append(row);continue
            ch=page.get('channels',{});primary=page['primary'];secondary='html'if primary=='http-link'else'http-link'
            rows,complete=channel_facts(ch.get(primary),primary);other,other_complete=channel_facts(ch.get(secondary),secondary)
            # Non-HTML secondary content is outside HTML by declaration, not an unknown primary.
            if secondary=='html' and ch.get('html',{}).get('active')is False:other_complete=True
            native_rows=rows+other
            candidates=[r['url']for r in native_rows if r['code']=='x-default']
            valid=native.url_table(candidates,node) if candidates else {}
            values=set(u for u in candidates if valid.get(u));primary_values=set(r['url']for r in rows if r['code']=='x-default' and valid.get(r['url']))
            row.update(xdefault_targets=sorted(values),native_rows=native_rows)
            if any(not valid.get(u)for u in candidates):row['unknowns'].append('Relative or unsupported x-default URL; no resolution inferred');complete=False
            row['primary_complete']=complete
            if not complete or not other_complete:row['unknowns'].append('Unqualified annotation surface; no complete role claim')
            if complete and not primary_values and p['requirement']=='required':row['failures'].append('Required primary channel has no qualified x-default; secondary does not repair the prior requirement')
            foreign=values-{p['target']}
            if foreign:
                row['failures'].append('Qualified x-default target contradicts the unique prior role destination; adding the expected target does not erase this policy contradiction')
            if len(values)>1:row['unknowns'].append('Multiple targets leave positive role binding ambiguous; native TS23 and prior-role-policy contradictions remain separate')
            elif values=={p['target']}:seen_expected=True
            if p['target']in values and any(r['code']!='x-default' and r['url']==p['target']for r in native_rows):known_variant_identity=True
            result['pages'].append(row)
        if seen_expected and destination.get('qualified') and destination.get('status')in (404,410):result['failures'].append('Declared x-default destination returned '+str(destination['status'])+' in this supplied request context; no future availability claim')
        elif not destination.get('qualified') or destination.get('status')!=200:result['unknowns'].append('Destination lacks qualified exact original200 for positive role assessment')
        if seen_expected and p['distinct_from_variants'] and known_variant_identity:result['failures'].append('Explicit distinctness expectation contradicts exact native shared variant URL; no inferred neutrality judgment')
        if not seen_expected:result['unknowns'].append('No unambiguous qualified occurrence of the expected x-default; no automatic NA')
        if t.get('hreflang_unsupported_channels'):result['unknowns'].append('Relevant supplied unsupported channels prevent complete role assessment')
        if 'xdefault_na'in t:result['unknowns'].append('No native manual-NA override; historical manual assessments remain separate')
        review=read_review(t,p,destination,seen_expected);result['review']=review
        if review['outcome']=='NC':result['failures'].append('Unambiguous bound supplied role defect; judgment is unauthenticated')
        elif review['outcome']!='C':result['unknowns'].append('Role review missing, contested or unqualified')
        failures=result['failures']+[v for row in result['pages']for v in row['failures']]
        unknowns=result['unknowns']+[v for row in result['pages']for v in row['unknowns']]
        result['outcome']='NC'if failures else'NT'if unknowns else'C'
    except (ValueError,TypeError,KeyError,OSError,OverflowError,UnicodeError) as error:result['unknowns'].append(str(error));result['outcome']='NT'
    if len(json.dumps(result,ensure_ascii=False,allow_nan=False).encode())>4*1024*1024:return {'profile':PROFILE,'outcome':'NT','candidate_normative_profile':'0.1.0-draft.41','reason':'Diagnostic exceeds4MiB; no truncated conclusion'}
    return result


PREFIX='Supplied x-default / x-default fourni: '

def assess(target,rule,*,diagnostics=None):
    value=qualify({'input_version':'2','target':target})
    if len(json.dumps(value,ensure_ascii=False).encode('utf-8'))>4*1024*1024:
        value={'outcome':'NT','reason':'Diagnostic exceeds4MiB; no truncated conclusion'}
    note={'kind':PROFILE,'rule':rule,'measurement':value,'scope':'Supplied documentary role only; no authenticated human approval, semantic truth or representative audience.'}
    if diagnostics is not None:diagnostics.append(note)
    return {'C':'pass','NC':'fail','NT':'inconclusive'}[value['outcome']],PREFIX+json.dumps(note,ensure_ascii=False,sort_keys=True)
