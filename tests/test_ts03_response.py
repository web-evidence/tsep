"""TS03 synthetic response-plan cases, importer and offline replay; no live HTTP."""
import copy
import json
from pathlib import Path
import socket
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import tsep
from adapters.captures import build
from adapters.replay import replay
from conformance.corpus import expand
from conformance.evaluate import evaluate
from conformance.ts03_response import assess

FIXTURE=tsep.read_json(ROOT/"tests/fixtures/ts03-response-cases.json")
CASES={case["id"]:case for case in FIXTURE["cases"]}


class TS03Response(unittest.TestCase):
    def test_frozen_cases_match_native_rule_and_corpus_without_network(self):
        self.assertTrue(FIXTURE["synthetic"])
        self.assertEqual(len(CASES),13)
        corpus=expand(tsep.read_json(ROOT/"conformance/cases.json"))
        frozen={case["id"]:case for case in corpus["cases"]}
        for case_id,case in CASES.items():
            self.assertIn(case_id,frozen)
            with self.subTest(case=case_id), patch.object(socket,"socket",side_effect=AssertionError("No socket")), patch.object(socket,"getaddrinfo",side_effect=AssertionError("No DNS")):
                before=copy.deepcopy(case["input"])
                target=case["input"]["targets"][0]
                actual,_=assess(target,"TS03-A01")
                self.assertEqual(actual,case["expected"][0]["outcome"])
                rows=evaluate(case["input"])
                self.assertEqual([(row["rule_id"],row["target"],row["outcome"]) for row in rows],
                                 [(row["rule_id"],row["target"],row["outcome"]) for row in case["expected"]])
                self.assertEqual(before,case["input"])

    def test_attributable_failure_survives_duplicate(self):
        case=CASES["ts03-status-fail-survives-duplicate"]
        self.assertEqual(evaluate(case["input"])[0]["outcome"],"fail")

    def test_native_import_export_and_offline_replay(self):
        # Draft.10 requires A02 too; the unchanged A01 pass alone is partial.
        for case_id,status in (("ts03-complete-synthetic-matrix","NT"),
                               ("ts03-removed-route-200","NC"),
                               ("ts03-missing-route-observation","NT")):
            with self.subTest(case=case_id), tempfile.TemporaryDirectory() as folder, patch.object(socket,"socket",side_effect=AssertionError("No collection")), patch.object(socket,"getaddrinfo",side_effect=AssertionError("No DNS")):
                base=Path(folder);source=base/"input.json";bundle=base/"bundle";out=base/"replay"
                source.write_text(json.dumps(CASES[case_id]["input"],ensure_ascii=False),encoding="utf-8")
                summary=build(source,bundle,assessor="Synthetic TSEP reviewer",label="TS03 synthetic response matrix",selection_method="Thirteen named .invalid cases only",access="synthetic",mode="semiAuto",selected=["TS03"])
                report=tsep.read_json(bundle/"report.json")
                self.assertEqual(report["results"][0]["status"],status)
                self.assertEqual(summary,tsep.validate(report,bundle))
                replay_summary=replay(bundle,out)
                record=tsep.read_json(out/"replay.json")
                self.assertTrue(record["replayed"])
                self.assertTrue(record["same_report_results"])
                self.assertTrue(record["same_gate"])
                self.assertEqual(replay_summary["decision"],summary["decision"])

    def test_pass_limitation_disclaims_real_soft404_classification(self):
        outcome,reason=assess(CASES["ts03-complete-synthetic-matrix"]["input"]["targets"][0],"TS03-A01")
        self.assertEqual(outcome,"pass")
        self.assertIn("soft-404 classification",reason)


if __name__=="__main__":
    unittest.main()
