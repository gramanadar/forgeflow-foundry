# Delivery Roadmap

## A0 — Groundwork (human setup)
Private repo, branch rules, Cursor GitHub connection, Cloud Agent environment, API key, spend limits.

## A1 — Single-task cloud execution (provided starter)
GitHub issue template, label-gated dispatch, Cursor v1 adapter, CI, audit comments, dry-run. **Not accepted until live smoke test.**

## A2 — Run monitor
Implement persisted run IDs, poll documented Get Run endpoint, reconcile Cursor statuses and PRs, report stalled runs. Tests: success, failure, timeout, unknown, API 429.

## A3 — Repair controller
Bounded 1–2 follow-up runs on failed tests, never modify acceptance criteria, stop on exhausted budget. Tests: no infinite loops.

## A4 — Operational hardening
Atomic lease DB, cost telemetry, notifications, provider outage circuit breaker, audit events, secret rotation runbook.

## A5 — Parallel backlog execution
Dependency graph, risk-based scheduling, independent review agents, isolated branches, max parallelism and budgets.

## System B kickoff
Only after A1 end-to-end proof: start ForgeFlow Core v0.1 (requirements capture, architecture artifacts, review gates). System A and B remain separate.
