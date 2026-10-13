"""TS32 declared identity corpus, native JSON-LD and supplied reviews. Apache-2.0.

No page collection, entity matching, cross-document blank-node merging or URL fetch.
"""
import json
import os

from conformance import inspection
from conformance.agent_policy import ERRORS, combine, digest, identifier, present
from conformance.http import need
from experiments import jsonld_processing as native

VERSION='1'
READER='jsonld-identity-corpus-v1'
PREFIX='Structured identity evidence / preuves des identités JSON-LD: '
RULES=('TS32-A01','TS32-A02','TS32-A03')


def stamp(value):return inspection.observer().stamp(value)


def population(rows,key,wanted):
    need(type(rows) is list and len(rows)<=64,'Missing/excessive supplied population')
    found=[r.get(key) if type(r) is dict else None for r in rows]
    need(all(type(v) is str for v in found) and len(set(found))==len(found)
         and set(found)==set(wanted),'Missing, duplicate or unplanned population')
    return 'pass','Exact declared population'


def one(rows,key,value):
    need(type(rows) is list and len(rows)<=64,'Missing/excessive supplied records')
    found=[r for r in rows if type(r) is dict and r.get(key)==value]
    need(len(found)==1,'Missing or duplicate record: '+value)
    return found[0]


def declared_ids(rows):
    need(type(rows) is list and len(rows)<=64,'Missing/excessive IRI declarations')
    ids=[]
    for r in rows:
        native.absolute(r['iri']);need(present(r.get('reason')),'Missing IRI scope reason');ids.append(r['iri'])
    need(len(ids)==len(set(ids)),'Repeated IRI declaration')
    return ids


def header(t):
    need(len(json.dumps(t,ensure_ascii=False,allow_nan=False).encode())<=8*1024*1024,'Identity target exceeds 8 MiB')
    need(type(t.get('identity_synthetic')) is bool,'Explicit identity evidence provenance required')
    need(all(present(t.get('context',{}).get(k)) for k in ('network','bounds','tool','tool_version')),'Missing corpus context')
    p=t['intent']['structured_identity'];need(p.get('reader')==READER,'Unsupported identity reader')
    need(all(present(p.get(k)) for k in ('selection_reason','population')),'Missing prior corpus selection')
    declared,start,end,observed=[stamp(v) for v in (t['intent']['declared_at'],p['window_start'],p['window_end'],t['observed_at'])]
    need(declared<=start<=end<=observed and end-start<=86400*10**9,'Corpus chronology/window unqualified')
    entities=p['entities'];need(type(entities) is list and 1<=len(entities)<=64,'Require 1–64 declared distinct entities')
    keys=[]
    for r in entities:
        need(identifier(r.get('key')) and present(r.get('reason')),'Missing entity key or independent registry reason')
        native.absolute(r['iri']);keys.append(r['key'])
    need(len(set(keys))==len(keys),'Duplicate entity key')
    docs=p['documents'];need(type(docs) is list and 2<=len(docs)<=16,'Require 2–16 selected JSON-LD exports')
    ids=[];used=set();by_key={r['key']:r['iri'] for r in entities}
    for d in docs:
        need(identifier(d.get('id')) and present(d.get('source')),'Missing export identity/source scope')
        native.absolute(d['base_iri']);ids.append(d['id']);members=d['entities']
        need(type(members) is list and 1<=len(members)<=64 and all(type(k) is str and k in keys for k in members)
             and len(set(members))==len(members),'Missing/duplicate/unregistered document entities')
        used.update(members);aux=declared_ids(d['auxiliary_ids']);external=declared_ids(d['external_refs'])
        required={by_key[k] for k in members}
        need(not set(aux)&set(external) and not (set(aux)|set(external))&required,'IRI declarations overlap required entities')
    need(len(set(ids))==len(ids) and used==set(keys),'Duplicate document or unused registry entity')
    need(t['url']==docs[0]['base_iri'],'Corpus anchor differs from first supplied base')
    return p,declared,start,end,observed


