"""Offline performance evidence readers; source quality is not performance quality.

Apache-2.0. No collection, runtime benchmark, fabricated review or engine inference.
"""
from datetime import date, timezone
from decimal import Decimal, InvalidOperation
import hashlib
import json
import re
import statistics
from urllib.parse import urlsplit

import tsep
from conformance.http import Unknown, need

VERSION = '1'
FIELD_METRICS = {
    'LCP': ('largest_contentful_paint', 'ms', Decimal('2500'), Decimal('4000')),
    'INP': ('interaction_to_next_paint', 'ms', Decimal('200'), Decimal('500')),
    'CLS': ('cumulative_layout_shift', 'unitless', Decimal('0.1'), Decimal('0.25')),
}
LAB_METRICS = {'LCP': ('largest-contentful-paint', 'millisecond'),
               'CLS': ('cumulative-layout-shift', 'unitless'),
               'TBT': ('total-blocking-time', 'millisecond')}
SETTING_KEYS = ('formFactor', 'throttlingMethod', 'throttling', 'screenEmulation',
                'emulatedUserAgent', 'disableStorageReset', 'blockedUrlPatterns', 'extraHeaders')


def text(value):
    return isinstance(value, str) and 0 < len(value.strip()) <= 8192


def number(value, *, field=False, cls=False):
    if field and not cls:
        need(type(value) is int, 'CrUX timing percentile must be integer milliseconds')
    elif field:
        need(isinstance(value, str) and re.fullmatch(r'(?:(?:0|[1-9][0-9]*)(?:\.[0-9]+)?|\.[0-9]+)', value),
             'CrUX CLS must be a nonnegative decimal string')
    else:
        need(type(value) in (int, float), 'Laboratory value must be a finite JSON number')
    need(len(str(value)) <= 64, 'Metric precision/size outside supported bounds')
    result = Decimal(str(value))
    need(result.is_finite() and 0 <= result <= Decimal('1000000000000'), 'Invalid metric value')
    return result


def period_date(value):
    need(isinstance(value, dict) and set(value) == {'year', 'month', 'day'}
         and all(type(v) is int for v in value.values()), 'Missing or malformed collection date')
    return date(value['year'], value['month'], value['day'])


def original(evidence, observed):
    need(isinstance(evidence, dict), 'Missing original performance evidence')
    raw = evidence.get('raw_json')
    need(isinstance(raw, str) and 0 < len(raw.encode('utf-8')) <= 4 * 1024 * 1024,
         'Missing or excessive original JSON')
    digest = hashlib.sha256(raw.encode('utf-8')).hexdigest()
    need(evidence.get('sha256') == digest, 'Original performance JSON hash mismatch')
    need(tsep.timestamp(evidence['observed_at']) <= observed, 'Evidence acquisition postdates assessment')
    source = urlsplit(evidence.get('source_url', ''))
    need(source.scheme in ('https', 'http') and source.hostname and not source.username,
         'Missing evidence source URL')
    parsed = tsep.parse_json(raw.encode('utf-8'))
    need(isinstance(parsed, dict), 'Original performance response is not an object')
    return parsed, digest


def plan_for(target, kind):
    observed = tsep.timestamp(target['observed_at']).astimezone(timezone.utc)
    need(tsep.timestamp(target['intent']['declared_at']) <= observed, 'Plan postdates assessment')
    plan = target['intent']['performance'][kind]
    need(isinstance(plan, dict), 'Missing performance plan')
    age = plan.get('max_age_days')
    need(type(age) is int and 0 <= age <= 3660, 'Declare a maximum age in calendar days')
    return plan, observed


