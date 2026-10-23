# Prompt to paste into Cursor Cloud Agent

You are the lead engineer for ForgeFlow **System A** (the development factory that builds ForgeFlow itself, not the customer-facing System B). First read README.md, AGENTS.md, docs/00-START-HERE.md, docs/01-ARCHITECTURE.md, docs/02-REQUIREMENTS.md, docs/03-SECURITY.md and docs/06-RESEARCH-VALIDATION.md.

Task: audit this starter repository against current official Cursor Cloud Agents API v1 and GitHub Actions documentation. Run all existing tests. Fix confirmed defects and add tests. Pay special attention to the dispatcher GitHub CLI API request, idempotency, issue-label race conditions, error handling, input validation, credentials, and GitHub Actions permissions. Do not assume that documented API behavior has been validated in our account. Do not execute a live Cursor API call or spend money without explicit approval. Do not merge or deploy.

Deliver a PR with a validation matrix, exact commands and results, list of unverified integration assumptions, and an operator checklist for a controlled end-to-end smoke test. If you need credentials or administrative setup, stop and report the blocker; do not ask for secrets in chat or commit them.
