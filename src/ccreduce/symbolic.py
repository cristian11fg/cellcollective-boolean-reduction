"""Exact BDD reduction, semantic classification, and independent SMT certificates.

No truth-table arity bound. Resource limits are reported separately from a
mathematically irreducible network. Optional dependencies: dd and z3-solver.
"""
import ast
from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import random

from dd.autoref import BDD


def expression_tree(text):
    return ast.parse(text.replace('!', '~').strip(), mode='eval').body


def evaluate_tree(node, variable, constant, negate, binary):
    if isinstance(node, ast.Name):
        return variable(node.id)
    if isinstance(node, ast.Constant) and type(node.value) is int and node.value in (0, 1):
        return constant(bool(node.value))
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Invert):
        return negate(evaluate_tree(node.operand, variable, constant, negate, binary))
    if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.BitAnd, ast.BitOr, ast.BitXor)):
        return binary(type(node.op), evaluate_tree(node.left, variable, constant, negate, binary),
                      evaluate_tree(node.right, variable, constant, negate, binary))
    raise ValueError(f'Unsupported Boolean syntax: {ast.dump(node)}')


def bnet_trees(path, inputs):
    trees = {}
    for line in Path(path).read_text(encoding='utf-8-sig').splitlines():
        line = line.split('#', 1)[0].strip()
        if not line or line.replace(' ', '').lower() == 'targets,factors':
            continue
        name, text = map(str.strip, line.split(',', 1))
        if not name.isidentifier() or name in trees:
            raise ValueError(f'Invalid or duplicate target: {name}')
        trees[name] = expression_tree(text)
    for name in inputs:
        trees.setdefault(name, ast.Name(id=name))
    return trees


@dataclass
class SymbolicNetwork:
    bdd: object
    functions: dict
    inputs: frozenset

    def __post_init__(self):
        if not self.inputs <= self.functions.keys():
            raise ValueError('Unknown inputs')
        for name, rule in self.functions.items():
            if not rule.support <= self.functions.keys():
                raise ValueError(f'Undeclared regulators: {name}')
        for name in self.inputs:
            if self.functions[name] != self.bdd.var(name):
                raise ValueError(f'Nonidentity input: {name}')


def read_symbolic(path, inputs=()):
    trees = bnet_trees(path, inputs)
    bdd = BDD()
    bdd.declare(*sorted(trees))
    functions = {n: evaluate_tree(t, bdd.var, lambda v: bdd.true if v else bdd.false,
                                  lambda f: ~f, lambda op, a, b: bdd.apply(
                                      {ast.BitAnd: 'and', ast.BitOr: 'or', ast.BitXor: 'xor'}[op], a, b))
                 for n, t in trees.items()}
    return SymbolicNetwork(bdd, functions, frozenset(inputs))


def local_class(bdd, f):
    signs = {}
    for name in sorted(f.support):
        low, high = bdd.let({name: False}, f), bdd.let({name: True}, f)
        positive, negative = (high & ~low) != bdd.false, (low & ~high) != bdd.false
        signs[name] = 'mixed' if positive and negative else '+' if positive else '-'
    if not signs:
        return {'signs': signs, 'constant': True, 'MIN': False, 'MAX': False,
                'unate': True, 'gates': ['CONST'], 'affine': True}
    conjunction, disjunction = bdd.true, bdd.false
    for name, sign in signs.items():
        literal = bdd.var(name) if sign == '+' else ~bdd.var(name)
        conjunction &= literal
        disjunction |= literal
    unate = 'mixed' not in signs.values()
    is_min, is_max = unate and f == conjunction, unate and f == disjunction
    positive = all(s == '+' for s in signs.values())
    negative = all(s == '-' for s in signs.values())
    gates = []
    for label, condition in [('AND', is_min and positive), ('OR', is_max and positive),
                             ('NAND', is_max and negative), ('NOR', is_min and negative)]:
        if condition:
            gates.append(label)
    if len(signs) == 1:
        gates.append('COPY' if positive else 'NOT')
    # An affine function has constant Boolean derivatives in every essential variable.
    derivatives = [bdd.apply('xor', bdd.let({n: False}, f), bdd.let({n: True}, f)) for n in signs]
    affine = all(d == bdd.true or d == bdd.false for d in derivatives)
    f_zero = bdd.let({n: False for n in signs}, f)
    is_xor = affine and all(d == bdd.true for d in derivatives) and f_zero == bdd.false
    is_xnor = affine and all(d == bdd.true for d in derivatives) and f_zero == bdd.true
    return {'signs': signs, 'constant': False, 'MIN': is_min, 'MAX': is_max,
            'unate': unate, 'gates': gates, 'affine': affine,
            'AND': is_min and positive, 'OR': is_max and positive,
            'NAND': is_max and negative, 'NOR': is_min and negative,
            'AND_NOT': is_min, 'OR_NOT': is_max, 'XOR': is_xor, 'XNOR': is_xnor,
            'COPY': len(signs) == 1 and positive, 'NOT': len(signs) == 1 and negative}


