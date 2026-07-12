"""Tests for the built-in tools. Run: python -m unittest discover -s tests -v"""
import unittest
from dynarq_agent.tools.calculator import calculate
from dynarq_agent.tools.converter import convert_units
from dynarq_agent.tools.text_tools import text_stats
from dynarq_agent.tools import default_registry


class TestCalculator(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(calculate("2 + 3 * 4"), "14")
        self.assertEqual(calculate("(4 + 5) * 3"), "27")
        self.assertEqual(calculate("2 ** 10"), "1024")

    def test_is_safe(self):
        # Anything that is not plain arithmetic must be refused, not executed.
        self.assertTrue(calculate("__import__('os').system('echo hi')").startswith("Error"))


class TestConverter(unittest.TestCase):
    def test_length(self):
        self.assertIn("3000", convert_units(3, "km", "m"))
        self.assertIn("100", convert_units(1, "m", "cm"))

    def test_temperature(self):
        self.assertIn("212", convert_units(100, "c", "f"))
        self.assertIn("273", convert_units(0, "c", "k"))

    def test_unknown_units(self):
        self.assertTrue(convert_units(1, "apples", "oranges").startswith("Error"))


class TestTextStats(unittest.TestCase):
    def test_counts(self):
        result = text_stats("Hello world. Bye now!")
        self.assertIn("4 words", result)
        self.assertIn("2 sentence", result)


class TestRegistry(unittest.TestCase):
    def test_default_registry_has_tools(self):
        registry = default_registry()
        self.assertEqual(len(registry), 6)
        self.assertIsNotNone(registry.get("calculator"))
        self.assertIsNotNone(registry.get("read_file"))
        self.assertIsNotNone(registry.get("fetch_url"))
        # Each tool exposes a valid OpenAI-style schema.
        for schema in registry.schemas():
            self.assertEqual(schema["type"], "function")
            self.assertIn("name", schema["function"])


if __name__ == "__main__":
    unittest.main()
