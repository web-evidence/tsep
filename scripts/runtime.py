"""Qualification preflight. Resolve one Node24 executable, never guess a fallback."""
import hashlib
import re
import shutil
import subprocess
from pathlib import Path


def node24(environment):
    requested=environment.get('TSEP_SOURCE_NODE')
    path=shutil.which(requested if requested is not None else 'node',path=environment.get('PATH'))
    if not path:raise ValueError('Node24 unavailable: set TSEP_SOURCE_NODE or install node on PATH')
    result=subprocess.run([path,'--version'],capture_output=True,text=True,timeout=10,env=environment)
    if result.returncode or not re.fullmatch(r'v24\.[0-9]+\.[0-9]+\n?',result.stdout):
        raise ValueError('Node24 required; selected executable reports '+result.stdout.strip())
    return {'path':str(Path(path).resolve()),'version':result.stdout.strip(),
            'sha256':hashlib.sha256(Path(path).read_bytes()).hexdigest()}


def source_runtime_available(environment):
    try:node24(environment);return True
    except (ValueError,OSError,subprocess.SubprocessError):return False
