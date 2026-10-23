# System A Requirements & Acceptance

| ID | Requirement | Acceptance |
|---|---|---|
| A-FR-001 | Only explicitly approved issues may dispatch | Unapproved issue is ignored |
| A-FR-002 | Laptop independence | Cloud agent runs after local laptop disconnects |
| A-FR-003 | Every task carries acceptance criteria | Missing criteria rejected |
| A-FR-004 | Cloud execution isolated | Agent works on new branch, not main |
| A-FR-005 | CI validates submitted changes | PR runs independent CI |
| A-FR-006 | Human controls merge | Protected main requires review |
| A-FR-007 | Track dispatched run | Issue comment records agent/run IDs and URL |
| A-FR-008 | Prevent duplicate scheduling | Label transition and workflow concurrency; test serial runs |
| A-NFR-001 | Least privilege | Actions token scoped; API key secret |
| A-NFR-002 | Cost control | One task/run and external provider spending cap |
| A-NFR-003 | Failure visibility | Failed dispatch moves to blocked, no hidden loop |
| A-NFR-004 | Reproducibility | Repo tests run without paid credentials |

## Exit criteria v0.1
One approved trivial issue → Cursor creates branch/PR → GitHub CI green → human reviews. Repeat once after laptop shutdown. Demonstrate failure containment and duplicate avoidance.

## Evidence policy
Each PR must contain issue link, changed files, tests executed, results, risks and screenshots where UI changes. Claims without logs are not verification.
