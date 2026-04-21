---
name: aws-sso-refresh
description: Refresh AWS SSO credentials for all Bamboo profiles. Use when AWS API calls start failing with authentication errors, before running long-running scripts that require AWS access, or to proactively check SSO token health. Handles all four Bamboo profiles (sandbox, develop, production, production-reconnect) which share a single SSO session.
---

# AWS SSO Refresh

Keeps all Bamboo AWS profiles authenticated via a shared SSO session.

## Profiles

| Profile | Account ID | Notes |
|---|---|---|
| `bamboo.sandbox` | 385936341354 | |
| `bamboo.develop` | 337387902522 | |
| `bamboo.production` | 053651923274 | ReadOnly |
| `bamboo.production-reconnect` | 053651923274 | ReconnectService role |

All four profiles share the same SSO session. A single re-auth refreshes all of them.

## Usage

Run the script at `scripts/aws-sso-refresh.py`:

```bash
# Check token status + verify all profiles (no re-auth)
python3 aws-sso-refresh.py --check

# Refresh if token is within 3h of expiry (default mode)
python3 aws-sso-refresh.py

# Force re-auth regardless of expiry
python3 aws-sso-refresh.py --force
```

## Auth Flow

When a refresh is needed:
1. Script runs `aws sso login --profile bamboo.production --no-browser`
2. Extracts the device verification URL from stdout
3. Opens it in the default browser (`open <url>`)
4. Sends a Slack DM to Kevin (U07BC9AB82V) with the URL as backup
5. Waits 20 seconds for browser confirmation
6. Verifies all profiles with `aws sts get-caller-identity`

**Kevin must approve the device auth** in the browser (or via the Slack link). The script cannot complete the flow autonomously.

## Logs

`~/.openclaw/workspace/logs/aws-sso-refresh.log`

## Failure Handling

On failure, the script auto-DMs Kevin on Slack with the error. If AWS calls are still failing after a successful auth, check that the correct profile is being used in the failing script.
