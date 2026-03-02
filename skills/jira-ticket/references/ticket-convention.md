# Bamboo Jira Ticket Convention

Source of truth: https://www.notion.so/Convention-Jira-Ticket-Template-Requirements-3174ce33e5068122bc01c501f7cd1fc4

## Readiness Checklist
Before creating, confirm:
- [ ] Requested by is known
- [ ] Current vs expected behaviour is clear
- [ ] Acceptance criteria are testable
- [ ] At least one service/repo identified
- [ ] How to test has clear steps

## Attachment Types
- Screenshots — broken UI, error dialogs, Datadog/CloudWatch graphs
- Figma / design files — screens, flows, component specs
- PDFs — product specs, API docs, business requirements
- Log files / stack traces — paste inline if short, attach as .txt if long
- CSV / JSON — sample data, test payloads, event examples

## Ticket Title Conventions
- Start with a verb: Add, Fix, Update, Remove, Migrate
- Include service name when relevant: `Fix roundup-pm fee calculation on zero-value trades`

## Priority Guidelines
- **Highest** — production outage or data loss
- **High** — broken feature affecting users, no workaround
- **Medium** — degraded feature, workaround exists
- **Low** — improvement, nice-to-have, tech debt

## Project
Always use project key: `BT`
