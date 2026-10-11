"""Bounded TS41 supplied pipeline evidence. Apache-2.0.

Never execute a supplied command. Process adequacy is not underlying SEO health.
"""
from datetime import timedelta
import hashlib
import json
import re

import tsep
from conformance.http import Unknown, need
from conformance.agent_policy import digest, identifier, present, ERRORS
from conformance.agent_access import reviewed
from experiments.rendered_canonical import supported_url

VERSION = '1'
READER = 'release-invariants-v1'
RULES = tuple('TS%s-A%02d' % (c, i) for c, n in
              [('01',2),('02',2),('04',2),('07',3),('10',4),('34',3),('35',2),('42',3),('43',3),('44',3)]
              for i in range(1, n+1))
POLICY = dict(pass_=0, fail=1, inconclusive=2, pre='block', post='hold', overrides='forbidden')
POLICY['pass'] = POLICY.pop('pass_')
KINDS = ('trigger-negative','negative-held','trigger-pre','blocked','deployed',
         'trigger-post','post-accepted','post-held','override')


class Contradiction(ValueError):
    pass


def require_match(condition, why):
    if not condition: raise Contradiction(why)


def fingerprint(value):
    return isinstance(value, str) and re.fullmatch('[a-f0-9]{64}', value)


def raw_json(text, claimed):
    need(isinstance(text, str) and 0 < len(text.encode()) <= 512*1024,
         'Missing or excessive UTF-8 native JSON')
    need(hashlib.sha256(text.encode()).hexdigest() == claimed, 'Native JSON fingerprint mismatch')
    return tsep.parse_json(text.encode())


def unique(rows, field, value):
    need(isinstance(rows, list), 'Missing record list')
    selected = [r for r in rows if isinstance(r, dict) and r.get(field) == value]
    need(len(selected) == 1, 'Missing or ambiguous '+field+': '+str(value))
    return selected[0]


def plan_binding(t):
    return digest({k:t[k] for k in ('url','intent')})


def review_binding(t):
    return digest({k:t[k] for k in ('url','intent','release_events','release_runs')})


def header(t):
    p=t['intent']['release'];need(p['reader']==READER,'Explicit supported release reader required')
    start,end,observed=(tsep.timestamp(v) for v in (p['window_start'],p['window_end'],t['observed_at']))
    need(tsep.timestamp(t['intent']['declared_at']) <= start < end <= observed and end-start <= timedelta(days=31),
         'Prior plan and bounded completed window required')
    need(all(present(t.get('context',{}).get(k)) for k in ('network','bounds','tool','tool_version')),
         'Missing supplied collection context')
    need(p['policy']==POLICY and all(type(p['policy'][k]) is int for k in ('pass','fail','inconclusive')),
         'First profile requires explicit strict block/hold policy and distinct exit codes')
    population=p['population'];matrix=p['matrix'];cmd=p['command'];negative=p['negative']
    need(isinstance(population,list) and 1 <= len(population) <= 16 and
         all(isinstance(d,dict) and identifier(d.get('id')) and all(fingerprint(d.get(k))
             for k in ('before_artifact','candidate_artifact')) for d in population), 'Bounded identified deployment population required')
    need(len({d['id'] for d in population})==len(population),'Duplicate deployment attempt')
    need(isinstance(matrix,list) and 1 <= len(matrix) <= 128,'Bounded explicit invariant matrix required')
    need(all(isinstance(c,dict) and identifier(c.get('id')) and c.get('rule_id') in RULES
         and supported_url(c.get('target')) and fingerprint(c.get('intent_sha256'))
         and fingerprint(c.get('context_sha256')) for c in matrix),'Unqualified matrix cell or recursive/unsupported rule')
    need(len({c['id'] for c in matrix})==len(matrix) and
         len({(c['rule_id'],c['target']) for c in matrix})==len(matrix),'Duplicate matrix cell')
    need(isinstance(cmd,dict) and isinstance(cmd.get('argv'),list) and 1 <= len(cmd['argv']) <= 32
         and all(isinstance(x,str) and x.strip() and len(x)<=1024 and '\0' not in x for x in cmd['argv'])
         and present(cmd.get('version')) and fingerprint(cmd.get('sha256')) and fingerprint(cmd.get('environment')),
         'Declare bounded command/tool/environment identities; they will never be executed')
    need(identifier(negative.get('id')) and negative['id'] not in {d['id'] for d in population}
         and fingerprint(negative.get('artifact_sha256')),'Distinct identified negative rehearsal required')
    failures=negative['required_failures']
    need(isinstance(failures,list) and failures and len(failures)<=len(matrix) and
         all(isinstance(x,str) and x in {c['id'] for c in matrix} for x in failures)
         and len(set(failures))==len(failures),'Declare distinct negative-case failing cells')
    return p,start,end,observed


