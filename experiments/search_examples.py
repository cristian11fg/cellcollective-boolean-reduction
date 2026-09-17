"""Bounded, reproducible search of alternative reductions; not a prevalence census.

Run from the repository root. Every BBM instance is attempted in an isolated
process. Input configurations are exhaustive only for models with 1..4 inputs.
All qualifying results include independent fixed-point-equation certificates.
"""
import argparse
import ast
from concurrent.futures import ThreadPoolExecutor
import hashlib
import itertools
import json
from pathlib import Path
import subprocess
import sys
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'src'), str(ROOT / '.tools/research')]
OUT = ROOT / 'results/example_search'


def write(path, data):
    path.write_text(json.dumps(data, indent=2), encoding='utf-8')


def condition(original, assignment):
    from ccreduce.symbolic import SymbolicNetwork
    return SymbolicNetwork(original.bdd,
        {n: original.bdd.let({k: bool(v) for k, v in assignment.items()}, f)
         for n, f in original.functions.items() if n not in assignment},
        original.inputs - assignment.keys())


def certificate(path, original, reduced, steps, assignment):
    import z3
    from ccreduce.symbolic import bnet_trees, evaluate_tree, bdd_to_z3
    variables = {n: z3.Bool(n) for n in original.functions}
    direct = {n: evaluate_tree(t, variables.__getitem__, z3.BoolVal, z3.Not,
        lambda op, a, b: {ast.BitAnd: z3.And, ast.BitOr: z3.Or,
                         ast.BitXor: z3.Xor}[op](a, b))
        for n, t in bnet_trees(path, original.inputs).items()}
    remaining = set(original.functions) - assignment.keys()
    for name, rule in steps:
        assert name in remaining and name not in original.inputs
        assert rule.support <= remaining - {name}
        remaining.remove(name)
    assert remaining == set(reduced.functions)
    convert = bdd_to_z3(original.bdd, variables)
    lhs = z3.And(*[variables[n] == f for n, f in direct.items()])
    rhs = z3.And(*[variables[n] == convert(f)
                  for n, f in list(reduced.functions.items()) + steps])
    convert.cache_clear()
    solver = z3.Solver()
    solver.set(timeout=10000)
    solver.add(*[variables[n] == bool(v) for n, v in assignment.items()])
    solver.add(z3.Xor(lhs, rhs))
    status = solver.check()
    return {'status': str(status), 'bijection_verified': status == z3.unsat,
            'method': 'independent original AST vs BDD reduced equations and triangular reconstruction, under input assignment'}


def properties(network):
    from ccreduce.symbolic import classify
    p = classify(network)
    # Strict family convention: constants are not silently empty gates.
    if p['constant_rules']:
        for k in ('is_conjunctive', 'is_disjunctive', 'is_AND_NOT', 'is_OR_NOT',
                  'is_AND_OR_NOT', 'is_AND_OR', 'is_AND_OR_NAND_NOR'):
            p[k] = False
        p['signed_operator_homogeneous'] = None
    nodes = set(network.functions) - network.inputs
    edges = {(s, t) for t in nodes for s in network.functions[t].support if s in nodes}
    reach = {n: {n} | {t for s, t in edges if s == n} for n in nodes}
    for k in sorted(nodes):
        for n in nodes:
            if k in reach[n]:
                reach[n] |= reach[k]
    components, unseen = [], set(nodes)
    while unseen:
        n = min(unseen)
        component = sorted(k for k in unseen if k in reach[n] and n in reach[k])
        components.append(component)
        unseen -= set(component)
    p['dynamic_topology'] = {
        'n_nodes': len(nodes), 'n_edges': len(edges), 'SCCs': components,
        'n_SCC': len(components),
        'strongly_connected': bool(nodes) and len(components) == 1,
        'symmetric_interaction_graph': all((t, s) in edges for s, t in edges),
        'all_self_loop': all((n, n) in edges for n in nodes)}
    return p


