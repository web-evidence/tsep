"""TS08 native Google inspection evidence and supplied decisions. Apache-2.0.

Offline documentation assessment, never a live Google or site-state measurement.
"""
import hashlib
import json

import tsep
from conformance.agent_policy import ERRORS, digest, present
from conformance.http import need

VERSION = '1'
READER = 'google-inspection-evidence-v1'
PREFIX = 'Inspection evidence / preuves d’inspection: '


def observer():
    # Keep diagnostic1's parser unchanged; lazy import avoids its adapter cycle.
    from diagnostics import search_console
    return search_console


def unique(rows, url):
    need(isinstance(rows, list) and len(rows) <= 16, 'Missing or excessive inspection records/reviews')
    found = [r for r in rows if isinstance(r, dict) and r.get('url') == url]
    need(len(found) == 1, 'Missing or ambiguous record for ' + url)
    return found[0]


def header(t):
    sc = observer()
    need(len(json.dumps(t, ensure_ascii=False, allow_nan=False).encode()) <= 4*1024*1024,
         'Inspection target exceeds 4 MiB')
    p = t['intent']['inspection']
    need(p['reader'] == READER, 'Unsupported inspection reader')
    need(type(t.get('inspection_synthetic')) is bool, 'Explicit inspection provenance required')
    need(all(present(t.get('context', {}).get(k)) for k in ('network','bounds','tool','tool_version')),
         'Missing inspection context')
    for k in ('selection_method','population','prior_knowledge'):
        need(present(p.get(k)), 'Missing prior ' + k)
    for k in ('max_retrieval_age_hours','max_crawl_age_hours'):
        need(type(p.get(k)) is int and 1 <= p[k] <= 8760, 'Prior bounded integer ' + k + ' required')
    members = p['members']
    need(isinstance(members, list) and 1 <= len(members) <= 16, 'Explicit bounded selected URL set required')
    urls = []
    for m in members:
        sc.check_request({'inspectionUrl':m['url'], 'siteUrl':p['site_url']})
        need(all(present(m.get(k)) for k in ('objective','objective_source','selection_reason')),
             'Missing member objective, source or selection reason')
        urls.append(m['url'])
    need(len(set(urls)) == len(urls) and t['url'] in urls, 'Duplicate members or missing scope anchor')
    declared, observed = sc.stamp(t['intent']['declared_at']), sc.stamp(t['observed_at'])
    need(declared <= observed, 'Plan postdates assessment')
    return p, declared, observed


def review(r, binding, first, last, synthetic):
    sc = observer()
    need(isinstance(r, dict) and r.get('provenance') in ('human','human-assisted','synthetic-exercise'),
         'Missing supplied review/provenance')
    need((r['provenance'] == 'synthetic-exercise') == synthetic, 'Review/evidence provenance differs')
    need(all(present(r.get(k)) for k in ('reviewer','assistance','reason')) and r.get('complete') is True,
         'Incomplete supplied review')
    need(r.get('binding_sha256') == binding, 'Review does not bind exact inputs')
    need(first <= sc.stamp(r['observed_at']) <= last, 'Review outside evidence/assessment dates')
    return r


def judgment(r, key):
    value = r.get(key)
    need(value in ('supported','contradiction'), 'Missing or unknown ' + key + ' qualification')
    return ('pass' if value == 'supported' else 'fail', 'Supplied ' + key + ': ' + value)


def body(value):
    need(isinstance(value, dict) and isinstance(value.get('raw_text'), str), 'Missing native JSON body')
    raw = value['raw_text'].encode('utf-8')
    need(0 < len(raw) <= 512*1024, 'Native body exceeds 512 KiB')
    need(hashlib.sha256(raw).hexdigest() == value.get('sha256'), 'Changed native JSON bytes')
    return tsep.parse_json(raw)


def record(t, p, m, declared, observed):
    sc = observer()
    r = unique(t.get('inspection_records'), m['url'])
    need(r.get('provenance') in ('synthetic-exercise','supplied-google-api') and present(r.get('description')),
         'Missing acquisition provenance')
    need((r['provenance'] == 'synthetic-exercise') == t['inspection_synthetic'], 'Record/evidence provenance differs')
    need(type(r.get('http_status')) is int and 100 <= r['http_status'] <= 599, 'Missing actual HTTP status')
    when = sc.stamp(r['retrieved_at'])
    need(declared <= when <= observed, 'Acquisition outside plan/assessment dates')
    req, response = body(r.get('request')), body(r.get('response'))
    sc.check_request(req)
    need(req['siteUrl'] == p['site_url'], 'Request property differs from prior scope')
    return r, req, sc.engine_state(response, r['http_status'], r['retrieved_at'])


