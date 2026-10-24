"""Bounded TS05 policy-map checker; never observes an actual search index."""
import tsep
from conformance.http import Unknown, need


CRAWL_METHODS = {"robots-txt", "other", "none", "unknown"}
CRAWL_EFFECTS = {"allow", "disallow", "unknown", "not-applicable"}
INDEX_METHODS = {"meta-noindex", "x-robots-tag-noindex", "removal-request",
                 "other", "none", "unknown", "not-applicable"}
INDEX_GOALS = {"exclude", "include", "not-assessed"}
VISIBILITY = {"fetchable", "blocked-by-robots", "unknown", "not-applicable"}
PROTECTION_METHODS = {"authentication", "authorization", "other", "public",
                      "robots-only", "none", "unknown", "not-applicable"}
PROTECTION_GOALS = {"private", "public", "not-assessed"}
CLAIM_KINDS = {"deindex", "confidentiality"}
SERVER_SIDE_BASIS = {"authentication", "authorization"}
CRAWL_ONLY_BASIS = {"robots-disallow", "noindex-directive", "removal-request"}


def _choice(value, allowed, label):
    need(isinstance(value, str) and value in allowed, "Unsupported TS05 " + label)
    return value


def _not_applicable(policy, observed_at):
    review = policy.get("non_applicability_review")
    need(isinstance(review, dict), "Missing positive TS05 non-applicability review")
    need(review.get("complete") is True and review.get("outcome") == "not-applicable",
         "Incomplete TS05 non-applicability review")
    need(isinstance(review.get("rationale"), str) and review["rationale"].strip(),
         "Missing TS05 non-applicability rationale")
    need(tsep.timestamp(review.get("reviewed_at")) <= tsep.timestamp(observed_at),
         "TS05 non-applicability review postdates observation")
    return ("not-applicable",
            "Dated supplied inventory review records no relevant policy in the declared scope; "
            "no site or index state is inferred")


