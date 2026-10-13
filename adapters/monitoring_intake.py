#!/usr/bin/env python3
"""TS36 offline intake, stage reviews, separate closure request. Apache-2.0."""
import argparse
from copy import deepcopy
from datetime import datetime,timezone
import hashlib
from pathlib import Path
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import tsep
from adapters import captures,intake_integrity
from adapters.package import regular,publish,json_bytes
from conformance import release_monitoring as monitoring

VERSION='2'
RULES=['TS36-A01','TS36-A02','TS36-A03']

def metadata():return {'reviewer':None,'assistance':None,'provenance':None,'observed_at':None,'reason':None,'complete':False}
def tools():return dict(captures.source_files(),**{name:tsep.digest(ROOT/name) for name in ('adapters/monitoring_intake.py','adapters/intake_integrity.py')})
def blank(target,name):
    rows=[c for c in target.get('monitoring_checkpoints',[]) if isinstance(c,dict) and c.get('id')==name]
    cp=rows[0] if len(rows)==1 else None
    return dict(metadata(),id=name,binding_sha256=monitoring.stage_binding(target,cp),claims={'api':{m['url']:None for m in target['intent']['inspection']['members']},'logs':{m['url']:{'requests':None,'server_errors':None} for m in target['intent']['inspection']['members']}},interpretation='unknown',anomalies='unknown',log_completeness='unknown',clock_scope='unknown',objective_relation=None,temporal_scope=None,explanation={'kind':None,'text':None},decision={'kind':None,'owner':None,'reason':None})
def write_new(files,output):
    with tempfile.TemporaryDirectory(prefix='tsep-monitoring-intake-') as tmp:
        root=Path(tmp)
        for name,data in files.items():
            p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
        publish(root,Path(output))

def prepare(plan,evidence,output):
    raw_plan=regular(Path(plan),tsep.MAX_JSON_BYTES);raw_evidence=regular(Path(evidence),tsep.MAX_JSON_BYTES)
    t=deepcopy(tsep.parse_json(raw_plan));pieces=tsep.parse_json(raw_evidence)
    tsep.require(isinstance(t,dict) and not any(k in t for k in ('monitoring_deployment','monitoring_checkpoints','monitoring_reviews','monitoring_closure_review')),'Prior plan must not contain acquired observations or final reviews')
    tsep.require(isinstance(pieces,dict) and set(pieces)<={'monitoring_deployment','monitoring_checkpoints'},'Evidence contains foreign fields or supplied final reviews')
    t.update(pieces);t['observed_at']=datetime.now(timezone.utc).isoformat();monitoring.header(t)
    data={'input_version':'2','rules':RULES,'targets':[t]};raw_input=json_bytes(data)
    files={'originals/plan.json':raw_plan,'originals/evidence.json':raw_evidence,'input.json':raw_input}
    files['review-request.json']=json_bytes({'kind':'tsep-monitoring-stage-reviews','version':VERSION,'input_sha256':hashlib.sha256(raw_input).hexdigest(),'reviews':[blank(t,n) for n in monitoring.STAGES],'instructions':'Blank request only; no review or decision supplied. Missing/future checkpoints remain unknown. Request a separate closure after supplying stage reviews.'})
    files['intake.json']=json_bytes({'kind':'tsep-monitoring-intake','version':VERSION,'input_sha256':hashlib.sha256(raw_input).hexdigest(),'source_files':tools(),'files':{n:hashlib.sha256(v).hexdigest() for n,v in files.items()},'network_requests':0})
    write_new(files,output);return {'prepared':str(output),'review_created':False,'network_requests':0}

def load(prepared,reviews):
    required={'originals/plan.json','originals/evidence.json','input.json','review-request.json'}
    files,input_hash=intake_integrity.read(prepared,'tsep-monitoring-intake',VERSION,tools(),required)
    data,target=intake_integrity.target(files,RULES)
    plan=tsep.parse_json(files['originals/plan.json']);evidence=tsep.parse_json(files['originals/evidence.json'])
    tsep.require(isinstance(plan,dict) and isinstance(evidence,dict)
                 and set(evidence)<={'monitoring_deployment','monitoring_checkpoints'},'Unexpected original plan or evidence')
    expected=dict(plan,**evidence)
    tsep.require({k:v for k,v in target.items() if k!='observed_at'}=={k:v for k,v in expected.items() if k!='observed_at'},
                 'Prepared input differs from original plan or evidence')
    original=intake_integrity.request(files['review-request.json'],'tsep-monitoring-stage-reviews',VERSION,input_hash)
    tsep.require(original.get('reviews')==[blank(target,n) for n in monitoring.STAGES],'Changed blank stage review request')
    q=intake_integrity.supplied(reviews,'tsep-monitoring-stage-reviews',VERSION,input_hash)
    target['monitoring_reviews']=q['reviews'];return data,{'input_sha256':input_hash}

def closure_request(prepared,reviews,output):
    data,meta=load(prepared,reviews);t=data['targets'][0]
    q=dict(metadata(),binding_sha256=monitoring.closure_binding(t),completed=None,causality=None)
    files={'closure-request.json':json_bytes({'kind':'tsep-monitoring-closure-review','version':VERSION,'input_sha256':meta['input_sha256'],'review':q,'instructions':'Blank closure bound to the exact supplied stage reviews. No completion, identity, causal attribution or signature inferred.'})}
    write_new(files,output);return {'prepared':str(output),'closure_created':False,'network_requests':0}

def build(prepared,reviews,output,assessor,closure=None):
    data,meta=load(prepared,reviews);t=data['targets'][0]
    if closure:
        q=intake_integrity.supplied(closure,'tsep-monitoring-closure-review',VERSION,meta['input_sha256'])
        t['monitoring_closure_review']=q['review']
    t['observed_at']=datetime.now(timezone.utc).isoformat()
    with tempfile.TemporaryDirectory(prefix='tsep-monitoring-build-') as tmp:
        p=Path(tmp)/'input.json';p.write_bytes(json_bytes(data))
        return captures.build(p,Path(output),assessor=assessor,label='TS36 supplied release follow-up dossier',selection_method=t['intent']['inspection']['selection_method'],access='synthetic' if t['inspection_synthetic'] else 'restricted',mode='semiAuto')

def main():
    p=argparse.ArgumentParser(description=__doc__);cmd=p.add_subparsers(dest='command',required=True)
    a=cmd.add_parser('prepare');a.add_argument('plan');a.add_argument('--evidence',required=True);a.add_argument('--output',required=True)
    a=cmd.add_parser('closure-request');a.add_argument('prepared');a.add_argument('--reviews',required=True);a.add_argument('--output',required=True)
    a=cmd.add_parser('build');a.add_argument('prepared');a.add_argument('--reviews',required=True);a.add_argument('--closure');a.add_argument('--output',required=True);a.add_argument('--assessor',required=True)
    a=p.parse_args()
    r=prepare(a.plan,a.evidence,a.output) if a.command=='prepare' else closure_request(a.prepared,a.reviews,a.output) if a.command=='closure-request' else build(a.prepared,a.reviews,a.output,a.assessor,a.closure)
    print(json_bytes(r).decode())
if __name__=='__main__':
    try:main()
    except (OSError,ValueError,KeyError,TypeError) as e:print(str(e),file=sys.stderr);sys.exit(1)
