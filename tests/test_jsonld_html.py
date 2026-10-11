"""Boundary and retained-observation checks. Node qualification is explicit."""
import base64
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from experiments import source_scripts as scripts
from experiments import jsonld_html as workflow
from scripts.jsonld_html_check import graph,projection,request
from scripts.source_http_check import fixture


class HtmlJsonLdObservation(unittest.TestCase):
    def source(self,id):
        case=next(c for c in fixture('source-scripts-v1.json')['cases'] if c['id']==id)
        observation=fixture('source-scripts-observations-v1.json')['observations'][id]
        raw=case['html'].encode('utf-8');source,decoding=scripts.http.decode(raw,['text/html; charset=utf-8'])
        return case,observation,source,raw,decoding

    def observed(self,id):return fixture('jsonld-html-observations-v1.json')['observations'][id]

    def test_all_retained_script_inventories_match_frozen_inputs(self):
        cases=fixture('source-scripts-v1.json')['cases'];self.assertEqual(len(cases),34)
        observations=fixture('source-scripts-observations-v1.json')['observations']
        self.assertEqual(set(observations),{c['id'] for c in cases})
        for case in cases:
            observation=observations[case['id']];raw=case['html'].encode('utf-8')
            source,decoding=scripts.http.decode(raw,['text/html; charset=utf-8'])
            scripts.validate_and_attribute(observation,source,raw,decoding)
            for mode,reading in observation['readings'].items():
                self.assertTrue(reading['complete']);self.assertEqual(projection(reading),case['expected'][mode])

    def test_combined_graphs_match_24_frozen_authored_expectations(self):
        cases=fixture('jsonld-html-v1.json')['cases'];self.assertEqual(len(cases),24)
        for case in cases:
            observation=self.observed(case['id'])
            self.assertEqual(observation['input'],request(case))
            for mode,reading in observation['readings'].items():
                value=dict(status=reading['status'],selected_count=reading['selected_count'],flattened=graph(observation,mode))
                self.assertEqual(value,case['expected'])
                combined=workflow.combine(observation['source']['readings'][mode])
                self.assertEqual(combined['combined_sha256'],reading['combined_sha256'])
                if observation['processing'] is not None:
                    processor=workflow.processor
                    processor.validate(observation['processing'],processor.prepare(observation['processing']['input']))

    def test_original_utf8_spans_and_bom_remain_distinct_from_parser_offsets(self):
        _,observation,source,raw,decoding=self.source('unicode-and-bom')
        self.assertEqual(decoding['consumed_bom_bytes'],3)
        scripts.validate_and_attribute(observation,source,raw,decoding)
        for reading in observation['readings'].values():
            script=reading['scripts'][0]
            for loc in [script['start_tag'],script['end_tag']]+[p['location'] for p in script['payload_parts']]:
                a,b=loc['body_span_bytes'];self.assertEqual(raw[a:b].decode(),loc['raw_source'])
            loc=script['end_tag'];self.assertGreater(loc['body_span_bytes'][0],loc['source_span_utf16'][0]+3)

    def test_crlf_and_nul_are_retained_as_raw_and_parsed_values(self):
        for id,raw_marker,parsed_marker in [('crlf-normalized','\r\n','\n'),('nul-replacement-retained','\x00','\ufffd')]:
            _,observation,_,_,_=self.source(id)
            script=observation['readings']['disabled']['scripts'][0]
            self.assertIn(raw_marker,''.join(p['location']['raw_source'] for p in script['payload_parts']))
            self.assertNotIn(raw_marker,script['payload']);self.assertIn(parsed_marker,script['payload'])

    def test_locations_payload_template_paths_and_population_tampering_refused(self):
        _,original,source,raw,decoding=self.source('unicode-and-bom')
        mutations=[lambda s:s.update(node_id=True),lambda s:s.update(template_path=[0]),
            lambda s:s.update(payload='forged'),lambda s:s['start_tag'].update(raw_source='forged'),
            lambda s:s['start_tag'].update(body_span_bytes=[0,1]),
            lambda s:s['end_tag'].update(source_span_utf16=[0,999999]),
            lambda s:s['payload_parts'][0].update(node_id=s['node_id'])]
        for mutate in mutations:
            result=copy.deepcopy(original);mutate(result['readings']['disabled']['scripts'][0])
            with self.assertRaises(ValueError):scripts.validate_and_attribute(result,source,raw,decoding)

    def test_incomplete_inventory_is_not_an_absence_or_partial_graph(self):
        _,result,source,raw,decoding=self.source('unicode-and-bom')
        reading=result['readings']['disabled'];reading.update(complete=False,reason='authored limit')
        with self.assertRaises(ValueError):scripts.validate_and_attribute(result,source,raw,decoding)
        reading.update(scripts=[],context_elements=[])
        scripts.validate_and_attribute(result,source,raw,decoding)
        combined=workflow.combine(reading)
        self.assertEqual(combined['status'],'source-incomplete');self.assertIsNone(combined['combined_json'])

    def test_noscript_hypotheses_remain_distinct(self):
        _,observed,_,_,_=self.source('noscript-body')
        self.assertEqual(observed['readings']['enabled']['scripts'],[])
        self.assertEqual(len(observed['readings']['disabled']['scripts']),1)

    def test_double_escaped_tokenizer_type_entities_and_base_csp_are_retained(self):
        cases=fixture('source-scripts-boundaries-v1.json')['cases']
        observations=fixture('source-scripts-boundaries-observations-v1.json')['observations']
        for case in cases:
            observed=observations[case['id']];raw=case['html'].encode()
            source,decoding=scripts.http.decode(raw,['text/html; charset=utf-8'])
            scripts.validate_and_attribute(observed,source,raw,decoding)
            for reading in observed['readings'].values():
                script=reading['scripts'][0]
                self.assertEqual(script['payload'],case['expected_payload'])
                if 'expected_type' in case:self.assertEqual(scripts.attributes(script)['type'],case['expected_type'])
                if 'expected_context_names' in case:
                    self.assertEqual([r['name'] for r in reading['context_elements']],case['expected_context_names'])

    def test_duplicate_html_ids_do_not_merge_and_entities_are_not_decoded(self):
        observed=self.observed('duplicate-html-id-no-collapse')
        self.assertEqual(len(graph(observed,'enabled')),2)
        self.assertEqual(self.observed('entities-not-html-decoded')['source']['readings']['enabled']['scripts'][0]['payload'],
                         '{"https://schema.org/name":"A &amp; B"}')

    def test_shared_blank_ids_combine_within_document_but_never_across_representations(self):
        first=self.observed('shared-blank-id');other=self.observed('same-blank-id-new-document')
        self.assertEqual(len(graph(first,'enabled')),1)
        self.assertEqual(graph(first,'enabled')[0]['https://schema.org/name'],[{'@value':'A'}])
        self.assertEqual(graph(other,'enabled')[0]['https://schema.org/name'],[{'@value':'Elsewhere'}])
        self.assertEqual(len(first['processing']['documents']),2)

    def test_root_graph_containers_and_cross_graph_descriptions_remain_distinct(self):
        cases=fixture('jsonld-html-graphs-v1.json')['cases']
        observations=fixture('jsonld-html-graphs-observations-v1.json')['observations']
        for case in cases:
            observed=observations[case['id']]
            for mode in ('enabled','disabled'):
                self.assertEqual(graph(observed,mode),case['expected']['flattened'])
                combined=workflow.combine(observed['source']['readings'][mode])
                self.assertIsInstance(json.loads(combined['combined_json']),list)
        observed=observations['blank-node-shared-between-graphs']
        a,b=graph(observed,'enabled')
        self.assertNotEqual(a['@id'],b['@id'])
        self.assertEqual(a['@graph'][0]['@id'],b['@graph'][0]['@id'])
        self.assertNotEqual(a['@graph'][0],b['@graph'][0])

    def test_bad_second_script_preserves_good_first_diagnostic_without_graph(self):
        observed=self.observed('valid-then-invalid')
        for row in observed['readings'].values():
            self.assertEqual([d['status'] for d in row['diagnostics']],['json-parsed','json-error'])
            self.assertIsNone(row['combined_sha256']);self.assertIsNone(row['processing_index'])
        self.assertIsNone(observed['processing'])

    def test_type_variants_remain_unresolved_not_absent_or_invalid_json(self):
        for id in ('uppercase-type-unresolved','spaced-type-unresolved','parameter-type-unresolved'):
            observed=self.observed(id)
            self.assertEqual(observed['readings']['enabled']['status'],'selection-unresolved')
            self.assertIsNone(observed['processing'])

    def test_combined_size_limit_does_not_keep_first_valid_subset(self):
        observed=self.observed('array-roots-combined');reading=observed['source']['readings']['enabled']
        for script in reading['scripts']:script['payload']=json.dumps({'https://schema.org/name':'x'*70000})
        result=workflow.combine(reading)
        self.assertEqual(result['status'],'combined-unsupported');self.assertIsNone(result['combined_json'])

    def test_context_preflight_runs_even_without_selected_scripts(self):
        observed=self.observed('no-script');req=observed['input']
        req['contexts']=[dict(url='https://example.test/context',raw_json='{}',sha256='0'*64)]
        with patch.object(scripts,'inventory') as inventory:
            with self.assertRaises(ValueError):workflow.observe(req,node='/missing/node')
            inventory.assert_not_called()

    def test_unknown_encoding_invalid_bytes_and_base64_have_no_fallback(self):
        original=self.observed('no-script')['input']
        for mode in ('encoding','bytes','base64','fields'):
            req=copy.deepcopy(original)
            if mode=='encoding':req['content_types']=['text/html']
            elif mode=='bytes':req['body_base64']=base64.b64encode(b'\xff').decode()
            elif mode=='base64':req['body_base64']='!!!!'
            else:req['ignored']=True
            with self.assertRaises(ValueError):workflow.prepare(req)

    def test_base_parameter_is_explicitly_only_a_hypothesis(self):
        observed=self.observed('local-base-context')
        self.assertEqual(observed['base_parameter']['status'],'supplied-hypothesis')
        self.assertEqual(observed['base_parameter']['iri'],'https://example.test/page')
        self.assertEqual(graph(observed,'enabled')[0]['@id'],'https://example.test/other/x')

    def test_missing_runtime_timeout_and_environment_do_not_fabricate_output(self):
        with self.assertRaisesRegex(ValueError,'unavailable'):
            scripts.inventory(b'<p>x',content_types=['text/html; charset=utf-8'],node='/missing/node')
        with patch.object(scripts.shutil,'which',return_value='/synthetic/node'), \
             patch.object(scripts.subprocess,'run',side_effect=subprocess.TimeoutExpired('node',30)) as run, \
             patch.dict(os.environ,{'NODE_OPTIONS':'--import unexpected','NODE_PATH':'/unexpected'}):
            with self.assertRaisesRegex(ValueError,'deadline'):
                scripts.inventory(b'<p>x',content_types=['text/html; charset=utf-8'],node='/synthetic/node')
        self.assertFalse(any(k.startswith('NODE_') for k in run.call_args.kwargs['env']))
        self.assertIn('--permission',run.call_args.args[0]);self.assertEqual(run.call_args.kwargs['stdin'],subprocess.DEVNULL)

    def test_replay_rejects_changed_sources_graphs_runtime_and_input_binding(self):
        original=self.observed('shared-blank-id')
        # Recalculation is mocked only for these replay guard tests. Actual Node
        # replays of every frozen case are in the separate explicit qualifier.
        with patch.object(workflow,'identity',return_value=original['source_sha256']), \
             patch.object(workflow,'observe',return_value=original):
            self.assertEqual(workflow.replay(original,node='unused'),original)
            for mode in ('source','graph','runtime','binding','status'):
                changed=copy.deepcopy(original)
                if mode=='source':changed['source_sha256']['experiments/jsonld_html.py']='0'*64
                elif mode=='graph':changed['processing']['documents'][0]['flattened']=[]
                elif mode=='runtime':changed['source']['runtime']['node']='v24.0.0'
                elif mode=='binding':changed['input_sha256']='0'*64
                else:changed['readings']['enabled']['status']='absent'
                with self.subTest(mode=mode),self.assertRaises(ValueError):workflow.replay(changed,node='unused')

    def test_cli_refuses_existing_output_and_invalid_input(self):
        with tempfile.TemporaryDirectory() as folder:
            folder=Path(folder);input=folder/'input.json';output=folder/'output.json'
            input.write_text('{}');output.write_text('preserve')
            result=subprocess.run([sys.executable,str(workflow.ROOT/'experiments/jsonld_html.py'),str(input),
                '--node','/missing/node','--output',str(output)],capture_output=True,text=True)
            self.assertEqual(result.returncode,64);self.assertEqual(output.read_text(),'preserve')


if __name__=='__main__':unittest.main()
