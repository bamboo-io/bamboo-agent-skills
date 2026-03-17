# Website Change Workflow — Operational Reference

**Full workflow (source of truth):** https://www.notion.so/Workflow-Website-Changes-3264ce33e506814facc3c1efd409d2d0

---

## Operational Details

**Repo:** bamboo-io/bamboo-web | Default branch: master
**Branch naming:** `copy/description`, `feat/description`, `fix/description`
**Always:** `git checkout master && git pull origin master` before branching

**Netlify project:** silly-yeot-95c868
**Preview URL:** `https://deploy-preview-{PR#}--silly-yeot-95c868.netlify.app`
**Merge command:** `gh pr merge <number> --repo bamboo-io/bamboo-web --squash --delete-branch --admin`

**Approvers (Slack written confirmation = sufficient to merge):**
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
