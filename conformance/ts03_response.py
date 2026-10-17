"""Bounded synthetic TS03 HTTP response-plan assessor; no network collection."""
import hashlib
import json
import re
from urllib.parse import urlsplit

import tsep
from conformance.http import Unknown, message, need

READER = "ts03-http-matrix-v1"
CONTENT_READER = "ts03-content-expectations-v1"
UA = "TSEP-TS03-fixture/1"
MAX_ROUTES = 64
MAX_CASES = 128
MAX_MARKERS = 32


def _hash(value):
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True,
                     separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _url(value, label):
    need(isinstance(value, str) and len(value) <= 2048,
         "Missing or excessive TS03 " + label)
    parts = urlsplit(value)
    try:
        port = parts.port
    except ValueError as error:
        raise Unknown("Invalid TS03 URL port") from error
    host = (parts.hostname or "").lower()
    need(parts.scheme in ("http", "https") and host.endswith(".invalid")
         and not parts.username and not parts.password and not parts.query
         and not parts.fragment and not re.search(r"[\s\x00-\x1f]", value)
         and (port is None or 1 <= port <= 65535),
         "TS03 accepts only query-free synthetic .invalid URLs")
    return parts


def _markers(value, label):
    need(type(value) is list and 0 < len(value) <= MAX_MARKERS
         and all(isinstance(item, str) and item.strip()
                 and len(item.encode("utf-8")) <= 128 for item in value)
         and len(value) == len(set(value)),
         "Missing, duplicate or excessive TS03 " + label)
    return value


def _planned(policy, observed_at):
    need(isinstance(policy, dict) and policy.get("reader") == READER,
         "Missing or unsupported TS03 prior plan")
    need(policy.get("applicability") == "applicable",
         "TS03 applicability is not explicitly applicable")
    need(isinstance(policy.get("scope"), str) and policy["scope"].strip(),
         "Missing TS03 declared synthetic scope")
    declared = tsep.timestamp(policy.get("declared_at"))
    observed = tsep.timestamp(observed_at)
    need(declared <= observed, "TS03 plan is missing, invalid or postdates observation")
    review = policy.get("plan_review")
    need(isinstance(review, dict) and review.get("complete") is True
         and review.get("provenance") == "synthetic-exercise"
         and isinstance(review.get("rationale"), str) and review["rationale"].strip()
         and tsep.timestamp(review.get("reviewed_at")) <= declared,
         "Missing or late TS03 synthetic plan review")
    routes = policy.get("routes")
    need(type(routes) is list and 3 <= len(routes) <= MAX_ROUTES,
         "Missing or excessive TS03 route plan")
    by_id, states = {}, set()
    for route in routes:
        need(isinstance(route, dict), "Malformed TS03 route plan")
        route_id, state = route.get("id"), route.get("state")
        need(isinstance(route_id, str) and re.fullmatch(r"[A-Za-z0-9_-]{1,64}", route_id)
             and route_id not in by_id, "Missing or duplicate TS03 route id")
        need(state in ("existing", "removed", "nonexistent"),
             "Unsupported TS03 route state")
        parts = _url(route.get("url"), "route URL")
        statuses = route.get("expected_statuses")
        allowed = {200} if state == "existing" else {404, 410}
        need(type(statuses) is list and statuses and
             all(type(status) is int and status in allowed for status in statuses)
             and len(statuses) == len(set(statuses)),
             "Invalid TS03 status expectation for route state")
        _markers(route.get("required_markers"), "required markers")
        forbidden = route.get("forbidden_markers", [])
        need(type(forbidden) is list and len(forbidden) <= MAX_MARKERS
             and all(isinstance(item, str) and item.strip()
                     and len(item.encode("utf-8")) <= 128 for item in forbidden)
             and len(forbidden) == len(set(forbidden))
             and not set(route["required_markers"]) & set(forbidden),
             "Malformed or contradictory TS03 forbidden markers")
        by_id[route_id] = (route, parts)
        states.add(state)
    need(states == {"existing", "removed", "nonexistent"},
         "TS03 plan must include existing, removed and nonexistent routes")
    return by_id


def _request(case, route, parts):
    first, headers, body = message(case.get("request"))
    path = (parts.path or "/")
    need(first == "GET " + path + " HTTP/1.1",
         "TS03 requires an unconditional GET for the planned route")
    need(set(headers) == {"host", "user-agent"}
         and headers["host"] == [parts.netloc]
         and headers["user-agent"] == [UA]
         and not body,
         "TS03 request attribution or headers are unsupported")


