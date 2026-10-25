"""TS09/11/19/20/38 bounded policy and native URL evidence. Apache-2.0."""
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from urllib.parse import urljoin, unquote_to_bytes
from conformance.evidence_dossier import Dossier, Findings, ERRORS, address, digest, text
from conformance.http import need

VERSION='2'
COUNTS={'TS09':1,'TS11':2,'TS19':2,'TS20':2,'TS38':2}
RULES=tuple(c+'-A%02d'%n for c,count in COUNTS.items() for n in range(1,count+1))
LIMITATION=('Supplied finite population and bound human judgments only. No acquisition or reviewer authentication, '
            'site-wide completeness, Google canonical choice, indexing, ranking or actual crawl volume established.')


def one(rows,identity):
    need(isinstance(rows,list) and len(rows)<=128,'Missing/bounded native rows')
    matches=[r for r in rows if isinstance(r,dict) and r.get('id')==identity]
    need(len(matches)==1,'Missing/ambiguous native item '+str(identity))
    return matches[0]


def crawl(d,identity):
    value,record=d.json(identity,'crawl','url-crawl-v1')
    rows=value.get('rows');need(isinstance(rows,list) and 1<=len(rows)<=128,'1–128 native crawl rows required')
    need(all(isinstance(r,dict) and text(r.get('key'),128) and text(r.get('url'),4096) for r in rows),'Incomplete crawl row')
    need(len({r['key'] for r in rows})==len(rows),'Ambiguous crawl identity')
    return rows,record


def canonical(d,url,preferred,f):
    from conformance.canonical import html,header_canonicals
    from conformance.evaluate import utf8_media
    final,status,headers,body=d.response(url)
    f.compare(url+':status',status==200,'Expected final200; observed '+str(status))
    if status!=200:return
    values=[]
    def header():
        found=header_canonicals(headers);values.extend(found)
        if found:f.compare(url+':HTTP canonical',all(urljoin(final,v)==preferred for v in found),'Every supplied HTTP canonical must match declared destination')
    f.check(url+':headers',header)
    def source():
        need(utf8_media(headers,('text/html',)),'UTF8 HTML source required')
        parsed=html(body,source=True);values.extend(v for v,_ in parsed.canonicals)
        if parsed.canonicals:f.compare(url+':HTML canonical',all(in_head and urljoin(final,v)==preferred for v,in_head in parsed.canonicals),'Every source canonical must match declared destination in head')
    f.check(url+':source',source)
    if not values:f.add(url,'inconclusive','No qualified explicit canonical; absence does not prove a chosen canonical')


def exclusions(d,item,rule,f):
    raw,_=d.json(item['record'],'configuration','exclusion-register-v1')
    family=one(raw.get('families'),item['id'])
    need(text(item.get('mechanism')),'Prior exclusion mechanism required')
    need(text(family.get('mechanism')),'Missing supplied mechanism')
    f.compare(item['id'],family['mechanism']==item['mechanism'],'Configured and intended exclusion mechanisms compared; not execution/index state')
    need(all(text(family.get(k)) for k in ('owner','reason','review_date')),'Missing owner, rationale or review date')
    import datetime
    datetime.date.fromisoformat(family['review_date'])
    selected={i['id'] for i in d.items}
    need(all(isinstance(r,dict) and r.get('id') in selected for r in raw['families']),'Unreviewed exclusion outside declared register population')


def duplicates(d,item,rule,f):
    need(item.get('relation') in ('duplicate','distinct'),'Prior editorial relation required')
    need(item.get('rendering')=='source-only-reviewed','Rendered-dependent comparison outside source-only profile')
    left,right=item['left'],item['right'];address(left);address(right);need(left!=right,'Distinct URL pair required')
    if rule.endswith('A01'):
        for url in (left,right):
            def compare_content(url=url):
                _,_,body,_=d.source(url)
                f.add(url,'pass','Complete bounded source available for supplied editorial comparison; SHA256='+hashlib.sha256(body if isinstance(body,bytes) else body.encode('utf-8')).hexdigest())
            f.check(url,compare_content)
    else:
        for url in (left,right):
            expected=right if item['relation']=='duplicate' else url
            f.check(url,lambda url=url,expected=expected:canonical(d,url,expected,f))


