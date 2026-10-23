import unittest
from foundry.dispatcher import deterministic_agent_id, issue_valid, select_issue, task_prompt

class DispatcherTests(unittest.TestCase):
    def issue(self, number, body="Objective: implement docs. Acceptance criteria: CI green and PR opened."):
        return {"number": number, "title": "Test", "body": body}

    def test_deterministic_id(self):
        a = deterministic_agent_id("owner/repo", 12)
        self.assertEqual(a, deterministic_agent_id("owner/repo", 12))
        self.assertNotEqual(a, deterministic_agent_id("owner/repo", 13))
        self.assertTrue(a.startswith("bc-"))

    def test_selects_oldest_eligible(self):
        self.assertEqual(select_issue([self.issue(4), self.issue(2)] )["number"], 2)

    def test_rejects_missing_criteria(self):
        self.assertFalse(issue_valid(self.issue(1, "a" * 60)))
        self.assertIsNone(select_issue([self.issue(1, "no criteria " * 5)]))

    def test_prompt_contains_safety(self):
        p = task_prompt(self.issue(7))
        self.assertIn("AGENTS.md", p)
        self.assertIn("Never push to main", p)
        self.assertIn("#7", p)

if __name__ == "__main__":
    unittest.main()
