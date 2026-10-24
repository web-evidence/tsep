"""TS17 source surface only; never a whole-control verdict. Apache-2.0."""
import json,os,hashlib
from pathlib import Path
from urllib.parse import urlsplit
from conformance.source_link_policy import Surface
from experiments import url_resolution,link_elements

PROFILE='essential-document-links-source-v1'
MAX_DESTINATIONS=32

def assess(case):
    result={'kind':PROFILE,'authenticates_evidence':False,'outcome':'inconclusive','scope':'Supplied main-document source only; rendered state and whole TS17 not assessed.','hypotheses':{}}
    try:
        def require(ok,reason):
            if not ok:raise ValueError(reason)
        require(case.get('complete') is True,'Complete native source not established')
        node=os.environ.get('TSEP_SOURCE_NODE');require(bool(node),'Explicit qualified Node runtime unavailable')
        destinations=case['destinations'];document=case['document_url']
        require(type(destinations) is list and 1<=len(destinations)<=MAX_DESTINATIONS and all(type(x) is str for x in destinations),'Bounded declared destinations required')
        require(len(set(destinations))==len(destinations),'Duplicate destination')
        declared=url_resolution.resolve([{'url':u,'base':None} for u in destinations+[document]],node=node)['results']
        for text,value in zip(destinations+[document],declared):
            require(value['ok'] and value['protocol'] in ('http:','https:') and value['href']==text and '#' not in text and not urlsplit(text).username and not urlsplit(text).password,'Exact credential-free fragment-free WHATWG HTTP(S) URL required')
        require(document not in destinations,'Same-document destination outside profile')
        raw=case['source'].encode('utf-8');result['source_sha256']=hashlib.sha256(raw).hexdigest()
        notes=[]
        Surface({'content-type':case['content_types']},raw,'html-tree-links-v2',destinations,destinations[0],[],document_url=document,requested_url=document,diagnostics=notes)
        note=notes[0];require('inventory' in note and 'hypotheses' in note,note.get('reason','Source interpretation unavailable'))
        result['source_reader']='html-tree-links-v2'
        for mode in ('enabled','disabled'):
            read=note['inventory']['readings'][mode];d=note['hypotheses'][mode]
            unknown=[]
            if not read['complete']:unknown.append('Incomplete source inventory')
            if read['parse_errors']:unknown.append('Reported HTML recovery remains unqualified')
            if any(r['namespace']==link_elements.HTML and r['tag']=='base' and not r['template_indices'] and link_elements.attribute(r,'href') is not None for r in read['records']):unknown.append('Active base outside closed initial source/render profile')
            unknown += d.get('unknowns',[])
            if 'links' not in d:unknown.append(d.get('reason','Missing qualified link records'))
            found=sorted({r['destination'] for r in d.get('links',[]) if r['tag']=='a' and r.get('destination') in destinations})
            missing=[x for x in destinations if x not in found]
            outcome='inconclusive' if unknown else 'fail' if missing else 'pass'
            result['hypotheses'][mode]={'outcome':outcome,'found':found,'missing':missing,'unknowns':list(dict.fromkeys(unknown))}
        values=[r['outcome'] for r in result['hypotheses'].values()]
        result['outcome']=values[0] if len(set(values))==1 else 'inconclusive'
        result['reason']='Two static hypotheses agree' if len(set(values))==1 else 'Static scripting hypotheses disagree'
    except (ValueError,TypeError,KeyError,OSError) as e:
        result['reason']=str(e)
    return result
