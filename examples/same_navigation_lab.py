#!/usr/bin/env python3
"""Same-navigation SYNTHETIC browser laboratory; exact HTTP bytes. Apache-2.0."""
import argparse
import hashlib
import html
import json
from pathlib import Path
import re
import secrets
import shutil
import socketserver
import sys
import threading
from datetime import datetime, timezone
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import tsep
from adapters import captures, package, replay
from conformance.evaluate import binding_digest, evaluate, trace
from conformance.http import encoded, header_fields
from experiments import rendered_metadata as metadata
from provenance.runtime import loaded_sources

VERSION = '1'
RECIPE = 'tests/fixtures/same-navigation-lab-v1.json'
PAGE = 'examples/same_navigation_page.js'
MAX_BODY = 2 * 1024 * 1024


def now():
    return datetime.now(timezone.utc).isoformat()


def save(path, value):
    with Path(path).open('xb') as stream:
        stream.write(package.json_bytes(value))


def sources():
    result = dict(captures.source_files(), **loaded_sources(ROOT, {
        'examples/same_navigation_lab.py': sys.modules[__name__], 'adapters/package.py': package,
        'adapters/replay.py': replay}))
    for name in (PAGE, RECIPE, RECIPE.replace('.json', '.sha256')):
        result[name] = tsep.digest(ROOT/name)
    return result


def recipes():
    path = ROOT/RECIPE
    tsep.require(tsep.digest(path) == path.with_suffix('.sha256').read_text().split()[0], 'Changed frozen recipe')
    return tsep.read_json(path)


def wire(body, media='text/html; charset=utf-8', status=200, extra=''):
    raw = body.encode('utf-8') if isinstance(body, str) else body
    return ('HTTP/1.1 '+str(status)+' Laboratory\r\nContent-Type: '+media+'\r\nContent-Length: '+str(len(raw))+
            "\r\nCache-Control: no-store\r\nContent-Security-Policy: default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'self'; img-src data:\r\n"+
            extra+'Connection: close\r\n\r\n').encode('ascii')+raw


def page(task, server):
    script = (ROOT/PAGE).read_text()
    for key, value in [('__MUTATION__', task['mutation']), ('__CONTEXT__', server['token']),
                       ('__TASK__', task['id']), ('__NAVIGATION__', task['navigation_id']),
                       ('__SCRIPT_SHA__', metadata.script_digest()), ('__ENDPOINT__', server['base']+'/capture')]:
        script = script.replace(key, json.dumps(value))
    script = script.replace('__CAPTURE_EXPRESSION__', (ROOT/metadata.SCRIPT).read_text().strip())
    url = html.escape(task['url'], quote=True)
    return ('<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>TSEP · '+task['id']+'</title>'+
            '<link rel="icon" href="data:,"><link id="primary-canonical" rel="canonical" href="'+url+'">'+
            '<style>body{font:18px/1.6 system-ui;background:#102032;color:#edf3f8;max-width:1000px;margin:40px auto;padding:20px}h1{font-size:36px}span{overflow-wrap:anywhere}</style></head><body>'+
            '<p>LABORATOIRE SYNTHÉTIQUE · NAVIGATION UNIQUE</p><h1>'+task['id']+'</h1>'+
            '<p>Navigation : <span id="lab-navigation">'+task['navigation_id']+'</span></p>'+
            '<p>État : <span id="lab-state">pending</span></p><p>Reçu : <span id="lab-receipt">pending</span></p>'+
            '<p>Cette page est un cas de test local. Elle ne représente pas Edikka ni une visite Googlebot.</p>'+
            '<a id="family-link" href="'+url+'">Ressource préférée déclarée</a><script>'+script+'</script></body></html>')


