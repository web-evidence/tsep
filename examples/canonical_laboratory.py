#!/usr/bin/env python3
"""TS10 canonical laboratory: synthetic sites, real HTTP, supplied browser states.

Apache-2.0. No human content review, exemptions, engine selection or global C.
Transport-only TS07 wrappers reuse rendered v1 binding; they emit no TS07 result.
"""
import argparse
import copy
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
import secrets
import shutil
import sys
import tempfile
import threading
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import tsep
from adapters import captures, rendered
from collectors import ts01
from conformance import evaluate as evaluator
from conformance.http import encoded, raw_bytes
from diagnostics import campaign
from provenance.runtime import loaded_sources, runtime_identity

VERSION = '1'
FIXTURE = 'tests/fixtures/canonical-laboratory-cases.json'
FREEZE = 'tests/fixtures/canonical-laboratory-freeze.sha256'
ASSESSOR = 'Automated synthetic canonical laboratory; no human content review'
SELECTION = 'Twelve prefrozen synthetic families; declared members, sitemap roots and link sources only'
SCOPE = 'Synthetic controlled loopback laboratory; supplied browser observations, no authenticated engine or human content review'
ROLES = ('product', 'variant', 'catalog')


def fixture():
    tsep.require(tsep.digest(ROOT/FIXTURE) == (ROOT/FREEZE).read_text().strip(), 'Frozen canonical fixture mismatch')
    return tsep.read_json(ROOT/FIXTURE)


def sources():
    result = ts01.collection_sources(); result.update(rendered.sources())
    result.update(loaded_sources(ROOT, {'examples/canonical_laboratory.py':sys.modules[__name__], 'diagnostics/campaign.py':campaign}))
    for name in (FIXTURE, FREEZE): result[name] = tsep.digest(ROOT/name)
    return result


def semantic(value):
    if isinstance(value, dict): return {k:semantic(v) for k,v in value.items() if k != 'runtime'}
    if isinstance(value, list): return [semantic(v) for v in value]
    return value


def scenario(base, case, declared):
    urls = {'product':base+'/product', 'variant':base+'/product?color=blue', 'catalog':base+'/catalog', 'sitemap':base+'/sitemap.xml'}
    rendering = {'mode':'required', 'required_states':fixture()['required_states']}
    context = {'id':'synthetic-'+urlsplit(base).path.strip('/').replace('/','-'), 'network':'127.0.0.1 controlled laboratory',
               'bounds':'3 seconds / 32768 bytes / one redirect per request', 'tool':'TSEP canonical laboratory', 'tool_version':VERSION}
    intent = {'declared_at':declared, 'crawler':'googlebot', 'canonical':{
        'preferred_url':urls['product'], 'members':[{'url':urls[role], 'required_methods':['html'], 'rendering':copy.deepcopy(rendering)} for role in ROLES[:2]],
        'sitemaps':{'mode':'required','roots':[urls['sitemap']],'require_preferred':True,'exceptions':[]},
        'links':{'sources':[{'url':urls['catalog'],'rendering':copy.deepcopy(rendering)}],'exceptions':[]}}}
    collected = list(urls.values())
    if case['id'] in ('missing-child','contradiction-with-gap'): collected.append(base+'/maps/one.xml')
    settings = {'urls':collected,'origins':[base.split(urlsplit(base).path)[0]],'agent':'googlebot','accept_encoding':'identity',
                'timeout':3,'max_bytes':32768,'max_redirects':1,'allow_loopback':True,'network':context['network'],
                'access':'synthetic','selection_method':SELECTION}
    return {'base':base,'urls':urls,'context':context,'intent':intent,'settings':settings,
            'uncollected_resources':[base+'/maps/two.xml'] if case['id'] in ('missing-child','contradiction-with-gap') else [],
            'browser_roles':[r for r in ROLES if not (case['id']=='preferred-404' and r=='product')]}


