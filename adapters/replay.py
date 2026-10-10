#!/usr/bin/env python3
"""Replay any offline capture-adapter bundle, without collection. Apache-2.0."""
import argparse
from pathlib import Path
import sys
import tempfile
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import tsep
from adapters import captures, package, replay_comparison
from adapters.package import inventory, json_bytes, publish, seal
from provenance.runtime import runtime_identity, loaded_sources

VERSION = '3'


def replay(source, output, *, comparison='exact'):
    tsep.require(comparison in replay_comparison.PROFILES, 'Unknown replay comparison profile')
    workflow_sources = loaded_sources(ROOT, {'adapters/replay.py': sys.modules[__name__],
                                            'adapters/package.py': package,
                                            'adapters/replay_comparison.py': replay_comparison})
    source, output = Path(source), Path(output)
    entries = inventory(source)
    needed = {'input.json', 'report.json', 'import.json', 'assessment.json', 'gate.json', 'earl.jsonld'}
    tsep.require(needed <= set(entries), 'Not a complete offline capture bundle')
    original = tsep.read_json(source/'report.json')
    original_gate = tsep.validate(original, source)
    metadata = tsep.read_json(source/'import.json')
    tsep.require(metadata['source_files'] == captures.source_files(),
                 'Tool sources differ: use the historical tool archive, or create a separate reassessment')
    tsep.require(metadata['input_sha256'] == entries['input.json'], 'Original input binding mismatch')
    tsep.require(metadata['protocol'] == original['protocol'], 'Protocol records disagree')
    tsep.require(tsep.read_json(source/'gate.json') == original_gate, 'Recorded gate differs from report')
    tsep.require(tsep.read_json(source/'earl.jsonld') == tsep.earl(original, original_gate), 'Recorded EARL differs')
    tsep.require(not output.exists() and not output.is_symlink() and output.parent.is_dir(),
                 'Choose a NEW output directory with an existing parent')
    with tempfile.TemporaryDirectory(prefix='.tsep-replay-', dir=output.parent) as folder:
        stage = Path(folder)
        summary = captures.build(source/'input.json', stage/'bundle',
            assessor=original['assessor']['name'], label=original['scope']['label'],
            selection_method=original['scope']['selection_method'], access=metadata['access'],
            mode=original['assessor']['mode'], selected=original['controls'],
            exclusions=original['scope']['exclusions'])
        same_results = tsep.read_json(stage/'bundle/assessment.json') == tsep.read_json(source/'assessment.json')
        observed_names = {name for name in entries if name.startswith('observations/source-observation-')}
        replay_names = {str(p.relative_to(stage/'bundle')) for p in (stage/'bundle/observations').glob('source-observation-*.json')}
        current_runtime = tsep.read_json(stage/'bundle/import.json')['runtime']
        tsep.require(current_runtime == runtime_identity(), 'Replay runtime record differs from execution')
        comparisons = {name: replay_comparison.compare(tsep.read_json(source/name),
            tsep.read_json(stage/'bundle'/name), metadata.get('runtime'), current_runtime, comparison)
            for name in sorted(observed_names & replay_names)}
        same_names = observed_names == replay_names
        same_source_observations = same_names and all(v['exact'] for v in comparisons.values())
        source_observations_match = same_names and all(v['match'] for v in comparisons.values())
        # Retain the old bytes, not a normalized substitute. This is a partial
        # evidence copy; the old manifest refers to the complete source bundle.
        for name in sorted(observed_names | {'import.json', 'SHA256SUMS'}):
            destination = stage/'original-evidence'/name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(package.regular(source/name))
        same_gate = summary == original_gate
        # Also catch a coherently rehashed report that disagrees with the raw input.
        current = tsep.read_json(stage/'bundle/report.json')
        same_report_results = current['results'] == original['results']
        result = {'kind': 'tsep-capture-replay', 'workflow_version': VERSION,
                  'workflow_source_files': workflow_sources,
                  'input_sha256': entries['input.json'], 'original_manifest_sha256': tsep.digest(source/'SHA256SUMS'),
                  'same_atomic_results': same_results, 'same_report_results': same_report_results,
                  'same_gate': same_gate, 'same_source_observations': same_source_observations, 'same_tool_sources': True,
                  'comparison_profile': comparison, 'source_observations_match': source_observations_match,
                  'source_observation_comparisons': comparisons,
                  'original_only_observations': sorted(observed_names - replay_names),
                  'current_only_observations': sorted(replay_names - observed_names),
                  'same_recorded_runtime': metadata.get('runtime') == current_runtime,
                  'original_runtime': metadata.get('runtime'), 'current_runtime': current_runtime,
                  'current_unicode_data_version': unicodedata.unidata_version,
                  'original_unicode_data_version': None,
                  'replayed': same_results and same_report_results and same_gate and source_observations_match,
                  'decision': summary['decision'], 'network_requests': 0,
                  'limitations': 'Integrity and deterministic interpretation only; no authentication of intent, reviews, captures or engine behavior.'}
        (stage/'replay.json').write_bytes(json_bytes(result))
        seal(stage)
        inventory(stage)
        tsep.require(inventory(source) == entries, 'Original bundle changed during replay')
        tsep.require(workflow_sources == loaded_sources(ROOT, {'adapters/replay.py': sys.modules[__name__],
                                                             'adapters/package.py': package,
                                                             'adapters/replay_comparison.py': replay_comparison}),
                     'Replay workflow changed during execution')
        publish(stage, output)  # Retain mismatches for inspection instead of erasing them.
    tsep.require(result['replayed'], 'Replay differs; retained output explains the mismatch')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('bundle', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--comparison', choices=replay_comparison.PROFILES, default='exact',
                        help='Exact typed JSON by default; an explicit profile can allow only bound Python supervisor versions')
    args = parser.parse_args()
    try:
        print(json_bytes(replay(args.bundle, args.output, comparison=args.comparison)).decode(), end='')
        return 0
    except (ValueError, OSError, KeyError, TypeError, AttributeError) as error:
        print(str(error), file=sys.stderr)
        return 64


if __name__ == '__main__':
    sys.exit(main())
