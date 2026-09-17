import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from fetch_live import normalize


class ImportTests(unittest.TestCase):
    def test_long_names_and_common_prefix(self):
        bnet, mapping, inputs, variables = normalize(
            'A = ( A B ) AND NOT ( ERK1/2 )\nA B = A OR ( ERK1/2 )\n', 'ERK1/2\n')
        self.assertIn('v_A, ( v_A_B ) & ! ( v_ERK1_2 )', bnet)
        self.assertEqual(inputs, ['v_ERK1_2'])
        self.assertEqual(len(variables), 2)

    def test_missing_variable_is_not_inferred_as_input(self):
        with self.assertRaisesRegex(ValueError, 'Unknown expression'):
            normalize('A = B\n', '')

    def test_name_collisions_are_preserved(self):
        _, mapping, _, _ = normalize('A-B = A_B\nA_B = A-B\n', '')
        self.assertNotEqual(mapping['A-B'], mapping['A_B'])

    def test_duplicate_target_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            normalize('A = 0\nA = 1\n', '')


if __name__ == '__main__':
    unittest.main()
