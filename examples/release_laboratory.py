#!/usr/bin/env python3
"""TS41: actual bounded loopback HTTP, child processes and sandbox file deployment.

Apache-2.0. Fictional site, injected faults and authored reviews. Offline replay
never runs a supplied command, recollects HTTP or applies an artifact.
"""
import argparse
import copy
from datetime import datetime,timedelta,timezone
import hashlib
from http.server import BaseHTTPRequestHandler,HTTPServer
import json
import os
from pathlib import Path
import re
import socket
import socketserver
import subprocess
import sys
import tempfile
import threading
import time
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import tsep
from adapters import captures,replay as bundle_replay,package as packages
from collectors import ts01
from conformance import release_invariants as release
from conformance.evaluate import evaluate
from conformance.http import header_fields
from provenance.runtime import loaded_sources,runtime_identity

VERSION='1'
FIXTURE='tests/fixtures/release-laboratory-v1.json'
FREEZE='tests/fixtures/release-laboratory-v1.sha256'
RULES=['TS41-A01','TS41-A02','TS41-A03']
NATIVE=['TS01-A01','TS07-A01']
UA='TSEPReleaseTest/1.0'
ASSESSOR='Automated controlled release laboratory; no human review'
SELECTION='Six prefrozen fictional scenarios; actual loopback HTTP, Python exits and sandbox artifact actions'
SCOPE=('Actual local HTTP/process/file observations; synthetic site, faults and reviews. '
       'Only TS01-A01 and TS07-A01 are the underlying invariants, not whole controls. '
       'No real CI, production deployment, human approval, Edikka assessment or Google behavior.')


