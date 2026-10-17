"""TS06 bounded synthetic access-matrix assessor; no network collection."""
import base64
import hashlib
import html
import json
import re
from urllib.parse import quote, unquote, urljoin, urlsplit

import tsep
from conformance.http import Unknown, message, need, raw_bytes

READER = "ts06-http-matrix-v1"
UA = "TSEP-TS06-fixture/1"
ROLE_HEADER = "x-tsep-synthetic-role"
MAX_ROUTES = 64
MAX_ROLES = 32
MAX_TESTS = 256
MAX_HOPS = 12
MAX_MARKERS = 32


def _hash(value):
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True,
                         separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _unique(values, label):
    need(len(values) == len(set(values)), "Duplicate TS06 " + label)


def _url(value, label):
    need(isinstance(value, str) and len(value) <= 2048,
         "Missing or excessive TS06 " + label)
    parts = urlsplit(value)
    try:
        port = parts.port
    except ValueError as error:
        raise Unknown("Invalid TS06 URL port") from error
    need(parts.scheme in ("http", "https") and parts.hostname and not parts.username
         and not parts.password and not parts.fragment and not parts.query
         and parts.hostname.lower().endswith(".invalid")
         and not re.search(r"[\s\x00-\x1f]", value)
         and (port is None or 1 <= port <= 65535),
         "TS06 uses query-free synthetic .invalid URL labels only")
    return parts


def _marker_forms(marker):
    raw = marker.encode("utf-8")
    return {value.casefold() for value in (
        marker, html.escape(marker, quote=True), quote(marker, safe=""),
        json.dumps(marker, ensure_ascii=True)[1:-1], raw.hex()) if value}


def _contains_base64_marker(candidates, marker):
    raw_marker = marker.encode("utf-8")
    for candidate in candidates:
        for match in re.finditer(r"[A-Za-z0-9+/_=-]{12,}", candidate):
            token = match.group(0)
            # Bounded chunks retain enough overlap for a 128-byte declared marker.
            for start in range(0, len(token), 512):
                piece = token[start:start + 520]
                if len(piece) < 12:
                    continue
                for offset in range(min(4, len(piece))):
                    value = piece[offset:]
                    value += "=" * ((-len(value)) % 4)
                    try:
                        decoded = base64.b64decode(value, altchars=b"-_", validate=True)
                    except (ValueError, base64.binascii.Error):
                        continue
                    if raw_marker in decoded:
                        return True
    return False


def _leaks(markers, headers, body):
    header_text = "\n".join(
        str(value) for values in headers.values() for value in values)
    if isinstance(body, bytes):
        raw = body
        try:
            text = body.decode("utf-8", errors="strict")
        except UnicodeDecodeError:
            text = ""
    else:
        text = str(body)
        raw = text.encode("utf-8")
    candidates = [text, html.unescape(text), header_text,
                  html.unescape(header_text), raw.decode("latin-1")]
    current = text
    for _ in range(3):
        decoded = unquote(current)
        if decoded == current:
            break
        candidates.append(decoded)
        current = decoded
    candidates.append(re.sub(
        r"\\u([0-9a-fA-F]{4})",
        lambda match: chr(int(match.group(1), 16)), text))
    for marker in markers:
        forms = _marker_forms(marker)
        if any(form in candidate.casefold()
               for form in forms for candidate in candidates):
            return True
        if marker.encode("utf-8") in raw:
            return True
        if _contains_base64_marker(candidates, marker):
            return True
    return False


def _origin(parts):
    default = 443 if parts.scheme.lower() == "https" else 80
    return parts.scheme.lower(), (parts.hostname or "").lower(), parts.port or default


def _target_url_for_hop(value, expected):
    parts = _url(value, "redirect URL")
    expected_parts = _url(expected, "expected URL")
    need(_origin(parts) == _origin(expected_parts),
         "Cross-origin TS06 redirect is outside the bounded matrix")
    return value