def page(case, role, record):
    preferred, variant = record['urls']['product'], record['urls']['variant']
    canonical = preferred if role != 'catalog' else None
    if case['id']=='relative-canonical' and role=='variant': canonical = urlsplit(preferred).path
    anchor = variant if case['id']=='link-variant' else preferred
    link = '<link rel="canonical" href="'+escape(canonical, quote=True)+'">' if canonical else ''
    mutation = "document.querySelector('link[rel=canonical]').href="+json.dumps(variant)+";" if case['id']=='js-canonical' and role=='variant' else ''
    return '''<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>TSEP — '''+escape(case['label'])+'''</title>'''+link+'''
<style>body{font:18px/1.6 system-ui;max-width:1000px;margin:40px auto;padding:25px;background:#102032;color:#edf3f8}h1{font-size:38px;line-height:1.15}.small{font-size:13px;overflow-wrap:anywhere;color:#b8c7d5}span{color:#b8ed76}a{color:#b8ed76}</style></head><body>
<p>LABORATOIRE SYNTHÉTIQUE · TSEP TS10</p><h1>'''+escape(case['label'])+'''</h1><p>Document : '''+role+'''</p>
<p>Produit de démonstration : même fiche, variante couleur bleue. Aucun jugement humain de similarité enregistré.</p>
<p>Canonique dans cet état : <span id="canonical-value">pending</span></p>
<p>État : <span id="state">waiting</span> · JavaScript : <span id="js">pending</span></p>
<p>Erreurs signalées par la page : <span id="errors">[]</span></p>
'''+('<p><a href="'+escape(anchor,quote=True)+'">Voir le produit</a></p>' if role=='catalog' else '')+'''
<p class="small">Document : <span id="document-url">pending</span> · Rôle : <span id="document-role">'''+role+'''</span></p>
<p class="small">Contexte : <span id="context">'''+escape(record['context']['id'])+'''</span></p>
<p class="small">Agent déclaré : <span id="agent">pending</span></p><p class="small">Observation du laboratoire : <span id="event-time">pending</span></p>
<p>Ce laboratoire ne prouve aucun choix de canonique par un moteur.</p>
<script>const errors=[];function error(value){errors.push(String(value));document.getElementById('errors').textContent=JSON.stringify(errors);}
window.addEventListener('error',e=>error(e.message));window.addEventListener('unhandledrejection',e=>error(e.reason));
document.getElementById('agent').textContent=navigator.userAgent;document.getElementById('document-url').textContent=location.href;
'''+mutation+'''
const canonical=document.querySelector('link[rel=canonical]');document.getElementById('canonical-value').textContent=canonical?canonical.getAttribute('href'):'aucune';
document.getElementById('js').textContent='executed';document.getElementById('state').textContent='loaded';document.getElementById('event-time').textContent=new Date().toISOString();
</script></body></html>'''


def wire(body, kind='text/html', status=200, headers=None):
    raw = body.encode('utf-8')
    fields = [('Content-Type',kind+'; charset=utf-8'),('Content-Length',str(len(raw))),('Cache-Control','no-store'),
              ('Content-Security-Policy',"default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'"),('Connection','close')]+list(headers or [])
    return ('HTTP/1.1 '+str(status)+' Laboratory\r\n'+''.join(k+': '+v+'\r\n' for k,v in fields)+'\r\n').encode('ascii')+raw


def xml(locations, index=False):
    tag, item = ('sitemapindex','sitemap') if index else ('urlset','url')
    return '<'+tag+' xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<'+item+'><loc>'+escape(u)+'</loc></'+item+'>' for u in locations)+'</'+tag+'>'


