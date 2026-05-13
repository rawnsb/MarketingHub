---
name: github-pull-requests
description: >-
  Drafts and refines GitHub pull requests, titles, descriptions, and review
  feedback using conventional commits and clear risk notes. Use when opening
  or updating a PR, preparing a merge, reviewing a diff on GitHub, or when the
  user mentions pull requests, merge requests, or code review before merge.
---

# GitHub pull requests

## Goals

- Make PRs easy to review: intent, scope, testing, and rollout risks are obvious.
- Match conventional commit style for titles when the repo uses it.

## PR title

- Prefer `type(scope): short summary` (examples: `feat`, `fix`, `chore`, `docs`, `refactor`, `test`).
- Keep the summary imperative and under ~72 characters when possible.

## PR description template

Use this structure unless the project already defines a template in `.github`:

```markdown
## Summary
[What changed and why in 1–3 sentences]

## How to test
[Commands, URLs, or checklist steps]

## Risk / rollout
[Data migrations, feature flags, permissions, or anything that could break prod]

## Screenshots (if UI)
[Optional]

## Checklist
- [ ] Tests added or updated (or N/A with reason)
- [ ] Migrations safe for existing data (or N/A)
```

## Review feedback

- Group comments: blocking issues first, then suggestions, then nits.
- Tie feedback to files or behaviors; propose concrete fixes when obvious.
- If CI failed, reference the failing job or log excerpt when summarizing for the author.

## Before merge

- Confirm the branch is up to date with the base branch when merge conflicts are likely.
- Note if `squash` vs `merge` commit strategy affects the final message.
