"""Bounded native render/HTML/transport evidence; no acquisition or live audit."""
import base64,hashlib,json,os,re,shutil,subprocess,tempfile
from pathlib import Path
from urllib.parse import urljoin,urlsplit
import tsep
from conformance.evidence_dossier import Dossier,Findings,ERRORS,address,digest,text
from conformance.http import need
VERSION='1'
COUNTS={'TS26':2,'TS27':2,'TS28':2,'TS29':2,'TS30':2,'TS37':3}
RULES=tuple(c+'-A%02d'%n for c,num in COUNTS.items() for n in range(1,num+1))
LIMITATION='Supplied bounded originals and unauthenticated reviews only. No actual browser execution, Googlebot, indexing, accessibility certification, universal trust store or site-wide security assessment.'
LIMIT=1024*1024
def origin(url):
    p=address(url);return p.scheme,p.hostname,p.port or (443 if p.scheme=='https' else 80)
def bytesof(v):return v if isinstance(v,bytes) else v.encode('utf-8')
def readjson(raw):return json.loads(raw.decode('utf-8'),object_pairs_hook=tsep.unique_object,parse_constant=lambda _:(_ for _ in ()).throw(ValueError('Nonfinite JSON')))
def bounded_list(v,minimum=1,maximum=32):
    need(isinstance(v,list) and minimum<=len(v)<=maximum,'Missing/bounded finite list');return v

def tree(raw):
    from experiments import source_content as sc
    raw=bytesof(raw);need(len(raw)<=LIMIT,'HTML exceeds1MiB')
    result=sc.tree_inventory(raw,content_types=['text/html; charset=utf-8'],node=os.environ.get('TSEP_SOURCE_NODE'))
    trees=[]
    for reading in result['readings'].values():
        need(reading['complete'] and not reading['parse_errors'],'Incomplete or parser-error HTML')
        nodes=reading['nodes'];paths,flags=sc.contexts(nodes);rows=[];runs={};run_flags={};characters=0
        for child in nodes:
            if child['kind']!='text' or {'script','style','template','foreign'}&set(flags[child['id']]):continue
            for ancestor in paths[child['id']]:
                if nodes[ancestor]['kind']!='element':continue
                characters+=len(child['data']);need(characters<=2*LIMIT,'Aggregate projected text exceeds2MiB')
                runs.setdefault(ancestor,[]).append(child['data']);run_flags.setdefault(ancestor,set()).update(flags[child['id']])
        for n in nodes:
            if n['kind']!='element':continue
            attrs=sc.attributes(n);need(not ('shadowrootmode' in attrs) and n['name'] not in ('iframe','frame','frameset'),'Uncollected frame/shadow surface')
            content=''.join(runs.get(n['id'],[]))
            rows.append({'tag':n['name'],'attrs':attrs,'text':' '.join(content.split()),'flags':flags[n['id']],'text_flags':sorted(run_flags.get(n['id'],set()))})
        trees.append(rows)
    need(len(trees)==2 and trees[0]==trees[1],'Static HTML hypotheses disagree')
    return trees[0]

def source(d,url):
    final,status,headers,body=d.response(url)
    from conformance.evaluate import utf8_media
    need(final==url and status==200 and utf8_media(headers,('text/html',)),'Direct200 UTF8 HTML prerequisite')
    return tree(body),headers,body

def select(rows,identity):
    need(text(identity,128),'Prior literal ID required');found=[r for r in rows if r['attrs'].get('id')==identity]
    need(len(found)<=1,'Duplicate selected ID');return found[0] if found else None

def content(rows,expect,f,subject):
    need(isinstance(expect,dict) and text(expect.get('text')),'Expected text required')
    row=select(rows,expect['id']);f.compare(subject,row is not None,'Selected literal ID must exist in the complete bounded serialization')
    if row is None:return
    need('body' in row['flags'] and not (set(row['flags'])|set(row['text_flags']))-{'body'},'Flagged element or descendant text requires a separately qualified visibility method')
    f.compare(subject+':text',row['text']==expect['text'],'Whitespace-collapsed exact text versus prior expectation')
    if expect.get('href') is not None:f.compare(subject+':href',row['attrs'].get('href')==expect['href'],'Declared literal navigation destination')

