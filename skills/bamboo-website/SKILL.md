---
name: bamboo-website
description: Make changes to the Bamboo website (getbamboo.io). Use when someone asks to update, change, edit, fix, or add something to the website — including copy/text changes, image swaps, new sections, or new pages. Triggers include "update the website", "change the website", "website change", "edit the site", "fix the website copy", "add a section to the site", "update the homepage", or any request referencing getbamboo.io content.
---

# bamboo-website

Handles the full website change workflow: intake → plan → execute → preview → iterate → ship.

Full workflow details: see [references/workflow.md](references/workflow.md).

## Core Steps

### 1. Intake
Gather (ask if missing):
- Page URL on getbamboo.io
- Figma link with approved design/copy (if applicable)
- Type of change: copy edit / image swap / new section / new page
- What changes and why

### 2. Plan (always before touching code)
- Identify what files need changing and what will visually change on the site
- Write the plan in **plain, non-technical language** — no mention of branches, PRs, commits, or repos
- Post plan in Slack and **wait for written confirmation** before proceeding
- If anything is unclear or missing (e.g. no Figma link, ambiguous copy), ask before planning

### 3. Execute
- Make the change in the repo (see references/workflow.md for branch/repo details)
- Post in Slack: "Change is done — building the preview now, I'll send the link shortly"

### 4. Preview & Iterate
- Post the Netlify preview link in Slack once the build completes (~3–5 min)
- Tag the requester: "Here's the preview — let me know what you think"
- If changes needed: re-confirm the updated plan in plain language → confirm → make changes → new preview
- Repeat until requester is happy

### 5. Merge to Production
- Wait for written Slack approval from Blake, Tracey, Deb, or Kevin
- Merge using --admin override (bamboo-io/bamboo-web only)
- Confirm in Slack: "Done — the change is live on getbamboo.io 🐼"

## Key Rules
- **Plan first, always** — never execute without confirmed plan
- **Plain language** — Tracey, Deb, Blake are non-technical; describe changes as what they'll see, not what the code does
- **No prod deploys Thu/Fri**
- **Admin override** only with written Slack approval on record
