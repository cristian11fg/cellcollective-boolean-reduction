"""Replay selected reductions and independently exhaust small state spaces."""
import ast
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'src'), str(ROOT / '.tools/research')]
from ccreduce.symbolic import (SymbolicNetwork, read_symbolic, readable,
    bnet_trees, evaluate_tree, fixed_point_summary, reduce_symbolic)
from search_examples import condition, certificate, properties, write


def exhaustive(trees, assignment, max_free=21):
    """Every state is one bit of an integer; no BDD or SAT used here."""
    names = sorted(set(trees) - assignment.keys())
    if len(names) > max_free:
        raise ValueError('Exhaustive state-space budget exceeded')
    total = 1 << len(names)
    mask = (1 << total) - 1
    variables = {n: mask if v else 0 for n, v in assignment.items()}
    for j, name in enumerate(names):
        if len(names) < 3:
            value = sum(((i >> j) & 1) << i for i in range(total))
        elif j < 3:
            value = int.from_bytes(bytes([0xaa, 0xcc, 0xf0][j:j+1]) * (total // 8), 'little')
        else:
            block = 1 << (j - 3)
            value = int.from_bytes((b'\x00' * block + b'\xff' * block) * (total // (16 * block)), 'little')
        variables[name] = value
    fixed = mask
    for name, tree in trees.items():
        value = evaluate_tree(tree, variables.__getitem__, lambda v: mask if v else 0,
            lambda a: mask ^ a,
            lambda op, a, b: a & b if op is ast.BitAnd else a | b if op is ast.BitOr else a ^ b)
        fixed &= mask ^ (variables[name] ^ value)
    count = fixed.bit_count()
    examples = []
    for _ in range(min(count, 32)):
        bit = fixed & -fixed
        state_id = bit.bit_length() - 1
        examples.append(assignment | {n: (state_id >> j) & 1 for j, n in enumerate(names)})
        fixed ^= bit
    return {'count': count, 'states_evaluated': total, 'examples': examples,
            'method': 'exhaustive bit-parallel AST evaluation, independent of BDD and Z3'}


def replay(original, sequence, assignment):
    network = condition(original, assignment)
    functions, steps = dict(network.functions), []
    for name in sequence:
        rule = functions.pop(name)
        assert name not in rule.support and name not in network.inputs
        steps.append((name, rule))
        functions = {n: original.bdd.let({name: rule}, f) for n, f in functions.items()}
    return SymbolicNetwork(original.bdd, functions, network.inputs), steps


def validate(ident, assignment, sequence, label):
    folder = ROOT / 'data/cellcollective' / ident
    meta = json.loads((folder / 'metadata.json').read_text())
    path = folder / 'model.bnet'
    original = read_symbolic(path, meta['input-names'])
    reduced, steps = replay(original, sequence, assignment)
    cert = certificate(path, original, reduced, steps, assignment)
    assert cert['bijection_verified']
    from ccreduce.symbolic import expression_tree
    rules = {n: readable(reduced.bdd, f) for n, f in reduced.functions.items()}
    reduced_exhaustive = exhaustive({n: expression_tree(f) for n, f in rules.items()}, {})
    result = {'id': ident, 'label': label, 'assignment': assignment,
        'dynamic_nodes_before': len(original.functions) - len(original.inputs),
        'dynamic_nodes_after': len(reduced.functions) - len(reduced.inputs),
        'remaining_inputs': sorted(reduced.inputs),
        'rules': {n: f for n, f in rules.items() if n not in reduced.inputs},
        'classification': properties(reduced), 'certificate': cert,
        'elimination_sequence': sequence,
        'reconstruction_functions': {n: readable(original.bdd, f) for n, f in steps},
        'reduced_exhaustive': reduced_exhaustive}
    if len(original.functions) - len(assignment) <= 21:
        brute = exhaustive(bnet_trees(path, original.inputs), assignment)
        assert brute['count'] == reduced_exhaustive['count'] <= 32
        lifted = []
        for point in reduced_exhaustive['examples']:
            state = dict(point)
            for name, rule in reversed(steps):
                state[name] = int(original.bdd.let({k: bool(v) for k, v in state.items()}, rule) == original.bdd.true)
            lifted.append(state | assignment)
        normalize = lambda points: {tuple(sorted(p.items())) for p in points}
        assert normalize(lifted) == normalize(brute['examples'])
        result['original_exhaustive'] = brute
        result['fixed_point_reduction_verified'] = True
    return result


def main():
    results = []
    for ident, index in [('019', 0), ('010', 0), ('073', 1), ('070', 0)]:
        c = json.loads((ROOT / f'results/example_search/{ident}.json').read_text())['candidates'][index]
        results.append(validate(ident, c['assignment'], c['elimination_sequence'], 'search_candidate'))
    aurora = ['AURKAPresent', 'BORA', 'CDC25B', 'CDK1CCNBComplex', 'CentrosomeMat',
        'Cytokinesis', 'ENSA', 'GWL_MASTL', 'MT', 'NEDD9', 'PLK1', 'PP1', 'PP2A',
        'STMN', 'TPX2', 'WEE1', 'hCPEB']
    results.append(validate('068', {'v_AJUBA': 1, 'v_GSK3B': 0},
                            ['v_' + n for n in aurora], 'user_supplied_partial_condition'))
    # Remove an unnecessary condition from the lymphoid candidate: Il7 stays free.
    meta = json.loads((ROOT / 'data/cellcollective/073/metadata.json').read_text())
    original = read_symbolic(ROOT / 'data/cellcollective/073/model.bnet', meta['input-names'])
    assignment = {'v_Cebpa_ER': 1, 'v_Csf1': 0}
    reduced, steps = reduce_symbolic(condition(original, assignment), 'min_growth')
    results.append(validate('073', assignment, [n for n, f in steps], 'partial_condition_Il7_free'))
    # Verify the complete IL-6 parameter formula, not merely its total count.
    meta = json.loads((ROOT / 'data/cellcollective/019/metadata.json').read_text())
    original = read_symbolic(ROOT / 'data/cellcollective/019/model.bnet', meta['input-names'])
    reduced, steps = replay(original, results[0]['elimination_sequence'], {})
    bdd = original.bdd
    fixed = bdd.true
    for n, f in reduced.functions.items():
        fixed &= ~bdd.apply('xor', bdd.var(n), f)
    a = bdd.var('v_gp130m') & bdd.var('v_il6') & ~bdd.var('v_nfkb')
    predicted = ~a & ~bdd.var('v_mek6') & ~bdd.var('v_shp2') & ~bdd.var('v_stat3_ta')
    assert fixed == predicted
    assert results[0]['reduced_exhaustive']['count'] == 7 * 2**12
    live_meta = json.loads((ROOT / 'data/live/2314_1/metadata.json').read_text())
    live = read_symbolic(ROOT / 'data/live/2314_1/model.bnet', live_meta['input-names'])
    assert original.functions.keys() == live.functions.keys() and original.inputs == live.inputs
    assert all(bdd.copy(f, live.bdd) == live.functions[n] for n, f in original.functions.items())
    results[0]['parameter_prediction'] = {
        'fixed_point_exists_iff': '!(gp130m & il6 & !nfkb)',
        'count_per_assignment_if_true': 1, 'count_per_assignment_if_false': 0,
        'fixed_dynamic_state_if_exists': {'mek6': 0, 'shp2': 0, 'stat3_ta': 0},
        'exact_total_over_all_32768_input_assignments': 28672,
        'prediction_verified_by_BDD_equivalence': True,
        'live_2314_1_function_equivalence_verified': True,
        'proof_type': 'direct algebraic derivation; no named theorem inferred from family'}
    write(ROOT / 'results/example_search/verified_examples.json', results)
    for r in results:
        print(r['id'], r['label'], r['rules'], r['reduced_exhaustive']['count'])


if __name__ == '__main__':
    main()