def state(d,identity,action=None,condition='normal'):
    s,record=d.json(identity,'render','browser-state-v1')
    need(s.get('complete') is True and type(s.get('frames')) is int and s['frames']==0 and type(s.get('shadow_roots')) is int and s['shadow_roots']==0,'Incomplete/uncollected supplied browser state')
    need(s.get('condition')==condition and (action is None or s.get('action')==action),'Wrong or unspecified observation scenario')
    need(isinstance(s.get('browser'),dict) and all(text(s['browser'].get(k)) for k in ('name','version')) and text(s.get('session')),'Supplied browser/session identity required')
    need(type(s.get('sequence')) is int and 0<=s['sequence']<=128,'Bounded sequence position required')
    bounded_list(s.get('steps'));need(all(text(v) for v in s['steps']),'Missing action observations')
    need(s.get('failures')==[],'Supplied acquisition failures prevent completeness')
    need(d.start<=tsep.timestamp(s.get('captured_at'))<=d.dated(record),'Invalid supplied observation chronology')
    docs=[v for v in d.data['documents'] if isinstance(v,dict) and v.get('id')==s.get('source_document')]
    need(len(docs)==1,'Missing/ambiguous source document identity');doc=docs[0];d.dated(doc)
    need(s.get('source_http_sha256')==digest(doc.get('http')),'Browser state source HTTP binding differs')
    from conformance.evaluate import trace
    final,status,headers,body=trace(doc['http'],doc['url'],d.target['intent']['crawler'])
    need(len(bytesof(body))<=LIMIT and text(s.get('html'),LIMIT),'Excessive/missing source or serialization')
    address(s.get('page_url'));return s,tree(s['html']),(final,status,headers,body)

def csp(headers,rows,page,resource,kind,f):
    need(address(page).scheme=='https','CSP source profile requires HTTPS page')
    need(kind in ('script','style','img','font','connect','media'),'Unsupported resource CSP kind')
    def meta():
        need(rows is not None,'Unqualified source cannot exclude meta CSP')
        need(not any(r['tag']=='meta' and r['attrs'].get('http-equiv','').lower()=='content-security-policy' for r in rows),'Meta CSP timing requires a separate qualified method')
    f.check('meta CSP',meta)
    policies=headers.get('content-security-policy',[])
    need(len(policies)<=8,'Excessive policies')
    for index,policy in enumerate(policies):
        def enforced(index=index,policy=policy):
            directives={}
            for segment in policy.split(';'):
                words=segment.split()
                if not words:continue
                name=words[0].lower();need(name not in directives,'Duplicate CSP directive outside profile');directives[name]=words[1:]
            need(set(directives)<=set(('default-src','script-src','script-src-elem','style-src','style-src-elem','img-src','font-src','connect-src','media-src','frame-src','worker-src','object-src','base-uri','form-action','frame-ancestors','report-uri','report-to')),'Unsupported CSP directive may alter request handling')
            primary=kind+'-src';keys=[primary,'default-src']
            if kind in ('script','style'):keys=[primary+'-elem']+keys
            tokens=next((directives[k] for k in keys if k in directives),None)
            if tokens is None:return
            need(tokens and ("'none'" not in tokens or tokens==["'none'"]),'Empty/ambiguous source expression')
            permitted=[]
            for token in tokens:
                if token=="'none'":permitted.append(False)
                elif token=="'self'":permitted.append(origin(resource)==origin(page))
                elif token=='*':permitted.append(urlsplit(resource).scheme in ('http','https'))
                elif token in ('http:','https:'):permitted.append(urlsplit(resource).scheme in (('http','https') if token=='http:' else ('https',)))
                else:
                    p=address(token);need(p.scheme=='https' and p.path in ('','/') and not p.query and not p.fragment and '*' not in token,'Only exact origins in bounded CSP profile')
                    permitted.append(origin(resource)==origin(token))
            f.compare('CSP:'+str(index)+':'+resource,any(permitted),'Intersection of supplied enforced HTTP CSP policies; no inline/nonced execution inferred')
        f.check("enforced CSP:"+str(index),enforced)
    if not policies:f.add('CSP','pass','No enforced HTTP CSP; source meta policy qualification is recorded separately')

