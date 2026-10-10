#!/usr/bin/env python3
"""Finite SYNTHETIC iframe experiment; raw same-visit HTTP, no TSEP verdict."""
import argparse
from datetime import datetime
import hashlib
import html
import json
from pathlib import Path
import secrets
import sys
import threading

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from examples import same_navigation_lab as transport
from experiments import rendered_links as observer
from conformance.http import message

PAGE = 'examples/rendered_links_page.js'
need = observer.require
sha = lambda raw: hashlib.sha256(raw).hexdigest()


def sources():
    return dict(transport.sources(), **{n: sha((ROOT/n).read_bytes()) for n in
        (PAGE, 'examples/rendered_links_lab.py', 'experiments/rendered_links.py', observer.SCRIPT,
         observer.RECIPE, observer.RECIPE.replace('.json', '.sha256'))})


def replace(value, url, origin):
    if isinstance(value, str):
        return value.replace('${URL}', url).replace('${ORIGIN}', origin)
    if isinstance(value, dict):
        return {k: replace(v, url, origin) for k, v in value.items()}
    return value


def wire(body, csp='', controller=False, media='text/html; charset=utf-8'):
    raw = body.encode('utf-8')
    policy = ("default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data:; "
              "form-action 'none'; connect-src " + ("'self'; frame-src 'self'" if controller else "'none'; frame-src 'none'"))
    if csp:
        policy += '; '+csp
    return ('HTTP/1.1 200 Laboratory\r\nContent-Type: '+media+'\r\nContent-Length: '+str(len(raw))+
            '\r\nCache-Control: no-store\r\nContent-Security-Policy: '+policy+
            '\r\nConnection: close\r\n\r\n').encode('ascii')+raw


def case_page(case, url, origin):
    c = replace(case, url, origin)
    script = 'window.addEventListener("load",()=>{'+c['setup']+'\nconst observation='+ (ROOT/observer.SCRIPT).read_text()+ ';\n'+\
        'parent.postMessage({kind:"rendered-link-case",id:'+json.dumps(c['id'])+',observation,observed_at:new Date().toISOString()},'+json.dumps(origin)+');});'
    return '<!doctype html><html><head><meta charset="utf-8"><title>'+html.escape(c['id'])+'</title>'+c['head']+\
        '</head><body>'+c['body']+'<script>'+script+'</script></body></html>'


def controller(plan):
    server=plan['server']
    config=dict(tasks=plan['tasks'], origin=server['origin'], token=server['token'], endpoint=server['base']+'/capture',
                plan_sha256=sha(transport.package.json_bytes(plan)))
    script=(ROOT/PAGE).read_text().replace('__CONFIG__',json.dumps(config))
    return '<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>TSEP · liens rendus</title>'+\
        '<link rel="icon" href="data:,"><style>body{font:18px/1.6 system-ui;max-width:900px;margin:40px auto;padding:24px;background:#102032;color:#eef4ff}#frames{display:none}#receipt{overflow-wrap:anywhere}</style></head><body>'+\
        '<p>LABORATOIRE SYNTHÉTIQUE · EXPÉRIENCE SANS VERDICT</p><h1>Attribut href, propriété navigateur et base effective</h1>'+\
        '<p>26 recettes déclarées avant implémentation. Aucun clic sur les liens observés.</p><p id="status">Préparation</p>'+\
        '<p>Reçu : <span id="receipt">en attente</span></p><p>Le reçu atteste la conservation locale, pas la réussite des attentes ni une conformité SEO.</p>'+\
        '<div id="frames"></div><script>'+script+'</script></body></html>'


