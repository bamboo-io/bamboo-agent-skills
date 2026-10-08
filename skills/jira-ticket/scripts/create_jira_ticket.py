#!/usr/bin/env python3
"""
Create a Jira ticket in the BT project following Bamboo's ticket convention.
Usage: python3 create_jira_ticket.py --help

Creates the issue (type, priority, labels, components, parent epic, R&D flag,
assignee), attaches files, then adds it to a sprint through the Agile API —
the sprint field cannot be set on creation. Prints the ticket URL.
"""
import os, sys, json, argparse, requests
from pathlib import Path

JIRA_BASE_URL = os.environ["JIRA_BASE_URL"].rstrip("/")
JIRA_AUTH = (os.environ["JIRA_USER_EMAIL"], os.environ["JIRA_API_TOKEN"])
HEADERS = {"Accept": "application/json", "Content-Type": "application/json"}

# ---- BT-specific values (keep in sync with SKILL.md "Credentials") ----------
PROJECT_KEY = "BT"
BOARD_ID = 21                       # BT Scrum board
PANDA_ACCOUNT_ID = "712020:6b24208b-9f08-40dd-b0f9-138194767aaa"
RD_FIELD = "customfield_10445"      # "R&D "
RD_OPTIONS = {"yes": "10476", "no": "10477"}

PRIORITY_MAP = {
    "highest": "Highest", "high": "High",
    "medium": "Medium", "low": "Low", "lowest": "Lowest",
}

ISSUE_TYPE_MAP = {
    "bug": "Bug", "task": "Task", "story": "Story", "spike": "Spike",
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
                  priority: str, requested_by: str, assignee: str,
                  labels: list, components: list, epic: str, rd: str) -> dict:
    full_description = f"Requested by: {requested_by}\n\n{description}"
    fields = {
        "project": {"key": PROJECT_KEY},
        "summary": summary,
        "description": text_to_adf(full_description),
        "issuetype": {"name": ISSUE_TYPE_MAP.get(issue_type.lower(), "Task")},
        "priority": {"name": PRIORITY_MAP.get(priority.lower(), "Medium")},
    }
    if assignee:
        fields["assignee"] = {"accountId": PANDA_ACCOUNT_ID if assignee.lower() == "panda" else assignee}
    if labels:
        fields["labels"] = labels
    if components:
        fields["components"] = [{"name": c} for c in components]
    if epic:
        fields["parent"] = {"key": epic}
    if rd:
        fields[RD_FIELD] = [{"id": RD_OPTIONS[rd.lower()]}]
    r = requests.post(f"{JIRA_BASE_URL}/rest/api/3/issue",
                      auth=JIRA_AUTH, headers=HEADERS, json={"fields": fields})
    if not r.ok:
        print(f"Jira rejected the issue: {r.status_code} {r.text}", file=sys.stderr)
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


def list_sprints() -> list:
    r = requests.get(f"{JIRA_BASE_URL}/rest/agile/1.0/board/{BOARD_ID}/sprint",
                     params={"state": "active,future"}, auth=JIRA_AUTH, headers=HEADERS)
    r.raise_for_status()
    return [{"id": s["id"], "name": s["name"], "state": s["state"]} for s in r.json().get("values", [])]


def add_to_sprint(issue_key: str, sprint: str) -> None:
    """sprint = numeric id, or a (case-insensitive) sprint name on the board."""
    sprint_id = None
    if sprint.isdigit():
        sprint_id = int(sprint)
    else:
        for s in list_sprints():
            if s["name"].lower() == sprint.lower():
                sprint_id = s["id"]
                break
    if sprint_id is None:
        print(f"Warning: no active/future sprint named '{sprint}' on board {BOARD_ID}; "
              f"available: {[s['name'] for s in list_sprints()]}", file=sys.stderr)
        return
    r = requests.post(f"{JIRA_BASE_URL}/rest/agile/1.0/sprint/{sprint_id}/issue",
                      auth=JIRA_AUTH, headers=HEADERS, json={"issues": [issue_key]})
    r.raise_for_status()
    print(f"  Added to sprint {sprint_id}")


def main():
    parser = argparse.ArgumentParser(description="Create a Jira ticket in the BT project")
    parser.add_argument("--summary", required=True, help="Ticket title/summary")
    parser.add_argument("--description", required=True, help="Full description (markdown)")
    parser.add_argument("--type", default="Task", help="Bug | Task | Story | Spike")
    parser.add_argument("--priority", default="Medium", help="Highest | High | Medium | Low | Lowest")
    parser.add_argument("--requested-by", required=True, help="@SlackName of requester")
    parser.add_argument("--assignee", default="panda",
                        help="Jira accountId, or 'panda'; pass '' to leave unassigned")
    parser.add_argument("--label", action="append", default=[], help="Label (repeatable). Back-end work: Back-End")
    parser.add_argument("--component", action="append", default=[], help="Component name (repeatable)")
    parser.add_argument("--epic", default="", help="Parent epic key, e.g. BT-242")
    parser.add_argument("--rd", default="", choices=["", "yes", "no"],
                        help="R&D field (customfield_10445): yes | no")
    parser.add_argument("--sprint", default="", help="Sprint id or name on the BT Scrum board (board 21)")
    parser.add_argument("--list-sprints", action="store_true", help="Print active/future sprints and exit")
    parser.add_argument("--attach", nargs="*", default=[], help="File paths to attach")
    args = parser.parse_args()

    if args.list_sprints:
        print(json.dumps(list_sprints(), indent=2))
        return

    print(f"Creating {args.type} ticket: {args.summary}")
    result = create_ticket(args.summary, args.description, args.type, args.priority,
                           args.requested_by, args.assignee, args.label, args.component,
                           args.epic, args.rd)
    key = result["key"]
    url = f"{JIRA_BASE_URL}/browse/{key}"
    print(f"Created: {key}")
    print(f"URL: {url}")

    for f in args.attach:
        attach_file(key, f)
    if args.sprint:
        add_to_sprint(key, args.sprint)

    return key, url


if __name__ == "__main__":
    main()