def network(d,item):
    raw,record=d.raw(item['har'],'render');v=readjson(raw);log=v['log']
    need(log.get('version')=='1.2' and item.get('complete_capture') is True and text(item.get('capture_reason')),'Explicit bounded HAR1.2 export completeness required; not authenticity')
    for key in ('creator','browser'):need(isinstance(log.get(key),dict) and all(text(log[key].get(k)) for k in ('name','version')),'Missing HAR tool identity')
    pages=bounded_list(log.get('pages'));matches=[p for p in pages if p.get('id')==item['page_ref']];need(len(matches)==1 and len(pages)==1,'Single selected HAR page required')
    start=tsep.timestamp(matches[0]['startedDateTime']);need(d.start<=start<=d.dated(record),'HAR page chronology outside scope')
    entries=bounded_list(log.get('entries'),1,128)
    for e in entries:
        need(e.get('pageref')==item['page_ref'] and start<=tsep.timestamp(e['startedDateTime'])<=d.dated(record),'HAR entry page/time attribution differs')
        address(e['request']['url']);need(e['request'].get('method')=='GET','Only bounded GET HAR observations supported')
        status=e['response'].get('status');need(type(status) is int and (status==0 or 100<=status<=599),'Missing HAR status')
    nav=[e for e in entries if e['request']['url']==item['page']];need(len(nav)==1,'Missing/ambiguous HAR main document')
    final,status,headers,body=d.response(item['page']);b=nav[0]['response'].get('content',{});rawbody=b.get('text')
    need(isinstance(rawbody,str),'HAR document body omitted')
    rawbody=base64.b64decode(rawbody,validate=True) if b.get('encoding')=='base64' else rawbody.encode('utf-8')
    need(b.get('encoding') in (None,'base64') and nav[0]['response']['status']==status and final==item['page'] and rawbody==bytesof(body),'HAR native source body/status binding differs')
    return entries,record

def console(d,item):
    v,_=d.json(item['console'],'render','browser-console-v1');raw,_=d.raw(item['har'],'render')
    need(v.get('page_url')==item['page'] and v.get('har_sha256')==hashlib.sha256(raw).hexdigest() and v.get('complete') is True,'Unbound or incomplete console')
    events=bounded_list(v.get('events'),0,128)
    for e in events:
        need(e.get('level') in ('debug','log','info','warning','error') and text(e.get('text')),'Unqualified console event')
        need(d.start<=tsep.timestamp(e.get('timestamp'))<=d.end,'Console event outside window')
    return events