def responses(case, record):
    urls, base = record['urls'], record['base']
    result = {urls[r]:wire(page(case,r,record)) for r in ROLES}
    if case['id']=='http-conflict': result[urls['variant']] = wire(page(case,'variant',record),headers=[('Link','<'+urls['variant']+'>; rel="canonical"')])
    if case['id']=='preferred-redirect':
        result[urls['product']] = wire('',status=302,headers=[('Location',base+'/landing')])
        result[base+'/landing'] = wire(page(case,'product',record))
    if case['id']=='preferred-404': result[urls['product']] = wire('Synthetic missing preferred destination','text/plain',404)
    entries = [] if case['id']=='sitemap-omission' else [urls['variant'] if case['id']=='sitemap-variant' else urls['product']]
    result[urls['sitemap']] = wire(xml(entries),'application/xml')
    if record['uncollected_resources']:
        result[urls['sitemap']] = wire(xml([base+'/maps/one.xml',base+'/maps/two.xml'],True),'application/xml')
        result[base+'/maps/one.xml'] = wire(xml([urls['variant']] if case['id']=='contradiction-with-gap' else []),'application/xml')
        result[base+'/maps/two.xml'] = wire(xml([urls['product']]),'application/xml')
    return result


class Handler(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'
    def log_message(self, *args): pass
    def do_GET(self):
        url = self.server.origin+self.path
        raw = self.server.responses.get(url,wire('Outside laboratory scope','text/plain',404))
        row = {'url':url,'observed_at':ts01.now(),'complete':False,'request_agent':self.headers.get('User-Agent'),
               'peer':self.client_address[0],'response':encoded(raw)}
        try:
            self.wfile.write(raw);self.wfile.flush();row['complete']=True
        finally:
            with self.server.log_lock, (self.server.folder/'requests.jsonl').open('a',encoding='utf-8') as handle:
                handle.write(json.dumps(row,ensure_ascii=False)+'\n')
        self.close_connection=True


def stop(server, thread):
    if thread.is_alive(): server.shutdown()
    server.server_close();thread.join()


def wrapper(doc, record):
    target = copy.deepcopy(doc)
    target['context'] = dict(record['context'], canonical_plan_sha256=evaluator.binding_digest(record['intent']),
                             transport_only='Binding carrier; indexing/link intent not declared; DO NOT EVALUATE as TS07')
    plans = [m['rendering'] for m in record['intent']['canonical']['members'] if m['url']==doc['url']]
    plans += [m['rendering'] for m in record['intent']['canonical']['links']['sources'] if m['url']==doc['url']]
    tsep.require(len(plans)==1, 'Document has no unique TS10 rendering plan')
    target['intent'] = {'declared_at':record['intent']['declared_at'],'crawler':'googlebot','public_canonical':False,
                        'indexing':'transport-not-declared','following':'transport-not-declared','access_basis':'transport-not-assessed',
                        'rendering':copy.deepcopy(plans[0])}
    return {'input_version':'2','rules':['TS07-A01','TS07-A02','TS07-A03'],'targets':[target]}


def check_phase(phase, record, before, previous):
    tsep.require(phase['settings']==record['settings'], 'Registered settings mismatch')
    ts01.same_collector(phase)
    tsep.require(all(phase['source_files'][k]==before[k] for k in phase['source_files']), 'Collector source mismatch')
    stamp=tsep.timestamp
    tsep.require(stamp(previous)<=stamp(phase['started_at'])<=stamp(phase['finished_at']), 'Invalid phase chronology')
    tsep.require([t['url'] for t in phase['targets']]==record['settings']['urls'],'Captured population mismatch')
    prior=phase['started_at']
    for target in phase['targets']:
        tsep.require(stamp(prior)<=stamp(target['started_at'])<=stamp(target['observed_at'])<=stamp(phase['finished_at']), 'Invalid target chronology')
        for hop in target['http']:
            tsep.require(hop.get('peer_address')=='127.0.0.1' and hop.get('complete') is True, 'Incomplete/non-loopback HTTP capture')
            tsep.require(stamp(target['started_at'])<=stamp(hop['started_at'])<=stamp(hop['finished_at'])<=stamp(target['observed_at']), 'Invalid hop chronology')
        prior=target['observed_at']


def source_inventory(root, registration):
    names=['registration.json','browser-tasks.json','SHA256SUMS']
    for case in registration['plan']['cases']:
        key=case['id'];record=registration['scenarios'][key]
        folder=root/key/'capture';names += [key+'/capture/'+n for n in list(ts01.verify(folder))+['SHA256SUMS']]
        names += [key+'/bindings/'+role+'/'+n for role in record['browser_roles'] for n in ('source.json','receipt.json')]
    return names


def start(output):
    plan,before=fixture(),sources();folder=ts01.new_directory(output)
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler);server.daemon_threads=True
    server.folder=folder;server.origin='http://127.0.0.1:'+str(server.server_port);server.log_lock=threading.Lock()
    declared=ts01.now();token=secrets.token_hex(8)
    registration={'kind':'canonical-laboratory','version':VERSION,'synthetic':True,'registered_at':declared,'origin':server.origin,
                  'token':token,'plan':plan,'source_files':before,'scenarios':{c['id']:scenario(server.origin+'/'+token+'/'+c['id'],c,declared) for c in plan['cases']}}
    ts01.save(folder/'registration.json',registration);(folder/'requests.jsonl').touch()
    server.responses={url:raw for c in plan['cases'] for url,raw in responses(c,registration['scenarios'][c['id']]).items()}
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    try:
        tasks=[];previous=declared
        for case in plan['cases']:
            tsep.require(sources()==before,'Laboratory sources changed before capture')
            key=case['id'];record=registration['scenarios'][key];casefolder=folder/key;casefolder.mkdir()
            ts01.capture(record['settings'],casefolder/'capture');phase,_=campaign.phase(casefolder/'capture')
            check_phase(phase,record,before,previous);previous=phase['finished_at']
            for role in record['browser_roles']:
                doc=next(d for d in phase['targets'] if d['url']==record['urls'][role])
                bind=casefolder/'bindings'/role;bind.mkdir(parents=True)
                ts01.save(bind/'source.json',wrapper(doc,record));receipt=rendered.prepare(bind/'source.json',bind/'receipt.json')
                tasks.append({'id':key+'/'+role,'case':key,'role':role,'url':receipt['url'],'context_id':receipt['context_id']})
        ts01.save(folder/'browser-tasks.json',tasks)
        names=['registration.json','browser-tasks.json']+[c['id']+'/capture/SHA256SUMS' for c in plan['cases']]
        names += [t['id'].replace('/','/bindings/',1)+'/'+n for t in tasks for n in ('source.json','receipt.json')]
        ts01.manifest(folder,names)
        return server,thread,registration,tasks
    except BaseException:
        stop(server,thread);raise


