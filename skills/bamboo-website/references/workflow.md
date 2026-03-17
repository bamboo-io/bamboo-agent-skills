# Website Change Workflow — Operational Reference

**Full workflow (source of truth):** https://www.notion.so/Workflow-Website-Changes-3264ce33e506814facc3c1efd409d2d0

---

## Figma MCP (use this first)
A Figma MCP is available at `http://127.0.0.1:3845/mcp` (configured in `~/.openclaw/workspace/config/mcporter.json`).

**Always use the Figma MCP when a Figma link is provided.** It allows reading the design file directly — inspect layers, read exact copy, check dimensions, and understand the intended design before writing any code.

Typical use:
- Get the Figma file key from the URL (e.g. `ovFN5HFH3ANiq9pDKNHtf6` from `figma.com/design/ovFN5HFH3ANiq9pDKNHtf6/...`)
- Use the MCP to read the specific node (node-id from URL `node-id=4358-58705`)
- Extract the exact copy, styles, and layout from the design
- Ask the requester for specific node IDs or frame names if the Figma link is too broad to navigate

The MCP removes the need to ask the requester to describe what they want in detail — read it from the design file directly.

---

## Repository
- **Repo:** bamboo-io/bamboo-web | Default branch: master
- **Branch naming:** `copy/description`, `feat/description`, `fix/description`
- **Always:** `git checkout master && git pull origin master` before branching

## Netlify
- **Project:** silly-yeot-95c868
- **Preview URL:** `https://deploy-preview-{PR#}--silly-yeot-95c868.netlify.app`
- **Merge command:** `gh pr merge <number> --repo bamboo-io/bamboo-web --squash --delete-branch --admin`

## Approvers (Slack written confirmation = sufficient to merge)
- Blake Cassidy (U0168B3B76D)
- Tracey Plowman (U0223KBQL1K)
- Deb Whincop (U06T6J8SY1G)
- Kevin Upton (U07BC9AB82V)

**Technical users:** Kevin only. Blake, Tracey, Deb are non-technical — plain language always.
**No prod deploys Thu/Fri.**

## Common File Locations
- Features page: `src/pages/features/index.js`
- Homepage: `src/pages/index.js`
- Blog posts: `content/blog/`
- Images: `src/assets/images/`
