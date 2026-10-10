#!/usr/bin/env python3
"""Independent diagnostic harness: top-level versus iframe, before/after mutation."""
import argparse
import html
import json
from pathlib import Path
import secrets
import sys
import threading
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from examples import rendered_links_lab as links
from experiments import rendered_links as observer
from conformance.http import message

transport=links.transport;need=links.need;sha=links.sha
RECIPE='tests/fixtures/base-uri-diagnostic-v1.json'
PAGE='examples/base_uri_diagnostic_page.js'


def recipe():
    p=ROOT/RECIPE;need(sha(p.read_bytes())==p.with_suffix('.sha256').read_text().strip(),'Changed diagnostic recipe')
    return json.loads(p.read_bytes())


def sources():
    return dict(links.sources(),**{n:sha((ROOT/n).read_bytes()) for n in
        (RECIPE,RECIPE.replace('.json','.sha256'),PAGE,'examples/base_uri_diagnostic.py')})


def case_page(task,case,server):
    config=dict(id=task['id'],token=server['token'],origin=server['origin'],endpoint=server['base']+'/capture',
                script_sha256=sha((ROOT/observer.SCRIPT).read_bytes()))
    script=(ROOT/PAGE).read_text().replace('__CONFIG__',json.dumps(config)).replace('__MUTATION__',case['setup'])
    script=script.replace('__COLLECTOR__',(ROOT/observer.SCRIPT).read_text())
    return '<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>TSEP · '+task['id']+'</title>'+case['head']+\
        '<link rel="icon" href="data:,"><style>body{font:17px/1.5 system-ui;margin:32px auto;max-width:950px;padding:20px;background:#102032;color:#eef4ff}pre{white-space:pre-wrap;overflow-wrap:anywhere}a{color:#b8dcff}</style></head><body>'+\
        '<p>LABORATOIRE SYNTHÉTIQUE · DIAGNOSTIC DE BASE</p><h1>'+task['id']+'</h1><p id="status">Mesure en cours</p>'+\
        '<p>Reçu : <span id="receipt">en attente</span></p><a id="anchor-probe" data-probe="anchor" href="x">Lien observé, ne pas activer</a>'+\
        '<pre id="facts"></pre><script>'+script+'</script></body></html>'


def controller(plan):
    tasks=[t for t in plan['tasks'] if t['context']=='frame'];config=dict(tasks=tasks,origin=plan['server']['origin'])
    script='''const config=__CONFIG__;
    (async()=>{for(const task of config.tasks){
      document.getElementById('status').textContent='Mesure '+task.id;
      const frame=document.createElement('iframe');
      await new Promise((resolve,reject)=>{
        const listener=e=>{if(e.source!==frame.contentWindow||e.origin!==config.origin||e.data?.kind!=='base-uri-case-receipt'||e.data.id!==task.id)return;
          clearTimeout(timer);window.removeEventListener('message',listener);const li=document.createElement('li');li.textContent=task.id+' : '+e.data.receipt;document.getElementById('receipts').append(li);resolve();};
        const timer=setTimeout(()=>{window.removeEventListener('message',listener);reject(Error('Timeout '+task.id));},10000);
        window.addEventListener('message',listener);frame.src=task.url;document.getElementById('frames').append(frame);
      });frame.remove();
    }document.getElementById('status').textContent='Six observations iframe conservées — analyse hors ligne nécessaire';
    })().catch(e=>document.getElementById('status').textContent=String(e));'''.replace('__CONFIG__',json.dumps(config))
    return '<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>TSEP · diagnostic iframe</title><link rel="icon" href="data:,">'+\
        '<style>body{font:17px/1.5 system-ui;margin:32px auto;max-width:1000px;background:#102032;color:#eef4ff;padding:20px}li{overflow-wrap:anywhere}#frames{display:none}</style></head><body>'+\
        '<p>LABORATOIRE SYNTHÉTIQUE · SANS VERDICT TSEP</p><h1>Diagnostic des bases en iframe</h1><p id="status">Préparation</p>'+\
        '<ul id="receipts"></ul><div id="frames"></div><script>'+script+'</script></body></html>'