def classify(network, include_inputs=False):
    bdd = network.bdd
    local = {n: local_class(bdd, f) for n, f in network.functions.items()
             if include_inputs or n not in network.inputs}
    active = [p for p in local.values() if not p['constant']]
    outgoing = {}
    for target, p in local.items():
        for source, sign in p['signs'].items():
            outgoing.setdefault(source, {})[target] = sign
    conflicts = {n: t for n, t in outgoing.items()
                 if 'mixed' in t.values() or len(set(t.values())) > 1}
    uniform = not conflicts
    nonvacuous = bool(active)
    min_family = nonvacuous and all(p['MIN'] for p in active)
    max_family = nonvacuous and all(p['MAX'] for p in active)
    minmax = nonvacuous and all(p['MIN'] or p['MAX'] for p in active)
    gate_family = nonvacuous and all(set(p['gates']) & {'AND', 'OR', 'NAND', 'NOR'} for p in active)
    common = set.intersection(*(set(p['gates']) for p in active)) if active else set()
    is_and_not = nonvacuous and all(p['AND_NOT'] for p in active)
    is_or_not = nonvacuous and all(p['OR_NOT'] for p in active)
    is_and = nonvacuous and all(p['AND'] for p in active)
    is_or = nonvacuous and all(p['OR'] for p in active)
    signed_and = is_and_not and uniform
    signed_or = is_or_not and uniform
    edges = {(s, t) for t, p in local.items() for s in p['signs']}
    # Solve the signed switching equations sign(j->i)=s_j*s_i.
    switching, switchable = {}, True
    neighbours = {}
    for source, targets in outgoing.items():
        for target, sign in targets.items():
            edge_sign = 1 if sign == '+' else -1 if sign == '-' else 0
            if not edge_sign:
                switchable = False
                continue
            neighbours.setdefault(source, []).append((target, edge_sign))
            neighbours.setdefault(target, []).append((source, edge_sign))
    for start in neighbours:
        if start in switching:
            continue
        switching[start] = 1
        todo = [start]
        while todo:
            node = todo.pop()
            for other, edge_sign in neighbours[node]:
                expected = switching[node] * edge_sign
                if other in switching:
                    switchable &= switching[other] == expected
                else:
                    switching[other] = expected
                    todo.append(other)
    return {'nodes': len(network.functions), 'n_nodes': len(network.functions), 'inputs': len(network.inputs),
            'internal_nodes': len(network.functions) - len(network.inputs),
            'nonconstant_rules': len(active), 'constant_rules': len(local) - len(active),
            'vacuous': not nonvacuous, 'out_uniform': uniform,
            'out_uniform_nonvacuous': uniform and nonvacuous,
            'locally_unate': all(p['unate'] for p in active),
            'MIN': min_family, 'MAX': max_family, 'MIN_MAX': minmax,
            'is_conjunctive': is_and, 'is_disjunctive': is_or,
            'is_AND_NOT': is_and_not, 'is_OR_NOT': is_or_not,
            'is_AND_OR_NOT': is_and_not or is_or_not or (nonvacuous and all(p['AND_NOT'] or p['OR_NOT'] for p in active)),
            'is_AND_OR': nonvacuous and all(p['AND'] or p['OR'] for p in active),
            'is_AND_OR_NAND_NOR': gate_family,
            'AND_OR_NOT_out_uniform': minmax and uniform,
            'AND_OR_NAND_NOR': gate_family,
            'AND_OR_NAND_NOR_out_uniform': gate_family and uniform,
            'homogeneous_MIN': min_family and uniform,
            'homogeneous_MAX': max_family and uniform,
            'signed_operator_homogeneous_AND': signed_and,
            'signed_operator_homogeneous_OR': signed_or,
            'signed_operator_homogeneous': 'AND' if signed_and else 'OR' if signed_or else None,
            'homogeneous_gate': bool(common), 'common_gates': sorted(common),
            'positive_AND': 'AND' in common, 'positive_OR': 'OR' in common,
            'affine': nonvacuous and all(p['affine'] for p in active),
            'reciprocal_support': all((t, s) in edges for s, t in edges),
            'all_internal_self_regulated': all(n in network.functions[n].support for n in local),
            'all_self_loop': all(n in network.functions[n].support for n in local),
            'self_loop_count': sum(n in network.functions[n].support for n in local),
            'is_monotone': nonvacuous and all(s == '+' for p in active for s in p['signs'].values()),
            'switchable_to_monotone': switchable,
            'switching_witness': {n: ('+' if value == 1 else '-') for n, value in switching.items()},
            'positive_edges': sum(s == '+' for targets in outgoing.values() for s in targets.values()),
            'negative_edges': sum(s == '-' for targets in outgoing.values() for s in targets.values()),
            'non_unate_edges': sum(s == 'mixed' for targets in outgoing.values() for s in targets.values()),
            'has_multi_input_rule': any(len(p['signs']) > 1 for p in active),
            'edges': len(edges), 'max_indegree': max((len(p['signs']) for p in local.values()), default=0),
            'local_family_counts': dict(Counter('CONST' if p['constant'] else 'MIN_MAX' if p['MIN'] and p['MAX']
                                              else 'MIN' if p['MIN'] else 'MAX' if p['MAX']
                                              else 'UNATE_OTHER' if p['unate'] else 'NON_UNATE' for p in local.values())),
            'conflicts': conflicts, 'local': local}


