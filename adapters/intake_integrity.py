"""Bounded snapshots for versioned intake tools; consistency, not authenticity."""
import hashlib
from pathlib import Path, PurePosixPath
import re

import tsep
from adapters.package import MAX_PACKAGE_BYTES, regular
from diagnostics import search_console

def read(root, kind, version, sources, required, optional=(), inspections=False):
    root=Path(root)
    tsep.require(root.is_dir() and not root.is_symlink(),'Expected a regular intake directory')
    meta=tsep.parse_json(regular(root/'intake.json',tsep.MAX_JSON_BYTES))
    tsep.require(isinstance(meta,dict) and meta.get('kind')==kind and meta.get('version')==version,
                 'Unsupported intake version; explicitly prepare a new v2 intake')
    declared=meta.get('files');required=set(required);allowed=required|set(optional)
    tsep.require(isinstance(declared,dict) and required<=set(declared) and len(declared)<=68,
                 'Incomplete or excessive intake inventory')
    files={};total=0
    for name,want in declared.items():
        path=PurePosixPath(name)
        native=inspections and re.fullmatch(r'originals/(?:[1-9]|1[0-6])/(?:manifest\.json|request\.json|response\.json|change-evidence\.txt)',name)
        tsep.require(path.as_posix()==name and not path.is_absolute() and '..' not in path.parts
                     and '\\' not in name and (name in allowed or native),'Unsafe or unsupported intake file path')
        tsep.require(isinstance(want,str) and re.fullmatch('[a-f0-9]{64}',want),'Invalid intake file digest')
        raw=regular(tsep.evidence_path(root,name),tsep.MAX_JSON_BYTES);total+=len(raw)
        tsep.require(total<=MAX_PACKAGE_BYTES,'Intake exceeds package byte bound')
        tsep.require(hashlib.sha256(raw).hexdigest()==want,'Changed intake file: '+name)
        files[name]=raw
    found=set()
    for index,path in enumerate(root.rglob('*')):
        tsep.require(index<100 and not path.is_symlink(),'Unexpected intake entry or symlink')
        if path.is_file():found.add(path.relative_to(root).as_posix())
        else:tsep.require(path.is_dir(),'Unexpected intake entry')
    tsep.require(found==set(files)|{'intake.json'},'Unlisted or missing intake files')
    digest=hashlib.sha256(files['input.json']).hexdigest()
    tsep.require(meta.get('input_sha256')==digest,'Intake binding differs from raw input bytes')
    tsep.require(meta.get('source_files')==sources,'Use exact intake tools or prepare a separate explicit reassessment')
    return files,digest

def target(files,rules):
    data=tsep.parse_json(files['input.json'])
    tsep.require(isinstance(data,dict) and set(data)=={'input_version','rules','targets'}
                 and data.get('input_version')=='2' and data.get('rules')==list(rules)
                 and isinstance(data.get('targets'),list) and len(data['targets'])==1
                 and isinstance(data['targets'][0],dict),'Unexpected intake input shape')
    return data,data['targets'][0]

def request(raw,kind,version,digest):
    data=tsep.parse_json(raw)
    tsep.require(isinstance(data,dict) and data.get('kind')==kind and data.get('version')==version
                 and data.get('input_sha256')==digest,'Reviews do not bind this intake input or version')
    return data

def supplied(path,kind,version,digest):
    return request(regular(Path(path),tsep.MAX_JSON_BYTES),kind,version,digest)

def native_inspections(files,records):
    tsep.require(isinstance(records,list) and 1<=len(records)<=16,'Missing bounded intake records')
    expected=set()
    for index,record in enumerate(records,1):
        prefix='originals/'+str(index)+'/'
        expected.update(prefix+n for n in ('manifest.json','request.json','response.json'))
        tsep.require(expected<=set(files),'Missing original intake files')
        native=tsep.parse_json(files[prefix+'manifest.json'])
        tsep.require(isinstance(native,dict) and isinstance(record,dict),'Missing original inspection manifest')
        original={k:native.get(k) for k in ('retrieved_at','provenance','description','http_status')}
        original['supplied_manifest']=native
        for key in ('request','response'):
            raw=files[prefix+key+'.json'];digest=hashlib.sha256(raw).hexdigest()
            tsep.require(native.get(key+'_sha256')==digest,'Original inspection digest differs')
            original[key]={'raw_text':raw.decode('utf-8'),'sha256':digest}
        original['url']=search_console.check_request(tsep.parse_json(files[prefix+'request.json']))
        tsep.require(record==original,'Prepared record differs from original inspection bytes')
        if native.get('change') is not None:
            name=prefix+'change-evidence.txt';expected.add(name)
            tsep.require(isinstance(native['change'],dict) and name in files
                         and hashlib.sha256(files[name]).hexdigest()==native['change'].get('evidence_sha256'),
                         'Missing or changed original change evidence')
    return expected
