# Research and Validation Register

Audit date: 2026-10-22 (Pacific). No live Cursor Cloud Agents call was made. No API key was present in this workspace, and none was requested.

## Official documentation checked

- Cursor Cloud Agents API endpoints, read 2026-10-22: https://cursor.com/docs/cloud-agent/api/endpoints
- Cursor Cloud Agents API overview, same contract family: https://cursor.com/docs/cloud-agent/api/overview
- Cursor APIs authentication and rate-limit overview: https://cursor.com/docs/api
- Cursor staff note on `startingRef` commit SHAs: https://forum.cursor.com/t/cloud-agents-api-v1-post-v1-agents-returns-validation-error-for-documented-request/168179
- GitHub CLI `gh api` manual and current `cli/cli` trunk `pkg/cmd/api/api.go`, `http.go`, and `fields.go`
- GitHub Actions workflow syntax, including `permissions`, `concurrency`, and `workflow_dispatch` inputs: https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions
- GitHub Actions security hardening: https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions
- GitHub REST API versions: https://docs.github.com/en/rest/about-the-rest-api/api-versions
- GitHub REST list-issues reference for API version `2022-11-28`: https://docs.github.com/en/rest/issues/issues?apiVersion=2022-11-28

`https://cursor.com/docs/cloud-agent/api/openapi.json` returned HTTP 500. The machine-readable OpenAPI file was not available, so request and error fields below come from the prose endpoint page and its examples.

## Validation matrix

| Check | Evidence | Result |
|---|---|---|
| Create URL and auth | Endpoint page and https://cursor.com/docs/api | `POST https://api.cursor.com/v1/agents`. Basic auth is the API key as the username and an empty password. Bearer is also documented. The adapter sends Basic and does not log the header. |
| Create body | Endpoint examples | `prompt.text`, `repos[].url`, `repos[].startingRef`, `autoCreatePR`, `workOnCurrentBranch`, `mode`. Client `agentId` cannot be combined with `envVars`. The adapter sends `mode: agent`, `workOnCurrentBranch: false`, `autoCreatePR: true`, `startingRef: main`, and omits `envVars`. |
| Idempotency | Endpoint page, `agentId` field | A repeat POST of the same `bc-` UUID returns **409 `agent_id_conflict`**. It does not return the original `agent` and `run` body. The dispatcher keeps `agent-running` on that status and does not mint a new id. |
| Branch safety | `workOnCurrentBranch` description | `false` pushes a new `cursor/...` branch from `startingRef`. `true` pushes to `startingRef` itself. The adapter sends `false`. |
| `startingRef` | Endpoint page plus Cursor staff forum reply | A branch name is the documented example. A full commit SHA is accepted only when that commit is on the default branch or a same-repo pull request. This repo sends the branch name `main`, which is not a pin. |
| Error body | Prose codes only | The adapter reads at most 4096 bytes, accepts a safe `code` token, and puts only the HTTP status and that token in errors and issue comments. Response messages are dropped. |
| Redirects | Adapter policy | Redirects are refused so the API key is not sent to another host. The public docs do not promise a redirect-free create call. |
| Issue list | GitHub REST `2022-11-28` and `gh api` source | Default sort is `created` descending and the page size max is 100. `gh api -f` becomes POST unless `--method GET` is set; current trunk then copies those fields onto the query string. The dispatcher now sends an explicit GET query with `direction=asc`, `per_page=100`, and `X-GitHub-Api-Version: 2022-11-28`. |
| Label race | GitHub label REST and `gh issue edit` history | Add and remove are separate calls. There is no compare-and-swap. The dispatcher adds `agent-running`, re-reads the issue, then removes `agent-approved`, and skips issues that already have `agent-running`, `agent-blocked`, or `agent-done`. Pull requests are skipped. The workflow token does not have `pull-requests: write`. |
| Actions boolean input | Workflow syntax docs | `inputs.dry_run` is a boolean. `github.event.inputs.dry_run` is the string `true` or `false`. The workflow assigns the string form to `DRY_RUN`. The process treats only that string `false` as a live run. |
| Token scope | Actions permissions docs | `write` includes `read`. Unspecified scopes are `none`. Dispatch grants `contents: read` and `issues: write`. CI grants `contents: read`. `CURSOR_API_KEY` is set on the dispatch step only. Checkout uses `persist-credentials: false`. |
| Concurrency | Actions concurrency docs | `cancel-in-progress: false` leaves the running dispatch alone. The default queue mode `single` still replaces an older pending run. That limits stacked launches. |
| Local tests | `python3 -m unittest discover -s tests -v` | 33 tests, OK. `python3 -m compileall -q foundry`, OK. No network call to `api.cursor.com`. |

## Corrected contract note

The previous register said a client `agentId` makes create retries idempotent. The current endpoint page is more specific: the duplicate POST is a **409**, not a replay of the first 200 response. The dispatcher follows that description. Whether this Cursor account returns that status is unverified.

## Not verified in this account

- Cursor API entitlement, billing, quota, spend limit, and GitHub repository connection.
- A real `POST /v1/agents` response, including the 409 JSON shape. The code accepts either a top-level `code`, `error.code`, or a non-JSON 409 body as `agent_id_conflict`. Any other parsed 409 code is a failure.
- That `agent.id` in a success body equals the client-supplied id. The adapter requires that match and will mark the issue blocked if it does not.
- That every run id matches `[A-Za-z0-9_-]{1,128}`. Examples use a `run-` prefix; the adapter does not require the prefix.
- That `startingRef: main` exists. The connected repository must use `main` as the branch the agent should fork from. A branch name resolves to HEAD at start time.
- `autoCreatePR: true` opening a pull request, and the default reviewer request that happens because `skipReviewerRequest` is omitted.
- GitHub Actions permission enforcement, rulesets, and required checks on the user's repository.
- `github.event.inputs.dry_run` on a real workflow run. The string behavior is from the workflow syntax docs.
- API version `2026-03-10`. Calls pin `2022-11-28`, the version whose issue-list parameters were read and the version GitHub uses when the header is absent. Support for `2022-11-28` currently runs through March 10, 2028.
- Actions major tags `actions/checkout@v4` and `actions/setup-python@v5`. `docs/03-SECURITY.md` still defers immutable SHA pinning for this starter.
- `GET /v1/agents/{id}` and `GET /v1/agents/{id}/runs/{runId}`. Run monitoring stays out of scope until a live schema check.
- Default model selection and account spend limits. The create body omits `model`.

## Design caveats

Cursor API v1 is public beta. GitHub labels are not a transaction. One page of 100 oldest `agent-approved` issues is the selection window; older invalid issues inside that page can occupy slots. Workflow concurrency covers this workflow file only. A second workflow with another concurrency group can still race, which is why the label re-read and the 409 path both exist.

Live smoke steps are in `docs/05-OPERATIONS.md`. Do not enable a schedule until those steps have evidence.
