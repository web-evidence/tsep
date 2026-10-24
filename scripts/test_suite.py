"""Standard serial unittest discovery with timing and exact inventory. Apache-2.0."""
import argparse
import collections
import hashlib
import json
import os
from pathlib import Path
import sys
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True


def cpu_seconds():
    usage = os.times()
    return usage.user + usage.system + usage.children_user + usage.children_system


def identifiers(suite):
    for test in suite:
        if isinstance(test, unittest.TestSuite):
            yield from identifiers(test)
        else:
            yield test.id()


class TimedResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.timings = []

    def startTest(self, test):
        self.started = time.monotonic()
        self.cpu_started = cpu_seconds()
        super().startTest(test)

    def stopTest(self, test):
        self.timings.append({'id': test.id(),
                             'seconds': round(time.monotonic()-self.started, 6),
                             'cpu_seconds': round(cpu_seconds()-self.cpu_started, 6)})
        super().stopTest(test)


def run_suite(suite):
    expected = list(identifiers(suite))
    start, cpu = time.monotonic(), cpu_seconds()
    result = unittest.TextTestRunner(verbosity=2, resultclass=TimedResult).run(suite)
    completed = [row['id'] for row in result.timings]
    complete = (bool(expected) and len(set(expected)) == len(expected)
                and collections.Counter(expected) == collections.Counter(completed))
    return {'success': result.wasSuccessful() and complete and not result.skipped and not result.expectedFailures,
            'inventory_complete': complete, 'expected': expected, 'completed': completed,
            'tests_run': result.testsRun, 'skipped': result.skipped,
            'errors': len(result.errors), 'failures': len(result.failures),
            'unexpected_successes': len(result.unexpectedSuccesses),
            'expected_failures': len(result.expectedFailures),
            'seconds': round(time.monotonic()-start, 6),
            'cpu_seconds': round(cpu_seconds()-cpu, 6), 'timings': result.timings}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    # Exactly the existing discover -s tests behavior; no test/module sharding.
    suite = unittest.defaultTestLoader.discover(str(ROOT/'tests'))
    expected = json.loads((ROOT/'scripts/qualification-inventory.json').read_text(encoding='utf-8'))
    ids = list(identifiers(suite))
    fingerprint = hashlib.sha256(json.dumps(ids, ensure_ascii=True, separators=(',', ':')).encode()).hexdigest()
    if len(ids) != expected['tests'] or fingerprint != expected['test_ids_sha256']:
        raise ValueError('Discovered tests differ from reviewed qualification manifest')
    report = run_suite(suite)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    return 0 if report['success'] else 1


if __name__ == '__main__':
    sys.exit(main())
