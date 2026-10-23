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
6. Add GitHub repository variable `SYSTEM_A_ENABLED=false` and secret `CURSOR_API_KEY`.
7. Run dispatcher workflow manually in dry-run; ensure only approved issues are selected.
8. Set variable true; manually launch a trivial issue. Verify agent URL, PR, CI, human review.
9. Test failure and duplicate-dispatch scenarios before enabling scheduled execution.

## User-controlled actions
Repository creation, GitHub/Cursor connection, API key, spending limits, repo rulesets and live launch need your authorization and cannot be completed by these files alone.
