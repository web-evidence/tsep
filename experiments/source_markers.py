#!/usr/bin/env python3
"""Unapplied static source-marker hypotheses; not a TS01 assessment. Apache-2.0."""
import argparse
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from experiments import source_content as content
from conformance.source_text import characters

VERSION='1'
need,sha=content.need,content.sha
HTML=content.HTML
SVG='http://www.w3.org/2000/svg'
MODES=('enabled','disabled')
MAX_OUTPUT=content.MAX_OUTPUT
MAX_SEGMENTS=20000
MAX_MARKERS=64
MAX_MARKER_CHARS=4096
MAX_MATCHES=50000
OUTSIDE=frozenset(('iframe','frame','frameset','plaintext','xmp','noembed','noframes','listing'))


def identity(root=ROOT):
    return dict(content.identity(root),**{name:sha((root/name).read_bytes()) for name in
                ('experiments/source_markers.py','conformance/source_text.py')})


def criteria(value):
    need(type(value) is dict and set(value)=={'required_markers','forbidden_markers'},'Expected explicit required and forbidden marker lists')
    for key in ('required_markers','forbidden_markers'):
        values=value[key]
        need(type(values) is list and len(values)<=MAX_MARKERS and
             all(type(m) is str and m.strip() and len(m)<=MAX_MARKER_CHARS and
                 not any(0xd800<=ord(c)<=0xdfff for c in m) for m in values), 'Invalid or excessive marker list')
        need(len(values)==len(set(values)), 'Duplicate identity marker')
    need(not any(bad in good for good in value['required_markers'] for bad in value['forbidden_markers']),
         'Contradictory required/forbidden markers')


def normalize_input(value):
    # HTML preprocessing precedes tokenization and reference expansion.
    return value.replace('\r\n','\n').replace('\r','\n')


def project(reading,mode):
    """Keep source-contiguous text runs. Any unresolved run invalidates the whole reading."""
    need(mode in MODES,'Unknown scripting hypothesis')
    need(reading['complete'],'Incomplete bounded source tree: '+reading.get('reason','unknown'))
    need(not reading['parse_errors'],'Reported parse5 errors outside this first projection: '+
         ', '.join(sorted({e['code'] for e in reading['parse_errors']})))
    nodes=reading['nodes']; paths=[]; segments=[]; excluded=[]; intervals=[]
    for node in nodes:
        parent=node['parent']; path=(paths[parent] if parent is not None else [])+[node['id']]; paths.append(path)
        elements=[nodes[i] for i in path if nodes[i]['kind']=='element']
        tags=[n['name'] for n in elements if n['namespace']==HTML]
        inactive='template' in tags or any(n['name'] in ('script','style') and n['namespace'] in (HTML,SVG) for n in elements)
        if node['kind']=='element' and node['namespace']==HTML:
            attrs=content.attributes(node)
            if node['name']=='template':
                need(attrs.get('shadowrootmode','').lower() not in ('open','closed') and 'for' not in attrs,
                     'Declarative shadow/streaming template outside source-marker projection')
            need(inactive or node['name'] not in OUTSIDE,'Frame or unsupported raw context outside source-marker projection: '+node['name'])
        if node['kind']!='text': continue
        record={'node_id':node['id'],'data':node['data'],'source_span_utf16':node['source_span_utf16'],
                'body_span_bytes':node.get('body_span_bytes'),'raw_source':node['raw_source'],
                'ancestors':[{'name':n['name'],'namespace':n['namespace']} for n in elements]}
        if inactive:
            excluded.append(dict(record,reason='Excluded script/style/inactive template context')); continue
        foreign=any(n['namespace']!=HTML for n in elements)
        need(not foreign or not node['data'].strip(),'Nonblank foreign text outside source-marker projection')
        if foreign:
            excluded.append(dict(record,reason='Foreign whitespace, outside HTML text')); continue
        need(elements and any(t in ('head','body') for t in tags),'Text outside attributed head/body')
        span=node.get('body_span_bytes'); raw=node['raw_source']
        need(type(span) is list and len(span)==2 and span[0]<span[1] and type(raw) is str,
             'Text run lacks an attributable source interval')
        parent_name=elements[-1]['name']
        rawtext=parent_name=='noscript' and mode=='enabled'
        rcdata=parent_name in ('title','textarea')
        # An ordinary interval crossing actual markup is not a source segment.
        # RAWTEXT/RCDATA may legitimately contain literal angle brackets.
        need(rawtext or rcdata or '<' not in raw,'Non-contiguous or markup-spanning text run')
        value=normalize_input(raw)
        if not rawtext:value=characters(value)
        if value!=node['data']:
            # The parser may include the discarded initial LF in its source span.
            first_child=node['index']==0 and nodes[node['parent']]['kind']=='element'
            need(parent_name in ('pre','textarea') and first_child and value.startswith('\n') and
                 value[1:]==node['data'],'Parsed text cannot be derived from one contiguous source interval')
        record['decoding']='rawtext-after-input-preprocessing' if rawtext else 'references-after-input-preprocessing'
        record['initial_lf_omitted']=value!=node['data']
        segments.append(record);intervals.append(span)
        need(len(segments)<=MAX_SEGMENTS,'Text segment bound exceeded')
    ordered=sorted(intervals)
    need(all(a[1]<=b[0] for a,b in zip(ordered,ordered[1:])),'Overlapping source text intervals')
    return segments,excluded


