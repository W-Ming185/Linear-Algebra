"""Regression coverage for parsing solver output captured through piped stdin."""
import unittest

from app import parse_output


class ParseOutputTests(unittest.TestCase):
    def test_method_after_input_prompts(self):
        output = (
            "Enter protein : Enter carb : Enter fats : Enter fiber : "
            "Enter your ingredient (type exit to exit) : "
            "Enter minimum amount for ingredient 1 (g) : "
            "Enter your ingredient (type exit to exit) : USing LS\n"
            "Ingredient_List :\nBanana : 100.0 g\nError : 0.125\n"
            "Total :\nTotal_Protein : 2.0 g\nTotal Carb : 20.0 g\n"
            "Total Fat : 0.5 g\nTotal_Fibre : 3.0 g\n"
            "Total_Energy : 100.0 kcal\nTotal_Price : 10.0 Baht\n"
        )
        result = parse_output(output)
        self.assertEqual(result['method'], 'LS')
        self.assertEqual(result['items'], [{'name': 'Banana', 'grams': 100.0}])
        self.assertEqual(result['error'], '0.125')
        self.assertEqual(result['totals']['protein'], 2.0)
        self.assertEqual(result['totals']['fiber'], 3.0)

    def test_standalone_method_and_case(self):
        for line in ('USing LS', 'Using LS', 'using LS'):
            with self.subTest(line=line):
                self.assertEqual(parse_output(line)['method'], 'LS')
        self.assertEqual(parse_output('Using NNLS')['method'], 'NNLS')

    def test_missing_method_is_not_invented(self):
        self.assertIsNone(parse_output('Error : 0.0')['method'])


if __name__ == '__main__':
    unittest.main()
