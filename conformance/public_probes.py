"""Versioned, bounded public probes. No whole-control or Google assertion."""
import hashlib
import json
import re
from urllib.parse import urlsplit

import tsep
from conformance.http import Unknown, need

PROFILE = 'public-probes-v1'
RULES = ('TS03-A02', 'TS06-A02')


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                    separators=(',', ':')).encode()).hexdigest()


def url(value):
    need(isinstance(value, str) and len(value) <= 4096 and value.isascii(), 'Invalid probe URL')
    p = urlsplit(value)
    need(p.scheme in ('http', 'https') and p.hostname and not p.username and not p.password
         and not p.fragment and not re.search(r'[\s\x00-\x20\x7f\\]', value), 'Invalid probe URL')
    need(p.port in (None, 80, 443) or p.hostname == '127.0.0.1', 'Unsupported probe port')
    return p


def origin(value):
    p = url(value)
    return p.scheme, p.hostname.lower(), p.port or (443 if p.scheme == 'https' else 80)


def plan(target, control):
    p = target.get('intent', {}).get('public_probe')
    need(isinstance(p, dict) and p.get('profile') == PROFILE and p.get('control') == control,
         'Missing versioned public probe plan')
    need(p.get('url') == target['url'], 'Probe plan targets a different URL')
    url(p['url'])
    need(tsep.timestamp(p['declared_at']) <= tsep.timestamp(target['observed_at']), 'Probe plan postdates capture')
    need(target.get('configuration', {}).get('public_probe_sha256') == digest(p), 'Probe plan fingerprint mismatch')
    return p


def ts03(target, p, diagnostics):
    from conformance.evaluate import trace
    routes = p.get('routes')
    need(isinstance(routes, list) and 2 <= len(routes) <= 3, 'Expected existing and generated routes, optional removed route')
    kinds = [r.get('kind') for r in routes if isinstance(r, dict)]
    need(len(kinds) == len(routes) and len(set(kinds)) == len(kinds)
         and set(kinds) in ({'existing', 'generated'}, {'existing', 'generated', 'removed'}), 'Ambiguous probe route scope')
    need(len({r.get('url') for r in routes}) == len(routes), 'Duplicate planned route URL')
    need(next(r['url'] for r in routes if r['kind'] == 'existing') == p['url'], 'Existing route differs from target')
    generated = next(r['url'] for r in routes if r['kind'] == 'generated')
    parent = (url(p['url']).path or '/').rsplit('/', 1)[0] + '/'
    need(origin(generated) == origin(p['url']) and url(generated).path.startswith(parent)
         and re.fullmatch(re.escape(parent)+r'tsep-check-[0-9a-f]{32}', url(generated).path)
         and not url(generated).query, 'Generated route is not the declared same-directory random probe')
    need(p.get('generated_assumption') == 'expected-absent-not-proven', 'Generated-route assumption missing')
    docs = target.get('probe_documents')
    need(isinstance(docs, list) and len(docs) <= 6, 'Missing or excessive probe documents')
    results = []
    for route in routes:
        row = {'kind': route['kind'], 'url': route['url'], 'outcome': 'inconclusive', 'status': None}
        try:
            need(origin(route['url']) == origin(p['url']), 'Route outside declared origin')
            matches = [d for d in docs if isinstance(d, dict) and d.get('url') == route['url']]
            need(matches, 'Missing route observation')
            observations=[]
            for d in matches:
                candidate={'kind':route['kind'],'url':route['url'],'status':None,'outcome':'inconclusive'}
                try:
                    need(tsep.timestamp(p['declared_at']) <= tsep.timestamp(d['observed_at']) <= tsep.timestamp(target['observed_at']), 'Invalid route chronology')
                    hops=d.get('http')
                    need(isinstance(hops,list) and 1 <= len(hops) <= 4,'Missing or excessive redirects')
                    need(all(origin(h['url'])==origin(p['url']) for h in hops),'Redirect outside declared origin')
                    final,status,headers,body=trace(hops,route['url'],p['agent'])
                    need(origin(final)==origin(p['url']),'Final URL outside declared origin')
                    candidate.update(status=status,final_url=final)
                    if status in (401,403,429,206,304) or status>=500:
                        candidate['reason']='Access, rate, partial response or service obstacle; route state unresolved'
                    elif route['kind']=='existing':
                        candidate.update(outcome='pass' if status==200 else 'fail',reason='Existing route: expected HTTP 200, observed '+str(status))
                    else:
                        candidate.update(outcome='pass' if status in (404,410) else 'fail' if status==200 else 'inconclusive',reason='Expected absent route: HTTP 404/410 expected, observed '+str(status))
                except (Unknown,tsep.Invalid,ValueError,TypeError,KeyError) as error:
                    candidate['reason']=str(error)
                observations.append(candidate)
            failures=[o for o in observations if o['outcome']=='fail']
            if failures: row=failures[0]
            elif len(observations)!=1:row['reason']='Duplicate route observations; no unique positive proof'
            else:row=observations[0]
        except (Unknown, tsep.Invalid, ValueError, TypeError, KeyError) as error:
            row['reason'] = str(error)
        results.append(row)
    if diagnostics is not None:
        diagnostics.append({'reader': PROFILE, 'findings': results,
            'limits': 'Declared/generated route states only; not Google soft-404 classification or content validation'})
    outcomes = [r['outcome'] for r in results]
    if any(not isinstance(d,dict) or d.get('url') not in {r['url'] for r in routes} for d in docs):
        outcomes.append('inconclusive')
    outcome = 'fail' if 'fail' in outcomes else 'inconclusive' if 'inconclusive' in outcomes else 'pass'
    return outcome, '; '.join(r['reason'] for r in results)+'; only these routes at collection time; content and removed-route inventory remain separate'