def reduce_symbolic(network, policy='first', seed=42, max_bdd_nodes=500000):
    if policy not in ('first', 'min_degree', 'min_growth', 'random'):
        raise ValueError(policy)
    bdd, functions, steps = network.bdd, dict(network.functions), []
    rng = random.Random(seed)
    while True:
        supports = {n: f.support for n, f in functions.items()}
        candidates = sorted(n for n in functions if n not in network.inputs and n not in supports[n])
        if not candidates:
            return SymbolicNetwork(bdd, functions, network.inputs), steps
        if len(bdd) > max_bdd_nodes:
            raise MemoryError(f'BDD node budget exceeded: {len(bdd)}')
        if policy == 'first':
            chosen = candidates[0]
        elif policy == 'random':
            chosen = rng.choice(candidates)
        elif policy == 'min_degree':
            chosen = min(candidates, key=lambda n: (len(supports[n]) + sum(n in s for s in supports.values()), n))
        else:
            # Structural support-growth estimate; distinct from the pilot truth-table trial cost.
            chosen = min(candidates, key=lambda n: (sum(len((s - {n}) | supports[n]) - len(s)
                                                        for s in supports.values() if n in s), n))
        rule = functions.pop(chosen)
        steps.append((chosen, rule))
        functions = {n: bdd.let({chosen: rule}, f) if chosen in supports[n] else f
                     for n, f in functions.items()}


