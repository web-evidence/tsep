#!/usr/bin/env python3
"""Offline TS12 import of supplied native API/technical pieces and blank reviews.

Apache-2.0. No collection, account access or invented human qualification.
"""
import argparse
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import tsep
from adapters import captures, inspection_intake, intake_integrity
from adapters.package import regular, json_bytes, publish
from conformance import canonical_comparison as comparison

VERSION='2'
RULES=['TS12-A01','TS12-A02','TS12-A03']


def sources():
    return dict(captures.source_files(),**{name:tsep.digest(ROOT/name) for name in
                ('adapters/comparison_intake.py','adapters/inspection_intake.py','adapters/intake_integrity.py')})


def blank(target,record):
    documents=[d for d in target['documents'] if d['url']==record['url']]
    member=next(m for m in target['intent']['canonical_comparison']['members'] if m['url']==record['url'])
    names=['googleCanonical','userCanonical','http','html']+['dom:'+s['id'] for s in member.get('rendering',{}).get('required_states',[])]
    return {'url':record['url'],'binding_sha256':comparison.binding(target,record,documents[0] if len(documents)==1 else None),
        'reviewer':None,'assistance':None,'provenance':None,'observed_at':None,'reason':None,'complete':False,
        'claims':{name:{'state':'unknown','values':[]} for name in names},'interpretation':'unknown',
        'temporal_interpretation':'unknown','temporal_scope':None,'objective_relation':'undetermined','changes':None,
        'explanation':{'kind':None,'text':None},'decision':{'kind':None,'owner':None,'reason':None}}


def prepare(plan,inspections,documents,output):
    raw=regular(Path(documents),tsep.MAX_JSON_BYTES);docs=tsep.parse_json(raw)
    tsep.require(isinstance(docs,list),'Technical file must contain the supplied document list')
    with tempfile.TemporaryDirectory(prefix='tsep-comparison-import-') as tmp:
        root=Path(tmp);old=root/'native'
        inspection_intake.prepare(plan,inspections,old)
        data=tsep.read_json(old/'input.json');data['rules']=RULES;target=data['targets'][0]
        tsep.require(not any(k in target for k in ('comparison_reviews','documents')),'Supply prior plan without later technical captures/reviews')
        target['documents']=docs;comparison.header(target)
        target['observed_at']=datetime.now(timezone.utc).isoformat()
        meta=tsep.read_json(old/'intake.json')
        files={k:regular(old/k,tsep.MAX_JSON_BYTES) for k in meta['files'] if k not in ('input.json','review-request.json')}
        files['originals/technical.json']=raw;files['input.json']=json_bytes(data)
        files['review-request.json']=json_bytes({'kind':'tsep-comparison-review-request','version':VERSION,
            'input_sha256':hashlib.sha256(files['input.json']).hexdigest(),
            'reviews':[blank(target,r) for r in target['inspection_records']],
            'instructions':'Blank request only. Supply genuine reviews; authored exercises stay synthetic. No values or decisions inferred.'})
        files['intake.json']=json_bytes({'kind':'tsep-comparison-intake','version':VERSION,
            'input_sha256':hashlib.sha256(files['input.json']).hexdigest(),'source_files':sources(),
            'files':{k:hashlib.sha256(v).hexdigest() for k,v in files.items()},'network_requests':0})
        stage=root/'stage';stage.mkdir()
        for name,content in files.items():
            path=stage/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(content)
        publish(stage,Path(output))
    return {'prepared':str(output),'members':len(target['inspection_records']),'review_created':False,'network_requests':0}


def build(prepared,reviews,output,assessor):
    required={'plan.json','input.json','review-request.json','originals/technical.json'}
    files,input_hash=intake_integrity.read(prepared,'tsep-comparison-intake',VERSION,sources(),required,inspections=True)
    data,target=intake_integrity.target(files,RULES)
    plan=tsep.parse_json(files['plan.json']);documents=tsep.parse_json(files['originals/technical.json'])
    tsep.require(isinstance(plan,dict) and isinstance(documents,list),'Missing original plan or technical documents')
    projected={k:v for k,v in target.items() if k not in ('observed_at','inspection_records','documents')}
    tsep.require(projected=={k:v for k,v in plan.items() if k!='observed_at'} and target.get('documents')==documents,
                 'Prepared input differs from original plan or technical documents')
    records=target.get('inspection_records');native=intake_integrity.native_inspections(files,records)
    tsep.require(set(files)==required|native,'Unexpected original intake inventory')
    original=intake_integrity.request(files['review-request.json'],'tsep-comparison-review-request',VERSION,input_hash)
    tsep.require(original.get('reviews')==[blank(target,r) for r in records],'Changed blank intake review request')
    supplied=intake_integrity.supplied(reviews,'tsep-comparison-review-request',VERSION,input_hash)
    target=data['targets'][0];target['comparison_reviews']=supplied['reviews'];target['observed_at']=datetime.now(timezone.utc).isoformat()
    with tempfile.TemporaryDirectory(prefix='tsep-comparison-build-') as tmp:
        path=Path(tmp)/'input.json';path.write_bytes(json_bytes(data))
        return captures.build(path,Path(output),assessor=assessor,label='TS12 supplied canonical comparison dossier',
            selection_method=target['intent']['inspection']['selection_method'],
            access='synthetic' if target['inspection_synthetic'] else 'restricted',mode='semiAuto')


def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
    p=sub.add_parser('prepare');p.add_argument('plan');p.add_argument('--inspection',action='append',required=True)
    p.add_argument('--documents',required=True);p.add_argument('--output',required=True)
    b=sub.add_parser('build');b.add_argument('prepared');b.add_argument('--reviews',required=True);b.add_argument('--output',required=True);b.add_argument('--assessor',required=True)
    a=parser.parse_args();print(json_bytes(prepare(a.plan,a.inspection,a.documents,a.output) if a.command=='prepare' else build(a.prepared,a.reviews,a.output,a.assessor)).decode())


if __name__=='__main__':
    try:main()
    except (OSError,ValueError,KeyError,TypeError) as error:
        print(str(error),file=sys.stderr);sys.exit(1)