def resources(d,item,rule,f):
    page=item['page'];address(page);resources=bounded_list(item.get('resources'))
    need(len({v['url'] for v in resources})==len(resources),'Duplicate critical resource')
    if rule.endswith('A01'):
        for resource in resources:
            url=resource['url'];address(url)
            def http_resource():
                final,status,_,_=d.response(url);f.compare(url,final==url and status==200,'Selected critical resource direct200 profile')
            f.check(url,http_resource)
            def robots_resource():
                from conformance import robots
                ru=resource['robots_url'];p,q=address(url),address(ru)
                need(p[:2]==q[:2] and q.path=='/robots.txt' and not q.query and not q.fragment,'Wrong robots origin')
                need(resource.get('robots_profile') in robots.GOOGLE_PROFILES,'Explicit supported Google robots profile required')
                final,status,_,body=d.response(ru);need(final==ru and status==200,'Native direct200 robots required')
                value=robots.body_policy(body,url,'googlebot',resource['robots_profile'])['decision'];need(value in ('allow','disallow'),'Unqualified robots policy')
                f.compare(url+':robots',value=='allow','Native supplied robots decision for declared client')
            f.check(url+':robots',robots_resource)
            def policy_resource():
                final,status,headers,body=d.response(page);need(final==page and status==200,'Native direct200 page required for enforced policy')
                rows=None
                try:rows=source(d,page)[0]
                except ERRORS as error:f.add('CSP source','inconclusive',str(error))
                csp(headers,rows,page,url,resource['type'],f)
            f.check(url+':CSP',policy_resource)
    else:
        def traffic():
            entries,_=network(d,item)
            for resource in resources:
                matches=[e for e in entries if e['request']['url']==resource['url']];need(len(matches)==1,'Missing/ambiguous critical-resource HAR entry')
                e=matches[0];f.compare(resource['url'],200<=e['response']['status']<300 and not e.get('_error'),'Selected critical resource HAR response and supplied network error')
        f.check('traffic',traffic)
        def events():
            values=console(d,item)
            need(not any(e['level']=='error' for e in values),'Console error relevance requires a separately evidenced classification; empty success cannot be assumed')
            f.add('console','pass','Bounded console retained without error; no indexing inference')
        f.check('console',events)

def routes(d,item,rule,f):
    def server():
        final,status,_,_=d.response(item['page']);f.compare('route server',final==item['page'] and status==200,'Independent native direct route response')
    f.check('route server',server)
    states=bounded_list(item.get('states'),4,4);actions=['direct','refresh','history-back','history-forward'];session=None;previous=None
    for index,(identity,action) in enumerate(zip(states,actions)):
        def observation():
            nonlocal session,previous
            s,rows,http=state(d,identity,action)
            need(s['sequence']==index,'Route sequence differs from prior action order')
            if session is None:session=s['session']
            need(s['session']==session,'Route states are not one supplied session')
            when=tsep.timestamp(s['captured_at']);need(previous is None or previous<=when,'Route time order differs');previous=when
            f.compare(identity+':URL',s['page_url']==item['page'],'Shareable route URL retained for supplied action')
            f.compare(identity+':HTTP',http[0]==item['page'] and http[1]==200,'Bound native server source for selected route')
            if rule.endswith('A02'):
                for e in bounded_list(item.get('content')):content(rows,e,f,identity+':'+e['id'])
                values=[r['attrs'].get('href') for r in rows if r['tag']=='link' and 'canonical' in r['attrs'].get('rel','').lower().split() and 'head' in r['flags']]
                f.compare(identity+':canonical',values==[item['canonical']],'One explicit supplied DOM canonical for intended route')
        f.check(identity,observation)

def structure(rows,expected,f,label):
    titles=[r['text'] for r in rows if r['tag']=='title' and 'head' in r['flags']]
    langs=[r['attrs'].get('lang') for r in rows if r['tag']=='html']
    f.compare(label+':title',titles==[expected['title']],'Prior title versus complete parsed structure')
    f.compare(label+':language',langs==[expected['lang']],'Declared document language; linguistic adequacy requires review')
    mains=[r for r in rows if r['tag']=='main'];f.compare(label+':main',len(mains)==1 and mains[0]['attrs'].get('id')==expected['main_id'],'One declared principal landmark in this selected profile')
    headings=bounded_list(expected.get('headings'));observed=[r for r in rows if re.fullmatch('h[1-6]',r['tag'])]
    f.compare(label+':heading-inventory',[(r['attrs'].get('id'),r['tag'],r['text']) for r in observed]==[(e['id'],e['tag'],e['text']) for e in headings],'Declared heading structure, not a universal H1 count rule')
    for e in headings:content(rows,e,f,label+':heading:'+e['id'])
    for e in bounded_list(expected.get('links')):content(rows,e,f,label+':link:'+e['id'])

def semantics(d,item,rule,f):
    f.check('source structure',lambda:structure(source(d,item['page'])[0],item['structure'],f,'source'))
    def rendered():
        s,rows,http=state(d,item['state'],'direct')
        f.compare('render-url',s['page_url']==item['page'] and http[0]==item['page'] and http[1]==200,'Selected source and supplied DOM URL/status agree')
        structure(rows,item['structure'],f,'DOM')
    f.check('supplied DOM structure',rendered)
    # A02 additionally requires its distinct semantic judgment through assess().