def cohort(target, observation):
    plan, observed = plan_for(target, 'field')
    evidence = target['field']
    need(evidence.get('reader') == 'crux-api-v1', 'Unqualified field data reader')
    raw, digest = original(evidence, observed)
    observation.update(source_sha256=digest, field_quality='unknown')
    if 'lighthouseVersion' in raw or 'lighthouseResult' in raw:
        return 'fail', 'Laboratory or mixed PSI response supplied as a CrUX field record', None
    record = raw.get('record')
    need(isinstance(record, dict) and 'error' not in raw, 'No usable CrUX record; cause not inferred')
    key = record['key']
    need(isinstance(key, dict) and ('url' in key) != ('origin' in key), 'Ambiguous CrUX granularity')
    granularity = 'url' if 'url' in key else 'origin'
    identity = key[granularity]
    need(text(identity), 'Missing cohort identifier')
    parsed_identity = urlsplit(identity)
    need(parsed_identity.scheme in ('https', 'http') and parsed_identity.hostname
         and not parsed_identity.username and not parsed_identity.fragment, 'Invalid cohort URL')
    if granularity == 'origin':
        need(not parsed_identity.path and not parsed_identity.query, 'Origin cohort must not include a path or query')
    need(plan.get('granularity') == granularity and plan.get('key') == identity
         and target['url'] == identity, 'Requested scope differs from returned cohort; no URL/origin fallback')
    request = evidence.get('request', {})
    requested = request.get(granularity)
    if requested != identity:
        normalization = raw.get('urlNormalizationDetails', {})
        need(granularity == 'url' and normalization.get('originalUrl') == requested
             and normalization.get('normalizedUrl') == identity,
             'Unattributed CrUX URL normalization')
    need(set(request) <= {'url', 'origin', 'formFactor', 'metrics'}
         and ('url' in request) != ('origin' in request), 'Unsupported CrUX request scope')
    device = key.get('formFactor', 'ALL')
    need(device in ('PHONE', 'DESKTOP', 'TABLET', 'ALL'), 'Unknown device class')
    need(plan.get('form_factor') == device and request.get('formFactor', 'ALL') == device,
         'Device population differs; no aggregation fallback')
    window = record['collectionPeriod']
    first, last = period_date(window['firstDate']), period_date(window['lastDate'])
    need(first <= last <= observed.date(), 'Invalid/future field window')
    need(last <= tsep.timestamp(evidence['observed_at']).astimezone(timezone.utc).date(), 'Field window postdates source acquisition')
    need((observed.date() - last).days <= plan['max_age_days'], 'Field window exceeds declared age limit')
    observation.update(cohort={'granularity': granularity, 'key': identity, 'requested_key': requested,
                              'device': device, 'first_date': first.isoformat(), 'last_date': last.isoformat(),
                              'age_calendar_days': (observed.date()-last).days,
                              'population': 'CrUX eligible observations; sample size not supplied; metric populations may differ',
                              'period_note': 'Aggregation window, not proof of daily coverage or individual measurements'})
    return 'pass', 'Identified field cohort and aggregation period; no claim of complete population', raw


def field_values(raw, observation):
    values, missing = {}, []
    metrics = raw['record'].get('metrics', {})
    for label, (key, unit, good, poor) in FIELD_METRICS.items():
        try:
            value = metrics[key]['percentiles']['p75']
            parsed = number(value, field=True, cls=label == 'CLS')
            quality = 'good' if parsed <= good else 'poor' if parsed > poor else 'needs-improvement'
            values[label] = {'p75': str(parsed), 'raw_value': value, 'unit': unit, 'classification': quality}
        except (Unknown, KeyError, TypeError, ValueError, InvalidOperation) as error:
            missing.append(label)
            values[label] = {'classification': 'unknown', 'reason': str(error)}
    observation['metrics'] = values
    observation['field_quality'] = ('unknown' if missing else 'good' if all(v['classification'] == 'good' for v in values.values())
                                    else 'poor' if any(v['classification'] == 'poor' for v in values.values()) else 'needs-improvement')
    return values, missing


def review_header(review, digests, observed):
    need(isinstance(review, dict) and text(review.get('reviewer')), 'Missing supplied reviewer identity')
    need(review.get('provenance') in ('synthetic-exercise', 'supplied-review'), 'Missing explicit review provenance')
    need(review.get('source_sha256') == digests, 'Review does not bind these exact original reports')
    need(tsep.timestamp(review['observed_at']) <= observed, 'Review postdates assessment')


def field_assess(target, rule, observation):
    result, reason, raw = cohort(target, observation)
    if result != 'pass':
        return (result, reason) if rule == 'TS34-A01' else ('inconclusive', reason)
    values, missing = field_values(raw, observation)
    if rule == 'TS34-A01':
        return result, reason
    review = target.get('field_review', {})
    # A directly bound contradictory classification survives other missing metrics.
    if isinstance(review, dict) and review.get('source_sha256') == observation['source_sha256']:
        supplied = review.get('metrics', {})
        if isinstance(supplied, dict):
            for metric, value in values.items():
                claimed = supplied.get(metric, {})
                if isinstance(claimed, dict) and 'classification' in claimed and metric not in missing:
                    if claimed['classification'] != value['classification']:
                        return 'fail', 'Supplied classification contradicts original p75 for ' + metric
    need(not missing, 'Missing/unqualified p75 metrics: '+', '.join(missing)+'; FID/TBT are not INP')
    if rule == 'TS34-A02':
        return 'pass', 'Three p75 metrics classified; poor performance does not fail documentation quality'
    _, observed = plan_for(target, 'field')
    review_header(review, observation['source_sha256'], observed)
    need(tsep.timestamp(review['observed_at']) >= tsep.timestamp(target['field']['observed_at']), 'Review predates source acquisition')
    supplied = review.get('metrics')
    need(isinstance(supplied, dict) and set(supplied) == set(FIELD_METRICS), 'Review must retain each metric')
    for label, value in supplied.items():
        need(isinstance(value, dict) and text(value.get('reason')) and text(value.get('action'))
             and value.get('classification') == values[label]['classification'], 'Incomplete decision for '+label)
    observation['review_provenance'] = review['provenance']
    return 'pass', 'Supplied metric decisions retained; authorship and judgment are not independently verified'


