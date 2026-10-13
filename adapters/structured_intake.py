#!/usr/bin/env python3
"""Offline TS31 intake with blank reviews and immutable supplied content. Apache-2.0."""
import argparse
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import tsep
from adapters import captures
from adapters.package import regular, json_bytes, publish
from conformance import structured_content as control

VERSION='1'


def sources():
    return dict(captures.source_files(),**{'adapters/structured_intake.py':tsep.digest(ROOT/'adapters/structured_intake.py')})


def blank(binding, **extra):
    return dict(binding_sha256=binding,complete=False,reviewer=None,assistance=None,
                provenance=None,reason=None,observed_at=None,**extra)


def plan_request(plan, output):
    """May run before the capture window; produces no assessed target or verdict."""
    t=tsep.parse_json(regular(Path(plan),tsep.MAX_JSON_BYTES))
    result=dict(kind='tsep-structured-plan-review-request',version=VERSION,
        review=blank(control.plan_binding(t),scope='unknown',source_base='unknown',guidance='unknown'),
        instructions='Supply a genuine prior review before acquisition. This template is not a review; never backdate a later judgment.')
    with tempfile.TemporaryDirectory(prefix='tsep-structured-plan-') as tmp:
        stage=Path(tmp)/'stage';stage.mkdir();(stage/'plan-review-request.json').write_bytes(json_bytes(result));publish(stage,Path(output))
    return dict(prepared=str(output),review_created=False)


def requests(t):
    notes={};e=control.Evidence(t,notes);records=[];unavailable=[]
    for s in e.surfaces():
        try:
            outcome,reason,_=e.qualify(s)
            if outcome!='pass':raise ValueError(reason)
            if s['reading']['status']=='absent':continue
            graph=s['processing']['flattened']
        except control.ERRORS as error:
            unavailable.append(dict(surface_id=s['id'],reason=str(error)));continue
        candidates=[r for r in t.get('structured_reviews',[]) if r.get('surface_id')==s['id']]
        tsep.require(len(candidates)<=1,'Duplicate content surface')
        content=candidates[0].get('content') if candidates else None
        records.append(dict(surface_id=s['id'],content=content,
            review=blank(control.content_binding(t,s['id'],content,graph),coverage='unknown'),
            entities=[dict(index=i,node_sha256=control.digest(node),**{
                key:dict(value='unknown',reason=None) for key in control.JUDGMENTS}) for i,node in enumerate(graph)]))
    return records,unavailable,notes


def prepare(input_path, output, plan_review=None):
    raw=regular(Path(input_path),tsep.MAX_JSON_BYTES);t=tsep.parse_json(raw)
    control.header(t)
    records=t.get('structured_reviews',[])
    tsep.require(type(records) is list and all(type(r) is dict and set(r)=={'surface_id','content'} for r in records),
                 'Supply content-only structured_reviews; later judgments belong in the separate review file')
    if plan_review is not None:
        p=tsep.parse_json(regular(Path(plan_review),tsep.MAX_JSON_BYTES))
        tsep.require(p.get('kind')=='tsep-structured-plan-review-request' and p.get('version')==VERSION,'Unsupported plan review file')
        tsep.require('structured_plan_review' not in t,'Prior review already supplied in target')
        t['structured_plan_review']=p['review']
    source=sources();reviews,unavailable,notes=requests(t)
    data=dict(input_version='2',rules=list(control.RULES),targets=[t]);input_bytes=json_bytes(data)
    files={'originals/target.json':raw,'input.json':input_bytes,
        'review-request.json':json_bytes(dict(kind='tsep-structured-review-request',version=VERSION,
            input_sha256=hashlib.sha256(input_bytes).hexdigest(),reviews=reviews,unavailable_surfaces=unavailable,
            instructions='Blank supplied-review request only. Keep content unchanged. Missing content requires a new intake. Supply all node judgments and reasons; no factual judgment is inferred.'))}
    if plan_review is not None:files['originals/plan-review.json']=regular(Path(plan_review),tsep.MAX_JSON_BYTES)
    tsep.require(sources()==source,'Intake sources changed during preparation')
    files['intake.json']=json_bytes(dict(kind='tsep-structured-intake',version=VERSION,source_files=source,
        input_sha256=hashlib.sha256(input_bytes).hexdigest(),files={k:hashlib.sha256(v).hexdigest() for k,v in files.items()},network_requests=0))
    with tempfile.TemporaryDirectory(prefix='tsep-structured-intake-') as tmp:
        stage=Path(tmp)/'stage';stage.mkdir()
        for name,value in files.items():
            path=stage/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(value)
        publish(stage,Path(output))
    return dict(prepared=str(output),surfaces=len(reviews),unavailable_surfaces=unavailable,review_created=False,network_requests=0)


def build(prepared, reviews, output, assessor):
    root=Path(prepared);meta=tsep.read_json(root/'intake.json')
    tsep.require(meta.get('kind')=='tsep-structured-intake' and meta.get('version')==VERSION,'Unsupported structured intake')
    mandatory={'originals/target.json','input.json','review-request.json'}
    tsep.require(mandatory<=set(meta['files'])<=mandatory|{'originals/plan-review.json'},'Unexpected intake inventory')
    for name,want in meta['files'].items():
        tsep.require(hashlib.sha256(regular(root/name,tsep.MAX_JSON_BYTES)).hexdigest()==want,'Changed intake file: '+name)
    tsep.require(meta['source_files']==sources(),'Use exact intake tools or prepare an explicit new assessment')
    data=tsep.read_json(root/'input.json');supplied=tsep.read_json(reviews);original=tsep.read_json(root/'review-request.json')
    tsep.require(supplied.get('kind')=='tsep-structured-review-request' and supplied.get('version')==VERSION
        and supplied.get('input_sha256')==meta['input_sha256'],'Review file does not bind intake input')
    t=data['targets'][0];given=supplied['reviews'];expected=original['reviews']
    control.population(given,'surface_id',[r['surface_id'] for r in expected])
    for r in given:
        base=control.one(expected,'surface_id',r['surface_id'])
        tsep.require(r.get('content')==base['content'],'Content changed in review file; prepare a new intake')
        tsep.require(r.get('review',{}).get('binding_sha256')==base['review']['binding_sha256'],'Review binding changed')
    t['structured_reviews']=given;t['observed_at']=datetime.now(timezone.utc).isoformat()
    with tempfile.TemporaryDirectory(prefix='tsep-structured-build-') as tmp:
        p=Path(tmp)/'input.json';p.write_bytes(json_bytes(data))
        return captures.build(p,Path(output),assessor=assessor,label='TS31 supplied JSON-LD/content dossier',
            selection_method=t['intent']['structured_content']['selection_reason'],
            access='synthetic' if t['structured_synthetic'] else 'restricted',mode='semiAuto')


def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
    p=sub.add_parser('plan');p.add_argument('target');p.add_argument('--output',required=True)
    p=sub.add_parser('prepare');p.add_argument('target');p.add_argument('--plan-review');p.add_argument('--output',required=True)
    p=sub.add_parser('build');p.add_argument('prepared');p.add_argument('--reviews',required=True);p.add_argument('--output',required=True);p.add_argument('--assessor',required=True)
    a=parser.parse_args()
    result=plan_request(a.target,a.output) if a.command=='plan' else prepare(a.target,a.output,a.plan_review) if a.command=='prepare' else build(a.prepared,a.reviews,a.output,a.assessor)
    print(json_bytes(result).decode())


if __name__=='__main__':
    try:main()
    except (OSError,ValueError,KeyError,TypeError) as error:
        print(str(error),file=sys.stderr);sys.exit(1)
