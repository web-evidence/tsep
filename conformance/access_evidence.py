"""Explicit TS07 access provenance: dated Google report or bound user declaration."""
import hashlib
import json
from urllib.parse import urlsplit
import tsep
from conformance.http import need


def assess(target):
    from conformance.evaluate import binding_digest
    intent=target['intent']
    need(intent.get('access_evidence_profile')=='ts07-access-evidence-v1','Unknown access evidence profile')
    observed=tsep.timestamp(target['observed_at'])
    review=target.get('access_review',{})
    if review:
        need(review.get('provenance')=='user-declaration' and review.get('outcome')=='no-obstacle'
             and review.get('source_http_sha256')==binding_digest(target['http'])
             and review.get('reason')=='I reviewed the displayed page and know of no rule blocking search crawlers',
             'Access declaration is missing or not bound to the displayed response')
        need(tsep.timestamp(review['observed_at'])>=observed,'Access declaration predates capture')
        return 'pass','Access supported by the explicit user declaration on the bound response; no actual Googlebot visit established'
    record=target.get('access_inspection',{})
    need(record.get('url')==target['url'] and record.get('provenance')=='supplied-google-api'
         and record.get('complete') is True and record.get('http_status')==200,'No complete authorized Google inspection for this exact URL')
    for name in ('request','response'):
        item=record.get(name,{})
        need(isinstance(item.get('raw_text'),str) and hashlib.sha256(item['raw_text'].encode()).hexdigest()==item.get('sha256'),'Inspection fingerprint mismatch')
    request=json.loads(record['request']['raw_text'])
    need(request.get('inspectionUrl')==target['url'],'Inspection request targets another URL')
    site=request.get('siteUrl','');p=urlsplit(target['url'])
    covered=((p.hostname==site[10:] or (p.hostname or '').endswith('.'+site[10:])) if site.startswith('sc-domain:')
             else target['url'].startswith(site) and urlsplit(site).netloc==p.netloc)
    need(covered and record.get('authorized_property')==site,'Inspection property does not cover the exact URL')
    need(isinstance(site,str) and site and (site.startswith('sc-domain:') and len(site)>10 or site.endswith('/')), 'Invalid property scope')
    retrieved=tsep.timestamp(record['retrieved_at'])
    need(observed<=retrieved,'Inspection retrieval predates current response')
    fields=json.loads(record['response']['raw_text'])['inspectionResult']['indexStatusResult']
    crawl=tsep.timestamp(fields['lastCrawlTime'])
    need(observed <= crawl <= retrieved,'Google crawl predates the current capture or is future-dated; retain it as dated historical evidence only')
    need(fields.get('pageFetchState')=='SUCCESSFUL' and fields.get('robotsTxtState')=='ALLOWED','Google reported no recent successful allowed fetch')
    return 'pass','Google reports an allowed successful fetch at '+fields['lastCrawlTime']+'; retrieved '+record['retrieved_at']+'; historical Google evidence, not a live inspection or indexing guarantee'
