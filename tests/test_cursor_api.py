import json
import unittest
from unittest.mock import patch
from foundry.cursor_api import create_agent

class FakeResponse:
    def __enter__(self): return self
    def __exit__(self, *args): pass
    def read(self, *args): return json.dumps({"agent":{"id":"bc-test"},"run":{"id":"run-test"}}).encode()

class CursorAPITests(unittest.TestCase):
    @patch("urllib.request.urlopen", return_value=FakeResponse())
    def test_create_payload(self, urlopen):
        response = create_agent("secret", "https://github.com/o/r", "do task", "bc-123")
        req = urlopen.call_args.args[0]
        body = json.loads(req.data)
        self.assertEqual(body["repos"][0]["startingRef"], "main")
        self.assertTrue(body["autoCreatePR"])
        self.assertFalse(body["workOnCurrentBranch"])
        self.assertEqual(response["run"]["id"], "run-test")
    def test_bad_repo(self):
        with self.assertRaises(ValueError):
            create_agent("key", "http://evil", "task", "bc-123")

if __name__ == "__main__": unittest.main()
