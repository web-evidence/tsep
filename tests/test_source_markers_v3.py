"""Explicit main-document projection: real parser, negative cases, native preflight."""
import base64
import zlib
import json
import hashlib
import copy
import os
import unittest
from unittest.mock import patch
from conformance import source_markers as policy
from collectors.preflight import reference_check
from experiments import source_markers as reader

HEADERS={'content-type':['text/html; charset=utf-8']}
OBJECTIVE={'required_markers':['Expected'],'forbidden_markers':['Forbidden']}
class ContentV3(unittest.TestCase):
    def observe(self,inner,head='',selected=policy.CURRENT_CONTENT_READER):
        raw=('<!doctype html><html><head>'+head+'</head><body>'+inner+'</body></html>').encode()
        result=policy.observe(raw,content_types=HEADERS['content-type'],objective=OBJECTIVE,
            node=os.environ['TSEP_SOURCE_NODE'],selected=selected)
        for row in result['readings'].values():
            for segment in (row['segments'] or [])+(row['excluded'] or []):
                a,b=segment['body_span_bytes'];self.assertEqual(raw[a:b].decode(),segment['raw_source'])
        packed=policy.compact(result);policy.verify_projection(result,packed)
        return result,raw
    def test_required_only_in_excluded_context_cannot_pass_or_seal(self):
        for inner in ('<svg><text>Expected</text></svg>',
                      '<svg><foreignObject><p>Expected</p></foreignObject></svg>',
                      '<math><mi>Expected</mi></math>','<iframe>Expected</iframe>',
                      '<noscript><b>Expected</b></noscript>',
                      '<iframe srcdoc="<p>Expected</p>"></iframe>'):
            with self.subTest(inner=inner):
                result,raw=self.observe('<p>Login</p>'+inner)
                self.assertEqual(result['candidate_consensus'],'fail')
                self.assertEqual(reference_check(HEADERS,raw,'markers',['Expected'],[],
                    identity_reader=policy.CURRENT_CONTENT_READER)['state'],'contradiction')
    def test_forbidden_in_excluded_context_is_unknown_never_success(self):
        for inner in ('<svg><text>Forbidden</text></svg>','<math><mi>Forbidden</mi></math>',
                      '<iframe>Forbidden</iframe>','<noscript>Forbidden</noscript>'):
            with self.subTest(inner=inner):
                result,_=self.observe('<p>Expected</p>'+inner)
                self.assertEqual(result['candidate_consensus'],'inconclusive')
                self.assertTrue(all(r['excluded_forbidden_matches'] for r in result['readings'].values()))
        result,_=self.observe('<p>Expected Forbidden</p><svg><text>Forbidden</text></svg>')
        self.assertEqual(result['candidate_consensus'],'fail')
    def test_no_match_joined_across_foreign_or_frame(self):
        for inner in ('Exp<svg><text>x</text></svg>ected','Exp<iframe>x</iframe>ected'):
            self.assertEqual(self.observe(inner)[0]['candidate_consensus'],'fail')
    def test_ordinary_content_survives_common_embeds_with_attributed_exclusions(self):
        inner='<p>Expected</p><svg><title>Icon</title><text>\u00a0</text></svg><noscript><iframe src="https://example.invalid/"></iframe></noscript><iframe srcdoc="opaque"></iframe>'
        result,_=self.observe(inner)
        self.assertEqual(result['candidate_consensus'],'pass')
        self.assertTrue(any('\u00a0' in x['data'] for x in result['readings']['enabled']['excluded']))
    def test_duplicate_attributes_only_v3_and_first_value_retained(self):
        inner='<p class="one" class="two">Expected</p>'
        result,_=self.observe(inner)
        self.assertEqual(result['candidate_consensus'],'pass')
        for row in result['inventory']['readings'].values():
            self.assertEqual({e['code'] for e in row['parse_errors']},{'duplicate-attribute'})
            p=next(n for n in row['nodes'] if n['name']=='p')
            self.assertEqual(reader.content.attributes(p)['class'],'one')
        for selected in (policy.READER,policy.CONTENT_READER):
            self.assertEqual(self.observe(inner,selected=selected)[0]['candidate_consensus'],'inconclusive')
    def test_other_errors_and_shadow_templates_remain_unknown(self):
        for inner,head in [('<p>Expected &#13;</p>',''),
                           ('<p>Expected</p>','<noscript><img src="pixel"></noscript>'),
                           ('<p>Expected</p><template shadowrootmode="open" shadowrootmode="closed">x</template>','')]:
            self.assertEqual(self.observe(inner,head)[0]['candidate_consensus'],'inconclusive')
    def test_ignored_end_tags_only_allow_exact_ascii_whitespace(self):
        self.assertEqual(self.observe('<p>Expected</p><a> </span> </a>')[0]['candidate_consensus'],'pass')
        for inner in ('<a>Exp</span>ected</a>','<p>Expected</p><a>\u00a0</span> </a>'):
            self.assertEqual(self.observe(inner)[0]['candidate_consensus'],'inconclusive')
    def test_real_div_and_p_closures_never_merge_markers(self):
        for inner in ('<div>Exp</div>ected','<p>Exp</p>ected'):
            self.assertEqual(self.observe(inner)[0]['candidate_consensus'],'fail')

    def test_v3_keeps_supported_body_tail_whitespace(self):
        raw=b'<!doctype html><html><head></head><body><p>Expected</p>\n</body>\n</html>\n'
        r=policy.observe(raw,content_types=HEADERS['content-type'],objective=OBJECTIVE,
                         node=os.environ['TSEP_SOURCE_NODE'],selected=policy.CURRENT_CONTENT_READER)
        self.assertEqual(r['candidate_consensus'],'pass')

    def test_utf8_without_http_charset_requires_bom_or_one_early_meta(self):
        cases=[(b'<meta charset="utf-8">',True),(b'<meta charset="windows-1252">',False),
               (b'',False),(b'<!-- <meta charset="utf-8"> -->',False),
               (b' '*1024+b'<meta charset="utf-8">',False),
               (b'<meta charset="utf-8"><meta charset="utf-8">',False),
               (b'<meta charset="utf-8" charset="windows-1252">',False),
               (b'<meta http-equiv="content-type" content="text/html; charset=windows-1252"><meta charset="utf-8">',False)]
        for head,accepted in cases:
            raw=b'<!doctype html><html><head>'+head+b'</head><body>Expected</body></html>'
            call=lambda:policy.observe(raw,content_types=['text/html'],objective=OBJECTIVE,
                node=os.environ['TSEP_SOURCE_NODE'],selected=policy.CURRENT_CONTENT_READER)
            if accepted:
                result=call();self.assertEqual(result['candidate_consensus'],'pass')
                self.assertEqual(result['content_types'],['text/html'])
                self.assertTrue(result['inventory']['content_type_source']['charset_evidence'])
            else:
                with self.assertRaises(ValueError):call()
        raw=b'\xef\xbb\xbf<!doctype html><html><head></head><body>Expected</body></html>'
        self.assertEqual(policy.observe(raw,content_types=['text/html'],objective=OBJECTIVE,
            node=os.environ['TSEP_SOURCE_NODE'],selected=policy.CURRENT_CONTENT_READER)['candidate_consensus'],'pass')
        for old in (policy.READER,policy.CONTENT_READER):
            with self.assertRaises(ValueError):policy.observe(raw,content_types=['text/html'],node=os.environ['TSEP_SOURCE_NODE'],selected=old)

    def test_existing_noscript_profiles_keep_their_semantics(self):
        inner='<p>Expected</p><noscript>Forbidden</noscript>'
        self.assertEqual(self.observe(inner,selected=policy.READER)[0]['candidate_consensus'],'fail')
        self.assertEqual(self.observe(inner,selected=policy.CONTENT_READER)[0]['candidate_consensus'],'pass')
    def test_projection_envelope_refuses_tamper_truncation_trailing_and_bomb(self):
        result,_=self.observe('<p>Expected</p><svg><text>Icon</text></svg>')
        packed=policy.compact(result);row=packed['hypotheses']['enabled']
        data=base64.b64decode(row['projection']['data'])
        for suffix in (b'junk',zlib.compress(b'{}')):
            bad=copy.deepcopy(row);bad['projection']['data']=base64.b64encode(data+suffix).decode()
            with self.assertRaises(ValueError):policy.expand_projection(bad)
        for key,value in [('raw_bytes',1),('raw_bytes',policy.MAX_PROJECTION_BYTES+1),
                          ('sha256','0'*64),('data',base64.b64encode(data[:-2]).decode()),
                          ('data',base64.b64encode(zlib.compress(b'x'*1000000)).decode())]:
            bad=copy.deepcopy(row);bad['projection'][key]=value
            with self.assertRaises(ValueError):policy.expand_projection(bad)
        forged=copy.deepcopy(packed);forged['hypotheses']['enabled']['projection']['sha256']='0'*64
        with self.assertRaises(ValueError):policy.verify_projection(result,forged)

    def test_compressed_projection_cannot_hide_identity_or_unused_contexts(self):
        result,_=self.observe('<p>Expected</p>');packed=policy.compact(result)
        for key in ('source_sha256','content_types','parser','observer_version'):
            bad=copy.deepcopy(packed);bad[key]=None
            with self.assertRaises(ValueError):policy.verify_projection(result,bad)
        bad=copy.deepcopy(packed);row=bad['hypotheses']['enabled'];payload=policy.expand_projection(row)
        payload['contexts'].append([])
        raw=json.dumps({k:payload[k] for k in ('segments','excluded','contexts')},sort_keys=True,
                       ensure_ascii=False,separators=(',',':')).encode()
        row['projection'].update(raw_bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),
                                 data=base64.b64encode(zlib.compress(raw,9)).decode())
        with self.assertRaisesRegex(ValueError,'Unused'):policy.verify_projection(result,bad)
        row=copy.deepcopy(packed['hypotheses']['enabled']);row['segments']=[]
        with self.assertRaisesRegex(ValueError,'Mixed'):policy.expand_projection(row)

    def test_explicit_reader_and_total_diagnostic_bound(self):
        with self.assertRaises(TypeError):policy.observe(b'Expected',content_types=HEADERS['content-type'])
        _,raw=self.observe('<p>Expected</p>');diagnostics=[]
        with patch.object(policy,'MAX_DIAGNOSTIC_BYTES',1):
            outcome,reason=policy.assess(HEADERS,raw,dict(OBJECTIVE,identity_reader=policy.CURRENT_CONTENT_READER),diagnostics=diagnostics)
        self.assertEqual(outcome,'inconclusive');self.assertIn('diagnostics exceed',reason)
        self.assertNotIn('hypotheses',diagnostics[0])
        result,_=self.observe('<p>Expected</p>');packed=policy.compact(result)
        packed['hypotheses']['enabled']=policy.expand_projection(packed['hypotheses']['enabled'])
        with self.assertRaisesRegex(ValueError,'encoding differs'):policy.verify_projection(result,packed)

    def test_native_recheck_and_exact_observation_replay(self):
        result,raw=self.observe('<p>Expected</p><iframe>external</iframe>')
        replay=reader.replay(result,raw,node=os.environ['TSEP_SOURCE_NODE'])
        self.assertEqual(result,replay)
        _,changed=self.observe('<p>Login</p><svg><text>Expected</text></svg>')
        self.assertEqual(policy.assess(HEADERS,changed,dict(OBJECTIVE,identity_reader=policy.CURRENT_CONTENT_READER))[0],'fail')
        forged=copy.deepcopy(result);forged['readings']['enabled']['excluded'][0]['data']='tampered'
        with self.assertRaisesRegex(ValueError,'replay differs'):reader.replay(forged,raw,node=os.environ['TSEP_SOURCE_NODE'])

if __name__=='__main__':unittest.main()