def load_source(root):
    registration=tsep.read_json(root/'registration.json');before=sources();plan=fixture()
    tsep.require(registration.get('kind')=='canonical-laboratory' and registration.get('version')==VERSION
                 and registration.get('synthetic') is True and registration['source_files']==before and registration['plan']==plan,'Laboratory source/plan mismatch')
    origin=registration['origin'];token=registration['token'];declared=registration['registered_at']
    tsep.require(ts01.origin(origin)[:2]==('http','127.0.0.1') and re.fullmatch('[a-f0-9]{16}',token),'Invalid loopback registration')
    expected={c['id']:scenario(origin+'/'+token+'/'+c['id'],c,declared) for c in plan['cases']}
    tsep.require(registration['scenarios']==expected,'Registered family/intent mismatch')
    tasks=[];phases={};previous=declared
    for case in plan['cases']:
        key=case['id'];record=expected[key];phase,_=campaign.phase(root/key/'capture')
        check_phase(phase,record,before,previous);previous=phase['finished_at'];phases[key]=phase
        served=responses(case,record)
        for target in phase['targets']:
            for hop in target['http']:
                tsep.require(raw_bytes(hop['response'])==served[hop['url']],'Source response differs from frozen scenario')
        for role in record['browser_roles']:
            bind=root/key/'bindings'/role
            doc=next(d for d in phase['targets'] if d['url']==record['urls'][role])
            raw,data=rendered.read(bind/'source.json');_,receipt=rendered.read(bind/'receipt.json')
            tsep.require(data==wrapper(doc,record) and receipt==rendered.registration(raw,receipt['prepared_at']),'Document/receipt binding mismatch')
            tasks.append({'id':key+'/'+role,'case':key,'role':role,'url':receipt['url'],'context_id':receipt['context_id']})
    tsep.require(tsep.read_json(root/'browser-tasks.json')==tasks,'Browser task inventory mismatch')
    manifest=set(ts01.verify(root));expected_names={'registration.json','browser-tasks.json'}
    expected_names.update(c['id']+'/capture/SHA256SUMS' for c in plan['cases'])
    expected_names.update(t['id'].replace('/','/bindings/',1)+'/'+n for t in tasks for n in ('source.json','receipt.json'))
    tsep.require(manifest==expected_names,'Incomplete source manifest')
    return registration,phases,tasks


