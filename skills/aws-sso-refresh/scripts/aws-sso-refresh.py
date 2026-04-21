#!/usr/bin/env python3
"""
AWS SSO Proactive Refresh — Panda 🐼

Keeps all AWS SSO profiles continuously authenticated by checking token
expiry and re-authing before they lapse.

Profiles (all share the same SSO session):
  - bamboo.sandbox        (385936341354)
  - bamboo.develop        (337387902522)
  - bamboo.production     (053651923274, ReadOnly)
  - bamboo.production-reconnect (053651923274, ReconnectService)

Usage:
    python3 aws-sso-refresh.py            # Check + refresh if needed
    python3 aws-sso-refresh.py --check    # Report token status only
    python3 aws-sso-refresh.py --force    # Force re-auth regardless of expiry
"""

import argparse
import glob
import json
import logging
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone, timedelta

SLACK_ALERT_CHANNEL = "C0AJBTRLRJA"  # #infrastructure

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

SSO_CACHE_DIR = os.path.expanduser("~/.aws/sso/cache")
LOG_DIR = os.path.expanduser("~/.openclaw/workspace/logs")
LOG_FILE = os.path.join(LOG_DIR, "aws-sso-refresh.log")

# All profiles sharing the same SSO session
PROFILES = [
    "bamboo.sandbox",
    "bamboo.develop",
    "bamboo.production",
    "bamboo.production-reconnect",
]

# Profile to use for the single re-auth call (refreshes session for all)
PRIMARY_PROFILE = "bamboo.production"

# Re-auth if token expires within this many hours
EXPIRY_BUFFER_HOURS = 3

# How long to wait for browser-based SSO confirmation (seconds)
BROWSER_WAIT_SECONDS = 20

# Max retries for the browser auth flow
MAX_AUTH_RETRIES = 2

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

os.makedirs(LOG_DIR, exist_ok=True)

log = logging.getLogger("aws-sso-refresh")
log.setLevel(logging.DEBUG)

# File handler
fh = logging.FileHandler(LOG_FILE)
fh.setLevel(logging.DEBUG)
fh.setFormatter(logging.Formatter(
    "%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
))
log.addHandler(fh)

# Console handler
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(logging.Formatter(
    "%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
))
log.addHandler(ch)

# ---------------------------------------------------------------------------
# Token inspection
# ---------------------------------------------------------------------------

def get_sso_token_info():
    """
    Parse SSO cache files and return info about the access token.
    Returns dict with keys: found, expires_at, expires_in, file_path
    or None if no valid token found.
    """
    cache_files = glob.glob(os.path.join(SSO_CACHE_DIR, "*.json"))
    if not cache_files:
        log.warning("No SSO cache files found in %s", SSO_CACHE_DIR)
        return None

    for fpath in cache_files:
        try:
            with open(fpath) as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            log.debug("Skipping %s: %s", fpath, e)
            continue

        # The actual SSO session token has accessToken + startUrl
        if "accessToken" not in data or "startUrl" not in data:
            continue

        expires_str = data.get("expiresAt", "")
        if not expires_str:
            continue

        try:
            # AWS SSO cache uses ISO 8601 format (always UTC)
            # Handle both "Z" suffix and "+00:00" and bare (assumed UTC)
            expires_str = expires_str.replace("Z", "+00:00")
            if "+" not in expires_str and "-" not in expires_str[10:]:
                expires_str += "+00:00"
            expires_at = datetime.fromisoformat(expires_str)
        except ValueError:
            log.warning("Could not parse expiresAt '%s' in %s", expires_str, fpath)
            continue

        now = datetime.now(timezone.utc)
        expires_in = expires_at - now

        return {
            "found": True,
            "expires_at": expires_at,
            "expires_in": expires_in,
            "file_path": fpath,
        }

    log.warning("No SSO access token found in cache files")
    return None