def decode(raw):
    tsep.require(len(raw) <= MAX_BODY, 'POST byte bound')
    envelope = json.loads(raw)
    tsep.require(set(envelope) == {'payload', 'sha256'} and isinstance(envelope['payload'], str)
                 and hashlib.sha256(envelope['payload'].encode()).hexdigest() == envelope['sha256'], 'POST payload digest mismatch')
    data = json.loads(envelope['payload'])
    tsep.require(data['kind'] == 'same-navigation-page' and data['version'] == VERSION
                 and data['script_sha256'] == metadata.script_digest(), 'Unsupported page export')
    metadata.inventory(data['tree'])
    return data


def logs(folder):
    return [json.loads(line) for line in (Path(folder)/'requests.jsonl').read_text().splitlines()]


class Server(socketserver.ThreadingTCPServer):
    daemon_threads = False
    block_on_close = True
    allow_reuse_address = False


class Handler(socketserver.StreamRequestHandler):
    def handle(self):
        self.connection.settimeout(5)
        with self.server.lock:
            number = self.server.sequence
            self.server.sequence += 1
        name = 'request-'+str(number)
        row = {'id': name, 'peer': self.client_address[0], 'received_at': now(), 'complete': False}
        raw = bytearray(); response = b''
        try:
            for _ in range(101):
                line = self.rfile.readline(65537); raw.extend(line)
                tsep.require(len(raw) <= 65536 and line.endswith(b'\r\n'), 'Incomplete/excessive HTTP header')
                if line == b'\r\n': break
            else: raise tsep.Invalid('HTTP header line bound')
            first, headers, _ = header_fields(bytes(raw))
            match = re.fullmatch(r'(GET|POST) ([^ ]+) HTTP/1\.1', first)
            tsep.require(match, 'Unsupported request line')
            method, path = match.groups()
            agents = headers.get('user-agent', [])
            tsep.require(len(agents) == 1 and agents[0], 'Missing/ambiguous HTTP agent')
            tsep.require(headers.get('host') == [urlsplit(self.server.record['origin']).netloc], 'Unexpected Host')
            tsep.require('transfer-encoding' not in headers, 'Chunked request outside laboratory scope')
            sizes = headers.get('content-length', ['0'])
            tsep.require(len(sizes) == 1 and re.fullmatch('[0-9]+', sizes[0]), 'Ambiguous request length')
            count = int(sizes[0]); tsep.require(0 <= count <= MAX_BODY, 'Request body bound')
            body = self.rfile.read(count); raw.extend(body)
            tsep.require(len(body) == count and (method != 'GET' or count == 0), 'Incomplete/unexpected request body')
            url = self.server.record['origin']+path
            row.update(method=method, url=url, user_agent=agents[0],
                       conditional_or_session=any(k in headers for k in
                           ('if-none-match', 'if-modified-since', 'range', 'authorization', 'cookie')))
            response, detail = self.dispatch(method, url, agents[0], body)
            row.update(detail)
        except (ValueError, KeyError, TypeError, OSError) as error:
            row['error'] = str(error)
            response = wire(json.dumps({'error': str(error)}), 'application/json', 400)
        try:
            row['response_started_at'] = now()
            self.wfile.write(response); self.wfile.flush(); row['complete'] = True
        except OSError as error:
            row['write_error'] = str(error)
        finally:
            row['finished_at'] = now()
            row['request_sha256'] = hashlib.sha256(raw).hexdigest()
            row['response_sha256'] = hashlib.sha256(response).hexdigest()
            with self.server.lock:
                (self.server.folder/(name+'-request.bin')).write_bytes(raw)
                (self.server.folder/(name+'-response.bin')).write_bytes(response)
                with (self.server.folder/'requests.jsonl').open('a') as stream:
                    stream.write(json.dumps(row)+'\n')

    def dispatch(self, method, url, agent, body):
        server = self.server.record; folder = self.server.folder
        if method == 'GET' and url == server['base']+'/calibrate':
            tsep.require(not (folder/'plan.json').exists(), 'Calibration already sealed')
            return wire('<html><head><title>TSEP calibration</title><link rel="icon" href="data:,"></head><body>'+
                '<h1>Calibration avant mesure</h1><p>Agent reçu : <span id="calibration-agent">'+html.escape(agent)+
                '</span></p><p>Aucun contrôle SEO effectué.</p></body></html>'), {'kind': 'calibration'}
        if method == 'GET' and url == server['origin']+'/favicon.ico':
            return wire(b'', status=204), {'kind': 'browser-favicon'}
        plan = tsep.read_json(folder/'plan.json')
        tsep.require(plan['source_files'] == sources(), 'Laboratory sources changed')
        if method == 'GET':
            task = next((t for t in plan['tasks'] if t['url'] == url), None)
            tsep.require(task is not None, 'Unplanned navigation')
            response = package.regular(folder/'planned'/(task['id']+'.bin'))
            tsep.require(hashlib.sha256(response).hexdigest() == task['response_sha256'], 'Planned response changed')
            return response, {'kind': 'navigation', 'task_id': task['id'], 'navigation_id': task['navigation_id']}
        tsep.require(url == server['base']+'/capture', 'Unplanned POST')
        data = decode(body)
        task = next((t for t in plan['tasks'] if t['id'] == data['task_id']), None)
        tsep.require(task and data['context'] == server['token'] and data['url'] == task['url']
                     and data['navigation_id'] == task['navigation_id'], 'Page attribution mismatch')
        receipt = hashlib.sha256(body).hexdigest()
        return wire(json.dumps({'receipt': receipt}), 'application/json'), {
            'kind': 'capture', 'task_id': task['id'], 'navigation_id': task['navigation_id'], 'receipt': receipt}


