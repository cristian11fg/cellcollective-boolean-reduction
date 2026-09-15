"""Semantic gate classification, graph metrics, and representation costs."""
from collections import Counter


def classify(f):
    k, v = len(f.support), f.values
    if k == 0:
        return 'CONST_' + str(v[0])
    if k == 1:
        return 'COPY' if v == (0, 1) else 'NOT'
    if sum(v) == 1:
        return 'AND' if v[-1] else 'NOR' if v[0] else 'SIGNED_AND'
    if sum(v) == len(v) - 1:
        return 'OR' if not v[0] else 'NAND' if not v[-1] else 'SIGNED_OR'
    parity = tuple(i.bit_count() % 2 for i in range(len(v)))
    if v == parity:
        return 'XOR'
    if v == tuple(1 - x for x in parity):
        return 'XNOR'
    return 'GENERAL'


def components(adjacency):
    # Iterative reachability avoids recursive depth limits in this reference engine.
    reach = {}
    for node in adjacency:
        visited, pending = set(), [node]
        while pending:
            v = pending.pop()
            if v not in visited:
                visited.add(v)
                pending.extend(adjacency[v] - visited)
        reach[node] = visited
    remaining, groups = set(adjacency), []
    while remaining:
        node = min(remaining)
        group = {v for v in remaining if v in reach[node] and node in reach[v]}
        groups.append(group)
        remaining -= group
    return groups


def metrics(network):
    functions = network.functions
    edges = {(source, target) for target, f in functions.items() for source in f.support}
    directed = {n: set() for n in functions}
    weak = {n: set() for n in functions}
    for u, v in edges:
        directed[u].add(v)
        weak[u].add(v)
        weak[v].add(u)
    classes = Counter(classify(f) for n, f in functions.items() if n not in network.inputs)
    kinds = set(classes)
    if not kinds:
        family = 'NO_INTERNAL_NODES'
    elif kinds == {'COPY'}:
        family = 'COPY_ONLY'
    elif kinds <= {'AND', 'COPY'}:
        family = 'HOMOGENEOUS_AND'
    elif kinds <= {'OR', 'COPY'}:
        family = 'HOMOGENEOUS_OR'
    elif kinds <= {'AND', 'OR', 'COPY'}:
        family = 'AND_OR'
    else:
        family = 'MIXED_OR_OTHER'
    return {'nodes': len(functions), 'internal_nodes': len(functions) - len(network.inputs), 'inputs': len(network.inputs),
            'edges': len(edges), 'edges_without_input_identity': len(edges) - len(network.inputs), 'self_loops': sum(u == v for u, v in edges),
            'scc': len(components(directed)), 'weak_components': len(components(weak)),
            'max_indegree': max((len(f.support) for f in functions.values()), default=0),
            'table_entries': sum(len(f.values) for f in functions.values()),
            'canonical_dnf_literals': sum(len(f.support) * sum(f.values) for f in functions.values()),
            'function_classes': dict(sorted(classes.items())), 'network_class': family}
