#!/usr/bin/env python3
"""Qualify named-element facts and existing anchor/base inventory consistency."""
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from experiments import link_elements as observer,source_head
from scripts.source_http_check import fixture

def common(record,modern=False):
    keys=('tag','namespace','context','ancestors','ancestor_namespaces','template_indices','source_span_utf16','raw_tag','body_span_bytes')
    result={k:record[k] for k in keys}
    result['attributes']={a['local_name']:a['value'] for a in record['attributes']} if modern else record['attributes']
    return result

def consistent(reading,old):
    for tag,group in [('a','anchors'),('base','bases')]:
        for inert in (False,True):
            current=[common(r,True) for r in reading['records'] if r['namespace']==observer.HTML and r['tag']==tag
                and (tag=='base' or observer.attribute(r,'href') is not None) and bool(r['template_indices'])==inert]
            previous=[common(r) for r in (old['template_signals'] if inert else old['inventory'][group])
                if not inert or r['group']==group]
            if current!=previous:return False
    return True

def check(node,output):
    output.mkdir(parents=True,exist_ok=False);rows=[]
    for case in fixture('link-elements-v1.json')['cases']:
        raw=case['html'].encode('utf-8');types=['text/html; charset=utf-8']
        r=observer.inventory(raw,content_types=types,node=node);old=source_head.inventory(raw,content_types=types,node=node)
        (output/(case['id']+'.json')).write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
        for mode,v in r['readings'].items():
            unchanged=v['complete'] and old['readings'][mode]['complete'] and consistent(v,old['readings'][mode])
            rows.append({'id':case['id'],'mode':mode,'expected':case['expected'][mode],'actual':v['classification'],
                'same_prior_anchor_base_inventory':unchanged,'matches':unchanged and v['classification']==case['expected'][mode]})
    return {'kind':'link-element-qualification','synthetic':True,'normative_effect':'none','rows':rows,
        'matched':sum(r['matches'] for r in rows),'total':len(rows),'source_sha256':observer.identity(),
        'baseline_sources':source_head.identity(),'script_sha256':observer.sha(Path(__file__).read_bytes()),
        'scope':'31 authored documents under two static hypotheses; element facts and unchanged prior a/base observations, not activated links or TSEP decisions.'}
def main():
    p=argparse.ArgumentParser();p.add_argument('--node',required=True);p.add_argument('--output-dir',type=Path,required=True);a=p.parse_args()
    r=check(a.node,a.output_dir);(a.output_dir/'qualification.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in r.items() if k not in ('rows','source_sha256','baseline_sources')}))
    return 0 if r['matched']==r['total'] else 1
if __name__=='__main__':sys.exit(main())
