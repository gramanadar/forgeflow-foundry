"""Minimal Cursor Cloud Agents API v1 adapter. No third-party dependencies.

The create call is not retried. A client-supplied agent id is a duplicate
guard: current public docs say a repeat POST returns HTTP 409
``agent_id_conflict`` and does not replay the original response. This module
does not send ``envVars``, which those docs forbid alongside a client id.
"""
import base64
import json
import re
import urllib.error
import urllib.request

BASE_URL = "https://api.cursor.com/v1"
CREATE_URL = BASE_URL + "/agents"

# Published examples use lowercase ``bc-`` plus a UUID. This is the client
# constraint; the live service was not called.
_AGENT_ID = re.compile(
    r"bc-[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\Z"
)
_REPO_URL = re.compile(r"https://github\.com/([A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?)/([A-Za-z0-9_.-]{1,100})\Z")
_API_KEY = re.compile(r"[\x21-\x7E]+\Z")
_SAFE_CODE = re.compile(r"[A-Za-z0-9_]{1,80}\Z")
_SAFE_TOKEN = re.compile(r"[A-Za-z0-9_-]{1,128}\Z")
_SAFE_AGENT_URL = re.compile(r"https://cursor\.com/agents/[A-Za-z0-9_-]{1,128}\Z")
# Local cap. The public create-agent page does not publish a prompt.text maximum.
MAX_PROMPT_CHARS = 20000


class CursorAPIError(RuntimeError):
    def __init__(self, message, *, status=None, code=None, conflict=False):
        super().__init__(message)
        self.status = status
        self.code = code
        self.conflict = conflict


class _RefuseRedirect(urllib.request.HTTPRedirectHandler):
    """Do not follow redirects. A redirect would move the API key to another URL."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise CursorAPIError(
            f"Cursor API HTTP {code} redirect; reconcile before retry",
            status=code,
        )


def valid_api_key(api_key):
    """True for a single-line token that Basic auth will not split on ':'."""
    if not isinstance(api_key, str) or not _API_KEY.fullmatch(api_key):
        return False
    if ":" in api_key:
        return False
    return True


def valid_agent_id(agent_id):
    return isinstance(agent_id, str) and bool(_AGENT_ID.fullmatch(agent_id))


def valid_github_repo_url(repo_url):
    if not isinstance(repo_url, str) or repo_url.endswith(".git"):
        return False
    match = _REPO_URL.fullmatch(repo_url)
    if not match:
        return False
    owner, name = match.group(1), match.group(2)
    if name in {".", ".."}:
        return False
    return True


def _error_code(raw):
    try:
        payload = json.loads(raw.decode("utf-8", errors="replace"))
    except (UnicodeError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict):
        return None
    code = payload.get("code")
    if not isinstance(code, str):
        error = payload.get("error")
        if isinstance(error, dict):
            code = error.get("code")
    if isinstance(code, str) and _SAFE_CODE.fullmatch(code):
        return code.lower()
    return None


def _http_error(exc):
    raw = b""
    try:
        raw = exc.read(4096) or b""
    except (OSError, UnicodeError, ValueError):
        raw = b""
    code = _error_code(raw)
    status = getattr(exc, "code", None)
    conflict = status == 409 and (code is None or code == "agent_id_conflict")
    if conflict:
        message = "Cursor API HTTP 409 agent_id_conflict; agent already exists; reconcile before retry"
        return CursorAPIError(message, status=409, code="agent_id_conflict", conflict=True)
    label = f" {code}" if code else ""
    status_text = status if isinstance(status, int) else "unknown"
    return CursorAPIError(
        f"Cursor API HTTP {status_text}{label}; reconcile before retry",
        status=status,
        code=code,
        conflict=False,
    )


def _validated_result(result, agent_id):
    if not isinstance(result, dict):
        raise CursorAPIError("Unexpected Cursor response; reconcile before retry")
    agent = result.get("agent")
    run = result.get("run")
    if not isinstance(agent, dict) or not isinstance(run, dict):
        raise CursorAPIError("Unexpected Cursor response; reconcile before retry")
    if agent.get("id") != agent_id:
        raise CursorAPIError("Unexpected Cursor response; reconcile before retry")
    run_id = run.get("id")
    if not isinstance(run_id, str) or not _SAFE_TOKEN.fullmatch(run_id):
        raise CursorAPIError("Unexpected Cursor response; reconcile before retry")
    run_agent = run.get("agentId", agent_id)
    if run_agent != agent_id:
        raise CursorAPIError("Unexpected Cursor response; reconcile before retry")
    url = agent.get("url")
    if url is None:
        url = ""
    if not isinstance(url, str) or (url and not _SAFE_AGENT_URL.fullmatch(url)):
        cleaned = dict(result)
        cleaned_agent = dict(agent)
        cleaned_agent["url"] = ""
        cleaned["agent"] = cleaned_agent
        return cleaned
    return result


def create_agent(api_key, repo_url, prompt, agent_id, timeout=30):
    if not valid_api_key(api_key):
        raise ValueError("Cursor API key must be a single-line token without ':'")
    if not valid_github_repo_url(repo_url):
        raise ValueError("Cursor repository URL must be https://github.com/owner/repo")
    if not valid_agent_id(agent_id):
        raise ValueError("agent_id must be bc- followed by a lowercase UUID")
    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("prompt text required")
    if len(prompt) > MAX_PROMPT_CHARS:
        raise ValueError("prompt exceeds dispatcher limit")
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or timeout <= 0:
        raise ValueError("timeout must be positive")
    body = {
        "agentId": agent_id,
        "prompt": {"text": prompt},
        "repos": [{"url": repo_url, "startingRef": "main"}],
        "workOnCurrentBranch": False,
        "autoCreatePR": True,
        "mode": "agent",
    }
    encoded = json.dumps(body).encode("utf-8")
    auth = base64.b64encode((api_key + ":").encode("ascii")).decode("ascii")
    request = urllib.request.Request(
        CREATE_URL,
        data=encoded,
        headers={"Authorization": "Basic " + auth, "Content-Type": "application/json"},
        method="POST",
    )
    opener = urllib.request.build_opener(_RefuseRedirect)
    try:
        with opener.open(request, timeout=timeout) as response:
            raw = response.read()
    except CursorAPIError:
        raise
    except urllib.error.HTTPError as exc:
        raise _http_error(exc) from None
    except (urllib.error.URLError, TimeoutError, OSError):
        raise CursorAPIError("Cursor API transport error; reconcile before retry") from None
    try:
        result = json.loads(raw.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError, AttributeError):
        raise CursorAPIError("Unexpected Cursor response; reconcile before retry") from None
    return _validated_result(result, agent_id)
