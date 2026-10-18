"""TS21/22/40 supplied indexing investigations and native locale methods."""
import base64
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from urllib.parse import urlsplit
import tsep
from conformance.evidence_dossier import Dossier,Findings,ERRORS,address,text
from conformance.http import need

VERSION='1'
COUNTS={'TS21':2,'TS22':2,'TS40':2}
RULES=tuple(c+'-A%02d'%n for c,count in COUNTS.items() for n in range(1,count+1))
ROOT=Path(__file__).resolve().parents[1]
NS='{http://www.sitemaps.org/schemas/sitemap/0.9}'
XHTML='{http://www.w3.org/1999/xhtml}'
LIMITATION='Supplied finite families/clusters only; no authenticated Google origin, current indexing, reviewer identity, causal proof, translation quality, audience targeting or worldwide/site-wide conformity.'


def raw_json(d,identity,kind):
    raw,record=d.raw(identity,kind)
    return tsep.parse_json(raw),record


def xml(d,identity):
    raw,record=d.raw(identity,'sitemap');value=raw.decode('utf-8')
    need(not re.search(r'<!DOCTYPE|<!ENTITY',value,re.I),'DTD/entities outside bounded XML profile')
    declaration=re.match(r'\s*<\?xml[^?]*encoding=[\"\x27]([^\"\x27]+)',value,re.I)
    need(not declaration or declaration[1].lower() in ('utf-8','utf8'),'UTF8 XML only')
    root=ET.fromstring(value)
    need(root.tag==NS+'urlset' and not root.attrib and 1<=len(root)<=128,'Complete bounded urlset required; indexes/empty sets unsupported')
    result={}
    for entry in root:
        need(entry.tag==NS+'url' and not entry.attrib,'Unexpected urlset entry')
        locs=[e for e in entry if e.tag==NS+'loc'];need(len(locs)==1 and not locs[0].attrib and not len(locs[0]) and text(locs[0].text),'One simple location required')
        loc=locs[0].text.strip();address(loc);need(loc not in result,'Duplicate native page location')
        rows=[]
        for child in entry:
            if child.tag==NS+'loc':continue
            if child.tag in (NS+'lastmod',NS+'changefreq',NS+'priority'):
                need(not child.attrib and not len(child),'Unsupported sitemap leaf structure');continue
            need(child.tag==XHTML+'link' and not len(child) and set(child.attrib)=={'rel','hreflang','href'} and child.attrib['rel'].lower()=='alternate','Unsupported native sitemap extension')
            rows.append({'code':child.attrib['hreflang'].lower(),'url':child.attrib['href']})
        need(len(rows)<=32,'Annotation bound32 exceeded')
        result[loc]=rows
    return result


def registry_code(code):
    p=ROOT/'conformance/data/locale-code-facts-v1.json';raw=p.read_bytes()
    need(hashlib.sha256(raw).hexdigest()==p.with_suffix('.sha256').read_text().strip(),'Locale registry fingerprint mismatch')
    registry=json.loads(raw)['codes'];code=code.lower()
    if code=='x-default':return 'pass','Reserved fallback token; no language or role conclusion'
    parts=code.split('-')
    if not re.fullmatch('[a-z]{2}',parts[0]):return 'fail','Language must use the selected ISO639-1 two-letter profile'
    def known(kind,token):
        table=registry[kind]
        if token not in table:return 'fail','Unregistered '+kind+' token in frozen registry: '+token
        if table[token]['deprecated']:return 'inconclusive','Deprecated '+kind+' token requires explicit review/migration'
        return 'pass','Registered '+kind+' token in frozen selected registry'
    first=known('language',parts[0])
    if first[0]!='pass':return first
    rest=parts[1:]
    if rest and len(rest[0])==4:
        result=known('script',rest.pop(0))
        if result[0]!='pass':return result
    if len(rest)>1:return 'inconclusive','Variants/extensions outside bounded language-script-region profile'
    if rest:
        region=rest[0]
        if not re.fullmatch('[a-z]{2}',region):return 'fail','Region outside the selected alpha2 profile'
        if region in ('eu','un','uk'):return 'fail','Reserved region has no regional effect under selected Google guidance'
        if region in ('aa','ac','cp','cq','dg','ea','ez','ic','ta','xk','zz'):return 'inconclusive','Reserved/private/exceptional region outside selected country-code subset'
        result=known('region',region)
        if result[0]!='pass':return result
    return 'pass','Language/script/region tokens checked against frozen registry subset; no language detection or engine-processing claim'


