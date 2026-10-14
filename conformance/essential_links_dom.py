"""TS17 supplied DOM surface; no observed browser or whole-control verdict. Apache-2.0."""
import os
from urllib.parse import urlsplit
import tsep
from conformance.structured_dom import Surface
from experiments import rendered_metadata as inventory,url_resolution

def assess(value):
    result={'kind':'essential-document-links-dom-v1','authenticates_evidence':False,'outcome':'inconclusive','scope':'Supplied main-document DOM only; no authenticated acquisition or whole-control verdict.'}
    try:
        def need(ok,reason):
            if not ok:raise ValueError(reason)
        state=value['state'];need(type(state) is dict,'Missing rendered state')
        need(state.get('complete') is True and state.get('javascript_enabled') is True and state.get('errors')==[],'Incomplete/error/script state')
        need(all(isinstance(state.get(k),str) and state[k].strip() for k in ('browser','browser_version')),'Missing named browser context')
        when=tsep.timestamp(state['observed_at']);need(tsep.timestamp(value['http_received_at'])<=when<=tsep.timestamp(value['window_end']),'Rendered state outside paired HTTP window')
        surface=Surface(state,value['document_url'],value['http'],value['crawler']);tree=surface.tree
        need(type(value['synthetic']) is bool and (state['structured_dom']['acquisition']['kind']=='authored-synthetic')==value['synthetic'],'DOM provenance differs from supplied evidence mode')
        need(tree['base_uri']==value['document_url'] and not any(r['kind']=='base' for r in surface.facts['metadata']),'Changed/active base outside initial closed profile')
        node=os.environ.get('TSEP_SOURCE_NODE');need(bool(node),'Explicit qualified Node runtime unavailable')
        targets=value['destinations'];need(type(targets) is list and 1<=len(targets)<=32 and all(type(u) is str for u in targets) and len(targets)==len(set(targets)),'Bounded distinct destinations required')
        declared=url_resolution.resolve([{'url':u,'base':None} for u in targets+[value['document_url']]],node=node)['results']
        for text,parsed in zip(targets+[value['document_url']],declared):
            need(parsed['ok'] and parsed['protocol'] in ('http:','https:') and parsed['href']==text and '#' not in text and not urlsplit(text).username and not urlsplit(text).password,'Exact credential-free document URL required')
        need(value['document_url'] not in targets,'Same-document target outside profile')
        hrefs=[];witnesses=[]
        for row in surface.facts['elements']:
            if row['local_name']!='a':continue
            attrs={a['local_name']:a['value'] for a in row['attributes'] if a['namespace'] is None}
            if 'href' not in attrs:continue
            need(row['namespace']==inventory.HTML and row['position']!='open-shadow','Foreign/shadow href outside profile')
            cursor=tree['nodes'][row['node_id']]['parent']
            while cursor is not None:
                parent=tree['nodes'][cursor]
                need(parent['type']!=1 or parent['namespace']==inventory.HTML,'HTML anchor in foreign ancestry remains unqualified')
                cursor=parent['parent']
            need(not any(a['local_name']=='href' and a['namespace'] is not None for a in row['attributes']),'Namespaced href requires review')
            hrefs.append(attrs['href']);witnesses.append({'node_id':row['node_id'],'raw_href':attrs['href']})
        resolved=url_resolution.resolve([{'url':h,'base':tree['base_uri']} for h in hrefs],node=node)['results'] if hrefs else []
        need(all(r['ok'] for r in resolved),'Unresolved href outside qualified profile')
        for witness,r in zip(witnesses,resolved):witness['resolved_document']=r['without_fragment'] if r['protocol'] in ('http:','https:') else None
        found=sorted({w['resolved_document'] for w in witnesses if w['resolved_document'] in targets});missing=[u for u in targets if u not in found]
        result.update(outcome='fail' if missing else 'pass',found=found,missing=missing,witnesses=witnesses,observed_at=state['observed_at'],snapshot_sha256=state['structured_dom']['snapshot_sha256'],reason='Qualified supplied structured DOM; exact document comparison only')
    except (ValueError,TypeError,KeyError,OSError) as error:result['reason']=str(error)
    return result
