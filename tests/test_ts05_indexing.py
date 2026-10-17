"""TS05 authored policy cases, native import and offline replay; no live observations."""
import copy
import hashlib
import json
from pathlib import Path
import socket
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
import tsep
from adapters import captures, replay
from conformance.corpus import expand
from conformance.evaluate import evaluate
from conformance.ts05_indexing import assess
from reports import html


def target():
    return {
        "url": "https://example.invalid/ts05-policy",
        "observed_at": "2026-10-16T15:00:00Z",
        "configuration": {
            "crawl_method": "robots-txt",
            "crawl_effect": "allow",
            "indexing_method": "x-robots-tag-noindex",
            "protection_method": "authentication",
        },
        "intent": {
            "ts05_policy": {
                "applicability": "applicable",
                "declared_at": "2026-10-16T14:00:00Z",
                "scope": "Synthetic policy model only",
                "crawl": {"method": "robots-txt", "effect": "allow"},
                "indexing": {
                    "goal": "exclude",
                    "method": "x-robots-tag-noindex",
                    "directive_visibility": "fetchable",
                },
                "protection": {"goal": "private", "method": "authentication"},
                "actual_index_state": "not-observed",
                "claims": [
                    {"kind": "deindex", "level": "statement",
                     "basis": ["noindex-directive"]},
                    {"kind": "confidentiality", "level": "statement",
                     "basis": ["authentication"]},
                ],
            }
        },
    }


def raw_input(value, rule="TS05-A01"):
    return {"input_version": "1", "rules": [rule], "targets": [value]}


def frozen_cases():
    corpus = expand(tsep.read_json(ROOT / "conformance/cases.json"))
    return [case for case in corpus["cases"] if case["id"].startswith("ts05-policy-")]


