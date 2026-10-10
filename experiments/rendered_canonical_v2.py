#!/usr/bin/env python3
"""Candidate 2 intent adapter; immutable candidate 1 comparison core. Apache-2.0."""
import copy
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import tsep
from experiments import rendered_canonical as core
from provenance import runtime

VERSION = '2'
MODE = 'predeclared-synthetic-laboratory'
EXTRA = {'registration_sha256', 'case_id'}


def sources():
    return dict(core.sources(), **runtime.loaded_sources(ROOT, {
        'experiments/rendered_canonical_v2.py': sys.modules[__name__]}))


def upgrade_intent_v1(intent):
    """Explicit adapter for old modes; never invent a predeclaration or edit input."""
    core.validate_intent(intent)
    if intent is None:
        return None
    return dict(copy.deepcopy(intent), version=VERSION, registration_sha256=None, case_id=None)


def assess(record, intent, registration=None):
    """Validate the declared plan binding; transport/chronology belong to the lab.

    The internal v1 mode adapter affects no comparison rule and is not a v1
    provenance claim. Returned intent/mode/version always describe this v2 call.
    """
    legacy = None
    if intent is not None:
        tsep.require(isinstance(intent, dict) and set(intent) == core.INTENT_KEYS | EXTRA
                     and intent['version'] == VERSION, 'Explicit v2 intent required')
        legacy = {k: copy.deepcopy(intent[k]) for k in core.INTENT_KEYS}
        legacy['version'] = core.VERSION
        if intent['mode'] == MODE:
            tsep.require(isinstance(registration, dict)
                         and registration.get('kind') == 'predeclared-canonical-laboratory'
                         and registration.get('version') == '1', 'Missing laboratory registration')
            tsep.require(intent['registration_sha256'] == core.digest(registration), 'Registration binding mismatch')
            tasks = [t for t in registration.get('tasks', []) if t['id'] == intent['case_id']]
            tsep.require(len(tasks) == 1, 'Unknown/ambiguous registered task')
            task = tasks[0]
            tsep.require(task['url'] == intent['document_url'] and
                         all(task['intent'][k] == intent[k] for k in
                             ('preferred_url', 'html_canonical_required', 'known_integrity_issues', 'state_label')),
                         'Intent differs from predeclared task')
            legacy['mode'] = 'authored-synthetic'
        else:
            tsep.require(intent['registration_sha256'] is None and intent['case_id'] is None,
                         'Non-predeclared mode cannot claim registration')
        core.validate_intent(legacy)
    result = core.assess(record, legacy)
    result.update(version=VERSION, mode=intent['mode'] if intent else None,
                  intent=copy.deepcopy(intent), comparison_core_version=core.VERSION,
                  registration_binding='declared-task-matches' if intent and intent['mode'] == MODE else 'not-claimed',
                  collection_validation='not-performed-by-comparison-adapter')
    return result
