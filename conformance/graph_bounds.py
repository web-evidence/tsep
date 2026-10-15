"""Bounded graph measurements; not an acquisition or standalone TS18 verdict.

Pair states must be established by a separate evidence reader. Missing states
remain unknown. Distances only concern the explicitly supplied population.
"""
from collections import deque

STATES = {'present', 'absent', 'unknown', 'excluded'}


def need(ok):
    if not ok:
        raise ValueError('Unqualified graph input')


def distances(nodes, root, edges):
    found = {root: 0}
    pending = deque([root])
    while pending:
        node = pending.popleft()
        for following in sorted(edges[node]):
            if following not in found:
                found[following] = found[node] + 1
                pending.append(following)
    return found


def read(graph):
    need(type(graph) is dict)
    nodes, roots, pairs = graph.get('nodes'), graph.get('roots'), graph.get('pairs')
    need(type(nodes) is list and 1 <= len(nodes) <= 16)
    need(all(type(n) is str and 0 < len(n) <= 4096 for n in nodes))
    need(len(set(nodes)) == len(nodes))
    need(type(roots) is list and 1 <= len(roots) <= 4)
    need(all(type(r) is str and r in nodes for r in roots) and len(set(roots)) == len(roots))
    need(type(pairs) is dict)
    known, possible = {n: set() for n in nodes}, {n: set() for n in nodes}
    outside = []
    for a, row in pairs.items():
        need(type(a) is str and 0 < len(a) <= 4096 and type(row) is dict and len(row) <= 256)
        for b, state in row.items():
            need(type(b) is str and 0 < len(b) <= 4096 and type(state) is str and state in STATES)
            if a not in nodes or b not in nodes:
                outside.append([a, b])
    need(len(pairs) <= 256 and len(outside) <= 256)
    for a in nodes:
        row = pairs.get(a, {})
        for b in nodes:
            if a == b:
                continue
            state = row.get(b, 'unknown')
            if state == 'present':
                known[a].add(b)
                possible[a].add(b)
            elif state == 'unknown':
                possible[a].add(b)
    known_by_root = {r: distances(nodes, r, known) for r in roots}
    possible_by_root = {r: distances(nodes, r, possible) for r in roots}
    values = []
    for n in nodes:
        proven = {r: ds[n] for r, ds in known_by_root.items() if n in ds}
        optimistic = {r: ds[n] for r, ds in possible_by_root.items() if n in ds}
        upper = min(proven.values()) if proven else None
        lower = min(optimistic.values()) if optimistic else None
        status = ('unreachable' if lower is None else 'no_proven_route' if upper is None
                  else 'exact' if lower == upper else 'interval')
        incoming_lower = sum(n in known[a] for a in nodes if a != n)
        incoming_upper = sum(n in possible[a] for a in nodes if a != n)
        values.append({'node': n, 'lower': lower, 'upper': upper, 'depth_state': status,
            'proven_shortest_roots': sorted(r for r, d in proven.items() if d == upper),
            'possible_shortest_roots': sorted(r for r, d in optimistic.items() if d == lower),
            'incoming_lower': incoming_lower, 'incoming_upper': incoming_upper,
            'root': n in roots, 'bounded_orphan_candidate': n not in roots and incoming_upper == 0})
    return {'scope': 'Declared graph population only; no site-wide reachability or orphan claim.',
            'authenticates_pair_states': False, 'nodes': values, 'outside_edges': sorted(outside)}
