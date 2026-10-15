"""TS15 prefrozen files/sets, byte limits, refusals and offline export/replay."""
import base64,copy,gzip,hashlib,json,os,socket,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import tsep
from adapters import captures,replay
from conformance import sitemap_files as native,sitemap_set
from conformance.corpus import expand
from conformance.evaluate import evaluate
from reports import html
ROOT=Path(__file__).resolve().parents[1]
READER_SHA='ad672686571f50ce98594c0add0609e8eebc1b2462edda3c97d665b01b26c657'
REVIEW_SHA='5ff55639fa8248fb8d5ab027799cf46863cd72777f310448df3c12786de0bbfa'
RECIPE_SHA='075fb77f6e82c31310c5f5ea1ea002a1c3e67625a7d63043a9592ee5ee87b167'
NS='http://www.sitemaps.org/schemas/sitemap/0.9'

def fixture(name,sha=None):
    raw=(ROOT/'tests/fixtures'/name).read_bytes()
    if sha is not None and hashlib.sha256(raw).hexdigest()!=sha:raise ValueError('Changed prefrozen expectations')
    return json.loads(raw)

def cases():return fixture('sitemap-files-v1.json')['cases']
def data(name='single-leaf'):return copy.deepcopy(next(c['input'] for c in cases() if c['id']=='sitemap-files-v1-'+name))
def body_bytes(case):
    body=case['body']
    if 'text' in body:return body['text'].encode()
    if 'hex' in body:return bytes.fromhex(body['hex'])
    if body['recipe']=='entries':
        root,entry=('urlset','url') if body['kind']=='urlset' else ('sitemapindex','sitemap')
        return ('<'+root+' xmlns="'+NS+'">'+('<'+entry+'><loc>https://example.test/a</loc></'+entry+'>')*body['count']+'</'+root+'>').encode()
    start=('\ufeff<urlset xmlns="'+NS+'"><url><loc>https://example.test/café</loc></url>').encode();end=b'</urlset>'
    return start+b' '*(body['bytes']-len(start)-len(end))+end

def record(case):
    raw=body_bytes(case)
    if case['encoding']=='gzip':raw=gzip.compress(raw,mtime=0)
    mutation=case.get('wire_mutation')
    if mutation=='truncated':raw=raw[:-5]
    if mutation=='bad-crc':raw=raw[:-8]+bytes([raw[-8]^1])+raw[-7:]
    if mutation=='second-member':raw+=gzip.compress(b' ',mtime=0)
    if mutation=='trailing':raw+=b'not-a-gzip-member'
    return dict(raw_base64=base64.b64encode(raw).decode(),sha256=hashlib.sha256(raw).hexdigest(),encoding=case['encoding'],complete=case['complete'])