def laboratory(target, observation):
    plan, observed = plan_for(target, 'lab')
    evidence = target['lab']
    need(evidence.get('reader') == 'lighthouse-json-v1', 'Unqualified lab reader; mixed PSI must be separated first')
    runs = evidence.get('runs')
    count = plan.get('run_count')
    need(type(count) is int and 2 <= count <= 10, 'Declare 2–10 lab runs; repeated observations are not field data')
    need(isinstance(runs, list) and len(runs) == count, 'Missing/extra lab runs against prior plan')
    values = {k: [] for k in LAB_METRICS}; digests = []; times = []
    for run in runs:
        raw, digest = original(run, observed); digests.append(digest)
        need('runtimeError' not in raw or raw['runtimeError'] is None, 'Lighthouse runtime error retained')
        need(raw.get('gatherMode') == 'navigation', 'Only explicit Lighthouse navigation reports are qualified')
        version = raw.get('lighthouseVersion')
        need(text(version) and re.fullmatch(r'\d+\.\d+\.\d+', version), 'Unqualified Lighthouse version')
        need(version == plan.get('lighthouse_version'), 'Lighthouse version differs from plan')
        requested, final = raw.get('requestedUrl'), raw.get('finalDisplayedUrl', raw.get('finalUrl'))
        need(not ('finalDisplayedUrl' in raw and 'finalUrl' in raw) or raw['finalDisplayedUrl'] == raw['finalUrl'],
             'Ambiguous lab final URL fields')
        need(text(requested) and text(final), 'Missing lab requested/final URL')
        if requested != plan.get('requested_url') or final != plan.get('final_url') or requested != target['url']:
            return 'fail', 'Measured requested/final URL contradicts the declared laboratory target', None
        fetched = tsep.timestamp(raw['fetchTime']).astimezone(timezone.utc); times.append(raw['fetchTime'])
        need(fetched <= tsep.timestamp(run['observed_at']) <= observed, 'Lab timestamps are inconsistent')
        need(tsep.timestamp(target['intent']['declared_at']) <= fetched, 'Laboratory plan postdates run')
        need((observed.date()-fetched.date()).days <= plan['max_age_days'], 'Lab run exceeds declared age')
        settings = raw.get('configSettings', {})
        need(isinstance(settings, dict) and all(k in settings and k in plan.get('settings', {}) for k in SETTING_KEYS),
             'Missing lab emulation/throttling settings')
        # Only presentation output is irrelevant to collection. Retain and compare
        # every other setting, including cache reset, headers and blocked resources.
        actual_settings = {k: v for k, v in settings.items() if k != 'output'}
        planned_settings = {k: v for k, v in plan['settings'].items() if k != 'output'}
        need(json.dumps(actual_settings, sort_keys=True) == json.dumps(planned_settings, sort_keys=True),
             'Lab collection settings differ from plan; not comparable')
        need(type(settings['disableStorageReset']) is bool
             and isinstance(settings['throttling'], dict) and isinstance(settings['screenEmulation'], dict)
             and text(settings['emulatedUserAgent'])
             and settings['throttlingMethod'] in ('simulate', 'devtools', 'provided')
             and (settings['blockedUrlPatterns'] is None or isinstance(settings['blockedUrlPatterns'], list))
             and (settings['extraHeaders'] is None or isinstance(settings['extraHeaders'], dict)),
             'Malformed laboratory collection settings')
        need(settings['formFactor'] == plan.get('form_factor') and settings['formFactor'] in ('mobile', 'desktop'),
             'Laboratory device differs or is unqualified')
        environment = raw.get('environment', {})
        need(text(environment.get('hostUserAgent')) and text(environment.get('networkUserAgent'))
             and environment['hostUserAgent'] == plan.get('host_user_agent')
             and environment['networkUserAgent'] == plan.get('network_user_agent'), 'Browser/client identity differs or is missing')
        for label, (key, unit) in LAB_METRICS.items():
            metric = raw['audits'][key]
            need(metric.get('numericUnit') == unit and metric.get('scoreDisplayMode') not in ('error', 'notApplicable'),
                 'Unqualified lab metric/unit: '+label)
            values[label].append(number(metric.get('numericValue')))
    need(len(set(digests)) == count and len({tsep.timestamp(t) for t in times}) == count,
         'Duplicated run does not establish repeated measurement')
    observation.update(source_sha256=digests, measured_at=times, metrics={k: {'values': [str(v) for v in nums],
        'median': str(statistics.median(nums)), 'minimum': str(min(nums)), 'maximum': str(max(nums)),
        'unit': LAB_METRICS[k][1]} for k, nums in values.items()},
        field_quality='not-assessed', inp='not-measured', repeats=count,
        repeatability_note='Same declared setup with observed spread, not statistical confidence or future reproducibility')
    return 'pass', 'Repeated laboratory measurements retain context and dispersion; TBT is not INP', digests