class Handler(transport.Handler):
    def dispatch(self, method, url, agent, body):
        folder=self.server.folder;plan=json.loads((folder/'plan.json').read_bytes());server=plan['server']
        need(plan['source_files']==sources(), 'Changed laboratory tools')
        if method=='GET' and url==server['origin']+'/favicon.ico':
            return transport.wire(b'',status=204), {'kind':'browser-favicon'}
        if method=='GET' and url==server['base']:
            return (folder/'controller.bin').read_bytes(), {'kind':'controller'}
        if method=='GET':
            task=next((t for t in plan['tasks'] if t['url']==url),None)
            need(task is not None,'Unplanned case URL')
            response=(folder/'planned'/task['file']).read_bytes()
            need(sha(response)==task['response_sha256'],'Changed planned response')
            return response, {'kind':'case','task_id':task['id']}
        need(url==server['base']+'/capture','Unplanned export')
        value=json.loads(body)
        need(value.get('kind')=='rendered-link-browser-campaign' and value.get('version')=='1' and
             value.get('token')==server['token'] and value.get('plan_sha256')==sha((folder/'plan.json').read_bytes()) and
             value.get('controller_url')==server['base'] and value.get('user_agent')==agent,'Export binding mismatch')
        return wire(json.dumps({'receipt':sha(body)}),media='application/json'), {'kind':'capture','receipt':sha(body)}


def start(folder):
    folder=Path(folder);need(not folder.exists(),'Choose a new folder')
    recipe=observer.recipes();folder.mkdir();(folder/'planned').mkdir()
    server=transport.Server(('127.0.0.1',0),Handler)
    token=secrets.token_hex(8);origin='http://'+token+'.localhost:'+str(server.server_address[1])
    record=dict(kind='rendered-link-server',version='1',origin=origin,base=origin+'/'+token,token=token)
    tasks=[]
    for case in recipe['cases']:
        url=origin+'/case/'+case['id'];body=case_page(case,url,origin);response=wire(body,case['csp']);name=case['id']+'.bin'
        (folder/'planned'/name).write_bytes(response)
        tasks.append(dict(id=case['id'],url=url,file=name,response_sha256=sha(response),source_sha256=sha(body.encode('utf-8'))))
    plan=dict(kind='rendered-link-browser-plan',version='1',registered_at=transport.now(),server=record,
              recipe=recipe,source_files=sources(),tasks=tasks,scope='SYNTHETIC iframes, page realm, one finite campaign; no TSEP outcome.')
    transport.save(folder/'plan.json',plan);(folder/'controller.bin').write_bytes(wire(controller(plan),controller=True))
    transport.save(folder/'server.json',record);(folder/'requests.jsonl').touch()
    server.folder=folder;server.record=record;server.sequence=0;server.lock=threading.Lock()
    return server,record


def close(server):
    server.server_close();folder=server.folder
    transport.save(folder/'closed.json',dict(closed_at=transport.now(),source_files=sources(),
        plan_sha256=sha((folder/'plan.json').read_bytes()),log_sha256=sha((folder/'requests.jsonl').read_bytes()),
        controller_sha256=sha((folder/'controller.bin').read_bytes())))


def at(value):
    result=datetime.fromisoformat(value.replace('Z','+00:00'))
    need(result.tzinfo is not None,'Undated observation');return result