def _denial(status, redirected_to_login, route):
    if status in (401, 403):
        return True
    declared = route.get("denial_statuses", [])
    return status in declared or (redirected_to_login and 200 <= status < 300)


def _raw_response_leaks(hop, markers):
    raw_response = hop.get("response")
    try:
        _, headers, body = message(raw_response, True)
    except (Unknown, TypeError, ValueError):
        try:
            wire = raw_bytes(raw_response)
        except (Unknown, TypeError, ValueError):
            return False
        return _leaks(markers, {}, wire)
    return _leaks(markers, headers, body)


def _inspect_case(record, route, role, test):
    from conformance.evaluate import exchange

    need(record.get("route_id") == route["id"]
         and record.get("role_id") == role["id"],
         "TS06 HTTP case route/role attribution differs from the prior plan")
    try:
        observed = tsep.timestamp(record.get("observed_at"))
    except (tsep.Invalid, TypeError, ValueError) as error:
        raise Unknown("Missing or invalid TS06 case observation time") from error
    need(record.get("complete") is True, "Incomplete TS06 HTTP case")
    hops = record.get("hops")
    need(type(hops) is list and 0 < len(hops) <= MAX_HOPS,
         "Missing or excessive TS06 HTTP hops")
    expected = route["url"]
    redirect_seen = False
    redirected_to_login = False
    final_status = None
    exposed_markers = set()
    for index, hop in enumerate(hops):
        status, headers, body = exchange(hop, expected, UA)
        first, request_headers, _ = message(hop.get("request"))
        need(first.startswith("GET "), "TS06 supports only captured GET requests")
        need(set(request_headers) == {"host", "user-agent", ROLE_HEADER},
             "TS06 synthetic fixtures reject undeclared request credentials and headers")
        roles = request_headers.get(ROLE_HEADER, [])
        need(roles == [role["id"]],
             "Missing or ambiguous synthetic role attribution")
        markers = route["canaries"]
        if role["authorization"] == "unauthorized-synthetic":
            if _leaks(markers, headers, body):
                return "leak", status, exposed_markers
        for marker in markers:
            if _leaks([marker], {}, body):
                exposed_markers.add(marker)
        if status in (206, 304):
            return "incomplete", status, exposed_markers
        if status in (301, 302, 303, 307, 308):
            locations = headers.get("location", [])
            need(len(locations) == 1 and locations[0],
                 "Missing or ambiguous TS06 Location")
            destination = urljoin(expected, locations[0])
            destination = _target_url_for_hop(destination, expected)
            path = urlsplit(destination).path or "/"
            login_paths = route.get("login_paths", [])
            if any(path == prefix or path.startswith(prefix.rstrip("/") + "/")
                   for prefix in login_paths):
                redirected_to_login = True
            else:
                raise Unknown("Redirect is not a declared same-origin authentication route")
            redirect_seen = True
            need(index < len(hops) - 1, "Unfinished TS06 redirect chain")
            expected = destination
            continue
        need(index == len(hops) - 1, "Unexpected TS06 hop after terminal response")
        final_status = status
    need(final_status is not None, "Missing TS06 terminal response")
    return (_denial(final_status, redirect_seen and redirected_to_login, route)
            and "denied" or "other", final_status, exposed_markers)


def _non_applicable(plan, observed_at):
    review = plan.get("inventory_review")
    need(isinstance(review, dict) and review.get("complete") is True
         and review.get("outcome") == "no-sensitive-routes",
         "TS06 NA requires a complete positive inventory review")
    need(isinstance(review.get("rationale"), str) and review["rationale"].strip(),
         "Missing TS06 NA rationale")
    need(review.get("review_type") == "authored-synthetic",
         "TS06 inventory review must be labelled synthetic")
    need(tsep.timestamp(review.get("reviewed_at")) <= tsep.timestamp(observed_at),
         "TS06 NA review is future-dated")
    need(not plan.get("routes") and not plan.get("tests")
         and not plan.get("cache_triplets"),
         "TS06 NA inventory contradicts a nonempty sensitive-route plan")
    return "not-applicable", (
        "A supplied dated synthetic inventory records no sensitive route "
        "in this declared scope")


