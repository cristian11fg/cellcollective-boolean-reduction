"""Semantic signs and MIN/MAX families, distinct from legacy gate labels."""
from .boolean import states


def local_structure(function):
    signs = {}
    witnesses = {}
    for source in function.support:
        other = tuple(n for n in function.support if n != source)
        changes = {}
        for state in states(other):
            low = function({**state, source: 0})
            high = function({**state, source: 1})
            if low != high:
                changes.setdefault('+' if high > low else '-', state)
        signs[source] = 'mixed' if len(changes) == 2 else next(iter(changes))
        witnesses[source] = changes
    k = len(function.support)
    return {'signs': signs, 'witnesses': witnesses,
            'unate': all(s != 'mixed' for s in signs.values()),
            'constant': not k,
            'MIN': bool(k) and sum(function.values) == 1,
            'MAX': bool(k) and sum(function.values) == len(function.values) - 1}


def network_structure(network, include_input_identities=False):
    """Default: biological rules only; external regulators still participate."""
    local = {n: local_structure(f) for n, f in network.functions.items()
             if include_input_identities or n not in network.inputs}
    outgoing = {n: {} for n in network.functions}
    edges = set()
    for target, properties in local.items():
        for source, sign in properties['signs'].items():
            outgoing[source][target] = sign
            edges.add((source, target))
    conflicts = {n: targets for n, targets in outgoing.items()
                 if 'mixed' in targets.values() or len(set(targets.values())) > 1}
    active = [p for p in local.values() if not p['constant']]
    uniform = not conflicts
    return {'scope': 'all_rules' if include_input_identities else 'biological_rules',
            'out_uniform': uniform,
            'locally_unate': all(p['unate'] for p in local.values()),
            'conflicts': conflicts,
            'unconstrained_sources': sorted(n for n, t in outgoing.items() if not t),
            'source_signs': {n: next(iter(set(t.values()))) for n, t in outgoing.items() if t and n not in conflicts},
            'nonconstant_rules': len(active),
            'MIN_with_constants': all(p['MIN'] for p in active),
            'MAX_with_constants': all(p['MAX'] for p in active),
            'MIN_MAX_with_constants': all(p['MIN'] or p['MAX'] for p in active),
            'homogeneous_MIN_with_constants': uniform and all(p['MIN'] for p in active),
            'homogeneous_MAX_with_constants': uniform and all(p['MAX'] for p in active),
            'reciprocal_support': all((v, u) in edges for u, v in edges),
            'all_rule_nodes_self_regulated': all(n in network.functions[n].support for n in local),
            'local': local}