class DocumentWitness(rendered.Witness):
    IDS = rendered.Witness.IDS | {'document-url', 'document-role'}


def assemble(root, observations, assessment_end, capture_kind):
    registration,phases,tasks=load_source(root)
    tsep.require(capture_kind in ('observed-browser','authored-fixture'),'Explicit browser evidence origin required')
    tsep.require(isinstance(observations,dict) and set(observations)=={t['id'] for t in tasks},'Browser observation population mismatch')
    journal=rendered.log_bytes(root/'requests.jsonl');lines=journal.splitlines(keepends=True)
    logs=[tsep.parse_json(line) for line in lines];stamp=tsep.timestamp
    tsep.require(stamp(assessment_end)<=stamp(ts01.now()),'Assessment date in future')
    served={url:raw for c in registration['plan']['cases'] for url,raw in responses(c,registration['scenarios'][c['id']]).items()}
    for row in logs:
        tsep.require(row.get('peer')=='127.0.0.1' and row.get('complete') is True and row['url'] in served
                     and raw_bytes(row['response'])==served[row['url']],'Unexpected/incomplete server request')
    expected_http=[hop for case in registration['plan']['cases'] for target in phases[case['id']]['targets'] for hop in target['http']]
    collected=[row for row in logs if row['request_agent']=='googlebot']
    tsep.require([r['url'] for r in collected]==[h['url'] for h in expected_http],'Source request scope mismatch')
    for row,hop in zip(collected,expected_http):
        tsep.require(stamp(hop['started_at'])<=stamp(row['observed_at'])<=stamp(hop['finished_at']),'Source request chronology mismatch')
    rendered_docs={};bindings={};used=[]
    for task in tasks:
        key=task['id'];obs=observations[key];bind=root/task['case']/'bindings'/task['role']
        source_raw,_=rendered.read(bind/'source.json');receipt_raw,receipt=rendered.read(bind/'receipt.json')
        agent=obs['agent'];tsep.require(isinstance(agent,str) and 'googlebot' not in agent.lower(),'Browser cannot claim a Googlebot user agent')
        matching=[(i,row) for i,row in enumerate(logs) if row['url']==task['url'] and row['request_agent']==agent
                  and stamp(receipt['prepared_at'])<=stamp(row['observed_at'])<=stamp(obs['observed_at'])]
        tsep.require(len(matching)==1,'Expected exactly one recorded browser navigation per document')
        i,nav=matching[0];used.append(i)
        tsep.require(stamp(obs['observed_at'])<=stamp(assessment_end),'Browser capture postdates assessment')
        browser=obs['browser']
        tsep.require(browser.get('user_agent')==agent,'Browser metadata/agent mismatch')
        planned=[s for s in receipt['plan']['required_states'] if s['id']==obs['state']]
        tsep.require(len(planned)==1, 'Observation has no unique planned state')
        state={'id':obs['state'],'url':obs['url'],'context_id':obs['context'],'source_http_sha256':receipt['source_http_sha256'],
               'observed_at':obs['observed_at'],'complete':obs['readyState']=='complete','javascript_enabled':obs['js']=='executed',
               'interactions':[],'wait':planned[0]['wait'],'errors':obs['errors'],'dom':obs['dom']}
        envelope={'capture_version':'1','receipt_sha256':rendered.fingerprint(receipt_raw),'server_log_sha256':rendered.fingerprint(journal),
                  'method':{'name':'Supplied laboratory DOM serialization','version':VERSION,
                            'description':capture_kind+'; read-only outerHTML after visible loaded marker; page-reported errors; developer logs supplementary; not execution authentication'},
                  'browser':browser,'states':[{'state':state,'navigation':nav,'log_index':i,'log_line_sha256':rendered.fingerprint(lines[i]),
                                               'supplementary_dev_logs':obs['devLogs']}]}
        associated,association=rendered.derive(source_raw,receipt_raw,envelope,journal)
        try:
            witness=DocumentWitness(obs['dom']).values
            tsep.require(witness.get('document-url')==receipt['url'] and witness.get('document-role')==task['role'], 'DOM document URL/role witness mismatch')
        except (ValueError,KeyError,TypeError) as error:
            associated['targets'][0]['render']['states'][0].pop('source_http_sha256',None)
            association['states'][0]['attributed']=False;association['states'][0]['reasons'].append(str(error))
        rendered_docs[key]=associated['targets'][0]['render']
        bindings[key]={'envelope':envelope,'association':association,'canonical_plan_sha256':evaluator.binding_digest(registration['scenarios'][task['case']]['intent'])}
    tsep.require(len(set(used))==len(tasks) and len(logs)==len(expected_http)+len(tasks),'Extra or reused browser request')
    inputs={}
    for case in registration['plan']['cases']:
        key=case['id'];record=registration['scenarios'][key];phase=phases[key]
        tsep.require(stamp(phase['finished_at'])<=stamp(assessment_end),'Assessment predates source')
        docs=[];maps=[];crawl=[]
        for original in phase['targets']:
            doc=copy.deepcopy(original);doc['context_id']=record['context']['id']
            roles=[r for r in ROLES if record['urls'][r]==doc['url']]
            if roles:
                role=roles[0]
                if key+'/'+role in rendered_docs:doc['render']=rendered_docs[key+'/'+role]
                (crawl if role=='catalog' else docs).append(doc)
            else:maps.append(doc)
        target={'url':record['urls']['product'],'observed_at':assessment_end,'context':record['context'],'intent':record['intent'],
                'documents':docs,'sitemaps':{'documents':maps},'crawl':{'documents':crawl}}
        inputs[key]={'input_version':'2','rules':registration['plan']['rules'],'targets':[target]}
    return registration,inputs,bindings,{'source_requests':len(expected_http),'browser_requests':len(tasks),'total_requests':len(logs)}


