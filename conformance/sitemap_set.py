"""TS15 supplied sitemap-set assessment. Apache-2.0."""
import datetime
import json
import re
from urllib.parse import urlsplit
from conformance import sitemap_files as reader

VERSION='1'
READER='native-sitemap-files-v1'
RULES=('TS15-A01','TS15-A02','TS15-A03')
LIMITATION='Supplied native files, declared URLs/dates/origin, not authenticated or observed server responses. Base XML structure only; no full XSD, URL host/path/length, lastmod truth, indexing, canonical or editorial quality conclusion.'
UNKNOWN='inconclusive'
PREFIX='Supplied sitemap files / fichiers sitemap fournis: '


def need(condition,reason):
    if not condition:raise ValueError(reason)


def stamp(value):
    need(isinstance(value,str),'timestamp required')
    parsed=datetime.datetime.fromisoformat(value.replace('Z','+00:00'))
    need(parsed.tzinfo is not None,'timestamp timezone required')
    return parsed


def address(url):
    need(type(url) is str and not re.search(r'[\s\x00-\x1f\x7f]',url),'URL must be an exact non-whitespace string')
    parts=urlsplit(url)
    need(parts.scheme in ('http','https') and parts.hostname and not parts.username and not parts.password and not parts.fragment,'absolute HTTP(S) URL without credentials/fragment required')
    need(parts.port is None or 0<parts.port<=65535,'invalid URL port')
    return url


def header(t):
    need(type(t.get('sitemap_synthetic')) is bool,'explicit provenance required')
    context=t['context'];need(all(isinstance(context.get(k),str) and context[k].strip() for k in ('network','bounds','tool','tool_version')),'context missing')
    p=t['intent']['sitemap_files'];need(p['reader']==READER,'unknown sitemap-file reader')
    need(isinstance(p.get('selection_reason'),str) and p['selection_reason'].strip(),'selection reason missing')
    declared,start,end,observed=[stamp(x) for x in (t['intent']['declared_at'],p['window_start'],p['window_end'],t['observed_at'])]
    need(declared<=start<=end<=observed and (end-start).total_seconds()<=86400,'invalid prior file window')
    docs,roots=p['documents'],p['roots']
    need(type(docs) is list and 1<=len(docs)<=16 and all(type(u) is str for u in docs) and len(set(docs))==len(docs),'require1–16 distinct declared documents')
    need(type(roots) is list and roots and all(type(u) is str and u in docs for u in roots) and len(set(roots))==len(roots),'require distinct declared roots within documents')
    for url in docs:address(url)
    need(t['url']==roots[0],'target differs from first declared root')
    return p,start,end


def assess(t,rule,*,diagnostics=None):
    rows=[];readings={}
    note=dict(reader=READER,version=VERSION,rule=rule,rows=rows,files={},limitation=LIMITATION)
    def row(subject,outcome,reason):rows.append(dict(subject=subject,outcome=outcome,reason=reason))
    try:
        need(rule in RULES,'unknown TS15 rule')
        p,start,end=header(t)
        note.update(declared_document_count=len(p['documents']), declared_roots=p['roots'], root_discovery='not-established', scope='declared-file-population-only')
        records=t.get('sitemap_files')
        need(type(records) is list and len(records)<=16,'supplied files missing or above16')
        names=[r.get('url') if type(r) is dict else None for r in records]
        if any(type(u) is not str or u not in p['documents'] for u in names):
            row('population',UNKNOWN,'Unexpected/unattributed supplied native file')
        for url in p['documents']:
            try:
                matches=[r for r in records if type(r) is dict and r.get('url')==url]
                need(len(matches)==1,'Missing or ambiguous supplied file')
                f=matches[0]
                need(f.get('provenance')==('synthetic-exercise' if t['sitemap_synthetic'] else 'supplied-native-file'),'file provenance contradicts declared provenance')
                need(isinstance(f.get('description'),str) and f['description'].strip(),'file description missing')
                need(start<=stamp(f['observed_at'])<=end,'file date outside prior window')
                result=reader.read_record(f['native'])
                readings[url]=result
                note['files'][url]={k:v for k,v in result.items() if k!='locations'}
                note['files'][url].update(original_sha256=f['native']['sha256'],declared_observed_at=f['observed_at'],provenance=f['provenance'],location_count=len(result['locations']),location_preview=result['locations'][:16])
                if rule!='TS15-A03':
                    key='format' if rule=='TS15-A01' else 'limits'
                    row(url,result[key],'Supplied file declared for URL '+url+'; '+(', '.join(result['reasons']) or key+' qualified in bounded profile'))
            except (KeyError,TypeError,ValueError,AttributeError,OverflowError) as error:
                row(url,UNKNOWN,'Supplied file declared for URL '+url+': '+str(error))
        if rule=='TS15-A03':
            reached=set()
            for root in p['roots']:
                try:
                    r=readings[root]
                    need(r['format']=='pass' and r['limits']=='pass' and r.get('xml_complete') is True,'root not completely qualified')
                    reached.add(root)
                    if r['kind']=='index':
                        for child in set(r['locations']):
                            address(child)
                            need(child in p['documents'],'Index child absent from declared set: '+child)
                            c=readings[child]
                            need(c['format']=='pass' and c['limits']=='pass' and c.get('xml_complete') is True,'child not completely qualified: '+child)
                            need(c['kind']=='urlset','Nested/cyclic index outside profile: '+child)
                            reached.add(child)
                    row(root,'pass','Declared population of '+str(len(p['documents']))+' supplied files: root and child bindings complete; root discovery not established, no site-wide claim')
                except (KeyError,TypeError,ValueError,AttributeError) as error:
                    row(root,UNKNOWN,str(error))
            if reached!=set(p['documents']):row('coverage',UNKNOWN,'Unreached declared documents or incomplete index traversal')
    except (KeyError,TypeError,ValueError,AttributeError,OverflowError) as error:
        row('scope',UNKNOWN,str(error))
    outcomes=[r['outcome'] for r in rows]
    outcome='fail' if 'fail' in outcomes else UNKNOWN if UNKNOWN in outcomes or not outcomes else 'pass'
    note['outcome']=outcome
    if diagnostics is not None:diagnostics.append(note)
    return outcome,PREFIX+json.dumps(note,ensure_ascii=False,sort_keys=True)