def analyze(folder):
    folder=Path(folder);plan=json.loads((folder/'plan.json').read_bytes());closed=json.loads((folder/'closed.json').read_bytes())
    need(plan['recipe']==observer.recipes() and plan['source_files']==closed['source_files']==sources(),'Changed recipe/tools')
    for name,key in [('plan.json','plan_sha256'),('requests.jsonl','log_sha256'),('controller.bin','controller_sha256')]:
        need(sha((folder/name).read_bytes())==closed[key],'Changed closed evidence')
    need((folder/'controller.bin').read_bytes()==wire(controller(plan),controller=True),'Changed controller')
    rows=transport.logs(folder)
    need(all(r.get('kind') in ('controller','case','capture','browser-favicon') and r['complete'] and
             not r.get('conditional_or_session') for r in rows),'Unexpected/incomplete/session-bearing exchange')
    controllers=[r for r in rows if r['kind']=='controller'];exports=[r for r in rows if r['kind']=='capture']
    need(len(controllers)==len(exports)==1,'Missing/duplicate controller or capture')
    for row in rows:
        for part in ('request','response'):
            need(sha((folder/(row['id']+'-'+part+'.bin')).read_bytes())==row[part+'_sha256'],'Wire fingerprint mismatch')
    need((folder/(controllers[0]['id']+'-response.bin')).read_bytes()==(folder/'controller.bin').read_bytes(),'Controller differs')
    export=exports[0];body=message((folder/(export['id']+'-request.bin')).read_bytes())[2];data=json.loads(body)
    need(sha(body)==export['receipt'] and data['kind']=='rendered-link-browser-campaign' and data['version']=='1' and
         data['token']==plan['server']['token'] and data['plan_sha256']==closed['plan_sha256'] and
         data['controller_url']==plan['server']['base'],'Export binding mismatch')
    need(data['complete'] is True and data['errors']==[] and len(data['results'])==len(plan['tasks']),'Incomplete campaign')
    need(all(r['user_agent']==data['user_agent'] for r in rows),'HTTP client changed')
    need(at(plan['registered_at'])<=at(controllers[0]['received_at'])<=at(export['received_at'])<=at(closed['closed_at']),'Campaign chronology')
    compared=[]
    for task,case in zip(plan['tasks'],plan['recipe']['cases']):
        visits=[r for r in rows if r['kind']=='case' and r.get('task_id')==task['id']]
        observations=[r for r in data['results'] if r['id']==task['id']]
        need(len(visits)==len(observations)==1,'Missing/duplicate case observation')
        visit=visits[0];observed=observations[0];raw=observed['observation'];reading=observer.inventory(raw)
        response=(folder/(visit['id']+'-response.bin')).read_bytes()
        need(response==wire(case_page(case,task['url'],plan['server']['origin']),case['csp']) and
             sha(response)==task['response_sha256'] and response==(folder/'planned'/task['file']).read_bytes() and
             sha(message(response,response=True)[2])==task['source_sha256'],'Case differs from prior bytes')
        need(raw['traversal_complete'] and reading['document_facts_equal'],'Incomplete/changed document facts')
        facts=raw['document_before']
        need(observed['url']==facts['url']==visit['url']==task['url'] and facts['character_set']=='UTF-8' and
             facts['content_type']=='text/html' and facts['ready_state']=='complete','Case identity/settings differ')
        need(at(controllers[0]['received_at'])<=at(observed['started_at'])<=at(visit['received_at'])<=
             at(observed['observed_at'])<=at(export['received_at']),'Case chronology')
        actual=observer.projection(raw);expected=replace(case['expected'],task['url'],plan['server']['origin'])
        matching=set(actual)==set(expected) and all(all(actual[k][f]==v for f,v in e.items()) for k,e in expected.items())
        base=replace(case['expected_base'],task['url'],plan['server']['origin'])
        matching=matching and facts['base_uri']==base and all(r['node_base_uri']==base for r in raw['records'])
        compared.append(dict(id=task['id'],matches=matching,expected=expected,actual=actual,
            expected_base=base,actual_base=facts['base_uri'],records=len(raw['records']),nodes=raw['nodes_visited']))
    need(sum(r['kind']=='case' for r in rows)==len(plan['tasks']),'Unplanned/extra case')
    return dict(kind='rendered-link-browser-comparison',normative_effect='none',synthetic=True,
                user_agent=data['user_agent'],matching=sum(r['matches'] for r in compared),total=len(compared),rows=compared,
                scope='Finite synthetic iframe observations, one browser session, page APIs not authenticated; no top-level equivalence, real-site capture or TSEP verdict.')


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
    else:
        r=analyze(a.folder);transport.save(a.output,r);print(json.dumps({k:v for k,v in r.items() if k!='rows'}))
        return 0 if r['matching']==r['total'] else 1
    return 0


if __name__=='__main__':sys.exit(main())