def resilience(d,item,rule,f):
    source(d,item['page'])
    key,condition=('script_state','scripts-blocked') if rule.endswith('A01') else ('style_state','styles-degraded')
    s,rows,http=state(d,item[key],'direct',condition)
    f.compare('degraded-url',s['page_url']==item['page'] and http[0]==item['page'] and http[1]==200,'Degraded observation bound to selected page')
    essential=Findings()
    for e in bounded_list(item.get('essential')):essential.check(e['id'],lambda e=e:content(rows,e,essential,e['id']))
    if essential.result()=='pass':f.rows+=essential.rows;return
    fallback=item.get('fallback')
    if fallback is None:f.rows+=essential.rows;return
    need(isinstance(fallback,dict) and text(fallback.get('reason')),'Fallback must be prior and justified')
    alt=Findings()
    for e in bounded_list(fallback.get('content')):alt.check(e['id'],lambda e=e:content(rows,e,alt,e['id']))
    # A supplied fallback only substitutes when all native expectations are met;
    # bound human review must assess actual use and actions, not merely text.
    if alt.result()=='pass':f.add('fallback','pass','Prior fallback present in tested degraded state; distinct bound review required for operation')
    elif essential.result()=='fail' and alt.result()=='fail':f.rows+=essential.rows;f.rows+=alt.rows
    else:f.add('fallback','inconclusive','Neither main function nor tested fallback fully qualified')

FIELDS=('title','description','h1','og:title','og:description')
def metadata(rows):
    result={k:[] for k in FIELDS}
    for r in rows:
        if r['tag']=='title' and 'head' in r['flags']:result['title'].append(r['text'])
        elif r['tag']=='h1' and 'body' in r['flags']:result['h1'].append(r['text'])
        elif r['tag']=='meta' and 'head' in r['flags']:
            key=r['attrs'].get('name','').lower() if 'name' in r['attrs'] else r['attrs'].get('property','').lower()
            if key in FIELDS:result[key].append(r['attrs'].get('content',''))
    return result
def editorial(d,item,rule,f):
    pages=bounded_list(item.get('pages'));need(len({p['url'] for p in pages})==len(pages),'Duplicate corpus page');seen={k:{} for k in FIELDS}
    for page in pages:
        def inspect():
            rows,_,_=source(d,page['url']);actual=metadata(rows);expected=page['metadata'];need(set(expected)==set(FIELDS),'Explicit five-field policy required, null for intentionally absent optional fields')
            for key in FIELDS:
                want=expected[key];need(text(want) or (want is None and key not in ('title','h1')),'Unqualified metadata expectation')
                f.compare(page['url']+':'+key,actual[key]==([] if want is None else [want]),'Native metadata versus prior literal expectation; adequacy needs semantic review')
                if len(actual[key])==1 and text(actual[key][0]):seen[key].setdefault(actual[key][0],[]).append(page['url'])
            if rule.endswith('A02'):content(rows,page['content'],f,page['url']+':main-content')
        f.check(page.get('url','unknown'),inspect)
    if rule.endswith('A01'):
        decisions=bounded_list(item.get('duplicate_decisions'),0,128)
        for field,values in seen.items():
            for value,urls in values.items():
                if len(urls)<2:continue
                matches=[r for r in decisions if r.get('field')==field and r.get('urls')==urls and r.get('value')==value and text(r.get('reason')) and r.get('decision')=='intentional']
                f.compare(field+':duplicate',len(matches)==1,'Observed duplicate metadata needs one prior explicit corpus decision and its bound review')