def summarize(registration, inputs, counts, capture_kind, assessment_end):
    rows=[]
    for case in registration['plan']['cases']:
        atoms=evaluator.evaluate(inputs[case['id']]);outcomes=[a['outcome'] for a in atoms]
        status='NC' if 'fail' in outcomes else 'NT'
        rows.append({'id':case['id'],'label':case['label'],'actual':outcomes,'expected':case['expected'],'status':status,
                     'matches_expectations':outcomes==case['expected'] and status==case['control'],'atomic_results':atoms})
    return {'kind':'canonical-laboratory-results','version':VERSION,'protocol':tsep.read_json(ROOT/'spec/protocol.json')['version'],
            'scope':SCOPE,'synthetic_site':True,'browser_evidence_origin':capture_kind,'assessment_end':assessment_end,
            'human_review_performed':False,'counts':counts,'cases':rows,'all_expectations_matched':all(r['matches_expectations'] for r in rows),
            'source_files':registration['source_files'],'runtime':runtime_identity()}


def reading_note(result):
    lines=['TSEP — laboratoire canonique TS10','Site synthétique ; captures HTTP réelles ; origine des DOM : '+result['browser_evidence_origin'],
           'A01 déclarations canonical / A02 destination et contenu / A03 sitemap / A04 liens internes.',
           'Aucune revue humaine de contenu. Une correction atomique ne suffit pas à conclure C.',
           'Canonical relative : échec du critère URL absolue TSEP, pas une conclusion générale sur les moteurs.',
           'Une branche non collectée n’est pas un fichier absent. Un défaut observé subsiste malgré la lacune.','',
           'Scénario | A01 / A02 / A03 / A04 | TS10']
    for row in result['cases']:
        lines += [row['label']+' | '+' / '.join(row['actual'])+' | '+row['status']]
        lines += ['  '+a['rule_id']+' : '+a['reason'] for a in row['atomic_results']]
    lines += ['', 'État rendu obtenu en naviguant vers l’URL finale de la trace source ; la redirection est mesurée par le client HTTP.',
              'Toute requête imprévue/recharge invalide la campagne ; conserver l’échec, puis relancer une nouvelle campagne.',
              'Les reçus de transport TS07 servent exclusivement à associer les DOM ; aucun rapport TS07 produit.',
              'Rejeu hors réseau : python3 examples/canonical_laboratory.py replay DOSSIER --output NOUVEAU.json',
              'Pas de choix canonical moteur, indexation, classement, exhaustivité du site ou validation indépendante.',
              'Agent et dates déclarés ; empreintes locales non signées ; erreurs signalées par les pages seulement.','']
    return '\n'.join(lines)


