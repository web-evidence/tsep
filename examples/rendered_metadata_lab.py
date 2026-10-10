#!/usr/bin/env python3
"""Synthetic two-environment DOM inventory laboratory. No TSEP verdict. Apache-2.0."""
import argparse
from collections import Counter
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import secrets
import shutil
import sys
import threading

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import tsep
from collectors import ts01
from experiments import rendered_metadata as metadata
from conformance.http import raw_bytes
from provenance.runtime import loaded_sources

VERSION='1'
AGENT='TSEP-metadata-source/1'


def sources():
    result=ts01.collection_sources()
    result.update(loaded_sources(ROOT,{'examples/rendered_metadata_lab.py':sys.modules[__name__],
                                       'experiments/rendered_metadata.py':metadata}))
    for name in (metadata.SCRIPT,metadata.RECIPE,metadata.RECIPE.replace('.json','.sha256')):
        result[name]=tsep.digest(ROOT/name)
    return result


def substitute(value,base,cross):
    if isinstance(value,str):return value.replace('{base}',base).replace('{cross}',cross)
    if isinstance(value,list):return [substitute(v,base,cross) for v in value]
    if isinstance(value,dict):return {k:substitute(v,base,cross) for k,v in value.items()}
    return value


def page(case,token):
    return ('<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>TSEP DOM · '+case['id']+'</title>'+
            case['head']+'<style>body{font:18px/1.6 system-ui;background:#102032;color:#edf3f8;max-width:1000px;margin:40px auto}h1{font-size:36px}code{color:#b8ed76;overflow-wrap:anywhere}</style></head><body>'+
            '<p>LABORATOIRE SYNTHÉTIQUE · INVENTAIRE SANS VERDICT</p><h1>'+case['id']+'</h1>'+
            '<p id="lab-state">waiting</p><p>Contexte : <code id="lab-context">'+token+'</code></p>'+
            '<p>Agent : <code id="lab-agent">pending</code></p><p>Document : <code id="lab-url">pending</code></p>'+
            '<p>Erreurs signalées : <code id="lab-errors">[]</code></p>'+case['body']+
            '<script>const failures=[];function error(x){failures.push(String(x));document.getElementById("lab-errors").textContent=JSON.stringify(failures)};'+
            'window.addEventListener("error",e=>error(e.message));window.addEventListener("unhandledrejection",e=>error(e.reason));'+
            'try{'+case['script']+'}catch(e){error(e)};'+
            'document.getElementById("lab-agent").textContent=navigator.userAgent;document.getElementById("lab-url").textContent=location.href;'+
            'document.getElementById("lab-state").textContent="loaded";</script></body></html>')


def wire(body,origins):
    raw=body.encode('utf-8')
    header=('HTTP/1.1 200 Laboratory\r\nContent-Type: text/html; charset=utf-8\r\nContent-Length: '+str(len(raw))+
            "\r\nCache-Control: no-store\r\nContent-Security-Policy: default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; frame-src "+
            ' '.join(origins)+" about:\r\nConnection: close\r\n\r\n")
    return header.encode('ascii')+raw