def registry(p):
    iris=[r['iri'] for r in p['entities']]
    return ('pass','Distinct declared registry entities have distinct IRIs') if len(set(iris))==len(iris) else ('fail','Distinct declared registry entities share an IRI')


def plan_binding(t):return digest(dict(url=t['url'],intent=t['intent']))


def review_binding(t,document,graph):
    return digest(dict(url=t['url'],intent=t['intent'],document=document,graph=graph))


def references(graph):
    """Flattened property links only. @json literals and vocabulary types are not links."""
    refs=set()
    def walk(v):
        if type(v) is list:
            for child in v:walk(child)
        elif type(v) is dict:
            if '@value' in v:return
            if '@id' in v:
                need(type(v['@id']) is str,'Non-string node reference');refs.add(v['@id'])
            for key,child in v.items():
                if key not in ('@id','@type'):walk(child)
    for node in graph:
        for key,value in node.items():
            if key not in ('@id','@type'):walk(value)
    return sorted(refs)


class Evidence:
    def __init__(self,t,p,notes):
        self.t=t;self.p=p;self.notes=notes;self.values={};self.errors={}
        node=os.environ.get('TSEP_SOURCE_NODE');need(present(node),'Explicit Node 24 / TSEP_SOURCE_NODE required; no fallback')
        for planned in p['documents']:
            did=planned['id']
            try:
                d=one(t.get('identity_documents'),'id',did)
                need(stamp(p['window_start'])<=stamp(d['observed_at'])<=stamp(p['window_end']),'Export outside prior capture window')
                need(type(d['raw_json']) is str and native.sha(d['raw_json'])==d.get('sha256'),'Native export fingerprint differs')
                result=native.observe({'documents':[dict(id=did,base_iri=planned['base_iri'],raw_json=d['raw_json'],contexts=d['contexts'])]},node=node)
                notes[did]=result;value=result['documents'][0]
                need(value['status']=='observed' and not value['notices'],'Unavailable/ambiguous processing or unresolved notices')
                graph=value['flattened'];need(type(graph) is list and 1<=len(graph)<=256,'Empty or excessive graph')
                need(all(type(n) is dict and type(n.get('@id')) is str and '@graph' not in n for n in graph),'Named graph or unsupported flattened node')
                self.values[did]=(d,graph)
            except ERRORS+(OSError,) as error:self.errors[did]=str(error)

    def read(self,did):
        need(did in self.values,self.errors.get(did,'Missing processed export'))
        return self.values[did]

    def ids(self,did):return {n['@id'] for n in self.read(did)[1] if len(n)>1}