def bdd_to_z3(bdd, zvars):
    import z3

    @lru_cache(None)
    def convert(f):
        if f == bdd.true:
            return z3.BoolVal(True)
        if f == bdd.false:
            return z3.BoolVal(False)
        if f.negated:
            return z3.Not(convert(~f))
        _, low, high = bdd.succ(f)
        return z3.If(zvars[f.var], convert(high), convert(low))
    return convert


def certify(path, original, reduced, steps, timeout_ms=30000):
    """SMT equality of original FP equations and reduced equations + triangular trace.

    Original expressions are translated directly from the input AST, independently
    of BDD parsing, substitution and semantic simplification.
    """
    import z3
    zvars = {n: z3.Bool(n) for n in original.functions}
    direct = {n: evaluate_tree(t, zvars.__getitem__, z3.BoolVal, z3.Not,
                               lambda op, a, b: {ast.BitAnd: z3.And, ast.BitOr: z3.Or, ast.BitXor: z3.Xor}[op](a, b))
              for n, t in bnet_trees(path, original.inputs).items()}
    convert = bdd_to_z3(original.bdd, zvars)
    remaining = set(original.functions)
    for name, rule in steps:
        if name in rule.support or name in original.inputs or not rule.support <= remaining - {name}:
            raise AssertionError('Invalid triangular elimination trace')
        remaining.remove(name)
    if remaining != set(reduced.functions):
        raise AssertionError('Trace and reduced variables disagree')
    lhs = z3.And(*[zvars[n] == f for n, f in direct.items()])
    rhs = z3.And(*[zvars[n] == convert(f) for n, f in list(reduced.functions.items()) + steps])
    convert.cache_clear()
    solver = z3.Solver()
    solver.set(timeout=timeout_ms)
    solver.add(z3.Xor(lhs, rhs))
    result = solver.check()
    return {'status': str(result), 'bijection_verified': result == z3.unsat,
            'method': 'Independent Z3 equivalence of original fixed-point equations and reduced equations plus triangular reconstruction trace',
            'reason_unknown': solver.reason_unknown() if result == z3.unknown else None}


def fixed_point_summary(network, limit=4096, timeout_ms=5000):
    import z3
    names = sorted(network.functions)
    variables = {n: z3.Bool(n) for n in names}
    convert = bdd_to_z3(network.bdd, variables)
    solver = z3.Solver()
    solver.set(timeout=timeout_ms)
    solver.add(*[variables[n] == convert(f) for n, f in network.functions.items()])
    convert.cache_clear()
    points = []
    for _ in range(limit + 1):
        result = solver.check()
        if result == z3.unsat:
            return {'exact': True, 'count': len(points), 'examples': points[:16]}
        if result == z3.unknown:
            return {'exact': False, 'lower_bound': len(points), 'reason': solver.reason_unknown(), 'examples': points[:16]}
        if len(points) == limit:
            return {'exact': False, 'lower_bound': limit + 1, 'reason': 'enumeration_limit', 'examples': points[:16]}
        model = solver.model()
        state = {n: int(z3.is_true(model.eval(v, model_completion=True))) for n, v in variables.items()}
        points.append(state)
        solver.add(z3.Or(*[v != bool(state[n]) for n, v in variables.items()]))


def readable(bdd, f):
    p = local_class(bdd, f)
    if p['constant']:
        return '1' if f == bdd.true else '0'
    if p['MIN'] or p['MAX']:
        return (' & ' if p['MIN'] else ' | ').join(n if s == '+' else '!' + n for n, s in p['signs'].items())
    # Bound the tree expansion of a shared DAG: even a small DAG can expand exponentially.
    @lru_cache(None)
    def render(g):
        if g == bdd.true:
            return '1'
        if g == bdd.false:
            return '0'
        if g.negated:
            text = '!(' + render(~g) + ')'
        else:
            _, low, high = bdd.succ(g)
            text = f'(({g.var} & {render(high)}) | (!{g.var} & {render(low)}))'
        if len(text) > 10000:
            raise OverflowError('Expression expansion budget')
        return text
    try:
        return render(f)
    except OverflowError:
        return '[see BDD artifact]'
    finally:
        render.cache_clear()
