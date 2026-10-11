#!/usr/bin/env python3
"""Offline HTML JSON-LD observation under an explicit supplied-base hypothesis.

Apache-2.0. Preserves scripts and errors; never emits a TSEP/Google verdict.
"""
import argparse
import base64
import binascii
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from experiments import source_scripts as scripts
from experiments import jsonld_processing as processor

need,sha,serialized=processor.need,processor.sha,processor.serialized
MAX_INPUT=16*1024*1024
MAX_OUTPUT=64*1024*1024
PROFILE='html-jsonld-exact-type-all-supplied-base-v1'
ASCII_SPACE=' \t\n\r\f'


def identity(root=ROOT):
    return dict(scripts.identity(root),**processor.identity(root),
                **{'experiments/jsonld_html.py':sha((root/'experiments/jsonld_html.py').read_bytes())})


def prepare(request):
    need(type(request) is dict and set(request)=={'body_base64','content_types','base_iri','contexts'},'Unexpected HTML request')
    need(len(serialized(request))<=MAX_INPUT,'HTML request bound exceeded')
    need(type(request['body_base64']) is str,'Expected base64 body')
    try:raw=base64.b64decode(request['body_base64'],validate=True)
    except (ValueError,binascii.Error) as error:raise ValueError('Invalid base64 body') from error
    need(base64.b64encode(raw).decode()==request['body_base64'],'Noncanonical base64 body')
    scripts.http.decode(raw,request['content_types'])
    # Validate supplied base/contexts even when no eligible script exists.
    processor.prepare({'documents':[dict(id='preflight',base_iri=request['base_iri'],raw_json='{}',contexts=request['contexts'])]})
    return raw


def selection(record):
    """Explicit finite profile, not a claim about arbitrary consumer MIME support."""
    if record['template_path']:return 'excluded-template'
    if record['namespace']!=scripts.HTML:return 'excluded-foreign-namespace'
    value=scripts.attributes(record).get('type')
    if value=='application/ld+json':return 'selected'
    if value is not None:
        folded=value.strip(ASCII_SPACE).translate(str.maketrans('ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'))
        if folded.split(';',1)[0].strip(ASCII_SPACE)=='application/ld+json':return 'unresolved-type-variant'
    return 'excluded-other-type'


def combine(reading):
    """Combine parsed roots BEFORE JSON-LD processing, preserving document scope."""
    result=dict(status='source-incomplete',selected_count=0,diagnostics=[],
                combined_json=None,combined_sha256=None,root_items=None,processing_index=None)
    if not reading['complete']:return result
    combined=[];failures=[];unresolved=False
    for record in reading['scripts']:
        choice=selection(record)
        row=dict(node_id=record['node_id'],selection=choice,payload_sha256=sha(record['payload']),
                 status='not-selected',reason=None,root_items=None)
        result['diagnostics'].append(row)
        if choice=='unresolved-type-variant':unresolved=True
        if choice!='selected':continue
        result['selected_count']+=1
        raw=record['payload']
        try:
            need(len(raw.encode('utf-8'))<=processor.MAX_DOCUMENT,'Script byte bound exceeded')
        except ValueError as error:
            row.update(status='unsupported-input',reason=str(error));failures.append('script-unsupported');continue
        try:value=processor.strict_json(raw)
        except (ValueError,RecursionError) as error:
            row.update(status='json-error',reason=str(error)[:2048]);failures.append('script-error');continue
        try:
            need(type(value) in (dict,list),'Root JSON value outside object/array profile')
            processor.bounded(value)
        except (ValueError,UnicodeError) as error:
            row.update(status='unsupported-input',reason=str(error)[:2048]);failures.append('script-unsupported');continue
        row.update(status='json-parsed',root_items=len(value) if type(value) is list else 1)
        combined.extend(value if type(value) is list else [value])
    if failures:
        result['status']='script-error' if 'script-error' in failures else 'script-unsupported'
    elif unresolved:result['status']='selection-unresolved'
    elif result['selected_count']==0:result['status']='absent'
    else:
        # Root arrays are concatenated one level; local contexts remain inside roots.
        raw=serialized(combined).decode('utf-8')
        try:
            need(len(raw.encode('utf-8'))<=processor.MAX_DOCUMENT,'Combined JSON document exceeds processor bound')
            processor.bounded(combined)
        except (ValueError,UnicodeError) as error:
            result.update(status='combined-unsupported',reason=str(error));return result
        result.update(status='prepared',combined_json=raw,combined_sha256=sha(raw),root_items=len(combined))
    return result