def start(output, origin_host='127.0.0.1'):
    tsep.require(origin_host in ('127.0.0.1', 'isolated-localhost'), 'Unsupported loopback origin')
    folder = Path(output); tsep.require(not folder.exists() and folder.parent.is_dir(), 'Choose a new source directory')
    folder.mkdir(); server = Server(('127.0.0.1', 0), Handler)
    token = secrets.token_hex(8)
    host = token+'.localhost' if origin_host == 'isolated-localhost' else origin_host
    origin = 'http://'+host+':'+str(server.server_address[1])
    record = {'kind': 'same-navigation-server', 'version': VERSION, 'created_at': now(), 'origin': origin,
              'token': token, 'base': origin+'/'+token, 'source_files': sources()}
    save(folder/'server.json', record); (folder/'requests.jsonl').touch()
    server.folder = folder; server.record = record; server.sequence = 0; server.lock = threading.Lock()
    return server, record


def seal(folder, browser_name, browser_version):
    folder = Path(folder); server = tsep.read_json(folder/'server.json')
    tsep.require(server['source_files'] == sources(), 'Changed tools before sealing')
    rows = logs(folder); calibration = [r for r in rows if r.get('kind') == 'calibration']
    tsep.require(len(calibration) == 1 and all(r.get('kind') in ('calibration', 'browser-favicon')
                 and r['complete'] for r in rows), 'Calibration must be unique with no prior control attempt')
    tsep.require(not calibration[0].get('conditional_or_session'), 'Calibration carries conditional/session headers; use a separate isolated origin, never strip the capture')
    tsep.require(browser_name.strip() and browser_version.strip(), 'Declared browser identity required')
    agent = calibration[0]['user_agent']; recipe = recipes(); tasks = []
    (folder/'planned').mkdir()
    for case in recipe['cases']:
        task = dict(case, url=server['base']+'/case/'+case['id'], navigation_id=server['token']+'-'+case['id'])
        extra = ('X-Robots-Tag: '+case['x_robots_tag']+'\r\n') if 'x_robots_tag' in case else ''
        raw = wire(page(task, server), extra=extra)
        (folder/'planned'/(case['id']+'.bin')).write_bytes(raw)
        task['response_sha256'] = hashlib.sha256(raw).hexdigest(); tasks.append(task)
    plan = {'kind': 'same-navigation-plan', 'version': VERSION, 'registered_at': now(), 'server': server,
            'source_files': sources(), 'recipe': recipe, 'agent': agent, 'calibration_id': calibration[0]['id'],
            'browser': {'name': browser_name, 'version': browser_version}, 'tasks': tasks,
            'capture': {'state_id': 'load-state', 'interactions': [], 'wait': 'window.load after fixed mutation'},
            'scope': 'Synthetic local pages, one navigation and export per task; no real site or engine inference'}
    save(folder/'plan.json', plan)
    return plan


