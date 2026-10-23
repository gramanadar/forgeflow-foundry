# MayanForge Foundry — Autonomous Development Factory

**Purpose:** Build MayanForge Platform using external cloud coding agents. This is NOT MayanForge's customer software-delivery runtime.

## Naming
| Component | Name |
|---|---|
| Company / product | MayanForge |
| Customer-facing platform | MayanForge Platform |
| Autonomous development infrastructure (this repo) | MayanForge Foundry |
| Internal GitHub repository | `mayanforge-foundry` |
| Platform GitHub repository | `mayanforge-platform` |
| Engineering agents | MayanForge Agents |

## What this package is
A versioned implementation specification plus a minimal, safe-by-default GitHub Actions dispatcher and Cursor Cloud Agents v1 API adapter. **Not a deployed service.** Live Cursor/GitHub integration requires your accounts and an end-to-end smoke test.

## Start here
1. Read `docs/00-START-HERE.md`, `docs/01-ARCHITECTURE.md`, `docs/03-SECURITY.md` and `AGENTS.md`.
2. Create a private GitHub repo; upload these files. Enable branch protection / rulesets for `main` (manual GitHub settings).
3. Connect the repo in Cursor Cloud Agents; complete its environment setup and verify it can run `python -m unittest discover -s tests -v`.
4. Add repository secret `CURSOR_API_KEY` and variable `FOUNDRY_ENABLED=false` (leave disabled until ready).
5. Create an issue using the template and label it `agent-approved` only after reviewing the specification.
6. Run the workflow manually with `dry_run=true` and inspect logs. When the smoke test is ready, set `FOUNDRY_ENABLED=true`, and manually run with `dry_run=false`.
7. Do not enable scheduled dispatch until a live end-to-end run creates a PR, CI passes, and recovery has been exercised.

## Local verification
```bash
python -m unittest discover -s tests -v
python -m compileall -q foundry
python -m foundry.dispatcher --help
```
No third-party Python packages required for dispatcher.

## Source of truth
- `docs/`: architecture, scope, security, validation, runbooks, roadmap.
- `engineering/tasks/`: implementation-ready milestones.
- GitHub Issues: approved task queue. PRs: delivery artifacts.
- `AGENTS.md`: repository-wide Cursor agent operating instructions.

## Current limits
The dispatcher submits **one** approved issue per run, marks it in progress, and records agent and run ids in an issue comment. A repeated create for the same issue reuses the same `bc-` UUID. Current public Cursor docs describe that repeat as HTTP 409 `agent_id_conflict`, so the issue stays `agent-running` for reconciliation. This is not yet a production-grade scheduler, cost meter, notification service, or recovery controller. Cursor API v1 is public beta. The live smoke test in `docs/05-OPERATIONS.md` is still required before any schedule.


## Original project references

The `reference/` directory contains the original AI software delivery platform blueprint (`ai_software_delivery_platform_blueprint.html`) and the MayanForge website prototype (`mayanforge_site_index.html`). These are reference artifacts for building MayanForge Foundry and ultimately MayanForge Platform; they are not themselves implemented application services.
