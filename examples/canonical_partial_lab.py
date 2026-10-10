#!/usr/bin/env python3
"""SYNTHETIC canonical family: fixed intent, partial repairs, actual browser/HTTP capture."""
import argparse
import hashlib
import html
import json
from pathlib import Path
import secrets
import shutil
import sys
import tempfile
import threading
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import tsep
from adapters import captures, package, replay, review
from conformance.evaluate import binding_digest, evaluate, trace
from conformance.http import encoded, header_fields
from examples import same_navigation_lab as transport
from experiments import rendered_metadata as metadata
from provenance.runtime import loaded_sources

VERSION = '1'
RECIPE = 'tests/fixtures/canonical-partial-repair-v1.json'
PAGE = 'examples/canonical_partial_page.js'
save, now, logs, wire = transport.save, transport.now, transport.logs, transport.wire


def sources():
    result = dict(transport.sources(), **loaded_sources(ROOT, {
        'examples/canonical_partial_lab.py': sys.modules[__name__], 'adapters/review.py': review}))
    for name in (RECIPE, RECIPE.replace('.json', '.sha256'), PAGE):
        result[name] = tsep.digest(ROOT / name)
    return result


def recipe():
    path = ROOT / RECIPE
    tsep.require(tsep.digest(path) == path.with_suffix('.sha256').read_text().split()[0], 'Changed frozen family recipe')
    return tsep.read_json(path)


def urls(server):
    return {role: server['base'] + path for role, path in recipe()['paths'].items()}


def page(task, server):
    locations = urls(server)
    canonical = locations['variant'] if task['role'] == 'variant' and 'canonical' in task['faults'] else locations['preferred']
    link = locations['variant'] if 'links' in task['faults'] else locations['preferred']
    script = (ROOT / PAGE).read_text()
    values = {'__SITEMAP__': locations['sitemap'] if task['role'] == 'catalog' else None,
              '__CONTEXT__': server['token'], '__TASK__': task['id'], '__NAVIGATION__': task['navigation_id'],
              '__SCRIPT_SHA__': metadata.script_digest(), '__ENDPOINT__': server['base'] + '/capture'}
    for key, value in values.items():
        script = script.replace(key, json.dumps(value))
    script = script.replace('__CAPTURE_EXPRESSION__', (ROOT / metadata.SCRIPT).read_text().strip())
    title = html.escape(task['phase'] + ' · ' + task['role'])
    return ('<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>TSEP · '+title+'</title>'
        '<link rel="icon" href="data:,"><link rel="canonical" href="'+html.escape(canonical, quote=True)+'">'
        '<style>body{font:18px/1.6 system-ui;background:#102032;color:#edf3f8;max-width:1000px;margin:40px auto;padding:20px}h1{font-size:34px}span{overflow-wrap:anywhere}a{color:#9ed8ff}</style>'
        '</head><body><p>LABORATOIRE SYNTHÉTIQUE · FAMILLE FIXE</p><h1>'+title+'</h1>'
        '<p>Produit de démonstration : lampe Atelier, modèle A, finition bleue. Le catalogue présente ce même modèle.</p>'
        '<p>Navigation : <span id="lab-navigation">'+task['navigation_id']+'</span></p>'
        '<p>État : <span id="lab-state">pending</span></p><p>Reçu : <span id="lab-receipt">pending</span></p>'
        '<p>Sitemap : <span id="lab-sitemap">'+('pending' if task['role']=='catalog' else 'not-requested')+'</span></p>'
        '<p>Page locale de test ; aucune observation Googlebot ou correction Edikka.</p>'+
        ('<a href="'+html.escape(link, quote=True)+'">Voir la lampe Atelier</a>' if task['role']=='catalog' else '')+
        '<script>'+script+'</script></body></html>')


def planned_responses(task, server):
    locations = urls(server)
    result = []
    if task['role'] == 'preferred' and 'destination' in task['faults']:
        result.append((locations['preferred'], wire(b'', status=302, extra='Location: '+locations['landing']+'\r\n')))
    result.append((task['final_url'], wire(page(task, server))))
    if task['role'] == 'catalog':
        locs = [locations['preferred']] + ([locations['variant']] if 'sitemap' in task['faults'] else [])
        xml = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        xml += ''.join('<url><loc>'+html.escape(u)+'</loc></url>' for u in locs) + '</urlset>'
        result.append((locations['sitemap'], wire(xml, 'application/xml; charset=utf-8')))
    return result


