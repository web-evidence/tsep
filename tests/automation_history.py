"""Exact inverses for closed historical checks; current rules are checked separately."""
import copy
import hashlib
import json
from pathlib import Path
import tsep

ROOT = Path(__file__).resolve().parents[1]


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(',', ':')).encode()).hexdigest()


def protocol_before_automation():
    raw = (ROOT/'provenance/v030-draft10-rule-baseline.json').read_bytes()
    if hashlib.sha256(raw).hexdigest() != 'c8c558db9983c99a5d7ab4e262e56b6c096a75904b1c79e584bedf538b26ab2d':
        raise ValueError('Changed automation historical baseline')
    previous = json.loads(raw)['controls']
    current = tsep.read_json(tsep.PROTOCOL_PATH)
    if current['version'] != '0.3.0-draft.10' or set(previous) != {'TS03','TS06','TS07'}:
        raise ValueError('Unexpected automation migration scope')
    if digest(current['controls']) != 'ce0f158217ca0b4c8faed2ea8a08e37ebb427743854e7109e5c84d277cbf8fea':
        raise ValueError('Undeclared current control delta')
    current['version'] = '0.3.0-draft.9'
    current['controls'] = [copy.deepcopy(previous.get(c['id'], c)) for c in current['controls']]
    if digest(current['controls']) != '621d1cd4124511ceeac965355221866a2c1ee0e4f4e1de1e678f3270361033db':
        raise ValueError('Projection does not restore the complete draft9 control inventory')
    return current


def method_before_automation():
    raw = (ROOT/'tests/fixtures/control-cases.json').read_bytes()
    overlay = tsep.read_json(ROOT/'provenance/public-automation-method-overlay-v1.json')
    if hashlib.sha256(raw).hexdigest() != overlay['current_sha256']:
        raise ValueError('Changed current method corpus')
    corpus = json.loads(raw)
    if corpus['protocol_version'] != overlay['current_protocol_version']:
        raise ValueError('Changed method corpus edition')
    for addition in reversed(overlay['added']):
        case = corpus['cases'].pop()
        if case['id'] != addition['id'] or digest(case) != addition['sha256']:
            raise ValueError('Changed added method case')
    for update in overlay['updates']:
        index = next(i for i, c in enumerate(corpus['cases']) if c['id'] == update['id'])
        if corpus['cases'][index] != update['after']:
            raise ValueError('Changed migrated method case')
        corpus['cases'][index] = copy.deepcopy(update['before'])
    corpus['protocol_version'] = overlay['base_protocol_version']
    restored = (json.dumps(corpus, ensure_ascii=False, indent=2)+'\n').encode()
    if hashlib.sha256(restored).hexdigest() != overlay['base_sha256']:
        raise ValueError('Method migration does not restore its exact predecessor')
    return corpus


def corpus_before_automation():
    corpus = tsep.read_json(ROOT/'conformance/cases.json')
    if corpus['protocol_version'] != '0.3.0-draft.10':
        raise ValueError('Unexpected conformance edition')
    refs = corpus['additional_case_files']
    added = [r for r in refs if r['path'] == 'tests/fixtures/public-automation-v1.json']
    if len(added) != 1:
        raise ValueError('Unexpected public-probe fixture registration')
    raw = (ROOT/added[0]['path']).read_bytes()
    if hashlib.sha256(raw).hexdigest() != added[0]['sha256']:
        raise ValueError('Changed public-probe fixture')
    corpus['additional_case_files'] = [r for r in refs if r not in added]
    corpus['protocol_version'] = '0.3.0-draft.9'
    return corpus
