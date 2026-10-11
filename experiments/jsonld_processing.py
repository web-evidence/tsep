#!/usr/bin/env python3
"""Optional, bounded, offline JSON-LD processing observations. No TSEP verdict.

Apache-2.0. Uses the unmodified jsonld.js 9.0.0 bundle under its retained license.
"""
import argparse
import hashlib
import io
import json
import math
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tarfile
import tempfile
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[1]
VERSION='1'
ARCHIVE_SHA='3628c8df4ceaf4da1f0b55dc7a006287dc4362ed78f6f7c85e83bd99b9328627'
MEMBER_SHA='d4cfcc3ad466b29fdc49b8eb0c7ed2545830fae79c99526999db2c5d6e913f7f'
MAX_INPUT=4*1024*1024
MAX_OUTPUT=16*1024*1024
MAX_DOCUMENT=128*1024
MAX_CONTEXT=1024*1024
TIMEOUT=30


def need(condition,reason):
    if not condition:raise ValueError(reason)


def sha(raw):return hashlib.sha256(raw.encode('utf-8') if isinstance(raw,str) else raw).hexdigest()
def serialized(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')


def pairs(values):
    result={}
    for key,value in values:
        need(key not in result,'Duplicate JSON object key: '+key[:128]);result[key]=value
    return result


def constant(value):raise ValueError('Non-JSON numeric constant: '+value)


def strict_json(raw):
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=constant)


def bounded(value):
    queue=[(value,0)];count=0
    while queue:
        item,depth=queue.pop();count+=1
        need(depth<=64 and count<=50000,'JSON structural bound exceeded')
        if type(item) is int:need(abs(item)<=9007199254740991,'Integer exceeds exact JavaScript range')
        if type(item) is float:
            need(math.isfinite(item),'Nonfinite numeric representation')
            need(not item.is_integer() or abs(item)<=9007199254740991,'Integer exceeds exact JavaScript range')
        if isinstance(item,dict):
            for key in item:key.encode('utf-8',errors='strict')
            queue.extend((v,depth+1) for v in item.values())
        elif isinstance(item,list):queue.extend((v,depth+1) for v in item)
        elif isinstance(item,str):item.encode('utf-8',errors='strict')


def absolute(value):
    need(isinstance(value,str) and 0<len(value)<=4096
         and not any(c.isspace() or ord(c)<32 or ord(c)==127 for c in value)
         and '\\' not in value,'Invalid declared IRI')
    parts=urlsplit(value)
    need(parts.scheme in ('http','https') and bool(parts.hostname) and not parts.username and not parts.password,'Expected declared absolute HTTP(S) IRI')
    parts.port  # Reject invalid port syntax; this does not perform DNS or HTTP.


def prepare(request):
    need(type(request) is dict and set(request)=={'documents'},'Expected documents object')
    docs=request['documents'];need(type(docs) is list and 1<=len(docs)<=64,'Expected 1–64 documents')
    need(len(serialized(request))<=MAX_INPUT,'Request byte bound exceeded')
    ids=set();result=[]
    for doc in docs:
        need(type(doc) is dict and set(doc)=={'id','base_iri','raw_json','contexts'},'Unexpected document fields')
        id=doc['id'];need(type(id) is str and 0<len(id)<=128 and id not in ids,'Invalid or repeated document ID');ids.add(id)
        absolute(doc['base_iri']);raw=doc['raw_json']
        need(type(raw) is str and len(raw.encode('utf-8'))<=MAX_DOCUMENT,'Document byte bound exceeded')
        contexts=doc['contexts'];need(type(contexts) is list and len(contexts)<=32,'Context population bound exceeded')
        seen=set()
        for context in contexts:
            need(type(context) is dict and set(context)=={'url','raw_json','sha256'},'Unexpected context fields')
            absolute(context['url']);need(context['url'] not in seen,'Repeated context URL');seen.add(context['url'])
            c=context['raw_json'];need(type(c) is str and len(c.encode('utf-8'))<=MAX_CONTEXT,'Context byte bound exceeded')
            need(sha(c)==context['sha256'],'Supplied context fingerprint differs')
            data=strict_json(c);bounded(data)
            need(type(data) is dict and '@context' in data,'Context document lacks @context')
        row=dict(doc,pre_error=None)
        try:data=strict_json(raw)
        except (ValueError,RecursionError) as error:
            row['pre_error']={'status':'json-error','reason':str(error)[:2048]}
        else:
            try:
                need(type(data) in (dict,list),'Root JSON value outside object/array profile');bounded(data)
            except (ValueError,UnicodeError) as error:
                row['pre_error']={'status':'unsupported-input','reason':str(error)[:2048]}
        result.append(row)
    return {'documents':result}


