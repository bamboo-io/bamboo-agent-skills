# Website Change Workflow — Reference

## Repository
- **Repo:** bamboo-io/bamboo-web
- **Default branch:** master (no develop branch)
- **Branch naming:** `copy/description-of-change`, `feat/description`, `fix/description`
- **Always:** `git checkout master && git pull origin master` before branching

## Netlify
- **Project:** silly-yeot-95c868
- **Preview URL format:** `https://deploy-preview-{PR#}--silly-yeot-95c868.netlify.app`
- **Build time:** ~3–5 minutes after push
- **Prod deploy:** auto-triggers when master is merged

## Merge Rules
- Slack written approval from any of the following is sufficient to merge — no GitHub PR review needed:
  - Blake Cassidy (U0168B3B76D)
  - Tracey Plowman (U0223KBQL1K)
  - Deb Whincop (U06T6J8SY1G)
  - Kevin Upton (U07BC9AB82V)
- Merge command: `gh pr merge <number> --repo bamboo-io/bamboo-web --squash --delete-branch --admin`
- **Only use --admin when written Slack approval is on record. Never bypass without it.**
- **No prod deploys Thursday or Friday.**

## Who is Technical?
- Kevin Upton — technical (CTO)
- Blake Cassidy — non-technical (marketing)
- Tracey Plowman — non-technical (marketing)
- Deb Whincop — non-technical (marketing)

When communicating with non-technical users: describe changes as what will look different on the website. No jargon.

## Workflow Channel
- **Primary channel:** #website-changes (Slack)
- **Notion workflow doc:** https://www.notion.so/Workflow-Website-Changes-3264ce33e506814facc3c1efd409d2d0

## Common File Locations
- Features page: `src/pages/features/index.js`
- Homepage: `src/pages/index.js`
- Content/blog posts: `content/blog/`
- Static images/assets: `src/assets/images/`
