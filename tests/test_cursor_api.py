import base64
import io
import json
import unittest
import urllib.error
import urllib.request
from unittest.mock import MagicMock, patch

from foundry.cursor_api import (
    CREATE_URL,
    CursorAPIError,
    _RefuseRedirect,
    create_agent,
    valid_api_key,
)

AGENT = "bc-12345678-1234-5678-1234-567812345678"
REPO = "https://github.com/o/r"
KEY = "crsr_test_secret_value"


class FakeResponse:
    def __init__(self, payload=None):
        self.payload = payload or {
            "agent": {"id": AGENT, "url": "https://cursor.com/agents/" + AGENT},
            "run": {"id": "run-123", "agentId": AGENT},
        }

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, *args):
        return json.dumps(self.payload).encode()


def http_error(status, body):
    return urllib.error.HTTPError(
        CREATE_URL,
        status,
        "error",
        None,
        io.BytesIO(body if isinstance(body, bytes) else body.encode()),
    )


class CursorAPITests(unittest.TestCase):
    def _open(self, side_effect=None, payload=None):
        opener = MagicMock()
        if side_effect is not None:
            opener.open.side_effect = side_effect
        else:
            opener.open.return_value = FakeResponse(payload)
        return opener

    @patch("urllib.request.build_opener")
    def test_create_payload(self, build_opener):
        opener = self._open()
        build_opener.return_value = opener
        response = create_agent(KEY, REPO, "do task", AGENT)
        self.assertIs(build_opener.call_args.args[0], _RefuseRedirect)
        request = opener.open.call_args.args[0]
        self.assertEqual(request.full_url, CREATE_URL)
        self.assertEqual(request.get_method(), "POST")
        body = json.loads(request.data)
        self.assertEqual(body["agentId"], AGENT)
        self.assertEqual(body["prompt"], {"text": "do task"})
        self.assertEqual(body["repos"], [{"url": REPO, "startingRef": "main"}])
        self.assertTrue(body["autoCreatePR"])
        self.assertFalse(body["workOnCurrentBranch"])
        self.assertEqual(body["mode"], "agent")
        self.assertNotIn("envVars", body)
        self.assertNotIn("env", body)
        self.assertNotIn("skipReviewerRequest", body)
        self.assertNotIn(KEY, request.data.decode())
        token = base64.b64encode((KEY + ":").encode()).decode()
        self.assertEqual(request.get_header("Authorization"), "Basic " + token)
        self.assertEqual(response["run"]["id"], "run-123")

    def test_bad_repo(self):
        with self.assertRaises(ValueError):
            create_agent(KEY, "http://evil", "task", AGENT)
        for url in (
            "https://github.com/o/r/extra",
            "https://user:token@github.com/o/r",
            "https://github.com/o/r/",
            "https://github.com/o/r.git",
            "https://github.com.evil/o/r",
        ):
            with self.assertRaises(ValueError, msg=url):
                create_agent(KEY, url, "task", AGENT)

    def test_bad_agent_id_and_prompt(self):
        with self.assertRaises(ValueError):
            create_agent(KEY, REPO, "task", "bc-123")
        with self.assertRaises(ValueError):
            create_agent(KEY, REPO, "  ", AGENT)
        with self.assertRaises(ValueError):
            create_agent("bad key", REPO, "task", AGENT)
        with self.assertRaises(ValueError):
            create_agent("key:with-colon", REPO, "task", AGENT)
        self.assertFalse(valid_api_key("line\nbreak"))
        self.assertTrue(valid_api_key(KEY))

    @patch("urllib.request.build_opener")
    def test_http_errors_hide_body(self, build_opener):
        secret = "secret-token-in-body"
        opener = self._open(side_effect=http_error(401, json.dumps({"code": "unauthorized", "message": secret})))
        build_opener.return_value = opener
        with self.assertRaises(CursorAPIError) as caught:
            create_agent(KEY, REPO, "task", AGENT)
        self.assertEqual(caught.exception.status, 401)
        self.assertFalse(caught.exception.conflict)
        self.assertNotIn(secret, str(caught.exception))
        self.assertNotIn(KEY, str(caught.exception))
        self.assertIsNone(caught.exception.__cause__)
        self.assertTrue(caught.exception.__suppress_context__)

    @patch("urllib.request.build_opener")
    def test_conflict_is_distinct(self, build_opener):
        secret = "conflict-body-secret"
        opener = self._open(
            side_effect=http_error(409, json.dumps({"error": {"code": "agent_id_conflict", "message": secret}}))
        )
        build_opener.return_value = opener
        with self.assertRaises(CursorAPIError) as caught:
            create_agent(KEY, REPO, "task", AGENT)
        self.assertTrue(caught.exception.conflict)
        self.assertEqual(caught.exception.status, 409)
        self.assertEqual(caught.exception.code, "agent_id_conflict")
        self.assertNotIn(secret, str(caught.exception))

    @patch("urllib.request.build_opener")
    def test_other_409_is_not_conflict(self, build_opener):
        opener = self._open(side_effect=http_error(409, json.dumps({"code": "something_else"})))
        build_opener.return_value = opener
        with self.assertRaises(CursorAPIError) as caught:
            create_agent(KEY, REPO, "task", AGENT)
        self.assertFalse(caught.exception.conflict)
        self.assertEqual(caught.exception.code, "something_else")

    @patch("urllib.request.build_opener")
    def test_unparsed_409_is_conflict(self, build_opener):
        opener = self._open(side_effect=http_error(409, b"not-json"))
        build_opener.return_value = opener
        with self.assertRaises(CursorAPIError) as caught:
            create_agent(KEY, REPO, "task", AGENT)
        self.assertTrue(caught.exception.conflict)

    @patch("urllib.request.build_opener")
    def test_transport_and_malformed_response(self, build_opener):
        opener = self._open(side_effect=urllib.error.URLError("dns secret " + KEY))
        build_opener.return_value = opener
        with self.assertRaises(CursorAPIError) as caught:
            create_agent(KEY, REPO, "task", AGENT)
        self.assertNotIn(KEY, str(caught.exception))
        self.assertIsNone(caught.exception.status)

        opener.open.side_effect = None
        opener.open.return_value = FakeResponse()
        opener.open.return_value.read = lambda *args: b"not-json " + KEY.encode()
        with self.assertRaises(CursorAPIError) as caught:
            create_agent(KEY, REPO, "task", AGENT)
        self.assertNotIn(KEY, str(caught.exception))

    @patch("urllib.request.build_opener")
    def test_mismatched_agent_id(self, build_opener):
        opener = self._open(
            payload={"agent": {"id": "bc-00000000-0000-0000-0000-000000000099"}, "run": {"id": "run-1", "agentId": AGENT}}
        )
        build_opener.return_value = opener
        with self.assertRaises(CursorAPIError) as caught:
            create_agent(KEY, REPO, "task", AGENT)
        self.assertFalse(caught.exception.conflict)

    @patch("urllib.request.build_opener")
    def test_unsafe_url_is_blanked(self, build_opener):
        opener = self._open(
            payload={
                "agent": {"id": AGENT, "url": "javascript:alert(1)"},
                "run": {"id": "run-1", "agentId": AGENT},
            }
        )
        build_opener.return_value = opener
        result = create_agent(KEY, REPO, "task", AGENT)
        self.assertEqual(result["agent"]["url"], "")

    def test_redirect_handler_does_not_leak_authorization(self):
        request = urllib.request.Request(CREATE_URL, headers={"Authorization": "Basic " + KEY})
        opener = urllib.request.build_opener(_RefuseRedirect)
        handlers = [handler for handler in opener.handlers if isinstance(handler, urllib.request.HTTPRedirectHandler)]
        self.assertEqual(len(handlers), 1)
        self.assertIsInstance(handlers[0], _RefuseRedirect)
        with self.assertRaises(CursorAPIError) as caught:
            handlers[0].redirect_request(request, None, 302, "Found", {}, "https://evil.example/steal")
        self.assertNotIn(KEY, str(caught.exception))
        self.assertIn("302", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
