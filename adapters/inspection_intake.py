#!/usr/bin/env python3
"""Prepare native TS08 inputs and blank reviews, then build a replayable bundle.

Apache-2.0. Offline only; never creates owner decisions or human reviews.
"""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import tsep
from adapters import captures
from adapters.package import json_bytes, regular, publish
from conformance import inspection
from conformance.agent_policy import digest
from diagnostics import search_console

VERSION = '1'
RULES = ['TS08-A01','TS08-A02','TS08-A03']


def blank(target, record):
    return {'url':record['url'], 'binding_sha256':digest({'url':target['url'],'intent':target['intent'],'record':record}),
            'reviewer':None,'assistance':None,'provenance':None,'observed_at':None,'reason':None,'complete':False,
            'claimed_verdict':None,'interpretation':'unknown','objective_relation':'undetermined','temporal_scope':None,
            'explanation':{'kind':None,'text':None},'decision':{'kind':None,'owner':None,'reason':None}}


def prepare(plan, directories, output):
    raw_plan=regular(Path(plan),tsep.MAX_JSON_BYTES)
    target=deepcopy(tsep.parse_json(raw_plan))
    tsep.require(isinstance(target,dict) and not any(k in target for k in ('inspection_records','inspection_reviews')),
                 'Supply a prior target plan without imported inspections/reviews')
    target['observed_at'] = datetime.now(timezone.utc).isoformat()
    p,_,_=inspection.header(target)
    records=[];files={'plan.json':raw_plan}
    for index,directory in enumerate(directories,1):
        meta,request,response,url,native=search_console.observation(Path(directory))
        rec={'url':url,'retrieved_at':meta['retrieved_at'],'provenance':meta['provenance'],
             'description':meta['description'],'http_status':meta['http_status'],'supplied_manifest':meta}
        for key in ('request','response'):
            raw=native[key+'.json']
            rec[key]={'raw_text':raw.decode('utf-8'),'sha256':hashlib.sha256(raw).hexdigest()}
        records.append(rec)
        for name,data in native.items():files['originals/'+str(index)+'/'+name]=data
    planned={m['url'] for m in p['members']}
    tsep.require(len(records)==len(planned) and {r['url'] for r in records}==planned,
                 'Import exactly one inspection per selected URL; no silent omission')
    target['inspection_records']=records
    data={'input_version':'2','rules':RULES,'targets':[target]}
    files['input.json']=json_bytes(data)
    files['review-request.json']=json_bytes({'kind':'tsep-inspection-review-request','version':VERSION,
        'input_sha256':hashlib.sha256(files['input.json']).hexdigest(),'reviews':[blank(target,r) for r in records],
        'instructions':'Blank request, not approval. Retain plan, populate genuine supplied decisions; never relabel authored reviews as human.'})
    files['intake.json']=json_bytes({'kind':'tsep-inspection-intake','version':VERSION,
        'input_sha256':hashlib.sha256(files['input.json']).hexdigest(),
        'source_files':dict(captures.source_files(),**{'adapters/inspection_intake.py':tsep.digest(Path(__file__))}),
        'files':{k:hashlib.sha256(v).hexdigest() for k,v in files.items()},'network_requests':0})
    with tempfile.TemporaryDirectory(prefix='tsep-inspection-intake-') as tmp:
        root=Path(tmp)
        for name,content in files.items():
            path=root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(content)
        publish(root,Path(output))
    return {'prepared':str(output),'members':len(records),'review_created':False,'network_requests':0}


def build(prepared, reviews, output, assessor):
    root=Path(prepared);meta=tsep.read_json(root/'intake.json')
    tsep.require(meta.get('kind')=='tsep-inspection-intake' and meta.get('version')==VERSION,'Unsupported intake version')
    for name,want in meta['files'].items():
        p=Path(name);tsep.require(not p.is_absolute() and '..' not in p.parts,'Unsafe intake file path')
        tsep.require(hashlib.sha256(regular(root/name,tsep.MAX_JSON_BYTES)).hexdigest()==want,'Changed intake file: '+name)
    actual=dict(captures.source_files(),**{'adapters/inspection_intake.py':tsep.digest(Path(__file__))})
    tsep.require(meta['source_files']==actual,'Use the exact intake tools or prepare a separate explicit reassessment')
    data=tsep.read_json(root/'input.json');supplied=tsep.read_json(reviews)
    tsep.require(supplied.get('kind')=='tsep-inspection-review-request' and supplied.get('version')==VERSION
        and supplied.get('input_sha256')==meta['input_sha256'],'Reviews do not bind this intake input')
    target=data['targets'][0];target['inspection_reviews']=supplied['reviews']
    # Record the actual new assessment time; earlier dossiers are never rewritten.
    target['observed_at'] = datetime.now(timezone.utc).isoformat()
    with tempfile.TemporaryDirectory(prefix='tsep-inspection-build-') as tmp:
        path=Path(tmp)/'input.json';path.write_bytes(json_bytes(data))
        return captures.build(path,Path(output),assessor=assessor,label='TS08 supplied inspection dossier',
            selection_method=target['intent']['inspection']['selection_method'],
            access='synthetic' if target['inspection_synthetic'] else 'restricted',mode='semiAuto')


def main():
    parser=argparse.ArgumentParser(description=__doc__);commands=parser.add_subparsers(dest='command',required=True)
    p=commands.add_parser('prepare');p.add_argument('plan');p.add_argument('--inspection',action='append',required=True);p.add_argument('--output',required=True)
    b=commands.add_parser('build');b.add_argument('prepared');b.add_argument('--reviews',required=True);b.add_argument('--output',required=True);b.add_argument('--assessor',required=True)
    a=parser.parse_args()
    print(json_bytes(prepare(a.plan,a.inspection,a.output) if a.command=='prepare' else build(a.prepared,a.reviews,a.output,a.assessor)).decode())


if __name__=='__main__':
    try:main()
    except (OSError,ValueError,KeyError,TypeError) as error:
        print(str(error),file=sys.stderr);sys.exit(1)
