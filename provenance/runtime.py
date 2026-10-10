"""Check loaded local module origins before recording source fingerprints. Apache-2.0.

This detects accidental mixed checkouts/imports, not a hostile Python process or
an authenticated execution. Absolute machine paths never enter the report.
"""
import hashlib
from pathlib import Path


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