def registration(server, agent, browser, calibration_id, registered_at):
    spec = recipe(); locations = urls(server); tasks = []
    render_plan = {'mode':'required', 'dom_reader':spec['profiles']['dom'], 'required_states':[
        {'id':'load-state', 'interactions':[], 'wait':spec['acquisition']['render_wait']}]}
    intent = {'declared_at':registered_at, 'crawler':agent, 'canonical':{
        'preferred_url':locations['preferred'], 'source_reader':spec['profiles']['canonical_source'],
        'members':[{'url':locations[r], 'required_methods':['html','dom'], 'rendering':render_plan} for r in ['preferred','variant']],
        'sitemaps':{'mode':'required','roots':[locations['sitemap']],'require_preferred':True,'exceptions':[]},
        'links':{'source_reader':spec['profiles']['links_source'],
                 'sources':[{'url':locations['catalog'],'rendering':render_plan}],'exceptions':[]}}}
    for phase in spec['phases']:
        for role in spec['roles']:
            task_id = phase['id']+'-'+role
            final = locations['landing'] if role=='preferred' and 'destination' in phase['faults'] else locations[role]
            task = {'id':task_id,'phase':phase['id'],'role':role,'faults':phase['faults'],
                    'navigation_id':server['token']+'-'+task_id,'url':locations[role],'final_url':final}
            task['responses'] = [{'url':u,'path':'planned/'+task_id+'-'+str(i)+'.bin',
                                  'sha256':hashlib.sha256(raw).hexdigest()}
                                 for i,(u,raw) in enumerate(planned_responses(task,server))]
            tasks.append(task)
    return {'kind':'canonical-family-plan','version':VERSION,'registered_at':registered_at,'server':server,
            'source_files':sources(),'recipe':spec,'agent':agent,'browser':browser,'calibration_id':calibration_id,
            'intent':intent,'tasks':tasks}


def decode(raw):
    tsep.require(len(raw) <= transport.MAX_BODY, 'POST byte bound')
    envelope = json.loads(raw)
    tsep.require(set(envelope)=={'payload','sha256'} and isinstance(envelope['payload'],str) and
                 hashlib.sha256(envelope['payload'].encode()).hexdigest()==envelope['sha256'], 'POST digest mismatch')
    data = json.loads(envelope['payload'])
    tsep.require(data['kind']=='canonical-family-page' and data['version']==VERSION and
                 data['script_sha256']==metadata.script_digest(), 'Unsupported family export')
    metadata.inventory(data['tree'])
    return data


def navigation_witness(tree, expected):
    """Check the phase witness INSIDE the retained tree, not only its envelope."""
    nodes=tree['nodes']
    witnesses=[n for n in nodes if n['type']==1 and n['namespace']==metadata.HTML and
               any(a['namespace'] is None and a['name']=='id' and a['value']=='lab-navigation'
                   for a in n['attributes'])]
    tsep.require(len(witnesses)==1 and witnesses[0]['name']=='span', 'Missing/duplicate DOM navigation witness')
    children=[n for n in nodes if n['parent']==witnesses[0]['id'] and n['edge']=='child']
    tsep.require(len(children)==1 and children[0]['type']==3 and children[0]['data']==expected,
                 'DOM navigation witness differs from registered phase')