def package(root=ROOT):
    base=root/'third_party/jsonld';manifest=json.loads((base/'packages.json').read_bytes())
    need(manifest.get('format_version')==1 and len(manifest['packages'])==1,'Unexpected package manifest')
    row=manifest['packages'][0]
    need((row['name'],row['version'],row['archive'],row['runtime_member'])==
         ('jsonld','9.0.0','jsonld-9.0.0.tgz','dist/jsonld.esm.js'),'Unexpected processor package')
    raw=(base/row['archive']).read_bytes()
    need(len(raw)<=4*1024*1024 and sha(raw)==row['sha256']==ARCHIVE_SHA,'Processor archive differs')
    files={};total=0
    with tarfile.open(fileobj=io.BytesIO(raw),mode='r:gz') as archive:
        for member in archive:
            path=PurePosixPath(member.name)
            need(member.isfile() and not member.issym() and not member.islnk(),'Only regular package files supported')
            need(path.parts[:1]==('package',) and len(path.parts)>1 and not path.is_absolute()
                and '..' not in path.parts and '\\' not in member.name and path.as_posix()==member.name,'Unsafe package member')
            name='/'.join(path.parts[1:]);total+=member.size
            need(name not in files and name in row['files'] and 0<=member.size<=2*1024*1024
                and total<=8*1024*1024 and len(files)<100,'Package extraction bound or inventory differs')
            data=archive.extractfile(member).read(member.size+1)
            need(len(data)==member.size and sha(data)==row['files'][name],'Package member differs');files[name]=data
    need(set(files)==set(row['files']),'Package inventory incomplete')
    need(sha(files[row['runtime_member']])==row['runtime_file_sha256']==MEMBER_SHA,'Processor member differs')
    need((base/'LICENSE').read_bytes()==files['LICENSE'],'Retained processor license differs')
    return files[row['runtime_member']]


def identity(root=ROOT):
    return {name:sha((root/name).read_bytes()) for name in ('experiments/jsonld_processing.py',
        'experiments/jsonld_processing.mjs','experiments/source_tree_network_guard.mjs',
        'third_party/jsonld/packages.json','third_party/jsonld/jsonld-9.0.0.tgz','third_party/jsonld/LICENSE')}


def validate(result,prepared):
    need(type(result) is dict,'Expected observation object')
    need(result.get('kind')=='unapplied-jsonld-processing' and result.get('version')==VERSION
        and result.get('normative_effect')=='none','Unexpected observation identity')
    need(result.get('request_sha256')==sha(serialized(prepared)),'Worker request attribution differs')
    need(result.get('processor')=={'name':'jsonld','version':'9.0.0','member':'dist/jsonld.esm.js'},'Processor identity differs')
    need(result['runtime']['node'].startswith('v24.'),'Unexpected Node runtime')
    rows=result['documents'];need(type(rows) is list and len(rows)==len(prepared['documents']),'Document population differs')
    for doc,row in zip(prepared['documents'],rows):
        need(type(row) is dict and set(row)=={'id','base_iri','raw_json_sha256','contexts',
            'status','expanded','flattened','notices','context_loads','error'},'Unexpected document output')
        need(row['id']==doc['id'] and row['base_iri']==doc['base_iri'] and row['raw_json_sha256']==sha(doc['raw_json'])
            and row['contexts']==[{'url':c['url'],'sha256':c['sha256']} for c in doc['contexts']],'Document or context attribution differs')
        need(row['status'] in ('observed','unavailable','processor-error','json-error','unsupported-input'),'Unknown processing status')
        if doc['pre_error']:
            need(row['status']==doc['pre_error']['status'] and row['error']==doc['pre_error']['reason'],'Input rejection differs')
            need(not row['notices'] and not row['context_loads'],'Rejected input has processor traces')
        else:
            need(row['status'] not in ('json-error','unsupported-input'),'Unexplained input rejection')
            if row['status']!='observed':
                error=row['error']
                need(type(error) is dict and set(error)=={'name','code','message','phase'}
                    and type(error['name']) is str and type(error['message']) is str
                    and len(error['message'])<=2048 and error['phase'] in ('expand','flatten')
                    and (error['code'] is None or type(error['code']) is str),'Malformed processor error')
        if row['status']=='observed':
            need(type(row['expanded']) is list and type(row['flattened']) is list and row['error'] is None,'Missing processed data')
        else:need(row['expanded'] is None and row['flattened'] is None and bool(row['error']),'Failed processing supplied graph')
        need(type(row['notices']) is list and len(row['notices'])<=128 and type(row['context_loads']) is list
            and len(row['context_loads'])<=64,'Processor trace bound exceeded')
        pinned={c['url']:c['sha256'] for c in doc['contexts']}
        for load in row['context_loads']:
            need(load['phase'] in ('expand','flatten') and type(load['url']) is str and type(load['supplied']) is bool,'Malformed context trace')
            need(load['supplied']==(load['url'] in pinned) and load['sha256']==pinned.get(load['url']),'Context lookup attribution differs')
        if row['status']=='observed':need(all(l['supplied'] for l in row['context_loads']),'Observed graph despite unavailable context')
        if row['status']=='unavailable':need(any(not l['supplied'] for l in row['context_loads']),'Missing context refusal')
        for notice in row['notices']:
            need(notice['phase'] in ('expand','flatten') and notice['level']=='warning'
                 and type(notice['code']) is str and type(notice['message']) is str,'Malformed processor notice')


