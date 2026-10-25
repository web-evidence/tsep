"""Only the two declared rule edits and their control editions may differ."""
import hashlib,json,unittest
import tsep
from tests.lot1_history import baseline


class Lot1Preservation(unittest.TestCase):
    def test_corpus_metadata_migration_preserves_every_case_and_expectation(self):
        from pathlib import Path
        root=Path(__file__).resolve().parents[1]
        for name,want in {'conformance/cases.json': '2d34a6e002d689c516add05e56971d9e3c1af87d3368021967401f4c7aecb402', 'tests/fixtures/control-cases.json': 'd87a5b60fea94d1e373a1e939edc639bb2435fcc9c2fddc859548e4b03baf5c0'}.items():
            value=json.loads((root/name).read_text());self.assertEqual(value.pop('protocol_version'),'0.3.0-draft.8')
            self.assertEqual(hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest(),want)

    def test_only_declared_normative_fields_change(self):
        old=baseline();actual=tsep.read_json(tsep.PROTOCOL_PATH)
        self.assertEqual(actual['version'],'0.3.0-draft.8')
        self.assertEqual(len(actual['controls']),44)
        allowed={'TS01-A02':{'procedure'},'TS02-A02':{'procedure','inconclusive'}}
        changed=set()
        priority1=tsep.read_json(tsep.PROTOCOL_PATH.parent.parent/'provenance/v030-draft7-priority1-baseline.json')['controls']
        for control in actual['controls']:
            control=priority1.get(control['id'],control)
            for rule in control['rules']:
                previous=old['rules'][rule['id']]
                digest=hashlib.sha256(json.dumps(rule,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
                self.assertEqual(control['rule_version'],'0.3.0-draft.7' if control['id']=='TS01' else '0.3.0-draft.6' if control['id']=='TS02' else previous['version'])
                if digest!=previous['sha256']:
                    changed.add(rule['id']);self.assertIn(rule['id'],allowed)
                    prior=next(r for r in old['controls'][control['id']]['rules'] if r['id']==rule['id'])
                    self.assertEqual({k for k in set(rule)|set(prior) if rule.get(k)!=prior.get(k)},allowed[rule['id']])
        self.assertEqual(changed,set(allowed))


if __name__=='__main__':unittest.main()