class Handler(transport.Handler):
    def dispatch(self, method, url, agent, body):
        server, folder = self.server.record, self.server.folder
        if method=='GET' and url==server['base']+'/calibrate':
            tsep.require(not (folder/'plan.json').exists(), 'Calibration already sealed')
            return wire('<html><head><title>TSEP calibration</title><link rel="icon" href="data:,"></head><body>'
                        '<h1>Calibration avant mesure</h1><p>Agent reçu : '+html.escape(agent)+'</p></body></html>'), {'kind':'calibration'}
        if method=='GET' and url==server['origin']+'/favicon.ico':
            return wire(b'',status=204), {'kind':'browser-favicon'}
        plan = tsep.read_json(folder/'plan.json')
        tsep.require(plan['source_files']==sources(), 'Family tools changed')
        tsep.require(agent==plan['agent'], 'Client changed after calibration')
        with self.server.lock:
            tsep.require(self.server.cursor<len(plan['tasks']), 'Completed family sequence cannot be repeated')
            task = plan['tasks'][self.server.cursor]
            if method=='GET':
                tsep.require(self.server.step<len(task['responses']), 'Export required before next navigation')
                expected = task['responses'][self.server.step]
                tsep.require(url==expected['url'], 'Out-of-order family request')
                raw = package.regular(folder/expected['path'])
                tsep.require(hashlib.sha256(raw).hexdigest()==expected['sha256'], 'Planned family response changed')
                index = self.server.step; self.server.step += 1
                return raw, {'kind':'sitemap' if task['role']=='catalog' and index==1 else 'navigation',
                             'task_id':task['id'],'navigation_id':task['navigation_id'],'response_index':index}
            tsep.require(url==server['base']+'/capture' and self.server.step==len(task['responses']), 'Incomplete task before export')
            data = decode(body)
            tsep.require(data['context']==server['token'] and data['task_id']==task['id'] and
                         data['navigation_id']==task['navigation_id'] and data['url']==task['final_url'] and
                         data['tree']['document_url']==task['final_url'] and data['user_agent']==agent, 'Family export attribution mismatch')
            receipt = hashlib.sha256(body).hexdigest()
            self.server.cursor += 1; self.server.step = 0
            return wire(json.dumps({'receipt':receipt}),'application/json'), {
                'kind':'capture','task_id':task['id'],'navigation_id':task['navigation_id'],'receipt':receipt}


def start(output, origin_host='isolated-localhost'):
    tsep.require(origin_host in ('isolated-localhost','127.0.0.1'), 'Unsupported loopback origin')
    recipe(); folder=Path(output)
    tsep.require(not folder.exists() and folder.parent.is_dir(), 'Choose a new capture directory')
    folder.mkdir(); server=transport.Server(('127.0.0.1',0),Handler); token=secrets.token_hex(8)
    host=token+'.localhost' if origin_host=='isolated-localhost' else origin_host
    origin='http://'+host+':'+str(server.server_address[1])
    record={'kind':'canonical-family-server','version':VERSION,'created_at':now(),'origin':origin,
            'token':token,'base':origin+'/'+token,'source_files':sources()}
    save(folder/'server.json',record); (folder/'requests.jsonl').touch()
    server.record=record;server.folder=folder;server.lock=threading.Lock();server.sequence=0;server.cursor=0;server.step=0
    return server,record


def empty_connection(row, folder):
    """Retain an idle/closed TCP connection separately from actual HTTP attempts."""
    if row.get('peer')!='127.0.0.1' or row.get('error') not in ('timed out','Incomplete/excessive HTTP header'):
        return False
    if any(k in row for k in ('method','url','user_agent','kind','task_id','navigation_id')):
        return False
    request=package.regular(Path(folder)/(row['id']+'-request.bin'))
    response=package.regular(Path(folder)/(row['id']+'-response.bin'))
    expected=wire(json.dumps({'error':row['error']}),'application/json',400)
    return (request==b'' and response==expected and
            hashlib.sha256(request).hexdigest()==row['request_sha256'] and
            hashlib.sha256(response).hexdigest()==row['response_sha256'])


def seal(folder,browser_name,browser_version):
    folder=Path(folder);server=tsep.read_json(folder/'server.json');rows=logs(folder)
    calibration=[r for r in rows if r.get('kind')=='calibration']
    tsep.require(server['source_files']==sources(), 'Tools changed before sealing')
    tsep.require(len(calibration)==1 and all((r['complete'] and r.get('kind') in ('calibration','browser-favicon')) or empty_connection(r,folder) for r in rows), 'One calibration and no prior controls required')
    tsep.require(not calibration[0].get('conditional_or_session'), 'Session/conditional calibration refused')
    tsep.require(browser_name.strip() and browser_version.strip(), 'Declared browser identity required')
    plan=registration(server,calibration[0]['user_agent'],{'name':browser_name,'version':browser_version},calibration[0]['id'],now())
    (folder/'planned').mkdir()
    for task in plan['tasks']:
        for record,(_,raw) in zip(task['responses'],planned_responses(task,server)):
            (folder/record['path']).write_bytes(raw)
    save(folder/'plan.json',plan);return plan


