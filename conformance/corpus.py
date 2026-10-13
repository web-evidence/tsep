"""Bounded explicit corpus extensions; report input size limits stay unchanged.

Apache-2.0. No recursive discovery, arbitrary path reads or expected-result generation.
"""
import hashlib
import json
from pathlib import Path
import re

import tsep

ROOT=Path(__file__).resolve().parents[1]
MAX_TOTAL_BYTES=32*1024*1024


def expand(corpus, *, root=ROOT):
    """Read only declared, fingerprinted fixture extensions in the release inventory."""
    refs=corpus.get('additional_case_files',[])
    tsep.require(type(refs) is list and len(refs)<=16,'Excessive/malformed corpus extensions')
    result=dict(corpus,cases=list(corpus['cases']))
    result.pop('additional_case_files',None)
    if not refs:return result
    released=tsep.read_json(root/'release-files.json')['files'];seen=set()
    total=len(json.dumps(corpus,ensure_ascii=False,separators=(',',':')).encode())
    for ref in refs:
        tsep.require(type(ref) is dict and set(ref)=={'path','sha256'},'Malformed corpus extension reference')
        name=ref['path']
        tsep.require(type(name) is str and re.fullmatch(r'tests/fixtures/[A-Za-z0-9_-]+\.json',name)
            and name in released and name not in seen,'Unsafe, unlisted or duplicate corpus extension')
        seen.add(name);p=root
        for part in Path(name).parts:
            p=p/part;tsep.require(not p.is_symlink(),'Symlink in corpus extension path')
        tsep.require(p.is_file() and p.stat().st_size<=tsep.MAX_JSON_BYTES,'Missing/excessive corpus extension')
        with p.open('rb') as stream:raw=stream.read(tsep.MAX_JSON_BYTES+1)
        total+=len(raw);tsep.require(total<=MAX_TOTAL_BYTES,'Aggregate corpus size exceeded')
        tsep.require(len(raw)<=tsep.MAX_JSON_BYTES and hashlib.sha256(raw).hexdigest()==ref['sha256'],'Corpus extension fingerprint differs')
        payload=tsep.parse_json(raw)
        tsep.require(payload.get('synthetic') is True and type(payload.get('cases')) is list
            and 'additional_case_files' not in payload,'Unqualified or recursive corpus extension')
        result['cases'].extend(payload['cases'])
        tsep.require(len(result['cases'])<=10000,'Aggregate corpus case bound exceeded')
    return result