def analyze(folder, observations):
    folder = Path(folder); server = tsep.read_json(folder/'server.json'); plan = tsep.read_json(folder/'plan.json')
    closed = tsep.read_json(folder/'closed.json')
    tsep.require(server['source_files'] == plan['source_files'] == closed['source_files'] == sources(), 'Changed collection tools')
    tsep.require(plan['server'] == server and plan['recipe'] == recipes(), 'Changed registration')
    tsep.require(closed['plan_sha256'] == tsep.digest(folder/'plan.json') and
                 closed['log_sha256'] == tsep.digest(folder/'requests.jsonl'), 'Changed closed campaign')
    tsep.require(set(observations) == {t['id'] for t in plan['tasks']}, 'Incomplete operator observation inventory')
    rows = logs(folder); used = set(); results = []
    tsep.require([t['id'] for t in plan['tasks']] == [c['id'] for c in recipes()['cases']],
                 'Missing/reordered registered task')
    expected_files = {'server.json', 'plan.json', 'closed.json', 'requests.jsonl'}
    expected_files.update('planned/'+t['id']+'.bin' for t in plan['tasks'])
    expected_files.update(r['id']+'-'+kind+'.bin' for r in rows for kind in ('request', 'response'))
    actual_files = set()
    for path in folder.rglob('*'):
        tsep.require(not path.is_symlink(), 'Source symlinks unsupported')
        if path.is_file(): actual_files.add(path.relative_to(folder).as_posix())
    tsep.require(actual_files == expected_files, 'Unexpected/missing source file or unlisted request')
    for row in rows:
        tsep.require(row['peer'] == '127.0.0.1' and row['complete'] and 'error' not in row, 'Failed/nonlocal request retained; campaign cannot be complete')
        for kind in ('request', 'response'):
            tsep.require(tsep.digest(folder/(row['id']+'-'+kind+'.bin')) == row[kind+'_sha256'], 'Raw HTTP sidecar changed')
        if row.get('kind') in ('calibration', 'browser-favicon'): used.add(row['id'])
    calibration = [r for r in rows if r.get('kind') == 'calibration']
    tsep.require(len(calibration) == 1 and calibration[0]['id'] == plan['calibration_id']
                 and calibration[0]['user_agent'] == plan['agent']
                 and tsep.timestamp(calibration[0]['finished_at']) <= tsep.timestamp(plan['registered_at']), 'Invalid prior calibration')
    for task, recipe in zip(plan['tasks'], recipes()['cases']):
        tsep.require(all(task[k] == v for k,v in recipe.items()) and task['url'] == server['base']+'/case/'+recipe['id']
                     and task['navigation_id'] == server['token']+'-'+recipe['id'], 'Task differs from frozen recipe')
        get = [r for r in rows if r.get('kind') == 'navigation' and r.get('task_id') == task['id']]
        post = [r for r in rows if r.get('kind') == 'capture' and r.get('task_id') == task['id']]
        tsep.require(len(get) == len(post) == 1, 'Missing/duplicate navigation or capture: '+task['id'])
        get, post = get[0], post[0]; used.update([get['id'], post['id']]); observation = observations[task['id']]
        _, _, body = header_fields((folder/(post['id']+'-request.bin')).read_bytes()); payload = decode(body)
        tsep.require(hashlib.sha256(body).hexdigest() == post['receipt'] == observation['receipt'], 'Operator/POST receipt mismatch')
        tsep.require(payload['context'] == server['token'] and payload['url'] == task['url'] == payload['tree']['document_url']
                     and payload['navigation_id'] == task['navigation_id'] and payload['task_id'] == task['id'], 'Capture identity mismatch')
        tsep.require(get['user_agent'] == post['user_agent'] == payload['user_agent'] == plan['agent'], 'Browser agent changed after calibration')
        dates = [plan['registered_at'], observation['navigation_started_at'], get['response_started_at'],
                 payload['capture_started_at'], payload['captured_at'], post['response_started_at'], observation['observed_at'], closed['closed_at']]
        tsep.require(all(tsep.timestamp(a) <= tsep.timestamp(b) for a,b in zip(dates, dates[1:])), 'Navigation/capture chronology mismatch')
        raw_response = (folder/(get['id']+'-response.bin')).read_bytes()
        expected = wire(page(task, server), extra=('X-Robots-Tag: '+task['x_robots_tag']+'\r\n') if 'x_robots_tag' in task else '')
        tsep.require(raw_response == expected == (folder/'planned'/(task['id']+'.bin')).read_bytes()
                     and hashlib.sha256(expected).hexdigest() == task['response_sha256'], 'Observed response differs from prior bytes')
        hops = [{'url':task['url'], 'complete':True, 'request':encoded((folder/(get['id']+'-request.bin')).read_bytes()), 'response':encoded(raw_response)}]
        trace(hops, task['url'], plan['agent'])
        support = json.dumps({'GET':get,'POST':post,'operator':observation,'plan_sha256':tsep.digest(folder/'plan.json')},sort_keys=True)
        snapshot = {'script_sha256':payload['script_sha256'],'tree':payload['tree']}
        structured = {'snapshot':snapshot,'snapshot_sha256':binding_digest(snapshot),'known_integrity_issues':[],
            'acquisition':{'kind':'same-navigation','navigation_id':task['navigation_id'],'user_agent':plan['agent'],
                          'http_sha256':binding_digest(hops),'support':[{'name':'Synthetic laboratory navigation receipt',
                          'content':support,'sha256':hashlib.sha256(support.encode()).hexdigest()}]}}
        state = dict(plan['capture'], id=plan['capture']['state_id'], url=task['url'], context_id=server['token'],
                     source_http_sha256=binding_digest(hops), observed_at=payload['captured_at'],complete=payload['tree']['traversal_complete'],
                     javascript_enabled=True,errors=payload['errors'],structured_dom=structured)
        state.pop('state_id')
        render_plan={'mode':'required','dom_reader':'structured-inventory-v2','required_states':[{'id':state['id'],'interactions':state['interactions'],'wait':state['wait']}]}
        context={'id':server['token'],'network':'synthetic loopback browser laboratory','bounds':'one registered navigation per task; inventory 2 limits','tool':'TSEP same-navigation laboratory','tool_version':VERSION}
        intent={'declared_at':plan['registered_at'],'crawler':plan['agent'],'directive_crawler':'googlebot',
                'public_canonical':True,'indexing':'allow','following':'unspecified','rendering':render_plan}
        document={'url':task['url'],'observed_at':get['response_started_at'],'context_id':server['token'],'http':hops,
                  'render':{'browser':plan['browser'],'states':[state]}}
        target=dict(document,context=context,intent=intent)
        if task['rules'][0].startswith('TS10-'):
            member={'url':task['url'],'required_methods':['html','dom'],'rendering':render_plan}
            members=[member]
            if task['mutation']=='links':members.append(dict(member,url=task['url']+'?variant=1'))
            intent['canonical']={'preferred_url':task['url'],'members':members,'links':{'sources':[{'url':task['url'],'rendering':render_plan}],'exceptions':[]}}
            target={'url':task['url'],'observed_at':observation['observed_at'],'context':context,'intent':intent,'documents':[document],'crawl':{'documents':[document]}}
        data={'input_version':'2','rules':task['rules'],'targets':[target]}; actual=evaluate(data)
        results.append({'id':task['id'],'input':data,'atomic_results':actual,'expected':task['expected'],
                        'matched':task['expected']==[r['outcome'] for r in actual], 'receipt':post['receipt']})
    tsep.require(len(used)==len(rows), 'Unmatched request; do not hide or resample attempts')
    return results


