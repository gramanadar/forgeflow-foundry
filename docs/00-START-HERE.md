# Operator Setup Checklist

## Prerequisites
- Private GitHub repository and administrator access.
- Cursor account with Cloud Agents API access and connected GitHub repo.
- Cursor API key stored only as GitHub Actions secret `CURSOR_API_KEY`.
- GitHub CLI `gh` available in GitHub Actions; workflow `GITHUB_TOKEN` has `issues:write` and `contents:read` only.

## Setup order
1. Review architecture and security documents; do not copy production secrets into Cursor.
2. Commit this package on `main`; configure required CI check and prohibit direct pushes/force pushes; disable auto-merge.
3. In Cursor dashboard, connect source control, choose repo, configure environment, run initial Build.
4. Verify `AGENTS.md` and tests are accessible in the Cloud Agent VM.
5. Create labels: `agent-approved`, `agent-running`, `agent-blocked`, `agent-done`.
6. Add GitHub repository variable `FOUNDRY_ENABLED=false` and secret `CURSOR_API_KEY`.
7. Run the dispatcher workflow manually with `dry_run` left at its default. The workflow passes that boolean through `github.event.inputs.dry_run`, which is the string `true` or `false`. Only the string `false` leaves dry-run mode.
8. Set `FOUNDRY_ENABLED` true and follow `docs/05-OPERATIONS.md` for the controlled smoke test. Verify the agent URL, pull request, CI, and human review.
9. Exercise the failure and duplicate-dispatch checks in that runbook before enabling a schedule. A create conflict leaves `agent-running` in place and records `agent_id_conflict`.

## User-controlled actions
Repository creation, GitHub/Cursor connection, API key, spending limits, repo rulesets and live launch need your authorization and cannot be completed by these files alone.