def observe(request,*,node,root=ROOT):
    raw=prepare(request);before=identity(root)
    source=scripts.inventory(raw,content_types=request['content_types'],node=node,root=root)
    readings={};documents=[]
    for mode,reading in source['readings'].items():
        result=combine(reading);readings[mode]=result
        if result['status']=='prepared':
            result['processing_index']=len(documents)
            documents.append(dict(id=mode,base_iri=request['base_iri'],contexts=request['contexts'],raw_json=result['combined_json']))
        # Retain combined input once in the processor observation, always bound by digest.
        del result['combined_json']
    processing=processor.observe({'documents':documents},node=node,root=root) if documents else None
    for mode,result in readings.items():
        if result['processing_index'] is not None:
            processed=processing['documents'][result['processing_index']]
            result['status']='processed' if processed['status']=='observed' else 'processing-unavailable'
    need(identity(root)==before,'HTML workflow sources changed during execution')
    result=dict(kind='unapplied-html-jsonld',version='1',normative_effect='none',profile=PROFILE,
        input=request,input_sha256=sha(serialized(request)),source_sha256=before,source=source,readings=readings,
        processing=processing,base_parameter=dict(iri=request['base_iri'],status='supplied-hypothesis',
            scope='Explicit processor input, not an inferred or observed document.baseURI. Retained base/meta elements may require another hypothesis or attributed rendered capture.'),
        limitations=[
            'Exact application/ld+json type in ordinary HTML tree; case/space/parameter variants remain unresolved, not declared invalid.',
            'All selected scripts in one representation are combined before processing; separate representations/documents have separate blank-node namespaces.',
            'Any selected invalid or unsupported script prevents a combined graph; valid subsets are not promoted to a complete page.',
            'Absence is only within this static HTML selection profile. It is not NA, a rendered-page result, or absence of Microdata/RDFa.',
            'Base IRI is a caller-supplied hypothesis. HTML base selection, CSP, navigation attribution and actual rendered base remain to establish.',
            'No targeted fragment/profile extraction, external script fetching, JavaScript execution or browser behavior.',
            'Processed means transformation completed under declared inputs; notices and empty graphs remain visible. No Schema.org validation, visible-fact truth, rich-result eligibility or TSEP outcome.'])
    need(len(serialized(result))<=MAX_OUTPUT,'HTML observation output bound exceeded');return result


def replay(observation,*,node,root=ROOT):
    need(type(observation) is dict and len(serialized(observation))<=MAX_OUTPUT,'Invalid HTML observation')
    need(observation.get('source_sha256')==identity(root),'Retained HTML workflow sources differ')
    need(observation.get('input_sha256')==sha(serialized(observation['input'])),'Retained HTML input binding differs')
    actual=observe(observation['input'],node=node,root=root)
    need(actual==observation,'Recomputed HTML JSON-LD observation differs; preserve original and new attempt');return actual


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input',type=Path);parser.add_argument('--replay',action='store_true')
    parser.add_argument('--node',required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    try:
        need(not args.output.exists() and not args.output.is_symlink(),'Choose a new output path')
        limit=MAX_OUTPUT if args.replay else MAX_INPUT
        with args.input.open('rb') as f:raw=f.read(limit+1)
        need(len(raw)<=limit,'Input file bound exceeded')
        result=(replay if args.replay else observe)(processor.strict_json(raw),node=args.node)
        with args.output.open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
        print(json.dumps({m:dict(status=r['status'],selected_count=r['selected_count']) for m,r in result['readings'].items()}));return 0
    except (ValueError,KeyError,TypeError,OSError,RecursionError) as error:
        print(json.dumps(dict(kind='html-jsonld-unavailable',reason=str(error),normative_effect='none')),file=sys.stderr);return 64


if __name__=='__main__':sys.exit(main())
