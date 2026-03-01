# bamboo-agent-skills

Monorepo of skills for Panda 🐼 — Bamboo's internal AI.

Each skill lives in `skills/{skill-name}/` and contains a `SKILL.md` (instructions for the agent) and supporting scripts.

## Skills

| Skill | Description |
|-------|-------------|
| [reconnect-service](skills/reconnect-service/) | Reconnect a Bamboo event listener service that's stuck in ERROR state |

## Usage

Skills are loaded by the OpenClaw agent when a task matches the skill description. See individual `SKILL.md` files for usage.
