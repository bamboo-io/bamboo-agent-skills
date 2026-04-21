# Skill: bamboo-app

Use when asked to make frontend changes, create branches, or raise PRs
in the bamboo-app (bamboo-io/bamboo-app) React Native codebase.

## Before touching any code

1. Read `CLAUDE.md` in the repo root — it is the source of truth for all
   conventions in this codebase. Always follow it.

2. Branch naming: `<type>/BT-XXXX-short-description`

   | Type     | When                       |
   |----------|----------------------------|
   | `feat/`  | New feature                |
   | `fix/`   | Bug fix                    |
   | `chore/` | Tooling, config, refactor  |

## Stack

- React Native CLI (not Expo)
- TypeScript
- MobX — all state, API calls, business logic
- React Navigation

## Key rules (from CLAUDE.md)

- Functional components only
- No inline styles — use `StyleSheet.create()`
- No hardcoded colours/spacing — use tokens from `styles/`
- No API calls from components — stores only
- No magic strings — use `redesignRoot/constants/`
- Always create/update a test file when you change logic
- Run lint and tests after changes: `npm run lint && npm run test`

## After raising a PR

Post a message to the `#bamboo-pr` Slack channel with:
- A short summary of the changes made
- The PR link

## After a PR is merged

1. Find the Jira ticket assigned to the PR author in the current sprint
2. Add a comment to that ticket with a short bullet list of changes made
   (max 10 points, concise and specific)

## PR checklist

- [ ] Branch named correctly (`<type>/BT-XXXX-...`)
- [ ] No inline styles
- [ ] No hardcoded values
- [ ] Test file created/updated
- [ ] Lint passes
- [ ] PR description includes: what changed, why, ticket reference
- [ ] `#bamboo-pr` Slack message sent with summary + PR link
- [ ] Jira ticket comment added after merge (max 10 points)