def assess(target, rule):
    """Compare a supplied plan/configuration map, not live behavior or index state."""
    try:
        need(rule == "TS05-A01", "Unsupported TS05 rule")
        need(isinstance(target.get("intent"), dict), "Missing TS05 intent")
        policy = target["intent"].get("ts05_policy")
        need(isinstance(policy, dict), "Missing prior TS05 policy map")
        observed_at = target.get("observed_at")
        applicability = policy.get("applicability")
        if applicability == "not-applicable":
            return _not_applicable(policy, observed_at)
        need(applicability == "applicable", "TS05 applicability is not explicitly declared")

        need(tsep.timestamp(policy.get("declared_at")) <= tsep.timestamp(observed_at),
             "TS05 policy map is missing or postdates observation")
        need(isinstance(policy.get("scope"), str) and policy["scope"].strip(),
             "Missing TS05 policy scope")
        config = target.get("configuration")
        need(isinstance(config, dict), "Missing structured TS05 configuration")
        crawl = policy.get("crawl")
        indexing = policy.get("indexing")
        protection = policy.get("protection")
        need(all(isinstance(axis, dict) for axis in (crawl, indexing, protection)),
             "TS05 requires separate crawl, indexing and protection decisions")

        crawl_method = _choice(crawl.get("method"), CRAWL_METHODS, "crawl method")
        crawl_effect = _choice(crawl.get("effect"), CRAWL_EFFECTS, "crawl effect")
        index_goal = _choice(indexing.get("goal"), INDEX_GOALS, "indexing goal")
        index_method = _choice(indexing.get("method"), INDEX_METHODS, "indexing method")
        visibility = _choice(indexing.get("directive_visibility"), VISIBILITY,
                              "directive visibility")
        protection_goal = _choice(protection.get("goal"), PROTECTION_GOALS,
                                  "protection goal")
        protection_method = _choice(protection.get("method"), PROTECTION_METHODS,
                                    "protection method")

        configured = (config.get("crawl_method"), config.get("crawl_effect"),
                      config.get("indexing_method"), config.get("protection_method"))
        declared = (crawl_method, crawl_effect, index_method, protection_method)
        if any(actual is not None and actual != expected
               for actual, expected in zip(configured, declared)):
            return "fail", "Declared policy decision contradicts the supplied configuration artifact"
        need(all(value is not None for value in configured),
             "Incomplete structured TS05 configuration")

        if policy.get("actual_index_state") != "not-observed":
            return ("inconclusive",
                    "Actual index state is outside this policy-only assessment")

        claims = policy.get("claims")
        need(isinstance(claims, list), "Missing TS05 claim inventory")
        seen = set()
        parsed = []
        for claim in claims:
            need(isinstance(claim, dict), "Malformed TS05 claim")
            kind, level = claim.get("kind"), claim.get("level")
            need(kind in CLAIM_KINDS and level in ("statement", "guarantee", "not-claimed"),
                 "Unsupported TS05 claim type")
            need(kind not in seen, "Duplicate TS05 claim axis")
            seen.add(kind)
            basis = claim.get("basis")
            need(isinstance(basis, list) and basis and
                 all(value in SERVER_SIDE_BASIS | CRAWL_ONLY_BASIS | {"other", "unknown"}
                     for value in basis), "Missing or unsupported TS05 claim basis")
            parsed.append((kind, level, basis))
        need(seen == CLAIM_KINDS,
             "TS05 must record both deindex and confidentiality claim axes")

        for kind, level, basis in parsed:
            if kind == "deindex" and level == "guarantee":
                if basis == ["robots-disallow"]:
                    return ("fail",
                            "Deindexing guarantee relies solely on robots Disallow; "
                            "robots controls crawling, not index removal")
                if "robots-disallow" in basis and visibility == "blocked-by-robots":
                    return ("fail",
                            "The supplied index directive is inaccessible under the "
                            "declared robots policy; the guarantee is unsupported")
                return ("inconclusive",
                        "A configuration snapshot cannot guarantee actual index removal")
            if kind == "confidentiality" and level == "guarantee":
                if protection_method == "robots-only":
                    return ("fail",
                            "robots Disallow is not server-side confidentiality or access control")
                if not any(value in SERVER_SIDE_BASIS for value in basis):
                    if all(value in CRAWL_ONLY_BASIS for value in basis):
                        return ("fail",
                                "Confidentiality guarantee relies only on crawl/index directives, "
                                "not server-side access control")
                    return ("inconclusive",
                            "Confidentiality guarantee has no declared, supported server-side basis")

        if crawl_method in ("unknown", "other") or crawl_effect == "unknown":
            return "inconclusive", "Crawl behavior is unknown or unsupported"
        if crawl_method == "none" and crawl_effect == "disallow":
            return "fail", "A disallow effect has no declared crawl-control mechanism"
        if index_method in ("unknown", "other"):
            return "inconclusive", "Indexing method is unknown or unsupported"
        if protection_method in ("unknown", "other"):
            return "inconclusive", "Protection method is unknown or unsupported"
        if index_goal == "include" and index_method in ("meta-noindex", "x-robots-tag-noindex"):
            if visibility == "fetchable":
                return "fail", "A fetchable noindex directive contradicts the declared inclusion goal"
            return "inconclusive", "Noindex visibility is not established for the declared inclusion goal"
        if index_goal == "include" and index_method == "removal-request":
            return "inconclusive", "Removal-request completion and index effect are not observed"
        if index_goal == "exclude":
            if index_method in ("none", "unknown", "not-applicable"):
                return "inconclusive", "Exclusion is intended but no usable indexing mechanism is declared"
            if index_method in ("meta-noindex", "x-robots-tag-noindex") and visibility != "fetchable":
                return ("inconclusive",
                        "The noindex directive is not established as available to a crawler; "
                        "no index state is inferred")
            if index_method == "removal-request":
                return ("inconclusive",
                        "A removal request is declared, but completion and index effect are not observed")
        if protection_goal == "private":
            if protection_method in ("robots-only", "none", "public"):
                return "fail", "Private content lacks a declared server-side access control"
            if protection_method in ("unknown", "not-applicable"):
                return "inconclusive", "The declared protection mechanism is unknown"
        if index_goal == "not-assessed" or protection_goal == "not-assessed":
            return "inconclusive", "An indexing or protection objective is not assessed"
        return ("pass",
                "Declared crawl, indexing and protection mechanisms are distinct; "
                "actual index state, crawler access and confidentiality are not established")
    except (Unknown, tsep.Invalid, KeyError, TypeError, ValueError) as error:
        return "inconclusive", str(error)
