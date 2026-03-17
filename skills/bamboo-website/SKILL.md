---
name: bamboo-website
description: Make changes to the Bamboo website (getbamboo.io). Use when someone asks to update, change, edit, fix, or add something to the website — copy edits, image swaps, new sections, new pages. Triggers: "update the website", "change the website", "website change", "edit the site", "fix the copy", "add a section", "update the homepage", or any request about getbamboo.io content.
---

# bamboo-website

Walk the requester through the full website change journey. Be proactive at every stage — don't wait to be asked, send updates before they have to check in.

Full workflow (source of truth): https://www.notion.so/Workflow-Website-Changes-v2-3264ce33e506815c9c98d8d4e9e3fc32
Operational details: see references/workflow.md

---

## Stage 1 — Intake

Acknowledge the request warmly. Check what you have:

**Need all of these — ask for anything missing:**
- Page URL (e.g. getbamboo.io/features)
- Figma link with the approved design (ask for specific node IDs if the link is broad)
- Type of change: text update / image swap / new section / new page
- What's changing and why

If a Figma link is provided, read it immediately via the Figma MCP (see references/workflow.md). Extract the exact copy, layout, and intent before planning.

---

## Stage 2 — Plan (confirm before touching anything)

Write the plan in plain language — describe what will visually change on the website. No code terms, no jargon.

**Say something like:**
> "Here's what I'll do: on the Features page, I'll change the heading from 'X' to 'Y'. That's the only change. Does that sound right?"

Wait for written confirmation. If anything is unclear, ask — don't guess.

---

## Stage 3 — Execute

Make the change. Then immediately message:
> "Done — I'm building a preview of the change now. I'll send you the link in a few minutes."

Wait for the Netlify build (~3–5 min), then post:
> "Here's your preview: [link] — head to the [page name] page to see the change. Let me know what you think!"

Tag the requester by name.

---

## Stage 4 — Iteration Loop

If changes are needed:
1. Summarise the new request in plain language
2. Confirm it's understood: "So I'll change X to Y — is that right?"
3. Wait for confirmation
4. Make the change, post a new preview link
5. Repeat until the requester is happy

Each loop: restate the plan clearly, get sign-off, execute, preview.

---

## Stage 5 — Ship to Production

Once the requester is happy, ask for explicit approval:
> "Looks great! Happy for me to push this live to getbamboo.io?"

On written approval from Blake, Tracey, Deb, or Kevin → merge using --admin (see references/workflow.md).

Confirm when live:
> "All done — the change is live on getbamboo.io 🐼"

---

## Hard Rules
- Never execute without a confirmed plan
- No prod deploys Thursday or Friday
- --admin override only with written Slack approval on record
- Plain language always with non-technical users (Blake, Tracey, Deb)
