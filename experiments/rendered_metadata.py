#!/usr/bin/env python3
"""Structured DOM inventory v2, not a TSEP evaluator. Apache-2.0."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import tsep

VERSION = '2'
SCRIPT = 'collectors/rendered_metadata.js'
RECIPE = 'tests/fixtures/rendered-metadata-browser-v2.json'
HTML = 'http://www.w3.org/1999/xhtml'
LIMITS = dict(nodes=1024, depth=64, tree_utf8_bytes=524288,
              serialization_utf8_bytes=262144, cooperative_ms=2000, invocation_timeout_ms=5000)
NODE_KEYS = {'id','parent','edge','index','type','name','namespace','attributes','data',
             'child_count','shadow','resolved_href'}
TOP_KEYS = {'format','version','limits','document_url','base_uri','ready_state','execution_context',
            'scripting','closed_shadow_coverage','frame_documents','template_fragments',
            'origin_attribution','serialization','nodes','traversal_complete','stop_reason',
            'api_errors','elapsed_ms','reported_node_count'}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def script_digest():
    return tsep.digest(ROOT/SCRIPT)


def recipes():
    path = ROOT/RECIPE
    tsep.require(tsep.digest(path) == path.with_suffix('.sha256').read_text().split()[0],
                 'Frozen browser recipe mismatch')
    value = tsep.read_json(path)
    tsep.require(value['limits'] == LIMITS, 'Recipe limits mismatch')
    return value


def attrs(node):
    return {a['local_name']:a['value'] for a in node['attributes'] if a['namespace'] is None}


def inventory(tree):
    """Validate supplied topology without repairing or parsing its HTML companion."""
    tsep.require(isinstance(tree, dict) and set(tree) == TOP_KEYS, 'Invalid tree fields')
    tsep.require(tree['format'] == 'rendered-metadata-tree' and tree['version'] == VERSION
                 and tree['limits'] == LIMITS, 'Unsupported tree contract')
    for k, v in [('closed_shadow_coverage','unknown'),('frame_documents','not-collected'),
                 ('template_fragments','not-collected'),('origin_attribution','unknown'),
                 ('execution_context','not-attested'),('scripting','enabled-by-laboratory-plan')]:
        tsep.require(tree[k] == v, 'Unsupported coverage claim: '+k)
    for key in ('document_url','base_uri','ready_state'):
        tsep.require(isinstance(tree[key],str) and tree[key] or
                     tree[key] is None and tree['stop_reason']=='api-error', 'Missing document facts')
    tsep.require(tree['ready_state'] in (None,'loading','interactive','complete'), 'Invalid ready state')
    tsep.require(type(tree['traversal_complete']) is bool and isinstance(tree['api_errors'],list)
                 and all(isinstance(e,str) for e in tree['api_errors']), 'Invalid completion facts')
    tsep.require(tree['stop_reason'] in (None,'node-limit','depth-limit','tree-byte-limit','time-limit','api-error'),
                 'Unknown stop reason')
    tsep.require(tree['traversal_complete'] == (tree['stop_reason'] is None and not tree['api_errors']),
                 'Contradictory completion facts')
    tsep.require(type(tree['elapsed_ms']) in (int,float) and 0 <= tree['elapsed_ms'] <= 86400000,
                 'Invalid elapsed time')
    serial = tree['serialization']
    tsep.require(serial is None and tree['stop_reason']=='api-error' or isinstance(serial,dict),
                 'Missing serialization record')
    if isinstance(serial,dict):
        if serial.get('available') is True:
            tsep.require(set(serial)=={'available','html'} and isinstance(serial['html'],str)
                         and len(serial['html'].encode('utf-8'))<=LIMITS['serialization_utf8_bytes'], 'Serialization bound')
        else:
            tsep.require(serial=={'available':False,'reason':'serialization-byte-limit'}, 'Serialization coverage')
    nodes = tree['nodes']
    tsep.require(isinstance(nodes,list) and len(nodes)<=LIMITS['nodes'], 'Node bound')
    tsep.require(type(tree['reported_node_count']) is int and tree['reported_node_count']==len(nodes),
                 'Transport node count mismatch')
    tsep.require(tree['stop_reason']!='api-error' or bool(tree['api_errors']), 'Missing API error')
    tsep.require(len(json.dumps(nodes,ensure_ascii=False,separators=(',',':')).encode('utf-8'))
                 <= LIMITS['tree_utf8_bytes'], 'Tree byte bound')
    positions, paths, by_parent, shadow_children = [], [], {}, {}
    ordered_paths=[]; document_element=head=body=None
    for i, node in enumerate(nodes):
        tsep.require(isinstance(node,dict) and set(node)==NODE_KEYS and type(node['id']) is int
                     and node['id']==i, 'Invalid/duplicate node ID or fields')
        p = node['parent']
        tsep.require((i==0 and p is None and node['type']==9 and node['edge']=='root' and node['index']==0)
                     or (i>0 and type(p) is int and 0<=p<i and node['edge'] in ('child','shadow')),
                     'Invalid parent/order')
        tsep.require(type(node['type']) is int and node['type'] in (1,3,8,9,10,11)
                     and isinstance(node['name'],str) and node['name'], 'Unsupported node type/name')
        tsep.require(type(node['index']) is int and node['index']>=0 and type(node['child_count']) is int
                     and 0<=node['child_count']<=1000000, 'Invalid child counts')
        tsep.require(node['namespace'] is None or isinstance(node['namespace'],str), 'Invalid namespace')
        tsep.require(node['data'] is None or isinstance(node['data'],str), 'Invalid node data')
        tsep.require(node['resolved_href'] is None or isinstance(node['resolved_href'],str), 'Invalid resolved URL')
        tsep.require(isinstance(node['attributes'],list) and len(node['attributes'])<=4096, 'Invalid attributes')
        keys = set()
        for a in node['attributes']:
            tsep.require(isinstance(a,dict) and set(a)=={'name','local_name','namespace','value'}
                         and all(isinstance(a[k],str) for k in ('name','local_name','value'))
                         and a['name'] and a['local_name']
                         and (a['namespace'] is None or isinstance(a['namespace'],str)), 'Invalid attribute')
            key = (a['namespace'],a['local_name'])
            tsep.require(key not in keys, 'Duplicate DOM attribute')
            keys.add(key)
        tsep.require(node['shadow'] in (('open','unexposed-or-absent') if node['type']==1 else ('not-element',)),
                     'Invalid shadow exposure')
        if node['type'] != 1:
            tsep.require(not node['attributes'] and node['namespace'] is None and node['resolved_href'] is None,
                         'Non-element attributes')
        if i==0:
            positions.append('document');paths.append([]);ordered_paths.append([])
            continue
        parent=nodes[p]
        tsep.require(parent['type'] in (1,9,11), 'Leaf node has children')
        tsep.require(not (parent['namespace']==HTML and parent['name']=='template'), 'Template fragment not in scope')
        if node['edge']=='shadow':
            tsep.require(parent['type']==1 and parent['shadow']=='open' and node['type']==11
                         and node['index']==0 and p not in shadow_children, 'Invalid shadow edge')
            shadow_children[p]=i
        else:
            tsep.require(node['index']==by_parent.get(p,0) and node['index']<parent['child_count'],
                         'Missing/duplicate child order')
            by_parent[p]=node['index']+1
            tsep.require(node['type'] not in (9,11), 'Unexpected nested document/fragment')
        path=paths[p]+[node['edge']+':'+str(node['index'])]
        order=ordered_paths[p]+[(0 if node['edge']=='child' else 1,node['index'])]
        tsep.require(order>ordered_paths[-1], 'Non-preorder tree')
        ordered_paths.append(order)
        tsep.require(len(path)<=LIMITS['depth'], 'Depth bound')
        paths.append(path)
        if p==0 and node['type']==1:
            tsep.require(document_element is None, 'Multiple document elements')
            tsep.require(node['namespace']==HTML and node['name']=='html', 'Unsupported document element')
            document_element=i
        if p==document_element and node['namespace']==HTML:
            if node['name']=='head' and head is None:head=i
            if node['name']=='body' and body is None:body=i
        if node['edge']=='shadow' or positions[p]=='open-shadow': position='open-shadow'
        elif p==head: position='head-direct'
        elif positions[p] in ('head-direct','head-descendant'): position='head-descendant'
        elif p==body or positions[p]=='body': position='body'
        else: position='outside-head-body'
        positions.append(position)
    if tree['traversal_complete']:
        tsep.require(bool(nodes), 'Empty complete tree')
        for i,n in enumerate(nodes):
            tsep.require(by_parent.get(i,0)==n['child_count'], 'Incomplete declared children')
            tsep.require((i in shadow_children)==(n['shadow']=='open'), 'Incomplete shadow tree')
    found=[]; boundaries=[]; elements=[]
    for i,n in enumerate(nodes):
        if n['type']!=1: continue
        a=attrs(n)
        detail={'node_id':i,'id_attribute':a.get('id'),'path':paths[i],'position':positions[i],
                'namespace':n['namespace'],'local_name':n['name'],'attributes':n['attributes']}
        elements.append(detail)
        if n['namespace']!=HTML: continue
        kind = ('canonical' if n['name']=='link' and 'canonical' in re.split('[\t\n\f\r ]+',a.get('rel','').lower())
                else 'robots' if n['name']=='meta' and a.get('name','').lower() in ('robots','googlebot')
                else 'base' if n['name']=='base' else None)
        if kind:
            found.append(dict(detail,kind=kind,raw_href=a.get('href'),resolved_href=n['resolved_href'],
                              content=a.get('content'),name_attribute=a.get('name')))
        if n['name'] in ('iframe','template'):
            boundaries.append(dict(node_id=i,kind=n['name'],coverage='not-collected'))
    return {'kind':'experimental-rendered-metadata-inventory','version':VERSION,
            'document_url':tree['document_url'],'base_uri':tree['base_uri'],
            'traversal_complete':tree['traversal_complete'],'stop_reason':tree['stop_reason'],
            'metadata':found,'elements':elements,'boundaries':boundaries,
            'limits':['No TSEP verdict','Closed shadow roots unknown','Frame documents and template fragments not collected',
                      'DOM APIs and execution world not authenticated','Page/extension origin unknown',
                      'No source HTML interpretation or search-engine inference']}


def compare(left, right):
    tsep.require(left['script_sha256']==right['script_sha256']==script_digest(), 'Different capture script')
    return {'same_script':True,'same_tree':left['tree']==right['tree'],
            'left':inventory(left['tree']),'right':inventory(right['tree']),
            'causal_attribution':'not-established'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('snapshot');p.add_argument('--output',required=True)
    a=p.parse_args()
    try:
        with Path(a.snapshot).open('rb') as handle: raw=handle.read(4*1024*1024+1)
        tsep.require(len(raw)<=4*1024*1024, 'Snapshot file bound')
        record=json.loads(raw)
        tsep.require(record['script_sha256']==script_digest(), 'Different capture script')
        result=inventory(record['tree'])
        result.update(input_sha256=sha(raw),script_sha256=script_digest())
        with Path(a.output).open('x',encoding='utf-8') as f: json.dump(result,f,ensure_ascii=False,indent=2)
        return 0
    except (ValueError,KeyError,TypeError,OSError) as e:
        print(str(e),file=sys.stderr);return 64


if __name__=='__main__':sys.exit(main())
