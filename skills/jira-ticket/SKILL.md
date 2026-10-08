---
name: jira-ticket
description: Create Jira tickets (Task, Story, Bug, Spike) in the BT project following Bamboo's ticket convention. Use when asked to create, file, or log a Jira ticket, issue, bug, task, spike, or when a teammate describes something that should become a ticket. Always creates the ticket directly in Jira, populates every required field — Requested by, problem, acceptance criteria, technical context, how to test, labels, components, R&D flag — and attaches any provided files, so the ticket is immediately implementation-ready for a human dev or Panda.
---

# jira-ticket

Create implementation-ready Jira tickets in the BT project following Bamboo's convention.

When anyone asks to create a ticket, task, story, bug or spike — **always create it directly in Jira**. Never just post the ticket content back as text. The plain-text output format at the end is a fallback only if the Jira API is completely unavailable.

After creating the ticket, always reply with the link in the format
`https://bambooblockchain.atlassian.net/browse/<issue-key>`.

When given a description, produce a complete ticket immediately — no clarifying questions about the content. Do ask for the required fields (sprint, assignee, priority, epic) before creating; see Step 1.

## Notion Template (source of truth)
https://www.notion.so/Convention-Jira-Ticket-Template-Requirements-3174ce33e5068122bc01c501f7cd1fc4

## Core Principles

- **Precise, complete, structured.** QA and non-technical teammates must be able to act without follow-up.
- **Context ≠ Scope ≠ AC.** Each section has a distinct job. Never duplicate content across them.
- **Scope = what devs build. AC = what QA verifies.**

## Ticket Types

- **Task** — technical/functional work. Sections: context paragraph, Scope, Acceptance Criteria, Resources (optional).
- **Story** — user-facing feature from the user's perspective. Sections: user story sentence, General look (Figma), Pre-conditions, Scope, Acceptance Criteria.
- **Bug** — QA-reported defects. Sections: one-sentence title (What/Where/When), Description with steps to reproduce, Expected result, Actual result.
- **Spike** — investigation/research. ⚠️ **Whenever a ticket is for investigation, research or discovery, use issue type `Spike`, not `Task`.** Sections: context paragraph, Scope (what to investigate), Acceptance Criteria (what "done" looks like), Resources (optional).

Per-type templates, gold-standard examples and common mistakes: [references/templates.md](references/templates.md).

## Title Formats

- Task / Spike: `[Epic/Area] Short description of what needs to be done`
- Story: `[Module/Area] Short description of the user-facing feature`
- Bug: one sentence answering *What happened? Where? When?*

Start the description with a verb where it reads naturally (Add, Fix, Update, Remove, Migrate) and name the service when relevant: `[Round-ups] Fix roundup-pm fee calculation on zero-value trades`.

## Required Fields

Every ticket MUST include:

1. **Requested by** — `Requested by: @SlackName` at the top of the description
2. **Problem / context** — current behaviour vs expected behaviour + impact (the context paragraph of the type template)
3. **Scope** — what devs build, per the type template
4. **Acceptance Criteria** — testable bullets; for code changes always include `Unit tests at 90%+ coverage of changed code`
5. **Technical Context** — service(s)/repo(s), relevant files, constraints, related tickets
6. **How to Test** — step-by-step QA instructions with environment and what to check
7. **Issue type** — Task, Story, Bug or Spike
8. **Priority** — Highest / High / Medium / Low / Lowest
9. **Labels and components** — set autonomously (below)
10. **R&D field** — set autonomously (below)

If any required field is missing and cannot be inferred, ask before creating.

## Description Template (Task / Spike; Story and Bug follow references/templates.md)

```
Requested by: @SlackName

<Context paragraph: current state, the problem or opportunity, why now — 2–4 sentences, no heading>

## Scope of the task
1.
2.

## Acceptance Criteria
- [ ]
- [ ]
- [ ] Unit tests at 90%+ coverage of changed code

## Technical Context
Service(s):
Relevant files/functions:
Constraints:
Related:

## How to Test
1.
2.
3.

## Resources
-

## Out of Scope
-
```

## Creating the Ticket

### Step 1 — Ask for required fields before creating

Always ask for ALL of the following before creating:

- **Which sprint?** (required)
- **Assignee?** (required — always ask, never assume; "Panda" is a valid answer and maps to the Panda account below)
- **Priority?** (required — Highest / High / Medium / Low / Lowest)
- **Fix version / version?** (optional — a ticket can exist without one, but always remind the creator: > ⚠️ Don't forget to add the *Fix Version* to this ticket if it applies — it helps track which release this work belongs to.)
- **Parent epic?** — try to infer from context first; if unclear or not found, ask.

To find the right epic, search Jira:

```bash
curl -s "$JIRA_BASE_URL/rest/api/3/issue/picker?query=<keyword>&currentJQL=issuetype=Epic%20AND%20project=BT" \
  -u "$JIRA_USER_EMAIL:$JIRA_API_TOKEN" | jq '.sections[].issues[] | {key, summaryText}'
```

If no matching epic is found, ask the requester which epic it belongs to.

### Labels and components — set autonomously

Always set labels and components on the ticket. Do NOT ask the requester — derive them from the ticket content:

- Fetch available components: `GET /rest/api/3/project/BT/components`
- Labels: derive from content (e.g. `process-improvement`, `team-morale`, `mobile`)
  - ⚠️ **Back-end tasks: always use label `Back-End` (not `backend`)** — capitalisation matters
- Components: pick the best match from the available list (e.g. `Business_Analysis`, `Back-end`, `Front-end`, `qa`, `AQA`, `design`, `website`)
- If none fit well, ask the requester rather than leaving them blank.

### R&D field — set autonomously

Jira field `customfield_10445` ("R&D "). Option ids: YES = `10476`, NO = `10477`. Analyse the description and set it on creation:

- **YES** if the ticket fits the R&D criteria in the Notion methodology:
  - Core R&D: novel/experimental features, new technical approaches, proof-of-concept, architecture research
  - Supporting R&D: implementation, bug fixes or UI changes that *directly support* a Core R&D feature (work under R&D epics such as Basiq User ID Deletion, Open Banking/Reconnect, WABP, Stablecoin/USDC, Spread V2, Monorepo Foundation, CI/CD architecture, Hydration Service, Basiq Unbound)
  - Positive signals: "new approach", "research", "proof of concept", "architecture redesign", "new integration", "CI/CD", "monorepo", "hydration", "cloudfront", "caching", "USDC", "WABP", "round-ups", "stablecoin"
- **NO** if routine: standard bug fixes, UI copy changes, customer support tasks, operational maintenance, no R&D epic link
- **Borderline**: default to NO, add a ticket comment "⚠️ R&D field set to NO — please review if this ticket qualifies as R&D.", and notify Olia (see below): "⚠️ Borderline R&D ticket: *[BT-XXXX](https://bambooblockchain.atlassian.net/browse/BT-XXXX)* — [title]. R&D field set to NO but may qualify — please review manually."

### Step 2 — Create the issue

See `scripts/create_jira_ticket.py` for the full implementation (`--help` lists every flag). Key steps:

1. POST `/rest/api/3/issue` — create the issue with the ADF-formatted description, type, priority, labels, components, parent epic, R&D field and assignee
2. If files provided: POST `/rest/api/3/issue/{key}/attachments` with multipart/form-data and header `X-Atlassian-Token: no-check`, field name `file`
3. Add to the sprint (Step 3)
4. Print the resulting ticket URL: `$JIRA_BASE_URL/browse/{key}`

### Step 3 — Add to sprint via the Agile API

Do NOT set `customfield_10020` (sprint) on creation — it fails. Use the Agile API instead (the script does this with `--sprint`):

```bash
# Find the sprint id on the BT Scrum board (board id 21)
curl -s "$JIRA_BASE_URL/rest/agile/1.0/board/21/sprint?state=active,future" \
  -u "$JIRA_USER_EMAIL:$JIRA_API_TOKEN" | jq '[.values[] | {id, name, state}]'

# Then add the issue
curl -s -X POST "$JIRA_BASE_URL/rest/agile/1.0/sprint/<sprint_id>/issue" \
  -u "$JIRA_USER_EMAIL:$JIRA_API_TOKEN" -H "Content-Type: application/json" \
  -d '{"issues": ["<issue_key>"]}'
```

## Credentials (BT-specific values)

- `$JIRA_BASE_URL`, `$JIRA_USER_EMAIL`, `$JIRA_API_TOKEN` — already in environment
- Project: `BT`; BT Scrum board id: `21`
- Panda accountId: `712020:6b24208b-9f08-40dd-b0f9-138194767aaa`
- Custom fields: R&D `customfield_10445` (YES `10476` / NO `10477`); Backend Services Affected `customfield_10115`; story points `customfield_10031`

## After Creating

- Confirm the ticket URL to the requester.
- If Panda was asked to create it, note `Requested by: @TheirSlackName` in the description — this is the notify target when the ticket is worked on later.
- **Notify the PM when the ticket was created by someone other than her.** Olia Hryb (Slack `U06NF1DG1PW`) is the Project Manager. After successfully creating any ticket for a requester other than Olia (including Panda itself), tell her:
  > 🎫 New Jira ticket created: *[BT-XXXX](https://bambooblockchain.atlassian.net/browse/BT-XXXX)* — [ticket title] (created by [name/Panda])
  Send it as a Slack DM when a Slack tool is available in this session; otherwise @mention Olia in a comment on the new ticket with the same text. Do NOT notify if Olia herself created the ticket.

## Output Format (when the API is unavailable)

Present the ticket clearly as plain text so it can be pasted into Jira by hand:

```
Title: [Area] Description

Context:
...

Scope of the task:
1. ...
2. ...

Acceptance Criteria:
1. ...
2. ...

Resources (if any):
- ...
```
