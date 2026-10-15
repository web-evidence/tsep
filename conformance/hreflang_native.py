"""Bounded supplied native hreflang interpretation. Apache-2.0."""
import base64,datetime,hashlib,json,os,re,sys
from pathlib import Path
from urllib.parse import urlsplit
import tsep
from experiments import link_elements,source_head,url_resolution
from conformance import http_canonical
from conformance.source_canonical import prefix_issues,ambiguous_attributes
ASCII=str.maketrans('ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')
HTML=link_elements.HTML
class TechnicalRefusal(tsep.Invalid):pass

def need(ok,why):
 if not ok:raise ValueError(why)
def folded(s):return s.translate(ASCII)
def sha(b):return hashlib.sha256(b).hexdigest()
def stamp(s):
 need(type(s)is str and len(s)<=40,'Timestamp absent or oversized')
 t=datetime.datetime.fromisoformat(s.replace('Z','+00:00'));need(t.tzinfo is not None,'Timezone required');return t

def code(c):
 need(type(c)is str and re.fullmatch(r'[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*',c) and len(c)<=35,'Unsupported language token; no registry inference')
 return folded(c)

def url_table(values,node):
 values=sorted(set(values));need(all(type(v)is str and len(v.encode())<=4096 for v in values),'URL bound')
 result=url_resolution.resolve([{'url':u,'base':None} for u in values],node=node)
 table={}
 for u,r in zip(values,result['results']):
  table[u]=bool(r['ok'] and r['protocol'] in ('http:','https:') and r['href']==u and '#' not in u and not urlsplit(u).username and not urlsplit(u).password)
 return table

