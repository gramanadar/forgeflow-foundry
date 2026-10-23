import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class WorkflowTests(unittest.TestCase):
    def test_dispatch_permissions_and_dry_run_encoding(self):
        text = (ROOT / ".github/workflows/dispatch.yml").read_text()
        self.assertIn("contents: read", text)
        self.assertIn("issues: write", text)
        self.assertNotIn("pull-requests:", text)
        self.assertNotIn("contents: write", text)
        self.assertNotIn("write-all", text)
        self.assertNotIn("id-token:", text)
        self.assertIn("cancel-in-progress: false", text)
        self.assertNotIn("schedule:", text)
        self.assertIn("persist-credentials: false", text)
        self.assertIn("DRY_RUN: ${{ github.event.inputs.dry_run }}", text)
        self.assertNotIn("DRY_RUN: ${{ inputs.dry_run }}", text)
        self.assertIn("timeout-minutes: 10", text)
        self.assertLess(text.index("name: Dispatch one task"), text.index("CURSOR_API_KEY:"))
        self.assertEqual(text.count("CURSOR_API_KEY:"), 1)
        self.assertNotIn("secrets.CURSOR_API_KEY", text.split("name: Dispatch one task")[0])

    def test_ci_is_read_only(self):
        text = (ROOT / ".github/workflows/ci.yml").read_text()
        self.assertIn("contents: read", text)
        self.assertNotIn("contents: write", text)
        self.assertNotIn("issues:", text)
        self.assertNotIn("pull_request_target", text)
        self.assertNotIn("secrets.", text)
        self.assertIn("persist-credentials: false", text)


if __name__ == "__main__":
    unittest.main()
