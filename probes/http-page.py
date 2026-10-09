# Copyright 2026 Edikka. SPDX-License-Identifier: Apache-2.0
# Adapted from Edikka technical-seo-minimal-check.py, 2026-10-09.
# Partial probe only: never maps a PASS to a whole TSEP control.
"""Bounded example for one expected canonical HTML page; Python 3 + curl.

This is not an indexability audit. Exit 0: these checks pass; 1: mismatch;
2: execution failed or manual review required. No crawl or JS rendering.
"""
import argparse
import re
import subprocess
import tempfile
from email.parser import Parser
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit

URL = "https://www.example.com/page"
EXPECTED_CANONICAL = "https://www.example.com/page"


def stop(message, code=1):
    print(message)
    raise SystemExit(code)


class Head(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_head = False
        self.in_template = 0
        self.canonicals, self.robots, self.bases = [], [], []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "head":
            self.in_head = True
        if tag == "template":
            self.in_template += 1
        if not self.in_head or self.in_template:
            return
        if tag == "link" and "canonical" in (attrs.get("rel") or "").lower().split():
            self.canonicals.append(attrs.get("href") or "")
        if tag == "base" and "href" in attrs:
            self.bases.append(attrs["href"] or "")
        if tag == "meta" and (attrs.get("name") or "").lower() in ("robots", "googlebot"):
            self.robots.append(attrs.get("content") or "")

    def handle_endtag(self, tag):
        if tag == "head":
            self.in_head = False
        if tag == "template":
            self.in_template = max(0, self.in_template - 1)


def main():
    global URL, EXPECTED_CANONICAL
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=URL)
    parser.add_argument("--canonical", default=EXPECTED_CANONICAL)
    args = parser.parse_args()
    URL, EXPECTED_CANONICAL = args.url, args.canonical
    for value in (URL, EXPECTED_CANONICAL):
        parsed = urlsplit(value)
        if parsed.scheme not in ("http", "https") or not parsed.netloc or parsed.fragment:
            stop("ERROR: configure absolute HTTP(S) URLs without fragments", 2)
    with tempfile.TemporaryDirectory() as folder:
        headers, body = Path(folder) / "headers", Path(folder) / "body"
        try:
            result = subprocess.run([
                "curl", "--location", "--silent", "--show-error",
                "--proto", "=http,https", "--proto-redir", "=http,https",
                "--connect-timeout", "3", "--max-time", "10", "--max-redirs", "5",
                "--max-filesize", "5242880", "--dump-header", str(headers),
                "--output", str(body), "--write-out", "%{http_code}\n%{url_effective}", URL,
            ], capture_output=True, text=True, timeout=12)
        except (OSError, subprocess.TimeoutExpired) as error:
            stop(f"ERROR: request not completed ({type(error).__name__})", 2)
        if result.returncode:
            stop(f"ERROR: curl exit {result.returncode}; no compliance conclusion", 2)
        status, final_url = result.stdout.strip().split("\n", 1)
        print(f"HTTP {status} | final URL: {final_url}")
        if status != "200":
            stop("FAIL: expected final HTTP 200")
        if final_url != EXPECTED_CANONICAL:
            stop("FAIL: final URL differs from the configured canonical URL")
        # Keep redirect/proxy headers separate; inspect only the final response.
        blocks = re.split(r"\r?\n\r?\n", headers.read_text(encoding="iso-8859-1"))
        responses = [block for block in blocks if block.startswith("HTTP/")]
        if not responses:
            stop("ERROR: final response headers unavailable", 2)
        final_headers = Parser().parsestr(responses[-1].split("\n", 1)[1])
        if final_headers.get_content_type() != "text/html":
            stop("REVIEW: this example requires text/html", 2)
        head = Head()
        head.feed(body.read_bytes().decode(final_headers.get_content_charset() or "utf-8"))
        if len(head.canonicals) != 1 or not head.canonicals[0].strip():
            stop("FAIL: expected exactly one non-empty HTML canonical in head")
        base = urljoin(final_url, head.bases[0]) if head.bases else final_url
        if urljoin(base, head.canonicals[0].strip()) != EXPECTED_CANONICAL:
            stop("FAIL: HTML canonical differs from the configured URL")
        reviews = set()
        # Consume URLs and quoted parameters before inspecting exact rel tokens.
        link_parameters = r'<[^>]*>|;\s*([^\s=;,]+)\s*=\s*(?:"((?:\\.|[^"\\])*)"|([^;,\s]+))'
        for header in final_headers.get_all("Link", []):
            for name, quoted, bare in re.findall(link_parameters, header):
                relations = re.sub(r"\\(.)", r"\1", quoted or bare).lower().split()
                if name.lower() == "rel" and "canonical" in relations:
                    reviews.add("compare HTTP rel=canonical with the HTML canonical")
        directives = head.robots + final_headers.get_all("X-Robots-Tag", [])
        for directive in directives:
            rules = re.sub(r"^\s*googlebot\s*:\s*", "", directive, flags=re.I)
            for rule in rules.lower().split(","):
                name, colon, value = rule.strip().partition(":")
                name, value = name.strip(), value.strip()
                if colon:
                    if name in ("max-snippet", "max-video-preview", "max-image-preview"):
                        valid = value in ("none", "standard", "large") if name == "max-image-preview" else bool(re.fullmatch(r"-1|\d+", value))
                        if not valid:
                            reviews.add("unrecognised preview value")
                        continue  # max-image-preview:none is not the none directive.
                    reviews.add("scoped, timed or unsupported robots directive")
                    break  # Do not treat the rest of an unknown bot scope as global.
                if re.search(r"(?:^|\s)(?:noindex|none)(?:$|\s)", name):
                    stop("FAIL: noindex/none in final HTTP headers or HTML head")
        if reviews:
            stop("REVIEW: " + "; ".join(sorted(reviews)), 2)
        print("PASS: final 200, configured HTML canonical, no checked noindex/none")
        print("NOT TESTED: robots.txt, rendered DOM, indexing, other SEO controls")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, LookupError, OSError) as error:
        stop(f"ERROR: response could not be interpreted ({type(error).__name__})", 2)
