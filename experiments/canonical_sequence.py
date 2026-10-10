#!/usr/bin/env python3
"""Ordered experimental canonical records. No sequence verdict. Apache-2.0."""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import tsep
from experiments import rendered_canonical_v2 as candidate
from provenance.runtime import loaded_sources

VERSION = '1'
METHOD = 'canonical-state-sequence-v1'


def sources():
    result = candidate.sources()
    result.update(loaded_sources(ROOT, {'experiments/canonical_sequence.py': sys.modules[__name__]}))
    return result


def assess(registration, page_id, records):
    """Compare each received snapshot; record missing ones, never collapse history.

    Transport, order of execution and chronology are checked by the laboratory,
    not established by this pure function or by an internally consistent digest.
    """
    tsep.require(isinstance(registration, dict) and registration.get('method') == METHOD and
                 registration.get('kind') == 'predeclared-canonical-laboratory' and
                 registration.get('version') == '1', 'Unsupported sequence registration')
    pages = [p for p in registration['pages'] if p['id'] == page_id]
    tsep.require(len(pages) == 1, 'Unknown/ambiguous page')
    ids = pages[0]['task_ids']
    tsep.require(isinstance(ids, list) and 1 <= len(ids) <= 32 and len(set(ids)) == len(ids), 'Invalid sequence task ids')
    tsep.require(isinstance(records, dict) and set(records) == set(ids), 'Every planned state needs a record or explicit missing reason')
    rows = []; contradictions = []; undetermined = []; missing = []
    for task_id in ids:
        tasks = [t for t in registration['tasks'] if t['id'] == task_id]
        tsep.require(len(tasks) == 1 and tasks[0]['page_id'] == page_id and tasks[0]['url'] == pages[0]['url'], 'Task/page mismatch')
        task = tasks[0]; entry = records[task_id]
        tsep.require(isinstance(entry, dict) and set(entry) == {'snapshot', 'missing_reason'}, 'Invalid sequence entry')
        if entry['snapshot'] is None:
            reason = entry['missing_reason']
            tsep.require(isinstance(reason, str) and reason.strip() and len(reason) <= 4096, 'Missing state needs reason')
            rows.append({'id': task['state_id'], 'task_id': task_id, 'availability': 'not-received', 'reason': reason, 'assessment': None})
            missing.append(task['state_id']); continue
        tsep.require(entry['missing_reason'] is None, 'Received state cannot also be missing')
        intent = dict(task['intent'], format='rendered-canonical-intent', version='2', mode=candidate.MODE,
                      document_url=task['url'], record_sha256=candidate.core.digest(entry['snapshot']),
                      registration_sha256=candidate.core.digest(registration), case_id=task_id)
        result = candidate.assess(entry['snapshot'], intent, registration)
        rows.append({'id': task['state_id'], 'task_id': task_id, 'availability': 'received', 'assessment': result})
        if result['outcome'] == 'contradiction-in-record': contradictions.append(task['state_id'])
        if result['outcome'] == 'undetermined': undetermined.append(task['state_id'])
    last = rows[-1]
    return {'kind': 'canonical-state-sequence', 'version': VERSION, 'normative': False, 'page_id': page_id,
            'states': rows, 'contradiction_state_ids': contradictions,
            'at_least_one_observed_contradiction': bool(contradictions),
            'undetermined_state_ids': undetermined, 'missing_state_ids': missing,
            'last_planned_state': {'id': last['id'], 'availability': last['availability'],
                'outcome': last['assessment']['outcome'] if last['assessment'] else None},
            'all_planned_states_received': not missing, 'continuous_stability': 'not-assessed',
            'execution_validation': 'not-performed-by-sequence-comparison'}
