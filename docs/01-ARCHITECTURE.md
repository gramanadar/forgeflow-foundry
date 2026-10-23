# Architecture Decision Record A-001 — ForgeFlow Foundry

## Mission and boundaries
ForgeFlow Foundry builds **ForgeFlow itself**. ForgeFlow Platform is the eventual product that builds customer software. Keep credentials, data, orchestration, lifecycle and deployments isolated. ForgeFlow Foundry must survive ForgeFlow Platform outages.

## Components
- **Planning:** human-approved roadmap/specifications stored as GitHub issues and repository documents.
- **Dispatch:** scheduled/manual GitHub Actions workflow, selects one `agent-approved` issue, validates issue content, marks it running, submits Cursor v1 agent.
- **Execution:** Cursor Cloud Agent in isolated environment, fresh branch, code/test iteration, PR handoff.
- **Verification:** independent GitHub Actions CI on PR, unit tests, static checks and later security scanners.
- **Governance:** protected main, mandatory review, no autonomous merge, no production credentials.
- **State:** GitHub issue labels/comments initially; durable DB and atomic leases later.

## Lifecycle
`draft → approved → running → PR-ready → reviewed → merged / blocked`.
Issue label is a convenience, **not** a security boundary. Dispatcher reads only issues with exact `agent-approved` label; action execution is gated by `FOUNDRY_ENABLED`.

## Non-goals in v0.1
Autonomous architecture approvals, multi-agent scheduling, unlimited retries, customer-project delivery, self-modifying deployment credentials, production deployment.

## Reliability decisions
- One dispatch at a time using GitHub Actions concurrency and one issue selected.
- Deterministic UUID-based Cursor `agentId` (`bc-` plus lowercase UUID v5). Current public docs say a repeat POST of that id returns HTTP 409 `agent_id_conflict` and does not replay the original create body. The dispatcher must not mint a replacement id. A 409 leaves the issue `agent-running`. Do not send `envVars` with a client-supplied id.
- A failed or ambiguous API launch is marked `agent-blocked` for operator recovery. A confirmed create that fails only while commenting on the issue stays `agent-running`.
- GitHub labels/comments are not atomic transactional storage; a future lease store is needed for parallelism.
- Keep API schema behind `foundry/cursor_api.py`; Cursor v1 is public beta.

## Future enhancements
Run polling via `/v1/agents/{id}/runs/{runId}` after confirming response schema; PR reconciliation; retry budget; spend telemetry; Slack/email reports; durable task DB; multiple workers; staged deployment.
