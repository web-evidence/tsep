"""Explicit inverses of lot1 and priority1 contract amendments for historical checks. New profiles have separate contradictory tests."""
import copy,hashlib,json
from pathlib import Path
import tsep
ROOT=Path(__file__).resolve().parents[1]
def baseline():
    raw=(ROOT/'provenance/v030-draft6-rule-baseline.json').read_bytes()
    if hashlib.sha256(raw).hexdigest()!='74b8ead15f768c7b6897d200047462df05e0718688428ee771f9690146dfea44':raise ValueError('Changed lot1 historical baseline')
    return json.loads(raw)
def controls_before_lot1():
    old=baseline()['controls']
    raw=(ROOT/'provenance/v030-draft7-priority1-baseline.json').read_bytes()
    if hashlib.sha256(raw).hexdigest()!='791ee10afb221194e5acd495ac9fe5d685fce9ab80f65be2b1fc3c0fdf3f6276':raise ValueError('Changed priority1 historical baseline')
    old.update(json.loads(raw)['controls'])
    new_raw=(ROOT/'provenance/v030-draft10-rule-baseline.json').read_bytes()
    if hashlib.sha256(new_raw).hexdigest()!='c8c558db9983c99a5d7ab4e262e56b6c096a75904b1c79e584bedf538b26ab2d':raise ValueError('Changed draft10 historical baseline')
    pre_automation=json.loads(new_raw)['controls']
    return [copy.deepcopy(old.get(c['id'],pre_automation.get(c['id'],c))) for c in tsep.read_json(tsep.PROTOCOL_PATH)['controls']]
