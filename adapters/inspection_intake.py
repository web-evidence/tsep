#!/usr/bin/env python3
"""Prepare native TS08 inputs and blank reviews, then build a replayable bundle.

Apache-2.0. Offline only; never creates owner decisions or human reviews.
"""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
from pathlib import Path, PurePosixPath
import re
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import tsep
from adapters import captures
from adapters.package import MAX_PACKAGE_BYTES, json_bytes, regular, publish
from conformance import inspection
from conformance.agent_policy import digest
from diagnostics import search_console

VERSION = '2'
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


def checked_input(root):
    """Check the complete intake and parse the same bounded bytes we hash."""
    tsep.require(root.is_dir() and not root.is_symlink(), 'Expected a regular intake directory')
    meta=tsep.parse_json(regular(root/'intake.json',tsep.MAX_JSON_BYTES))
    tsep.require(isinstance(meta,dict) and meta.get('kind')=='tsep-inspection-intake'
                 and meta.get('version')==VERSION,'Unsupported intake version; explicitly prepare a new v2 intake')
    declared=meta.get('files')
    required={'plan.json','input.json','review-request.json'}
    tsep.require(isinstance(declared,dict) and required <= set(declared) and len(declared)<=67,
                 'Incomplete or excessive intake inventory')
    files={};total=0
    for name,want in declared.items():
        p=PurePosixPath(name)
        tsep.require(p.as_posix()==name and not p.is_absolute() and '..' not in p.parts
                     and '\\' not in name and (name in required or re.fullmatch(
                         r'originals/(?:[1-9]|1[0-6])/(?:manifest\.json|request\.json|response\.json|change-evidence\.txt)',name)),
                     'Unsafe or unsupported intake file path')
        tsep.require(isinstance(want,str) and re.fullmatch('[a-f0-9]{64}',want), 'Invalid intake file digest')
        files[name]=regular(tsep.evidence_path(root,name),tsep.MAX_JSON_BYTES)
        total+=len(files[name])
        tsep.require(total<=MAX_PACKAGE_BYTES,'Intake exceeds package byte bound')
        tsep.require(hashlib.sha256(files[name]).hexdigest()==want,'Changed intake file: '+name)
    found=set()
    for index,path in enumerate(root.rglob('*')):
        tsep.require(index<100 and not path.is_symlink(),'Unexpected intake entry or symlink')
        if path.is_file():found.add(path.relative_to(root).as_posix())
        else:tsep.require(path.is_dir(),'Unexpected intake entry')
    tsep.require(found==set(files)|{'intake.json'},'Unlisted or missing intake files')
    actual_hash=hashlib.sha256(files['input.json']).hexdigest()
    tsep.require(meta.get('input_sha256')==actual_hash,'Intake binding differs from raw input bytes')
    data=tsep.parse_json(files['input.json'])
    tsep.require(isinstance(data,dict) and set(data)=={'input_version','rules','targets'}
                 and data['input_version']=='2' and data['rules']==RULES
                 and isinstance(data['targets'],list) and len(data['targets'])==1,'Unexpected intake input shape')
    target=data['targets'][0];plan=tsep.parse_json(files['plan.json'])
    tsep.require(isinstance(target,dict) and isinstance(plan,dict),'Missing intake target or plan')
    projected={k:v for k,v in target.items() if k not in ('observed_at','inspection_records')}
    tsep.require(projected=={k:v for k,v in plan.items() if k!='observed_at'},'Prepared input differs from original plan')
    records=target.get('inspection_records')
    tsep.require(isinstance(records,list) and 1<=len(records)<=16,'Missing bounded intake records')
    expected=set(required)
    for index,record in enumerate(records,1):
        prefix='originals/'+str(index)+'/'
        expected.update(prefix+name for name in ('manifest.json','request.json','response.json'))
        tsep.require(expected <= set(files),'Missing original intake files')
        native=tsep.parse_json(files[prefix+'manifest.json'])
        tsep.require(isinstance(native,dict) and isinstance(record,dict) and record.get('supplied_manifest')==native,
                     'Prepared record differs from original manifest')
        for key in ('request','response'):
            raw=files[prefix+key+'.json'];wanted={'raw_text':raw.decode('utf-8'),'sha256':hashlib.sha256(raw).hexdigest()}
            tsep.require(record.get(key)==wanted and native.get(key+'_sha256')==wanted['sha256'],
                         'Prepared record differs from original '+key+' bytes')
        for key in ('retrieved_at','provenance','description','http_status'):
            tsep.require(record.get(key)==native.get(key),'Prepared record differs from original '+key)
        request=tsep.parse_json(files[prefix+'request.json'])
        tsep.require(record.get('url')==search_console.check_request(request),'Prepared record URL differs from native request')
        if native.get('change') is not None:
            name=prefix+'change-evidence.txt';expected.add(name)
            tsep.require(isinstance(native['change'],dict) and name in files
                         and hashlib.sha256(files[name]).hexdigest()==native['change'].get('evidence_sha256'),
                         'Missing or changed original change evidence')
    tsep.require(set(files)==expected,'Unexpected original intake inventory')
    blank_request=tsep.parse_json(files['review-request.json'])
    tsep.require(isinstance(blank_request,dict) and blank_request.get('kind')=='tsep-inspection-review-request'
                 and blank_request.get('version')==VERSION and blank_request.get('input_sha256')==actual_hash
                 and blank_request.get('reviews')==[blank(target,r) for r in records],
                 'Changed blank intake review request')
    actual=dict(captures.source_files(),**{'adapters/inspection_intake.py':tsep.digest(Path(__file__))})
    tsep.require(meta['source_files']==actual,'Use the exact intake tools or prepare a separate explicit reassessment')
    return data,actual_hash


def build(prepared, reviews, output, assessor):
    data,input_hash=checked_input(Path(prepared))
    supplied=tsep.parse_json(regular(Path(reviews),tsep.MAX_JSON_BYTES))
    tsep.require(isinstance(supplied,dict) and supplied.get('kind')=='tsep-inspection-review-request' and supplied.get('version')==VERSION
        and supplied.get('input_sha256')==input_hash,'Reviews do not bind this intake input')
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