def review(t,p,start,end,observed,prior=False):
    r=t.get('release_plan_review' if prior else 'release_review')
    earliest=tsep.timestamp(t['intent']['declared_at']) if prior else end
    if not prior:
        earliest=max(end,tsep.timestamp(t['release_events']['exported_at']))
    reviewed(r,plan_binding(t) if prior else review_binding(t),earliest,start if prior else observed)
    need(r.get('complete') is True,'Review incomplete')
    need(r.get('judgment') in ('supported','contradiction','unknown'),'Missing review judgment')
    require_match(r['judgment']!='contradiction','Supplied bound review rejects the scope or attribution')
    need(r['judgment']=='supported','Review remains unknown')
    if not prior:
        need(all(r.get(k) is True for k in ('population_complete','attribution_supported','clock_supported')),
             'Population completeness, runner attribution or clocks not qualified')
    return {'reviewer':r['reviewer'],'review_provenance':r['provenance'],'identity':'supplied, not authenticated'}


class Evidence:
    def __init__(self,t,p,start,end,observed):
        self.t,self.p,self.start,self.end,self.observed=t,p,start,end,observed
        self.cache={};self.notes=[]

    def event_rows(self):
        if 'events' in self.cache:return self.cache['events']
        review(self.t,self.p,self.start,self.end,self.observed)
        packet=self.t['release_events'];text=packet['raw_jsonl']
        need(isinstance(text,str) and 0 < len(text.encode()) <= 512*1024 and
             hashlib.sha256(text.encode()).hexdigest()==packet['sha256'],'Missing or invalid journal fingerprint/bound')
        lines=text.splitlines();need(0 < len(lines) <= 128 and all(s.strip() for s in lines),'Bounded nonempty JSONL records required')
        rows=[tsep.parse_json(s.encode()) for s in lines];ids=[];previous=self.start
        allowed={d['id'] for d in self.p['population']}|{self.p['negative']['id']}
        for e in rows:
            need(isinstance(e,dict) and identifier(e.get('id')) and e.get('kind') in KINDS
                 and e.get('attempt_id') in allowed and identifier(e.get('run_id')) and fingerprint(e.get('artifact_sha256')),
                 'Unqualified event identity/type/population')
            date=tsep.timestamp(e['at']);need(previous <= date <= self.end,'Journal clock/order outside window')
            previous=date;ids.append(e['id'])
        need(len(set(ids))==len(ids),'Duplicate event IDs')
        need(previous <= tsep.timestamp(packet['exported_at']) <= self.observed,'Journal export outside observation dates')
        self.cache['events']=rows;return rows

    def run_records(self):
        runs=self.t['release_runs'];need(isinstance(runs,list) and 1 <= len(runs) <= 64,'Bounded supplied execution receipts required')
        ids=[r.get('id') for r in runs if isinstance(r,dict)]
        need(len(ids)==len(runs) and all(identifier(i) for i in ids) and len(set(ids))==len(ids),'Duplicate/unqualified execution IDs')
        total=0
        for r in runs:
            for k in ('input_json','stdout_json'):
                v=r.get(k);need(isinstance(v,str),'Missing native input/output');total+=len(v.encode())
        need(total <= 4*1024*1024,'Cumulative native input/output exceeds4MiB')
        return runs

    def journal_coverage(self):
        """Every retained event must belong to exactly one declared run phase."""
        runs=self.run_records();events=self.event_rows()
        need(all(e['run_id'] in {r['id'] for r in runs} for e in events),
             'Journal contains an event without an execution receipt')
        actions={'negative':('negative-held',),'pre':('blocked','deployed'),
                 'post':('post-accepted','post-held')}
        for r in runs:
            phase=r.get('phase');need(phase in actions,'Unsupported execution phase')
            selected=[e for e in events if e['run_id']==r['id'] and e['kind']!='override']
            triggers=[e for e in selected if e['kind']=='trigger-'+phase]
            effects=[e for e in selected if e['kind'] in actions[phase]]
            need(len(selected)==2 and len(triggers)==len(effects)==1,
                 'Missing, duplicate or phase-incompatible journal event for '+r['id'])
        return 'pass','Every retained non-override event belongs to one execution phase'

    def execution(self,attempt,phase):
        key=(attempt['id'],phase)
        if key in self.cache:return self.cache[key]
        runs=self.run_records();found=[r for r in runs if r.get('attempt_id')==attempt['id'] and r.get('phase')==phase]
        need(len(found)==1,'Missing or duplicate execution for '+str(key));r=found[0]
        need(r.get('complete') is True,'Execution incomplete; preserve partial receipt')
        a,b=tsep.timestamp(r['started_at']),tsep.timestamp(r['ended_at'])
        need(self.start <= a <= b <= self.end,'Execution clock outside plan window')
        expected_artifact=attempt.get('artifact_sha256',attempt.get('candidate_artifact'))
        need(fingerprint(r.get('artifact_sha256')),'Missing artifact identity')
        require_match(r['artifact_sha256']==expected_artifact,'Execution names a different artifact')
        require_match(r.get('command')==self.p['command'],'Execution command/tool/environment differs from prior plan')
        need(identifier(r.get('trigger_event_id')),'Missing trigger event ID')
        data=raw_json(r['input_json'],r['input_sha256']);supplied=raw_json(r['stdout_json'],r['stdout_sha256'])
        need(isinstance(data,dict) and data.get('input_version') in ('1','2') and isinstance(data.get('rules'),list)
             and data['rules'] and all(x in RULES for x in data['rules']) and len(set(data['rules']))==len(data['rules']),
             'Unsupported native input or recursive rule')
        targets=data.get('targets');need(isinstance(targets,list) and 1 <= len(targets) <= 100,'Missing native targets')
        need(all(isinstance(x,dict) and supported_url(x.get('url')) for x in targets),'Invalid native target')
        need(len({x['url'] for x in targets})==len(targets),'Duplicate native target')
        desired={(c['rule_id'],c['target']) for c in self.p['matrix']}
        actual={(rid,x['url']) for rid in data['rules'] for x in targets}
        need(actual==desired,'Native execution matrix is incomplete or outside prior selection')
        for x in targets:
            need(a <= tsep.timestamp(x['observed_at']) <= b,'Native observation not within its execution')
            need(tsep.timestamp(x['intent']['declared_at']) <= tsep.timestamp(self.t['intent']['declared_at']),
                 'Native invariant intent not declared before release plan')
            for c in self.p['matrix']:
                if c['target']==x['url']:
                    require_match(digest(x['intent'])==c['intent_sha256'],'Native expectation differs from frozen invariant intent')
                    require_match(digest(x['context'])==c['context_sha256'],'Native context differs from frozen comparison context')
        need(isinstance(supplied,list) and len(supplied)==len(desired),'Missing or excessive native output cells')
        def project(rows):
            result={}
            for row in rows:
                need(isinstance(row,dict) and row.get('outcome') in ('pass','fail','inconclusive','not-applicable')
                     and present(row.get('reason')),'Unqualified native result')
                pair=(row['rule_id'],row['target']);need(pair in desired and pair not in result,'Duplicate or foreign output cell')
                result[pair]=row['outcome']
            need(set(result)==desired,'Incomplete output matrix');return result
        original=project(supplied)
        # This executes only our bounded interpreter, never argv from evidence.
        from conformance.evaluate import evaluate
        computed=evaluate(data);current=project(computed)
        mismatches=[pair for pair in desired if current[pair]!=original[pair]]
        certain=[pair for pair in mismatches if current[pair] in ('pass','fail')]
        outcomes=list(current.values())
        decision='fail' if 'fail' in outcomes else ('pass' if all(x=='pass' for x in outcomes) else 'inconclusive')
        result={'receipt':r,'started_at':a,'ended_at':b,'supplied':supplied,'computed':computed,
                'decision':decision,'mismatches':mismatches,'certain_mismatches':certain,'outcomes':current}
        self.cache[key]=result
        self.notes.append({'attempt':attempt['id'],'phase':phase,'run_id':r['id'],'artifact_sha256':r['artifact_sha256'],
                           'underlying_decision':decision,'supplied_results':supplied,'recalculated_results':computed,
                           'comparison':'Exact selected cells; no site-wide or causal inference'})
        return result

    def trigger(self,v,kind):
        r=v['receipt'];e=unique(self.event_rows(),'id',r['trigger_event_id'])
        require_match(e['attempt_id']==r['attempt_id'] and e['run_id']==r['id'] and e['kind']==kind
                      and e['artifact_sha256']==r['artifact_sha256'],'Trigger does not identify this execution/artifact')
        require_match(tsep.timestamp(e['at']) <= v['started_at'],'Trigger postdates execution')
        return e

    def actions(self,v,kinds):
        r=v['receipt'];rows=[e for e in self.event_rows() if e['attempt_id']==r['attempt_id'] and e['kind'] in kinds]
        need(len(rows)==1,'Missing/ambiguous action for '+r['id']);e=rows[0]
        require_match(e['run_id']==r['id'] and e['artifact_sha256']==r['artifact_sha256'],'Action linked to other execution/artifact')
        require_match(v['ended_at'] <= tsep.timestamp(e['at']),'Action predates completed execution')
        return e