def channels(d,item,f):
    """Read each supplied method separately; never union partial methods into success."""
    from conformance import hreflang_native as native
    pages=item.get('pages');methods=item.get('methods');mappings=item.get('mappings')
    need(isinstance(pages,list) and 1<=len(pages)<=16 and len(set(pages))==len(pages),'Explicit1–16 page population required')
    need(isinstance(methods,list) and 1<=len(methods)<=3 and len(set(methods))==len(methods) and set(methods)<= {'html','http-link','sitemap'},'Explicit supported method inventory required')
    need(item.get('rendering')=='source-only-reviewed','Rendered hreflang outside supplied-source profile')
    need(isinstance(mappings,list) and 1<=len(mappings)<=32,'Expected1–32 mapping pairs required')
    expected={}
    for pair in mappings:
        need(isinstance(pair,list) and len(pair)==2 and text(pair[0],35),'Malformed mapping pair')
        code=pair[0].lower();need(code not in expected,'Ambiguous prior language code');address(pair[1]);expected[code]=pair[1]
    need(set(pages)<=set(expected.values()),'Every selected page needs a prior mapping')
    result=[]
    for url in pages:
        try:
            final,status,headers,body=d.response(url)
            need(final==url and status==200,'Direct200 annotation source required')
            raw=body if isinstance(body,bytes) else body.encode('utf-8')
            doc={'body_base64':base64.b64encode(raw).decode(),'body_sha256':hashlib.sha256(raw).hexdigest(),'content_type':headers.get('content-type',[None])[0],
                 'headers':[[k,v] for k,values in headers.items() for v in values]}
        except ERRORS as error:
            f.add(url,'inconclusive',str(error));continue
        def http():
            h=native.http_channel(doc)
            rows=[(r['code'],r['url']) for r in h['rows']]
            if 'http-link' in methods:
                complete=not h['unknowns']
                if not complete:f.add(url+':http-link','inconclusive','Unqualified HTTP alternate fields retained')
                result.append((url,'http-link',rows,complete))
            elif rows:f.add(url+':http-link','inconclusive','Published HTTP method omitted from prior method inventory')
        f.check(url+':http-link',http)
        def html():
            if not isinstance(doc['content_type'],str) or not doc['content_type'].lower().startswith('text/html'):
                need('html' not in methods,'Declared HTML annotation method on non-HTML source');return
            h=native.html_channel(doc,os.environ.get('TSEP_SOURCE_NODE'));hyp=h.get('hypotheses',{})
            need(set(hyp)=={'enabled','disabled'},'Both static HTML hypotheses required')
            pairs=[];complete=True
            for mode,v in hyp.items():
                qualified=not v.get('global_unqualified')
                pairs.append(set((r['code'],r['url']) for r in v['rows']) if qualified else set())
                complete=complete and qualified and not v.get('unknowns') and not v.get('misplaced')
            common=pairs[0]&pairs[1];complete=complete and pairs[0]==pairs[1]
            if 'html' in methods:
                if not complete:f.add(url+':html','inconclusive','Incomplete or divergent static annotation hypotheses')
                result.append((url,'html',sorted(common),bool(complete)))
            elif common:f.add(url+':html','inconclusive','Published HTML method omitted from prior method inventory')
        f.check(url+':html',html)
    if 'sitemap' in methods:
        names=item.get('sitemaps');need(isinstance(names,list) and 1<=len(names)<=16 and len(set(names))==len(names),'Explicit selected native sitemap population required')
        merged={};all_complete=True
        for name in names:
            try:
                for url,rows in xml(d,name).items():
                    need(url not in merged,'Ambiguous page across selected sitemaps')
                    merged[url]=rows
            except ERRORS as error:all_complete=False;f.add(name,'inconclusive',str(error))
        for url in pages:
            if url in merged:result.append((url,'sitemap',[(r['code'],r['url']) for r in merged[url]],all_complete))
            elif all_complete:result.append((url,'sitemap',[],True))
            else:f.add(url+':sitemap','inconclusive','Native sitemap coverage unresolved')
    if len(result)!=len(pages)*len(methods):f.add(item['id'],'inconclusive','One or more required method/page captures unavailable')
    return expected,result