def spaces(d,item,rule,f):
    need(type(item.get('max_combinations')) is int and 1<=item['max_combinations']<=128,'Explicit finite population bound1–128 required')
    if rule.endswith('A01'):
        value,_=d.json(item['configuration'],'configuration','url-pattern-config-v1');actual=one(value.get('patterns'),item['id'])
        for key in ('max_combinations','navigation','indexing'):
            need(key in actual and key in item and (text(item[key]) if key!='max_combinations' else True),'Missing policy axis: '+key)
            f.compare(item['id']+':'+key,actual[key]==item[key],'Supplied configuration compared with prior finite policy')
    else:
        urls=item.get('urls');need(isinstance(urls,list) and 1<=len(urls)<=128 and len(set(urls))==len(urls),'Prior finite URL population required')
        for url in urls:address(url)
        rows,_=crawl(d,item['crawl']);seen={r['url'] for r in rows}
        f.compare(item['id']+':bound',len(seen)<=item['max_combinations'],'Observed distinct URL count versus declared finite bound')
        f.compare(item['id']+':population',seen<=set(urls),'Observed URLs must belong to prior finite selected population')
        need(text(item.get('trap_decision')),'Observed traps/cycles need an explicit decision and bound review')
        f.add(item['id'],'pass','Distinct observed URLs='+str(len(seen))+'; no claim of finite entire web space or real crawler volume')


def shapes(d,item,rule,f):
    if rule.endswith('A01'):
        def configuration():
            p,_=d.json('policy','configuration','url-shape-config-v1');actual=one(p.get('items'),item['id'])
            f.compare(item['id']+':configuration',actual==item,'Supplied configuration must match the prior shape/stability/variation policy')
        f.check('configuration',configuration)
        rows,_=crawl(d,item['after']);need(item.get('case') in ('lower-path','preserve') and type(item.get('allow_fragment')) is bool,'Case/fragment policy required')
        for row in rows:
            def lexical(row=row):
                url=row['url'];p=address(url)
                malformed=bool(re.search(r'[\s\x00-\x20\\]|%(?![0-9A-Fa-f]{2})',url))
                f.compare(row['key']+':encoding',not malformed,'No raw space/control/backslash or malformed percent escape in observed URL')
                if not malformed:
                    decoded=unquote_to_bytes(url).decode('utf-8')
                    need(not re.search(r'[\x00-\x1f\x7f]',decoded),'Escaped control character outside lexical profile')
                f.compare(row['key']+':fragment',item['allow_fragment'] or not p.fragment,'Fragment policy compared literally')
                if item['case']=='lower-path':f.compare(row['key']+':case',p.path==p.path.lower(),'Declared lower-path policy compared; server equivalence not assumed')
            f.check(row['key'],lexical)
    else:
        before,br=crawl(d,item['before']);after,ar=crawl(d,item['after'])
        need(d.dated(br)<d.dated(ar),'Two ordered observations required for bounded temporal comparison')
        need(item.get('stability')=='stable','Unsupported stability policy')
        decisions=item.get('decisions');need(isinstance(decisions,list) and len(decisions)<=128,'Explicit variation decisions required')
        b={r['key']:r['url'] for r in before};a={r['key']:r['url'] for r in after}
        need(set(a)==set(b),'Temporal population incomplete; key absence is not URL removal proof')
        for key in a:
            if a[key]==b[key]:f.add(key,'pass','Stable literal URL across the two supplied dates')
            else:
                found=[r for r in decisions if isinstance(r,dict) and r.get('key')==key and r.get('before')==b[key] and r.get('after')==a[key] and text(r.get('reason'))]
                f.compare(key,len(found)==1,'Changed URL needs one explicit reasoned before/after decision')