def prerequisite(fn):
    """A rejected binding cannot qualify a later behavioral accusation."""
    try: return fn()
    except Contradiction as error: raise Unknown(str(error)) from error


def attempt_check(fn):
    try: return fn()
    except Contradiction as e: return 'fail',str(e)
    except ERRORS as e: return 'inconclusive',str(e)


def combine(rows):
    outcomes=[r['outcome'] for r in rows]
    return 'fail' if 'fail' in outcomes else ('inconclusive' if not outcomes or 'inconclusive' in outcomes else 'pass')


def assess(t,rule,*,diagnostics=None):
    notes=[];rows=[]
    def check(label,fn):
        out,reason=attempt_check(fn);rows.append({'subject':label,'outcome':out,'reason':reason});return out
    try:
        p,start,end,observed=header(t);e=Evidence(t,p,start,end,observed)
        if rule=='TS41-A01':
            def prior():
                info=review(t,p,start,end,observed,prior=True);notes.append(info)
                return 'pass','Prior supplied scope review; representativeness and identity not independently authenticated'
            check('prior-scope',prior)
        else:
            def ledger():
                e.event_rows();return 'pass','Supplied complete population/journal reviewed and bound'
            check('journal-attribution',ledger)
            attempts=[(p['negative'],'negative')]+[(d,'pre') for d in p['population']]
            # Post coverage depends on a positive applied event, never an absent line.
            for d in p['population']:
                try:
                    pre=e.execution(d,'pre');action=e.actions(pre,('blocked','deployed'))
                    if action['kind']=='deployed':attempts.append((d,'post'))
                except (Contradiction,)+ERRORS as error:
                    rows.append({'subject':d['id']+'-lifecycle','outcome':'inconclusive','reason':str(error)})
            check('journal-coverage',e.journal_coverage)
            if rule=='TS41-A02':
                def inventory():
                    wanted={(a['id'],phase) for a,phase in attempts};actual=[(r.get('attempt_id'),r.get('phase')) for r in e.run_records()]
                    need(len(actual)==len(wanted) and set(actual)==wanted,'Unplanned, duplicate or missing execution')
                    need(not any(x['kind']=='override' for x in e.event_rows()),'Override flow outside strict coverage profile')
                    return 'pass','Exact declared attempted execution population'
                check('execution-population',inventory)
                for a,phase in attempts:
                    def coverage(a=a,phase=phase):
                        v=e.execution(a,phase);e.trigger(v,'trigger-'+phase)
                        require_match(not v['certain_mismatches'],'Conclusive recalculation contradicts supplied output')
                        need(not v['mismatches'],'Recalculation differs with unresolved runtime/method coverage')
                        if phase=='post':
                            pre=e.execution(a,'pre');action=e.actions(pre,('deployed',));require_match(tsep.timestamp(action['at']) <= v['started_at'],'Post run predates deployment')
                        return 'pass','Complete native execution; supplied/recomputed outcomes agree, including retained unknowns'
                    check(a['id']+'/'+phase,coverage)
            elif rule=='TS41-A03':
                for a,phase in attempts:
                    def behavior(a=a,phase=phase):
                        v=prerequisite(lambda:e.execution(a,phase));r=v['receipt']
                        # A conclusively corrected false output can still expose a masked failure.
                        need(not v['mismatches'] or v['certain_mismatches'],'Unknown recalculation cannot accuse an old result')
                        need(type(r.get('exit_code')) is int,'Missing native process exit code')
                        require_match(r['exit_code']==p['policy'][v['decision']],
                                      'Process exit contradicts underlying decision: '+v['decision'])
                        if phase=='negative':
                            byid={c['id']:v['outcomes'][(c['rule_id'],c['target'])] for c in p['matrix']}
                            need(all(byid[k]!='inconclusive' for k in p['negative']['required_failures']),'Required negative cell unverified')
                            require_match(all(byid[k]=='fail' for k in p['negative']['required_failures']),'Negative rehearsal does not demonstrate its planned contradiction')
                        return 'pass','Process code preserves fail/unknown; no all-pass promotion'
                    check(a['id']+'/'+phase+'/exit',behavior)
                    def action_check(a=a,phase=phase):
                        v=prerequisite(lambda:e.execution(a,phase));need(not v['mismatches'],'Unqualified native output for action attribution');prerequisite(lambda:e.trigger(v,'trigger-'+phase))
                        if phase=='negative':
                            action=e.actions(v,('negative-held',));need(v['decision']=='fail','Negative rehearsal not conclusively failed')
                            for d in p['population']:
                                pre=e.execution(d,'pre');require_match(tsep.timestamp(action['at']) <= pre['started_at'],'Negative rehearsal postdates selected attempt')
                        else:
                            action=e.actions(v,('blocked','deployed') if phase=='pre' else ('post-accepted','post-held'))
                            wanted=('deployed' if v['decision']=='pass' else 'blocked') if phase=='pre' else ('post-accepted' if v['decision']=='pass' else 'post-held')
                            require_match(action['kind']==wanted,'Recorded action contradicts declared '+phase+' policy for '+v['decision'])
                        return 'pass','Explicit phase-specific action retained; no production authentication'
                    check(a['id']+'/'+phase+'/action',action_check)
                def overrides():
                    require_match(not any(x['kind']=='override' for x in e.event_rows()),'Observed override contradicts strict no-override plan')
                    return 'pass','No override in the reviewed supplied journal; no claim beyond this inventory'
                check('override-policy',overrides)
            else:raise Unknown('Unsupported release invariant rule')
            notes.extend(e.notes)
        outcome=combine(rows)
    except Contradiction as error:
        outcome='fail';rows.append({'subject':'plan','outcome':outcome,'reason':str(error)})
    except ERRORS as error:
        outcome='inconclusive';rows.append({'subject':'plan','outcome':outcome,'reason':str(error)})
    detail={'reader':READER,'rule':rule,'outcome':outcome,'rows':rows,'executions':notes,
            'limitations':'Process evidence only; supplied runner/reviewer and journal completeness not authenticated. Underlying SEO failures/unknowns remain distinct. No remote CI, site-wide conformity or causal claim.'}
    if diagnostics is not None:diagnostics.append(detail)
    return outcome,'Release process / dispositif de déploiement: '+json.dumps(detail,ensure_ascii=False,sort_keys=True)
