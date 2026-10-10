"""Versioned, closed exceptions for replay diagnostics; never changes evidence."""
import hashlib
import json
import re

PROFILES = ('exact', 'python-supervisor-v1')
MAX_DIFFERENCES = 1000
_MISSING = object()


def _python(runtime):
    if not isinstance(runtime, dict) or runtime.get('implementation') != 'CPython':
        return None
    version = runtime.get('python')
    if isinstance(version, str) and re.fullmatch(r'3\.(?:9|[1-9][0-9]+)\.[0-9]+', version):
        return version
    return None


def _paths(document):
    """Only named worker slots of existing, named policy/rule pairs qualify."""
    paths = set()
    if not isinstance(document, dict) or not isinstance(document.get('observations'), list):
        return paths
    rule = document.get('rule_id')
    for index, observation in enumerate(document['observations']):
        if not isinstance(observation, dict):
            continue
        reader, version = observation.get('reader'), observation.get('policy_version')
        prefix = ('observations', index)

        def worker(path, identities, field):
            value = observation
            for key in path:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                elif isinstance(value, list) and type(key) is int and 0 <= key < len(value):
                    value = value[key]
                else:
                    return
            if (isinstance(value, dict) and all(value.get(k) == v for k, v in identities.items())
                    and isinstance(value.get('supervisor'), dict)
                    and isinstance(value['supervisor'].get(field), str)):
                paths.add(prefix + path + ('supervisor', field))

        http = {'kind': 'unapplied-http-source-tree', 'experiment_version': '1',
                'metadata_extension': '1', 'normative_effect': 'none'}
        if reader == 'html-tree-directives-v1' and version == '1' and rule in ('TS07-A01', 'TS07-A03'):
            worker(('inventory',), http, 'python_version')
        elif reader == 'html-tree-canonical-v1' and version == '1' and rule in ('TS10-A01', 'TS10-A02'):
            worker(('inventory',), dict(http, head_extension='1'), 'python_version')
        elif ((reader, version) in (('html-tree-links-v1', '1'), ('html-tree-links-v2', '2'))
              and rule == 'TS10-A04'):
            worker(('inventory',), {'kind': 'unapplied-link-elements', 'version': '1',
                                   'normative_effect': 'none'}, 'python')
            worker(('base_policy_metadata',), http, 'python_version')
            runs = observation.get('url_runs')
            if isinstance(runs, list):
                for run in range(len(runs)):
                    worker(('url_runs', run), {'kind': 'unapplied-url-resolution', 'version': '1',
                                              'normative_effect': 'none'}, 'python')
    return paths


def _summary(value):
    if value is _MISSING:
        return {'present': False}
    raw = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode('utf-8')
    return {'present': True, 'type': type(value).__name__, 'sha256': hashlib.sha256(raw).hexdigest()}


def compare(original, current, original_runtime, current_runtime, profile='exact'):
    """Strict typed JSON comparison; list order matters, object key order does not.

    Exceptions retain their exact values. Other differences carry typed hashes;
    the replay package retains both raw files. Over-budget differences fail closed.
    """
    if profile not in PROFILES:
        raise ValueError('Unknown replay comparison profile')
    permitted = (_paths(original) & _paths(current)) if profile == 'python-supervisor-v1' else set()
    before, after = _python(original_runtime), _python(current_runtime)
    differences = []
    complete = True
    stack = [((), original, current)]
    while stack:
        path, left, right = stack.pop()
        if type(left) is type(right):
            if isinstance(left, dict):
                stack.extend((path+(key,), left.get(key, _MISSING), right.get(key, _MISSING))
                             for key in sorted(set(left) | set(right), reverse=True))
                continue
            if isinstance(left, list):
                stack.extend((path+(i,), left[i] if i < len(left) else _MISSING,
                              right[i] if i < len(right) else _MISSING)
                             for i in reversed(range(max(len(left), len(right)))))
                continue
            if left == right:
                continue
        if len(differences) == MAX_DIFFERENCES:
            complete = False
            break
        allowed = (path in permitted and before is not None and after is not None
                   and type(left) is str and type(right) is str and left == before and right == after)
        item = {'pointer': '/'+'/'.join(str(k).replace('~', '~0').replace('/', '~1') for k in path),
                'allowed_python_supervisor_difference': allowed,
                'original': _summary(left), 'current': _summary(right)}
        if allowed:
            item.update(original_value=left, current_value=right)
        differences.append(item)
    return {'profile': profile, 'exact': complete and not differences,
            'match': complete and all(d['allowed_python_supervisor_difference'] for d in differences),
            'complete': complete, 'difference_limit': MAX_DIFFERENCES, 'differences': differences}
