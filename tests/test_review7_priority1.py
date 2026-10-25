"""Independent counterexamples for indexing priority 1; synthetic unless stated."""
import copy
import tempfile
import unittest
from pathlib import Path
from conformance.google_directives import PROFILE, result
from conformance.ts05_indexing import assess
from conformance.evaluate import evaluate
from tests.test_ts05_indexing import target
from tests.test_url_policy import data, rebind
from conformance.exclusion_observation import READER
from adapters import captures, replay, package
import json

NOW = '2026-10-25T05:00:00Z'


class GoogleRules(unittest.TestCase):
    def verdict(self, rules, goal='allow', headers=None):
        notes=[]
        got=result(headers or {}, [rules], {'directive_policy':PROFILE,'crawler':'googlebot','indexing':goal}, NOW, notes)
        return got[0], notes[0]

    def test_known_exclusion_survives_all_other_rules(self):
        for extra in ('all','noarchive','nocache','nositelinkssearchbox','noimageindex','notranslate','indexifembedded',
                      'nofollow','nosnippet','max-snippet: -1','max-video-preview: 10','max-image-preview: large',
                      'unavailable_after: invalid', 'unknown-future-rule'):
            for goal, expected in (('allow','fail'),('exclude','pass')):
                with self.subTest(extra=extra,goal=goal):self.assertEqual(self.verdict('noindex, '+extra,goal)[0],expected)

    def test_unknown_absence_never_passes(self):
        for goal in ('allow','exclude'):self.assertEqual(self.verdict('noidex',goal)[0],'inconclusive')
        for date,state in [('2020-01-01T00:00:00Z','expired'),('2030-01-01T00:00:00Z','future'),('nonsense','invalid')]:
            self.assertEqual(self.verdict('unavailable_after: '+date)[1]['expires'][0]['state'],state)

    def test_other_crawler_scope_and_combination(self):
        for header in ('otherbot: noindex','googlebot-news: noindex'):
            self.assertEqual(self.verdict('',headers={'x-robots-tag':[header]})[0],'pass')
        self.assertEqual(self.verdict('nofollow',headers={'x-robots-tag':['otherbot: noindex, googlebot: noindex']})[0],'fail')
        self.assertEqual(self.verdict('noindex',headers={'x-robots-tag':['googlebot: all']})[0],'fail')

    def test_header_exclusion_does_not_need_html_absence_inference(self):
        from unittest.mock import patch
        from conformance.evaluate import directive_result
        from conformance import source_directives
        for goal,expected in [('allow','fail'),('exclude','pass')]:
            with patch.object(source_directives.source_http,'inventory',side_effect=OSError('unavailable')):
                got=directive_result({'x-robots-tag':['noindex, noarchive']},b'not HTML',
                    {'crawler':'googlebot','indexing':goal,'directive_policy':PROFILE,'source_reader':source_directives.READER},source=True,observed_at=NOW)
            self.assertEqual(got[0],expected)

    def test_meta_news_scope_does_not_apply_to_web_search(self):
        from conformance.evaluate import directive_result
        html='<!doctype html><html><head><meta name="googlebot-news" content="noindex"></head><body>Test</body></html>'
        got=directive_result({'content-type':['text/html; charset=utf-8']},html,
            {'crawler':'googlebot','indexing':'allow','directive_policy':PROFILE,'source_reader':'html-tree-directives-v1'},source=True,observed_at=NOW)
        self.assertEqual(got[0],'pass')

    def test_expiry_is_relative_to_capture_not_wall_clock(self):
        for date,state in (('21 Oct 2026 00:00:00 GMT','fail'),('Wed, 21 Oct 2026 00:00:00 GMT','fail'),
                           ('Wednesday, 21-Oct-26 00:00:00 GMT','fail'),('2030-01-01T00:00:00Z','pass'),('2020-01-01T00:00:00Z','fail'),
                           ('2026-10-25T06:00:00','inconclusive'),('nonsense','pass')):
            with self.subTest(date=date):self.assertEqual(self.verdict('unavailable_after: '+date)[0],state)