def certificate(d,item,f):
    v,record=d.json(item['certificates'],'tls','tls-certificates-v1')
    host=item['host'];need(re.fullmatch(r'[A-Za-z0-9](?:[A-Za-z0-9.-]{0,251}[A-Za-z0-9])?',host) is not None,'Bounded DNS hostname required')
    need(v.get('host')==host and text(v.get('trust_scope')),'Certificate capture host/trust attribution differs')
    at=tsep.timestamp(v['captured_at']);need(d.start<=at<=d.dated(record),'Certificate observation time outside window')
    root,_=d.raw(v['trust_store'],'tls');leaf=v.get('leaf_pem');chain=bounded_list(v.get('intermediates_pem'),0,8)
    need(text(leaf,131072) and all(text(c,131072) for c in chain),'Missing/bounded PEM certificates')
    for value in [root.decode('ascii'),leaf]+chain:need('PRIVATE KEY' not in value and value.count('-----BEGIN CERTIFICATE-----') in range(1,17),'Only public bounded certificate PEM bundles')
    executable=shutil.which(os.environ.get('TSEP_OPENSSL','openssl'));need(executable is not None,'Optional OpenSSL3 unavailable')
    with tempfile.TemporaryDirectory(prefix='tsep-offline-cert-') as folder:
        work=Path(folder);(work/'roots.pem').write_bytes(root);(work/'leaf.pem').write_text(leaf);(work/'chain.pem').write_text('\n'.join(chain));(work/'empty.cnf').write_text('')
        env={k:v for k,v in os.environ.items() if not k.startswith(('OPENSSL_','SSL_CERT_'))};env['OPENSSL_CONF']=str(work/'empty.cnf')
        identity=subprocess.run([executable,'version'],capture_output=True,text=True,env=env,timeout=10)
        need(identity.returncode==0 and identity.stdout.startswith('OpenSSL 3.'),'Optional pinned OpenSSL major3 required')
        args=[executable,'verify','-no-CApath','-no-CAstore','-CAfile',str(work/'roots.pem'),'-purpose','sslserver','-verify_hostname',host,'-attime',str(int(at.timestamp())),'-verify_depth','8','-auth_level','2']
        if chain:args+=['-untrusted',str(work/'chain.pem')]
        args+=[str(work/'leaf.pem')]
        result=subprocess.run(args,capture_output=True,text=True,env=env,timeout=10);diagnostic=(result.stdout+result.stderr).replace(str(work),'<temporary>')[:8192]
        if result.returncode:
            codes=[int(n) for n in re.findall(r'error (\d+) at \d+ depth lookup',diagnostic)]
            need(result.returncode==2 and codes and set(codes)<={2,7,9,10,18,19,20,21,23,24,25,26,27,28,30,32,34,62,66,67,68},'Unqualified OpenSSL failure: '+diagnostic)
        f.compare('certificate',result.returncode==0,'Offline supplied trust-store/host/time verification; '+identity.stdout.strip()+'; '+diagnostic)

def transport_policy(d,item,f):
    page=item['page'];p=address(page);need(p.scheme=='https' and p.hostname==item['host'],'HTTPS page differs from declared host')
    variant=item['http_variant'];q=address(variant);need(q.scheme=='http' and q.hostname==p.hostname,'HTTP variant origin differs')
    final,status,_,_=d.response(variant);doc=d.document(variant)
    f.compare('HTTP redirect',len(doc['http'])>=2 and final==page and status==200 and all(urlsplit(h['url']).scheme=='https' for h in doc['http'][1:]),'HTTP redirects to intended HTTPS without later downgrade')
    final,status,headers,_=d.response(page);f.compare('HTTPS',final==page and status==200,'Native direct HTTPS200 profile')
    v,_=d.json(item['configuration'],'configuration','transport-policy-v1');policy=item['hsts']
    need(v.get('host')==item['host'],'HSTS configuration host differs')
    for name in ('scope','reason','owner'):need(text(policy.get(name)),'HSTS decision axis missing: '+name)
    need(type(policy.get('enabled')) is bool and type(policy.get('max_age')) is int and 0<=policy['max_age']<=2**31-1 and type(policy.get('include_subdomains')) is bool,'Invalid prior bounded HSTS decision')
    f.compare('configuration',v.get('hsts')==policy,'Supplied HSTS configuration agrees with prior decision')
    values=headers.get('strict-transport-security',[]);need(len(values)<=1,'Ambiguous duplicate HSTS headers')
    if not values:f.compare('HSTS',policy['enabled'] is False,'Missing HSTS compared with explicit enablement decision');return
    fields={}
    for piece in values[0].split(';'):
        parts=piece.strip().split('=',1);name=parts[0].lower()
        need(name in ('max-age','includesubdomains','preload') and name not in fields,'Unsupported/duplicate HSTS directive')
        fields[name]=parts[1].strip('"') if len(parts)==2 else None
    need('max-age' in fields and re.fullmatch('[0-9]+',fields['max-age'] or '') and all(fields[k] is None for k in fields if k!='max-age'),'Malformed HSTS profile')
    age=int(fields['max-age']);f.compare('HSTS age',age==policy['max_age'] and ((age>0)==policy['enabled']),'Native HSTS max-age and enabled/disabled decision')
    f.compare('HSTS scope',('includesubdomains' in fields)==policy['include_subdomains'],'Native HSTS subdomain scope; preload not required or authenticated')

