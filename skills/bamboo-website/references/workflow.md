# Website Change Workflow — Operational Reference

**Full workflow (source of truth):** https://www.notion.so/Workflow-Website-Changes-v2-3264ce33e506815c9c98d8d4e9e3fc32

---

## Repository
- **Repo:** bamboo-io/bamboo-web
- **Clone:** `gh repo clone bamboo-io/bamboo-web`
- **Default branch:** master (no develop branch)
- **Branch naming:** `copy/description`, `feat/description`, `fix/description`
- **Always:** `git checkout master && git pull origin master` before branching

**To spin up locally:**
```bash
gh repo clone bamboo-io/bamboo-web
cd bamboo-web
npm install
npm run develop   # Gatsby dev server at http://localhost:8000
```

---

## Coding — Always Use Opus Sub-Agent

**Never implement code changes inline.** Always delegate to an Opus sub-agent:

```
sessions_spawn(
  runtime="subagent",
  model="anthropic/claude-opus-4-6",
  thinking="high",
  mode="run",
  runTimeoutSeconds=1800,
  label="website-change-{description}",
  task="<full task with context, files to change, branch name, PR instructions>"
)
```

Use Opus for:
- **Initial implementation** — making the requested change, branching, committing, raising the PR
- **Iterative changes** — any follow-up edits after preview review
- **All PR work** — always includes: checkout master, new branch, change, commit, push, gh pr create

The task passed to Opus must include:
- Exact repo path (cloned to /tmp/bamboo-web or similar)
- Branch name to use
- Precise description of what to change (extracted from Figma MCP where applicable)
- PR title and body template

---

## Figma MCP
- **Endpoint:** `http://127.0.0.1:3845/mcp` (Membrane remote proxy — configured in `~/.openclaw/workspace/config/mcporter.json`)
- Use for ALL website changes when a Figma link is provided
- File key: from Figma URL `figma.com/design/{FILE_KEY}/...`
- Node IDs: from URL `node-id=4358-58705` (convert `-` to `:` for API calls → `4358:58705`)
- Ask requester for specific node IDs or frame names if the link is too broad

---

## Netlify
- **Project:** silly-yeot-95c868
- **Preview URL:** `https://deploy-preview-{PR#}--silly-yeot-95c868.netlify.app`
- **Build time:** ~3–5 minutes after push
- **Prod deploy:** auto-triggers on master merge

## Merge
- **Command:** `gh pr merge <number> --repo bamboo-io/bamboo-web --squash --delete-branch --admin`
- **Approvers (Slack written confirmation = sufficient):**
  - Blake Cassidy (U0168B3B76D)
  - Tracey Plowman (U0223KBQL1K)
  - Deb Whincop (U06T6J8SY1G)
  - Kevin Upton (U07BC9AB82V)
- **No prod deploys Thursday or Friday**

## Who is Technical?
- Kevin Upton — technical
- Blake, Tracey, Deb — non-technical (plain language always)

## Common File Locations
- Features page: `src/pages/features/index.js`
- Homepage: `src/pages/index.js`
- Blog posts: `content/blog/`
- Images: `src/assets/images/`
