#!/usr/bin/env python3
"""Compare explicit URL inputs outside the observed page, without selecting its base."""
import argparse
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from examples import base_uri_diagnostic as lab
from experiments import url_resolution


def compare(folder,node):
    observed=lab.analyze(folder);requests=[];bindings=[];base_requests=[];base_bindings=[]
    for row in observed['rows']:
        d=row['direct']
        for name,key,base in [('document','parsed_against_document',d['document_url']),
                              ('observed-base','parsed_against_observed_base',d['base_uri'])]:
            requests.append(dict(url=d['raw_href'],base=base))
            browser=d[key];lab.need(type(browser.get('ok')) is bool,'Malformed browser parser result')
            normalized=dict(ok=browser['ok'])
            if browser['ok']:
                lab.need(isinstance(browser.get('href'),str),'Missing browser serialization');normalized['href']=browser['href']
            bindings.append(dict(id=row['id'],phase=row['phase'],base_source=name,browser=normalized))
        if d['bases']:
            base_requests.append(dict(url=d['bases'][0]['raw'],base=d['document_url']))
            base_bindings.append(dict(id=row['id'],phase=row['phase'],base_property=d['bases'][0]['property']))
    run=url_resolution.resolve(requests+base_requests,node=node);comparisons=[]
    for binding,result,request in zip(bindings,run['results'],requests):
        actual=dict(ok=result['ok'])
        if result['ok']:actual['href']=result['href']
        comparisons.append(dict(binding,request=request,node=actual,matches=actual==binding['browser']))
    bases=[dict(binding,request=request,node=result) for binding,request,result in
           zip(base_bindings,base_requests,run['results'][len(requests):])]
    return dict(kind='base-uri-explicit-url-comparison',synthetic=True,normative_effect='none',
        browser_standard_expectations=dict(matching=observed['matching'],total=observed['total']),
        explicit_url_comparisons=dict(matching=sum(r['matches'] for r in comparisons),total=len(comparisons)),
        comparisons=comparisons,first_base_parses=bases,node_run=run,
        script_sha256=lab.sha(Path(__file__).read_bytes()),
        scope='Node compares identical explicit URL/base inputs, not browser base selection or engine validity. Browser expectation mismatches remain unchanged. No normative decision or real-site inference.')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('folder',type=Path);p.add_argument('--node',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    lab.need(not a.output.exists(),'Choose a new output');r=compare(a.folder,a.node);lab.transport.save(a.output,r)
    print(json.dumps({k:r[k] for k in ('kind','normative_effect','browser_standard_expectations','explicit_url_comparisons','scope')}))
    return 0 if r['explicit_url_comparisons']['matching']==r['explicit_url_comparisons']['total'] else 1


if __name__=='__main__':sys.exit(main())
