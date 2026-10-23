# Operations Runbook

## Daily review
Check GitHub Actions dispatcher results; GitHub issues with `agent-running`/`agent-blocked`; Cursor Agents dashboard; open PRs and CI.

## Dispatch blocked
Inspect issue comment and Actions logs. Do not add `agent-approved` until verifying Cursor did not create a live agent. If an agent exists, reconcile its run and PR before retry.

## Cursor API 401/403
Verify account API entitlement, API key validity, repository connection and permissions. Never paste secrets into issues.

## Cursor API 429/5xx
Stop automatic retries; inspect provider dashboard and recorded deterministic agent ID. Retry only after reconciliation.

## Cursor agent finishes without PR
Inspect agent URL, branch and tests. Open a PR manually if safe, or create a follow-up task. Do not mark completed without evidence.

## Incident shutdown
Set `FOUNDRY_ENABLED=false`, disable scheduled workflow, revoke key if compromised, audit changes and notify owner.

## Metrics to capture later
Issue-to-PR lead time, successful PR ratio, human rework hours, CI first-pass rate, cost per accepted issue, incidents and timeouts.
