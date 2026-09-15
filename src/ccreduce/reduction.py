"""Veliz-Cuba S/R steps with exact functional dependencies and inverse trace."""
from dataclasses import dataclass
import random
from .boolean import Network


@dataclass
class Reduction:
    network: Network
    steps: list
    policy: str
    seed: int

    def lift(self, state):
        if not self.network.is_fixed(state):
            raise ValueError('Expected a reduced fixed point')
        restored = dict(state)
        for name, function in reversed(self.steps):
            restored[name] = function(restored)
        return restored


def eliminate(network, name, max_support=16):
    rule = network.functions[name]
    if name in network.inputs or name in rule.support:
        raise ValueError(f'Node {name} cannot be eliminated')
    return Network({n: f.substitute(name, rule, max_support) for n, f in network.functions.items() if n != name}, network.inputs)


def reduce_network(network, policy='first', seed=0, max_support=16):
    if policy not in ('first', 'min_degree', 'min_growth', 'random'):
        raise ValueError('Unknown reduction policy')
    current, steps = network, []
    rng = random.Random(seed)
    while True:
        candidates = sorted(n for n, f in current.functions.items() if n not in current.inputs and n not in f.support)
        if not candidates:
            return Reduction(current, steps, policy, seed)
        if policy == 'random':
            chosen = rng.choice(candidates)
        elif policy == 'min_degree':
            chosen = min(candidates, key=lambda n: (len(current.functions[n].support) + sum(n in f.support for f in current.functions.values()), n))
        elif policy == 'min_growth':
            # Exact trial cost in table entries; failures are explicit, not irreducibility.
            trials = {n: eliminate(current, n, max_support) for n in candidates}
            chosen = min(candidates, key=lambda n: (sum(len(f.values) for f in trials[n].functions.values()), n))
        else:
            chosen = candidates[0]
        next_network = trials[chosen] if policy == 'min_growth' else eliminate(current, chosen, max_support)
        steps.append((chosen, current.functions[chosen]))
        current = next_network