class Handler(transport.Handler):
    def dispatch(self,method,url,agent,body):
        folder=self.server.folder;plan=json.loads((folder/'plan.json').read_bytes());server=plan['server']
        need(plan['source_files']==sources(),'Changed diagnostic tools')
        if method=='GET' and url==server['origin']+'/favicon.ico':
            return transport.wire(b'',status=204),dict(kind='browser-favicon')
        if method=='GET' and url==server['base']:
            return (folder/'controller.bin').read_bytes(),dict(kind='controller')
        if method=='GET':
            task=next((t for t in plan['tasks'] if t['url']==url),None);need(task is not None,'Unplanned diagnostic visit')
            response=(folder/'planned'/task['file']).read_bytes();need(sha(response)==task['response_sha256'],'Changed planned bytes')
            return response,dict(kind='case',task_id=task['id'])
        need(url==server['base']+'/capture','Unplanned capture URL')
        data=json.loads(body);task=next((t for t in plan['tasks'] if t['id']==data.get('task_id')),None)
        need(task is not None and data.get('kind')=='base-uri-diagnostic-export' and data.get('version')=='1' and
             data.get('token')==server['token'] and data.get('user_agent')==agent and data.get('context')==task['context'] and
             data.get('script_sha256')==plan['source_files'][observer.SCRIPT],'Capture binding mismatch')
        return links.wire(json.dumps(dict(receipt=sha(body))),media='application/json'),dict(kind='capture',task_id=task['id'],receipt=sha(body))


def start(folder):
    folder=Path(folder);need(not folder.exists(),'Choose a new folder');r=recipe();folder.mkdir();(folder/'planned').mkdir()
    server=transport.Server(('127.0.0.1',0),Handler);token=secrets.token_hex(8)
    origin='http://'+token+'.localhost:'+str(server.server_address[1]);record=dict(kind='base-uri-diagnostic-server',version='1',token=token,origin=origin,base=origin+'/'+token)
    tasks=[]
    for context in r['contexts']:
        for case in r['cases']:
            id=context+'-'+case['id'];task=dict(id=id,case_id=case['id'],context=context,url=origin+'/'+context+'/'+case['id'],file=id+'.bin')
            body=case_page(task,case,record);response=links.wire(body,controller=True)
            task.update(response_sha256=sha(response),source_sha256=sha(body.encode()));tasks.append(task);(folder/'planned'/task['file']).write_bytes(response)
    plan=dict(kind='base-uri-diagnostic-plan',version='1',registered_at=transport.now(),server=record,recipe=r,tasks=tasks,source_files=sources())
    transport.save(folder/'plan.json',plan);transport.save(folder/'server.json',record)
    (folder/'controller.bin').write_bytes(links.wire(controller(plan),controller=True));(folder/'requests.jsonl').touch()
    server.folder=folder;server.record=record;server.sequence=0;server.lock=threading.Lock();return server,record


def close(server):
    server.server_close();p=server.folder
    transport.save(p/'closed.json',dict(closed_at=transport.now(),source_files=sources(),**{
        n+'_sha256':sha((p/f).read_bytes()) for n,f in [('plan','plan.json'),('log','requests.jsonl'),('controller','controller.bin')]}))