def locale(d,item,rule,f):
    expected,observed=channels(d,item,f)
    if rule=='TS22-A01':
        seen=set()
        for url,method,rows,complete in observed:
            need(rows,'No native annotations to qualify')
            for code,destination in rows:
                f.add(url+':'+method+':'+code,*registry_code(code));address(destination)
                if code in expected:f.compare(code+':destination',destination==expected[code],'Native annotation attributed to declared selected destination')
                else:f.add(code,'inconclusive','Unplanned native mapping remains outside selected cluster')
                seen.add(destination)
        need(set(expected.values())<=seen,'Selected destination lacks native annotation evidence')
    elif rule=='TS22-A02':
        from conformance.evaluate import directive_values
        from conformance import robots
        from conformance.url_policy import canonical
        strategy=item.get('destinations');need(isinstance(strategy,list),'Prior destination indexing/robots strategy required')
        for url in sorted(set(expected.values())):
            def destination(url=url):
                matches=[s for s in strategy if isinstance(s,dict) and s.get('url')==url];need(len(matches)==1,'Missing/ambiguous destination strategy')
                plan=matches[0];f.compare(url+':intent',plan.get('indexing')=='allow','Selected hreflang destination intended for indexing')
                final,status,headers,body=d.response(url)
                f.compare(url+':HTTP',final==url and status==200,'Selected destination must be directly200')
                # HTTP noindex survives unavailable HTML or review.
                f.add(url+':HTTP directives',*directive_values(headers,[],{'crawler':d.target['intent']['crawler'],'directive_crawler':'googlebot','indexing':'allow'}))
                canonical(d,url,url,f)
                def html_directives():
                    _,_,_,parsed=d.source(url)
                    f.add(url+':source directives',*directive_values(headers,parsed.directives,{'crawler':d.target['intent']['crawler'],'directive_crawler':'googlebot','indexing':'allow'}))
                f.check(url+':HTML',html_directives)
                robots_url=plan['robots_url'];a,b=urlsplit(url),urlsplit(robots_url)
                need((a.scheme,a.netloc)==(b.scheme,b.netloc) and b.path=='/robots.txt' and not b.query and not b.fragment,'Robots origin attribution mismatch')
                end,code,rh,rb=d.response(robots_url);need(end==robots_url and code==200,'Complete direct200 robots representation required')
                need(plan.get('robots_profile') in robots.GOOGLE_PROFILES,'Explicit existing Google robots profile required')
                result=robots.body_policy(rb,url,'googlebot',plan['robots_profile'])
                need(result['decision']!='unknown',result.get('reason','Unknown robots policy'))
                f.compare(url+':robots',result['decision']=='allow','Selected Googlebot policy on supplied client representation; no actual Googlebot visit')
            f.check(url,destination)
    elif rule=='TS40-A01':
        for url,method,rows,complete in observed:
            values={}
            for code,destination in rows:
                address(destination)
                if code in values:f.compare(url+':'+code,values[code]==destination,'Repeated code must not identify conflicting destinations')
                values[code]=destination
                if code in expected:f.compare(url+':'+code,destination==expected[code],'Native code destination agrees with declared cluster')
                else:f.add(code,'inconclusive','Unplanned mapping outside selected group')
            if complete:f.compare(url+':'+method,set(expected)<=set(values),'Every complete used method supplies every selected mapping; no union of partial lists')
    elif rule=='TS40-A02':
        maps=[(url,method,set(rows),complete) for url,method,rows,complete in observed]
        need(maps,'No qualified method comparison')
        for index,(url,method,rows,complete) in enumerate(maps):
            for other_url,other_method,other,other_complete in maps[:index]:
                for code,destination in rows:
                    conflicts=[u for c,u in other if c==code and u!=destination]
                    if conflicts:f.add(url+':'+method+':'+code,'fail','Independent native methods disagree on a destination')
                if complete and other_complete:f.compare(url+':'+method,rows==other,'Complete selected method/page sets agree; one method is sufficient')
            if complete:f.add(url+':'+method,'pass','Complete method available for comparison; no requirement for multiple methods')


