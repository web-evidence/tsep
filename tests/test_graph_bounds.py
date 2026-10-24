"""Prior-authored boundaries plus independent all-realizations simple-path oracle."""
import copy
import hashlib
import itertools
import json
from pathlib import Path
import unittest
from conformance.graph_bounds import read

P = Path(__file__).resolve().parent/'fixtures'
HASH = 'e60beb99c3f61a0182b6f14d7aa666ae735d920df110d0c5ee9f5a309ae4f679'


def cases():
    raw = (P/'ts18-graph-component-cases-r1.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == HASH
    return json.loads(raw)['cases']


def simple_path_depth(nodes, roots, edges, destination):
    # Independent exhaustive simple-path oracle, not the production BFS.
    for length in range(len(nodes)):
        for route in itertools.permutations(nodes, length+1):
            if route[0] in roots and route[-1] == destination and all(pair in edges for pair in zip(route, route[1:])):
                return length
    return None


class BoundedGraph(unittest.TestCase):
    def test_twenty_prefrozen_cases(self):
        for case in cases():
            with self.subTest(case=case['id']):
                original = copy.deepcopy(case['graph'])
                if 'error' in case['expected']:
                    with self.assertRaisesRegex(ValueError, case['expected']['error']): read(case['graph'])
                else:
                    result = read(case['graph'])
                    row = next(r for r in result['nodes'] if r['node'] == case['node'])
                    for key, value in case['expected'].items():
                        self.assertEqual(result[key] if key == 'outside_edges' else row[key], value)
                    self.assertFalse(result['authenticates_pair_states'])
                self.assertEqual(case['graph'], original)

    def test_independent_all_realizations_oracle(self):
        # Three nodes, all3**6 non-self pair assignments and every realizable
        # subset of unknown edges. No network and no HTML/DOM interpretation.
        nodes = ['A', 'B', 'C']; pairs = list(itertools.permutations(nodes, 2))
        for states in itertools.product(('present', 'absent', 'unknown'), repeat=len(pairs)):
            graph = {'nodes': nodes, 'roots': ['A'], 'pairs': {n: {} for n in nodes}}
            known, unknown = set(), []
            for pair, state in zip(pairs, states):
                graph['pairs'][pair[0]][pair[1]] = state
                if state == 'present': known.add(pair)
                if state == 'unknown': unknown.append(pair)
            realizations = [known | {p for p, on in zip(unknown, flags) if on}
                            for flags in itertools.product((False, True), repeat=len(unknown))]
            result = read(graph)
            for row in result['nodes']:
                depths = [simple_path_depth(nodes, ['A'], edges, row['node']) for edges in realizations]
                finite = [d for d in depths if d is not None]
                lower = min(finite) if finite else None
                upper = max(depths) if len(finite) == len(depths) else None
                incoming = [sum((a, row['node']) in e for a in nodes if a != row['node']) for e in realizations]
                self.assertEqual((row['lower'],row['upper']), (lower,upper), (states,row))
                self.assertEqual((row['incoming_lower'],row['incoming_upper']), (min(incoming),max(incoming)))


if __name__ == '__main__': unittest.main()