def finish(source, observation_file, output):
    source, output = Path(source), Path(output)
    observations=tsep.read_json(observation_file); results=analyze(source,observations)
    tsep.require(not output.exists() and output.parent.is_dir(), 'Choose a new delivery directory')
    output.mkdir(); shutil.copytree(source,output/'source'); shutil.copyfile(observation_file,output/'observations.json')
    summary=[]
    for row in results:
        path=output/row['id'];path.mkdir();save(path/'input.json',row['input'])
        captures.build(path/'input.json',path/'bundle',assessor='Automated laboratory import; no human review',label='SYNTHETIC browser navigation — '+row['id'],
                       selection_method='One predeclared local page and state; actual browser observations, synthetic scenario',access='synthetic',mode='automatic')
        replay.replay(path/'bundle',path/'replay')
        summary.append({k:v for k,v in row.items() if k!='input'})
    save(output/'results.json',{'kind':'same-navigation-results','version':VERSION,'synthetic':True,'observations':len(results),'cases':summary,
                              'all_expected_matched':all(r['matched'] for r in results),'no_engine_or_real_site_assessment':True})
    package.seal(output);package.inventory(output)
    return {'observations':len(results),'all_expected_matched':all(r['matched'] for r in results)}


def replay_delivery(folder):
    folder=Path(folder);package.inventory(folder);actual=analyze(folder/'source',tsep.read_json(folder/'observations.json'))
    stored=tsep.read_json(folder/'results.json')
    tsep.require([{k:v for k,v in r.items() if k!='input'} for r in actual]==stored['cases'], 'Recomputed laboratory results differ')
    for row in actual:
        tsep.require(tsep.read_json(folder/row['id']/'input.json')==row['input'], 'Derived input differs')
        report=tsep.read_json(folder/row['id']/'bundle/report.json');tsep.validate(report,folder/row['id']/'bundle')
        tsep.require(tsep.read_json(folder/row['id']/'bundle/assessment.json')==row['atomic_results'],'Native results differ')
    return {'same_results':True,'observations':len(actual),'network_requests':0,'browser_executed':False}