def compare(segments,objective):
    required=objective['required_markers']; forbidden=objective['forbidden_markers']
    count=0
    def matches(markers):
        nonlocal count
        result={}
        for marker in markers:
            hits=[]
            for i,segment in enumerate(segments):
                position=segment['data'].find(marker)
                if position>=0:
                    count+=1;need(count<=MAX_MATCHES,'Marker match bound exceeded')
                    hits.append({'segment':i,'text_offset':position})
            result[marker]=hits
        return result
    req=matches(required);bad=matches(forbidden)
    missing=[m for m,hits in req.items() if not hits];present=[m for m,hits in bad.items() if hits]
    outcome='fail' if missing or present else 'pass' if required else 'inconclusive'
    return {'candidate_outcome':outcome,'missing_required':missing,'present_forbidden':present,
            'required_matches':req,'forbidden_matches':bad,
            'reason':'Literal parsed-segment comparison; no visibility or semantic sufficiency established'}


def hypotheses(inventory,objective):
    if objective is not None:criteria(objective)
    readings={}
    for mode in MODES:
        try:
            segments,excluded=project(inventory['readings'][mode],mode)
            row={'complete':True,'segments':segments,'excluded':excluded}
            if objective is not None:row.update(compare(segments,objective))
            else:row['candidate_outcome']=None
        except (ValueError,KeyError,TypeError) as error:
            row={'complete':False,'reason':str(error),'segments':None,'excluded':None,
                 'candidate_outcome':'inconclusive' if objective is not None else None}
        readings[mode]=row
    outcomes=[readings[m]['candidate_outcome'] for m in MODES]
    consensus=None if objective is None else outcomes[0] if outcomes[0]==outcomes[1] and outcomes[0] in ('pass','fail') else 'inconclusive'
    return readings,consensus


def observe(raw,*,content_types,objective=None,node=None,root=ROOT):
    if objective is not None:criteria(objective)
    before=identity(root)
    inventory=content.tree_inventory(raw,content_types=content_types,node=node,root=root)
    readings,consensus=hypotheses(inventory,objective)
    result={'kind':'unapplied-source-marker-readings','experiment_version':VERSION,'normative_effect':'none',
            'body_sha256':sha(raw),'content_types':content_types,'source_sha256':before,'inventory':inventory,
            'criteria':objective,'readings':readings,'candidate_consensus':consensus,
            'scope':'Two static whole-document scripting hypotheses; no scripts executed, measured browser, HTTP attribution, TS01 outcome or implicit migration. Parsed line endings differ explicitly from historical lexical source text.'}
    need(identity(root)==before,'Source marker tool changed during execution')
    need(len(json.dumps(result,ensure_ascii=False,indent=2).encode('utf-8'))<=MAX_OUTPUT,'Complete marker observation exceeds output bound; no partial result')
    return result


def replay(saved,raw,*,node,root=ROOT):
    need(saved.get('kind')=='unapplied-source-marker-readings' and saved.get('experiment_version')==VERSION,
         'Unknown source-marker observation')
    need(saved.get('normative_effect')=='none' and saved.get('body_sha256')==sha(raw),'Observation body identity differs')
    need(saved.get('source_sha256')==identity(root),'Exact source-marker tool edition required')
    actual=observe(raw,content_types=saved['content_types'],objective=saved['criteria'],node=node,root=root)
    need(actual==saved,'Exact source-marker replay differs; preserve the mismatch')
    return actual


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('body',type=Path);parser.add_argument('--content-type',action='append',required=True)
    parser.add_argument('--criteria',type=Path);parser.add_argument('--replay',type=Path)
    parser.add_argument('--node',required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    try:
        need(not args.output.exists(),'Output already exists')
        with args.body.open('rb') as handle:raw=handle.read(content.http.MAX_BYTES+1)
        need(not(args.criteria and args.replay),'Replay uses retained criteria; no replacement criteria')
        if args.replay:
            saved=json.loads(args.replay.read_text());need(saved['content_types']==args.content_type,'Replay Content-Type differs')
            result=replay(saved,raw,node=args.node)
        else:
            objective=json.loads(args.criteria.read_text()) if args.criteria else None
            result=observe(raw,content_types=args.content_type,objective=objective,node=args.node)
        with args.output.open('x',encoding='utf-8') as handle:json.dump(result,handle,ensure_ascii=False,indent=2);handle.write('\n')
        print(json.dumps({'normative_effect':'none','candidate_consensus':result['candidate_consensus'],
                          'complete':{m:r['complete'] for m,r in result['readings'].items()}}))
    except (ValueError,KeyError,TypeError,OSError) as error:
        print(json.dumps({'kind':'source-marker-observation-unavailable','normative_effect':'none','reason':str(error)}),file=sys.stderr);return 64
    return 0


if __name__=='__main__':sys.exit(main())
