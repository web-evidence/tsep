"""TS36 supplied release follow-up. Apache-2.0. No collection or future execution."""
from datetime import datetime,timezone
import hashlib
import json
import re

import tsep
from conformance import inspection
from conformance.agent_policy import ERRORS, digest, present, identifier
from conformance.http import need
from conformance.canonical_comparison import decisions
from experiments.rendered_canonical import supported_url

VERSION='1'
READER='release-monitoring-v1'
PREFIX='Release monitoring evidence / preuves de suivi: '
STAGES=('baseline','d1','d7','d30')
MAX_BYTES=4*1024*1024


def stamp(value):return inspection.observer().stamp(value)
def utc(value):
    whole=int(value)
    if value<whole:whole-=1
    fraction=format(value-whole,'.9f')[1:].rstrip('0').rstrip('.')
    return datetime.fromtimestamp(whole,timezone.utc).strftime('%Y-%m-%dT%H:%M:%S')+fraction+'Z'
def unique(rows,name):
    need(isinstance(rows,list) and len(rows)<=16,'Missing/excessive stage list')
    found=[r for r in rows if isinstance(r,dict) and r.get('id')==name]
    need(len(found)==1,'Missing or ambiguous stage '+name)
    return found[0]
def population(rows,names,label):
    need(isinstance(rows,list) and len(rows)<=len(names),'Missing/excessive '+label)
    ids=[r.get('id') if isinstance(r,dict) else None for r in rows]
    need(all(isinstance(i,str) for i in ids) and len(set(ids))==len(ids) and set(ids)==set(names),'Missing/duplicate/unplanned '+label)
    return 'pass','Exact '+label

def header(t):
    need(len(json.dumps(t,ensure_ascii=False,allow_nan=False).encode())<=MAX_BYTES,'Target exceeds 4 MiB')
    ip,declared,observed=inspection.header(t)
    p=t['intent']['monitoring'];need(p['reader']==READER,'Unsupported monitoring reader')
    return ip,p,declared,observed

def policy(p,declared):
    for k in ('release_id','environment','log_layer'):need(identifier(p.get(k)),'Missing bounded '+k)
    for k in ('before_artifact_sha256','after_artifact_sha256'):need(isinstance(p.get(k),str) and re.fullmatch('[a-f0-9]{64}',p[k]),'Missing '+k)
    need(present(p.get('risk')) and present(p.get('schedule_reason')),'Missing prior risk/schedule reason')
    need(type(p.get('window_hours')) is int and 1<=p['window_hours']<=24,'Window must be 1–24 hours')
    need(type(p.get('review_grace_hours')) is int and 1<=p['review_grace_hours']<=168,'Grace must be 1–168 hours')
    a,b,c,d=[stamp(p[k]) for k in ('baseline_start','baseline_end','deployment_window_start','deployment_window_end')]
    need(declared<=a<b<=c<d and d-c<=7*86400 and b-a==p['window_hours']*3600,'Unqualified prior baseline/deployment windows')
    uas=p.get('user_agents');need(isinstance(uas,list) and 1<=len(uas)<=16 and all(present(u) and len(u)<=2048 for u in uas) and len(set(uas))==len(uas),'Distinct exact User-Agent filters required')
    return 'pass','Prior selected scope, strict D1/D7/D30 schedule and exact log filter'

def deployment(t,observed):
    d=t['monitoring_deployment']
    need(d.get('provenance') in ('synthetic-exercise','supplied-release') and present(d.get('description')),'Missing release provenance')
    need((d['provenance']=='synthetic-exercise')==t['inspection_synthetic'],'Release provenance differs')
    r=inspection.body(d.get('body'));need(isinstance(r,dict),'Release receipt must be an object')
    for k in ('release_id','environment'):need(identifier(r.get(k)),'Missing release '+k)
    for k in ('before_artifact_sha256','after_artifact_sha256'):need(isinstance(r.get(k),str) and re.fullmatch('[a-f0-9]{64}',r[k]),'Missing release artifact')
    when=stamp(r['deployed_at']);need(when<=stamp(d['observed_at'])<=observed,'Release export outside deployment/assessment')
    changes=r.get('other_changes');need(isinstance(changes,list) and len(changes)<=16,'Explicit bounded other-changes list required')
    for row in changes:need(stamp(row['at'])<=observed and all(present(row.get(k)) for k in ('description','source')),'Unqualified other change')
    return r

def window(p,dep,name):
    if name=='baseline':return stamp(p['baseline_start']),stamp(p['baseline_end'])
    need(name in STAGES and dep is not None,'Missing attributed deployment for stage window')
    start=stamp(dep['deployed_at'])+int(name[1:])*86400
    need(type(p.get('window_hours')) is int and 1<=p['window_hours']<=24,'Unknown window duration')
    return start,start+p['window_hours']*3600

