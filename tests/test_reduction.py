import random
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from ccreduce.boolean import Function, Network
from ccreduce.parser import parse_expression, read_bnet
from ccreduce.reduction import eliminate, reduce_network
from ccreduce.fixed_points import fixed_points, validate_bijection
from ccreduce.metrics import classify, metrics


def network(rules, inputs=()):
    return Network({n: parse_expression(f) for n, f in rules.items()}, frozenset(inputs))


class ReductionTests(unittest.TestCase):
    def test_paper_examples_2_1_and_2_2(self):
        original = network({'x1': '(x2 & x3) | x2', 'x2': '(x1 & x3) | !x2', 'x3': '!x1'})
        self.assertEqual(original.functions['x1'].support, ('x2',))
        reduced = eliminate(original, 'x3')
        self.assertEqual(reduced.functions['x2'], parse_expression('!x2'))
        self.assertEqual(fixed_points(original), [])
        validate_bijection(original, reduce_network(original))

    def test_empty_reduction_has_one_fixed_point(self):
        result = reduce_network(network({'a': '0', 'b': '!a', 'c': 'a | b'}))
        self.assertEqual(result.network.functions, {})
        self.assertEqual(fixed_points(result.network), [{}])
        self.assertEqual(result.lift({}), {'a': 0, 'b': 1, 'c': 1})

    def test_self_loops_and_inputs(self):
        original = network({'u': 'u', 'a': '!u', 'b': 'b & a'}, ('u',))
        result = reduce_network(original)
        self.assertIn('u', result.network.functions)
        self.assertIn('b', result.network.functions)
        validate_bijection(original, result)
        with self.assertRaises(ValueError):
            eliminate(original, 'u')

    def test_semantic_self_loop_removed(self):
        f = parse_expression('(a & b) | (!a & b)')
        self.assertEqual(f, parse_expression('b'))

    def test_exhaustive_all_two_node_networks(self):
        # All 16^2 maps {0,1}^2 -> {0,1}^2, independent FP oracle.
        for a in range(16):
            for b in range(16):
                original = Network({n: Function(('a', 'b'), tuple((mask >> i) & 1 for i in range(4))) for n, mask in (('a', a), ('b', b))})
                for policy in ('first', 'min_degree', 'min_growth', 'random'):
                    validate_bijection(original, reduce_network(original, policy, 17))

    def test_random_four_node_networks(self):
        rng = random.Random(123)
        for _ in range(100):
            rules = {}
            for n in 'abcd':
                support = tuple(v for v in 'abcd' if rng.random() < .5)
                rules[n] = Function(support, tuple(rng.randrange(2) for _ in range(2 ** len(support))))
            original = Network(rules)
            for policy in ('first', 'min_degree', 'min_growth', 'random'):
                validate_bijection(original, reduce_network(original, policy, 19))

    def test_classification(self):
        for expression, expected in [('a & b', 'AND'), ('a | b', 'OR'), ('!(a & b)', 'NAND'), ('!(a | b)', 'NOR'), ('a ^ b', 'XOR'), ('!(a ^ b)', 'XNOR'), ('a & !b', 'SIGNED_AND'), ('a | !b', 'SIGNED_OR'), ('a | (b & c)', 'GENERAL')]:
            self.assertEqual(classify(parse_expression(expression)), expected)

    def test_graph_metrics(self):
        m = metrics(network({'a': 'b', 'b': 'a', 'c': '0'}))
        self.assertEqual((m['edges'], m['scc'], m['weak_components']), (2, 2, 2))

    def test_reject_invalid_syntax_and_limits(self):
        for expression in ['__import__("os")', 'a + b', '2', 'a and b']:
            with self.assertRaises(ValueError):
                parse_expression(expression)
        with self.assertRaises(ValueError):
            parse_expression('a | b', max_support=1)

    def test_pilot_all_policies(self):
        import json
        root = Path(__file__).resolve().parents[1]
        for directory in sorted((root / 'data/raw').iterdir()):
            if not directory.is_dir():
                continue
            metadata = json.loads((directory / 'metadata.json').read_text())
            original = read_bnet(directory / 'model.bnet', metadata['input-names'])
            for policy in ('first', 'min_degree', 'min_growth', 'random'):
                validate_bijection(original, reduce_network(original, policy, 42))

if __name__ == '__main__':
    unittest.main()