class SitemapFiles(unittest.TestCase):
    def test_encoding_failure_needs_bounded_root_attribution(self):
        rows=fixture('sitemap-root-attribution-v1.json','b2f88aa39d24da5adfda3f4df8ba22ac4948ffddd1a71dd47504f134aa75e943')['cases']
        self.assertEqual(len(rows),8)
        with patch.object(socket,'socket',side_effect=AssertionError('No schema/entity fetch')):
            for case in rows:
                with self.subTest(case=case['id']),tempfile.TemporaryDirectory() as folder:
                    raw=bytes.fromhex(case['raw_hex']);observed=native.read_native(raw,'identity',True)
                    self.assertEqual({k:observed[k] for k in case['expected']},case['expected'])
                    payload=data();payload['targets'][0]['sitemap_files'][0]['native']={'raw_base64':base64.b64encode(raw).decode(),'sha256':hashlib.sha256(raw).hexdigest(),'encoding':'identity','complete':True}
                    root=Path(folder);source=root/'in.json';source.write_text(json.dumps(payload))
                    captures.build(source,root/'bundle',assessor='Fictional',label='Synthetic root attribution',selection_method='Authored',access='synthetic')
                    self.assertEqual(tsep.read_json(root/'bundle/report.json')['results'][0]['status'],case['bundle_status'])

    def test_byte_limit_needs_attributed_sitemaps_prefix(self):
        rows=fixture('sitemap-files-prefix-v1.json','c4f9fe59c2a4f81d9dd5325131298b579dbff7126d7666ed01da0e91dc486565')['cases']
        self.assertEqual(len(rows),6)
        for case in rows:
            with self.subTest(case=case['id']),tempfile.TemporaryDirectory() as folder:
                prefix=case['prefix'].encode();suffix=case['suffix'].encode()
                decoded=prefix+b' '*(case['decoded_bytes']-len(prefix)-len(suffix))+suffix
                raw=gzip.compress(decoded,mtime=0);del decoded
                observed=native.read_native(raw,'gzip',True)
                self.assertEqual({k:observed[k] for k in case['expected']},case['expected'])
                self.assertEqual(observed['decoded_bytes_read'],native.BYTE_LIMIT+1)
                self.assertEqual(observed['byte_measurement'],'lower-bound')
                payload=data();payload['targets'][0]['sitemap_files'][0]['native']={'raw_base64':base64.b64encode(raw).decode(),'sha256':hashlib.sha256(raw).hexdigest(),'encoding':'gzip','complete':True}
                root=Path(folder);source=root/'in.json';source.write_text(json.dumps(payload))
                captures.build(source,root/'bundle',assessor='Fictional',label='Synthetic bounded-prefix case',selection_method='Authored',access='synthetic')
                self.assertEqual(tsep.read_json(root/'bundle/report.json')['results'][0]['status'],case['bundle_status'])

    def test_prefrozen_reader_and_review_cases(self):
        rows=fixture('sitemap-files-reader-v1.json',READER_SHA)['cases']+fixture('sitemap-files-review-v1.json',REVIEW_SHA)['cases']
        self.assertEqual(len(rows),48)
        with patch.object(socket,'socket',side_effect=AssertionError('No network or schema fetch')):
            for c in rows:
                with self.subTest(case=c['id']):
                    observed=native.read_record(record(c));self.assertEqual({k:observed[k] for k in c['expected']},c['expected'])
    def test_frozen_recipe_expectations_and_expanded_corpus(self):
        frozen=fixture('sitemap-files-set-recipes-v1.json',RECIPE_SHA)['cases'];rows=cases();self.assertEqual(len(rows),31)
        for a,b in zip(frozen,rows):self.assertEqual(a['expected'],[v['outcome'] for v in b['expected']])
        raw=(ROOT/'tests/fixtures/sitemap-files-v1.json').read_bytes();self.assertEqual(hashlib.sha256(raw).hexdigest(),(ROOT/'tests/fixtures/sitemap-files-v1.sha256').read_text().strip())
        corpus=expand(tsep.read_json(ROOT/'conformance/cases.json'));self.assertEqual(corpus['cases'][1608:1639],rows)
    def test_all_set_cases_offline_without_node_or_input_mutation(self):
        with patch.dict(os.environ,{},clear=True),patch.object(socket,'socket',side_effect=AssertionError('No network')):
            for c in cases():
                before=copy.deepcopy(c['input'])
                with self.subTest(case=c['id']):
                    self.assertEqual([r['outcome'] for r in evaluate(c['input'])],[r['outcome'] for r in c['expected']]);self.assertEqual(c['input'],before)
    def test_c_nc_nt_and_actual_byte_limits_replay(self):
        scenarios=[('index-and-child','C'),('namespace-error','NC'),('missing-child','NT'),('full-path-byte-52428800','C'),('full-path-byte-52428801','NC'),('full-path-entries-50000','C'),('full-path-entries-50001','NC')]
        for name,status in scenarios:
            with self.subTest(case=name),tempfile.TemporaryDirectory() as folder:
                root=Path(folder);source=root/'input.json';source.write_text(json.dumps(data(name)));original=source.read_bytes()
                captures.build(source,root/'bundle',assessor='Fictional operator',label='Synthetic TS15',selection_method='Declared fictional files only',access='synthetic',mode='automatic')
                report=tsep.read_json(root/'bundle/report.json');self.assertEqual(report['results'][0]['status'],status)
                self.assertEqual((root/'bundle/input.json').read_bytes(),original)
                self.assertTrue({'sitemap','intent'}<={a['kind'] for a in report['artifacts']})
                self.assertTrue(tsep.decision(report)['synthetic_evidence']);self.assertIn('sitemap_files_interpretation',tsep.decision(report))
                with patch.object(socket,'socket',side_effect=AssertionError('Offline replay')):result=replay.replay(root/'bundle',root/'replayed')
                self.assertTrue(result['same_atomic_results']);self.assertTrue(result['same_gate'])
                for lang in ('fr','en'):
                    rendered=html.render(root/'bundle/report.json',language=lang)
                    self.assertIn(html.TEXT[lang]['sitemap_files_note'],rendered)
                    self.assertIn(html.TEXT[lang]['sitemap_roots_note'],rendered)
    def test_intake_refuses_tampering_and_preserves_existing_directory(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);source=root/'in.json'
            for mutation in ('hash','base64','encoding','large','mixed-provenance'):
                d=data();r=d['targets'][0]['sitemap_files'][0]['native']
                if mutation=='hash':r['sha256']='0'*64
                if mutation=='base64':r['raw_base64']='!'
                if mutation=='encoding':r['encoding']='br'
                if mutation=='large':
                    raw=b' '*(native.RAW_LIMIT+1);r.update(raw_base64=base64.b64encode(raw).decode(),sha256=hashlib.sha256(raw).hexdigest())
                if mutation=='mixed-provenance':d['targets'][0]['sitemap_files'][0]['provenance']='supplied-native-file'
                source.write_text(json.dumps(d));dest=root/mutation
                with self.subTest(mutation=mutation),self.assertRaises(tsep.Invalid):captures.build(source,dest,assessor='Fictional',label='Synthetic refusal',selection_method='Authored',access='synthetic')
                self.assertFalse(dest.exists())
            source.write_bytes(b' '*(tsep.MAX_JSON_BYTES+1))
            with self.assertRaises(tsep.Invalid):captures.build(source,root/'json-limit',assessor='Fictional',label='Too large',selection_method='Authored',access='synthetic')
            existing=root/'existing';existing.mkdir();(existing/'original').write_text('preserved')
            source.write_text(json.dumps(data()))
            with self.assertRaises(tsep.Invalid):captures.build(source,existing,assessor='Fictional',label='Existing',selection_method='Authored',access='synthetic')
            self.assertEqual((existing/'original').read_text(),'preserved')
    def test_raw_transport_boundary_not_protocol_failure(self):
        start=('<urlset xmlns="'+NS+'"><url><loc>https://example.test/a</loc></url>').encode();end=b'</urlset>'
        raw=start+b' '*(native.RAW_LIMIT-len(start)-len(end))+end
        self.assertEqual(native.read_native(raw,'identity',True)['format'],'pass')
        with self.assertRaises(native.IntakeError):native.read_native(raw+b' ','identity',True)
        with self.assertRaises(native.IntakeError):native.read_native(b' '*native.BYTE_LIMIT,'identity',True)
    def test_partial_rules_and_synthetic_relabeling(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);source=root/'in.json';d=data();d['rules']=['TS15-A02'];source.write_text(json.dumps(d))
            captures.build(source,root/'partial',assessor='Fictional',label='Partial',selection_method='Authored',access='synthetic',mode='automatic')
            self.assertEqual(tsep.read_json(root/'partial/report.json')['results'][0]['status'],'NT')
            with self.assertRaises(tsep.Invalid):captures.build(source,root/'public',assessor='Fictional',label='False public',selection_method='Authored',access='public')
    def test_declared_population_and_html_escape(self):
        target=data()['targets'][0];_,reason=sitemap_set.assess(target,'TS15-A03');note=json.loads(reason[len(sitemap_set.PREFIX):])
        self.assertEqual(note['declared_document_count'],1);self.assertEqual(note['root_discovery'],'not-established');self.assertEqual(note['scope'],'declared-file-population-only')
        note['rows'][0]['reason']='<img src=x onerror=alert(1)>'
        for lang in ('fr','en'):
            with patch.object(sitemap_set,'assess',side_effect=AssertionError('No reassessment')):out=html.sitemap_files_values({'reason':sitemap_set.PREFIX+json.dumps(note)},html.TEXT[lang])
            self.assertNotIn('<img ',out);self.assertIn('&lt;img ',out);self.assertIn(html.TEXT[lang]['sitemap_roots_note'],out)
    def test_native_modules_bound_to_adapter(self):
        sources=captures.source_files();self.assertIn('conformance/sitemap_files.py',sources);self.assertIn('conformance/sitemap_set.py',sources)
    def test_bad_inputs_never_raise_or_pass(self):
        for key in ('intent','context','sitemap_files'):
            for value in (None,False,[],{},'broken'):
                t=data()['targets'][0];t[key]=value
                for rule in sitemap_set.RULES:
                    with self.subTest(key=key,value=value,rule=rule):self.assertEqual(sitemap_set.assess(t,rule)[0],'inconclusive')
    def test_closed_outcomes_preserve_historical_requirements(self):
        rules={r['id']:r for c in tsep.read_json(tsep.PROTOCOL_PATH)['controls'] for r in c.get('rules',[])}
        closed = ('TS15-A03', 'TS18-A01', 'TS18-A02')
        for rid in closed:
            with self.subTest(rule=rid):
                self.assertEqual(tsep.atomic_outcomes(rules[rid]), ('pass', 'inconclusive'))
            for value in (None, ['pass'], ['inconclusive'], ['pass','fail','inconclusive'],
                          ['pass','not-applicable','inconclusive'], ['inconclusive','pass']):
                changed=copy.deepcopy(rules[rid])
                if value is None:changed.pop('allowed_outcomes')
                else:changed['allowed_outcomes']=value
                with self.subTest(rule=rid,value=value), self.assertRaises(tsep.Invalid):
                    tsep.atomic_outcomes(changed)
        for rid,rule in rules.items():
            if rid not in closed:
                with self.subTest(rule=rid):
                    self.assertEqual(set(tsep.atomic_outcomes(rule)),{'pass','fail','not-applicable','inconclusive'})
                with self.subTest(rule=rid),self.assertRaises(tsep.Invalid):
                    tsep.atomic_outcomes(dict(rule,allowed_outcomes=['pass','inconclusive']))
    def test_missing_declared_outcome_coverage_is_rejected(self):
        from conformance.run import run
        full=expand(tsep.read_json(ROOT/'conformance/cases.json'))
        for rid,missing,replacement in [('TS15-A03','pass','inconclusive'),('TS15-A03','inconclusive','pass'),('TS01-A01','fail','inconclusive')]:
            altered=copy.deepcopy(full);count=0
            for case in altered['cases']:
                for row in case['expected']:
                    if row['rule_id']==rid and row['outcome']==missing:
                        row['outcome']=replacement;count+=1
            self.assertGreater(count,0)
            # No external interpreter work: this exercise tests corpus completeness.
            def unknown(payload):
                return [dict(rule_id=r,target=t['url'],outcome='inconclusive',reason='Coverage test only') for r in payload['rules'] for t in payload['targets']]
            with self.subTest(rule=rid,missing=missing),patch('conformance.run.evaluate',side_effect=unknown),self.assertRaisesRegex(tsep.Invalid,'Missing contradictory coverage per rule: '+rid):
                run(altered,rules=['TS15-A03'])
    def test_impossible_a03_outcomes_refused_and_orphan_stays_unknown(self):
        from conformance.run import outcomes
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);source=root/'in.json';source.write_text(json.dumps(data()))
            captures.build(source,root/'bundle',assessor='Fictional',label='Synthetic outcome validation',selection_method='Authored',access='synthetic')
            report=tsep.read_json(root/'bundle/report.json')
            for invalid in ('fail','not-applicable'):
                forged=copy.deepcopy(report);r=forged['results'][0];r['status']='NC' if invalid=='fail' else 'C'
                atom=next(a for a in r['atomic_results'] if a['rule_id']=='TS15-A03');atom['outcome']=invalid
                with self.subTest(outcome=invalid),self.assertRaisesRegex(tsep.Invalid,'Outcome outside declared rule domain: TS15-A03'):tsep.validate(forged,root/'bundle')
                with self.assertRaisesRegex(tsep.Invalid,'Outcome outside declared rule domain: TS15-A03'):outcomes([atom])
        self.assertEqual(evaluate(data('orphan-declared-file'))[2]['outcome'],'inconclusive')
    def test_corrupt_original_refused_even_when_plan_missing(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);source=root/'in.json';payload=data();payload['targets'][0]['intent']={}
            payload['targets'][0]['sitemap_files'][0]['native']['sha256']='0'*64
            source.write_text(json.dumps(payload))
            with self.assertRaisesRegex(tsep.Invalid,'Native sitemap intake refused'):
                captures.build(source,root/'bundle',assessor='Fictional',label='Synthetic missing plan and corrupt bytes',selection_method='Authored',access='synthetic')
            self.assertFalse((root/'bundle').exists())

    def test_intact_missing_plan_preserves_original_and_unknown(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);source=root/'in.json';payload=data();payload['targets'][0]['intent']={}
            source.write_text(json.dumps(payload));original=source.read_bytes()
            captures.build(source,root/'bundle',assessor='Fictional',label='Synthetic intact missing plan',selection_method='Authored',access='synthetic')
            report=tsep.read_json(root/'bundle/report.json')
            self.assertEqual(report['results'][0]['status'],'NT')
            self.assertTrue(tsep.decision(report)['synthetic_evidence'])
            self.assertEqual((root/'bundle/input.json').read_bytes(),original)
            with patch.object(socket,'socket',side_effect=AssertionError('Offline replay')):
                result=replay.replay(root/'bundle',root/'replayed')
            self.assertTrue(result['same_atomic_results']);self.assertTrue(result['same_gate'])

    def test_wrapped_missing_plan_cannot_hide_corrupt_or_synthetic_original(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);source=root/'in.json'
            for mutation,access in [('hash','synthetic'),('provenance','synthetic'),('relabel','public')]:
                child=data();child['targets'][0]['intent']={}
                if mutation=='hash':child['targets'][0]['sitemap_files'][0]['native']['sha256']='0'*64
                if mutation=='provenance':child['targets'][0]['sitemap_files'][0]['provenance']='supplied-native-file'
                payload={'input_version':'2','rules':['TS41-A01'],'targets':[{'url':'https://example.test/release','observed_at':child['targets'][0]['observed_at'],'intent':{},'release_runs':[{'input_json':json.dumps(child)}]}]}
                source.write_text(json.dumps(payload))
                with self.subTest(mutation=mutation),self.assertRaises(tsep.Invalid):
                    captures.build(source,root/mutation,assessor='Fictional',label='Synthetic wrapped refusal',selection_method='Authored',access=access)
                self.assertFalse((root/mutation).exists())