def stage_binding(t,c):return digest({'url':t['url'],'intent':t['intent'],'deployment':t.get('monitoring_deployment'),'checkpoint':c})
def closure_binding(t):return digest({k:t.get(k) for k in ('url','intent','monitoring_deployment','monitoring_checkpoints','monitoring_reviews')})

def logs(t,p,c,start,end,urls):
    s=c['logs'];need(s.get('reader')=='supplied-monitoring-log-v1' and s.get('format')=='normalized-jsonl','Unknown normalized log reader')
    need(s.get('provenance') in ('synthetic-exercise','supplied-log') and (s['provenance']=='synthetic-exercise')==t['inspection_synthetic'],'Log provenance differs')
    need(all(present(s.get(k)) for k in ('description','normalization_source')),'Missing log origin/normalization')
    need(s.get('layer')==p.get('log_layer') and s.get('complete') is True,'Log layer or completeness unqualified')
    need(stamp(s['window_start'])==start and stamp(s['window_end'])==end and end<=stamp(s['observed_at'])<=stamp(c['observed_at']),'Log window/export does not bind stage')
    raw=s['raw_jsonl'];need(isinstance(raw,str) and len(raw.encode())<=512*1024,'Log exceeds 512 KiB')
    need(hashlib.sha256(raw.encode()).hexdigest()==s.get('sha256'),'Changed log bytes')
    lines=raw.splitlines();need(len(lines)<=10000,'Too many log rows')
    need(isinstance(p.get('user_agents'),list) and 1<=len(p['user_agents'])<=16 and all(present(u) for u in p['user_agents']),'Missing log filter')
    totals={u:{'requests':0,'server_errors':0} for u in urls};rows=[];seen=set();previous=start
    for line in lines:
        need(bool(line.strip()),'Blank log row');r=tsep.parse_json(line.encode())
        need(isinstance(r,dict) and identifier(r.get('id')) and r['id'] not in seen,'Invalid/duplicate log ID')
        need(supported_url(r.get('url')) and present(r.get('user_agent')) and len(r['user_agent'])<=2048,'Unsupported log URL/User-Agent')
        need(isinstance(r.get('method'),str) and re.fullmatch('[A-Z]{1,20}',r['method']) and type(r.get('status')) is int and 100<=r['status']<=599,'Malformed log method/status')
        when=stamp(r['at']);need(previous<=when<end and when>=start,'Log time outside ordered window')
        previous=when;seen.add(r['id']);selected=r['url'] in urls and r['method']=='GET' and r['user_agent'] in p['user_agents']
        rows.append(dict(r,selected=selected))
        if selected:
            totals[r['url']]['requests']+=1;totals[r['url']]['server_errors']+=int(r['status']>=500)
    return {'state':'known','values':totals,'rows':rows,'scope':'Exact supplied GET/User-Agent/window counts; operator identity and population authenticity not established'}

def stage(t,ip,p,dep,name,declared,observed):
    note={'id':name,'rows':[],'api':{},'logs':{'state':'unknown','reason':'Missing qualified complete export'}}
    def row(subject,fn):
        try:o,r=fn()
        except ERRORS as e:o,r='inconclusive',str(e)
        note['rows'].append({'subject':subject,'outcome':o,'reason':r})
    urls=[m['url'] for m in ip['members']]
    try:
        start,end=window(p,dep,name);note['window_utc']={'start':utc(start),'end':utc(end)};note['pending']=end>observed
        need(end<=observed,'Future stage; no completed observation inferred')
        c=unique(t.get('monitoring_checkpoints'),name);note['observed_at']=c['observed_at'];at=stamp(c['observed_at'])
        need(type(p.get('review_grace_hours')) is int and 1<=p['review_grace_hours']<=168,'Unknown checkpoint grace')
        need(end<=at<=end+p['review_grace_hours']*3600 and at<=observed,'Checkpoint outside closed stage/grace/assessment')
    except ERRORS as e:
        row('stage',lambda:('inconclusive',str(e)));return note
    sub={'url':t['url'],'observed_at':c['observed_at'],'intent':t['intent'],'context':t['context'],'inspection_synthetic':t['inspection_synthetic'],'inspection_records':c.get('inspection_records')}
    row('native-inspection',lambda:inspection.assess(sub,'TS08-A02'))
    for m in ip['members']:
        try:
            r,req,engine=inspection.record(sub,ip,m,declared,at)
            need(start<=stamp(r['retrieved_at'])<end,'API acquisition outside exact stage window')
            need(req['inspectionUrl']==m['url'],'API request differs from assigned URL')
            need(engine['state']=='recorded' and engine['fields']['verdict']['state']=='present','No known native API verdict')
            note['api'][m['url']]={'state':'known','value':engine['fields']['verdict']['value'],'retrieved_at':r['retrieved_at'],'engine':engine}
            row(m['url']+':window',lambda:('pass','API acquisition belongs to stage, separate from reported crawl'))
        except ERRORS as e:
            note['api'][m['url']]={'state':'unknown','reason':str(e)};row(m['url']+':window',lambda:('inconclusive',str(e)))
    try:
        note['logs']=logs(t,p,c,start,end,urls);row('logs',lambda:('pass','Complete bounded supplied log inventory; no verified Google visit'))
    except ERRORS as e:note['logs']={'state':'unknown','reason':str(e)};row('logs',lambda:('inconclusive',str(e)))
    return note