def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
    serve=sub.add_parser('serve');serve.add_argument('--output',required=True)
    serve.add_argument('--origin-host', choices=['isolated-localhost','127.0.0.1'], default='isolated-localhost')
    plan=sub.add_parser('seal');plan.add_argument('source');plan.add_argument('--browser-name',required=True);plan.add_argument('--browser-version',required=True)
    done=sub.add_parser('finish');done.add_argument('source');done.add_argument('--observations',required=True);done.add_argument('--output',required=True)
    check=sub.add_parser('replay');check.add_argument('folder');args=parser.parse_args()
    try:
        if args.command=='serve':
            server,record=start(args.output,args.origin_host);print(json.dumps({'ready':True,'calibration_url':record['base']+'/calibrate'}),flush=True)
            try:server.serve_forever()
            except KeyboardInterrupt:pass
            finally:
                server.server_close();folder=Path(args.output)
                save(folder/'closed.json',{'closed_at':now(),'source_files':sources(),'plan_sha256':tsep.digest(folder/'plan.json') if (folder/'plan.json').exists() else None,'log_sha256':tsep.digest(folder/'requests.jsonl')})
            return 0
        result=seal(args.source,args.browser_name,args.browser_version) if args.command=='seal' else finish(args.source,args.observations,args.output) if args.command=='finish' else replay_delivery(args.folder)
        print(json.dumps(result));return 0
    except (ValueError,KeyError,TypeError,OSError) as error:print(str(error),file=sys.stderr);return 64


if __name__=='__main__':sys.exit(main())