def observe(request,*,node,root=ROOT):
    prepared=prepare(request);before=identity(root);bundle=package(root)
    executable=shutil.which(node);need(executable is not None,'Optional Node 24 unavailable; no fallback processor')
    with tempfile.TemporaryDirectory(prefix='tsep-jsonld-') as folder:
        work=Path(folder).resolve()
        for name in ('jsonld_processing.mjs','source_tree_network_guard.mjs'):(work/name).write_bytes((root/'experiments'/name).read_bytes())
        (work/'jsonld.cjs').write_bytes(bundle);(work/'request.json').write_bytes(serialized(prepared))
        command=[executable,'--max-old-space-size=128','--no-addons','--disable-proto=throw',
            '--disallow-code-generation-from-strings','--permission','--allow-fs-read='+str(work),str(work/'jsonld_processing.mjs')]
        env={k:v for k,v in os.environ.items() if not k.startswith('NODE_')}
        with (work/'stdout').open('wb') as out,(work/'stderr').open('wb') as err:
            try:run=subprocess.run(command,cwd=work,env=env,stdin=subprocess.DEVNULL,stdout=out,stderr=err,timeout=TIMEOUT)
            except subprocess.TimeoutExpired as error:raise ValueError('JSON-LD processor exceeded 30-second deadline') from error
        with (work/'stderr').open('rb') as f:error=f.read(4096).decode('utf-8',errors='replace')
        need(run.returncode==0,'JSON-LD worker failed: '+error)
        with (work/'stdout').open('rb') as f:raw=f.read(MAX_OUTPUT+1)
        need(len(raw)<=MAX_OUTPUT,'Processor output bound exceeded');result=strict_json(raw)
    need(identity(root)==before,'Processor sources changed during execution');validate(result,prepared)
    result.update(input=request,source_sha256=before,supervisor={'python':sys.version.split()[0],
        'process_timeout_seconds':TIMEOUT,'node_old_space_mib':128,'input_byte_limit':MAX_INPUT,'output_byte_limit':MAX_OUTPUT,
        'document_byte_limit':MAX_DOCUMENT,'context_byte_limit':MAX_CONTEXT},
        limitations=['Processing observations only; no Schema.org or search-feature validation, visible facts or TSEP outcome.',
            'All local contexts are supplied evidence, not authenticated authoritative contexts.',
            'Notices retain omitted or transformed information; observed is not a validity or conformance verdict.',
            'Blank-node identifiers are document scoped; separate document results are not silently merged.',
            'Numbers use the processor JavaScript representation; unsafe integers are refused, raw numeric text remains retained.',
            'No HTML extraction, browser observation, rendering, indexing, ranking or content truth is established.'])
    need(len(serialized(result))<=MAX_OUTPUT,'Attributed observation output bound exceeded');return result


def replay(observation,*,node,root=ROOT):
    """Recompute with exact retained sources and runtime, without fetching contexts.

    Structural validation alone is not a computation or authenticity guarantee.
    This comparison includes runtime versions and every emitted value/notice.
    """
    need(type(observation) is dict and len(serialized(observation))<=MAX_OUTPUT,'Invalid retained observation')
    need(observation.get('source_sha256')==identity(root),'Retained processor sources differ')
    prepared=prepare(observation['input']);validate(observation,prepared)
    actual=observe(observation['input'],node=node,root=root)
    need(actual==observation,'Recomputed observation differs; retain both attempts, do not rewrite the original')
    return actual


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input',type=Path);parser.add_argument('--node',required=True);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--replay',action='store_true',help='Recompute a retained observation using its exact sources/runtime')
    args=parser.parse_args()
    try:
        need(not args.output.exists() and not args.output.is_symlink(),'Choose a new output path')
        limit=MAX_OUTPUT if args.replay else MAX_INPUT
        with args.input.open('rb') as f:raw=f.read(limit+1)
        need(len(raw)<=limit,'Input file byte bound exceeded')
        result=(replay if args.replay else observe)(strict_json(raw),node=args.node)
        with args.output.open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
        print(json.dumps({'kind':result['kind'],'normative_effect':'none','documents':[{k:r[k] for k in ('id','status')} for r in result['documents']]}));return 0
    except (ValueError,KeyError,TypeError,OSError,RecursionError,tarfile.TarError) as error:
        print(json.dumps({'kind':'jsonld-processing-unavailable','reason':str(error),'normative_effect':'none'}),file=sys.stderr);return 64


if __name__=='__main__':sys.exit(main())