class TS05Indexing(unittest.TestCase):
    def test_authored_conformance_corpus_routes_through_engine(self):
        cases = frozen_cases()
        self.assertEqual(len(cases), 4)
        for case in cases:
            with self.subTest(case=case["id"]), patch.object(
                    socket, "socket", side_effect=AssertionError("No network")):
                before = copy.deepcopy(case["input"])
                actual=evaluate(case["input"])
                self.assertEqual([{key: row[key] for key in ("rule_id","target","outcome")}
                                  for row in actual], case["expected"])
                self.assertEqual(case["input"], before)

    def test_positive_result_is_only_plan_consistency(self):
        outcome, reason = assess(target(), "TS05-A01")
        self.assertEqual(outcome, "pass")
        self.assertIn("actual index state", reason)
        self.assertIn("confidentiality are not established", reason)

    def test_disallow_only_deindexing_guarantee_is_fail(self):
        value = target()
        policy = value["intent"]["ts05_policy"]
        policy["crawl"]["effect"] = "disallow"
        policy["indexing"].update(goal="exclude", method="none",
                                  directive_visibility="blocked-by-robots")
        value["configuration"].update(crawl_effect="disallow", indexing_method="none")
        policy["claims"][0].update(level="guarantee", basis=["robots-disallow"])
        self.assertEqual(assess(value, "TS05-A01")[0], "fail")

    def test_blocked_noindex_guarantee_is_fail_but_without_guarantee_is_unknown(self):
        value = target()
        policy = value["intent"]["ts05_policy"]
        policy["crawl"]["effect"] = "disallow"
        policy["indexing"].update(method="meta-noindex",
                                  directive_visibility="blocked-by-robots")
        value["configuration"].update(crawl_effect="disallow", indexing_method="meta-noindex")
        policy["claims"][0].update(
            level="guarantee", basis=["robots-disallow", "noindex-directive"])
        self.assertEqual(assess(value, "TS05-A01")[0], "fail")
        policy["claims"][0]["level"] = "statement"
        self.assertEqual(assess(value, "TS05-A01")[0], "inconclusive")

    def test_robots_only_is_not_confidentiality(self):
        value = target()
        policy = value["intent"]["ts05_policy"]
        policy["protection"].update(goal="private", method="robots-only")
        value["configuration"]["protection_method"] = "robots-only"
        policy["claims"][1].update(level="guarantee", basis=["robots-disallow"])
        self.assertEqual(assess(value, "TS05-A01")[0], "fail")

    def test_configuration_disagreement_is_fail(self):
        value = target()
        value["configuration"]["crawl_effect"] = "disallow"
        self.assertEqual(assess(value, "TS05-A01")[0], "fail")

    def test_fetchable_noindex_contradicts_include_goal(self):
        value = target()
        policy = value["intent"]["ts05_policy"]
        policy["indexing"]["goal"] = "include"
        self.assertEqual(assess(value, "TS05-A01")[0], "fail")

    def test_missing_or_future_plan_is_inconclusive(self):
        missing = target()
        del missing["intent"]["ts05_policy"]
        self.assertEqual(assess(missing, "TS05-A01")[0], "inconclusive")
        future = target()
        future["intent"]["ts05_policy"]["declared_at"] = "2026-10-17T00:00:00Z"
        self.assertEqual(assess(future, "TS05-A01")[0], "inconclusive")

    def test_actual_index_state_is_out_of_scope(self):
        value = target()
        value["intent"]["ts05_policy"]["actual_index_state"] = "excluded"
        self.assertEqual(assess(value, "TS05-A01")[0], "inconclusive")

    def test_unsupported_method_never_passes(self):
        for axis, field in (("crawl", "method"), ("indexing", "method"),
                            ("protection", "method")):
            value = target()
            policy = value["intent"]["ts05_policy"]
            policy[axis][field] = "other"
            config_field = {"crawl": "crawl_method", "indexing": "indexing_method",
                            "protection": "protection_method"}[axis]
            value["configuration"][config_field] = "other"
            self.assertEqual(assess(value, "TS05-A01")[0], "inconclusive")

    def test_non_applicability_requires_positive_dated_review(self):
        value = target()
        policy = value["intent"]["ts05_policy"]
        policy.clear()
        policy.update(applicability="not-applicable", non_applicability_review={
            "complete": True, "outcome": "not-applicable",
            "rationale": "Authored review: no relevant policy in this declared fixture scope.",
            "reviewed_at": "2026-10-16T14:30:00Z",
        })
        self.assertEqual(assess(value, "TS05-A01")[0], "not-applicable")
        policy["non_applicability_review"]["reviewed_at"] = "2026-10-17T00:00:00Z"
        self.assertEqual(assess(value, "TS05-A01")[0], "inconclusive")

    def test_duplicate_or_missing_claim_axis_cannot_pass(self):
        value = target()
        policy = value["intent"]["ts05_policy"]
        policy["claims"].append(copy.deepcopy(policy["claims"][0]))
        self.assertEqual(assess(value, "TS05-A01")[0], "inconclusive")
        policy["claims"]=policy["claims"][:1]
        self.assertEqual(assess(value, "TS05-A01")[0], "inconclusive")

    def test_application_bundle_and_outside_process_replay(self):
        case = next(c for c in frozen_cases() if c["id"] == "ts05-policy-separated-plan")
        with tempfile.TemporaryDirectory() as directory, patch.object(
                socket, "socket", side_effect=AssertionError("No collection")):
            root = Path(directory)
            source = root / "input.json"
            source.write_text(json.dumps(case["input"], ensure_ascii=False), encoding="utf-8")
            source_bytes = source.read_bytes()
            captures.build(source, root / "bundle", assessor="Synthetic application importer",
                           label="Synthetic TS05 policy model",
                           selection_method="Four predeclared synthetic policy cases",
                           access="synthetic")
            report = tsep.read_json(root / "bundle/report.json")
            self.assertEqual(report["results"][0]["status"], "C")
            self.assertEqual(report["results"][0]["atomic_results"][0]["outcome"], "pass")
            self.assertEqual(source.read_bytes(), source_bytes)
            self.assertEqual(tsep.read_json(root / "bundle/input.json"), case["input"])
            replayed = replay.replay(root / "bundle", root / "replayed")
            self.assertTrue(replayed["replayed"])
            self.assertTrue(replayed["same_atomic_results"])
            self.assertTrue(replayed["same_gate"])
            for language in ("fr", "en"):
                page = html.render(root / "bundle/report.json", language=language)
                self.assertNotIn("<script", page)
                self.assertIn("TS05", page)

    def test_positive_inventory_is_whole_control_na_not_atomic_exemption(self):
        case = next(c for c in frozen_cases()
                    if c['id'] == 'ts05-policy-dated-not-applicable')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / 'input.json'
            source.write_text(json.dumps(case['input'], ensure_ascii=False), encoding='utf-8')
            captures.build(source, root / 'bundle', assessor='Synthetic reviewer',
                           label='Synthetic all-target NA review',
                           selection_method='Complete declared synthetic scope', access='synthetic')
            report = tsep.read_json(root / 'bundle/report.json')
            result = report['results'][0]
            self.assertEqual(result['status'], 'NA')
            self.assertEqual(result['atomic_results'], [])
            intent = next(a for a in report['artifacts'] if a['kind'] == 'intent')
            self.assertIn(intent['id'], result['evidence_ids'])
            replayed = replay.replay(root / 'bundle', root / 'replayed')
            self.assertTrue(replayed['same_gate'])

    def test_partial_non_applicability_cannot_close_a_mixed_scope(self):
        unavailable = next(c for c in frozen_cases()
                           if c['id'] == 'ts05-policy-dated-not-applicable')['input']['targets'][0]
        applicable = next(c for c in frozen_cases()
                          if c['id'] == 'ts05-policy-separated-plan')['input']['targets'][0]
        applicable = copy.deepcopy(applicable)
        applicable['url'] = 'https://example.invalid/ts05-applicable'
        data = {'input_version': '1', 'rules': ['TS05-A01'],
                'targets': [unavailable, applicable]}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / 'input.json'
            source.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
            captures.build(source, root / 'bundle', assessor='Synthetic reviewer',
                           label='Synthetic mixed applicability scope',
                           selection_method='Two explicitly declared synthetic targets', access='synthetic')
            report = tsep.read_json(root / 'bundle/report.json')
            result = report['results'][0]
            outcomes = {a['target']: a['outcome'] for a in result['atomic_results']}
            self.assertEqual(result['status'], 'NT')
            self.assertEqual(outcomes[unavailable['url']], 'inconclusive')
            self.assertEqual(outcomes[applicable['url']], 'pass')
            replayed = replay.replay(root / 'bundle', root / 'replayed')
            self.assertTrue(replayed['same_gate'])

    def test_source_capture_fingerprint(self):
        capture = ROOT / "docs/source-captures/ts05-google-search-central-2026-10-16.md"
        digest = hashlib.sha256(capture.read_bytes()).hexdigest()
        self.assertEqual(capture.with_suffix(".sha256").read_text(encoding="ascii").split()[0], digest)


if __name__ == "__main__":
    unittest.main()