def variants(d,item,rule,f):
    need(item.get('rendering')=='source-only-reviewed','Rendered-dependent signals outside source-only profile')
    values=item.get('variants');need(isinstance(values,list) and 1<=len(values)<=32 and len(set(values))==len(values),'Bounded distinct variant population required')
    preferred=item['preferred'];address(preferred)
    for url in values:address(url)
    need(item.get('equivalence') in ('equivalent','distinct'),'Supplied editorial equivalence required')
    f.compare(item['id']+':equivalence',item['equivalence']=='equivalent','Declared distinct resources cannot be merged by this convergence plan')
    if rule.endswith('A01'):
        for url in values+[preferred]:
            def trajectory(url=url):
                final,status,_,_=d.response(url);doc=d.document(url)
                f.compare(url+':trajectory',final==preferred and status==200 and len(doc['http'])==(1 if url==preferred else 2),'Exactly one redirect per nonpreferred variant to direct200 preferred URL')
                canonical(d,url,preferred,f)
            f.check(url,trajectory)
    else:
        def sitemap():
            from conformance import sitemap_files
            raw,record=d.raw(item['sitemap'],'sitemap');parsed=sitemap_files.read_record(record['native'])
            need(parsed['format']==parsed['limits']=='pass' and parsed.get('xml_complete') is True and parsed['kind']=='urlset' and parsed['count']<=128,'Complete bounded native urlset required; indexes need separate declared leaf dossier')
            root=ET.fromstring(raw);ns='{'+sitemap_files.NS+'}'
            urls=[e.find(ns+'loc').text.strip() for e in root]
            f.compare(item['id']+':sitemap',preferred in urls and not(set(values)&set(urls)),'Preferred URL present and nonpreferred variants absent in complete selected native sitemap')
        f.check('sitemap',sitemap)
        sources=item.get('link_sources');need(isinstance(sources,list) and 1<=len(sources)<=32 and len(set(sources))==len(sources),'Prior nonempty link-source population required')
        for url in sources:
            def links(url=url):
                final,_,_,parsed=d.source(url)
                destinations=[urljoin(final,a) for a in parsed.anchors]
                f.compare(url+':links',not(set(values)&set(destinations)),'No nonpreferred variant in complete selected source links; unrelated links retained')
            f.check(url,links)


HANDLERS={'TS09':exclusions,'TS11':duplicates,'TS19':spaces,'TS20':shapes,'TS38':variants}


def assess(target,rule,*,diagnostics=None):
    f=Findings();control=rule.split('-')[0]
    try:
        need(rule in RULES,'Unsupported URL policy rule')
        from conformance.exclusion_observation import READER, assess as observed
        reader=target.get('intent',{}).get('evidence_checks',{}).get(control,{}).get('reader')
        enhanced=control=='TS09' and reader==READER
        d=Dossier(target,control,READER if enhanced else 'url-policy-v1')
        for item in d.items:
            subject=rule+':'+item['id']
            start=len(f.rows)
            f.check(subject,lambda item=item:HANDLERS[control](d,item,rule,f))
            if enhanced:f.check(subject+':representative',lambda item=item:observed(d,item,f))
            native_unknown=any(row['outcome']=='inconclusive' for row in f.rows[start:])
            def reviewed(subject=subject,native_unknown=native_unknown):
                result=d.review(subject)
                if not enhanced and result[0]=='fail' and native_unknown:
                    return 'inconclusive','Contradictory review cannot resolve missing native prerequisites'
                return result
            f.check(subject+':review',reviewed)
    except ERRORS as error:f.add(control,'inconclusive',str(error))
    note={'reader':target.get('intent',{}).get('evidence_checks',{}).get(control,{}).get('reader','url-policy-v1'),'version':VERSION,'rule':rule,'findings':f.rows,'limitations':LIMITATION}
    if hasattr(f,'info'):note['informative_observations']=f.info
    if diagnostics is not None:diagnostics.append(note)
    return f.result(),'Supplied URL policy / politique URL fournie: '+json.dumps(note,ensure_ascii=False,sort_keys=True)
