"""Local truth tables: first variable is the most significant index bit."""
from dataclasses import dataclass
from itertools import product


def states(names):
    for bits in product((0, 1), repeat=len(names)):
        yield dict(zip(names, bits))


@dataclass(frozen=True)
class Function:
    support: tuple[str, ...]
    values: tuple[int, ...]

    def __post_init__(self):
        if len(set(self.support)) != len(self.support):
            raise ValueError('Duplicate variables')
        if len(self.values) != 2 ** len(self.support) or any(v not in (0, 1) for v in self.values):
            raise ValueError('Invalid Boolean truth table')

    def __call__(self, state):
        index = 0
        for name in self.support:
            bit = state[name]
            if bit not in (0, 1):
                raise ValueError('Non-Boolean state')
            index = 2 * index + int(bit)
        return self.values[index]

    @classmethod
    def build(cls, names, evaluate, max_support=16):
        names = tuple(sorted(names))
        if len(names) > max_support:
            raise ValueError(f'Local truth-table limit exceeded: {len(names)} > {max_support}')
        return cls(names, tuple(int(evaluate(s)) for s in states(names))).simplify()

    def simplify(self):
        names, values = list(self.support), self.values
        # A variable is essential iff its two cofactors differ.
        for position in range(len(names) - 1, -1, -1):
            mask = 1 << (len(names) - position - 1)
            if all(values[i] == values[i | mask] for i in range(len(values)) if not i & mask):
                values = tuple(values[i] for i in range(len(values)) if not i & mask)
                names.pop(position)
        return Function(tuple(names), values)

    def substitute(self, name, replacement, max_support=16):
        if name not in self.support:
            return self
        names = (set(self.support) - {name}) | set(replacement.support)
        return Function.build(names, lambda s: self({**s, name: replacement(s)}), max_support)

    def as_dict(self):
        return {'support': self.support, 'values': self.values}

    def expression(self):
        """Canonical DNF, for inspection; not a minimum-size expression."""
        if not self.support:
            return str(self.values[0])
        terms = []
        for s in states(self.support):
            if self(s):
                terms.append('(' + ' & '.join(n if s[n] else '!' + n for n in self.support) + ')')
        return ' | '.join(terms) or '0'


@dataclass
class Network:
    functions: dict[str, Function]
    inputs: frozenset[str] = frozenset()

    def __post_init__(self):
        self.functions = {n: f.simplify() for n, f in self.functions.items()}
        if not self.inputs <= self.functions.keys():
            raise ValueError('Unknown input nodes')
        for name, f in self.functions.items():
            if not set(f.support) <= self.functions.keys():
                raise ValueError(f'Undeclared regulators of {name}')
        for name in self.inputs:
            if self.functions[name] != Function((name,), (0, 1)):
                raise ValueError('Free inputs must have identity update functions')

    def is_fixed(self, state):
        return set(state) == set(self.functions) and all(state[n] == f(state) for n, f in self.functions.items())

    def as_dict(self):
        return {'inputs': sorted(self.inputs), 'functions': {n: f.as_dict() for n, f in self.functions.items()}}