def lab_assess(target, rule, observation):
    try:
        result, reason, digests = laboratory(target, observation)
    except (Unknown, tsep.Invalid, KeyError, TypeError, ValueError, AttributeError, InvalidOperation, OverflowError, RecursionError) as error:
        result, reason, digests = 'inconclusive', str(error), None
    if rule == 'TS35-A01':return result, reason
    review = target.get('lab_review', {})
    # An explicit field/INP substitution remains wrong even if a separate
    # setting or measurement is unknown. Establish its own source binding.
    if digests is None and isinstance(review, dict) and (review.get('claims_field_cwv') is True or review.get('claims_inp_from_tbt') is True):
        try:
            observed = tsep.timestamp(target['observed_at'])
            runs = target['lab']['runs']
            need(isinstance(runs, list) and 0 < len(runs) <= 10, 'Missing source reports')
            originals = [original(run, observed) for run in runs]
            need(all(text(raw.get('lighthouseVersion')) for raw, _ in originals), 'Unidentified lab originals')
            digests = [digest for _, digest in originals]
        except (Unknown, tsep.Invalid, KeyError, TypeError, ValueError, AttributeError, RecursionError):
            digests = None
    if isinstance(review, dict) and review.get('source_sha256') == digests and digests is not None:
        if review.get('claims_field_cwv') is True or review.get('claims_inp_from_tbt') is True:
            observation.update(source_sha256=digests, context_outcome=result, context_reason=reason)
            return 'fail', 'Supplied interpretation falsely substitutes laboratory measures for field CWV/INP'
    need(result == 'pass', 'Laboratory context is not established')
    _, observed = plan_for(target, 'lab')
    review_header(review, digests, observed)
    need(tsep.timestamp(review['observed_at']) >= max(tsep.timestamp(r['observed_at']) for r in target['lab']['runs']),
         'Lab review predates source acquisition')
    need(review.get('claims_field_cwv') is False and review.get('claims_inp_from_tbt') is False,
         'Declare the limits of the laboratory interpretation')
    need(text(review.get('hypothesis')) and text(review.get('next_measurement')), 'Missing supplied hypothesis or verification action')
    selected = review.get('metrics')
    need(isinstance(selected, list) and selected and all(k in LAB_METRICS for k in selected)
         and len(set(selected)) == len(selected), 'Hypothesis must reference measured laboratory metrics')
    observation['review_provenance'] = review['provenance']
    return 'pass', 'Supplied diagnostic hypothesis retained, not a demonstrated cause or field result'


def assess(target, rule, *, diagnostics=None):
    observation = {'reader': 'performance-evidence-v1', 'rule': rule,
                   'metric_quality_distinct_from_method': True,
                   'limitations': 'Supplied reports/reviews not authenticated; no new measurement, ranking or site-wide conclusion.'}
    try:
        result, reason = field_assess(target, rule, observation) if rule.startswith('TS34-') else lab_assess(target, rule, observation)
    except (Unknown, tsep.Invalid, KeyError, TypeError, ValueError, AttributeError, InvalidOperation, OverflowError, RecursionError) as error:
        result, reason = 'inconclusive', str(error)
    observation.update(outcome=result, reason=reason)
    if diagnostics is not None:diagnostics.append(observation)
    return result, 'Performance documentation / documentation de performance: '+json.dumps(observation,ensure_ascii=False,sort_keys=True)
