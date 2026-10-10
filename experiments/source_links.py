#!/usr/bin/env python3
"""Conditional source anchor resolution; no runtime, security-policy or TSEP inference."""
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from experiments import source_head,url_resolution
need,sha=source_head.need,source_head.sha
HTML=source_head.HTML

def identity(root=ROOT):
    return dict(source_head.identity(root),**url_resolution.identity(root),
                **{'experiments/source_links.py':sha((root/'experiments/source_links.py').read_bytes())})

def project(reading):
    return {'base':reading['candidate_base']['url'],'links':[
        {'id':row['record']['attributes'].get('id'),'href':row['resolution'].get('href')}
        for row in reading['anchors']]}

def inventory(raw,*,content_types,document_url,csp_headers=None,node=None):
    need(type(document_url) is str,'Document URL must be a string')
    need(csp_headers is None or (type(csp_headers) is list and all(type(v) is str for v in csp_headers)),
         'Malformed supplied CSP fields')
    before=identity();source=source_head.inventory(raw,content_types=content_types,node=node)
    initial=url_resolution.resolve([{'url':document_url,'base':None}],node=node)
    fallback=initial['results'][0]
    need(fallback['ok'] and fallback['protocol'] in ('http:','https:'),'Ordinary HTTP(S) document URL required')
    readings={};url_runs=[initial]
    for mode,r in source['readings'].items():
        need(r['complete'],'Incomplete source inventory; no partial link absence claim')
        bases=r['inventory']['bases'];selected=next((i for i,b in enumerate(bases) if 'href' in b['attributes']),None)
        base=fallback['href'];basis='document-url';resolution=None
        if selected is not None:
            run=url_resolution.resolve([{'url':bases[selected]['attributes']['href'],'base':fallback['href']}],node=node)
            url_runs.append(run);resolution=run['results'][0]
            if not resolution['ok']:basis='first-base-invalid-fallback'
            elif resolution['protocol'] in ('data:','javascript:'):basis='first-base-disallowed-scheme-fallback'
            else:base=resolution['href'];basis='first-base-href'
        anchors=r['inventory']['anchors']
        run=url_resolution.resolve([{'url':a['attributes']['href'],'base':base} for a in anchors],node=node)
        url_runs.append(run)
        flags=['Static conditional calculation; scripts, events and document policy are not executed.']
        if csp_headers is None:flags.append('CSP response fields not supplied; base-policy effect not assessed.')
        elif csp_headers:flags.append('CSP response fields supplied but their base-policy effect is not applied.')
        csp_meta=[m for m in r['metadata'] if m['attributes'].get('http-equiv','').lower()=='content-security-policy']
        if csp_meta:flags.append('CSP meta present; its base-policy effect is not applied.')
        if r['parse_errors']:flags.append('Parser reports errors; static facts are not an admissibility decision.')
        if any(t['shadow_declaration']['value_state'] in ('open','closed') or 'for' in t['attributes'] for t in r['template_containers']):
            flags.append('Declared template/shadow attachment not applied.')
        if any(any(ns not in (None,HTML) for ns in rec['ancestor_namespaces']) for rec in bases+anchors):
            flags.append('HTML base/anchor under foreign namespace ancestry retained without qualification.')
        readings[mode]={'complete':True,'candidate_base':{'url':base,'basis':basis,'selected_index':selected,
            'resolution':resolution,'assumption':'Static UTF-8 document; no CSP restriction or script/base mutation applied.'},
            'bases':bases,'anchors':[{'record':a,'resolution':v} for a,v in zip(anchors,run['results'])],
            'template_signals':[s for s in r['template_signals'] if s['group'] in ('anchors','bases')],
            'csp_meta':csp_meta,'review_flags':flags}
    need(identity()==before,'Source link tools changed during calculation')
    result={'kind':'unapplied-source-link-resolution','version':'1','normative_effect':'none',
        'document_url':document_url,'normalized_document_url':fallback['href'],'csp_headers':csp_headers,
        'source':source,'url_runs':url_runs,'readings':readings,'source_sha256':before,
        'scope':'Ordinary HTML a from two alternative complete source trees; area, SVG hyperlinks, frames and shadow attachment not covered. No family normalization, rendered state, navigation, Google selection or TS10 verdict.'}
    need(len(json.dumps(result,ensure_ascii=False,indent=2).encode())<=32*1024*1024,'Source-link output exceeds 32 MiB; no truncated result')
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('body',type=Path)
    p.add_argument('--content-type',action='append',required=True);p.add_argument('--document-url',required=True)
    p.add_argument('--node',required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();need(not a.output.exists(),'Choose a new output')
    with a.body.open('rb') as f:raw=f.read(source_head.http.MAX_BYTES+1)
    r=inventory(raw,content_types=a.content_type,document_url=a.document_url,node=a.node)
    with a.output.open('x') as f:json.dump(r,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'normative_effect':'none','readings':{m:project(v) for m,v in r['readings'].items()}}))
if __name__=='__main__':main()
