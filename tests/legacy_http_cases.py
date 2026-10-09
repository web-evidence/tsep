# Copyright 2026 Edikka. SPDX-License-Identifier: Apache-2.0
# Adapted from the article regression cases; not a 44-control conformance suite.
"""Exercise the exact published example against local contradictory responses."""
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "probes/http-page.py").read_text()
CASES = {}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        status, headers, body = CASES[self.path]
        self.send_response(status)
        for key, value in headers:
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(body.encode())


server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
threading.Thread(target=server.serve_forever, daemon=True).start()
base = f"http://127.0.0.1:{server.server_port}"
canonical = f'<link rel="canonical" href="{base}/page">'
valid = f"<html><head>{canonical}</head><body>Example</body></html>"
html = [("Content-Type", "text/html; charset=utf-8")]
preview = "index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1"
tests = [
    ("valid", 200, html, valid, 0, "PASS:"),
    ("noindex-single-quotes", 200, html, valid.replace("</head>", "<meta content='noindex' name='robots'></head>"), 1, "noindex/none"),
    ("reversed-unquoted-attrs", 200, html, valid.replace("</head>", "<META content=NOINDEX name=ROBOTS></head>"), 1, "noindex/none"),
    ("googlebot-none", 200, html, valid.replace("</head>", "<meta name=googlebot content=none></head>"), 1, "noindex/none"),
    ("http-noindex", 200, html + [("X-Robots-Tag", "noindex")], valid, 1, "noindex/none"),
    ("http-googlebot", 200, html + [("X-Robots-Tag", "googlebot: noindex")], valid, 1, "noindex/none"),
    ("repeated-http", 200, html + [("X-Robots-Tag", "index"), ("X-Robots-Tag", "none")], valid, 1, "noindex/none"),
    ("other-bot-review", 200, html + [("X-Robots-Tag", "bingbot: noindex")], valid, 2, "REVIEW:"),
    ("timed-review", 200, html + [("X-Robots-Tag", "unavailable_after: 25 Jun 2030 15:00:00 PST")], valid, 2, "REVIEW:"),
    ("http-link-review", 200, html + [("Link", '<https://example.org>; rel="canonical"')], valid, 2, "REVIEW:"),
    ("meta-common-preview", 200, html, valid.replace("</head>", f'<meta name="robots" content="{preview}"></head>'), 0, "PASS:"),
    ("http-common-preview", 200, html + [("X-Robots-Tag", preview)], valid, 0, "PASS:"),
    ("googlebot-preview", 200, html + [("X-Robots-Tag", "GoogleBot: MAX-IMAGE-PREVIEW: NONE, max-snippet:0, max-video-preview:0")], valid, 0, "PASS:"),
    ("meta-preview-none", 200, html, valid.replace("</head>", '<meta name="robots" content="max-image-preview:none"></head>'), 0, "PASS:"),
    ("preview-and-noindex", 200, html + [("X-Robots-Tag", preview + ", noindex")], valid, 1, "noindex/none"),
    ("preview-and-none", 200, html + [("X-Robots-Tag", "max-image-preview:none, none")], valid, 1, "noindex/none"),
    ("googlebot-noindex-preview", 200, html + [("X-Robots-Tag", "googlebot: max-image-preview:none, noindex")], valid, 1, "noindex/none"),
    ("googlebot-other-scope", 200, html + [("X-Robots-Tag", "googlebot: index, otherbot: noindex")], valid, 2, "REVIEW:"),
    ("unknown-preview-rule", 200, html + [("X-Robots-Tag", "max-custom:large")], valid, 2, "REVIEW:"),
    ("malformed-preview-value", 200, html + [("X-Robots-Tag", "max-image-preview:noindex")], valid, 2, "REVIEW:"),
    ("wordpress-api-link", 200, html + [("Link", '<https://example.org/wp-json/>; rel="https://api.w.org/"')], valid, 0, "PASS:"),
    ("preload-link", 200, html + [("Link", '</style.css>; rel=preload; as=style')], valid, 0, "PASS:"),
    ("link-canonical-bare", 200, html + [("Link", '<https://example.org>; rel=canonical')], valid, 2, "REVIEW:"),
    ("link-canonical-multiple-relations", 200, html + [("Link", '<https://example.org>; REL="alternate CANONICAL"')], valid, 2, "REVIEW:"),
    ("link-canonical-combined", 200, html + [("Link", '</app.css>; rel=preload, <https://example.org>; rel="canonical alternate"')], valid, 2, "REVIEW:"),
    ("link-canonical-repeated-header", 200, html + [("Link", '</app.css>; rel=preload'), ("Link", '<https://example.org>; rel=canonical')], valid, 2, "REVIEW:"),
    ("link-unrelated-title", 200, html + [("Link", '<https://example.org/a,b>; title="example; rel=canonical"; rel=alternate')], valid, 0, "PASS:"),
    ("link-unrelated-relation", 200, html + [("Link", '<https://example.org>; rel="not-canonical"')], valid, 0, "PASS:"),
    ("review-does-not-hide-noindex", 200, html + [("Link", '<https://example.org>; rel=canonical'), ("X-Robots-Tag", "otherbot: noindex"), ("X-Robots-Tag", "noindex")], valid, 1, "noindex/none"),
    ("404", 404, html, valid, 1, "HTTP 200"),
    ("500", 500, html, valid, 1, "HTTP 200"),
    ("no-canonical", 200, html, valid.replace(canonical, ""), 1, "exactly one"),
    ("empty-canonical", 200, html, valid.replace(canonical, '<link rel="canonical" href="">'), 1, "exactly one"),
    ("wrong-canonical", 200, html, valid.replace(canonical, '<link rel="canonical" href="https://example.org">'), 1, "differs"),
    ("duplicate-canonical", 200, html, valid.replace(canonical, canonical * 2), 1, "exactly one"),
    ("relative-canonical", 200, html, valid.replace(canonical, "<LINK href='/page' REL='canonical'>"), 0, "PASS:"),
    ("base-mismatch", 200, html, valid.replace(canonical, '<base href="https://example.org"><link rel="canonical" href="/page">'), 1, "differs"),
    ("comment-is-not-directive", 200, html, valid.replace("</head>", '<!-- <meta name="robots" content="noindex"> --></head>'), 0, "PASS:"),
    ("template-is-inert", 200, html, valid.replace("</head>", '<template><meta name="robots" content="noindex"></template></head>'), 0, "PASS:"),
    ("fake-canonical-comment", 200, html, valid.replace(canonical, f"<!-- {canonical} -->"), 1, "exactly one"),
    ("non-html", 200, [("Content-Type", "application/json")], valid, 2, "REVIEW:"),
    ("oversized", 200, html + [("Content-Length", "6000000")], valid, 2, "ERROR:"),
]
results = []