def check_profile_credentials(profile):
    """
    Try `aws sts get-caller-identity --profile <profile>`.
    Returns (success: bool, identity: str or error: str).
    """
    try:
        result = subprocess.run(
            ["/usr/local/bin/aws", "sts", "get-caller-identity", "--profile", profile],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0:
            try:
                identity = json.loads(result.stdout)
                arn = identity.get("Arn", "unknown")
                return True, arn
            except json.JSONDecodeError:
                return True, result.stdout.strip()
        else:
            return False, result.stderr.strip()
    except subprocess.TimeoutExpired:
        return False, "timeout"
    except Exception as e:
        return False, str(e)


# ---------------------------------------------------------------------------
# Re-authentication
# ---------------------------------------------------------------------------

def sso_reauth(profile=PRIMARY_PROFILE):
    """
    Re-authenticate AWS SSO using the browser-based flow.

    1. Run `aws sso login --profile <profile> --no-browser` to get the auth URL
    2. Open it with `open` (macOS) — OpenClaw browser handles confirmation
    3. Wait for the flow to complete
    4. Verify with sts get-caller-identity
    """
    log.info("Starting SSO re-auth via profile '%s'...", profile)

    for attempt in range(1, MAX_AUTH_RETRIES + 1):
        log.info("Auth attempt %d/%d", attempt, MAX_AUTH_RETRIES)

        # Start the SSO login process (non-blocking, captures URL+code)
        proc = subprocess.Popen(
            ["/usr/local/bin/aws", "sso", "login", "--profile", profile, "--no-browser"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            env={**os.environ, "PATH": "/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"},
        )

        url = None
        output_lines = []

        # Read output to find the verification URL
        for line in proc.stdout:
            stripped = line.rstrip()
            output_lines.append(stripped)
            log.debug("sso-login: %s", stripped)

            if not url:
                m = re.search(r"(https://\S+user_code=\S+)", line)
                if m:
                    url = m.group(1)

        proc.wait()

        # If login succeeded immediately (token was still valid), we're done
        if proc.returncode == 0:
            log.info("SSO login succeeded (token was still valid or refreshed)")
            return True

        # If we got a URL, open it in the browser for confirmation
        if url:
            log.info("Opening SSO verification URL in browser...")
            log.debug("URL: %s", url)

            try:
                # Try to open in default browser (works when run interactively)
                subprocess.Popen(["/usr/bin/open", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception as e:
                log.debug("Could not auto-open browser: %s", e)
            
            # Also send Slack DM to Kevin with the auth URL (backup notification)
            try:
                subprocess.run([
                    "openclaw", "message", "send",
                    "--channel", "slack",
                    "--target", "U07BC9AB82V",  # Kevin Upton
                    "--message", f"🐼 *AWS SSO Auth Needed*\nOpening device auth flow...\nURL: {url}"
                ], timeout=10, check=False)
            except Exception as slack_err:
                log.debug("Could not send Slack notification: %s", slack_err)

            # Wait for the browser flow to complete
            log.info("Waiting %ds for browser confirmation...", BROWSER_WAIT_SECONDS)
            time.sleep(BROWSER_WAIT_SECONDS)

            # Verify the auth worked
            ok, result = check_profile_credentials(profile)
            if ok:
                log.info("SSO re-auth succeeded via browser — %s", result)
                return True
            else:
                log.warning("Verification failed after browser flow: %s", result)
                if attempt < MAX_AUTH_RETRIES:
                    log.info("Retrying in 5 seconds...")
                    time.sleep(5)
        else:
            log.error("No verification URL found in SSO login output")
            for line in output_lines:
                log.error("  > %s", line)

    log.error("SSO re-auth failed after %d attempts", MAX_AUTH_RETRIES)
    return False


# ---------------------------------------------------------------------------
# Main logic
# ---------------------------------------------------------------------------

def report_status():
    """Report current SSO token status and profile credential validity."""
    log.info("=" * 60)
    log.info("AWS SSO Token Status Report")
    log.info("=" * 60)

    # Check SSO token
    token_info = get_sso_token_info()
    if token_info:
        expires_at = token_info["expires_at"]
        expires_in = token_info["expires_in"]
        total_seconds = int(expires_in.total_seconds())

        if total_seconds <= 0:
            status = "EXPIRED"
        elif total_seconds < EXPIRY_BUFFER_HOURS * 3600:
            status = "EXPIRING SOON"
        else:
            status = "VALID"

        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60

        log.info("SSO Token: %s", status)
        log.info("  Expires at: %s", expires_at.strftime("%Y-%m-%d %H:%M:%S UTC"))
        if total_seconds > 0:
            log.info("  Expires in: %dh %dm", hours, minutes)
        else:
            log.info("  Expired: %dh %dm ago", abs(hours), abs(minutes))
    else:
        log.info("SSO Token: NOT FOUND")

    # Check each profile
    log.info("-" * 40)
    all_ok = True
    for profile in PROFILES:
        ok, detail = check_profile_credentials(profile)
        mark = "✅" if ok else "❌"
        log.info("  %s %s — %s", mark, profile, detail)
        if not ok:
            all_ok = False

    log.info("=" * 60)
    return all_ok, token_info


def run(force=False, check_only=False):
    """Main entry point."""
    log.info("🐼 AWS SSO Refresh — %s", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    if check_only:
        all_ok, _ = report_status()
        return 0 if all_ok else 1

    # Check token expiry
    token_info = get_sso_token_info()
    needs_refresh = force

    if force:
        log.info("Force mode — will re-auth regardless of expiry")
    elif token_info is None:
        log.warning("No SSO token found — need to authenticate")
        needs_refresh = True
    else:
        expires_in = token_info["expires_in"]
        total_seconds = int(expires_in.total_seconds())
        buffer_seconds = EXPIRY_BUFFER_HOURS * 3600

        if total_seconds <= 0:
            log.warning("SSO token is EXPIRED — need to re-auth")
            needs_refresh = True
        elif total_seconds < buffer_seconds:
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            log.info(
                "SSO token expires in %dh %dm (< %dh buffer) — refreshing",
                hours, minutes, EXPIRY_BUFFER_HOURS,
            )
            needs_refresh = True
        else:
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            log.info(
                "SSO token valid for %dh %dm — no refresh needed",
                hours, minutes,
            )

    if not needs_refresh:
        # Still verify all profiles can resolve credentials
        log.info("Verifying all profiles can resolve credentials...")
        all_ok = True
        for profile in PROFILES:
            ok, detail = check_profile_credentials(profile)
            if ok:
                log.info("  ✅ %s — %s", profile, detail)
            else:
                log.warning("  ❌ %s — %s", profile, detail)
                all_ok = False
                needs_refresh = True

        if not needs_refresh:
            log.info("All profiles healthy — nothing to do")
            return 0

        log.info("Some profiles failed credential check — triggering re-auth")

    # Perform re-auth
    if not sso_reauth(PRIMARY_PROFILE):
        log.error("❌ SSO re-auth failed")
        return 1

    # Verify all profiles after re-auth
    log.info("Verifying all profiles after re-auth...")
    all_ok = True
    for profile in PROFILES:
        ok, detail = check_profile_credentials(profile)
        if ok:
            log.info("  ✅ %s — %s", profile, detail)
        else:
            log.error("  ❌ %s — %s", profile, detail)
            all_ok = False

    if all_ok:
        log.info("✅ All profiles authenticated successfully")
        return 0
    else:
        log.error("❌ Some profiles failed verification after re-auth")
        return 1


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="AWS SSO Proactive Refresh — keeps all profiles authenticated"
    )
    parser.add_argument(
        "--check", action="store_true",
        help="Report token status without re-authenticating",
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Force re-auth regardless of token expiry",
    )
    args = parser.parse_args()

    try:
        exit_code = run(force=args.force, check_only=args.check)
    except Exception as e:
        log.error("Unhandled error: %s", e, exc_info=True)
        exit_code = 1

    if exit_code != 0 and not args.check:
        # Alert Kevin on failure
        try:
            subprocess.run([
                "openclaw", "message", "send",
                "--channel", "slack",
                "--target", "U07BC9AB82V",  # Kevin Upton
                "--message", f"⚠️ AWS SSO Refresh Failed 🐼\nProactive SSO refresh failed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}. All AWS scripts may fail until this is resolved.\n\nCheck logs: `tail -50 ~/.openclaw/workspace/logs/aws-sso-refresh.log`"
            ], timeout=30, check=False)
        except Exception as alert_err:
            log.warning("Failed to send Slack DM to Kevin: %s", alert_err)

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
