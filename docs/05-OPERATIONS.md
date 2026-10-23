# Operations Runbook

## Daily review
Check GitHub Actions dispatcher results; GitHub issues with `agent-running`/`agent-blocked`; Cursor Agents dashboard; open PRs and CI.

## Dispatch blocked
Inspect the issue comment and Actions logs. Do not add `agent-approved` until verifying Cursor did not create a live agent for the recorded id. If an agent exists, reconcile its run and PR before retry. A workflow failure that leaves `agent-running` in place, with an `agent_id_conflict` comment, means the create call reported that the id already exists. Leave that label in place until the existing agent is reconciled.

## Dispatch red, issue still `agent-running`, no conflict comment
The create call returned before the GitHub comment was posted. Treat the agent as launched. Do not remove `agent-running` or approve the issue again until the Cursor dashboard shows no agent for that id.

## Cursor API 401/403
Verify account API entitlement, API key validity, repository connection and permissions. Never paste secrets into issues.

## Cursor API 429/5xx
Stop automatic retries; inspect provider dashboard and recorded deterministic agent ID. Retry only after reconciliation.

## Cursor agent finishes without PR
Inspect agent URL, branch and tests. Open a PR manually if safe, or create a follow-up task. Do not mark completed without evidence.

## Controlled end-to-end smoke test
Run this only after an operator with repository admin and Cursor access approves the spend. This repository cannot complete the live steps. Do not paste API keys, tokens, or `CURSOR_API_KEY` into issues, pull requests, or chat.

1. Confirm the repository is private, `main` rejects direct pushes and force pushes, the required status check is the `test` job from `MayanForge Foundry CI`, and auto-merge is off.
2. Confirm Cursor is connected to this repository and a cloud environment build has completed. Set an account spend limit before any live create.
3. Create labels `agent-approved`, `agent-running`, `agent-blocked`, and `agent-done`.
4. Store the Cursor key only as the Actions secret `CURSOR_API_KEY`. Set the repository variable `FOUNDRY_ENABLED` to `false`.
5. Open one trivial issue from `.github/ISSUE_TEMPLATE/agent-task.yml`. Include the heading text `Acceptance criteria`. Leave it unlabeled.
6. Run **MayanForge Foundry Dispatch** manually with `dry_run` checked (the default). The log should say there is no eligible issue. Confirm no Cursor agent was created.
7. Add `agent-approved` to the trivial issue. Run the workflow again with `dry_run` checked. The log should select that issue and must not change labels.
8. Set `FOUNDRY_ENABLED` to `true`. Run again with `dry_run` checked. Selection may repeat. Labels and Cursor must stay unchanged.
9. Run once with `dry_run` unchecked. Expect `agent-running`, an issue comment with the agent id, run id, and `https://cursor.com/agents/...` URL, a new branch, a pull request, and green CI. Merge only by a human review.
10. Shut the laptop off, or disconnect it, and confirm the cloud run continues from the Cursor dashboard.
11. Failure containment: dispatch one issue whose acceptance criteria are missing. It must be skipped. A live invalid-key check is optional and only safe when the working key remains stored outside the workflow run. Do not paste either key into an issue or chat. Unit tests cover a locally rejected key (issue stays `agent-approved`) and an HTTP 401 (issue moves to `agent-blocked`).
12. Duplicate guard: after a successful launch, add `agent-approved` again without removing `agent-running`. The next dispatch must skip that issue. Then remove `agent-running`, add `agent-approved`, and dispatch once. Expect HTTP 409 behavior: the issue ends on `agent-running`, the comment cites `agent_id_conflict`, and no second id is created. Record the agent URL and the workflow log.
13. Leave the schedule commented out until steps 9 through 12 have evidence.

Record the issue number, workflow run URL, agent URL, run id, pull request URL, CI URL, and the duplicate-dispatch log. Claims without those links are not verification.

## Incident shutdown
Set `FOUNDRY_ENABLED=false`, disable scheduled workflow, revoke key if compromised, audit changes and notify owner.

## Metrics to capture later
Issue-to-PR lead time, successful PR ratio, human rework hours, CI first-pass rate, cost per accepted issue, incidents and timeouts.