class PolicyV2(unittest.TestCase):
    def test_authentication_removal_and_robot_conflicts(self):
        for mechanism in ('authentication','authorization','http-404','http-410','meta-noindex'):
            for effect,expected in (('allow','pass'),('disallow','fail')):
                t=target();p=t['intent']['ts05_policy'];p['policy_version']='2'
                p['indexing']['method']=mechanism;p['crawl']['effect']=effect
                if mechanism in ('authentication','authorization'):p['protection']['method']=mechanism
                t['configuration'].update(indexing_method=mechanism,crawl_effect=effect,protection_method=p['protection']['method'])
                with self.subTest(mechanism=mechanism,effect=effect):self.assertEqual(assess(t,'TS05-A01')[0],expected)

    def test_inclusion_and_public_protection_contradictions(self):
        for goal,effect,protection_goal,method in [('include','disallow','public','none'),('include','allow','private','authentication'),('exclude','allow','public','authentication')]:
            t=target();p=t['intent']['ts05_policy'];p['policy_version']='2'
            p['indexing'].update(goal=goal,method='none' if goal=='include' else 'x-robots-tag-noindex')
            p['crawl']['effect']=effect;p['protection'].update(goal=protection_goal,method=method)
            for claim in p['claims']:claim['level']='not-claimed'
            t['configuration'].update(indexing_method=p['indexing']['method'],crawl_effect=effect,protection_method=method)
            with self.subTest(goal=goal,effect=effect,protection=protection_goal):self.assertEqual(assess(t,'TS05-A01')[0],'fail')

    def test_normative_delta_is_explicit_and_bounded(self):
        import tsep
        root=Path(__file__).resolve().parents[1]
        baseline=json.loads((root/'provenance/v030-draft7-priority1-baseline.json').read_text())['controls']
        protocol=tsep.read_json(tsep.PROTOCOL_PATH)
        self.assertEqual(protocol['version'],'0.3.0-draft.9')
        for c in protocol['controls']:
            if c['id'] not in baseline:continue
            old=baseline[c['id']]
            self.assertEqual(c['rule_version'],'0.3.0-draft.9' if c['id']=='TS07' else '0.3.0-draft.8')
            self.assertEqual({k for k in c if c[k]!=old[k]}, {'rule_version','acceptance_note','rules'})
            self.assertEqual({k for k in c['rules'][0] if c['rules'][0][k]!=old['rules'][0][k]}, {'procedure'})
            self.assertEqual(c['rules'][1:],old['rules'][1:])

    def test_declared_model_never_proves_effective_confidentiality(self):
        t=target();t['intent']['ts05_policy']['policy_version']='2'
        self.assertIn('confidentiality are not established',assess(t,'TS05-A01')[1])


def observed_case(meta='noindex', mechanism='meta-noindex', robots='Allow: /', reviewed=False):
    value=data();t=value['targets'][0];p=t['intent']['evidence_checks']['TS09'];p['reader']=READER
    url='https://synthetic.invalid/page';t['url']=url;t['context']['network']='isolated synthetic'
    p['items'][0].update(representative_url=url,url_prefix=url,mechanism=mechanism)
    e=t['evidence_checks']['TS09'];e['reviews']=e['reviews'] if reviewed else []
    from tests.test_url_policy import record_payload
    raw=json.loads(__import__('base64').b64decode(e['records'][0]['native']['raw_base64']))
    raw['families'][0]['mechanism']=mechanism;record_payload(e['records'][0],raw)
    def doc(url,body,kind):
        from urllib.parse import urlsplit
        return {'url':url,'observed_at':'2026-10-14T10:00:00Z','context_id':'synthetic',
                'http':[{'url':url,'request':'GET '+urlsplit(url).path+' HTTP/1.1\r\nHost: synthetic.invalid\r\nUser-Agent: Authored-TSEP/1\r\n\r\n',
                         'response':'HTTP/1.1 200 OK\r\nContent-Type: '+kind+'; charset=utf-8\r\nContent-Length: '+str(len(body.encode()))+'\r\n\r\n'+body,'complete':True}]}
    e['documents']=[doc(url,'<!doctype html><html><head><title>Synthetic</title><meta name="robots" content="'+meta+'"></head><body>Test</body></html>','text/html'),
                    doc('https://synthetic.invalid/robots.txt','User-agent: *\n'+robots+'\n','text/plain')]
    rebind(t,'TS09')
    return value