def body_bytes(document):
 if document.get('body_base64') is not None:
  value=document['body_base64'];need(type(value)is str and len(value)<=4*((8*1024*1024+2)//3),'Body byte container bound')
  raw=base64.b64decode(value,validate=True);need(base64.b64encode(raw).decode()==value,'Noncanonical body bytes');return raw
 need(type(document.get('body'))is str,'Original body bytes unavailable')
 return document['body'].encode('utf-8')

def integrity(data):
 docs=data.get('documents',[])
 if type(docs)is not list:return
 for d in docs:
  if type(d)is not dict:continue
  for content,digest in [('body','body_sha256'),('headers','headers_sha256')]:
   if (d.get(content) is None and not(content=='body' and d.get('body_base64')is not None)) or d.get(digest) is None:continue
   if content=='body':
    raw=body_bytes(d)
   else:raw=json.dumps(d[content],ensure_ascii=False,separators=(',',':')).encode()
   if d[digest]!=sha(raw):raise TechnicalRefusal('Own '+content+' digest mismatch, including unplanned original')

def html_channel(document,node):
 ct=document.get('content_type');result={'channel':'html','active':True,'unknowns':[],'hypotheses':{}}
 if type(ct)is str and not ct.lower().startswith('text/html'):
  return dict(result,active=False,unknowns=['Response is not declared HTML'],hypotheses={})
 raw=body_bytes(document)
 try:
  element=link_elements.inventory(raw,content_types=[ct],node=node)
  prefix=source_head.inventory(raw,content_types=[ct],node=node)
  need(element['decoding']['body_sha256']==prefix['decoding']['body_sha256']==document['body_sha256'],'Observer body binding differs')
  result['source_bindings']={'body_sha256':document['body_sha256'],'element_reader':element['source_sha256'],'head_reader':prefix['source_sha256']}
  for mode in ('enabled','disabled'):
   e=element['readings'][mode];h=prefix['readings'][mode];unknown=[];rows=[];misplaced=[]
   need(e['complete'] and h['complete'] and h['head_prefix']['complete'],'Partial source reader cannot establish absence')
   global_unknown=prefix_issues(h)
   implicit=None
   last=h['head_prefix']['tokens'][-1]
   # New profile policy over unchanged native facts; no parser-error exception.
   before=last['before'];direct=bool(before and before[-1]=={'tag':'head','namespace':HTML})
   supported=(last['kind']=='start-tag' and last['tag']in('div','img','iframe')) or (last['kind']in('characters','text-run') and bool(last['raw'].strip()))
   if direct and supported and last['constructs_document_body'] and not e['parse_errors'] and not h['parse_errors']:
    implicit={'tag':last['tag'],'kind':last['kind'],'raw':last['raw'],'body_span_bytes':last['body_span_bytes'],'basis':'Direct source-head token constructs ordinary body in this static hypothesis'}
    global_unknown=[v for v in global_unknown if v!='Unqualified source head element: '+str(last['tag'])]
   if e['parse_errors'] or h['parse_errors']:global_unknown.append('HTML recovery or duplicate attributes require review')
   for t in e['templates']:
    if link_elements.attribute(t,'shadowrootmode') is not None or link_elements.attribute(t,'for') is not None:global_unknown.append('Supplied shadow/template attachment outside profile')
   closed=[t['source_span_utf16'][0] for t in h['head_prefix']['tokens'] if t['closes_document_head']]
   close=min(closed) if closed else None
   for r in e['records']:
    if r['tag']!='link':continue
    attrs={a['local_name']:a['value'] for a in r['attributes'] if a['namespace'] is None}
    rel=sorted({v for v in re.split(r'[\t\n\f\r ]+',folded(attrs.get('rel',''))) if v})
    if 'alternate' not in rel or 'stylesheet' in rel:continue
    if r['template_indices']:continue
    try:
     need(r['namespace']==HTML and all(n in (None,HTML) for n in r['ancestor_namespaces']),'Foreign source ancestry')
     need(r['source_span_utf16'] is not None and r['body_span_bytes'] is not None,'Unattributed source annotation')
     need(not ambiguous_attributes(r,e['parse_errors']),'Duplicate attributes on annotation')
     need(rel==['alternate'],'Combined relation purpose outside profile')
     need(not(set(attrs)&{'media','type','as','disabled'}),'Purpose modifiers need review')
     c=code(attrs.get('hreflang'));u=attrs.get('href');need(type(u)is str and bool(u),'Missing href')
     row={'code':c,'url':u,'body_span_bytes':r['body_span_bytes'],'raw_tag':r['raw_tag']}
     if r['context']=='body':misplaced.append(row);continue
     need(r['context']=='head' and r['ancestors'][-1]=='head','Indirect source head annotation needs review')
     need(close is None or r['source_span_utf16'][0]<close,'Annotation reinserted after explicit source head closure')
     rows.append(row)
    except (ValueError,TypeError,KeyError) as ex:unknown.append(str(ex))
   need(len(rows)+len(misplaced)<=128,'Annotation population bound exceeded')
   result['hypotheses'][mode]={'rows':rows,'misplaced':misplaced,'unknowns':global_unknown+unknown,'global_unqualified':bool(global_unknown),'absence_blocked':bool(global_unknown+unknown),'implicit_head_closure':implicit}
 except (ValueError,TypeError,KeyError,OSError) as ex:result['unknowns'].append(str(ex))
 return result

def http_channel(document):
 result={'channel':'http-link','active':False,'rows':[],'unknowns':[],'absence_blocked':False}
 try:
  headers=document['headers'];need(type(headers)is list and len(headers)<=100,'Header population bound')
  need(all(type(x)is list and len(x)==2 and all(type(v)is str for v in x) for x in headers),'Original header pairs required')
  fields=[v for k,v in headers if folded(k)=='link'];need(sum(len(v.encode()) for v in fields)<=65536,'Link field byte bound')
  result['active']=bool(fields)
  seen=0
  for field in fields:
   for raw,error in http_canonical.split_field(field):
    try:
     seen+=1;need(seen<=128,'Link item population bound');need(error is None,error)
     target,params=http_canonical.parse_item(raw);by={}
     for p in params:by.setdefault(p['name'],[]).append(p['value'])
     rels=by.get('rel',[]);need(len(rels)==1 and type(rels[0])is str,'One relation parameter required')
     rel=sorted({folded(v) for v in rels[0].split(' ') if v})
     if 'alternate' not in rel or 'stylesheet' in rel:continue
     need([folded(v) for v in rel]==['alternate'],'Combined relation purpose outside profile')
     need(set(by)<= {'rel','hreflang'},'Unsupported alternate parameter, including anchor')
     langs=by.get('hreflang',[]);need(len(langs)==1,'One hreflang parameter required')
     result['rows'].append({'code':code(langs[0]),'url':target,'raw_item':raw})
    except (ValueError,TypeError,KeyError,http_canonical.Unknown) as ex:result['unknowns'].append(str(ex));result['absence_blocked']=True
 except (ValueError,TypeError,KeyError) as ex:result['unknowns'].append(str(ex));result['absence_blocked']=True
 return result

def mapping_decision(channel,expected,excluded,valid,primary):
 rows=channel['rows'];unknown=list(channel['unknowns']);failures=[];found=set();outside=[]
 blocked=channel.get('absence_blocked',False)
 if channel.get('global_unqualified'):return {'outcome':'NT','unknowns':unknown,'found':[],'failures':[],'outside':[]}
 for row in rows:
  c,u=row['code'],row['url']
  if not valid.get(u,False):
   label='Non évalué : URL relative hors profil / Not evaluated: relative URL outside profile: ' if not urlsplit(u).scheme else 'Unsupported absolute exact target: '
   unknown.append(label+u);blocked=True;continue
  if c in expected:
   if u==expected[c]:found.add((c,u))
   else:failures.append({'kind':'conflicting-target','code':c,'expected':expected[c],'observed':u,'native':row})
  elif (c,u) in excluded:outside.append({'mapping':[c,u],'state':'prior-excluded'})
  else:outside.append({'mapping':[c,u],'state':'unplanned'});unknown.append('Unplanned mapping outside declared group')
 for row in channel.get('misplaced',[]) if primary else []:
  if valid.get(row['url'],False) and row['code'] in expected:failures.append({'kind':'outside-required-head','native':row})
  else:unknown.append('Unsupported misplaced annotation');blocked=True
 missing=[{'code':c,'url':u} for c,u in expected.items() if (c,u)not in found]
 if primary and missing and not blocked:failures.append({'kind':'primary-mappings-missing','mappings':missing})
 return {'outcome':'NC' if failures else 'NT' if unknown else 'C','found':[list(x) for x in sorted(found)],'missing':missing,'complete_expected_set':not missing and not blocked,'failures':failures,'unknowns':unknown,'outside':outside}

def assess(data):
 integrity(data)
 result={'profile':'hreflang-reciprocity-v1','synthetic':data.get('synthetic')is True,'outcome':'NT','pages':[],'unknowns':[],'candidate_normative_profile':'0.1.0-draft.39','authenticates_evidence':False}
 try:
  need(len(json.dumps(data,ensure_ascii=False).encode())<=8*1024*1024,'Input bound exceeded')
  node=os.environ.get('TSEP_SOURCE_NODE');need(bool(node),'Explicit qualified Node24 runtime required')
  p=data['plan'];need(type(p)is dict and p.get('version')=='1','Prior plan unavailable')
  need(set(p)=={'version','recorded_at','window_start','window_end','mappings','pages','excluded_mappings'},'Closed prior plan fields')
  start,end,prior=(stamp(p[k]) for k in ['window_start','window_end','recorded_at']);need(prior<=start<=end and end-start<=datetime.timedelta(hours=24),'Prior bounded window required')
  mappings=p['mappings'];pages=p['pages'];excluded=p['excluded_mappings']
  need(type(mappings)is list and 1<=len(mappings)<=32 and type(pages)is list and 1<=len(pages)<=16,'Prior population bounds')
  need(type(excluded)is list and len(excluded)<=32,'Excluded population bound')
  expected={}
  for pair in mappings:
   need(type(pair)is list and len(pair)==2,'Mapping pair required');c=code(pair[0]);need(c not in expected,'Duplicate normalized prior language');expected[c]=pair[1]
  exc=[]
  for pair in excluded:
   need(type(pair)is list and len(pair)==2,'Excluded mapping pair');c=code(pair[0]);need(c not in expected,'Expected code cannot be excluded');exc.append((c,pair[1]))
  need(len(set(exc))==len(exc),'Duplicate excluded mapping')
  pageurls=[]
  for page in pages:
   need(type(page)is dict and set(page)=={'url','primary'} and page['primary']in('html','http-link'),'Unsupported prior page mode')
   pageurls.append(page['url'])
  need(len(set(pageurls))==len(pageurls) and set(pageurls)==set(expected.values()),'Prior pages and mapped URLs differ')
  planned=url_table(list(expected.values())+[u for c,u in exc],node);need(all(planned.values()),'Unsupported planned URL')
  docs=data['documents'];need(type(docs)is list and len(docs)<=48,'Original document bound')
  by={}
  for doc in docs:
   need(type(doc)is dict and type(doc.get('url'))is str,'Original identity absent');need(doc['url']not in by,'Duplicate original document URL');by[doc['url']]=doc
  for page in pages:
   pr={'url':page['url'],'primary':page['primary'],'outcome':'NT','channels':{}}
   try:
    need(page['url'] in by,'Original fourni absent pour la page prévue / Missing supplied original for planned page: '+page['url'])
    d=by[page['url']];need(d.get('complete')is True and d.get('status')==200 and d.get('requested_url')==d.get('final_url')==page['url'],'Complete exact requested/final HTTP200 required')
    need(prior<=stamp(d['captured_at']) and start<=stamp(d['captured_at'])<=end,'Original outside prior capture window')
    body_bytes(d);need(type(d.get('body_sha256'))is str and type(d.get('headers_sha256'))is str,'Original body and header digest required')
    h=html_channel(d,node);t=http_channel(d)
    allrows=t['rows']+[r for hyp in h['hypotheses'].values() for r in hyp['rows']+hyp.get('misplaced',[])]
    valid=url_table([r['url'] for r in allrows],node)
    td=mapping_decision(t,expected,exc,valid,page['primary']=='http-link');pr['channels']['http-link']=dict(t,decision=td)
    decisions=[]
    for mode,hyp in h['hypotheses'].items():decisions.append(mapping_decision(hyp,expected,exc,valid,page['primary']=='html'));hyp['decision']=decisions[-1]
    hd='NT'
    if decisions and len({x['outcome'] for x in decisions})==1:hd=decisions[0]['outcome']
    if not h['active'] and page['primary']!='html':hd='C'
    pr['channels']['html']=dict(h,outcome=hd)
    pr['outcome']='NC' if td['outcome']=='NC' or hd=='NC' else 'NT' if td['outcome']=='NT' or hd=='NT' else 'C'
   except (ValueError,TypeError,KeyError,OSError) as ex:pr['reason']=str(ex)
   result['pages'].append(pr)
  if data.get('unsupported_channels'):result['unknowns'].append('Relevant supplied unsupported channel remains outside this profile')
  statuses=[p['outcome'] for p in result['pages']];result['outcome']='NC' if 'NC'in statuses else 'NT' if 'NT'in statuses or result['unknowns'] else 'C'
 except (ValueError,TypeError,KeyError,OSError) as ex:result['unknowns'].append(str(ex))
 if len(json.dumps(result,ensure_ascii=False).encode())>4*1024*1024:result={'profile':result['profile'],'outcome':'NT','reason':'Diagnostic bound exceeded; no truncated conclusion','candidate_normative_profile':'0.1.0-draft.39'}
 return result
