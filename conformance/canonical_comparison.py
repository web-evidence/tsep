"""TS12 documentary canonical comparisons; supplied evidence, no collection.

Apache-2.0. Literal comparisons are observations, never engine/TS10 outcomes.
"""
import json
from conformance import inspection, canonical, source_canonical, http_canonical
from conformance.agent_policy import ERRORS, digest, present
from conformance.http import need
from experiments.rendered_canonical import supported_url

VERSION = '1'
READER = 'google-canonical-comparison-v1'
PREFIX = 'Canonical comparison evidence / preuves de comparaison: '
MAX_DIAGNOSTIC_BYTES = 4*1024*1024


def population(rows, urls, label):
    need(isinstance(rows,list) and len(rows)<=16, 'Missing/excessive '+label)
    found=[r.get('url') if isinstance(r,dict) else None for r in rows]
    need(all(isinstance(u,str) for u in found) and len(set(found))==len(found)
         and set(found)==set(urls), 'Missing, duplicate or unplanned '+label)
    return 'pass','Exact selected '+label


def header(t):
    p,declared,observed=inspection.header(t)
    c=t['intent']['canonical_comparison']
    need(c['reader']==READER,'Unsupported canonical comparison reader')
    need(present(t['context'].get('id')) and present(t['intent'].get('crawler')),'Missing technical context/client')
    population(c.get('members'),[m['url'] for m in p['members']],'comparison members')
    return p,c,declared,observed


def rendering(m):
    r=m['rendering'];need(r.get('mode')=='required','First profile requires supplied rendering, no exemption')
    need(r.get('dom_reader')=='structured-inventory-v2','Explicit structured DOM reader required')
    states=r.get('required_states');need(isinstance(states,list) and 1<=len(states)<=16,'Require 1–16 rendered states')
    ids=[]
    for s in states:
        need(present(s.get('id')) and isinstance(s.get('interactions'),list)
             and len(s['interactions'])<=100 and all(present(x) for x in s['interactions'])
             and present(s.get('wait')),'Missing bounded state scenario')
        ids.append(s['id'])
    need(len(set(ids))==len(ids),'Duplicate rendered state')
    return r


def policy(c):
    need(c.get('source_reader')==source_canonical.READER,'Explicit canonical source reader required')
    need(c.get('http_reader')==http_canonical.READER,'Explicit HTTP canonical reader required')
    for k in ('max_capture_age_hours','max_capture_offset_hours'):
        need(type(c.get(k)) is int and 1<=c[k]<=8760,'Missing bounded '+k)
    return 'pass','Explicit source/HTTP readers and prior age/offset policy'


def preference(m):
    need(supported_url(m.get('preferred_url')) and present(m.get('preference_source')),
         'Missing supported preference and independent source')
    return 'pass','Prior preference and supplied source retained; independence not authenticated'


def fact(values, *, detail=None):
    need(all(supported_url(v) for v in values),'Relative, fragment, empty or unsupported URL; no resolution/normalization')
    value={'state':'present' if values else 'absent','values':values}
    if detail is not None:value['detail']=detail
    return value


def unknown(reason, detail=None):
    value={'state':'unknown','values':[],'reason':str(reason)}
    if detail is not None:value['detail']=detail
    return value


def source_reading(reading):
    need(reading['complete'] and reading['head_prefix']['complete'],'Incomplete source/head inventory')
    need(not source_canonical.prefix_issues(reading),'Unqualified source head prefix')
    need(not reading['parse_errors'],'Source parse errors prevent complete comparison')
    need(not any(t['shadow_declaration']['value_state'] in ('open','closed') or 'for' in t['attributes']
                 for t in reading['template_containers']),'Shadow/template attachment outside source profile')
    closures=[x['source_span_utf16'][0] for x in reading['head_prefix']['tokens'] if x['closes_document_head']]
    first_close=min(closures) if closures else None
    values=[]
    for r in reading['inventory']['canonical']:
        need(r['namespace']==source_canonical.HTML and all(n in (None,source_canonical.HTML) for n in r['ancestor_namespaces']),
             'Foreign canonical ancestry')
        need(r['source_span_utf16'] is not None and not source_canonical.ambiguous_attributes(r,reading['parse_errors']),
             'Unknown/ambiguous canonical attribution')
        source_canonical.check(r['attributes'])
        need(r['context'] in ('head','body'),'Unknown canonical position')
        if r['context']=='head':
            need(r['ancestors'][-1]=='head' and (first_close is None or r['source_span_utf16'][0]<first_close),
                 'Indirect or reinserted head canonical')
        values.append((r['attributes'].get('href'),r['context']))
    fact([v for v,_ in values])
    return values


