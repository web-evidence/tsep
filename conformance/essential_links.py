"""Bounded TS17 supplied-evidence interpretation. Apache-2.0."""
from datetime import timedelta
import json,os
from urllib.parse import urlsplit
import tsep
from conformance.evaluate import trace
from experiments import url_resolution
from conformance import essential_links_source as source_reader
from conformance import essential_links_dom as dom_reader

ERRORS=(ValueError,TypeError,KeyError,OSError)
def need(ok,reason):
 if not ok:raise ValueError(reason)
def named(v):return isinstance(v,str) and bool(v.strip()) and len(v)<=4096
def header(t):
 need(type(t) is dict,'Target must be an object')
 need(type(t.get('context')) is dict,'Capture context must be an object')
 need(type(t.get('intent')) is dict and type(t['intent'].get('essential_links')) is dict,'Missing object-shaped prior link plan')
 need(len(json.dumps(t,ensure_ascii=False,allow_nan=False).encode())<=8*1024*1024,'Input exceeds bounded JSON profile')
 need(type(t.get('link_synthetic')) is bool,'Explicit synthetic provenance required')
 need(all(named(t.get('context',{}).get(k)) for k in ('network','bounds','tool','tool_version')),'Missing named capture context')
 intent=t['intent'];p=intent['essential_links'];need(p['reader']=='essential-document-links-v1' and p['strategy']=='source-and-rendered','Unsupported prior reader/strategy')
 need(named(p.get('selection_reason')) and named(intent.get('crawler')),'Missing prior selection/client')
 declared,start,end,observed=[tsep.timestamp(x) for x in (intent['declared_at'],p['window_start'],p['window_end'],t['observed_at'])]
 need(declared<=start<=end<=observed and end-start<=timedelta(hours=24),'Prior plan/window chronology unqualified')
 need(type(p['max_duration_ms']) is int and 0<p['max_duration_ms']<=30000,'Finite per-exchange duration required')
 destinations=p['destinations'];need(type(destinations) is list and 1<=len(destinations)<=32,'Bounded essential destination set required')
 need(all(type(x) is dict and set(x)=={'url','reason'} and named(x['url']) and named(x['reason']) for x in destinations),'Each destination needs exact URL and supplied rationale')
 urls=[d['url'] for d in destinations];need(len(urls)==len(set(urls)),'Duplicate essential destination')
 node=os.environ.get('TSEP_SOURCE_NODE');need(named(node),'Explicit qualified Node runtime unavailable')
 texts=urls+[t['url'],p['final_url']];results=url_resolution.resolve([{'url':u,'base':None} for u in texts],node=node)['results']
 for text,r in zip(texts,results):
  need(r['ok'] and r['protocol'] in ('http:','https:') and r['href']==text and '#' not in text and not urlsplit(text).username and not urlsplit(text).password,'Exact serialized credential-free document URLs required')
 need(p['final_url'] not in urls and t['url'] not in urls,'Self-document destination outside profile')
 states=p['states'];need(type(states) is list and 1<=len(states)<=16,'Bounded required rendered-state plan')
 need(all(type(s) is dict and set(s)=={'id','browser','browser_version','scenario'} and all(named(v) for v in s.values()) for s in states),'Named state/scenario/browser required')
 need(len({s['id'] for s in states})==len(states),'Duplicate planned state')
 return p,urls,start,end

def capture(t,p,start,end):
 hops=t['http'];need(type(hops) is list and 1<=len(hops)<=16,'Bounded explicit HTTP trace required')
 need(all(type(hop) is dict for hop in hops),'Each supplied HTTP exchange must be an object')
 final,status,headers,body=trace(hops,t['url'],t['intent']['crawler']);previous=start
 for hop in hops:
  sent,received=tsep.timestamp(hop['sent_at']),tsep.timestamp(hop['received_at']);need(previous<=sent<=received<=end and received-sent<=timedelta(milliseconds=p['max_duration_ms']),'HTTP chronology/duration outside prior window');previous=received
 need(status==200 and final==p['final_url'],'No complete expected HTTP200 representation for link assessment')
 return final,headers,body,previous

def unknown(reason):return {'outcome':'inconclusive','reason':reason}
def assess_target(t):
 result={'kind':'essential-document-links-control-v1','authenticates_evidence':False,'scope':'Declared source-and-rendered strategy only; no whole-site/Google assertion.','state_identity':'provider-declared-not-observed-interactions','http_dom_binding':'supplied-association-not-authenticated-acquisition','repeated_snapshots':[],'source':unknown('Unavailable'),'rendered':unknown('Unavailable')}
 try:p,urls,start,end=header(t)
 except ERRORS as e:result['source']=unknown(str(e));result['rendered']=unknown(str(e));return result
 try:final,headers,body,received=capture(t,p,start,end)
 except ERRORS as e:result['source']=unknown(str(e));result['rendered']=unknown(str(e));return result
 try:
  value={'source':body.decode('utf-8') if type(body) is bytes else body,'complete':True,'content_types':headers.get('content-type',[]),'document_url':final,'destinations':urls}
  result['source']=source_reader.assess(value)
 except ERRORS as e:result['source']=unknown(str(e))
 rows=[];render=t.get('render');actual=render.get('states') if type(render) is dict else None
 if type(actual) is not list or len(actual)>16:result['rendered']=unknown('Missing/excessive supplied states');return result
 groups={}
 for state in actual:
  if type(state) is dict and type(state.get('structured_dom')) is dict:
   digest=state['structured_dom'].get('snapshot_sha256')
   if isinstance(digest,str) and len(digest)==64:groups.setdefault(digest,[]).append(state.get('id'))
 result['repeated_snapshots']=[{'snapshot_sha256':h,'state_ids':ids} for h,ids in sorted(groups.items()) if len(ids)>1]
 planned_ids=[s['id'] for s in p['states']];actual_ids=[s.get('id') if type(s) is dict else None for s in actual]
 if set(x for x in actual_ids if isinstance(x,str))!=set(planned_ids) or len(actual_ids)!=len(set(x for x in actual_ids if isinstance(x,str))):rows.append(dict(id='population',**unknown('Missing, duplicate or unplanned supplied states')))
 for prior in p['states']:
  sid=prior['id'];matches=[s for s in actual if type(s) is dict and s.get('id')==sid]
  if len(matches)!=1:rows.append(dict(id=sid,**unknown('Required state is missing/ambiguous')));continue
  state=matches[0]
  if any(state.get(k)!=prior[k] for k in ('browser','browser_version')):rows.append(dict(id=sid,**unknown('Observed browser differs from prior state')));continue
  value={'state':state,'document_url':final,'destinations':urls,'http':t['http'],'crawler':t['intent']['crawler'],'http_received_at':received.isoformat(),'window_end':p['window_end'],'synthetic':t['link_synthetic']}
  rows.append(dict(id=sid,**dom_reader.assess(value)))
 outcomes=[r['outcome'] for r in rows];result['rendered']={'outcome':'fail' if 'fail' in outcomes else 'inconclusive' if not outcomes or 'inconclusive' in outcomes else 'pass','rows':rows}
 return result

PREFIX='Supplied essential links / liens essentiels fournis: '
RULES=('TS17-A01','TS17-A02')
def assess(target,rule,*,diagnostics=None):
 result=assess_target(target)
 stage={'TS17-A01':'source','TS17-A02':'rendered'}.get(rule)
 result['rule_stage']=stage
 outcome=result[stage]['outcome'] if stage else 'inconclusive'
 if diagnostics is not None:diagnostics.append(result)
 return outcome,PREFIX+json.dumps(result,ensure_ascii=False,sort_keys=True)
