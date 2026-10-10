#!/usr/bin/env python3
"""Optional Node 24 URL observations; never silently substitute urllib or a browser."""
import json,os,shutil,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from experiments.source_tree import need,sha
MAX_INPUT=4*1024*1024
MAX_OUTPUT=16*1024*1024
TIMEOUT=10

def identity(root=ROOT):
    return {n:sha((root/n).read_bytes()) for n in ('experiments/url_resolution.py',
        'experiments/url_resolution.mjs','experiments/source_tree.py','experiments/source_tree_network_guard.mjs')}

def validate_requests(requests):
    need(type(requests) is list and len(requests)<=50000,'URL request count bound exceeded')
    for r in requests:
        need(type(r) is dict and set(r)=={'url','base'} and type(r['url']) is str
             and (r['base'] is None or type(r['base']) is str),'Malformed URL request')
        need(all(len(s.encode('utf-8'))<=65536 for s in (r['url'],r['base']) if s is not None),
             'URL string byte bound exceeded')
    raw=(json.dumps(requests,ensure_ascii=False,separators=(',',':'))+'\n').encode('utf-8')
    need(len(raw)<=MAX_INPUT,'URL input byte bound exceeded')
    return raw

def validate_result(result,raw,count):
    need(result.get('kind')=='unapplied-url-resolution' and result.get('version')=='1'
         and result.get('normative_effect')=='none','Unexpected URL worker identity')
    need(result.get('request_sha256')==sha(raw),'URL request binding mismatch')
    need(type(result.get('runtime')) is dict and str(result['runtime'].get('node','')).startswith('v24.'),
         'Unqualified URL runtime')
    rows=result.get('results');need(type(rows) is list and len(rows)==count,'Incomplete URL result matrix')
    for row in rows:
        need(type(row) is dict and type(row.get('ok')) is bool,'Malformed URL result')
        if row['ok']:
            need(set(row)=={'ok','href','without_fragment','protocol','origin'} and
                 all(type(row[k]) is str for k in ('href','without_fragment','protocol','origin')),
                 'Malformed serialized URL')
            need('#' not in row['without_fragment'] and row['href'].split('#',1)[0]==row['without_fragment'],
                 'Fragment projection mismatch')
        else:need(row=={'ok':False,'error':'invalid-url'},'Unexpected URL failure')

def resolve(requests,*,node=None,root=ROOT):
    raw=validate_requests(requests);before=identity(root)
    selected=shutil.which(node or 'node');need(selected is not None,'Optional Node 24 unavailable; no fallback')
    with tempfile.TemporaryDirectory(prefix='tsep-url-resolution-') as folder:
        work=Path(folder).resolve()
        for name in ('url_resolution.mjs','source_tree_network_guard.mjs'):
            (work/name).write_bytes((root/'experiments'/name).read_bytes())
        (work/'requests.json').write_bytes(raw)
        command=[selected,'--max-old-space-size=128','--no-addons','--disable-proto=throw',
            '--disallow-code-generation-from-strings','--permission','--allow-fs-read='+str(work),str(work/'url_resolution.mjs')]
        env={k:v for k,v in os.environ.items() if not k.startswith('NODE_')}
        with (work/'stdout').open('wb') as out,(work/'stderr').open('wb') as err:
            try:r=subprocess.run(command,cwd=work,env=env,stdin=subprocess.DEVNULL,stdout=out,stderr=err,timeout=TIMEOUT)
            except subprocess.TimeoutExpired as error:raise ValueError('URL worker exceeded 10-second deadline') from error
        with (work/'stderr').open('rb') as f:errors=f.read(4096).decode('utf-8',errors='replace')
        need(r.returncode==0,'URL worker failed: '+errors)
        with (work/'stdout').open('rb') as f:output=f.read(MAX_OUTPUT+1)
        need(len(output)<=MAX_OUTPUT,'URL output byte bound exceeded');result=json.loads(output)
    need(identity(root)==before,'URL reader sources changed')
    validate_result(result,raw,len(requests))
    result['source_sha256']=before
    result['supervisor']={'python':sys.version.split()[0],'deadline_seconds':TIMEOUT,'input_byte_limit':MAX_INPUT,
        'output_byte_limit':MAX_OUTPUT,'max_strings':50000,'string_byte_limit':65536,'node_old_space_mib':128}
    need(len(json.dumps(result,ensure_ascii=False,indent=2).encode())<=MAX_OUTPUT,'Formatted URL output byte bound exceeded')
    return result