def technical(t,c,m):
    """Keep independent surfaces readable; never substitute TS10 preference results."""
    out={'url':m['url'],'facts':{'http':unknown('Missing attributed HTTP'),'html':unknown('Missing attributed HTML')},'details':{}}
    try:
        plan=rendering(m)
        states=plan['required_states']
    except ERRORS as error:
        plan=None;states=[];out['rendering_error']=str(error)
    for state in states:out['facts']['dom:'+state['id']]=unknown('Missing supplied rendered state')
    try:
        doc=canonical.capture(t,t.get('documents'),m['url'])
        final,status,headers,body=canonical.response(t,doc)
        need(status==200 and final==m['url'],'Final GET 200 URL differs or representation unavailable')
        out.update(observed_at=doc['observed_at'],final_url=final,source_http_sha256=digest(doc['http']))
    except ERRORS as error:
        out['attribution_error']=str(error);return out
    records=[]
    try:
        http_canonical.assess(headers,final,m.get('preferred_url'),False,c.get('http_reader'),
            document_url=m['url'],source_sha256=digest(doc['http']),observed_at=doc['observed_at'],diagnostics=records)
        record=records[0];out['details']['http']=record
        need('items' in record and not record.get('errors') and not record['counts']['unknown'],record['reason'])
        out['facts']['http']=fact([i['target'] for i in record['items'] if i['classification'] in ('compatible','conflict')])
    except ERRORS as error:out['facts']['http']=unknown(error)
    records=[]
    try:
        source_canonical.Surface(headers,body,c.get('source_reader'),m.get('preferred_url'),False,
                                 document_url=m['url'],diagnostics=records)
        record=records[0];out['details']['html']=record
        readings=record['inventory']['readings']
        need(set(readings)=={'enabled','disabled'},'Missing two static hypotheses')
        results=[source_reading(r) for r in readings.values()]
        need(results[0]==results[1],'Static scripting hypotheses differ; no rendered inference')
        out['facts']['html']=fact([v for v,_ in results[0]],detail={'positions':[p for _,p in results[0]]})
    except ERRORS as error:out['facts']['html']=unknown(error)
    if plan:
        try:
            results=canonical.doms(t,doc,plan,final,headers)
            need(len(results)==len(states),'Missing/extra rendered state population')
            for state,(surface,error) in zip(states,results):
                name='dom:'+state['id']
                try:
                    need(surface is not None,error or 'Unknown rendered state')
                    native=next(r for r in doc['render']['states'] if r['id']==state['id'])
                    kind=native['structured_dom']['acquisition']['kind']
                    need((kind=='authored-synthetic')==t['inspection_synthetic'],'DOM/evidence provenance differs')
                    values=surface.canonicals
                    out['facts'][name]=fact([v for v,_ in values],detail={'positions':['head' if head else 'other' for _,head in values],
                        'metadata':surface.facts['metadata'],'acquisition':native['structured_dom']['acquisition'],
                        'observed_at':native['observed_at'],'scope':surface.detail})
                except ERRORS as error:out['facts'][name]=unknown(error)
        except ERRORS as error:
            out['rendering_error']=str(error)
    return out


def binding(t,rec,doc):
    return digest({'url':t['url'],'intent':t['intent'],'record':rec,'document':doc})


def decisions(q):
    e=q.get('explanation');need(isinstance(e,dict) and present(e.get('text')),'Missing explanation')
    need(e.get('kind') in ('observation','hypothesis','unresolved'),'Unsupported established cause/explanation type')
    need(e['kind']!='hypothesis' or present(e.get('test')),'Hypothesis needs an observable test')
    d=q.get('decision');need(isinstance(d,dict) and all(present(d.get(k)) for k in ('owner','reason')),'Missing supplied decision/owner/reason')
    kind=d.get('kind');need(kind in ('accept','correct','monitor','revise-objective'),'Missing decision type')
    if kind=='monitor':need(present(d.get('criterion')) and inspection.observer().stamp(d.get('due_at'))>inspection.observer().stamp(q['observed_at']),'Monitoring needs criterion and future deadline')
    elif kind=='correct':need(present(d.get('action')),'Correction needs an action description')
    elif kind=='revise-objective':need(present(d.get('new_plan_reference')),'Revision needs a separate new plan')
    return 'pass','Supplied '+e['kind']+' explanation and '+kind+' decision; no action executed'


