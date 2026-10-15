"""TS23 raw transport qualification, without external collection. Apache-2.0."""
import base64,hashlib,json,datetime
from conformance import hreflang_native as native
from conformance.http import raw_bytes
from conformance.evaluate import trace

need=native.need

def own(container,version):
 if container is None:return
 if type(container)is not dict:raise native.TechnicalRefusal('Original HTTP payload must be a v2 byte object or absent/null evidence')
 if version!='2':raise native.TechnicalRefusal('Binary originals require input_version2')
 if container.get('base64')is None:return
 text=container['base64']
 try:
  need(type(text)is str and len(text)<=4*((8*1024*1024+2)//3),'Original byte bound')
  raw=base64.b64decode(text,validate=True);need(len(raw)<=8*1024*1024 and base64.b64encode(raw).decode()==text,'Noncanonical original')
  if container.get('sha256')is not None:need(type(container['sha256'])is str and hashlib.sha256(raw).hexdigest()==container['sha256'],'Original own digest mismatch')
 except (ValueError,TypeError)as e:raise native.TechnicalRefusal(str(e))from e

def integrity(data):
 t=data.get('target');t=t if type(t)is dict else {};version=data.get('input_version');docs=t.get('hreflang_documents')
 if type(docs)is list:
  for d in docs:
   hops=d.get('http')if type(d)is dict else None
   if hops is not None and (type(hops)is not list or any(type(x)is not dict for x in hops)):raise native.TechnicalRefusal('HTTP structure must be original exchange objects or absent')
   for h in hops or []:
    for k in ('request','response'):own(h.get(k),version)
 other=t.get('hreflang_unsupported_channels')
 if type(other)is list:
  for x in other:
   if type(x)is dict:own(x.get('original'),version)

def qualify(data):
 integrity(data)
 t=data.get('target');notes=[]
 try:
  need(type(t)is dict,'Target required');need(type(t.get('hreflang_synthetic'))is bool,'Explicit synthetic provenance required')
  context=t.get('context');need(type(context)is dict and all(type(context.get(k))is str and 0<len(context[k].strip())<=4096 for k in ['network','bounds','tool','tool_version']),'Named capture context required')
  intent=t['intent'];p=intent['hreflang'];need(type(p)is dict and p.get('reader')=='hreflang-reciprocity-v1','Unsupported prior profile')
  need(set(p)=={'reader','selection_reason','max_duration_ms','window_start','window_end','mappings','pages','excluded_mappings'},'Closed prior transport plan fields')
  need(type(p.get('selection_reason'))is str and bool(p['selection_reason'].strip()) and len(p['selection_reason'])<=4096,'Prior selection rationale required')
  duration=p['max_duration_ms'];need(type(duration)is int and 0<duration<=30000,'Finite integer per-exchange deadline required')
  crawler=intent.get('crawler');need(type(crawler)is str and 0<len(crawler)<=4096,'Named prior client required')
  start,end,prior,observed=[native.stamp(x)for x in [p['window_start'],p['window_end'],intent['declared_at'],t['observed_at']]]
  need(prior<=start<=end<=observed and end-start<=datetime.timedelta(hours=24),'Prior window chronology invalid')
  docs=t.get('hreflang_documents');need(type(docs)is list and len(docs)<=48,'Bounded original documents required')
  component={'synthetic':t['hreflang_synthetic'],'plan':{'version':'1','recorded_at':intent['declared_at'],**{k:p[k]for k in ['window_start','window_end','mappings','pages','excluded_mappings']}},'documents':[],'unsupported_channels':t.get('hreflang_unsupported_channels',[])}
  for doc in docs:
   need(type(doc)is dict,'Structure documentaire non interprétable / Uninterpretable documentary record structure')
   projected={'url':doc.get('url'),'complete':False};note={'url':doc.get('url'),'qualified':False}
   try:
    need(set(doc)=={'url','http'},'Document fields outside closed native profile');hops=doc.get('http');need(type(hops)is list and len(hops)==1,'Initial profile requires one supplied non-redirect exchange')
    hop=hops[0]
    need(all(type(hop.get(k))is dict for k in ['request','response']),'Original v2 byte containers required')
    # raw_bytes requires exact base64+sha fields. Missing hashes are unknown here;
    # malformed present bytes and actual hash contradictions were refused above.
    final,status,headers,body=trace(hops,doc['url'],crawler)
    need(final==doc['url'] and status==200,'Complete exact requested/final HTTP200 required')
    sent,received=[native.stamp(hop[k])for k in ['sent_at','received_at']]
    need(start<=sent<=received<=end and received-sent<=datetime.timedelta(milliseconds=duration),'HTTP chronology or duration outside prior bounds')
    need(type(body)is bytes,'Native binary input profile required')
    types=headers.get('content-type',[]);need(len(types)==1,'One declared response Content-Type required')
    # Preserve duplicate fields from native parsed originals; no matrix input.
    pairs=[[name,value]for name,values in headers.items()for value in values]
    projected.update(requested_url=doc['url'],final_url=final,status=status,content_type=types[0],headers=pairs,headers_sha256=hashlib.sha256(json.dumps(pairs,ensure_ascii=False,separators=(',',':')).encode()).hexdigest(),body_base64=base64.b64encode(body).decode(),body_sha256=hashlib.sha256(body).hexdigest(),complete=True,captured_at=hop['received_at'])
    note.update(qualified=True,request_sha256=hashlib.sha256(raw_bytes(hop['request'])).hexdigest(),response_sha256=hashlib.sha256(raw_bytes(hop['response'])).hexdigest(),decoded_body_sha256=projected['body_sha256'],received_at=hop['received_at'])
   except (ValueError,TypeError,KeyError,OSError)as e:note['reason']=str(e)
   component['documents'].append(projected);notes.append(note)
  result=native.assess(component);result['transport']=notes;result['original_target_sha256']=hashlib.sha256(json.dumps(t,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest();result['originals_retained_in_input']=True
  return result
 except (ValueError,TypeError,KeyError,OSError)as e:return {'outcome':'NT','reason':str(e),'transport':notes,'candidate_normative_profile':'0.1.0-draft.39'}


PREFIX='Supplied hreflang / hreflang fourni: '

def assess(target,rule,*,diagnostics=None):
    value=qualify({'input_version':'2','target':target})
    if len(json.dumps(value,ensure_ascii=False).encode('utf-8'))>4*1024*1024:
        value={'outcome':'NT','reason':'Diagnostic exceeds4MiB; no truncated conclusion'}
    note={'kind':'hreflang-reciprocity-v1','rule':rule,'measurement':value,'scope':'Supplied prior cluster only; no language registry, translation, indexing or Google processing claim.'}
    if diagnostics is not None:diagnostics.append(note)
    return {'C':'pass','NC':'fail','NT':'inconclusive'}[value['outcome']],PREFIX+json.dumps(note,ensure_ascii=False,sort_keys=True)