def assess(t,rule,*,diagnostics=None):
    note={'reader':READER,'version':VERSION,'target':t.get('url'),'rule_id':rule,'rows':[],'stages':[],
          'scope':'One selected release follow-up dossier; no live indexing, authenticated operator, causality or whole-site conformity'}
    def row(subject,fn):
        try:o,r=fn()
        except ERRORS as e:o,r='inconclusive',str(e)
        note['rows'].append({'subject':subject,'outcome':o,'reason':r})
    try:
        ip,p,declared,observed=header(t);note['plan']=p;dep=None
        try:dep=deployment(t,observed);note['deployment']=dep
        except ERRORS as e:note['deployment_error']=str(e)
        if rule=='TS36-A01':
            row('prior-plan',lambda:policy(p,declared))
            for key in ('selection','objectives','schedule','logging'):
                def plan_review(key=key):
                    q=inspection.review(t.get('monitoring_plan_review'),digest({'url':t['url'],'intent':t['intent']}),declared,stamp(p['baseline_start']),t['inspection_synthetic'])
                    return inspection.judgment(q,key)
                row('plan:'+key,plan_review)
            def receipt():
                need(dep is not None,note.get('deployment_error','Missing deployment'))
                for k in ('release_id','environment','before_artifact_sha256','after_artifact_sha256'):
                    if dep[k]!=p.get(k):return 'fail','Release '+k+' contradicts prior plan'
                when=stamp(dep['deployed_at'])
                if when<stamp(p['baseline_end']):return 'fail','Declared deployment precedes baseline completion'
                need(stamp(p['deployment_window_start'])<=when<=stamp(p['deployment_window_end']),'Deployment outside prior window')
                return 'pass','Supplied release identity and chronology; not production authentication'
            row('deployment',receipt)
            def baseline():
                c=unique(t.get('monitoring_checkpoints'),'baseline');need(dep is not None,'Missing release time')
                if stamp(c['observed_at'])>stamp(dep['deployed_at']):return 'fail','Baseline recorded after declared deployment'
                need(stamp(p['baseline_end'])<=stamp(c['observed_at'])<=observed,'Unqualified baseline date')
                return 'pass','Baseline recorded before declared deployment'
            row('baseline-order',baseline)
        elif rule in ('TS36-A02','TS36-A03'):
            row('stage-population',lambda:population(t.get('monitoring_checkpoints'),STAGES,'checkpoints'))
            if dep is None:row('deployment-attribution',lambda:('inconclusive',note.get('deployment_error','Missing release')))
            for name in STAGES:
                s=stage(t,ip,p,dep,name,declared,observed);note['stages'].append(s)
                if rule=='TS36-A02':
                    note['rows'].extend(dict(r,subject=name+':'+r['subject']) for r in s['rows'])
            if rule=='TS36-A03':
                row('review-population',lambda:population(t.get('monitoring_reviews'),STAGES,'stage reviews'))
                for s in note['stages']:
                    name=s['id']
                    try:
                        c=unique(t.get('monitoring_checkpoints'),name);q=unique(t.get('monitoring_reviews'),name)
                        dates=[stamp(c['observed_at'])]
                        dates.extend(stamp(r['retrieved_at']) for r in c.get('inspection_records',[]))
                        if isinstance(c.get('logs'),dict):dates.append(stamp(c['logs']['observed_at']))
                        inspection.review(q,stage_binding(t,c),max(dates),observed,t['inspection_synthetic'])
                        s['supplied_review']=q
                    except ERRORS as e:row(name+':review',lambda:('inconclusive',str(e)));continue
                    def claims_population(q=q):
                        cl=q.get('claims');urls={m['url'] for m in ip['members']}
                        need(isinstance(cl,dict) and set(cl)=={'api','logs'} and all(isinstance(cl[k],dict) and set(cl[k])==urls for k in cl),'Missing/foreign claim population')
                        return 'pass','Exactly the selected API/log claims'
                    row(name+':claims',claims_population)
                    for m in ip['members']:
                        u=m['url']
                        def api_claim(s=s,q=q,u=u):
                            f=s['api'].get(u,{});need(f.get('state')=='known',f.get('reason','Unknown stage API'))
                            want=q.get('claims',{}).get('api',{}).get(u);need(want in ('PASS','FAIL','NEUTRAL'),'Missing API verdict claim')
                            return ('pass' if want==f['value'] else 'fail','Supplied API verdict claim against native known value')
                        def log_claim(s=s,q=q,u=u):
                            f=s['logs'];need(f['state']=='known',f.get('reason','Unknown log'))
                            want=q.get('claims',{}).get('logs',{}).get(u)
                            need(isinstance(want,dict) and set(want)=={'requests','server_errors'} and all(type(x) is int and x>=0 for x in want.values()),'Missing typed log count claims')
                            return ('pass' if want==f['values'][u] else 'fail','Supplied counts against complete known log inventory')
                        row(name+':'+u+':api-claim',api_claim);row(name+':'+u+':log-claim',log_claim)
                    for key in ('interpretation','anomalies','log_completeness','clock_scope'):
                        row(name+':'+key,lambda q=q,key=key:inspection.judgment(q,key))
                    def temporal(q=q):
                        scope=q.get('temporal_scope');need(scope in ('reported-index-and-separate-log-windows','current-live-page','all-fields-at-last-crawl','authenticated-googlebot'),'Missing temporal scope')
                        return ('pass' if scope=='reported-index-and-separate-log-windows' else 'fail','Indexed report and declared User-Agent log windows; not one live/authenticated state')
                    def relation(q=q):
                        need(q.get('objective_relation') in ('aligned','different'),'Missing objective relation');return 'pass','Supplied objective relation, not an automatic SEO outcome'
                    row(name+':temporal-scope',temporal);row(name+':objective-relation',relation);row(name+':decision',lambda q=q:decisions(q))
                def closure():
                    dates=[declared]
                    for c in t.get('monitoring_checkpoints',[]):dates.append(stamp(c['observed_at']))
                    for q in t.get('monitoring_reviews',[]):dates.append(stamp(q['observed_at']))
                    q=inspection.review(t.get('monitoring_closure_review'),closure_binding(t),max(dates),observed,t['inspection_synthetic'])
                    need(type(q.get('completed')) is bool,'Missing closure status')
                    if q['completed'] and any(window(p,dep,n)[1]>stamp(q['observed_at']) for n in STAGES):return 'fail','Supplied closure asserts completion before windows future at its own review date'
                    need(q['completed'],'Follow-up explicitly still open')
                    need(q.get('causality')=='not-established','Unsupported causal closure claim')
                    return 'pass','Supplied completed documentary cycle, no causal attribution'
                row('closure',closure)
            base=next(s for s in note['stages'] if s['id']=='baseline');comparisons=[]
            for s in note['stages'][1:]:
                for m in ip['members']:
                    u=m['url'];a=base['api'].get(u,{});b=s['api'].get(u,{})
                    r={'stage':s['id'],'url':u,'verdict_change':'unknown'}
                    if a.get('state')==b.get('state')=='known':r['verdict_change']='same' if a['value']==b['value'] else 'different'
                    if base['logs']['state']==s['logs']['state']=='known':r['count_deltas']={k:s['logs']['values'][u][k]-base['logs']['values'][u][k] for k in ('requests','server_errors')}
                    comparisons.append(r)
            note['comparisons']=comparisons
        else:need(False,'Unsupported monitoring rule')
    except ERRORS as e:row('plan',lambda:('inconclusive',str(e)))
    outcomes=[r['outcome'] for r in note['rows']]
    outcome='fail' if 'fail' in outcomes else 'inconclusive' if not outcomes or 'inconclusive' in outcomes else 'pass';note['outcome']=outcome
    if len(json.dumps(note,ensure_ascii=False,indent=2).encode())>MAX_BYTES:
        outcome='inconclusive';note={'reader':READER,'version':VERSION,'target':t.get('url'),'rule_id':rule,'outcome':outcome,'rows':[{'subject':'bound','outcome':outcome,'reason':'Complete monitoring diagnostic exceeds 4 MiB; no truncated conclusion'}]}
    if diagnostics is not None:diagnostics.append(note)
    return outcome,PREFIX+json.dumps(note,ensure_ascii=False,separators=(',',':'))
