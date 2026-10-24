"""Explicit runtime-sensitive TS25 fixture extension; no production guard import."""
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT/'tests/fixtures/critical-presence-runtime-boundaries-v1.json'


def compact(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')


def fixture():
    raw = PATH.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == PATH.with_suffix('.sha256').read_text().strip()
    data = json.loads(raw)
    assert hashlib.sha256((ROOT/data['historical_fixture']).read_bytes()).hexdigest() == data['historical_sha256']
    return data


def public_bytes(notes):
    return sum(len((json.dumps(n, ensure_ascii=False, indent=2)+'\n').encode('utf-8')) for n in notes)


def historical_expectation(row, notes):
    """Only two historical exact-byte rows depend on recorded runtime identities."""
    match = next((r for r in fixture()['historical'] if r['id'] == row['id']), None)
    if match is None:
        return row['expected_public'], row.get('expected_public_diagnostic_bytes')
    normalized = copy.deepcopy(notes)
    found = []
    for group in normalized:
        for note in group['observations']:
            for key, inventory in note.get('inventories', {}).items():
                if 'supervisor' not in inventory:
                    continue
                assert key in ('url-0', 'url-1')
                assert set(inventory['runtime']) == {'node', 'v8', 'ada', 'icu', 'unicode'}
                assert isinstance(inventory['supervisor']['python'], str)
                inventory['supervisor']['python'] = '<runtime-version>'
                for field in inventory['runtime']:
                    assert isinstance(inventory['runtime'][field], str)
                    inventory['runtime'][field] = '<runtime-version>'
                found.append(key)
    assert sorted(found) == ['url-0', 'url-1'] and len(found) == match['identity_locations']
    assert hashlib.sha256(compact(normalized)).hexdigest() == match['normalized_observations_sha256']
    size = public_bytes(notes)
    return ('C' if size <= 4194304 else 'technical-refusal'), size


def calibrated(row, fixtures, materialize, evaluate):
    """Linear byte calibration, once; literal outcomes remain authored in fixture."""
    recipe = {'mutation':'scope-padding', 'padding':0, 'review_extra':0}
    notes = []
    evaluate(materialize(recipe, fixtures), source_observations=notes)
    padding, remainder = divmod(row['bytes']-public_bytes(notes), 2)
    assert padding >= 0 and remainder in (0, 1)
    recipe.update(padding=padding, review_extra=remainder)
    return materialize(recipe, fixtures)