def investigation(d,item,rule,f):
    urls=item.get('urls');need(isinstance(urls,list) and 1<=len(urls)<=16 and len(set(urls))==len(urls),'Finite family URLs required')
    for url in urls:address(url)
    if rule=='TS21-A01':
        from diagnostics.search_console import check_request,engine_state
        records=item.get('inspections');need(isinstance(records,list) and len(records)==len(urls),'Exactly one native inspection per selected family URL required')
        seen=set()
        for entry in records:
            def inspection(entry=entry):
                url=entry['url'];need(url in urls and url not in seen,'Unplanned/duplicate inspection URL');seen.add(url)
                req,_=raw_json(d,entry['request'],'search-console');res,r=raw_json(d,entry['response'],'search-console')
                check_request(req)
                f.compare(url+':request',req['inspectionUrl']==url and req['siteUrl']==item['site_url'],'Native request attributed to selected URL/property')
                need(type(entry.get('http_status')) is int,'Supplied acquisition HTTP status required')
                state=engine_state(res,entry['http_status'],r['observed_at']);need(state['state']=='recorded','Native API result unavailable')
                field=state['fields']['coverageState'];need(field['state']=='present','Native coverage label unavailable')
                f.compare(url+':label',field['value']==item['reported_state'],'Supplied API label agrees with selected family state; not its cause or a live test')
            f.check(entry.get('url','inspection') if isinstance(entry,dict) else 'inspection',inspection)
        need(item.get('reported_state') in ('Discovered - currently not indexed','Crawled - currently not indexed'),'Only explicitly supported English nonindexed labels qualified')
        def sitemap():
            entries=xml(d,item['sitemap'])
            expected=item.get('sitemap_members');need(isinstance(expected,list) and set(expected)<=set(urls),'Explicit family sitemap-membership expectation required')
            f.compare(item['id']+':sitemap',set(entries)&set(urls)==set(expected),'Native selected sitemap membership reconciled with declared family')
        f.check('sitemap',sitemap)
        def logs():
            raw,_=d.raw(item['logs'],'logs');lines=raw.decode('utf-8').splitlines();need(1<=len(lines)<=129 and lines[0]=='timestamp\turl\tstatus\tuser_agent','Bounded supplied TSV log export profile required')
            for line in lines[1:]:
                fields=line.split('\t');need(len(fields)==4,'Unqualified log row');at,url,status,ua=fields
                need(tsep.timestamp(item['log_start'])<=tsep.timestamp(at)<=tsep.timestamp(item['log_end']),'Log event outside declared window');address(url)
                need(re.fullmatch('[1-5][0-9][0-9]',status) and text(ua),'Malformed status/client log field')
            f.add(item['id']+':logs','pass','Supplied '+str(len(lines)-1)+' log rows retained; empty bounded window proves no global absence and UA does not authenticate a crawler')
        f.check('logs',logs)
    else:
        record,_=d.json(item['diagnosis'],'content','family-diagnosis-v1')
        need(record.get('family_id')==item['id'],'Diagnosis family attribution mismatch')
        need(record.get('urls')==urls,'Diagnosis selected URL order/population differs')
        for key in ('diagnosis','hypothesis','prediction','falsification','measurement','decision','owner','due_date'):
            need(text(record.get(key)),'Missing diagnostic axis: '+key)
        datetime.date.fromisoformat(record['due_date'])
        f.compare(item['id']+':causality',record.get('causality')=='unproven','State label and correlation cannot be promoted to demonstrated cause')
        need(record.get('follow_up') in ('planned-not-observed','observed-separately'),'Follow-up state must distinguish plan from observed result')
        need(record['follow_up']=='planned-not-observed','Observed correction/follow-up requires its separately qualified method; not established by this diagnostic profile')
        f.add(item['id'],'pass','Diagnostic hypothesis and decision supplied; planned follow-up is not an observed correction or causal effect')


def assess(target,rule,*,diagnostics=None):
    f=Findings();cid=rule.split('-')[0]
    try:
        need(rule in RULES,'Unsupported indexing/locale rule');d=Dossier(target,cid,'indexing-locale-v1')
        for item in d.items:
            subject=rule+':'+item['id'];start=len(f.rows)
            f.check(subject,lambda item=item:(investigation if cid=='TS21' else locale)(d,item,rule,f))
            unknown=any(r['outcome']=='inconclusive' for r in f.rows[start:])
            def reviewed(subject=subject,unknown=unknown):
                value=d.review(subject)
                return ('inconclusive','Review cannot replace unqualified native prerequisites') if value[0]=='fail' and unknown else value
            f.check(subject+':review',reviewed)
    except ERRORS+(OSError,) as error:f.add(cid,'inconclusive',str(error))
    note={'reader':'indexing-locale-v1','version':VERSION,'rule':rule,'findings':f.rows,'limitations':LIMITATION}
    if diagnostics is not None:diagnostics.append(note)
    return f.result(),'Supplied indexing/locales / indexation et langues fournies: '+json.dumps(note,ensure_ascii=False,sort_keys=True)