def ts06(target, p, diagnostics):
    need(not url(p['url']).query, 'Private URL probe refuses all query parameters')
    need(p.get('expectation') in ('authentication', 'login', 'not-found'), 'Missing expected denial')
    login = p.get('login_url', '')
    if p['expectation'] == 'login':
        need(login and origin(login) == origin(p['url']) and not url(login).query, 'Declare an exact query-free same-origin login URL')
    record = target.get('anonymous_probe')
    need(isinstance(record, dict) and record.get('profile') == 'anonymous-http-redacted-v1', 'Missing anonymous probe')
    need(record.get('url') == p['url'] and record.get('agent') == p['agent'] and record.get('method') == 'GET'
         and record.get('cookies') is False and record.get('credentials') is False, 'Anonymous context is not attributable')
    need(record.get('plan_sha256') == digest(p), 'Anonymous probe plan mismatch')
    need(tsep.timestamp(p['declared_at']) <= tsep.timestamp(record['started_at'])
         <= tsep.timestamp(record['finished_at']) <= tsep.timestamp(target['observed_at']), 'Invalid anonymous probe chronology')
    need(record.get('complete') is True, 'Anonymous response incomplete')
    need(all(isinstance(record.get(k), str) and re.fullmatch('[0-9a-f]{64}',record[k])
             for k in ('response_sha256','body_sha256','headers_sha256')), 'Missing redacted evidence fingerprints')
    need(type(record.get('body_bytes')) is int and 0 <= record['body_bytes'] <= 2097152, 'Invalid body size')
    need(record.get('body_retained') is False and record.get('redirect_followed') is False, 'Unknown private-body or redirect policy')
    schemes=record.get('authentication_schemes')
    need(isinstance(schemes,list) and len(schemes)<=16 and all(isinstance(x,str) and re.fullmatch('[a-z][a-z0-9_-]{0,49}',x) for x in schemes), 'Invalid authentication scheme evidence')
    status = record.get('status'); need(type(status) is int and 100 <= status <= 599, 'Missing HTTP status')
    if status == 401 and record.get('authentication_schemes') and p['expectation'] == 'authentication':
        outcome, reason = 'pass', 'HTTP 401 with an authentication challenge observed; content not retained or examined'
    elif status in (301,302,303,307,308) and p['expectation'] == 'login' and record.get('location_sha256') == hashlib.sha256(login.encode()).hexdigest():
        outcome, reason = 'pass', 'Redirect to the exact predeclared login URL observed; destination not followed'
    elif status == 404 and p['expectation'] == 'not-found':
        outcome, reason = 'pass', 'Explicitly expected HTTP 404 observed; body confidentiality not established'
    elif status == 200:
        outcome, reason = 'fail', 'HTTP 200 instead of the expected denial; check for exposed content or a login page served as 200'
    else:
        outcome, reason = 'inconclusive', 'HTTP '+str(status)+' does not establish the expected protection; a firewall or challenge may be responsible'
    if diagnostics is not None:
        diagnostics.append({'reader':PROFILE,'findings':[{'url':p['url'],'status':status,'outcome':outcome,'reason':reason}],
            'limits':'One anonymous GET only. No body retained, roles tested, cache seeded, or confidentiality established.'})
    return outcome, reason+'; anonymous response only, not whole-control confidentiality'


def assess(target, rule, diagnostics=None):
    try:
        need(rule in RULES, 'Unsupported public probe rule')
        p = plan(target, rule[:4])
        return ts03(target,p,diagnostics) if rule == 'TS03-A02' else ts06(target,p,diagnostics)
    except (Unknown, tsep.Invalid, KeyError, TypeError, ValueError) as error:
        return 'inconclusive', str(error)
