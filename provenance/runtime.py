"""Check loaded local module origins before recording source fingerprints. Apache-2.0.

This detects accidental mixed checkouts/imports, not a hostile Python process or
an authenticated execution. Absolute machine paths never enter the report.
"""
import hashlib
import importlib
from pathlib import Path
import platform
import sys


def runtime_identity():
    """Selected runtime dependencies, not an exhaustive execution attestation."""
    files = {}
    for name in ('html', 'html.entities', 'html.parser'):
        module = importlib.import_module(name)
        path = getattr(module, '__file__', None)
        files[name] = hashlib.sha256(Path(path).read_bytes()).hexdigest() if path and Path(path).is_file() else None
    return {'implementation': platform.python_implementation(), 'python': platform.python_version(),
            'build': sys.version, 'stdlib_source_sha256': files,
            'scope': 'Selected HTML runtime dependencies; null means source unavailable. Not complete environment authentication.'}


def loaded_sources(root, modules):
    root = Path(root).resolve()
    result = {}
    for relative, module in modules.items():
        expected = root/relative
        if not expected.is_file() or expected.resolve() != expected:
            raise ValueError('Source must be a local regular file: '+relative)
        locations = [getattr(module, '__file__', None)]
        spec = getattr(module, '__spec__', None)
        if spec is not None:
            locations.append(spec.origin)
        if any(not isinstance(value, str) or Path(value).resolve() != expected for value in locations):
            raise ValueError('Loaded module origin differs from source inventory: '+relative)
        result[relative] = hashlib.sha256(expected.read_bytes()).hexdigest()
    return result
