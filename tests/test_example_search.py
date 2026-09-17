import itertools
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'experiments'))
from verify_examples import exhaustive, validate
from ccreduce.symbolic import expression_tree


class ExampleTests(unittest.TestCase):
    def test_exhaustive_bit_patterns_against_scalar_states(self):
        # Exercise every bit-pattern size, with both nonlinear and XOR functions.
        for n in range(1, 8):
            names = ['x' + str(j) for j in range(n)]
            trees = {name: expression_tree(f'{name} ^ ({names[0]} & {names[-1]})') for name in names}
            expected = sum(all(x[j] == (x[j] ^ (x[0] & x[-1])) for j in range(n))
                           for x in itertools.product((0, 1), repeat=n))
            self.assertEqual(exhaustive(trees, {})['count'], expected)

    def test_cardiac_reconstruction_regression(self):
        candidate = json.loads((ROOT / 'results/example_search/010.json').read_text())['candidates'][0]
        r = validate('010', candidate['assignment'], candidate['elimination_sequence'], 'regression')
        self.assertEqual(r['original_exhaustive']['count'], 2)
        self.assertTrue(r['fixed_point_reduction_verified'])
        self.assertTrue(r['classification']['dynamic_topology']['symmetric_interaction_graph'])

    def test_aurora_partial_input_regression(self):
        records = json.loads((ROOT / 'results/example_search/verified_examples.json').read_text())
        r = next(r for r in records if r['id'] == '068')
        checked = validate('068', r['assignment'], r['elimination_sequence'], 'regression')
        self.assertEqual(checked['rules'], {'v_AURKAActive': 'v_AURKAActive',
                         'v_SpindleAssembly': 'v_AURKAActive & !v_SpindleAssembly'})
        self.assertEqual(checked['original_exhaustive']['count'], 4)
        self.assertTrue(checked['fixed_point_reduction_verified'])


if __name__ == '__main__':
    unittest.main()
