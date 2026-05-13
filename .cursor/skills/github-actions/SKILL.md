---
name: github-actions
description: >-
  Helps author and debug GitHub Actions workflows (jobs, steps, secrets,
  matrices, caches, and permissions). Use when editing workflow YAML, fixing CI
  failures on GitHub, or when the user mentions GitHub Actions or workflow files.
paths:
  - ".github/workflows/**/*.yml"
  - ".github/workflows/**/*.yaml"
---

# GitHub Actions

## Editing workflows

- Prefer explicit `permissions:` at workflow or job level; default `GITHUB_TOKEN` permissions are narrow in newer repos.
- Pin third-party actions to full commit SHAs for supply-chain safety when the org expects it; otherwise use tagged versions the repo already uses.
- Keep secrets out of logs: avoid echoing env vars; use `::add-mask::` for dynamically generated secrets when needed.

## Debugging CI

- Read the failing job name and step; distinguish compile/test failures from infra (timeouts, rate limits, missing secrets).
- For `pull_request` from forks, remember secrets are not available to untrusted code unless using `pull_request_target` (avoid widening trust without team review).

## Structure

- One workflow file per concern when it reduces noise (e.g. `ci.yml`, `deploy.yml`).
- Reuse composite actions or reusable workflows only if the repo already does or the user asks for that refactor.
