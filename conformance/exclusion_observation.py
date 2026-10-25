"""TS09 observations for one explicitly selected representative URL per family."""
from urllib.parse import urlsplit
from conformance.http import need
from conformance.evidence_dossier import ERRORS
from conformance import google_directives

READER = 'url-exclusion-observed-v2'


def assess(d, item, f):
    from conformance.robots_control import policy_for
    from conformance.source_directives import assess as source_assess
    url = item.get('representative_url')
    mechanism = item.get('mechanism')
    from conformance.evidence_dossier import address
    source, target, prefix = address(url), address(d.target['url']), address(item.get('url_prefix'))
    origin = lambda p: (p.scheme, p.hostname.lower(), p.port or (443 if p.scheme=='https' else 80))
    need(origin(source)==origin(target)==origin(prefix), 'Representative URL outside target origin')
    scope=item['url_prefix']
    need(url==scope or (scope.endswith('/') and url.startswith(scope)), 'Representative URL outside prior exact URL or path prefix')
    f.info=getattr(f,'info',[])
    key = item['id'] + ':observation'
    p = urlsplit(url)
    robot_url = p.scheme + '://' + p.netloc + '/robots.txt'
    decision = ['unknown']

    def access():
        robot = d.document(robot_url)
        target = dict(d.target, robots=robot, intent=dict(d.target['intent'],
            robots_policy={'profile': 'google-robotstxt-fields-v2', 'product_token': 'Googlebot'}))
        decision[0], reason = policy_for(target, url, client_representation_only=True)
        f.add(key+':robots', 'inconclusive' if decision[0]=='unknown' else 'fail' if decision[0]=='disallow' else 'pass',
              'Crawler access to exclusion evidence: '+decision[0]+'; '+reason)
    f.check(key+':robots', access)

    def page():
        final, status, headers, body = d.response(url)
        captured_at = d.document(url)['observed_at']
        f.info.append({'subject':key+':http','reason':'Anonymous final HTTP '+str(status)+' at '+final+'; not authenticated Googlebot','status':status,'url':final})
        if final != url:
            f.add(key+':redirect', 'inconclusive', 'Representative URL redirects; exclusion of the original URL is not established by the final page')
        if mechanism == 'robots-disallow':
            f.add(key+':mechanism', 'fail', 'Robots Disallow alone is not an indexing exclusion mechanism; use TS05 to distinguish crawl, exclusion and protection')
        elif mechanism in ('404-410', 'http-404', 'http-410'):
            expected = (404, 410) if mechanism=='404-410' else (int(mechanism[5:]),)
            f.compare(key+':mechanism', status in expected, 'Declared HTTP removal compared with observed status '+str(status))
        elif mechanism in ('authentication', 'authorization'):
            if status == 401 and headers.get('www-authenticate'):
                f.add(key+':mechanism', 'pass', 'Anonymous authentication challenge observed; no role, cache or confidentiality validation')
            elif status in (401, 403):
                f.add(key+':mechanism', 'inconclusive', 'Anonymous access refused; authentication cause not established (WAF, geography or other policy possible)')
            elif status == 200:
                f.add(key+':mechanism', 'inconclusive', 'HTTP 200 does not establish authentication or its absence; login forms and protected content require an access review')
            else:
                f.add(key+':mechanism', 'inconclusive', 'No attributable authentication challenge observed')
        # Always expose both source surfaces, including when the declaration differs.
        if status == 200:
            if mechanism == 'x-robots-tag-noindex':
                header_match=bool(set(google_directives.facts(headers, [], captured_at)['tokens']) & {'noindex','none'})
                f.compare(key+':mechanism', header_match, 'Declared HTTP noindex compared with complete response headers; HTML parsing is not required')
            notes = []
            intent = {'source_reader': 'html-tree-directives-v1', 'directive_policy': google_directives.PROFILE,
                      'crawler': 'googlebot', 'indexing': 'exclude'}
            def combine(h, values, i, diagnostics=None):
                result = google_directives.result(h, values, i, captured_at, diagnostics)
                if diagnostics is not None:
                    diagnostics.append({'surface': 'meta', **google_directives.facts({}, values, captured_at)})
                    diagnostics.append({'surface': 'header', **google_directives.facts(h, [], captured_at)})
                return result
            try:
                outcome, reason = source_assess(headers, body, intent, combine=combine, diagnostics=notes)
            except ERRORS as error:
                outcome, reason = 'inconclusive', str(error)
            f.info.append({'subject':key+':directives','reason':reason,'source_interpretation':outcome,'readings':notes})
            if mechanism == 'meta-noindex':
                surface = 'meta' if mechanism=='meta-noindex' else 'header'
                readings = notes[0].get('directive_observations', {}) if notes else {}
                states = [row for rows in readings.values() for row in rows if row.get('surface')==surface]
                if len(states)!=2:
                    f.add(key+':mechanism', 'inconclusive', 'Complete attributable source readings missing for '+surface)
                else:
                    # The registered noindex mechanism must be present on its declared surface.
                    matches = [bool(set(row['tokens']) & {'noindex', 'none'}) for row in states]
                    f.add(key+':mechanism', 'pass' if all(matches) else 'fail' if not any(matches) else 'inconclusive',
                          'Declared '+mechanism+' compared with both static readings of its source surface')
        elif mechanism in ('meta-noindex', 'x-robots-tag-noindex'):
            f.add(key+':mechanism', 'inconclusive', 'Non-200 representative response; readable page-level noindex not established')
        if mechanism not in ('robots-disallow', '404-410', 'http-404', 'http-410', 'authentication', 'authorization', 'meta-noindex', 'x-robots-tag-noindex'):
            f.add(key+':mechanism', 'inconclusive', 'Declared exclusion mechanism missing or unsupported')
    f.check(key+':page', page)