def assess(target, rule):
    """Compare supplied response samples with a bound synthetic prior plan."""
    try:
        need(rule == "TS03-A01", "Unsupported TS03 rule")
        intent = target.get("intent")
        need(isinstance(intent, dict), "Missing TS03 intent")
        policy = intent.get("ts03_response")
        observed_at = target.get("observed_at")
        by_id = _planned(policy, observed_at)
        configuration = target.get("configuration")
        record = configuration.get("ts03_response") if isinstance(configuration, dict) else None
        need(isinstance(record, dict) and record.get("reader") == READER
             and record.get("plan_sha256") == _hash(policy),
             "TS03 plan/configuration fingerprint mismatch")
        content = target.get("content")
        need(isinstance(content, dict) and content.get("reader") == CONTENT_READER,
             "Missing TS03 content expectations")
        expected_content = [
            {"route_id": route_id,
             "required_markers": route["required_markers"],
             "forbidden_markers": route.get("forbidden_markers", [])}
            for route_id, (route, _) in by_id.items()
        ]
        content_mismatch = content.get("routes") != expected_content
        matrix = target.get("http")
        need(isinstance(matrix, dict) and matrix.get("reader") == READER,
             "Missing or unsupported TS03 HTTP matrix")
        cases = matrix.get("cases")
        need(type(cases) is list and len(cases) <= MAX_CASES,
             "Missing or excessive TS03 HTTP cases")
        issues, failures, seen = [], [], {}
        try:
            matrix_time = tsep.timestamp(matrix.get("observed_at"))
            need(tsep.timestamp(policy["declared_at"]) <= matrix_time <=
                 tsep.timestamp(observed_at), "TS03 matrix time is outside the planned window")
        except (Unknown, ValueError, TypeError, KeyError) as error:
            issues.append(str(error))

        for case in cases:
            if not isinstance(case, dict):
                issues.append("Malformed TS03 HTTP case")
                continue
            route_id = case.get("route_id")
            if route_id not in by_id:
                issues.append("Unplanned TS03 route capture")
                continue
            seen[route_id] = seen.get(route_id, 0) + 1
            route, parts = by_id[route_id]
            try:
                need(case.get("complete") is True, "Incomplete TS03 HTTP capture")
                need(case.get("url") == route["url"],
                     "TS03 capture URL differs from prior route plan")
                case_time = tsep.timestamp(case.get("observed_at"))
                need(tsep.timestamp(policy["declared_at"]) <= case_time <=
                     tsep.timestamp(observed_at), "TS03 case time is outside the planned window")
                _request(case, route, parts)
                status, headers, body = message(case.get("response"), True)
                if status in (206, 304):
                    issues.append("TS03 partial/conditional response cannot establish a full body")
                    continue
                if status not in route["expected_statuses"]:
                    failures.append("TS03 status contradiction for " + route_id
                                    + ": observed " + str(status))
                    continue
                body_text = body.decode("utf-8", errors="strict") if isinstance(body, bytes) else body
                missing = [marker for marker in route["required_markers"] if marker not in body_text]
                present = [marker for marker in route.get("forbidden_markers", [])
                           if marker in body_text]
                if missing or present:
                    failures.append("TS03 body-marker contradiction for " + route_id
                                    + ": " + json.dumps(
                                        {"missing": missing, "forbidden": present},
                                        ensure_ascii=False))
            except (Unknown, tsep.Invalid, UnicodeError, KeyError, TypeError, ValueError) as error:
                issues.append(str(error))

        if failures:
            return "fail", "; ".join(failures) + "; supplied point-in-time matrix only"
        if content_mismatch:
            issues.append("TS03 content expectations differ from the bound plan")
        if matrix.get("complete") is not True:
            issues.append("TS03 HTTP matrix is not marked complete")
        if set(seen) != set(by_id):
            issues.append("TS03 matrix omits one or more planned route states")
        if any(count != 1 for count in seen.values()):
            issues.append("Duplicate TS03 route capture")
        if issues:
            return "inconclusive", "; ".join(issues) + "; no whole-site or soft-404 classification"
        return "pass", ("Complete supplied synthetic matrix matches declared status and literal body criteria; "
                        "does not establish real routes, persistent availability, indexing or soft-404 classification")
    except (Unknown, tsep.Invalid, KeyError, TypeError, ValueError, UnicodeError) as error:
        return "inconclusive", str(error)