def now():return datetime.now(timezone.utc).isoformat()
def compact(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def sha(value):return hashlib.sha256(value.encode() if isinstance(value,str) else value).hexdigest()
def save(path,value):ts01.save(path,value)
def fixture():
    tsep.require(tsep.digest(ROOT/FIXTURE)==(ROOT/FREEZE).read_text().strip(),'Frozen release recipe mismatch')
    return tsep.read_json(ROOT/FIXTURE)
def sources():
    result=captures.source_files()
    result.update(loaded_sources(ROOT,{'examples/release_laboratory.py':sys.modules[__name__],
        'collectors/ts01.py':ts01,'adapters/replay.py':bundle_replay,'adapters/package.py':packages}))
    for name in (FIXTURE,FREEZE,'spec/protocol.json','schemas/report.schema.json'):result[name]=tsep.digest(ROOT/name)
    return result
def loopback(base):
    tsep.require(isinstance(base,str) and re.fullmatch(r'http://127\.0\.0\.1:[1-9][0-9]{0,4}',base)
                 and 0<urlsplit(base).port<=65535,'Only a numeric loopback origin is permitted')
    return urlsplit(base)
def environment():return {'PATH':os.defpath,'PYTHONUTF8':'1','PYTHONDONTWRITEBYTECODE':'1'}
def artifact(name):
    recipe=fixture();value=dict(recipe['artifacts'][name])
    value.update(bodies=recipe['bodies'],truncated_content_length_excess=recipe['truncated_content_length_excess'])
    return compact(value)+'\n'
def baseline():return artifact('baseline')
def decision(rows):
    outcomes={r['outcome'] for r in rows}
    return 'fail' if 'fail' in outcomes else 'pass' if outcomes=={'pass'} else 'inconclusive'
def worker_exit(rows,mode):
    value=decision(rows)
    return 0 if mode=='mask-unknown' and value=='inconclusive' else {'pass':0,'fail':1,'inconclusive':2}[value]
def review(binding,at,prior=False):
    value={'reviewer':'Fictional laboratory reviewer','assistance':'Authored automatically from the frozen controlled recipe',
           'reason':'Synthetic exercise only; no human review or authenticated production runner',
           'provenance':'synthetic-exercise','observed_at':at,'binding_sha256':binding,'complete':True,'judgment':'supported'}
    if not prior:value.update(population_complete=True,attribution_supported=True,clock_supported=True)
    return value


def native_plan(base,case,declared):
    loopback(base);url=base+'/'+case['id']+'/page'
    return {'url':url,'intent':{'declared_at':declared,'crawler':UA,'directive_crawler':'googlebot',
             'access_basis':'test-client-only','public_canonical':True,'indexing':'allow','following':'unspecified',
             'expected_final_url':url},
            'context':{'network':'Numeric 127.0.0.1 only; no DNS/proxy/external request',
             'bounds':'One GET per native process; 3 seconds, 16384 response bytes',
             'tool':'TSEP controlled release laboratory worker','tool_version':VERSION,
             'comparison':'Same URL/client and declared invariant; preview before application, active package after. Phase retained with each exchange.',
             'scope':SCOPE}}


def plans(base,declared,reviewed,start,end,launcher,source_files,runtime):
    result={}
    for case in fixture()['cases']:
        native=native_plan(base,case,declared)
        command={'argv':[launcher['python'],launcher['script'],'worker','--mode',case['worker_mode']],
                 'version':VERSION,'sha256':source_files['examples/release_laboratory.py'],
                 'environment':release.digest({'variables':environment(),'runtime':runtime})}
        p={'reader':release.READER,'window_start':start,'window_end':end,
           'population':[{'id':case['id'],'before_artifact':sha(baseline()),'candidate_artifact':sha(artifact(case['artifact']))}],
           'matrix':[{'id':key,'rule_id':rid,'target':native['url'],'intent_sha256':release.digest(native['intent']),
                      'context_sha256':release.digest(native['context'])} for key,rid in zip(('status','index'),NATIVE)],
           'command':command,'policy':copy.deepcopy(release.POLICY),
           'negative':{'id':'negative-'+case['id'],'artifact_sha256':sha(artifact('negative')),'required_failures':['index']}}
        t={'url':base+'/scope/'+case['id'],'intent':{'declared_at':declared,'release':p}}
        t['release_plan_review']=review(release.plan_binding(t),reviewed,prior=True)
        result[case['id']]={'native':native,'target':t}
    return result


class Server(HTTPServer):
    def server_bind(self):
        socketserver.TCPServer.server_bind(self)
        self.server_name,self.server_port=self.server_address


class Handler(BaseHTTPRequestHandler):
    protocol_version='HTTP/1.1'
    def setup(self):super().setup();self.connection.settimeout(3)
    def log_message(self,*args):pass
    def do_GET(self):
        s=self.server;job=s.job
        if (not job or self.path!='/'+job['case']+'/page' or len(s.records)>=16
            or self.headers.get('User-Agent')!=UA or self.headers.get('X-Lab-Run-ID')!=job['run_id']
            or self.headers.get('Authorization') or self.headers.get('Cookie')):
            s.scope_error='Unexpected or excessive release laboratory request';self.close_connection=True;return
        payload=Path(job['artifact_path']).read_bytes();package=tsep.parse_json(payload)
        surface=package['active' if job['phase']=='post' else 'preview'];body=package['bodies'][surface].encode()
        length=len(body)+(package['truncated_content_length_excess'] if surface=='truncated' else 0)
        request_id='release-request-'+str(len(s.records)+1)
        record={'request_id':request_id,'run_id':job['run_id'],'request_at':now(),'method':'GET',
                'url':s.base+self.path,'user_agent':UA,'peer_ip':self.client_address[0],'phase':job['phase'],
                'artifact_sha256':sha(payload),'status':200,'body_sha256':sha(body),
                'actual_body_bytes':len(body),'declared_content_length':length}
        s.records.append(record)
        self.send_response_only(200);self.send_header('Content-Type','text/html; charset=utf-8')
        self.send_header('Content-Length',str(length));self.send_header('X-Lab-Request-ID',request_id)
        self.send_header('X-Lab-Run-ID',job['run_id']);self.send_header('X-Lab-Phase',job['phase'])
        self.send_header('X-Lab-Artifact-SHA256',sha(payload));self.send_header('Connection','close')
        self.end_headers();self.wfile.write(body);self.close_connection=True


def fetch(base,case_id,run_id):
    parts=loopback(base)
    tsep.require(case_id in {c['id'] for c in fixture()['cases']} and
                 run_id in {case_id+'-'+p for p in ('negative','pre','post')},'Unplanned release request')
    path='/'+case_id+'/page'
    request='GET '+path+' HTTP/1.1\r\nHost: '+parts.netloc+'\r\nUser-Agent: '+UA+'\r\nX-Lab-Run-ID: '+run_id+'\r\nConnection: close\r\n\r\n'
    sent=now();deadline=time.monotonic()+3;parts_raw=[];size=0
    with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as client:
        client.settimeout(3);client.connect(('127.0.0.1',parts.port));peer=client.getpeername()[0]
        client.sendall(request.encode('ascii'))
        while True:
            remaining=deadline-time.monotonic();tsep.require(remaining>0,'Release response duration bound exceeded')
            client.settimeout(remaining);raw=client.recv(4096)
            if not raw:break
            size+=len(raw);tsep.require(size<=16384,'Release response byte bound exceeded');parts_raw.append(raw)
    raw=b''.join(parts_raw);first,headers,body=header_fields(raw)
    lengths=headers.get('content-length',[])
    complete=len(lengths)==1 and lengths[0].isdigit() and int(lengths[0])==len(body)
    return {'url':base+path,'complete':complete,'sent_at':sent,'received_at':now(),'peer_address':peer,
            'request':request,'response':raw.decode('utf-8'),
            'collection_note':'Complete response' if complete else 'Observed EOF before declared Content-Length; raw bytes retained'}


def worker(config,mode):
    """Fixed program only; not the command recorded inside an evidence bundle."""
    tsep.require(mode in ('strict','mask-unknown'),'Unknown worker mode')
    tsep.require(config['source_files']==sources(),'Worker source identity differs before collection')
    native=config['native'];case_id=config['case'];base=config['base'];loopback(base)
    expected=native_plan(base,{'id':case_id},native['intent']['declared_at'])
    tsep.require(native==expected,'Worker native plan differs before collection')
    hop=fetch(base,case_id,config['run_id']);save(Path('exchange.json'),hop)
    target=dict(copy.deepcopy(native),observed_at=now(),http=[hop])
    data={'input_version':'1','rules':list(NATIVE),'targets':[target]};save(Path('input.json'),data)
    rows=evaluate(data)
    save(Path('worker.json'),{'version':VERSION,'pid':os.getpid(),'source_files':sources(),
                            'runtime':runtime_identity(),'mode':mode,'network_requests':1})
    sys.stdout.write(compact(rows)+'\n');sys.stdout.flush();return worker_exit(rows,mode)


def run_process(folder,command,config,timeout=6):
    """Retain actual process output and failure receipts; argv is constructed locally."""
    folder.mkdir();save(folder/'job.json',config);started=now()
    process=subprocess.Popen(command['argv'],cwd=folder,env=environment(),stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    timed_out=False
    try:stdout,stderr=process.communicate((compact(config)+'\n').encode(),timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out=True;process.kill();stdout,stderr=process.communicate()
    ended=now();(folder/'stdout.json').write_bytes(stdout);(folder/'stderr.txt').write_bytes(stderr)
    actual={'pid':process.pid,'started_at':started,'ended_at':ended,'exit_code':process.returncode,
            'timed_out':timed_out,'command':copy.deepcopy(command),'stdout_sha256':sha(stdout),'stderr_sha256':sha(stderr)}
    save(folder/'process.json',actual)
    tsep.require(not timed_out and process.returncode in (0,1,2),'Native worker failed or timed out; original outputs retained')
    tsep.require(len(stdout)<=65536 and len(stderr)<=65536,'Excessive worker output')
    return actual


def append(path,value):
    with path.open('a',encoding='utf-8',newline='\n') as f:f.write(compact(value)+'\n');f.flush()
def replace_active(path,payload):
    temporary=path.with_suffix('.next')
    with temporary.open('xb') as f:f.write(payload)
    os.replace(temporary,path)
def actual_effect(path,payload,action):
    before=path.read_bytes();started=now()
    if action=='deployed':replace_active(path,payload)
    after=path.read_bytes()
    return {'started_at':started,'ended_at':now(),'before_json':before.decode(),'after_json':after.decode(),
            'before_sha256':sha(before),'after_sha256':sha(after),
            'operation':'atomic-replace' if action=='deployed' else 'explicit-hold-no-write'}
def emit_event(path,run_id,attempt,kind,artifact_sha):
    row={'id':run_id+'-'+kind,'attempt_id':attempt,'kind':kind,'at':now(),
         'artifact_sha256':artifact_sha,'run_id':run_id};append(path,row);return row


def execute_case(root,registration,case,server):
    folder=root/case['id'];active=folder/'active.json';plan=registration['plans'][case['id']]
    path=folder/'events.jsonl';effects=folder/'effects.jsonl';receipts=[]
    phases=['negative','pre'];index=0
    while index<len(phases):
        phase=phases[index];index+=1;run_id=case['id']+'-'+phase
        name='negative' if phase=='negative' else case['artifact'];artifact_path=root/'artifacts'/(name+'.json')
        payload=artifact_path.read_bytes();attempt='negative-'+case['id'] if phase=='negative' else case['id']
        server.job={'case':case['id'],'run_id':run_id,'phase':phase,
                    'artifact_path':str(active if phase=='post' else artifact_path)}
        trigger=emit_event(path,run_id,attempt,'trigger-'+phase,sha(payload))
        job={'base':registration['base'],'case':case['id'],'run_id':run_id,
             'native':plan['native'],'source_files':registration['source_files']}
        actual=run_process(folder/run_id,plan['target']['intent']['release']['command'],job)
        tsep.require(server.scope_error is None,server.scope_error or 'Release transport scope mismatch')
        native_raw=(folder/run_id/'input.json').read_text();stdout=(folder/run_id/'stdout.json').read_text()
        r={'id':run_id,'attempt_id':attempt,'phase':phase,'artifact_sha256':sha(payload),
           'trigger_event_id':trigger['id'],'started_at':actual['started_at'],'ended_at':actual['ended_at'],
           'complete':True,'command':actual['command'],'input_json':native_raw,'input_sha256':sha(native_raw),
           'stdout_json':stdout,'stdout_sha256':sha(stdout),'exit_code':actual['exit_code']}
        receipts.append(r);save(folder/run_id/'receipt.json',r)
        if phase=='negative':action='negative-held'
        elif phase=='pre':action='deployed' if actual['exit_code']==0 or case['ignore_pre_exit'] else 'blocked'
        else:action='post-accepted' if actual['exit_code']==0 else 'post-held'
        effect=actual_effect(active,payload,action)
        event=emit_event(path,run_id,attempt,action,sha(payload));effect.update(event_id=event['id'],run_id=run_id,action=action)
        append(effects,effect)
        if action=='deployed':phases.append('post')
    save(folder/'runs.json',receipts)
    return {'id':case['id'],'phases':phases}


def input_for(root,registration,case,receipt):
    folder=root/case['id'];t=copy.deepcopy(registration['plans'][case['id']]['target'])
    t.update(observed_at=receipt['assessed_at'],context={'network':'Controlled numeric loopback and local process/files only',
         'bounds':'Six prior scenarios; 16 GETs/processes, 3 seconds/16384 bytes per GET, 6 seconds per child',
         'tool':'TSEP controlled release laboratory','tool_version':VERSION,'scope':SCOPE},
         release_runs=tsep.read_json(folder/'runs.json'),release_events={'raw_jsonl':(folder/'events.jsonl').read_text(),
         'sha256':tsep.digest(folder/'events.jsonl'),'exported_at':receipt['exported_at']})
    t['release_review']=review(release.review_binding(t),receipt['synthetic_review_at'])
    return {'input_version':'1','rules':list(RULES),'targets':[t]}


def read_lines(path):return [tsep.parse_json(line.encode()) for line in path.read_text().splitlines()]
def expected_headers(body,package,phase,run_id,request_id):
    key=package['active' if phase=='post' else 'preview']
    return {'content-type':['text/html; charset=utf-8'],
            'content-length':[str(len(body.encode())+(package['truncated_content_length_excess'] if key=='truncated' else 0))],
            'x-lab-request-id':[request_id],'x-lab-run-id':[run_id],'x-lab-phase':[phase],
            'x-lab-artifact-sha256':[sha(compact(package)+'\n')],'connection':['close']}


def check_capture(root,registration,receipt):
    """Reconstruct attribution from retained bytes; never trust a summary alone."""
    recipe=fixture();base=registration['base'];parts=loopback(base)
    tsep.require(registration['kind']=='controlled-release-registration' and registration['version']==VERSION
                 and registration['synthetic'] is True and registration['recipe']==recipe,'Registration/recipe mismatch')
    tsep.require(registration['source_files']==sources(),'Laboratory source identity mismatch')
    launcher=registration['launcher']
    tsep.require(set(launcher)=={'python','script'} and all(isinstance(x,str) and Path(x).is_absolute() for x in launcher.values())
                 and Path(launcher['script']).name=='release_laboratory.py','Invalid supplied launcher identity')
    times=[tsep.timestamp(registration[k]) for k in ('declared_at','synthetic_plan_review_at','registered_at','window_start','window_end')]
    prior,reviewed,registered,start,end=times
    tsep.require(prior<=reviewed<=registered<=start<end and end-start==timedelta(seconds=recipe['window_seconds']),
                 'Registration chronology differs from prior fixed window')
    expected=plans(base,registration['declared_at'],registration['synthetic_plan_review_at'],
        registration['window_start'],registration['window_end'],launcher,registration['source_files'],registration['runtime'])
    tsep.require(expected==registration['plans'],'Registered native or release plans differ')
    for name in recipe['artifacts']:
        tsep.require((root/'artifacts'/(name+'.json')).read_text()==artifact(name),'Frozen artifact bytes differ')
    exported,reviewed,assessed=[tsep.timestamp(receipt[k]) for k in ('exported_at','synthetic_review_at','assessed_at')]
    tsep.require(end<=exported<=reviewed<=assessed and receipt['collection_complete'] is True,'Final receipt chronology/completion mismatch')
    logs=read_lines(root/'requests.jsonl');index=0;last=start;observed=[]
    tsep.require(len(logs)==recipe['max_requests'],'Unexpected or missing server requests')
    for case in recipe['cases']:
        folder=root/case['id'];runs=tsep.read_json(folder/'runs.json');events=read_lines(folder/'events.jsonl');effects=read_lines(folder/'effects.jsonl')
        tsep.require(len(runs)==case['requests'] and len(events)==2*len(runs) and len(effects)==len(runs),'Run/event/effect population differs')
        active=baseline();phases=['negative','pre'];plan=registration['plans'][case['id']]
        for i,r in enumerate(runs):
            tsep.require(i<len(phases),'Unexpected post execution')
            phase=phases[i];run_id=case['id']+'-'+phase;sub=folder/run_id
            artifact_name='negative' if phase=='negative' else case['artifact'];payload=artifact(artifact_name);package=json.loads(payload)
            before,after=tsep.timestamp(r['started_at']),tsep.timestamp(r['ended_at'])
            tsep.require(last<=before<=after<=end and (after-before).total_seconds()<=6,'Execution clock/window mismatch')
            tsep.require(r==tsep.read_json(sub/'receipt.json') and r['id']==run_id and r['phase']==phase
                         and r['artifact_sha256']==sha(payload) and r['complete'] is True,'Execution receipt identity mismatch')
            actual=tsep.read_json(sub/'process.json');worker_record=tsep.read_json(sub/'worker.json')
            tsep.require(type(actual['pid']) is int and actual['pid']>0 and actual['timed_out'] is False
                         and actual['pid']==worker_record['pid'] and worker_record['source_files']==registration['source_files']
                         and worker_record['runtime']==registration['runtime'] and worker_record['version']==VERSION
                         and worker_record['mode']==case['worker_mode'] and worker_record['network_requests']==1,
                         'Actual worker/process identity mismatch')
            command=plan['target']['intent']['release']['command']
            tsep.require(type(actual['exit_code']) is int and type(r['exit_code']) is int
                         and actual['command']==r['command']==command and actual['started_at']==r['started_at']
                         and actual['ended_at']==r['ended_at'] and actual['exit_code']==r['exit_code'], 'Process/receipt binding mismatch')
            job={'base':base,'case':case['id'],'run_id':run_id,'native':plan['native'],'source_files':registration['source_files']}
            tsep.require(tsep.read_json(sub/'job.json')==job,'Worker job differs from registration')
            raw_input=(sub/'input.json').read_text();raw_out=(sub/'stdout.json').read_text();stderr=(sub/'stderr.txt').read_bytes()
            tsep.require(r['input_json']==raw_input and r['input_sha256']==sha(raw_input)
                         and r['stdout_json']==raw_out and r['stdout_sha256']==actual['stdout_sha256']==sha(raw_out)
                         and actual['stderr_sha256']==sha(stderr) and not stderr,'Native bytes/process output binding mismatch')
            data=tsep.parse_json(raw_input.encode());hop=tsep.read_json(sub/'exchange.json')
            tsep.require(isinstance(data,dict) and isinstance(data.get('targets'),list)
                         and len(data['targets'])==1 and isinstance(data['targets'][0],dict),'Missing native target')
            target=data['targets'][0]
            expected_native=dict(copy.deepcopy(plan['native']),observed_at=target['observed_at'],http=[hop])
            tsep.require(data=={'input_version':'1','rules':list(NATIVE),'targets':[expected_native]},'Native input scope differs')
            sent,received,at=[tsep.timestamp(x) for x in (hop['sent_at'],hop['received_at'],target['observed_at'])]
            tsep.require(before<=sent<=received<=at<=after and (received-sent).total_seconds()<=3,'HTTP/process clock mismatch')
            request,headers,request_body=header_fields(hop['request']);first,response_headers,body_bytes=header_fields(hop['response'])
            surface=package['active' if phase=='post' else 'preview'];body=package['bodies'][surface]
            request_id='release-request-'+str(index+1)
            tsep.require(request=='GET /'+case['id']+'/page HTTP/1.1' and not request_body
                and headers=={'host':[parts.netloc],'user-agent':[UA],'x-lab-run-id':[run_id],'connection':['close']}
                and hop['peer_address']=='127.0.0.1' and hop['url']==plan['native']['url'],'HTTP request scope/peer mismatch')
            tsep.require(first=='HTTP/1.1 200 OK' and body_bytes==body.encode()
                and response_headers==expected_headers(body,package,phase,run_id,request_id)
                and hop['complete']==(surface!='truncated') and len(hop['response'].encode())<=16384,
                'Observed HTTP body/header/completeness differs from frozen package')
            record=logs[index];index+=1
            wanted={'request_id':request_id,'run_id':run_id,'request_at':record['request_at'],'method':'GET',
                    'url':hop['url'],'user_agent':UA,'peer_ip':'127.0.0.1','phase':phase,'artifact_sha256':sha(payload),
                    'status':200,'body_sha256':sha(body),'actual_body_bytes':len(body.encode()),
                    'declared_content_length':int(response_headers['content-length'][0])}
            tsep.require(record==wanted and sent<=tsep.timestamp(record['request_at'])<=received,'Native server-log binding mismatch')
            calculated=evaluate(data);supplied=tsep.parse_json(raw_out.encode())
            tsep.require(supplied==calculated and r['exit_code']==worker_exit(calculated,case['worker_mode']),
                         'Worker result/exit differs from retained bytes and pinned program')
            attempt='negative-'+case['id'] if phase=='negative' else case['id'];trigger,action=events[2*i:2*i+2]
            kind=('negative-held' if phase=='negative' else
                  ('deployed' if r['exit_code']==0 or case['ignore_pre_exit'] else 'blocked') if phase=='pre' else
                  ('post-accepted' if r['exit_code']==0 else 'post-held'))
            for event,wanted_kind in ((trigger,'trigger-'+phase),(action,kind)):
                tsep.require(event=={'id':run_id+'-'+wanted_kind,'attempt_id':attempt,'kind':wanted_kind,'at':event['at'],
                                    'artifact_sha256':sha(payload),'run_id':run_id},'Event action/attribution differs')
            tsep.require(r['attempt_id']==attempt and r['trigger_event_id']==trigger['id']
                         and last<=tsep.timestamp(trigger['at'])<=before,'Execution trigger mismatch')
            effect=effects[i];next_active=payload if kind=='deployed' else active
            effect_start,effect_end=tsep.timestamp(effect['started_at']),tsep.timestamp(effect['ended_at'])
            tsep.require(after<=effect_start<=effect_end<=tsep.timestamp(action['at'])<=end,'Artifact action chronology mismatch')
            tsep.require(effect=={'started_at':effect['started_at'],'ended_at':effect['ended_at'],
                'before_json':active,'after_json':next_active,'before_sha256':sha(active),'after_sha256':sha(next_active),
                'operation':'atomic-replace' if kind=='deployed' else 'explicit-hold-no-write','event_id':action['id'],
                'run_id':run_id,'action':kind},'Observed artifact action or snapshot differs')
            if phase=='post':tsep.require(active==payload,'Post execution not tied to applied artifact')
            active=next_active;last=tsep.timestamp(action['at'])
            if kind=='deployed':phases.append('post')
        tsep.require((folder/'active.json').read_text()==active,'Final active artifact differs from observed actions')
        observed.append({'id':case['id'],'phases':phases})
    tsep.require(index==len(logs)==recipe['max_requests'],'Unexpected or missing server requests')
    tsep.require(tsep.read_json(root/'executions.json')==observed,'Execution inventory differs')


def result_row(root,case):
    folder=root/case['id'];data=tsep.read_json(folder/'bundle/assessment.json');report=tsep.read_json(folder/'bundle/report.json')
    runs=tsep.read_json(folder/'runs.json');actions=[r['kind'] for r in read_lines(folder/'events.jsonl') if not r['kind'].startswith('trigger-')]
    actual={'atomic_outcomes':[r['outcome'] for r in data],'control_status':report['results'][0]['status'],
            'decisions':[decision(tsep.parse_json(r['stdout_json'].encode())) for r in runs],
            'exits':[r['exit_code'] for r in runs],'actions':actions}
    expected={'atomic_outcomes':case['expected_atomic_outcomes'],'control_status':case['expected_control_status'],
              'decisions':case['expected_decisions'],'exits':case['expected_exits'],'actions':case['expected_actions']}
    return {'id':case['id'],'actual':actual,'expected':expected,'matches_expectations':actual==expected,
            'report':case['id']+'/bundle/report.json','input':case['id']+'/input.json'}
def summary(registration,rows):
    return {'kind':'controlled-release-laboratory','version':VERSION,'scope':SCOPE,
            'source_files':registration['source_files'],'runtime':registration['runtime'],
            'protocol_version':tsep.read_json(ROOT/'spec/protocol.json')['version'],
            'registered_at':registration['registered_at'],'actual_http_requests':sum(len(r['actual']['exits']) for r in rows),
            'actual_processes':sum(len(r['actual']['exits']) for r in rows),'cases':rows,
            'all_expectations_matched':all(r['matches_expectations'] for r in rows),
            'human_review_performed':False,'production_deployed':False,'edikka_assessed':False}


def names(registration):
    result=['registration.json','requests.jsonl','receipt.json','executions.json','results.json']
    result+=['artifacts/'+name+'.json' for name in fixture()['artifacts']]
    for case in fixture()['cases']:
        result+=[case['id']+'/'+name for name in ('active.json','runs.json','events.jsonl','effects.jsonl','input.json','bundle/SHA256SUMS')]
        for phase in (('negative','pre','post') if case['requests']==3 else ('negative','pre')):
            result+=[case['id']+'/'+case['id']+'-'+phase+'/'+name for name in
                     ('job.json','exchange.json','input.json','worker.json','process.json','stdout.json','stderr.txt','receipt.json')]
    return result


def closed_files(root,inventory):
    """Known nested bundles are sealed separately; no other file may hide outside."""
    allowed=set(inventory)|{'SHA256SUMS'}
    for case in fixture()['cases']:
        prefix=case['id']+'/bundle/'
        allowed.update(prefix+name for name in packages.inventory(root/case['id']/'bundle'))
    directories={str(parent) for name in allowed for parent in Path(name).parents if str(parent)!='.'}
    found=set()
    for count,path in enumerate(root.rglob('*')):
        tsep.require(count<5000 and not path.is_symlink(),'Excessive entries or unsupported laboratory symlink')
        name=path.relative_to(root).as_posix()
        if path.is_file():found.add(name)
        else:tsep.require(path.is_dir() and name in directories,'Unlisted laboratory directory')
    tsep.require(found==allowed,'Unlisted or missing laboratory files')


def run(output):
    before=sources();recipe=fixture();root=ts01.new_directory(output);records=[];executions=[];server=None;thread=None
    try:
        (root/'artifacts').mkdir()
        for name in recipe['artifacts']:(root/'artifacts'/(name+'.json')).write_text(artifact(name),encoding='utf-8')
        for case in recipe['cases']:
            folder=root/case['id'];folder.mkdir();(folder/'active.json').write_text(baseline(),encoding='utf-8')
            (folder/'events.jsonl').touch();(folder/'effects.jsonl').touch()
        server=Server(('127.0.0.1',0),Handler);server.base='http://127.0.0.1:'+str(server.server_port)
        server.records=records;server.scope_error=None;server.job=None
        declared,reviewed=now(),now();start=(datetime.now(timezone.utc)+timedelta(seconds=1)).isoformat()
        end=(tsep.timestamp(start)+timedelta(seconds=recipe['window_seconds'])).isoformat()
        runtime=runtime_identity();launcher={'python':sys.executable,'script':str(ROOT/'examples/release_laboratory.py')}
        registration={'kind':'controlled-release-registration','version':VERSION,'synthetic':True,
            'declared_at':declared,'synthetic_plan_review_at':reviewed,'registered_at':now(),
            'window_start':start,'window_end':end,'base':server.base,'launcher':launcher,
            'source_files':before,'runtime':runtime,'recipe':recipe,
            'plans':plans(server.base,declared,reviewed,start,end,launcher,before,runtime)}
        save(root/'registration.json',registration)
        tsep.require(datetime.now(timezone.utc)<=tsep.timestamp(start),'Plan could not be retained before window')
        time.sleep(max(0,(tsep.timestamp(start)-datetime.now(timezone.utc)).total_seconds()))
        thread=threading.Thread(target=server.serve_forever,kwargs={'poll_interval':0.01},daemon=True);thread.start()
        for case in recipe['cases']:executions.append(execute_case(root,registration,case,server))
        tsep.require(before==sources(),'Laboratory sources changed during collection')
        remaining=(tsep.timestamp(end)-datetime.now(timezone.utc)).total_seconds()
        tsep.require(remaining>=0,'Collection exceeded the prior fixed window')
        if remaining>0:time.sleep(remaining)
    except Exception as error:
        save(root/'failure.json',{'at':now(),'phase':'collection','type':type(error).__name__,
                                'error':str(error),'collection_complete':False});raise
    finally:
        if thread is not None:server.shutdown();thread.join(timeout=4)
        if server is not None:server.server_close()
        (root/'requests.jsonl').write_text(''.join(compact(r)+'\n' for r in records),encoding='utf-8')
        save(root/'executions.json',executions)
    receipt={'exported_at':now(),'synthetic_review_at':now(),'assessed_at':now(),'collection_complete':True}
    save(root/'receipt.json',receipt)
    try:
        check_capture(root,registration,receipt);rows=[]
        for case in recipe['cases']:
            folder=root/case['id'];save(folder/'input.json',input_for(root,registration,case,receipt))
            captures.build(folder/'input.json',folder/'bundle',assessor=ASSESSOR,
                label='SYNTHETIC SITE / actual local HTTP-process-artifact actions / TS41 '+case['id'],
                selection_method=SELECTION,access='synthetic',mode='semiAuto')
            rows.append(result_row(root,case))
        result=summary(registration,rows);save(root/'results.json',result)
        tsep.require(before==sources(),'Laboratory sources changed during interpretation')
        ts01.manifest(root,names(registration));closed_files(root,ts01.verify(root));return result
    except Exception as error:
        save(root/'failure.json',{'at':now(),'phase':'interpretation','type':type(error).__name__,
                                'error':str(error),'collection_complete':True});raise


def replay(root):
    root=Path(root);before=sources();inventory=ts01.verify(root);registration=tsep.read_json(root/'registration.json')
    tsep.require(set(inventory)==set(names(registration)),'Incomplete release laboratory manifest')
    closed_files(root,inventory)
    receipt=tsep.read_json(root/'receipt.json');check_capture(root,registration,receipt);rows=[]
    for case in fixture()['cases']:
        folder=root/case['id'];expected=input_for(root,registration,case,receipt)
        tsep.require(expected==tsep.read_json(folder/'input.json')==tsep.read_json(folder/'bundle/input.json'),
                     'Laboratory/native input binding differs')
        report=tsep.read_json(folder/'bundle/report.json')
        tsep.require(report['assessor']=={'name':ASSESSOR,'mode':'semiAuto','tool':{'name':captures.NAME,'version':captures.VERSION}}
            and report['scope']=={'label':'SYNTHETIC SITE / actual local HTTP-process-artifact actions / TS41 '+case['id'],
            'targets':[expected['targets'][0]['url']],'selection_method':SELECTION,'exclusions':[]}
            and all(a['access']=='synthetic' for a in report['artifacts']),'Synthetic laboratory report identity differs')
        with tempfile.TemporaryDirectory() as tmp:bundle_replay.replay(folder/'bundle',Path(tmp)/'replay')
        rows.append(result_row(root,case))
    tsep.require(summary(registration,rows)==tsep.read_json(root/'results.json'),'Replayed release results differ')
    tsep.require(before==sources(),'Laboratory sources changed during replay')
    return {'kind':'controlled-release-offline-replay','version':VERSION,'cases':6,'network_requests':0,'processes_executed':0,
            'artifact_applications':0,'same_observations_and_results':True,
            'all_expectations_matched':all(r['matches_expectations'] for r in rows),'scope':SCOPE,'source_files':before}


def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
    create=sub.add_parser('run');create.add_argument('--output',type=Path,required=True)
    repeat=sub.add_parser('replay');repeat.add_argument('laboratory',type=Path);repeat.add_argument('--output',type=Path,required=True)
    child=sub.add_parser('worker');child.add_argument('--mode',choices=('strict','mask-unknown'),required=True)
    args=parser.parse_args()
    try:
        if args.command=='worker':return worker(tsep.parse_json(sys.stdin.buffer.read(512*1024+1)),args.mode)
        if args.command=='run':result=run(args.output)
        else:
            tsep.require(not args.output.exists() and not args.output.is_symlink(),'Choose a NEW replay output')
            result=replay(args.laboratory);save(args.output,result)
        print(json.dumps({k:v for k,v in result.items() if k not in ('source_files','runtime')},ensure_ascii=False))
        return 0 if result['all_expectations_matched'] else 2
    except (ValueError,OSError,KeyError,TypeError) as error:
        print(str(error),file=sys.stderr);return 64 if args.command=='worker' else 1


if __name__=='__main__':raise SystemExit(main())
