#!/usr/bin/env python3
"""
Create a Jira ticket in the BT project following Bamboo's ticket convention.
Usage: python3 create_jira_ticket.py --help
"""
import os, sys, json, argparse, requests
from pathlib import Path

JIRA_BASE_URL = os.environ["JIRA_BASE_URL"].rstrip("/")
JIRA_AUTH = (os.environ["JIRA_USER_EMAIL"], os.environ["JIRA_API_TOKEN"])
HEADERS = {"Accept": "application/json", "Content-Type": "application/json"}
PROJECT_KEY = "BT"
PANDA_ACCOUNT_ID = "712020:6b24208b-9f08-40dd-b0f9-138194767aaa"

PRIORITY_MAP = {
    "highest": "Highest", "high": "High",
    "medium": "Medium", "low": "Low"
}

ISSUE_TYPE_MAP = {
    "bug": "Bug", "task": "Task", "story": "Story"
}


def text_to_adf(text: str) -> dict:
    """Convert plain markdown-ish text to Atlassian Document Format."""
    paragraphs = []
    for line in text.split("\n"):
        if line.startswith("## "):
            paragraphs.append({"type": "heading", "attrs": {"level": 2},
                                "content": [{"type": "text", "text": line[3:]}]})
        elif line.startswith("- [ ] ") or line.startswith("- [x] "):
            paragraphs.append({"type": "paragraph",
                                "content": [{"type": "text", "text": line}]})
        elif line.strip():
            paragraphs.append({"type": "paragraph",
                                "content": [{"type": "text", "text": line}]})
        else:
            paragraphs.append({"type": "paragraph", "content": []})
    return {"type": "doc", "version": 1, "content": paragraphs}


def create_ticket(summary: str, description: str, issue_type: str,
                  priority: str, requested_by: str) -> dict:
    full_description = f"Requested by: {requested_by}\n\n{description}"
    payload = {
        "fields": {
            "project": {"key": PROJECT_KEY},
            "summary": summary,
            "description": text_to_adf(full_description),
            "issuetype": {"name": ISSUE_TYPE_MAP.get(issue_type.lower(), "Task")},
            "priority": {"name": PRIORITY_MAP.get(priority.lower(), "Medium")},
            "assignee": {"accountId": PANDA_ACCOUNT_ID},
        }
    }
    r = requests.post(f"{JIRA_BASE_URL}/rest/api/3/issue",
                      auth=JIRA_AUTH, headers=HEADERS, json=payload)
    r.raise_for_status()
    return r.json()


def attach_file(issue_key: str, file_path: str) -> None:
    path = Path(file_path)
    if not path.exists():
        print(f"Warning: attachment not found: {file_path}", file=sys.stderr)
        return
    with open(path, "rb") as f:
        r = requests.post(
            f"{JIRA_BASE_URL}/rest/api/3/issue/{issue_key}/attachments",
            auth=JIRA_AUTH,
            headers={"X-Atlassian-Token": "no-check"},
            files={"file": (path.name, f)},
        )
        r.raise_for_status()
        print(f"  Attached: {path.name}")


def main():
    parser = argparse.ArgumentParser(description="Create a Jira ticket in BT project")
    parser.add_argument("--summary", required=True, help="Ticket title/summary")
    parser.add_argument("--description", required=True, help="Full description (markdown)")
    parser.add_argument("--type", default="Task", help="Bug | Task | Story")
    parser.add_argument("--priority", default="Medium", help="Highest | High | Medium | Low")
    parser.add_argument("--requested-by", required=True, help="@SlackName of requester")
    parser.add_argument("--attach", nargs="*", default=[], help="File paths to attach")
    args = parser.parse_args()

    print(f"Creating {args.type} ticket: {args.summary}")
    result = create_ticket(args.summary, args.description,
                           args.type, args.priority, args.requested_by)
    key = result["key"]
    url = f"{JIRA_BASE_URL}/browse/{key}"
    print(f"Created: {key}")
    print(f"URL: {url}")

    for f in args.attach:
        attach_file(key, f)

    return key, url


if __name__ == "__main__":
    main()
