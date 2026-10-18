"""Bounded supplied originals and human reviews for explicit control profiles.

No acquisition, authenticity, reviewer generation or acceptance of imported verdicts.
"""
import hashlib
import json
from urllib.parse import urlsplit
import tsep
from conformance.http import Unknown, need
from conformance.sitemap_files import original_bytes

VERSION = '1'
ERRORS = (Unknown, ValueError, TypeError, KeyError, AttributeError, OverflowError, RecursionError)
LIMIT = 1024 * 1024
KINDS = {'configuration','crawl','content','sitemap','search-console','logs','render','robots','tls','hreflang','html','http'}


def digest(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode('utf-8')).hexdigest()


def text(value, bound=8192):
    return isinstance(value,str) and bool(value.strip()) and len(value.encode('utf-8')) <= bound


def address(value):
    need(text(value,4096), 'Missing/bounded absolute URL')
    p=urlsplit(value)
    need(p.scheme in ('http','https') and p.hostname and not p.username and not p.password and (p.port is None or 1<=p.port<=65535), 'Unsupported URL authority')
    return p


def binding(target, control):
    evidence=target['evidence_checks'][control]
    return digest({'target':target['url'],'observed_at':target['observed_at'],'intent':target['intent'],
                   'context':target['context'],'control':control,'evidence':{k:v for k,v in evidence.items() if k!='reviews'}})


def verify(target, access=None):
    """A malformed present original is a refusal; absent evidence stays NT."""
    dossiers=target.get('evidence_checks')
    if not isinstance(dossiers,dict):return
    for dossier in dossiers.values():
        if not isinstance(dossier,dict):continue
        if access is not None and 'synthetic' in dossier:
            tsep.require(type(dossier['synthetic']) is bool and dossier['synthetic']==(access=='synthetic'), 'Dossier provenance differs from evidence access')
        records=dossier.get('records')
        for r in records if isinstance(records,list) else []:
            if isinstance(r,dict) and 'native' in r:
                try: original_bytes(r['native'])
                except (ValueError, TypeError, KeyError) as error:
                    raise tsep.Invalid('Evidence dossier original integrity: '+str(error)) from error
        if access is not None:
            for review in dossier.get('reviews',[]) if isinstance(dossier.get('reviews'),list) else []:
                if isinstance(review,dict) and review.get('provenance')=='synthetic-exercise':
                    tsep.require(access=='synthetic','Synthetic review cannot become real evidence')