def assess(t,rule,*,diagnostics=None):
    sc=inspection.observer()
    note={'reader':READER,'version':VERSION,'target':t.get('url'),'rule_id':rule,'rows':[], 'members':[],
          'scope':'Selected-set documentation, HTTP/source and declared supplied DOM states; not canonical correctness, TS10, live state or indexing'}
    def row(subject,fn):
        try:outcome,reason=fn()
        except ERRORS as error:outcome,reason='inconclusive',str(error)
        note['rows'].append({'subject':subject,'outcome':outcome,'reason':reason})
    try:
        p,c,declared,observed=header(t);note['selection']=c;urls=[m['url'] for m in p['members']]
        if rule=='TS12-A01':
            row('inspection-plan',lambda:inspection.assess(t,'TS08-A01'))
            row('document-population',lambda:population(t.get('documents'),urls,'documents'))
            row('comparison-policy',lambda:policy(c))
            for m in c['members']:
                row(m['url']+':preference',lambda m=m:preference(m))
                row(m['url']+':rendering-plan',lambda m=m:('pass','Declared structured states: '+str(len(rendering(m)['required_states']))))
                def chronology(m=m):
                    doc=inspection.unique(t.get('documents'),m['url']);when=sc.stamp(doc['observed_at'])
                    if when<declared:return 'fail','Declared technical acquisition precedes plan'
                    need(when<=observed,'Technical acquisition postdates assessment')
                    return 'pass','Declared plan precedes technical capture; chronology not authenticated'
                row(m['url']+':technical-plan-order',chronology)
            for key in ('preferences','surfaces','temporal_policy'):
                def prior_review(key=key):
                    dates=[sc.stamp(inspection.unique(t.get('inspection_records'),u)['retrieved_at']) for u in urls]
                    dates += [sc.stamp(inspection.unique(t.get('documents'),u)['observed_at']) for u in urls]
                    q=inspection.review(t.get('inspection_plan_review'),digest({'url':t['url'],'intent':t['intent']}),declared,min(dates),t['inspection_synthetic'])
                    return inspection.judgment(q,key)
                row('plan:'+key,prior_review)
        elif rule in ('TS12-A02','TS12-A03'):
            if rule=='TS12-A02':
                row('native-inspections',lambda:inspection.assess(t,'TS08-A02'))
                row('document-population',lambda:population(t.get('documents'),urls,'documents'))
                row('comparison-policy',lambda:policy(c))
            else:row('review-population',lambda:population(t.get('comparison_reviews'),urls,'comparison reviews'))
            for m in c['members']:
                local=technical(t,c,m);note['members'].append(local)
                facts=local['facts'];rec=None
                try:
                    im=next(x for x in p['members'] if x['url']==m['url'])
                    rec,req,engine=inspection.record(t,p,im,declared,observed)
                    need(req['inspectionUrl']==m['url'],'Native request URL differs from member; no claim attribution')
                    need(engine['state']=='recorded','API error or absent native index result')
                    local['engine']=engine;local['retrieved_at']=rec['retrieved_at']
                    for key in ('googleCanonical','userCanonical'):
                        f=engine['fields'][key]
                        facts[key]=fact([f['value']] if f['state']=='present' else []) if f['state'] in ('present','absent') else unknown('Unusable API '+key+': '+f['state'])
                except ERRORS as error:
                    facts['googleCanonical']=unknown(error);facts['userCanonical']=unknown(error)
                    local['api_error']=str(error)
                google=facts['googleCanonical'];preferred=m.get('preferred_url')
                local['comparisons']=[{'surface':name,'index':i,'value':v,
                    'google':'exact-string-equal' if v==google['values'][0] else 'exact-string-different',
                    'preference':'exact-string-equal' if v==preferred else 'exact-string-different'}
                    for name,f in facts.items() if f['state']!='unknown' for i,v in enumerate(f['values'])
                    if google['state']=='present']
                local['comparison_scope']='Literal strings only; no URL equivalence, cause or representation identity inferred'
                if rule=='TS12-A02':
                    def age():
                        policy(c);need('observed_at' in local and rec is not None,'Missing attributed acquisition dates')
                        when=sc.stamp(local['observed_at'])
                        need(observed-when<=c['max_capture_age_hours']*3600,'Technical capture exceeds prior age policy')
                        need(abs(when-sc.stamp(rec['retrieved_at']))<=c['max_capture_offset_hours']*3600,'API/capture offset exceeds prior policy')
                        return 'pass','Separate acquisition/capture dates within policy; no identity of representation'
                    row(m['url']+':capture-dates',age)
                    row(m['url']+':rendering-required',lambda m=m:('pass','Required supplied states: '+str(len(rendering(m)['required_states']))))
                    if local.get('rendering_error'):row(m['url']+':rendering-population',lambda:('inconclusive',local['rendering_error']))
                    for name,f in facts.items():
                        def reading(name=name,f=f):
                            need(f['state']!='unknown',f.get('reason','Unknown surface'))
                            need(name!='googleCanonical' or f['state']=='present','Google canonical absent; no value comparison')
                            return 'pass',name+': '+f['state']+'; exact values '+repr(f['values'])
                        row(m['url']+':'+name,reading)
                else:
                    try:
                        q=inspection.unique(t.get('comparison_reviews'),m['url'])
                        docs=[d for d in t.get('documents',[]) if d.get('url')==m['url']]
                        need(len(docs)<=1,'Ambiguous document for review binding')
                        doc=docs[0] if docs else None
                        need(rec is not None and 'api_error' not in local,'No attributed native API for review')
                        dates=[sc.stamp(rec['retrieved_at'])]
                        if doc:
                            dates.append(sc.stamp(doc['observed_at']))
                            dates.extend(sc.stamp(s['observed_at']) for s in doc.get('render',{}).get('states',[]))
                        inspection.review(q,binding(t,rec,doc),max(dates),observed,t['inspection_synthetic'])
                    except ERRORS as error:
                        row(m['url']+':review',lambda:('inconclusive',str(error)));continue
                    local['supplied_review']=q
                    def claims_population():
                        plan=rendering(m)
                        names={'googleCanonical','userCanonical','http','html'}|{'dom:'+s['id'] for s in plan['required_states']}
                        need(isinstance(q.get('claims'),dict) and set(q['claims'])==names,'Missing or unplanned claims')
                        need(not local.get('rendering_error'),local.get('rendering_error'))
                        return 'pass','Exactly the planned surface claims'
                    row(m['url']+':claim-population',claims_population)
                    for name,f in facts.items():
                        def compare(name=name,f=f):
                            need(f['state']!='unknown',f.get('reason','Unknown surface'))
                            claim=q.get('claims',{}).get(name)
                            need(isinstance(claim,dict) and claim.get('state') in ('present','absent') and isinstance(claim.get('values'),list)
                                 and all(isinstance(v,str) for v in claim['values']),'Missing/unknown claim')
                            need((claim['state']=='absent')==(claim['values']==[]),'Malformed claim state/list')
                            same=claim['state']==f['state'] and claim['values']==f['values']
                            return 'pass' if same else 'fail','Supplied claim '+name+' compared with complete known ordered values'
                        row(m['url']+':claim:'+name,compare)
                    for key in ('interpretation','temporal_interpretation'):
                        row(m['url']+':'+key,lambda key=key:inspection.judgment(q,key))
                    def temporal():
                        value=q.get('temporal_scope')
                        need(value in ('reported-index-and-separate-captures','current-live-page','all-fields-at-last-crawl'),'Missing temporal scope')
                        return 'pass' if value=='reported-index-and-separate-captures' else 'fail','Reported API, crawl and separate captures are not one live timestamp'
                    def relation():
                        need(q.get('objective_relation') in ('aligned','different'),'Unknown objective relation')
                        return 'pass','Supplied objective relation: '+q['objective_relation']+'; not a Google conformity verdict'
                    def changes():
                        rows=q.get('changes');need(isinstance(rows,list) and len(rows)<=16,'Missing/excessive supplied changes list')
                        for r in rows:
                            need(sc.stamp(r['at'])<=observed and all(present(r.get(k)) for k in ('description','source')),'Invalid supplied change')
                        return 'pass','Supplied change records retained; no causality or absence of other changes inferred'
                    for name,fn in [('temporal-scope',temporal),('objective-relation',relation),('changes',changes),('decision',lambda:decisions(q))]:row(m['url']+':'+name,fn)
        else:need(False,'Unsupported canonical comparison rule')
    except ERRORS as error:row('plan',lambda:('inconclusive',str(error)))
    outcomes=[r['outcome'] for r in note['rows']]
    outcome='fail' if 'fail' in outcomes else 'inconclusive' if not outcomes or 'inconclusive' in outcomes else 'pass'
    note['outcome']=outcome
    if len(json.dumps(note,ensure_ascii=False,indent=2).encode())>MAX_DIAGNOSTIC_BYTES:
        outcome='inconclusive';note={'reader':READER,'version':VERSION,'target':t.get('url'),'rule_id':rule,'outcome':outcome,
                                     'rows':[{'subject':'bound','outcome':outcome,'reason':'Complete comparison diagnostic exceeds 4 MiB; no truncated conclusion'}]}
    if diagnostics is not None:diagnostics.append(note)
    return outcome,PREFIX+json.dumps(note,ensure_ascii=False,separators=(',',':'))