def analyze(folder):
    folder=Path(folder);plan=json.loads((folder/'plan.json').read_bytes());closed=json.loads((folder/'closed.json').read_bytes())
    need(plan['recipe']==recipe() and plan['source_files']==closed['source_files']==sources(),'Changed recipe/tools')
    for name,key in [('plan.json','plan'),('requests.jsonl','log'),('controller.bin','controller')]:
        need(sha((folder/name).read_bytes())==closed[key+'_sha256'],'Changed closed evidence')
    need((folder/'controller.bin').read_bytes()==links.wire(controller(plan),controller=True),'Changed controller bytes')
    rows=transport.logs(folder)
    need(all(r.get('kind') in ('controller','case','capture','browser-favicon') and r['complete'] and not r.get('conditional_or_session') for r in rows),'Unexpected/incomplete/session-bearing exchange')
    controllers=[r for r in rows if r['kind']=='controller'];need(len(controllers)==1,'Missing/duplicate controller')
    agents=set()
    for row in rows:
        request=(folder/(row['id']+'-request.bin')).read_bytes();response=(folder/(row['id']+'-response.bin')).read_bytes()
        need(sha(request)==row['request_sha256'] and sha(response)==row['response_sha256'],'Wire fingerprint mismatch')
        first,headers,body=message(request);agents.add(row['user_agent'])
        need(headers.get('user-agent')==[row['user_agent']] and headers.get('host')==[urlsplit(plan['server']['origin']).netloc] and
             not any(k in headers for k in ('cookie','authorization','if-none-match','if-modified-since','range','transfer-encoding')),'Request context differs')
        need(first==row['method']+' '+urlsplit(row['url']).path+' HTTP/1.1','Request URL differs')
    need(len(agents)==1,'Client changed')
    need((folder/(controllers[0]['id']+'-response.bin')).read_bytes()==(folder/'controller.bin').read_bytes(),'Controller response differs')
    compared=[]
    for task in plan['tasks']:
        case=next(c for c in plan['recipe']['cases'] if c['id']==task['case_id'])
        visits=[r for r in rows if r.get('task_id')==task['id'] and r['kind']=='case'];exports=[r for r in rows if r.get('task_id')==task['id'] and r['kind']=='capture']
        need(len(visits)==len(exports)==1,'Missing/duplicate visit or export');visit=visits[0];export=exports[0]
        response=(folder/(visit['id']+'-response.bin')).read_bytes();body=message((folder/(export['id']+'-request.bin')).read_bytes())[2];data=json.loads(body)
        need(response==links.wire(case_page(task,case,plan['server']),controller=True) and sha(response)==task['response_sha256'] and
             response==(folder/'planned'/task['file']).read_bytes() and sha(message(response,response=True)[2])==task['source_sha256'],'Response differs from prior bytes')
        need(sha(body)==export['receipt'] and data['kind']=='base-uri-diagnostic-export' and data['version']=='1' and
             data['token']==plan['server']['token'] and data['task_id']==task['id'] and data['context']==task['context'] and
             data['script_sha256']==plan['source_files'][observer.SCRIPT] and data['user_agent'] in agents,'Export binding differs')
        need(len(data['phases'])==2 and [p['phase'] for p in data['phases']]==['before','after'],'Missing/duplicate phase')
        previous=links.at(visit['received_at'])
        need(links.at(plan['registered_at'])<=previous<=links.at(export['received_at'])<=links.at(closed['closed_at']),'Invalid campaign chronology')
        if task['context']=='frame':need(links.at(controllers[0]['received_at'])<=previous,'Frame before controller')
        for phase in data['phases']:
            raw=phase['observation'];reading=observer.inventory(raw);facts=raw['document_before'];direct=phase['direct']
            need(raw['traversal_complete'] and reading['document_facts_equal'],'Incomplete/changed facts')
            need(facts['url']==task['url']==visit['url'] and facts['ready_state']=='complete' and facts['content_type']=='text/html' and facts['character_set']=='UTF-8','Document identity differs')
            need(previous<=links.at(phase['started_at'])<=links.at(phase['observed_at'])<=links.at(export['received_at']),'Phase chronology')
            previous=links.at(phase['observed_at'])
            selected=[r for r in reading['records'] if observer.attribute(r,'id')=='anchor-probe'];need(len(selected)==1,'Missing/duplicate instrumented anchor');anchor=selected[0]
            need(direct['document_url']==task['url'] and direct['base_uri']==facts['base_uri'] and direct['anchor_base_uri']==anchor['node_base_uri'] and
                 direct['href_property']==anchor['href_property'] and direct['raw_href']==anchor['raw_href'],'Direct and collector API reads disagree')
            base_records=[r for r in reading['records'] if r['tag']=='base' and r['namespace']==observer.HTML]
            need(direct['bases']==[dict(raw=r['raw_href'],property=r['href_property']) for r in base_records],'Base reads disagree')
            expected=links.replace(case['expected'][phase['phase']],task['url'],plan['server']['origin'])
            expected={k:v.replace('${CONTEXT}',task['context']) for k,v in expected.items()}
            actual=dict(base=facts['base_uri'],href=anchor['href_property'])
            compared.append(dict(id=task['id'],phase=phase['phase'],expected=expected,actual=actual,matches=expected==actual,direct=direct))
    need(sum(r['kind']=='case' for r in rows)==len(plan['tasks']) and sum(r['kind']=='capture' for r in rows)==len(plan['tasks']),'Extra observations')
    return dict(kind='base-uri-diagnostic-comparison',synthetic=True,normative_effect='none',rows=compared,
        matching=sum(r['matches'] for r in compared),total=len(compared),user_agent=next(iter(agents)),
        scope='One browser session, synthetic top-level and iframe documents, direct getters and collector in the same page realm. No cross-engine proof, authenticated origin, Google observation or TSEP verdict.')


def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    serve=sub.add_parser('serve');serve.add_argument('--output',type=Path,required=True)
    check=sub.add_parser('analyze');check.add_argument('folder',type=Path);check.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    if a.command=='serve':
        server,record=start(a.output);print(json.dumps(record),flush=True)
        try:server.serve_forever()
        except KeyboardInterrupt:pass
        finally:close(server)
        return 0
    r=analyze(a.folder);transport.save(a.output,r);print(json.dumps({k:v for k,v in r.items() if k!='rows'}));return 0 if r['matching']==r['total'] else 1


if __name__=='__main__':sys.exit(main())