def mixed(d,item,f):
    need(address(item['page']).scheme=='https','Selected HTTPS page required')
    def traffic():
        entries,_=network(d,item)
        for e in entries:
            url=e['request']['url'];f.compare(url,urlsplit(url).scheme=='https','Bounded strict transport profile disallows observed HTTP requests, even if browser might upgrade or block them')
    f.check('mixed traffic',traffic)
    def html():
        rows,_,_=source(d,item['page'])
        for r in rows:
            attrs=r['attrs']
            need('srcset' not in attrs and 'style' not in attrs and r['tag']!='style','CSS/srcset mixed-resource surfaces need separately qualified inventory')
            values=[]
            if r['tag'] in ('script','img','iframe','audio','video','source','track','embed','input') and 'src' in attrs:values.append(attrs['src'])
            if r['tag']=='link' and set(attrs.get('rel','').lower().split())&{'stylesheet','preload','modulepreload','icon'}:values.append(attrs.get('href',''))
            if r['tag']=='object':values.append(attrs.get('data',''))
            if 'poster' in attrs:values.append(attrs['poster'])
            for value in values:
                absolute=urljoin(item['page'],value);address(absolute);f.compare('embedded:'+value,urlsplit(absolute).scheme=='https','Native selected embedded URL uses HTTPS in strict profile')
    f.check('mixed source',html)
    f.check('console retained',lambda: ('pass','Bound console retained for mixed-content review') if console(d,item) is not None else None)

def assess(target,rule,*,diagnostics=None):
    f=Findings();cid=rule.split('-')[0]
    try:
        need(rule in RULES,'Unsupported render/transport rule');d=Dossier(target,cid,'render-transport-v1')
        for item in d.items:
            subject=rule+':'+item['id'];start=len(f.rows)
            def inspect():
                if cid=='TS37':return (certificate if rule.endswith('A01') else transport_policy if rule.endswith('A02') else mixed)(d,item,f)
                return {'TS26':resources,'TS27':routes,'TS28':semantics,'TS29':resilience,'TS30':editorial}[cid](d,item,rule,f)
            f.check(subject,inspect);unknown=any(v['outcome']=='inconclusive' for v in f.rows[start:])
            def review():
                value=d.review(subject)
                return ('inconclusive','Review cannot replace unqualified native prerequisites') if unknown and value[0]=='fail' else value
            f.check(subject+':review',review)
    except ERRORS+(OSError,subprocess.SubprocessError) as error:f.add(cid,'inconclusive',str(error))
    note={'reader':'render-transport-v1','version':VERSION,'rule':rule,'findings':f.rows,'limitations':LIMITATION}
    if diagnostics is not None:diagnostics.append(note)
    return f.result(),'Supplied render/transport / rendu et transport fournis: '+json.dumps(note,ensure_ascii=False,sort_keys=True)
