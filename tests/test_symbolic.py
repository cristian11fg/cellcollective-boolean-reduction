"""Independent exhaustive oracle for the symbolic reduction and classification."""
import ast
from itertools import product
from pathlib import Path
import random
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'src'), str(ROOT / '.tools/research')]
try:
    from ccreduce.symbolic import read_symbolic, classify, reduce_symbolic, certify, fixed_point_summary, local_class
    AVAILABLE = True
except ImportError:
    AVAILABLE = False
from ccreduce.parser import read_bnet
from ccreduce.reduction import reduce_network
from ccreduce.fixed_points import fixed_points
from ccreduce.structure import local_structure


@unittest.skipUnless(AVAILABLE, 'Install research extras for symbolic tests')
class SymbolicTests(unittest.TestCase):
    def test_all_three_argument_functions(self):
        from dd.autoref import BDD
        from ccreduce.boolean import Function, states
        bdd = BDD()
        bdd.declare('x', 'y', 'z')
        names = ('x', 'y', 'z')
        for values in product((0, 1), repeat=8):
            truth = Function(names, values).simplify()
            f = bdd.false
            for state, value in zip(states(names), values):
                if value:
                    cube = bdd.true
                    for n, bit in state.items():
                        cube &= bdd.var(n) if bit else ~bdd.var(n)
                    f |= cube
            actual, expected = local_class(bdd, f), local_structure(truth)
            for key in ('signs', 'MIN', 'MAX', 'constant', 'unate'):
                self.assertEqual(actual[key], expected[key], (values, key))

    def test_pilot_oracle(self):
        import json
        for ident in ('007', '023', '029', '031', '064'):
            folder = ROOT / 'data/raw' / ident
            inputs = json.loads((folder / 'metadata.json').read_text())['input-names']
            table = read_bnet(folder / 'model.bnet', inputs)
            symbolic = read_symbolic(folder / 'model.bnet', inputs)
            for policy in ('first', 'min_degree', 'random'):
                reduced, steps = reduce_symbolic(symbolic, policy)
                reference = reduce_network(table, policy, seed=42)
                self.assertEqual([n for n, _ in steps], [n for n, _ in reference.steps])
                for n, f in reference.network.functions.items():
                    from ccreduce.boolean import states
                    self.assertEqual(set(f.support), reduced.functions[n].support)
                    for state in states(f.support):
                        value = symbolic.bdd.let({k: bool(v) for k, v in state.items()}, reduced.functions[n])
                        self.assertEqual(value == symbolic.bdd.true, bool(f(state)))
                self.assertTrue(certify(folder / 'model.bnet', symbolic, reduced, steps)['bijection_verified'])
                self.assertEqual(fixed_point_summary(reduced)['count'], len(fixed_points(table)))

    def test_corrupted_result_rejected(self):
        from ccreduce.symbolic import SymbolicNetwork
        folder = ROOT / 'data/raw/031'
        network = read_symbolic(folder / 'model.bnet')
        reduced, steps = reduce_symbolic(network)
        altered = dict(reduced.functions)
        altered['v_SFF'] = network.bdd.true
        broken = SymbolicNetwork(network.bdd, altered, frozenset())
        self.assertFalse(certify(folder / 'model.bnet', network, broken, steps)['bijection_verified'])

    def test_input_scope_and_vacuity(self):
        from ccreduce.symbolic import SymbolicNetwork
        from dd.autoref import BDD
        bdd = BDD()
        bdd.declare('u', 'x')
        network = SymbolicNetwork(bdd, {'u': bdd.var('u'), 'x': ~bdd.var('u')}, frozenset({'u'}))
        self.assertTrue(classify(network)['out_uniform'])
        self.assertFalse(classify(network, True)['out_uniform'])
        reduced, _ = reduce_symbolic(network)
        self.assertTrue(classify(reduced)['vacuous'])
        self.assertFalse(classify(reduced)['homogeneous_MIN'])


if __name__ == '__main__':
    unittest.main()
