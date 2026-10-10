#!/usr/bin/env python3
"""SYNTHETIC browser/static-parser qualification; no normative decision. Apache-2.0."""
import argparse
import hashlib
import json
from pathlib import Path
import secrets
import sys
import threading

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from examples import same_navigation_lab as transport
from conformance.http import message

RECIPE = 'tests/fixtures/source-browser-v1.json'
PAGE = 'examples/source_browser_page.js'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def sources():
    return dict(transport.sources(), **{n: sha((ROOT/n).read_bytes()) for n in
                (RECIPE, RECIPE.replace('.json', '.sha256'), PAGE, 'examples/source_browser_lab.py',
                 'tests/fixtures/source-tree-cases-v2.json', 'tests/fixtures/source-tree-cases-v2.sha256')})


def recipe():
    raw = (ROOT/RECIPE).read_bytes()
    transport.tsep.require(sha(raw) == (ROOT/RECIPE).with_suffix('.sha256').read_text().strip(), 'Changed recipe')
    value = json.loads(raw)
    transport.tsep.require(sha((ROOT/value['fixture']).read_bytes()) == value['fixture_sha256'], 'Changed source fixtures')
    return value


def wire(body, *, controller=False, media='text/html; charset=utf-8'):
    raw = body.encode() if isinstance(body, str) else body
    policy = ("default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; "
              "img-src data:; base-uri 'none'; form-action 'none'; " +
              ("connect-src 'self'; frame-src 'self'" if controller else "connect-src 'none'; frame-src 'none'"))
    return ('HTTP/1.1 200 Laboratory\r\nContent-Type: '+media+'\r\nContent-Length: '+str(len(raw))+
            '\r\nCache-Control: no-store\r\nContent-Security-Policy: '+policy+
            '\r\nConnection: close\r\n\r\n').encode()+raw


def controller(server, plan):
    config = {'base': server['base'], 'token': server['token'], 'recipe': plan['recipe'],
              'plan_sha256': sha(transport.package.json_bytes(plan))}
    script = (ROOT/PAGE).read_text().replace('__CONFIG__', json.dumps(config))
    return ('<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>TSEP · qualification navigateur</title>'+
            '<link rel="icon" href="data:,"><style>body{font:17px/1.5 system-ui;background:#101b27;color:#e8eff8;max-width:1000px;margin:32px auto;padding:20px}h1{font-size:30px}p{overflow-wrap:anywhere}#frames{display:none}#observations{font-size:13px;columns:2}</style>'+
            '</head><body><p>LABORATOIRE SYNTHÉTIQUE — AUCUN VERDICT TSEP</p><h1>HTML source confronté au navigateur</h1>'+
            '<p>36 documents · deux configurations · témoins script/noscript · templates et shadow séparés</p>'+
            '<p id="status">Mesures en cours</p><p>Reçu : <span id="receipt">en attente</span></p>'+
            '<div id="observations"></div><div id="frames"></div><script>'+script+'</script></body></html>')


class Handler(transport.Handler):
    def dispatch(self, method, url, agent, body):
        server = self.server.record; folder = self.server.folder
        plan = transport.tsep.read_json(folder/'plan.json')
        transport.tsep.require(plan['source_files'] == sources(), 'Changed laboratory sources')
        if method == 'GET' and url == server['origin']+'/favicon.ico':
            return transport.wire(b'', status=204), {'kind':'browser-favicon'}
        if method == 'GET' and url == server['base']:
            return (folder/'controller.bin').read_bytes(), {'kind':'controller'}
        if method == 'GET':
            task = next((t for t in plan['tasks'] if t['url'] == url), None)
            transport.tsep.require(task is not None, 'Unplanned frame URL')
            response = (folder/'planned'/task['file']).read_bytes()
            transport.tsep.require(sha(response) == task['response_sha256'], 'Changed planned response')
            return response, {'kind':'frame','task_id':task['id'],'mode':task['mode']}
        transport.tsep.require(url == server['base']+'/capture' and len(body) <= 2*1024*1024, 'Unplanned/excessive capture')
        value = json.loads(body)
        transport.tsep.require(value['kind'] == 'synthetic-source-browser-observation' and value['version'] == '1'
            and value['token'] == server['token'] and value['plan_sha256'] == sha((folder/'plan.json').read_bytes())
            and value['user_agent'] == agent and value['controller_url'] == server['base'], 'Capture binding mismatch')
        return wire(json.dumps({'receipt':sha(body)}), media='application/json'), {'kind':'capture','receipt':sha(body)}


