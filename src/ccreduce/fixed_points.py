"""Exhaustive independent oracle for small networks."""
from .boolean import states


def fixed_points(network, max_nodes=20):
    if len(network.functions) > max_nodes:
        raise ValueError('Exhaustive fixed-point limit exceeded')
    return [s for s in states(tuple(sorted(network.functions))) if network.is_fixed(s)]


def validate_bijection(original, reduction, max_nodes=20):
    before = fixed_points(original, max_nodes)
    after = fixed_points(reduction.network, max_nodes)
    lifted = [reduction.lift(s) for s in after]
    canonical = lambda s: tuple(sorted(s.items()))
    valid = {canonical(s) for s in before} == {canonical(s) for s in lifted}
    valid = valid and len(lifted) == len({canonical(s) for s in lifted})
    valid = valid and all({n: s[n] for n in reduction.network.functions} in after for s in before)
    if not valid:
        raise AssertionError('Fixed-point bijection failed')
    return before, after, lifted
