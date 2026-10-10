"""Prior bounded canonical source policy; no URL resolution or engine inference."""
import hashlib
import json
import os

from conformance.http import Unknown, need
from conformance.canonical_attributes import check
from conformance.source_directives import consensus
from experiments import source_head

READER = 'html-tree-canonical-v1'
VERSION = '1'
HTML = 'http://www.w3.org/1999/xhtml'
MAX_DIAGNOSTIC_BYTES = 4 * 1024 * 1024
HEAD_ELEMENTS = {'base', 'link', 'meta', 'noscript', 'script', 'style', 'template', 'title'}


def prefix_issues(reading):
    """Explicit bounded frontier, not a complete HTML validity checker."""
    issues=[]
    for token in reading['head_prefix']['tokens']:
        before=token['before']
        if any(n['tag']=='template' and n['namespace']==HTML for n in before):
            continue
        tags=[n['tag'] for n in before if n['namespace']==HTML]
        if token['unmatched_end']:
            issues.append('Unmatched source end tag: '+str(token['tag']))
        if token['kind']=='start-tag':
            tag=token['tag']
            if tag in ('html','head') and tag in tags:
                issues.append('Repeated source '+tag+' start tag')
            elif 'head' in tags and tag not in HEAD_ELEMENTS | {'body','html'}:
                issues.append('Unqualified source head element: '+str(tag))
    return issues


def ambiguous_attributes(record, errors):
    a,b=record['source_span_utf16']
    for error in errors:
        if error['code']!='duplicate-attribute':continue
        p=error.get('startOffset')
        if type(p) is not int or p<0 or a<=p<b:return True
    return False


def decide_reading(reading, preferred, required):
    need(reading['complete'] and reading['head_prefix']['complete'],
         'Incomplete source/head inventory; no absence conclusion')
    unknowns=prefix_issues(reading)
    errors=reading['parse_errors']
    if errors:unknowns.append('Reported parse errors: '+', '.join(sorted({e['code'] for e in errors})))
    for template in reading['template_containers']:
        if template['shadow_declaration']['value_state'] in ('open','closed') or 'for' in template['attributes']:
            unknowns.append('Declared shadow/template attachment is not covered')
    closures=[t['source_span_utf16'][0] for t in reading['head_prefix']['tokens'] if t['closes_document_head']]
    first_close=min(closures) if closures else None
    values=[];bad=[]
    for record in reading['inventory']['canonical']:
        try:
            need(record['namespace']==HTML and all(n in (None,HTML) for n in record['ancestor_namespaces']),
                 'Foreign-context HTML canonical needs review')
            need(record['source_span_utf16'] is not None, 'Canonical lacks source attribution')
            need(not ambiguous_attributes(record,errors), 'Duplicate canonical attributes need review')
            check(record['attributes'])
            context=record['context']
            need(context in ('head','body'), 'Canonical context is outside this profile')
            if context=='head':
                need(record['ancestors'][-1]=='head', 'Indirect head canonical needs review')
                need(first_close is None or record['source_span_utf16'][0]<first_close,
                     'Canonical reinserted after explicit head closure; source admission unqualified')
            href=record['attributes'].get('href')
            values.append({'href':href,'context':context,'body_span_bytes':record['body_span_bytes']})
            # preferred is validated as absolute HTTP(S), no fragment by the caller.
            # Exact literal equality never resolves a relative href via base.
            if context!='head' or href!=preferred:bad.append(values[-1])
        except (Unknown,KeyError,TypeError,ValueError) as error:
            unknowns.append(str(error))
    if bad:
        return 'fail', 'Attributable canonical contradiction: '+repr(bad)+'; other limits: '+repr(unknowns)
    if unknowns:return 'inconclusive', '; '.join(unknowns)
    if required and not values:return 'fail', 'Required HTML canonical absent from complete qualified source inventory'
    return 'pass', 'Source canonical values compared literally: '+repr(values)+'; ordinary template contents excluded, bases not used for resolution'


class Surface:
    """One already-attributed source, assessed in two alternative hypotheses."""
    def __init__(self, headers, body, selection, preferred, required, *, document_url, diagnostics=None):
        record={'reader':selection,'policy_version':VERSION,'document_url':document_url,
                'required_html_canonical':required,
                'scope':'Static source alternatives only; no rendered state, HTML validity or Google canonical selection.'}
        try:
            need(selection==READER, 'Unsupported canonical source_reader; no legacy fallback')
            raw=body if type(body) is bytes else body.encode('utf-8')
            record['body_sha256']=hashlib.sha256(raw).hexdigest()
            result=source_head.inventory(raw,content_types=headers.get('content-type',[]),
                                         node=os.environ.get('TSEP_SOURCE_NODE'))
            record['inventory']={k:v for k,v in result.items() if k not in
                                  ('readings','comparisons','supplementary_comparisons')}
            record['inventory']['readings']={}
            for mode,r in result['readings'].items():
                part={k:v for k,v in r.items() if k in ('complete','reason','head_prefix',
                    'template_containers','encoding_declarations','parse_errors','tree_nodes','document_mode')}
                part['inventory']={k:r['inventory'][k] for k in ('canonical','bases')}
                part['template_signals']=[s for s in r['template_signals'] if s['group'] in ('canonical','bases')]
                record['inventory']['readings'][mode]=part
            decisions={}
            for mode,reading in result['readings'].items():
                try: outcome,reason=decide_reading(reading,preferred,required)
                except (Unknown,KeyError,TypeError,ValueError) as error:outcome,reason='inconclusive',str(error)
                decisions[mode]={'outcome':outcome,'reason':reason}
            record['hypotheses']=decisions
            outcome=consensus(decisions)
            reason=READER+': '+'; '.join(m+'='+d['outcome']+' ('+d['reason']+')' for m,d in decisions.items())
        except (Unknown,KeyError,TypeError,ValueError,OSError) as error:
            outcome,reason='inconclusive',str(error)
        record.update(outcome=outcome,reason=reason)
        if len(json.dumps(record,ensure_ascii=False,indent=2).encode('utf-8'))>MAX_DIAGNOSTIC_BYTES:
            outcome,reason='inconclusive','Canonical source diagnostics exceed 4 MiB; no truncated absence claim'
            record={'reader':READER if selection==READER else '[unsupported; see retained input]',
                    'policy_version':VERSION,'document_url':document_url,'body_sha256':record.get('body_sha256'),
                    'outcome':outcome,'reason':reason}
        self.source_decision=(outcome,reason)
        self.reviewable=outcome!='inconclusive'
        if diagnostics is not None:diagnostics.append(record)
