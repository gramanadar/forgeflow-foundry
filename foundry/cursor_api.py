"""Minimal Cursor Cloud Agents API v1 adapter; no third-party dependencies."""
import base64
import json
import urllib.error
import urllib.request

BASE_URL = "https://api.cursor.com/v1"

class CursorAPIError(RuntimeError):
    pass

def create_agent(api_key, repo_url, prompt, agent_id, timeout=30):
    if not api_key or not repo_url.startswith("https://github.com/"):
        raise ValueError("Cursor key and GitHub HTTPS repository URL required")
    if not agent_id.startswith("bc-"):
        raise ValueError("agent_id must start with bc-")
    body = {
        "agentId": agent_id,
        "prompt": {"text": prompt},
        "repos": [{"url": repo_url, "startingRef": "main"}],
        "workOnCurrentBranch": False,
        "autoCreatePR": True,
    }
    encoded = json.dumps(body).encode("utf-8")
    auth = base64.b64encode((api_key + ":").encode()).decode()
    request = urllib.request.Request(
        BASE_URL + "/agents", data=encoded,
        headers={"Authorization": "Basic " + auth, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            result = json.load(response)
    except urllib.error.HTTPError as exc:
        # Do not expose server response, which may include sensitive details.
        raise CursorAPIError(f"Cursor API HTTP {exc.code}; reconcile before retry") from None
    except (urllib.error.URLError, TimeoutError) as exc:
        raise CursorAPIError("Cursor API transport error; reconcile before retry") from None
    if not isinstance(result, dict) or not isinstance(result.get("agent"), dict) or not isinstance(result.get("run"), dict):
        raise CursorAPIError("Unexpected Cursor response; reconcile before retry")
    return result
