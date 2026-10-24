"""Explicit inverse of the TS01/TS02 lot1 contract amendment for historical checks."""
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
    return [copy.deepcopy(old.get(c['id'],c)) for c in tsep.read_json(tsep.PROTOCOL_PATH)['controls']]