def close_record(folder):
    folder=Path(folder)
    save(folder/'closed.json',{'closed_at':now(),'source_files':sources(),
        'plan_sha256':tsep.digest(folder/'plan.json') if (folder/'plan.json').exists() else None,
        'log_sha256':tsep.digest(folder/'requests.jsonl')})


def analyze(folder, observations):
    """Validate retained acquisition and derive inputs; no evaluation or browser execution."""
    folder=Path(folder);server=tsep.read_json(folder/'server.json');plan=tsep.read_json(folder/'plan.json');closed=tsep.read_json(folder/'closed.json')
    origin=urlsplit(server['origin'])
    tsep.require(server['kind']=='canonical-family-server' and server['version']==VERSION and
                 origin.scheme=='http' and origin.hostname in ('127.0.0.1',server['token']+'.localhost') and
                 origin.port and server['base']==server['origin']+'/'+server['token'], 'Unsupported family server record')
    tsep.require(server['source_files']==plan['source_files']==closed['source_files']==sources(), 'Changed family tools')
    tsep.require(plan==registration(server,plan['agent'],plan['browser'],plan['calibration_id'],plan['registered_at']), 'Changed frozen family registration')
    tsep.require(closed['plan_sha256']==tsep.digest(folder/'plan.json') and closed['log_sha256']==tsep.digest(folder/'requests.jsonl'), 'Changed closed family campaign')
    tsep.require(set(observations)=={t['id'] for t in plan['tasks']}, 'Incomplete family observation inventory')
    rows=logs(folder);used=set();expected_files={'server.json','plan.json','closed.json','requests.jsonl'}
    expected_files.update(r['path'] for t in plan['tasks'] for r in t['responses'])
    expected_files.update(r['id']+'-'+kind+'.bin' for r in rows for kind in ('request','response'))
    paths=list(folder.rglob('*'))
    tsep.require(not any(p.is_symlink() for p in paths), 'Family source symlink refused')
    tsep.require({p.relative_to(folder).as_posix() for p in paths if p.is_file()}==expected_files, 'Unlisted/missing family source files')
    for row in rows:
        empty=empty_connection(row,folder)
        tsep.require(empty or (row['complete'] and row['peer']=='127.0.0.1' and 'error' not in row and not row.get('conditional_or_session')), 'Failed/session/nonlocal family request retained')
        for kind in ('request','response'):
            tsep.require(tsep.digest(folder/(row['id']+'-'+kind+'.bin'))==row[kind+'_sha256'], 'Changed family HTTP sidecar')
        if empty or row.get('kind') in ('calibration','browser-favicon'):used.add(row['id'])
    calibration=[r for r in rows if r.get('kind')=='calibration']
    tsep.require(len(calibration)==1 and calibration[0]['id']==plan['calibration_id'] and calibration[0]['user_agent']==plan['agent'] and
                 tsep.timestamp(calibration[0]['finished_at'])<=tsep.timestamp(plan['registered_at']), 'Invalid family calibration')
    collected={}; previous=plan['registered_at']
    for task in plan['tasks']:
        task_rows=[r for r in rows if r.get('task_id')==task['id']]
        gets=sorted([r for r in task_rows if r.get('kind') in ('navigation','sitemap')],key=lambda r:r['response_index'])
        posts=[r for r in task_rows if r.get('kind')=='capture']
        tsep.require(len(gets)==len(task['responses']) and len(posts)==1 and len(task_rows)==len(gets)+1, 'Missing/duplicate family request')
        post=posts[0];observation=observations[task['id']]
        _,_,body=header_fields((folder/(post['id']+'-request.bin')).read_bytes());data=decode(body)
        tsep.require(hashlib.sha256(body).hexdigest()==post['receipt']==observation['receipt'], 'Family receipt mismatch')
        tsep.require(data['context']==server['token'] and data['task_id']==task['id'] and data['navigation_id']==task['navigation_id'] and
                     data['url']==data['tree']['document_url']==task['final_url'], 'Family identity mismatch')
        navigation_witness(data['tree'],task['navigation_id'])
        tsep.require(all(r['user_agent']==plan['agent'] and r['navigation_id']==task['navigation_id'] for r in task_rows) and
                     data['user_agent']==plan['agent'], 'Family agent/navigation mismatch')
        dates=[previous,observation['navigation_started_at']]+[r['response_started_at'] for r in gets]+[
            data['capture_started_at'],data['captured_at'],post['response_started_at'],observation['observed_at'],closed['closed_at']]
        tsep.require(all(tsep.timestamp(a)<=tsep.timestamp(b) for a,b in zip(dates,dates[1:])), 'Family navigation chronology mismatch')
        previous=observation['observed_at'];hops=[];sitemap=None
        for index,(row,registered,(url,expected_raw)) in enumerate(zip(gets,task['responses'],planned_responses(task,server))):
            raw=(folder/(row['id']+'-response.bin')).read_bytes()
            tsep.require(row['response_index']==index and row['url']==registered['url']==url and raw==expected_raw==package.regular(folder/registered['path']) and
                         hashlib.sha256(raw).hexdigest()==registered['sha256'], 'Family response differs from frozen plan')
            hop={'url':url,'complete':True,'request':encoded((folder/(row['id']+'-request.bin')).read_bytes()),'response':encoded(raw)}
            expected_kind='sitemap' if task['role']=='catalog' and index==1 else 'navigation'
            tsep.require(row['kind']==expected_kind, 'Changed family request role')
            if expected_kind=='sitemap':
                _,status,_,xml=trace([hop],url,plan['agent'])
                tsep.require(data['auxiliary']=={'url':url,'status':status,'body_sha256':hashlib.sha256(xml).hexdigest()}, 'Sitemap fetch/body attribution mismatch')
                sitemap={'url':url,'observed_at':row['response_started_at'],'context_id':server['token'],'http':[hop]}
            else:hops.append(hop)
        if sitemap is None:tsep.require(data['auxiliary'] is None, 'Unplanned auxiliary fetch')
        final,_,_,_=trace(hops,task['url'],plan['agent']);tsep.require(final==task['final_url'], 'Unexpected final navigation URL')
        support=json.dumps({'GETs':gets,'POST':post,'operator':observation,'plan_sha256':tsep.digest(folder/'plan.json')},sort_keys=True)
        snapshot={'script_sha256':data['script_sha256'],'tree':data['tree']}
        structured={'snapshot':snapshot,'snapshot_sha256':binding_digest(snapshot),'known_integrity_issues':[],
            'acquisition':{'kind':'same-navigation','navigation_id':task['navigation_id'],'user_agent':plan['agent'],
            'http_sha256':binding_digest(hops),'support':[{'name':'Synthetic family laboratory navigation receipt','content':support,'sha256':hashlib.sha256(support.encode()).hexdigest()}]}}
        state={'id':'load-state','interactions':[],'wait':plan['recipe']['acquisition']['render_wait'],
               'url':final,'context_id':server['token'],'source_http_sha256':binding_digest(hops),'observed_at':data['captured_at'],
               'complete':data['tree']['traversal_complete'],'javascript_enabled':True,'errors':data['errors'],'structured_dom':structured}
        doc={'url':task['url'],'observed_at':gets[0]['response_started_at'],'context_id':server['token'],'http':hops,'render':{'browser':plan['browser'],'states':[state]}}
        collected[task['id']]={'document':doc,'sitemap':sitemap,'observed_at':observation['observed_at'],'receipt':post['receipt']}
        used.update(r['id'] for r in task_rows)
    tsep.require(len(used)==len(rows), 'Unmatched family request; do not resample or hide attempts')
    results=[]
    for phase in plan['recipe']['phases']:
        parts={r:collected[phase['id']+'-'+r] for r in plan['recipe']['roles']}
        target={'url':plan['intent']['canonical']['preferred_url'],'observed_at':parts['catalog']['observed_at'],
            'context':{'id':server['token'],'network':'synthetic loopback browser laboratory',
                'bounds':'one fixed family; three HTML navigations and one XML fetch per phase; inventory 2 limits',
                'tool':'TSEP canonical partial repair laboratory','tool_version':VERSION},'intent':plan['intent'],
            'documents':[parts[r]['document'] for r in ['preferred','variant']],
            'crawl':{'documents':[parts['catalog']['document']]},'sitemaps':{'documents':[parts['catalog']['sitemap']]}}
        results.append({'id':phase['id'],'expected':phase['expected'],'expected_control':phase['expected_control'],
                        'input':{'input_version':'2','rules':plan['recipe']['rules'],'targets':[target]},
                        'receipts':{r:parts[r]['receipt'] for r in parts}})
    return results