class Dossier:
    def __init__(self,target,control,reader):
        self.target,self.control=target,control
        self.plan=target['intent']['evidence_checks'][control]
        self.data=target['evidence_checks'][control]
        need(isinstance(self.plan,dict) and self.plan.get('reader')==reader,'Missing/unsupported prior profile')
        need(isinstance(self.data,dict) and type(self.data.get('synthetic')) is bool,'Explicit supplied provenance required')
        need(text(self.plan.get('scope_reason')),'Prior finite scope rationale required')
        need(isinstance(target.get('context'),dict) and all(text(target['context'].get(k)) for k in ('id','tool','tool_version','bounds')),'Attributed bounded context required')
        self.start=tsep.timestamp(target['intent']['declared_at']);self.end=tsep.timestamp(target['observed_at'])
        need(self.start<=self.end,'Plan postdates assessment')
        self.items=self.plan.get('items')
        need(isinstance(self.items,list) and 1<=len(self.items)<=32,'1–32 explicitly selected items required; empty is not NA')
        ids=[i.get('id') for i in self.items if isinstance(i,dict)]
        need(len(ids)==len(self.items) and all(text(i,128) for i in ids) and len(set(ids))==len(ids),'Unique bounded item identifiers required')
        for name in ('records','documents','reviews'):
            values=self.data.get(name)
            need(isinstance(values,list) and len(values)<=128,'Missing/excessive '+name+' inventory')
        need(len(json.dumps(self.data,ensure_ascii=False).encode('utf-8'))<=8*LIMIT,'Dossier exceeds8MiB')

    def dated(self,record):
        need(record.get('context_id')==self.target['context']['id'],'Evidence context mismatch')
        when=tsep.timestamp(record.get('observed_at'));need(self.start<=when<=self.end,'Evidence outside prior assessment window')
        return when

    def raw(self,identity,kind):
        records=[r for r in self.data['records'] if isinstance(r,dict) and r.get('id')==identity]
        need(len(records)==1,'Missing/ambiguous original: '+str(identity))
        r=records[0];need(r.get('kind')==kind,'Wrong original kind');self.dated(r)
        raw=original_bytes(r['native'])
        need(r['native']['complete'] is True and r['native']['encoding']=='identity' and len(raw)<=LIMIT,'Incomplete/compressed/excessive original; no truncated inference')
        return raw,r

    def json(self,identity,kind,format):
        raw,record=self.raw(identity,kind)
        value=json.loads(raw.decode('utf-8'),object_pairs_hook=tsep.unique_object,parse_constant=lambda v:(_ for _ in ()).throw(ValueError('Nonfinite JSON')))
        need(isinstance(value,dict) and value.get('format')==format,'Unknown native JSON profile')
        return value,record

    def document(self,url):
        address(url)
        docs=[d for d in self.data['documents'] if isinstance(d,dict) and d.get('url')==url]
        need(len(docs)==1,'Missing/ambiguous source document: '+str(url))
        self.dated(docs[0])
        return docs[0]

    def response(self,url):
        from conformance.evaluate import trace
        doc=self.document(url);need(text(self.target['intent'].get('crawler')),'Prior client required')
        hops=doc.get('http');need(isinstance(hops,list) and 1<=len(hops)<=12,'Missing/bounded HTTP hops')
        final,status,headers,body=trace(hops,url,self.target['intent']['crawler'])
        need(len(body if isinstance(body,bytes) else body.encode('utf-8'))<=LIMIT,'Source exceeds1MiB')
        return final,status,headers,body

    def source(self,url):
        from conformance.canonical import html
        from conformance.evaluate import utf8_media
        final,status,headers,body=self.response(url)
        need(status==200 and utf8_media(headers,('text/html',)),'Complete200 UTF8 HTML required')
        return final,headers,body,html(body,source=True)

    def review(self,subject):
        matches=[r for r in self.data['reviews'] if isinstance(r,dict) and r.get('subject')==subject]
        need(len(matches)==1,'Missing/ambiguous supplied review: '+subject)
        r=matches[0]
        need(len(json.dumps(r,ensure_ascii=False).encode('utf-8'))<=32768,'Review exceeds32KiB')
        need(r.get('binding_sha256')==binding(self.target,self.control),'Review evidence binding mismatch')
        need(text(r.get('reviewer')) and text(r.get('reason')),'Reviewer/rationale missing')
        allowed=('synthetic-exercise',) if self.data['synthetic'] else ('human','human-assisted')
        need(r.get('provenance') in allowed,'Review provenance mismatch')
        dates=[self.start]+[self.dated(v) for name in ('records','documents') for v in self.data[name] if isinstance(v,dict)]
        need(max(dates)<=tsep.timestamp(r.get('reviewed_at'))<=self.end,'Review chronology mismatch')
        need(r.get('judgment') in ('supported','contradicted'),'Human judgment unresolved')
        return ('fail','Supplied human review contradicts expectation') if r['judgment']=='contradicted' else ('pass','Supplied human review supports bounded expectation; not authenticated')


class Findings:
    def __init__(self):self.rows=[]
    def add(self,subject,outcome,reason):self.rows.append({'subject':subject,'outcome':outcome,'reason':reason})
    def check(self,subject,fn):
        try:
            value=fn()
            if value is not None:self.add(subject,*value)
        except ERRORS as error:self.add(subject,'inconclusive',str(error))
    def compare(self,subject,condition,reason):self.add(subject,'pass' if condition else 'fail',reason)
    def result(self):
        outcomes=[r['outcome'] for r in self.rows]
        return 'fail' if 'fail' in outcomes else ('pass' if outcomes and all(v=='pass' for v in outcomes) else 'inconclusive')


def pieces(target):
    """Retain actual supplied originals under their stated kind; never fill a gap."""
    result={}
    dossiers=target.get('evidence_checks')
    if not isinstance(dossiers,dict):return result
    for control,dossier in dossiers.items():
        if not isinstance(dossier,dict):continue
        for r in dossier.get('records',[]) if isinstance(dossier.get('records'),list) else []:
            if isinstance(r,dict) and r.get('kind') in KINDS:
                result.setdefault(r['kind'],[]).append({'control':control,'record':r})
        docs=dossier.get('documents')
        if isinstance(docs,list) and docs:
            for kind in ('http','html'):
                result.setdefault(kind,[]).append({'control':control,'supplied_documents':docs})
            if control in ('TS11','TS38'):
                result.setdefault('content',[]).append({'control':control,'supplied_source_content':docs,'reviews':dossier.get('reviews')})
            if control=='TS38':
                result.setdefault('crawl',[]).append({'control':control,'supplied_link_source_population':docs,'scope':'Original HTML sources of selected internal-link corpus, not a live crawl'})
        if 'reviews' in dossier:result.setdefault('intent',[]).append({'control':control,'supplied_reviews':dossier['reviews']})
    return result
