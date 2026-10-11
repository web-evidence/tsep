#!/usr/bin/env python3
"""Observe supplied delivery variants and bounded Vary matching. Apache-2.0.

No collection, cache simulator, operator authentication or TSEP control verdict.
"""
import argparse
from datetime import timedelta
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import urljoin,urlsplit

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import tsep
from conformance import http
from conformance.http import Unknown,need
from provenance import runtime

VERSION='1'
TOKEN=r"[!#$%&'*+.^_`|~0-9A-Za-z-]+"
REDIRECTS=(301,302,303,307,308)
FIELDS=('link','x-robots-tag','content-language','vary','location','cache-control',
        'age','etag','last-modified','content-type','content-encoding')
LIMITS={'cells':64,'pairs':128,'hops_per_cell':20,'request_fields':32,'vary_members':128,
        'window_seconds':86400,'input_bytes':8*1024*1024,'aggregate_http_bytes':8*1024*1024}
SCOPE=('Supplied complete or partial HTTP observations and bounded Vary request-field matching only. '
       'No cache reuse, storage/freshness/revalidation, region/POP, operator identity, semantic content/language '
       'equivalence, rendered/source SEO interpretation, global coverage or TS39 verdict established.')
ERRORS=(ValueError,TypeError,KeyError,AttributeError,OverflowError,RecursionError)