def assess(t, rule, *, diagnostics=None):
    sc = observer()
    note = {'reader':READER, 'version':VERSION, 'target':t.get('url'), 'rule_id':rule,
            'rows':[], 'engine_readings':[], 'scope':'Explicit selected URL set; documentation, not indexing or live state'}
    def row(subject, fn):
        try: outcome, reason = fn()
        except ERRORS as error: outcome, reason = 'inconclusive', str(error)
        note['rows'].append({'subject':subject, 'outcome':outcome, 'reason':reason})
    try:
        p, declared, observed = header(t)
        note['selection'] = p
        members = p['members']
        def population():
            records = t.get('inspection_records')
            need(isinstance(records, list) and len(records) <= 16, 'Missing bounded inspection population')
            urls = [r.get('url') if isinstance(r, dict) else None for r in records]
            need(len(set(urls)) == len(urls) and set(urls) == {m['url'] for m in members},
                 'Missing, duplicate or unplanned inspection record')
            return 'pass', 'All selected URLs have exactly one supplied record'
        row('inspection-population', population)
        if rule == 'TS08-A01':
            for m in members:
                def chronology(m=m):
                    r = unique(t.get('inspection_records'), m['url'])
                    when = sc.stamp(r['retrieved_at'])
                    if when < declared:return 'fail', 'Declared acquisition precedes the declared plan; prospective order contradicted'
                    need(when <= observed, 'Acquisition postdates assessment')
                    return 'pass', 'Declared plan precedes acquisition; dates are not authenticated'
                row(m['url']+':prior-plan', chronology)
            for key in ('selection','objectives'):
                def plan_review(key=key):
                    first = min(sc.stamp(unique(t.get('inspection_records'), m['url'])['retrieved_at']) for m in members)
                    r = review(t.get('inspection_plan_review'), digest({'url':t['url'],'intent':t['intent']}),
                               declared, first, t['inspection_synthetic'])
                    return judgment(r,key)
                row('plan:'+key, plan_review)
        elif rule in ('TS08-A02','TS08-A03'):
            if rule == 'TS08-A03':
                def review_population():
                    reviews = t.get('inspection_reviews')
                    need(isinstance(reviews,list) and len(reviews)<=16, 'Missing bounded review population')
                    urls = [r.get('url') if isinstance(r,dict) else None for r in reviews]
                    need(len(set(urls))==len(urls) and set(urls)=={m['url'] for m in members}, 'Missing, duplicate or unplanned review')
                    return 'pass', 'Exactly one supplied review per selected URL'
                row('review-population',review_population)
            for m in members:
                try:
                    rec, req, engine = record(t,p,m,declared,observed)
                    note['engine_readings'].append(dict(url=m['url'], retrieved_at=rec['retrieved_at'], **engine))
                    if req['inspectionUrl'] != m['url']:
                        note['rows'].append({'subject':m['url']+':attribution','outcome':'fail' if rule=='TS08-A02' else 'inconclusive',
                                             'reason':'Native inspection URL differs from the URL assigned to this record'})
                        continue
                except ERRORS as error:
                    note['rows'].append({'subject':m['url']+':native-input','outcome':'inconclusive','reason':str(error)})
                    continue
                fields = engine['fields']
                def available():
                    need(engine['state']=='recorded', 'API error or missing native index result')
                    return 'pass','Native index result recorded; supplied attribution is not authenticated'
                row(m['url']+':native-result', available)
                if rule == 'TS08-A02':
                    def freshness():
                        need(observed-sc.stamp(rec['retrieved_at']) <= p['max_retrieval_age_hours']*3600, 'Acquisition too old under prior policy')
                        return 'pass','Acquisition within prior age policy, not a live test'
                    row(m['url']+':acquisition-age',freshness)
                    for key in ('verdict','robotsTxtState','indexingState','pageFetchState','crawledAs','googleCanonical','userCanonical','lastCrawlTime'):
                        def field_check(key=key):
                            available();f=fields[key];state=f['state'];value=f['value']
                            if state=='absent':
                                allowed=(key=='userCanonical' or key=='googleCanonical' and fields['verdict']['value'] in ('FAIL','NEUTRAL')
                                    or key=='lastCrawlTime' and fields['verdict']['value'] in ('FAIL','NEUTRAL')
                                    and fields['pageFetchState']['state']=='present' and fields['pageFetchState']['value']!='SUCCESSFUL')
                                need(allowed,'Absent required API field: '+key)
                                return 'pass','Documented absent API field: '+key+'; no source/DOM absence inferred'
                            need(state=='present','Unusable API field '+key+': '+state)
                            if key=='lastCrawlTime':
                                age=sc.stamp(rec['retrieved_at'])-sc.stamp(value)
                                need(0 <= age <= p['max_crawl_age_hours']*3600,'Crawl after retrieval or too old under prior policy')
                            return 'pass','Reported '+key+': '+str(value)+'; not a TSEP site-state verdict'
                        row(m['url']+':'+key,field_check)
                else:
                    try:
                        available()
                        q = unique(t.get('inspection_reviews'),m['url'])
                        review(q,digest({'url':t['url'],'intent':t['intent'],'record':rec}),sc.stamp(rec['retrieved_at']),observed,t['inspection_synthetic'])
                    except ERRORS as error:
                        note['rows'].append({'subject':m['url']+':review','outcome':'inconclusive','reason':str(error)})
                        continue
                    def claimed():
                        need(fields['verdict']['state']=='present','No known API verdict to qualify')
                        need(q.get('claimed_verdict') in ('PASS','FAIL','NEUTRAL'),'Missing qualified reported verdict')
                        return ('pass' if q['claimed_verdict']==fields['verdict']['value'] else 'fail',
                                'Supplied verdict claim compared with the native API value')
                    def temporal():
                        need(q.get('temporal_scope') in ('reported-index-version','current-live-page'),'Missing temporal scope')
                        return ('pass' if q['temporal_scope']=='reported-index-version' else 'fail','API describes reported indexed version, never current live page')
                    def relation():
                        need(q.get('objective_relation') in ('aligned','different'),'Objective relation missing or undetermined')
                        return 'pass','Supplied relation to prior objective: '+q['objective_relation']+'; difference is not a TSEP failure'
                    def explanation():
                        e=q.get('explanation');need(isinstance(e,dict) and present(e.get('text')),'Missing explanation')
                        need(e.get('kind') in ('observation','hypothesis','unresolved'),'Unsupported established cause or missing explanation type')
                        need(e['kind']!='hypothesis' or present(e.get('test')),'Hypothesis needs an observable test')
                        return 'pass','Supplied '+e['kind']+': '+e['text']
                    def decision():
                        d=q.get('decision');need(isinstance(d,dict) and all(present(d.get(k)) for k in ('owner','reason')),'Missing supplied decision/owner/reason')
                        kind=d.get('kind');need(kind in ('accept','correct','monitor','revise-objective'),'Missing decision type')
                        if kind=='monitor':
                            need(present(d.get('criterion')) and sc.stamp(d.get('due_at'))>sc.stamp(q['observed_at']),'Monitoring needs observable criterion and future deadline')
                        elif kind=='correct':need(present(d.get('action')),'Correction needs an action description')
                        elif kind=='revise-objective':need(present(d.get('new_plan_reference')),'Objective revision needs a separate plan reference')
                        return 'pass','Supplied decision: '+kind+'; no execution or objective rewrite performed'
                    for name,fn in [('claimed-verdict',claimed),('interpretation',lambda:judgment(q,'interpretation')),
                                    ('temporal-scope',temporal),('objective-relation',relation),('explanation',explanation),('decision',decision)]:
                        row(m['url']+':'+name,fn)
        else:need(False,'Unsupported inspection rule')
    except ERRORS as error:
        note['rows'].append({'subject':'plan','outcome':'inconclusive','reason':str(error)})
    outcomes=[r['outcome'] for r in note['rows']]
    outcome='fail' if 'fail' in outcomes else 'inconclusive' if not outcomes or 'inconclusive' in outcomes else 'pass'
    if diagnostics is not None:diagnostics.append(note)
    return outcome,PREFIX+json.dumps(note,ensure_ascii=False,separators=(',',':'))