def start(output):
    folder = Path(output); transport.tsep.require(not folder.exists(), 'Choose a new folder')
    source = recipe(); folder.mkdir(); (folder/'planned').mkdir()
    server = transport.Server(('127.0.0.1',0), Handler)
    token = secrets.token_hex(8); origin = 'http://'+token+'.localhost:'+str(server.server_address[1])
    record = {'kind':'source-browser-server','version':'1','created_at':transport.now(),
              'origin':origin,'base':origin+'/'+token,'token':token}
    fixture = json.loads((ROOT/source['fixture']).read_bytes())
    calibration = ('<!doctype html><html><head><meta charset="utf-8"></head><body>'
       '<span id="script-status">not-run</span><script>document.getElementById("script-status").textContent="ran";</script>'
       '<noscript><span id="noscript-status">present</span></noscript></body></html>')
    documents = [{'id':'calibration','html':calibration}] + fixture['cases']
    tasks=[]
    for doc in documents:
        for mode in source['modes']:
            response = wire(doc['html']); name = doc['id']+'-'+mode+'.bin'
            (folder/'planned'/name).write_bytes(response)
            tasks.append({'id':doc['id'],'mode':mode,'url':record['base']+'/case/'+doc['id']+'/'+mode,
                          'file':name,'source_sha256':sha(doc['html'].encode()),'response_sha256':sha(response)})
    plan = {'kind':'source-browser-plan','version':'1','registered_at':transport.now(),'server':record,
            'recipe':source,'source_files':sources(),'tasks':tasks,'scope':source['scope']}
    transport.save(folder/'plan.json',plan)
    (folder/'controller.bin').write_bytes(wire(controller(record,plan),controller=True))
    transport.save(folder/'server.json',record);(folder/'requests.jsonl').touch()
    server.folder=folder;server.record=record;server.sequence=0;server.lock=threading.Lock()
    return server,record


def close(server):
    server.server_close();folder=server.folder
    transport.save(folder/'closed.json',{'closed_at':transport.now(),'source_files':sources(),
        'plan_sha256':sha((folder/'plan.json').read_bytes()),'log_sha256':sha((folder/'requests.jsonl').read_bytes()),
        'controller_sha256':sha((folder/'controller.bin').read_bytes())})


