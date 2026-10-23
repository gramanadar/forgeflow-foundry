# Research and Validation Register — 2026-10-22

## Official documentation checked
- Cursor Cloud Agents: https://cursor.com/docs/cloud-agent — cloud VMs, GitHub integration, branches, no laptop required.
- Cursor Cloud Environment Setup: https://cursor.com/docs/cloud-agent/setup — setup, `.cursor/environment.json`, AGENTS.md, secrets, builds.
- Cursor Cloud Agents API v1: https://prod.cursor.com/docs/cloud-agent/api/endpoints — POST `/v1/agents`, `prompt.text`, `repos[].url`, `startingRef`, `agentId`, `autoCreatePR`, response `agent` and `run`.
- Cursor security/network: https://prod.cursor.com/docs/cloud-agent/security-network — cloud execution, network, Git permissions.
- GitHub Actions documentation: https://docs.github.com/en/actions — schedules, workflow_dispatch, concurrency, token permissions.
- GitHub security hardening: https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions

## Validated from published docs
- Cursor cloud agents can operate without local laptop connectivity.
- Cursor API v1 uses Basic/Bearer auth and is public beta.
- Create Agent accepts client-supplied `agentId` as `bc-<uuid>` for idempotency, but cannot combine with envVars.
- Cursor can create a PR with `autoCreatePR=true`.
- GitHub Actions supports manually triggered and scheduled jobs.

## Not yet validated live
- User's Cursor API access, connected repository, billing and quota.
- Real API request/response with user credentials.
- GitHub branch protection / Actions permissions in user's repository.
- Successful cloud environment Build and actual PR.
- Run-monitor endpoint compatibility; intentionally not implemented in starter.

## Design caveats
Cursor v1 public beta may change. GitHub issue labels are weak transactional storage. Live smoke tests are mandatory before unattended schedules.