def finish(source, observation_file, output):
    source,output=Path(source),Path(output);observations=tsep.read_json(observation_file);rows=analyze(source,observations)
    tsep.require(not output.exists() and output.parent.is_dir(), 'Choose a new family delivery directory')
    output.mkdir();shutil.copytree(source,output/'source');shutil.copyfile(observation_file,output/'observations.json');summary=[]
    for row in rows:
        folder=output/row['id'];folder.mkdir();save(folder/'input.json',row['input'])
        captures.build(folder/'input.json',folder/'bundle',assessor='Automated family import; no human review',
            label='SYNTHETIC partial repair — '+row['id'],selection_method='One predeclared family and phase; actual browser/HTTP capture',access='synthetic',mode='automatic')
        replay.replay(folder/'bundle',folder/'replay')
        actual=tsep.read_json(folder/'bundle/assessment.json');report=tsep.read_json(folder/'bundle/report.json')
        controls=[c['status'] for c in report['results'] if c['control_id']=='TS10']
        summary.append({k:v for k,v in row.items() if k!='input'} | {'actual':actual,'control_status':controls,
            'matched':[r['outcome'] for r in actual]==row['expected'] and controls==[row['expected_control']]})
    review.prepare(output/rows[-1]['id']/'bundle',output/'blank-review')
    final_target=rows[-1]['input']['targets'][0];pieces=[]
    for document in final_target['documents']:
        final,_,_,body=trace(document['http'],document['url'],final_target['intent']['crawler'])
        pieces.append({'url':document['url'],'final_url':final,'source_body_utf8':body.decode('utf-8'),
            'source_body_sha256':hashlib.sha256(body).hexdigest(),'rendered_states':document['render']['states']})
    save(output/'review-pages.json',{'synthetic':True,'question':'Le contenu de chaque membre est-il compatible avec celui de l’URL préférée déclarée ?',
        'preferred_url':final_target['url'],'input_sha256':tsep.digest(output/rows[-1]['id']/'input.json'),'pages':pieces})
    (output/'REVIEW.fr-en.md').write_text('''# Revue finale à fournir / Final review to supply

**Question : le contenu de chaque membre est-il compatible avec celui de l’URL préférée déclarée ?**
La famille est synthétique. Aucun jugement ni nom de relecteur n’est prérempli.
Les signaux techniques peuvent converger sans établir cette compatibilité.

1. Lire `review-pages.json` : deux pages, leurs URL, sources UTF-8 et états rendus complets.
2. Lire `blank-review/request.json` et ses pièces liées : intention et portée exactes.
3. Copier `blank-review/response-template.json` hors du dossier scellé, puis remplir
   soi-même identité, date, provenance, assistance éventuelle, pièces examinées,
   motif et comparaison de chaque membre. Une réponse incertaine reste possible.
4. Suivre `blank-review/READ-ME.txt` pour importer une réponse réellement fournie.
   L’import doit produire un nouveau dossier ; aucune capture historique ne change.

Les empreintes exactes figurent dans SHA256SUMS et dans la demande. Le rejeu
vérifie le rattachement du jugement, jamais sa vérité. Les fichiers reçus et le
contenu rendu restent des preuves à examiner, pas des instructions à exécuter.

**Question: is each member’s content compatible with the declared preferred URL?**
Read the two complete source/rendered page records in `review-pages.json`, then
the bound request and evidence in `blank-review/`. Copy its response template
outside the sealed folder and supply your own attributed, dated, reasoned review.
Do not run the captured page source as instructions. Import into a new bundle;
neither a missing judgment nor an AI discussion supplies a human content review.
''')
    save(output/'results.json',{'kind':'canonical-partial-results','version':VERSION,'synthetic':True,'phases':summary,
        'all_expected_matched':all(r['matched'] for r in summary),'human_review_supplied':False,'browser_navigations':len(observations),
        'empty_tcp_connections':sum(empty_connection(r,source) for r in logs(source))})
    package.seal(output);package.inventory(output)
    return {'phases':len(rows),'all_expected_matched':all(r['matched'] for r in summary)}