def assess(target,rule,*,diagnostics=None):
    obs=dict(reader=READER,version=VERSION,rule=rule,rows=[],inventories={},
        limitation='Selected supplied JSON-LD exports and bound reviews only; no authenticated source completeness, semantic identity, future stability, URL dereference or search claim.')
    rows=obs['rows']
    def row(subject,fn):
        try:
            value=fn();outcome,reason=value[:2];detail=value[2] if len(value)>2 else {}
        except ERRORS+(OSError,) as error:outcome,reason,detail='inconclusive',str(error),{}
        rows.append(dict(detail,subject=subject,outcome=outcome,reason=reason))
    try:
        p,declared,start,end,observed=header(target)
        if rule=='TS32-A01':
            row('registry',lambda:registry(p))
            try:
                r=inspection.review(target.get('identity_plan_review'),plan_binding(target),declared,start,target['identity_synthetic'])
                for key in ('population','mapping','references'):row('plan:'+key,lambda key=key:inspection.judgment(r,key))
            except ERRORS as error:rows.append(dict(subject='prior-review',outcome='inconclusive',reason=str(error)))
        elif rule in ('TS32-A02','TS32-A03'):
            need(registry(p)[0]=='pass','Ambiguous prior registry collision; see A01')
            row('documents',lambda:population(target.get('identity_documents'),'id',[d['id'] for d in p['documents']]))
            e=Evidence(target,p,obs['inventories']);registered={r['key']:r['iri'] for r in p['entities']}
            known={n['@id'] for _,graph in e.values.values() for n in graph if len(n)>1 and not n['@id'].startswith('_:')}
            for d in p['documents']:
                did=d['id']
                if rule=='TS32-A02':
                    for key in d['entities']:
                        def required(key=key,did=did):
                            ids=e.ids(did);expected=registered[key];ok=expected in ids
                            return 'pass' if ok else 'fail','Required declared IRI '+('present' if ok else 'absent from complete nonempty graph'),dict(document=did,entity_key=key,iri=expected)
                        row(did+':entity:'+key,required)
                    def extra(d=d,did=did):
                        allowed={registered[k] for k in d['entities']}|set(declared_ids(d['auxiliary_ids']))
                        unknown=sorted(i for i in e.ids(did) if not i.startswith('_:') and i not in allowed)
                        need(not unknown,'Unplanned defined IRI(s): '+json.dumps(unknown))
                        return 'pass','All defined IRIs fit declared entity/auxiliary scope; blank nodes remain local'
                    row(did+':defined-scope',extra)
                    def links(d=d,did=did):
                        _,graph=e.read(did);local=e.ids(did);external=set(declared_ids(d['external_refs']));facts=[]
                        for iri in references(graph):
                            resolution=('local-document' if iri in local else 'unknown') if iri.startswith('_:') else (
                                'selected-corpus' if iri in known else 'declared-external' if iri in external else 'unknown')
                            facts.append(dict(iri=iri,resolution=resolution))
                        unknown=any(x['resolution']=='unknown' for x in facts)
                        return 'inconclusive' if unknown else 'pass','Reference inventory; no URL fetched',dict(document=did,references=facts)
                    row(did+':references',links)
                else:
                    try:
                        document,graph=e.read(did);r=one(target.get('identity_reviews'),'document_id',did)
                        inspection.review(r,review_binding(target,document,graph),stamp(document['observed_at']),observed,target['identity_synthetic'])
                        def coverage(r=r,graph=graph):
                            supplied=r.get('covered_nodes');expected=[digest(n) for n in graph]
                            need(type(supplied) is list and all(type(v) is str for v in supplied)
                                 and len(set(supplied))==len(supplied) and sorted(supplied)==sorted(expected),'Incomplete/duplicate/changed node review coverage')
                            return 'pass','Every flattened node covered; raw JSON also bound for merged-description review'
                        row(did+':coverage',coverage)
                        for key in ('mapping','duplicate_qualification','reference_meaning'):
                            row(did+':'+key,lambda key=key,r=r:inspection.judgment(r,key))
                    except ERRORS as error:rows.append(dict(subject=did,outcome='inconclusive',reason=str(error)))
            if rule=='TS32-A03':row('review-population',lambda:population(target.get('identity_reviews'),'document_id',[d['id'] for d in p['documents']]))
            obs['registry_observations']=[dict(entity_key=k,iri=iri,
                planned_documents=[d['id'] for d in p['documents'] if k in d['entities']],
                observed_documents=[did for did in e.values if iri in e.ids(did)],
                interpretation='Selected corpus only; a single occurrence is not observed repetition or future stability') for k,iri in registered.items()]
        else:need(False,'Unsupported structured-identity rule')
    except ERRORS+(OSError,) as error:rows.append(dict(subject='scope',outcome='inconclusive',reason=str(error)))
    obs['outcome']=combine(rows)
    if diagnostics is not None:diagnostics.append(obs)
    return obs['outcome'],PREFIX+json.dumps({k:v for k,v in obs.items() if k!='inventories'},ensure_ascii=False,sort_keys=True)