class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def do_GET(self):
        url=self.server.origin+self.path
        raw=self.server.responses.get(url,b'HTTP/1.1 404 Outside scope\r\nContent-Length: 0\r\nConnection: close\r\n\r\n')
        row={'url':url,'agent':self.headers.get('User-Agent'),'peer':self.client_address[0],
             'observed_at':ts01.now(),'response_sha256':metadata.sha(raw),'complete':False}
        try:self.wfile.write(raw);self.wfile.flush();row['complete']=True
        finally:
            with self.server.lock,(self.server.folder/'requests.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
        self.close_connection=True


def stop(servers,threads):
    for s,t in zip(servers,threads):
        if t.is_alive():s.shutdown()
        s.server_close();t.join()


def start(output):
    folder=ts01.new_directory(output);before=sources();recipes=metadata.recipes()
    token=secrets.token_hex(8);servers=[ThreadingHTTPServer(('127.0.0.1',0),Handler) for _ in range(2)]
    origins=['http://127.0.0.1:'+str(s.server_port) for s in servers]
    base,cross=[o+'/'+token for o in origins]
    cases=[substitute(c,base,cross) for c in recipes['cases']]
    responses={base+'/case/'+c['id']:wire(page(c,token),origins) for c in cases}
    frames=[base+'/frame.html',cross+'/frame.html']
    for url in frames:responses[url]=wire('<!doctype html><html><head><link id="case-frame-link" rel="canonical" href="'+base+'/inner"></head><body>Separate frame document</body></html>',origins)
    reg={'kind':'synthetic-metadata-laboratory','version':VERSION,'registered_at':ts01.now(),
         'token':token,'base':base,'cross':cross,'origins':origins,'source_files':before,
         'script_sha256':metadata.script_digest(),'recipe':recipes,'cases':cases,
         'tasks':[{'id':c['id'],'url':base+'/case/'+c['id']} for c in cases],'frames':frames,
         'environments':['integrated','chrome'],'execution_context':'not-attested',
         'method':'One fixed read-only structured traversal after loaded, then logs/screenshot. No resampling or DOM cleanup.',
         'normative':False}
    ts01.save(folder/'registration.json',reg);(folder/'requests.jsonl').touch()
    lock=threading.Lock();threads=[]
    for s,origin in zip(servers,origins):
        s.folder=folder;s.origin=origin;s.lock=lock;s.responses=responses;s.daemon_threads=True
        t=threading.Thread(target=s.serve_forever,daemon=True);t.start();threads.append(t)
    try:
        urls=[t['url'] for t in reg['tasks']]+frames
        phases=[]
        for i in range(0,len(urls),10):
            name='source-'+str(i//10+1);phases.append(name)
            settings={'urls':urls[i:i+10],'origins':origins,'agent':AGENT,'accept_encoding':'identity','timeout':3,
                      'max_bytes':262144,'max_redirects':0,'allow_loopback':True,'network':'controlled loopback synthetic',
                      'selection_method':'Frozen browser recipes and both frame resources','access':'synthetic'}
            ts01.capture(settings,folder/name)
        receipt={'created_at':ts01.now(),'registration_sha256':tsep.digest(folder/'registration.json'),
                 'phases':{n:tsep.digest(folder/n/'SHA256SUMS') for n in phases},
                 'script_sha256':metadata.script_digest(),'source_files':before}
        ts01.save(folder/'receipt.json',receipt)
        tsep.require(sources()==before,'Sources changed before browser collection')
        return servers,threads,reg
    except BaseException:stop(servers,threads);raise


def assertions(case,tree,inv,source):
    """Recipe concordance only, never a normative outcome."""
    checks=[];expected=case['expected']
    ids={e['id_attribute']:e for e in inv['elements'] if e['id_attribute']}
    def check(label,value):checks.append({'check':label,'matches':bool(value)})
    check('planned traversal coverage',inv['traversal_complete']==expected.get('traversal_complete',True))
    for kind in ('canonical','robots','nodes'):
        candidates=inv['elements'] if kind=='nodes' else [x for x in inv['metadata'] if x['kind']==kind]
        for key,fields in expected.get(kind,{}).items():
            found=[r for r in candidates if r['id_attribute']==key]
            check(kind+':'+key,len(found)==1 and all(found[0].get(k)==v for k,v in fields.items()))
    for kind in ('canonical','robots'):
        if kind+'_ids' in expected:
            check(kind+' order',[m['id_attribute'] for m in inv['metadata'] if m['kind']==kind and m['id_attribute'] in expected[kind+'_ids']]==expected[kind+'_ids'])
    for key in expected.get('absent_ids',[]):check('absent:'+key,inv['traversal_complete'] and key not in ids)
    for key in expected.get('non_html',[]):check('foreign:'+key,key in ids and ids[key]['namespace']!=metadata.HTML and not any(m['id_attribute']==key for m in inv['metadata']))
    for label,kind in [('frame_ids','iframe'),('template_ids','template')]:
        for key in expected.get(label,[]):check(label+':'+key,key in ids and any(b['node_id']==ids[key]['node_id'] and b['kind']==kind for b in inv['boundaries']))
    for key in expected.get('unexposed_shadow',[]):check('shadow unknown:'+key,key in ids and tree['nodes'][ids[key]['node_id']]['shadow']=='unexposed-or-absent')
    for key in ('base_uri','traversal_complete','stop_reason'):
        if key in expected:check(key,inv[key]==expected[key])
    if 'source_contains' in expected:check('retained source',expected['source_contains'] in source)
    if 'attribute_order' in expected:check('attribute order','case-canonical' in ids and [a['name'] for a in ids['case-canonical']['attributes']]==expected['attribute_order'])
    if 'text_under' in expected:check('noscript text',expected['text_under'] in ids and any(n['parent']==ids[expected['text_under']]['node_id'] and n['type']==3 for n in tree['nodes']))
    return checks


def analyze(source,observations):
    source=Path(source);reg=tsep.read_json(source/'registration.json');receipt=tsep.read_json(source/'receipt.json')
    tsep.require(reg['source_files']==receipt['source_files']==sources() and reg['script_sha256']==metadata.script_digest(),
                 'Changed laboratory or capture script')
    tsep.require(receipt['registration_sha256']==tsep.digest(source/'registration.json'),'Registration changed')
    tsep.require(reg['recipe']==metadata.recipes() and reg['environments']==['integrated','chrome'], 'Changed recipes/environments')
    cases=[substitute(c,reg['base'],reg['cross']) for c in metadata.recipes()['cases']]
    tasks=[{'id':c['id'],'url':reg['base']+'/case/'+c['id']} for c in cases]
    frames=[reg['base']+'/frame.html',reg['cross']+'/frame.html']
    tsep.require(reg['cases']==cases and reg['tasks']==tasks and reg['frames']==frames,'Changed registered scope')
    expected_urls=[t['url'] for t in tasks]+frames
    tsep.require(list(receipt['phases'])==['source-1','source-2','source-3'],'Unexpected source phases')
    source_responses={}
    for phase_number,(name,digest) in enumerate(receipt['phases'].items()):
        tsep.require(tsep.digest(source/name/'SHA256SUMS')==digest,'Source phase changed');ts01.verify(source/name)
        phase=tsep.read_json(source/name/'capture.json');ts01.same_collector(phase)
        selected=expected_urls[phase_number*10:phase_number*10+10]
        tsep.require(phase['settings']['urls']==selected and [t['url'] for t in phase['targets']]==selected,
                     'Changed source URL order')
        tsep.require(phase['sources_unchanged_during_collection'] is True and
                     tsep.timestamp(reg['registered_at'])<=tsep.timestamp(phase['started_at'])<=
                     tsep.timestamp(phase['finished_at'])<=tsep.timestamp(receipt['created_at']), 'Source chronology mismatch')
        for number,target in enumerate(phase['targets'],1):
            tsep.require(len(target['http'])==1 and target['http'][0]['complete'] is True,'Incomplete source')
            for kind in ('request','response'):
                sidecar=source/name/('target-'+str(number)+'-hop-1-'+kind+'.bin')
                tsep.require(sidecar.read_bytes()==raw_bytes(target['http'][0][kind]),'Source JSON/sidecar mismatch')
            raw=raw_bytes(target['http'][0]['response']);source_responses[target['url']]=raw
    logs=[json.loads(line) for line in (source/'requests.jsonl').read_text().splitlines()]
    tsep.require(set(source_responses)==set(expected_urls),'Source scope mismatch')
    for row in logs:
        tsep.require(row['url'] in source_responses and row['peer']=='127.0.0.1' and row['complete'] is True
                     and row['response_sha256']==metadata.sha(source_responses[row['url']]),'Unexpected/different server response')
    tsep.require(Counter(r['url'] for r in logs if r['agent']==AGENT)==Counter(expected_urls),'Source request scope')
    tsep.require(set(observations)==set(reg['environments']),'Missing browser environment')
    results={};used=set();frame_requests=[]
    for env in reg['environments']:
        records=observations[env];tsep.require(set(records)=={t['id'] for t in reg['tasks']},'Missing/extra browser task')
        rows=[];agent=None
        for case,task in zip(reg['cases'],reg['tasks']):
            record=records[case['id']];tree=record['tree']
            tsep.require(record['script_sha256']==receipt['script_sha256']==metadata.script_digest(),'Different capture script')
            tsep.require(tree['document_url']==task['url'] and record['context']==reg['token']
                         and record['url']==task['url'] and record['state']=='loaded','Wrong page/context/state')
            tsep.require(isinstance(record['browser'],dict) and all(record['browser'].get(k) for k in ('name','version','user_agent')),
                         'Missing browser identity')
            ua=record['browser']['user_agent']
            tsep.require(ua!=AGENT and (agent is None or ua==agent),'Ambiguous environment agent');agent=ua
            tsep.require(tsep.timestamp(receipt['created_at'])<=tsep.timestamp(record['navigation_started_at'])
                         <=tsep.timestamp(record['observed_at']), 'Browser chronology mismatch')
            matches=[i for i,r in enumerate(logs) if r['url']==task['url'] and r['agent']==ua and i not in used
                     and tsep.timestamp(record['navigation_started_at'])<=tsep.timestamp(r['observed_at'])<=tsep.timestamp(record['observed_at'])]
            tsep.require(len(matches)==1,'Missing/ambiguous browser request');index=matches[0];used.add(index)
            if case['id'] in ('frame-same-origin','frame-cross-origin'):
                frame_url=reg['frames'][0 if case['id']=='frame-same-origin' else 1]
                frame_matches=[i for i,r in enumerate(logs) if r['url']==frame_url and r['agent']==ua and i not in used
                               and tsep.timestamp(record['navigation_started_at'])<=tsep.timestamp(r['observed_at'])<=tsep.timestamp(record['observed_at'])]
                tsep.require(len(frame_matches)==1,'Missing/ambiguous frame request')
                used.add(frame_matches[0]);frame_requests.append(frame_matches[0])
            inv=metadata.inventory(tree)
            checks=assertions(case,tree,inv,source_responses[task['url']].split(b'\r\n\r\n',1)[1].decode())
            rows.append({'id':case['id'],'inventory':inv,'recipe_checks':checks,
                         'recipe_checks_matched':all(c['matches'] for c in checks),'server_log_index':index,
                         'source_response_sha256':metadata.sha(source_responses[task['url']]),
                         'browser_record_sha256':metadata.sha(json.dumps(record,sort_keys=True,ensure_ascii=False).encode()),
                         'page_reported_errors':record['errors'],'developer_logs':record['devLogs']})
        results[env]=rows
    remaining=[r for i,r in enumerate(logs) if i not in used and r['agent']!=AGENT]
    tsep.require(not remaining,'Extra browser requests')
    return {'kind':'experimental-metadata-campaign','version':VERSION,'normative':False,
            'script_sha256':metadata.script_digest(),'environments':results,'server_requests':len(logs),
            'frame_server_log_indices':frame_requests,
            'observations':sum(len(r) for r in results.values()),
            'all_recipe_checks_matched':all(r['recipe_checks_matched'] for rows in results.values() for r in rows),
            'limits':['Not a TSEP assessment','No authentication of execution, browser APIs, timestamps or node origin',
                      'Server logs measure this loopback laboratory only','No iframe or template content inventory; closed shadow roots unknown',
                      'Recipe checks do not establish global coverage or SEO conformity']}


def source_names(root):
    receipt=tsep.read_json(root/'receipt.json')
    names=['registration.json','receipt.json','requests.jsonl']
    for phase in receipt['phases']:names += [phase+'/'+n for n in list(ts01.verify(root/phase))+['SHA256SUMS']]
    return names


def finish(source,observation_file,output):
    source=Path(source);observation_file=Path(observation_file)
    result=analyze(source,tsep.read_json(observation_file));output=ts01.new_directory(output);names=[]
    for name in source_names(source):
        p=output/'source'/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source/name,p);names.append('source/'+name)
    shutil.copyfile(observation_file,output/'observations.json');names.append('observations.json')
    ts01.save(output/'results.json',result);names.append('results.json')
    ts01.manifest(output,names);return result


def replay(folder):
    folder=Path(folder);manifest=ts01.verify(folder)
    tsep.require(set(manifest)=={'observations.json','results.json'}|{'source/'+n for n in source_names(folder/'source')},'Unexpected manifest file')
    actual={p.relative_to(folder).as_posix() for p in folder.rglob('*') if p.is_file() or p.is_symlink()}
    tsep.require(actual==set(manifest)|{'SHA256SUMS'},'Unexpected file')
    result=analyze(folder/'source',tsep.read_json(folder/'observations.json'))
    tsep.require(result==tsep.read_json(folder/'results.json'),'Replayed inventory differs')
    return {'same_inventory':True,'observations':result['observations'],'all_recipe_checks_matched':result['all_recipe_checks_matched'],
            'network_requests':0,'browser_executed':False,'normative':False}


def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    s=sub.add_parser('serve');s.add_argument('--output',required=True)
    f=sub.add_parser('finish');f.add_argument('source');f.add_argument('--observations',required=True);f.add_argument('--output',required=True)
    r=sub.add_parser('replay');r.add_argument('folder')
    a=p.parse_args()
    try:
        if a.command=='serve':
            servers,threads,reg=start(a.output);print(json.dumps({'ready':True,'tasks':reg['tasks'],'script_sha256':reg['script_sha256']}),flush=True)
            try:threads[0].join()
            except KeyboardInterrupt:stop(servers,threads)
            return 0
        result=finish(a.source,a.observations,a.output) if a.command=='finish' else replay(a.folder)
        print(json.dumps({k:v for k,v in result.items() if k!='environments'},ensure_ascii=False))
        return 0 if result['all_recipe_checks_matched'] else 2
    except (ValueError,KeyError,TypeError,OSError) as e:print(str(e),file=sys.stderr);return 64


if __name__=='__main__':sys.exit(main())