def finish(source, observations_path, output, capture_kind):
    source,output=Path(source),Path(output);before=sources()
    observation_raw,observations=rendered.read(observations_path);end=ts01.now()
    registration,inputs,bindings,counts=assemble(source,observations,end,capture_kind)
    result=summarize(registration,inputs,counts,capture_kind,end)
    tsep.require(not output.exists() and not output.is_symlink() and output.parent.is_dir(),'Choose a NEW output directory')
    with tempfile.TemporaryDirectory(prefix='.tsep-canonical-',dir=output.parent) as temporary:
        stage=Path(temporary);names=[]
        def copy_file(path,relative):
            dest=stage/relative;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,dest);names.append(relative)
        for name in source_inventory(source,registration)+['requests.jsonl']:copy_file(source/name,'source/'+name)
        (stage/'observations.json').write_bytes(observation_raw);names.append('observations.json')
        for key,data in inputs.items():
            folder=stage/key;folder.mkdir();ts01.save(folder/'input.json',data);names.append(key+'/input.json')
            for binding_key,value in bindings.items():
                if binding_key.startswith(key+'/'):
                    relative=binding_key.split('/')[1]+'-binding.json';ts01.save(folder/relative,value);names.append(key+'/'+relative)
            captures.build(folder/'input.json',folder/'bundle',assessor=ASSESSOR,label='SYNTHETIC TS10 / '+key,
                           selection_method=SELECTION,access='synthetic',mode='automatic',selected=['TS10'])
            names += [key+'/bundle/'+n for n in list(ts01.verify(folder/'bundle'))+['SHA256SUMS']]
        ts01.save(stage/'results.json',result);names.append('results.json')
        (stage/'LIRE-MOI.txt').write_text(reading_note(result),encoding='utf-8');names.append('LIRE-MOI.txt')
        tsep.require(sources()==before,'Sources changed during import');ts01.manifest(stage,names)
        replay(stage)
        output.mkdir(mode=0o700)
        try:
            for child in stage.iterdir():shutil.move(str(child),str(output/child.name))
        except BaseException:
            shutil.rmtree(output);raise
    return result