def assess(target, rule):
    try:
        need(rule == "TS06-A01", "Unsupported TS06 rule")
        _url(target.get("url"), "report target label")
        observed_at = target.get("observed_at")
        plan = target.get("intent", {}).get("ts06_access")
        need(isinstance(plan, dict), "Missing prior TS06 access plan")
        config = target.get("configuration", {}).get("ts06_access")
        need(isinstance(config, dict) and set(config) == {"reader", "plan_sha256"}
             and config.get("reader") == READER,
             "Missing or unsupported TS06 configuration binding")
        if config.get("plan_sha256") != _hash(plan):
            return "fail", "TS06 configuration and intent plan fingerprint disagree"
        if plan.get("applicability") == "not-applicable":
            return _non_applicable(plan, observed_at)
        need(plan.get("applicability") == "applicable",
             "TS06 applicability is not explicitly declared")
        need(tsep.timestamp(plan.get("declared_at")) <= tsep.timestamp(observed_at),
             "TS06 access plan is missing or postdates observation")
        need(isinstance(plan.get("scope"), str) and plan["scope"].strip(),
             "Missing TS06 declared scope")

        routes, roles, tests = plan.get("routes"), plan.get("roles"), plan.get("tests")
        triplets = plan.get("cache_triplets")
        need(type(routes) is list and 0 < len(routes) <= MAX_ROUTES,
             "Missing or excessive TS06 route inventory")
        need(type(roles) is list and 0 < len(roles) <= MAX_ROLES,
             "Missing or excessive TS06 role inventory")
        need(type(tests) is list and 0 < len(tests) <= MAX_TESTS,
             "Missing or excessive TS06 planned test matrix")
        need(type(triplets) is list and triplets,
             "TS06 cache-path cold/seed/replay triplets must be declared")
        route_map, role_map, test_map = {}, {}, {}
        for route in routes:
            need(isinstance(route, dict), "Malformed TS06 route")
            route_id = route.get("id")
            need(isinstance(route_id, str)
                 and re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", route_id),
                 "Invalid TS06 route id")
            _url(route.get("url"), "route")
            markers = route.get("canaries")
            need(type(markers) is list and 0 < len(markers) <= MAX_MARKERS
                 and all(isinstance(marker, str) and 8 <= len(marker) <= 128
                         and marker.strip() == marker for marker in markers),
                 "Each TS06 sensitive route needs bounded synthetic canaries")
            _unique(markers, "route canary")
            login_paths = route.get("login_paths", [])
            need(type(login_paths) is list and login_paths
                 and all(isinstance(path, str) and path.startswith("/")
                         and not path.startswith("//")
                         and ".." not in path.split("/") for path in login_paths),
                 "TS06 auth redirects need same-origin login path allowlist")
            _unique(login_paths, "login path")
            denial_statuses = route.get("denial_statuses", [])
            need(type(denial_statuses) is list
                 and all(type(status) is int and status == 404
                         for status in denial_statuses),
                 "Only an explicitly planned 404 may be accepted as a hidden route")
            _unique(denial_statuses, "declared denial status")
            need(route_id not in route_map, "Duplicate TS06 route id")
            route_map[route_id] = route
        for role in roles:
            need(isinstance(role, dict) and isinstance(role.get("id"), str)
                 and re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", role["id"])
                 and role.get("authorization") in
                     ("authorized-synthetic", "unauthorized-synthetic"),
                 "TS06 roles must be explicitly labelled synthetic")
            need(role["id"] not in role_map, "Duplicate TS06 role id")
            role_map[role["id"]] = role
        need(role_map.get("anonymous", {}).get("authorization")
             == "unauthorized-synthetic",
             "TS06 requires an explicit anonymous synthetic role")
        for test in tests:
            need(isinstance(test, dict) and isinstance(test.get("id"), str)
                 and re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", test["id"])
                 and test.get("route_id") in route_map
                 and test.get("role_id") in role_map,
                 "Malformed TS06 planned test")
            need(test["id"] not in test_map, "Duplicate TS06 planned test id")
            test_map[test["id"]] = test

        expected_unauthorized = {
            (route_id, role_id) for route_id in route_map
            for role_id, role in role_map.items()
            if role["authorization"] == "unauthorized-synthetic"}
        actual_unauthorized = {
            (test["route_id"], test["role_id"]) for test in tests
            if role_map[test["role_id"]]["authorization"]
            == "unauthorized-synthetic"}
        need(actual_unauthorized == expected_unauthorized,
             "TS06 matrix must cover every route and unauthorized synthetic role")
        authorized_ids = {test["id"] for test in tests
                          if role_map[test["role_id"]]["authorization"]
                          == "authorized-synthetic"}

        triplet_by_seed, triplet_test_ids, cache_ids = {}, set(), []
        for triplet in triplets:
            need(isinstance(triplet, dict) and isinstance(triplet.get("id"), str)
                 and isinstance(triplet.get("cache_id"), str)
                 and triplet["cache_id"].strip(),
                 "Malformed TS06 cache triplet")
            route_id = triplet.get("route_id")
            cold = test_map.get(triplet.get("cold_test_id"))
            seed = test_map.get(triplet.get("seed_test_id"))
            replay = test_map.get(triplet.get("replay_test_id"))
            need(route_id in route_map and cold and seed and replay
                 and cold["route_id"] == seed["route_id"] == replay["route_id"] == route_id
                 and cold["role_id"] == replay["role_id"] == "anonymous"
                 and role_map[seed["role_id"]]["authorization"]
                 == "authorized-synthetic",
                 "TS06 triplet must bind anonymous cold/replay around an authorized synthetic seed")
            ids = {cold["id"], seed["id"], replay["id"]}
            need(len(ids) == 3 and not (ids & triplet_test_ids),
                 "Ambiguous or repeated TS06 cache triplet tests")
            triplet_test_ids.update(ids)
            triplet_by_seed[seed["id"]] = triplet
            cache_ids.append(triplet["cache_id"])
        _unique([triplet["id"] for triplet in triplets], "cache triplet id")
        _unique(cache_ids, "cache label")
        need(set(triplet_by_seed) == authorized_ids,
             "Each authorized synthetic seed must have exactly one cache triplet")
        need({test_id for triplet in triplets for test_id in (
            triplet["cold_test_id"], triplet["replay_test_id"])}
             <= {test["id"] for test in tests
                 if test["role_id"] == "anonymous"},
             "Triplets require planned anonymous cold and replay cells")
        need({triplet["route_id"] for triplet in triplets} == set(route_map),
             "Every route needs a cold/seed/replay triplet")

        http = target.get("http")
        need(isinstance(http, dict) and http.get("reader") == READER
             and http.get("complete") is True,
             "Missing or incomplete TS06 supplied HTTP matrix")
        http_observed = tsep.timestamp(http.get("observed_at"))
        plan_observed = tsep.timestamp(plan["declared_at"])
        assessment_observed = tsep.timestamp(observed_at)
        need(plan_observed <= http_observed <= assessment_observed,
             "TS06 HTTP observations must follow the prior plan and not postdate assessment")
        records = http.get("cases")
        need(type(records) is list and records,
             "Missing TS06 HTTP cases")

        # Preserve any attributable contradiction before rejecting gaps/duplicates.
        for record in records:
            if not isinstance(record, dict):
                continue
            test = test_map.get(record.get("test_id"))
            route_id = test["route_id"] if test else record.get("route_id")
            role_id = test["role_id"] if test else record.get("role_id")
            route, role = route_map.get(route_id), role_map.get(role_id)
            if route and role and role["authorization"] == "unauthorized-synthetic":
                for hop in record.get("hops", []) if isinstance(record.get("hops"), list) else []:
                    if isinstance(hop, dict) and _raw_response_leaks(hop, route["canaries"]):
                        return "fail", (
                            "An attributable supplied unauthorized response contains "
                            "a declared synthetic canary")

        need(len(records) == len(test_map),
             "TS06 HTTP matrix is missing or duplicates planned tests")
        record_map, order, times = {}, {}, {}
        triplet_phase = {}
        for triplet in triplets:
            triplet_phase[triplet["cold_test_id"]] = (triplet, "cold")
            triplet_phase[triplet["seed_test_id"]] = (triplet, "seed")
            triplet_phase[triplet["replay_test_id"]] = (triplet, "replay")
        for index, record in enumerate(records):
            need(isinstance(record, dict)
                 and record.get("test_id") in test_map
                 and record["test_id"] not in record_map,
                 "Unknown or duplicate TS06 HTTP test")
            test = test_map[record["test_id"]]
            need(record.get("route_id") == test["route_id"]
                 and record.get("role_id") == test["role_id"],
                 "TS06 HTTP case route/role attribution differs from the prior plan")
            case_time = tsep.timestamp(record.get("observed_at"))
            need(plan_observed <= case_time <= http_observed,
                 "TS06 case time is outside its declared observation interval")
            triplet_phase_entry = triplet_phase.get(test["id"])
            if triplet_phase_entry:
                triplet, phase = triplet_phase_entry
                need(record.get("cache_id") == triplet["cache_id"]
                     and record.get("cache_phase") == phase,
                     "TS06 cache observation label/phase mismatch")
            else:
                need(record.get("cache_id") is None and record.get("cache_phase") is None,
                     "Unexpected TS06 cache attribution")
            record_map[test["id"]] = record
            order[test["id"]] = index
            times[test["id"]] = case_time
        need(set(record_map) == set(test_map),
             "TS06 HTTP matrix has uncovered tests")
        for triplet in triplets:
            cold, seed, replay = (triplet[k] for k in
                                  ("cold_test_id", "seed_test_id", "replay_test_id"))
            need(order[cold] < order[seed] < order[replay]
                 and times[cold] < times[seed] < times[replay],
                 "TS06 cold/seed/replay observations must have strict declared order")

        for test_id, test in test_map.items():
            route, role = route_map[test["route_id"]], role_map[test["role_id"]]
            status, final_status, exposed = _inspect_case(
                record_map[test_id], route, role, test)
            if status == "leak":
                return "fail", (
                    "A supplied unauthorized or cache-replay response contains "
                    "a declared synthetic canary")
            if status == "incomplete":
                return "inconclusive", (
                    "A 206 partial or 304 without the stored full representation "
                    "cannot establish the access result")
            if test_id in authorized_ids:
                if not (200 <= final_status < 300) or set(exposed) != set(route["canaries"]):
                    return "inconclusive", (
                        "Synthetic cache seed did not expose the complete declared canary set")
            elif role["authorization"] == "unauthorized-synthetic":
                if status != "denied":
                    if final_status is not None and 200 <= final_status < 300:
                        return "fail", (
                            "A declared sensitive route delivered a successful representation "
                            "to a synthetic unauthorized role")
                    return "inconclusive", (
                        "Supplied response does not establish the declared denial outcome")
        return "pass", (
            "All declared synthetic route-role cells and cold/seed/replay triplets were "
            "complete and showed denial without canary leakage; this does not establish "
            "a real identity, server protection or shared cache")
    except (Unknown, tsep.Invalid, KeyError, TypeError, ValueError, AttributeError) as error:
        return "inconclusive", str(error)
