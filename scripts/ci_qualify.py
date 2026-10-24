#!/usr/bin/env python3
"""Bind the complete verification receipt to its actual CI checkout. Apache-2.0."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True
from scripts.postmerge_check import read_json, require


def checkout_identity():
    sha = subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True, timeout=10).strip()
    raw = subprocess.check_output(['git','cat-file','-p',sha], cwd=ROOT, text=True, timeout=10)
    headers = raw.split('\n\n', 1)[0].splitlines()
    tree = [line[5:] for line in headers if line.startswith('tree ')]
    require(len(tree) == 1, 'Git tree missing')
    return {'checkout':sha, 'tree':tree[0],
            'parents':[line[7:] for line in headers if line.startswith('parent ')],
            'workflow_sha256':hashlib.sha256((ROOT/'.github/workflows/verify.yml').read_bytes()).hexdigest(),
            'event':os.environ.get('GITHUB_EVENT_NAME', '')}


def main():
    before = checkout_identity()
    # stderr remains live; exactly one JSON receipt is emitted on stdout.
    result = subprocess.run([sys.executable, '-I','-B','-X','utf8','scripts/verify.py','--jobs','2'],
                            cwd=ROOT, stdout=subprocess.PIPE, text=True, encoding='utf-8')
    receipt = read_json(result.stdout)
    require(checkout_identity() == before, 'Checkout changed during qualification')
    receipt['ci_identity'] = before
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return result.returncode if result.returncode else (0 if receipt.get('success') is True else 1)


if __name__ == '__main__':
    sys.exit(main())