def replay(root):
    root=Path(root);before=sources();manifest=ts01.verify(root)
    retained=tsep.read_json(root/'results.json');observations=tsep.read_json(root/'observations.json')
    registration,inputs,bindings,counts=assemble(root/'source',observations,retained['assessment_end'],retained['browser_evidence_origin'])
    expected={'observations.json','results.json','LIRE-MOI.txt','source/requests.jsonl'}
    expected.update('source/'+name for name in source_inventory(root/'source',registration))
    for key,value in bindings.items():
        name=key+'-binding.json'
        tsep.require(tsep.read_json(root/name)==value,'Replayed transport association differs');expected.add(name)
    for key,data in inputs.items():
        folder=root/key;bundle=folder/'bundle';expected.add(key+'/input.json')
        tsep.require(tsep.read_json(folder/'input.json')==data and tsep.read_json(bundle/'input.json')==data,'Family/capture input mismatch')
        bundle_names=ts01.verify(bundle)
        known={'input.json','import.json','assessment.json','report.json','gate.json','earl.jsonld'}
        known.update('evidence/target-1-'+kind+'.json' for kind in captures.pieces(data['targets'][0]))
        tsep.require(set(bundle_names)==known, 'Unexpected bundle file; only TS10 report artifacts allowed')
        expected.update(key+'/bundle/'+n for n in list(bundle_names)+['SHA256SUMS'])
        atoms=evaluator.evaluate(data);report=tsep.read_json(bundle/'report.json');imported=tsep.read_json(bundle/'import.json')
        tsep.require(imported['source_files']==captures.source_files() and imported['access']=='synthetic'
                     and imported['input_sha256']==tsep.digest(folder/'input.json'),'Bundle provenance mismatch')
        tsep.require(tsep.read_json(bundle/'assessment.json')==atoms,'Replayed atomic results differ')
        tsep.require(report['scope']=={'label':'SYNTHETIC TS10 / '+key,'targets':[data['targets'][0]['url']],
                     'selection_method':SELECTION,'exclusions':[]} and report['assessor']=={'name':ASSESSOR,'mode':'automatic',
                     'tool':{'name':captures.NAME,'version':captures.VERSION}} and all(a['access']=='synthetic' for a in report['artifacts']), 'Synthetic report identity mismatch')
        tsep.require([{k:v for k,v in a.items() if k!='evidence_ids'} for a in report['results'][0]['atomic_results']]==atoms,'Report/atomic binding mismatch')
        gate=tsep.validate(report,bundle)
        tsep.require(tsep.read_json(bundle/'gate.json')==gate and tsep.read_json(bundle/'earl.jsonld')==tsep.earl(report,gate),'Report derivative mismatch')
    result=summarize(registration,inputs,counts,retained['browser_evidence_origin'],retained['assessment_end'])
    tsep.require(set(manifest)==expected,'Incomplete laboratory manifest')
    actual={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() or p.is_symlink()}
    tsep.require(actual==expected|{'SHA256SUMS'}, 'Unexpected unlisted file; transport wrappers must remain inert')
    tsep.require(semantic(result)==semantic(retained),'Replayed summary differs')
    tsep.require((root/'LIRE-MOI.txt').read_text()==reading_note(result),'Reading note differs')
    tsep.require(sources()==before,'Sources changed during replay')
    return {'same_results':True,'cases':len(inputs),'all_expectations_matched':result['all_expectations_matched'],
            'network_requests':0,'same_recorded_runtime':result['runtime']==retained['runtime'],'runtime':runtime_identity(),'scope':SCOPE}


def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    s=sub.add_parser('serve');s.add_argument('--output',required=True)
    f=sub.add_parser('finish');f.add_argument('source');f.add_argument('--observations',required=True);f.add_argument('--output',required=True);f.add_argument('--capture-kind',choices=['observed-browser','authored-fixture'],required=True)
    r=sub.add_parser('replay');r.add_argument('folder');r.add_argument('--output',required=True)
    args=p.parse_args()
    try:
        if args.command=='serve':
            server,thread,registration,tasks=start(args.output)
            print(json.dumps({'ready':True,'tasks':tasks,'output':args.output}),flush=True)
            try:thread.join()
            except KeyboardInterrupt:stop(server,thread)
            return 0
        if args.command=='finish':value=finish(args.source,args.observations,args.output,args.capture_kind)
        else:value=replay(args.folder);ts01.save(args.output,value)
        print(json.dumps({k:v for k,v in value.items() if k not in ('runtime','source_files','cases')},ensure_ascii=False))
        return 0 if value['all_expectations_matched'] else 2
    except (ValueError,KeyError,TypeError,OSError) as error:
        print(json.dumps({'error':str(error)}),file=sys.stderr);return 64


if __name__=='__main__':sys.exit(main())
