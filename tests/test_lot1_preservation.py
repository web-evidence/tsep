"""Only the two declared rule edits and their control editions may differ."""
import hashlib,json,unittest
import tsep
from tests.lot1_history import baseline


class Lot1Preservation(unittest.TestCase):
    def test_only_declared_normative_fields_change(self):
        old=baseline();actual=tsep.read_json(tsep.PROTOCOL_PATH)
        self.assertEqual(actual['version'],'0.3.0-draft.6')
        self.assertEqual(len(actual['controls']),44)
        allowed={'TS01-A02':{'procedure'},'TS02-A02':{'procedure','inconclusive'}}
        changed=set()
        for control in actual['controls']:
            for rule in control['rules']:
                previous=old['rules'][rule['id']]
                digest=hashlib.sha256(json.dumps(rule,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
                self.assertEqual(control['rule_version'],'0.3.0-draft.6' if control['id'] in old['controls'] else previous['version'])
                if digest!=previous['sha256']:
                    changed.add(rule['id']);self.assertIn(rule['id'],allowed)
                    prior=next(r for r in old['controls'][control['id']]['rules'] if r['id']==rule['id'])
                    self.assertEqual({k for k in set(rule)|set(prior) if rule.get(k)!=prior.get(k)},allowed[rule['id']])
        self.assertEqual(changed,set(allowed))


if __name__=='__main__':unittest.main()
