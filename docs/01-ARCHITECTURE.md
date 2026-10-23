# Architecture Decision Record A-001 — System A

## Mission and boundaries
System A builds **ForgeFlow itself**. System B is the eventual product that builds customer software. Keep credentials, data, orchestration, lifecycle and deployments isolated. System A must survive System B outages.

## Components
- **Planning:** human-approved roadmap/specifications stored as GitHub issues and repository documents.
- **Dispatch:** scheduled/manual GitHub Actions workflow, selects one `agent-approved` issue, validates issue content, marks it running, submits Cursor v1 agent.
- **Execution:** Cursor Cloud Agent in isolated environment, fresh branch, code/test iteration, PR handoff.
- **Verification:** independent GitHub Actions CI on PR, unit tests, static checks and later security scanners.
- **Governance:** protected main, mandatory review, no autonomous merge, no production credentials.
- **State:** GitHub issue labels/comments initially; durable DB and atomic leases later.

## Lifecycle
`draft → approved → running → PR-ready → reviewed → merged / blocked`.
Issue label is a convenience, **not** a security boundary. Dispatcher reads only issues with exact `agent-approved` label; action execution is gated by `SYSTEM_A_ENABLED`.

## Non-goals in v0.1
Autonomous architecture approvals, multi-agent scheduling, unlimited retries, customer-project delivery, self-modifying deployment credentials, production deployment.

## Reliability decisions
- One dispatch at a time using GitHub Actions concurrency and one issue selected.
- Deterministic UUID-based Cursor `agentId` for idempotent create retries; no envVars with this mode.
- A failed API launch is marked blocked for operator recovery; never silently retry with a different ID.
- GitHub labels/comments are not atomic transactional storage; a future lease store is needed for parallelism.
- Keep API schema behind `system_a/cursor_api.py`; Cursor v1 is public beta.

## Future enhancements
Run polling via `/v1/agents/{id}/runs/{runId}` after confirming response schema; PR reconciliation; retry budget; spend telemetry; Slack/email reports; durable task DB; multiple workers; staged deployment.
