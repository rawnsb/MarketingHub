---
name: github-issues
description: >-
  Writes clear GitHub issues, repro steps, acceptance criteria, and links work
  to branches or PRs. Use when filing bugs, planning tasks, triaging reports,
  or when the user mentions GitHub issues, bug reports, or feature requests.
---

# GitHub issues

## Goals

- Issues should be actionable: someone can pick them up without guessing intent.
- Bugs include repro, expected vs actual, and environment when relevant.

## Bug report template

```markdown
## Summary
[One sentence]

## Steps to reproduce
1.
2.

## Expected
[What should happen]

## Actual
[What happens instead]

## Environment
- OS / browser / version (if applicable)
- App version or commit SHA if known

## Logs / screenshots
[Paste or attach]
```

## Feature / task template

```markdown
## Problem / motivation
[User or business need]

## Proposed solution
[High-level approach]

## Acceptance criteria
- [ ]
- [ ]

## Out of scope
[Optional: what this issue is not doing]
```

## Linking work

- Reference related PRs with full URLs or `owner/repo#123` when helpful.
- Use closing keywords in PR descriptions when appropriate (`Fixes #123`, `Closes #123`).

## Labels and routing

- Suggest labels only when they match conventions visible in the repo (existing labels, CONTRIBUTING, or team docs).
- If severity or priority is unclear, ask once instead of inventing a process.