def worker(ident):
    from ccreduce.symbolic import read_symbolic, reduce_symbolic, readable, fixed_point_summary
    sys.setrecursionlimit(10000)
    folder = ROOT / 'data/cellcollective' / ident
    meta = json.loads((folder / 'metadata.json').read_text())
    inputs = sorted(meta['input-names'])
    path = folder / 'model.bnet'
    original = read_symbolic(path, inputs)
    assignments = [{}]
    if 0 < len(inputs) <= 4:
        assignments += [dict(zip(inputs, bits)) for bits in itertools.product((0, 1), repeat=len(inputs))]
    result = {'id': ident, 'name': meta['name'], 'publication': meta.get('url-publication'),
        'model_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        'original_dynamic_nodes': len(original.functions) - len(inputs),
        'external_inputs': inputs, 'input_assignments_planned': len(assignments),
        'attempted': 0, 'errors': [], 'candidates': [], 'status': 'running'}
    OUT.mkdir(exist_ok=True, parents=True)
    seen = set()
    for assignment in assignments:
        policies = [('first', 42), ('min_growth', 42), ('random', 10)] if assignment else [('random', seed) for seed in range(10, 22)]
        conditioned = condition(original, assignment)
        before = properties(conditioned)
        for policy, seed in policies:
            result['attempted'] += 1
            try:
                reduced, steps = reduce_symbolic(conditioned, policy, seed, max_bdd_nodes=200000)
                dynamic = set(reduced.functions) - reduced.inputs
                if not 2 <= len(dynamic) <= 12 or not steps:
                    continue
                after = properties(reduced)
                interesting = ((after['is_AND_OR_NOT'] and after['out_uniform']) or
                    after['affine'] or after['is_monotone'] or
                    (after['is_AND_OR_NOT'] and after['switchable_to_monotone']))
                if not interesting or not after['has_multi_input_rule']:
                    continue
                rules = {n: readable(reduced.bdd, reduced.functions[n]) for n in sorted(dynamic)}
                key = json.dumps([assignment, rules], sort_keys=True)
                if key in seen:
                    continue
                seen.add(key)
                cert = certificate(path, original, reduced, steps, assignment)
                if not cert['bijection_verified']:
                    result['errors'].append({'assignment': assignment, 'policy': policy, 'seed': seed, 'certificate': cert})
                    continue
                fp = fixed_point_summary(reduced, limit=256)
                reconstructed = []
                for point in fp['examples']:
                    state = dict(point)
                    for n, f in reversed(steps):
                        value = reduced.bdd.let({k: bool(v) for k, v in state.items()}, f)
                        assert value in (reduced.bdd.false, reduced.bdd.true)
                        state[n] = int(value == reduced.bdd.true)
                    state.update(assignment)
                    reconstructed.append(state)
                result['candidates'].append({'scope': 'input_conditioned_reduced' if assignment else 'reduced',
                    'assignment': assignment, 'policy': policy, 'seed': seed,
                    'before': before, 'after': after, 'rules': rules,
                    'elimination_sequence': [n for n, f in steps],
                    'reconstruction_functions': {n: readable(reduced.bdd, f) for n, f in steps},
                    'certificate': cert, 'fixed_points': fp,
                    'reconstructed_examples': reconstructed,
                    'theorem_applicability': {'status': 'not_assessed', 'reason': 'Family membership alone is insufficient.'}})
            except (MemoryError, OverflowError) as error:
                result['errors'].append({'assignment': assignment, 'policy': policy, 'seed': seed, 'error': repr(error)})
            finally:
                write(OUT / f'{ident}.json', result)
        original.bdd.collect_garbage()
    result['status'] = 'complete'
    write(OUT / f'{ident}.json', result)
    print(ident, result['attempted'], len(result['candidates']), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--worker')
    parser.add_argument('--timeout', type=int, default=60)
    args = parser.parse_args()
    if args.worker:
        worker(args.worker)
        return
    OUT.mkdir(exist_ok=True, parents=True)
    records = json.loads((ROOT / 'data/cellcollective/manifest.json').read_text())['models']
    def run(record):
        ident = record['id']
        start = perf_counter()
        try:
            p = subprocess.run([sys.executable, __file__, '--worker', ident], cwd=ROOT,
                               capture_output=True, text=True, timeout=args.timeout)
            outcome = {'id': ident, 'status': 'complete' if p.returncode == 0 else 'error',
                       'output': (p.stdout + p.stderr)[-1500:]}
        except subprocess.TimeoutExpired:
            outcome = {'id': ident, 'status': 'timeout'}
        outcome['seconds'] = round(perf_counter() - start, 2)
        print(ident, outcome['status'], flush=True)
        return outcome
    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(run, records))
    write(OUT / 'run.json', {'strategy': '12 random orders, seeds 10..21; all assignments for 1..4 inputs with first/min_growth/random(seed10)',
        'candidate_filter': '2..12 dynamic survivors, at least one multiargument rule; signed AND_OR_NOT or affine or monotone or switchable AND_OR_NOT',
        'timeout_per_model_seconds': args.timeout, 'outcomes': outcomes})


if __name__ == '__main__':
    main()