class ExclusionEvidence(unittest.TestCase):
    def test_matching_capture_missing_review_stays_unknown(self):
        self.assertEqual(evaluate(observed_case())[0]['outcome'],'inconclusive')

    def test_mismatch_survives_missing_review_and_register_field(self):
        value=observed_case('index');value['targets'][0]['evidence_checks']['TS09']['reviews']=[]
        self.assertEqual(evaluate(value)[0]['outcome'],'fail')

    def test_review_plus_observed_match_can_pass(self):
        self.assertEqual(evaluate(observed_case(reviewed=True))[0]['outcome'],'pass')

    def test_disallow_conflict_and_different_surface(self):
        self.assertEqual(evaluate(observed_case(robots='Disallow: /',reviewed=True))[0]['outcome'],'fail')
        self.assertEqual(evaluate(observed_case(mechanism='x-robots-tag-noindex',reviewed=True))[0]['outcome'],'fail')
        self.assertEqual(evaluate(observed_case(mechanism='robots-disallow'))[0]['outcome'],'fail')

    def test_unknown_other_surface_does_not_hide_missing_declared_noindex(self):
        value=observed_case('index');doc=value['targets'][0]['evidence_checks']['TS09']['documents'][0]
        doc['http'][0]['response']=doc['http'][0]['response'].replace('Content-Type:', 'X-Robots-Tag: foo\r\nContent-Type:')
        self.assertEqual(evaluate(value)[0]['outcome'],'fail')

    def test_header_mechanism_independent_of_unreadable_html(self):
        from unittest.mock import patch
        from conformance.http import Unknown
        for header,expected in [('', 'fail'),('noindex, other-rule','pass')]:
            v=observed_case(mechanism='x-robots-tag-noindex',reviewed=True);t=v['targets'][0]
            doc=t['evidence_checks']['TS09']['documents'][0]
            if header:doc['http'][0]['response']=doc['http'][0]['response'].replace('Content-Type:', 'X-Robots-Tag: '+header+'\r\nContent-Type:')
            rebind(t,'TS09')
            with patch('conformance.source_directives.assess',side_effect=Unknown('Unsupported streaming template')):
                self.assertEqual(evaluate(v)[0]['outcome'],expected)

    def test_explicit_negative_review_survives_unknown_capture(self):
        v=observed_case(reviewed=True);t=v['targets'][0];e=t['evidence_checks']['TS09']
        e['documents']=[];e['reviews'][0]['judgment']='contradicted';rebind(t,'TS09')
        self.assertEqual(evaluate(v)[0]['outcome'],'fail')

    def test_foreign_or_out_of_prefix_representative_cannot_pass(self):
        for scope in ('https://other.invalid/page','https://synthetic.invalid/other/'):
            value=observed_case(reviewed=True);t=value['targets'][0]
            t['intent']['evidence_checks']['TS09']['items'][0]['url_prefix']=scope;rebind(t,'TS09')
            self.assertEqual(evaluate(value)[0]['outcome'],'inconclusive')

    def test_replay_local_manifests_are_complete_and_original_retained(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);source=root/'input.json';source.write_text(json.dumps(observed_case(reviewed=True)))
            captures.build(source,root/'bundle',assessor='Synthetic reviewer',label='Synthetic priority1',selection_method='Counterexample',access='synthetic')
            original=(root/'bundle/SHA256SUMS').read_bytes()
            result=replay.replay(root/'bundle',root/'replay')
            self.assertTrue(result['replayed'])
            self.assertEqual((root/'replay/original-evidence/source-bundle.SHA256SUMS.txt').read_bytes(),original)
            for manifest in (root/'replay').rglob('SHA256SUMS'):package.inventory(manifest.parent)


if __name__=='__main__':unittest.main()
