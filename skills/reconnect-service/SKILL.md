# Skill: reconnect-service

Reconnect a Bamboo event listener service that is stuck in ERROR state.

## Usage

When asked to reconnect or restart a service (e.g. "reconnect payment-domain in sandbox-au"):

```bash
python3 ~/Projects/bamboo-agent-skills/skills/reconnect-service/reconnect.py <service> <env>

# Dry run first to confirm state
python3 ~/Projects/bamboo-agent-skills/skills/reconnect-service/reconnect.py <service> <env> --dry-run

# Examples
python3 ~/Projects/bamboo-agent-skills/skills/reconnect-service/reconnect.py payment-domain sandbox-au
python3 ~/Projects/bamboo-agent-skills/skills/reconnect-service/reconnect.py recurring-pm develop-au
python3 ~/Projects/bamboo-agent-skills/skills/reconnect-service/reconnect.py payment-domain prod-au
```

## Prerequisites

- AWS SSO active: `aws sso login --profile sso` (lasts ~8h)
- `boto3` installed: `pip3 install boto3`

## Environments

| Env | AWS Profile | Account |
|-----|-------------|---------|
| sandbox-au / sandbox-us | bamboo.sandbox | 385936341354 |
| develop-au / develop-us | bamboo.develop | 337387902522 |
| prod-au / prod-us | bamboo.production | 053651923274 |

## What it does

1. Finds the ListenerState DynamoDB table for the service
2. Confirms status is ERROR and gets the errorSequenceId
3. Advances sequenceId past the bad event (sets status → STREAMING)
4. Re-attaches the Streamer lambda to the DynamoDB event stream

## Safety

- Always dry-run first unless urgent
- Production environments require typing 'yes' to confirm
- bamboo.production is ReadOnly — reconnect will fail on prod (requires escalation)

## After reconnecting

Reply in the #broken-services / #broken-services-dev thread with the result.
DM Kevin (U07BC9AB82V), Anton (U0471TYBJM6), Bibek G (U05QN7VBU5N) that it's been reconnected.