def run(name, url, expected, code, message):
    source = SOURCE.replace('URL = "https://www.example.com/page"', f"URL = {url!r}")
    source = source.replace('EXPECTED_CANONICAL = "https://www.example.com/page"', f"EXPECTED_CANONICAL = {expected!r}")
    result = subprocess.run([sys.executable, "-"], input=source, text=True, capture_output=True, timeout=15)
    passed = result.returncode == code and message in result.stdout and "Traceback" not in result.stderr
    results.append({"case": name, "passed": passed, "exit": result.returncode, "stdout": result.stdout.strip(), "stderr": result.stderr.strip()})


try:
    for name, status, headers, body, code, message in tests:
        CASES["/page"] = status, headers, body
        run(name, base + "/page", base + "/page", code, message)
    CASES["/page"] = 200, html, valid
    CASES["/redirect"] = 301, [("Location", base + "/page"), ("X-Robots-Tag", "noindex")], ""
    run("intermediate-noindex", base + "/redirect", base + "/page", 0, "PASS:")
    CASES["/page"] = 200, html + [("X-Robots-Tag", "noindex")], valid
    run("final-noindex-after-redirect", base + "/redirect", base + "/page", 1, "noindex/none")
    CASES["/loop"] = 302, [("Location", base + "/loop")], ""
    run("redirect-limit", base + "/loop", base + "/page", 2, "ERROR:")
    CASES["/page"] = 200, html, valid
    run("unexpected-final-url", base + "/page", base + "/other", 1, "final URL differs")
    run("invalid-scheme", "file:///etc/hosts", base + "/page", 2, "ERROR:")
finally:
    server.shutdown()
    server.server_close()
run("connection-refused", base + "/page", base + "/page", 2, "ERROR:")
report = {"scope": "Controlled local cases, no market sample or indexing claim", "total": len(results), "passed": sum(row["passed"] for row in results), "cases": results}
if os.environ.get("TSEP_HTTP_REPORT"):
    Path(os.environ["TSEP_HTTP_REPORT"]).write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({"total": report["total"], "passed": report["passed"], "failed": [r for r in results if not r["passed"]]}, indent=2))
sys.exit(0 if report["passed"] == report["total"] else 1)