def analyze(folder):
    folder=Path(folder);plan=transport.tsep.read_json(folder/'plan.json');closed=transport.tsep.read_json(folder/'closed.json')
    need=transport.tsep.require
    need(plan['recipe']==recipe() and plan['source_files']==closed['source_files']==sources(), 'Changed recipe/tools')
    need(closed['plan_sha256']==sha((folder/'plan.json').read_bytes()) and
         closed['log_sha256']==sha((folder/'requests.jsonl').read_bytes()), 'Changed closed records')
    need(closed['controller_sha256']==sha((folder/'controller.bin').read_bytes()) and
         (folder/'controller.bin').read_bytes()==wire(controller(plan['server'],plan),controller=True), 'Changed controller')
    rows=transport.logs(folder);allowed={'controller','frame','capture','browser-favicon'}
    need(all(r.get('kind') in allowed and r['complete'] and not r.get('conditional_or_session') for r in rows),
         'Unexpected, incomplete or session-bearing HTTP exchange')
    controllers=[r for r in rows if r['kind']=='controller'];captures=[r for r in rows if r['kind']=='capture']
    need(len(controllers)==len(captures)==1, 'Missing/duplicate controller or capture')
    for row in rows:
        request=(folder/(row['id']+'-request.bin')).read_bytes();response=(folder/(row['id']+'-response.bin')).read_bytes()
        need(sha(request)==row['request_sha256'] and sha(response)==row['response_sha256'], 'Wire fingerprint mismatch')
    need((folder/(controllers[0]['id']+'-response.bin')).read_bytes()==(folder/'controller.bin').read_bytes(),'Controller response differs')
    first,headers,body=message((folder/(captures[0]['id']+'-request.bin')).read_bytes());data=json.loads(body)
    need(sha(body)==captures[0]['receipt'] and data['plan_sha256']==sha((folder/'plan.json').read_bytes())
         and data['token']==plan['server']['token'], 'Export binding mismatch')
    need(data['kind']=='synthetic-source-browser-observation' and data['version']=='1' and
         data['controller_url']==plan['server']['base'], 'Export kind/controller mismatch')
    need(data['complete'] is True and data['errors']==[] and len(data['results'])==74, 'Incomplete browser observation')
    need(all(r['user_agent']==data['user_agent'] for r in rows), 'HTTP client changed')
    need(plan['registered_at']<=controllers[0]['received_at']<=captures[0]['received_at']<=closed['closed_at'], 'Invalid chronology')
    compared=[]
    for task in plan['tasks']:
        visits=[r for r in rows if r['kind']=='frame' and r.get('task_id')==task['id'] and r.get('mode')==task['mode']]
        observations=[r for r in data['results'] if r['id']==task['id'] and r['mode']==task['mode']]
        need(len(visits)==len(observations)==1,'Missing/duplicate frame or observation')
        visit=visits[0];observed=observations[0];tree=observed['tree']
        response=(folder/(visit['id']+'-response.bin')).read_bytes()
        need(sha(response)==task['response_sha256'] and response==(folder/'planned'/task['file']).read_bytes(), 'Frame differs from prior bytes')
        need(sha(message(response,response=True)[2])==task['source_sha256'], 'Source body differs')
        need(observed['url']==tree['url']==visit['url']==task['url'] and
             observed['sandbox']==plan['recipe']['modes'][task['mode']] and tree['ready_state']=='complete'
             and tree['character_set']=='UTF-8' and tree['content_type']=='text/html','Frame identity/settings differ')
        need(controllers[0]['received_at']<=observed['started_at']<=visit['received_at']<=observed['observed_at']<=captures[0]['received_at'], 'Frame chronology differs')
        if task['id']=='calibration':
            need(observed['calibration']==plan['recipe']['calibration'][task['mode']], 'Calibration failed')
            continue
        actual={k:[s['id'] for s in tree['signals'] if s['context']==k] for k in ('head','body','template','shadow')}
        expectation=next(c for c in plan['recipe']['cases'] if c['id']==task['id'])['expected_browser'][task['mode']]
        compared.append({'id':task['id'],'mode':task['mode'],'actual':actual,'expected':expectation,'matches':actual==expectation})
    return {'kind':'synthetic-source-browser-comparison','normative_effect':'none','user_agent':data['user_agent'],
            'observations':74,'compared_readings':72,'matching':sum(r['matches'] for r in compared),'rows':compared,
            'scope':'Observed iframe DOMs in one declared browser session, finite synthetic documents and sandbox configurations. Client identity is self-reported, not authenticated. No top-level navigation equivalence, Google observation, browser universality, human review or TSEP outcome.'}


def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
    serve=sub.add_parser('serve');serve.add_argument('--output',type=Path,required=True)
    compare=sub.add_parser('analyze');compare.add_argument('folder',type=Path);compare.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.command=='serve':
        server,record=start(args.output);print(json.dumps(record),flush=True)
        try:server.serve_forever()
        except KeyboardInterrupt:pass
        finally:close(server)
    else:
        result=analyze(args.folder);transport.save(args.output,result)
        print(json.dumps({k:v for k,v in result.items() if k!='rows'}))


if __name__=='__main__':main()