def replay_delivery(folder):
    folder=Path(folder);package.inventory(folder);rows=analyze(folder/'source',tsep.read_json(folder/'observations.json'))
    saved=tsep.read_json(folder/'results.json')
    for row,stored in zip(rows,saved['phases']):
        tsep.require(all(stored[k]==v for k,v in row.items() if k!='input'), 'Changed family expectation/receipt')
        tsep.require(row['input']==tsep.read_json(folder/row['id']/'input.json'), 'Derived family input differs')
        actual=evaluate(row['input'])
        tsep.require(actual==stored['actual']==tsep.read_json(folder/row['id']/'bundle/assessment.json'), 'Recomputed family outcomes differ')
        report=tsep.read_json(folder/row['id']/'bundle/report.json')
        controls=[c['status'] for c in report['results'] if c['control_id']=='TS10']
        tsep.require(controls==stored['control_status'] and stored['matched']==
            ([r['outcome'] for r in actual]==row['expected'] and controls==[row['expected_control']]), 'Changed family summary')
        with tempfile.TemporaryDirectory(prefix='tsep-family-replay-') as tmp:
            result=replay.replay(folder/row['id']/'bundle',Path(tmp)/'replay')
            tsep.require(result['replayed'], 'Family bundle replay mismatch')
    tsep.require(len(rows)==len(saved['phases']), 'Changed phase population')
    tsep.require(saved['empty_tcp_connections']==sum(empty_connection(r,folder/'source') for r in logs(folder/'source')), 'Changed empty connection count')
    tsep.require(saved['all_expected_matched']==all(r['matched'] for r in saved['phases']) and
                 saved['human_review_supplied'] is False and saved['browser_navigations']==len(tsep.read_json(folder/'observations.json')),
                 'Changed family coverage summary')
    return {'same_results':True,'phases':len(rows),'network_requests':0,'browser_executed':False}


def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
    serve=sub.add_parser('serve');serve.add_argument('--output',required=True)
    serve.add_argument('--origin-host',choices=['isolated-localhost','127.0.0.1'],default='isolated-localhost')
    plan=sub.add_parser('seal');plan.add_argument('source');plan.add_argument('--browser-name',required=True);plan.add_argument('--browser-version',required=True)
    done=sub.add_parser('finish');done.add_argument('source');done.add_argument('--observations',required=True);done.add_argument('--output',required=True)
    check=sub.add_parser('replay');check.add_argument('folder');args=parser.parse_args()
    try:
        if args.command=='serve':
            server,record=start(args.output,args.origin_host);print(json.dumps({'ready':True,'calibration_url':record['base']+'/calibrate'}),flush=True)
            try:server.serve_forever()
            except KeyboardInterrupt:pass
            finally:server.server_close();close_record(args.output)
            return 0
        result=seal(args.source,args.browser_name,args.browser_version) if args.command=='seal' else finish(args.source,args.observations,args.output) if args.command=='finish' else replay_delivery(args.folder)
        print(json.dumps(result));return 0
    except (ValueError,KeyError,TypeError,OSError) as error:print(str(error),file=sys.stderr);return 64


if __name__=='__main__':sys.exit(main())
