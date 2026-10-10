#!/usr/bin/env python3
"""Optional head/source observation, never a normative TSEP or Google decision."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from experiments import source_http as http
from experiments import source_tree as shared

need, sha = shared.need, shared.sha
MAX_OUTPUT, TIMEOUT = http.MAX_OUTPUT, http.TIMEOUT
HTML = 'http://www.w3.org/1999/xhtml'


def identity(root=ROOT):
    need(Path(http.__file__).resolve() == ROOT/'experiments/source_http.py', 'Foreign HTTP supervisor')
    return dict(http.identity(root), **{name:sha((root/name).read_bytes()) for name in
        ('experiments/source_head.py','experiments/source_head.mjs')})


def attribute_prefix(result, source, raw, decoding):
    need(result.get('head_extension') == '1', 'Unexpected head extension')
    located=[]
    for reading in result['readings'].values():
        prefix=reading['head_prefix']
        need(type(prefix['complete']) is bool and type(prefix['tokens']) is list, 'Malformed head prefix')
        need(prefix['complete'] == reading['complete'], 'Incomplete head prefix')
        need(len(prefix['tokens']) <= 50000, 'Head token bound exceeded')
        if not reading['complete']: need(not prefix['tokens'], 'Partial head prefix retained')
        previous=0
        for token in prefix['tokens']:
            a,b=token['source_span_utf16']
            need(type(a) is int and type(b) is int and previous == a <= b, 'Unordered head source spans')
            previous=b
            need(token['kind'] in ('start-tag','end-tag','characters','whitespace','text-run','null','comment','doctype','eof'), 'Unknown head token')
            need(type(token['raw']) is str and all(type(token[k]) is bool for k in
                ('unmatched_end','closes_document_head','constructs_document_body')), 'Malformed token observations')
            for side in ('before','after'):
                need(type(token[side]) is list and len(token[side]) <= 257, 'Head stack bound exceeded')
                need(all(type(n['tag']) is str and (n['namespace'] is None or type(n['namespace']) is str)
                         for n in token[side]), 'Malformed observed stack')
            if token['kind']=='text-run':
                need(type(token.get('token_count')) is int and 2 <= token['token_count'] <= 200000 and
                     type(token.get('text_kinds')) is list and token['text_kinds'] and
                     set(token['text_kinds']) <= {'characters','whitespace'}, 'Malformed text run')
            located.append(token)
        if prefix['complete']:
            need(prefix['tokens'] and (prefix['tokens'][-1]['constructs_document_body'] or
                                      prefix['tokens'][-1]['kind'] == 'eof'), 'Missing prefix terminator')
            need(not any(t['constructs_document_body'] or t['kind'] == 'eof' for t in prefix['tokens'][:-1]),
                 'Prefix continues after body/EOF')
    mapped=http.byte_positions(source,decoding['consumed_bom_bytes'],{p for t in located for p in t['source_span_utf16']})
    for token in located:
        a,b=[mapped[p] for p in token['source_span_utf16']]
        need(raw[a:b].decode('utf-8') == token['raw'], 'Head token does not match body bytes')
        token['body_span_bytes']=[a,b]


def inventory(raw, *, content_types, node=None, root=ROOT):
    source, decoding = http.decode(raw, content_types)
    node = shutil.which(node or 'node')
    need(node is not None, 'Optional Node 24 runtime unavailable; no fallback reader')
    worker = 'source_head.mjs'
    def sources():
        result = identity(root)
        result['experiments/'+worker] = sha((root/'experiments'/worker).read_bytes())
        return result
    before = sources()
    dependencies = shared.packages(root)
    with tempfile.TemporaryDirectory(prefix='tsep-source-head-') as folder:
        work = Path(folder).resolve()
        for name, files in dependencies.items():
            for relative, data in files.items():
                destination = work/'node_modules'/name/relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(data)
        for name in (worker, 'source_tree_network_guard.mjs'):
            (work/name).write_bytes((root/'experiments'/name).read_bytes())
        (work/'source.bin').write_bytes(source.encode('utf-8'))
        command = [node, '--max-old-space-size=128', '--no-addons', '--disable-proto=throw',
                   '--disallow-code-generation-from-strings', '--permission',
                   '--allow-fs-read='+str(work), str(work/worker)]
        env = {k: v for k, v in os.environ.items() if not k.startswith('NODE_')}
        with (work/'stdout').open('wb') as out, (work/'stderr').open('wb') as err:
            try:
                completed = subprocess.run(command, cwd=work, env=env, stdin=subprocess.DEVNULL,
                                           stdout=out, stderr=err, timeout=TIMEOUT)
            except subprocess.TimeoutExpired as error:
                raise ValueError('HTTP source reader exceeded 30-second process deadline') from error
        with (work/'stderr').open('rb') as handle:
            error_text = handle.read(4096).decode('utf-8', errors='replace')
        need(completed.returncode == 0, 'HTTP source reader failed: '+error_text)
        with (work/'stdout').open('rb') as handle:
            output = handle.read(MAX_OUTPUT+1)
        need(len(output) <= MAX_OUTPUT, 'Source result byte bound exceeded')
        result = json.loads(output)
    need(sources() == before, 'Reader files changed during execution')
    need(result.get('parser_input_utf8_sha256') == decoding['parser_input_utf8_sha256'], 'Parser input identity differs')
    http.validate_and_attribute(result, source, raw, decoding, metadata=True)
    attribute_prefix(result, source, raw, decoding)
    result['decoding'] = decoding
    result['source_sha256'] = before
    result['supervisor'] = {'python_version': sys.version.split()[0], 'process_timeout_seconds': TIMEOUT,
                            'node_old_space_mib': 128, 'output_byte_limit': MAX_OUTPUT}
    need(len(json.dumps(result, ensure_ascii=False, indent=2).encode('utf-8')) <= MAX_OUTPUT, 'Attributed result byte bound exceeded')
    return result


def projection(reading):
    """A small fact projection for authored qualification; no admissibility decision."""
    tokens=reading['head_prefix']['tokens']
    closures=[t['source_span_utf16'][0] for t in tokens if t['closes_document_head']]
    first_close=min(closures) if closures else None
    spans={tuple(t['source_span_utf16']) for t in tokens if t['kind']=='start-tag'}
    links=reading['inventory']['canonical'] + [t for t in reading['template_signals'] if t['group']=='canonical']
    links.sort(key=lambda r:r['source_span_utf16'][0])
    return {'canonicals':[{'id':r['attributes'].get('id'),'tree_context':r['context'],
        'in_prefix':tuple(r['source_span_utf16']) in spans,
        'after_explicit_head_close':first_close is not None and first_close < r['source_span_utf16'][0]} for r in links],
        'unmatched_head_end_tags':[t['tag'] for t in tokens if t['unmatched_end']]}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('body',type=Path)
    parser.add_argument('--content-type',action='append',required=True)
    parser.add_argument('--node',required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    try:
        need(not args.output.exists(),'Output already exists')
        with args.body.open('rb') as handle: raw=handle.read(http.MAX_BYTES+1)
        result=inventory(raw,content_types=args.content_type,node=args.node)
        with args.output.open('x',encoding='utf-8') as handle:
            json.dump(result,handle,ensure_ascii=False,indent=2);handle.write('\n')
        print(json.dumps({'normative_effect':'none','readings':{m:{'complete':r['complete'],'facts':projection(r) if r['complete'] else None,'reason':r.get('reason')} for m,r in result['readings'].items()}}))
    except (ValueError,KeyError,TypeError,OSError) as error:
        print(json.dumps({'kind':'head-observation-unavailable','reason':str(error),'normative_effect':'none'}),file=sys.stderr)
        return 64
    return 0

if __name__ == '__main__':sys.exit(main())
