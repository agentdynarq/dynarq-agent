"""The agent, driven by the offline local router, should route to the right tool."""
import unittest
from dynarq_agent.agent import Agent
from dynarq_agent.backends import LocalRouterBackend
from dynarq_agent.tools import default_registry


def make_agent():
    return Agent(default_registry(), LocalRouterBackend())


class TestAgentLocal(unittest.TestCase):
    def setUp(self):
        self.agent = make_agent()

    def test_math_query(self):
        self.assertIn("42", self.agent.run("what is 6 * 7?"))

    def test_conversion_query(self):
        self.assertIn("2000", self.agent.run("convert 2 km to m"))

    def test_time_query(self):
        self.assertIn("UTC", self.agent.run("what time is it now?"))

    def test_text_stats_query(self):
        self.assertIn("words", self.agent.run("count the words in this sentence"))

    def test_fallback(self):
        self.assertIn("arithmetic", self.agent.run("tell me a story"))


if __name__ == "__main__":
    unittest.main()
