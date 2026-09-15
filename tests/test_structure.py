import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from ccreduce.boolean import Network
from ccreduce.parser import parse_expression
from ccreduce.structure import local_structure, network_structure


def net(rules, inputs=()):
    return Network({n: parse_expression(f) for n, f in rules.items()}, frozenset(inputs))


class StructureTests(unittest.TestCase):
    def test_min_max_de_morgan_and_unary_overlap(self):
        self.assertTrue(local_structure(parse_expression('!(a | b)'))['MIN'])
        self.assertTrue(local_structure(parse_expression('!(a & b)'))['MAX'])
        for expression in ('a', '!a'):
            p = local_structure(parse_expression(expression))
            self.assertTrue(p['MIN'] and p['MAX'])

    def test_local_unateness_does_not_imply_out_uniformity(self):
        p = network_structure(net({'a': 'a', 'b': '!a'}))
        self.assertTrue(p['locally_unate'])
        self.assertFalse(p['out_uniform'])
        self.assertEqual(p['conflicts']['a'], {'a': '+', 'b': '-'})

    def test_xor_context_dependence(self):
        p = local_structure(parse_expression('a ^ b'))
        self.assertFalse(p['unate'])
        self.assertEqual(p['signs']['a'], 'mixed')
        self.assertEqual(set(p['witnesses']['a']), {'+', '-'})

    def test_ignore_artificial_input_identity(self):
        n = net({'u': 'u', 'a': '!u'}, ('u',))
        self.assertTrue(network_structure(n)['out_uniform'])
        self.assertFalse(network_structure(n, True)['out_uniform'])

    def test_uniform_general_function(self):
        p = network_structure(net({'a': '0', 'b': '0', 'c': '0', 'd': 'a | (b & c)'}))
        self.assertTrue(p['out_uniform'])
        self.assertFalse(p['MIN_MAX_with_constants'])

    def test_three_node_article_candidate(self):
        n = net({'a': 'a & !b & !c', 'b': 'a & !b & !c', 'c': 'a & !b & !c'})
        p = network_structure(n)
        self.assertTrue(p['homogeneous_MIN_with_constants'])
        self.assertTrue(p['reciprocal_support'])
        self.assertTrue(p['all_rule_nodes_self_regulated'])

    def test_empty_is_vacuous(self):
        p = network_structure(Network({}))
        self.assertTrue(p['out_uniform'])
        self.assertEqual(p['nonconstant_rules'], 0)

    def test_syntactically_mixed_inessential_variable(self):
        p = local_structure(parse_expression('(a & b) | (!a & b)'))
        self.assertEqual(p['signs'], {'b': '+'})
