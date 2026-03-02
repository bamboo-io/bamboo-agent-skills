---
name: jira-ticket
description: Create Jira tickets (bugs, tasks, stories) in the BT project following Bamboo's ticket convention. Use when asked to create, file, or log a Jira ticket, issue, bug, or task. Ensures all required fields are populated — including Requested by, acceptance criteria, technical context, and how to test — so the ticket is immediately implementation-ready for a human dev or Panda. Attaches any provided files (screenshots, PDFs, specs) to the issue.
---

# jira-ticket

Create implementation-ready Jira tickets in the BT project following Bamboo's convention.

## Notion Template (source of truth)
https://www.notion.so/Convention-Jira-Ticket-Template-Requirements-3174ce33e5068122bc01c501f7cd1fc4

## Required Fields

Every ticket MUST include:

1. **Requested by** — `Requested by: @SlackName` at the top of the description
2. **Problem** — current behaviour vs expected behaviour + impact
3. **Acceptance Criteria** — testable bullets, always includes `Unit tests at 90%+ coverage of changed code`
4. **Technical Context** — service(s)/repo(s), relevant files, constraints, related tickets
5. **How to Test** — step-by-step QA instructions with environment and what to check
6. **Issue type** — Bug, Task, or Story
7. **Priority** — Highest / High / Medium / Low

If any required field is missing and cannot be inferred, ask before creating.

## Description Template

```
Requested by: @SlackName

## Problem
Current behaviour: 
Expected behaviour: 
Impact: 

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

## Out of Scope
- 
```

## Creating the Ticket

See `scripts/create_jira_ticket.py` for the full implementation. Key steps:

1. POST `/rest/api/3/issue` — create issue with ADF-formatted description
2. If files provided: POST `/rest/api/3/issue/{key}/attachments` with multipart/form-data and header `X-Atlassian-Token: no-check`, field name `file`
3. Print the resulting ticket URL: `$JIRA_BASE_URL/browse/{key}`

## Credentials
- `$JIRA_BASE_URL`, `$JIRA_USER_EMAIL`, `$JIRA_API_TOKEN` — already in environment
- Project: `BT`
- Panda accountId: `712020:6b24208b-9f08-40dd-b0f9-138194767aaa`

## After Creating
- Confirm ticket URL to the requester
- If Panda was asked to create it, note `Requested by: @TheirSlackName` in the description — this is the notify target when the ticket is worked on later