def digest(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def identity():
    return runtime.loaded_sources(ROOT,{'experiments/delivery_variants.py':sys.modules[__name__],
        'conformance/http.py':http,'tsep.py':tsep,'provenance/runtime.py':runtime})


def url(value):
    need(isinstance(value,str) and len(value)<=8192 and not re.search(r'[\s\x00-\x1f\x7f]',value),
         'Invalid explicit URL')
    p=urlsplit(value)
    need(p.scheme in ('http','https') and p.hostname and not p.username and not p.password
         and not p.fragment and (p.port is None or 0<p.port<=65535),'Invalid explicit URL')
    return p


def identifier(value):return isinstance(value,str) and re.fullmatch('[a-zA-Z0-9_-]{1,80}',value)


def validate(data):
    need(isinstance(data,dict) and data.get('kind')=='delivery-variants-input' and data.get('version')=='1',
         'Unknown delivery observation input')
    need(set(data)=={'kind','version','synthetic','plan','observations'} and type(data['synthetic']) is bool,
         'Unexpected input fields; expected outcomes are not reader inputs')
    need(len(json.dumps(data,ensure_ascii=False,allow_nan=False).encode())<=LIMITS['input_bytes'],'Input byte bound exceeded')
    p=data['plan'];need(isinstance(p,dict),'Missing delivery plan')
    declared,start,end=[tsep.timestamp(p[k]) for k in ('declared_at','window_start','window_end')]
    need(declared<=start<end and end-start<=timedelta(seconds=LIMITS['window_seconds']),'Prior bounded window required')
    cells=p['cells'];need(isinstance(cells,list) and 0<len(cells)<=LIMITS['cells'],'Cell population bound exceeded')
    ids=set()
    for c in cells:
        need(isinstance(c,dict) and identifier(c.get('id')),'Invalid planned cell')
        need(c['id'] not in ids,'Duplicate planned cell');ids.add(c['id']);url(c['url'])
        need(isinstance(c.get('user_agent'),str) and c['user_agent'].strip() and re.fullmatch(r'[\x20-\x7e]{1,2048}',c['user_agent']),
             'Explicit full User-Agent required')
        fields=c.get('request_fields')
        need(isinstance(fields,dict) and len(fields)<=LIMITS['request_fields'],'Bounded request fields required')
        for name,values in fields.items():
            need(isinstance(name,str) and re.fullmatch(TOKEN,name) and name==name.lower()
                 and name not in ('host','user-agent'),'Lowercase request field required; Host/client are separate')
            need(values is None or isinstance(values,list) and 0<len(values)<=32 and all(
                isinstance(v,str) and len(v)<=8192 and not re.search('[\r\n\x00]',v) and v==v.strip(' \t') for v in values),
                'Request field is absent (null) or an ordered list of parsed values')
        claims=c.get('context_claims')
        need(isinstance(claims,dict) and len(claims)<=32 and all(isinstance(k,str) and isinstance(v,str)
             and len(k)<=80 and len(v)<=2048 for k,v in claims.items()),'Bounded unverified context claims required')
    pairs=p['pairs'];need(isinstance(pairs,list) and len(pairs)<=LIMITS['pairs'],'Comparison bound exceeded')
    seen=set()
    for pair in pairs:
        need(isinstance(pair,dict) and identifier(pair.get('id')) and pair['id'] not in seen
             and pair.get('left') in ids and pair.get('right') in ids and pair['left']!=pair['right'],'Invalid comparison')
        seen.add(pair['id'])
    obs=data['observations'];need(isinstance(obs,list) and len(obs)<=LIMITS['cells'],'Observation bound exceeded')
    found={};size=0
    for o in obs:
        need(isinstance(o,dict) and o.get('cell_id') in ids,'Unplanned observation')
        need(o['cell_id'] not in found,'Duplicate observation');found[o['cell_id']]=o
        need(isinstance(o.get('http'),list) and len(o['http'])<=LIMITS['hops_per_cell'],'HTTP hop bound exceeded')
        # The JSON bound also catches invalid encoded records before decoding.
        size+=len(json.dumps(o['http'],ensure_ascii=False,allow_nan=False).encode())
    need(size<=LIMITS['aggregate_http_bytes'],'Aggregate HTTP byte bound exceeded')
    return p,found


def vary(headers):
    values=headers.get('vary');result={'present':values is not None,'raw':values,'valid':True,'fields':[],'wildcard':False}
    if values is None:return result
    members=','.join(values).split(',')
    if len(members)>LIMITS['vary_members']:
        result.update(valid=False,reason='Vary member bound exceeded');return result
    for part in members:
        member=part.strip(' \t')
        if not member:continue  # RFC list recipients tolerate bounded empty members.
        if not re.fullmatch(TOKEN,member):
            result.update(valid=False,reason='Invalid Vary member');return result
        name=member.lower()
        if name=='*':result['wildcard']=True
        elif name not in result['fields']:result['fields'].append(name)
    return result


def preferences(values,field):
    """Qualified only for language ranges/codings and q weights, not full negotiation."""
    items=','.join(values).split(',');need(len(items)<=128,'Preference list bound exceeded')
    result=[];seen=set()
    token=r'(?:\*|[A-Za-z]{1,8}(?:-[A-Za-z0-9]{1,8})*)' if field=='accept-language' else TOKEN
    for item in items:
        if not item.strip(' \t'):continue
        m=re.fullmatch(r'[ \t]*('+token+r')[ \t]*(?:;[ \t]*[qQ]=(0(?:\.[0-9]{0,3})?|1(?:\.0{0,3})?)[ \t]*)?',item)
        need(m is not None,'Unqualified preference syntax')
        name=m[1].lower();need(name not in seen,'Duplicate preference range/coding');seen.add(name)
        weight=int(round(float(m[2] or '1')*1000));result.append((name,weight))
    return result


def field_match(name,left,right):
    if left is None or right is None:return 'equal' if left is right else 'different'
    if left==right:return 'equal'
    if name not in ('accept-language','accept-encoding'):return 'undetermined'
    try:a,b=preferences(left,name),preferences(right,name)
    except ERRORS:return 'undetermined'
    if a==b:return 'equal'
    # Do not assume order irrelevance, including equal-weight language preferences.
    return 'undetermined' if sorted(a)==sorted(b) else 'different'


def vary_match(left,right):
    if left is None or right is None:return {'match':'undetermined','reason':'Missing attributable terminal response'}
    if left['url']!=right['url']:return {'match':'not-comparable','reason':'Different target URIs'}
    v=left['vary']
    if not v['valid']:return {'match':'undetermined','reason':'Stored-side Vary is unqualified'}
    if v['wildcard']:return {'match':'nonmatching','reason':'Stored-side Vary contains *'}
    if not v['fields']:return {'match':'unconstrained','reason':'No stored-side Vary fields; not evidence of valid cache reuse'}
    comparisons={name:{'left':left['request_headers'].get(name),'right':right['request_headers'].get(name),
        'comparison':field_match(name,left['request_headers'].get(name),right['request_headers'].get(name))} for name in v['fields']}
    values=[v['comparison'] for v in comparisons.values()]
    result='nonmatching' if 'different' in values else 'undetermined' if 'undetermined' in values else 'matching'
    return {'match':result,'fields':comparisons,'reason':'Stored-side request-field condition only; no reuse, freshness, storage or validation established'}


def observe_cell(c,o,p):
    result={'id':c['id'],'observed':o is not None,'complete':False,'request_plan_matches':True,
            'context_claims':c['context_claims'],'context_authentication':'not-established',
            'cache_reuse':'not-established','hops':[],'terminal':None,'final_url':None,'issues':[]}
    if o is None:result['issues'].append('Planned cell not observed');return result
    expected=c['url'];previous=tsep.timestamp(p['window_start']);end=tsep.timestamp(p['window_end']);visited=set()
    for index,hop in enumerate(o['http']):
        try:
            need(isinstance(hop,dict) and hop.get('url')==expected,'Missing or mismatched redirect hop')
            parts=url(expected);need(expected not in visited,'Redirect cycle');visited.add(expected)
            sent,received=[tsep.timestamp(hop[k]) for k in ('sent_at','received_at')]
            need(previous<=sent<=received<=end,'Exchange outside prior window/order');previous=received
            first,request,request_body=http.message(hop['request'])
            path=(parts.path or '/')+('?' + parts.query if parts.query else '')
            need(first=='GET '+path+' HTTP/1.1' and not request_body,'Only bodyless HTTP/1.1 GET requests are observed')
            need(request.get('host')==[parts.netloc],'Request Host differs from URL')
            need(request.get('user-agent')==[c['user_agent']],'Request User-Agent differs from declared client')
            differences={name:{'planned':values,'observed':request.get(name)} for name,values in c['request_fields'].items()
                         if request.get(name)!=values}
            if differences:result['request_plan_matches']=False
            first,headers,_=http.header_fields(hop['response'])
            status_match=re.fullmatch(r'HTTP/1\.[01] ([1-5][0-9]{2})(?: [^\r\n]*)?',first)
            need(status_match is not None,'Unsupported response status line')
            status=int(status_match[1]);need(status>=200,'No terminal response after informational status')
            row={'url':expected,'status':status,'request_headers':request,'response_headers':headers,
                 'vary':vary(headers),'request_dimension_differences':differences,'sent_at':hop['sent_at'],
                 'received_at':hop['received_at'],'capture_declared_complete':hop.get('complete') is True,
                 'body_complete':False,'body_sha256':None,'issues':[],
                 'request_sha256':hashlib.sha256(http.raw_bytes(hop['request'])).hexdigest(),
                 'response_sha256':hashlib.sha256(http.raw_bytes(hop['response'])).hexdigest()}
            result['hops'].append(row)
            try:
                need(hop.get('complete') is True,'Capture declared incomplete')
                need(status not in (204,205,206,304) and not any(k in request for k in ('range','if-range','if-none-match','if-modified-since')),
                     'Body/conditional semantics outside this observer profile')
                _,_,body=http.message(hop['response'],True)
                row.update(body_complete=True,body_sha256=http.body_digest(body))
            except ERRORS as error:row['issues'].append(str(error))
            if status in REDIRECTS:
                locations=headers.get('location',[])
                need(len(locations)==1 and locations[0],'Missing or ambiguous redirect Location')
                expected=urljoin(expected,locations[0]);url(expected)
                need(index<len(o['http'])-1,'Unfinished redirect chain')
            else:
                need(index==len(o['http'])-1,'Unexpected hop after terminal response')
                result.update(terminal=index,final_url=row['url'])
        except ERRORS as error:result['issues'].append(str(error));break
    if not o['http']:result['issues'].append('Planned cell has no HTTP exchange')
    result['complete']=(result['terminal'] is not None and not result['issues'] and result['request_plan_matches']
                        and all(h['body_complete'] for h in result['hops']))
    return result


def terminal(cell):return cell['hops'][cell['terminal']] if cell['terminal'] is not None else None


def compare(pair,cells):
    left,right=[cells[pair[k]] for k in ('left','right')];a,b=terminal(left),terminal(right)
    result=dict(pair,same_resource=None,status='unavailable',body='unavailable',header_changes={},
                varying_context_claims={k:{'left':left['context_claims'].get(k),'right':right['context_claims'].get(k)}
                  for k in sorted(set(left['context_claims'])|set(right['context_claims']))
                  if left['context_claims'].get(k)!=right['context_claims'].get(k)},vary=vary_match(a,b),
                all_planned_observations_complete=left['complete'] and right['complete'])
    if a is not None and b is not None:
        result.update(same_resource=a['url']==b['url'],status='equal' if a['status']==b['status'] else 'different',
                      header_changes={k:'equal' if a['response_headers'].get(k)==b['response_headers'].get(k) else 'different' for k in FIELDS})
        if a['body_complete'] and b['body_complete']:
            result['body']='equal' if a['body_sha256']==b['body_sha256'] else 'different'
    return result


def observe(data):
    try:p,obs=validate(data)
    except ERRORS as error:raise ValueError(str(error)) from error
    cells=[observe_cell(c,obs.get(c['id']),p) for c in p['cells']];indexed={c['id']:c for c in cells}
    return {'kind':'delivery-variants-observation','version':VERSION,'normative_effect':'none',
            'synthetic':data['synthetic'],'input_sha256':digest(data),'source_files':identity(),'bounds':LIMITS,
            'cells':cells,'pairs':[compare(pair,indexed) for pair in p['pairs']],
            'network_requests':0,'operator_access':'not-established','scope':SCOPE}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('input',type=Path);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    try:
        before=identity()
        with args.input.open('rb') as handle:raw=handle.read(LIMITS['input_bytes']+1)
        need(len(raw)<=LIMITS['input_bytes'],'Input byte bound exceeded')
        result=observe(tsep.parse_json(raw));need(before==identity(),'Reader sources changed')
        result['input_file_sha256']=hashlib.sha256(raw).hexdigest()
        with args.output.open('x',encoding='utf-8') as handle:json.dump(result,handle,ensure_ascii=False,indent=2);handle.write('\n')
        print(json.dumps({'written':str(args.output),'normative_effect':'none','cells':len(result['cells']),'network_requests':0}));return 0
    except (OSError,)+ERRORS as error:print(str(error),file=sys.stderr);return 64


if __name__=='__main__':sys.exit(main())
