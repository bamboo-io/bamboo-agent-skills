#!/usr/bin/env python3
"""
reconnect.py — Reconnect a Bamboo event listener service stuck in ERROR state.

Usage:
  python3 reconnect.py <service> <env> [--dry-run]

Examples:
  python3 reconnect.py payment-domain sandbox-au
  python3 reconnect.py recurring-pm develop-au --dry-run
"""

import sys
import argparse
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

ENV_PROFILES = {
    "sandbox-au": "bamboo.sandbox", "sandbox-us": "bamboo.sandbox", "sandbox": "bamboo.sandbox",
    "develop-au": "bamboo.develop", "develop-us": "bamboo.develop", "develop": "bamboo.develop",
    "prod-au": "bamboo.production", "prod-us": "bamboo.production", "prod": "bamboo.production",
}
REGION = "ap-southeast-2"
EVENT_STORE_STREAMS = {
    "sandbox":    "arn:aws:dynamodb:ap-southeast-2:385936341354:table/event-repo-EventStore165FCE28-KLTJQLLUH6K3/stream/2020-07-20T10:01:57.355",
    "sandbox-au": "arn:aws:dynamodb:ap-southeast-2:385936341354:table/event-repo-EventStore165FCE28-KLTJQLLUH6K3/stream/2020-07-20T10:01:57.355",
    "sandbox-us": "arn:aws:dynamodb:ap-southeast-2:385936341354:table/event-repo-EventStore165FCE28-1USRIO3KG963U/stream/2020-07-20T10:01:57.355",
    "develop":    "arn:aws:dynamodb:ap-southeast-2:337387902522:table/event-repo-EventStore165FCE28-OOIYCQO77FZM/stream/2020-07-20T10:01:57.355",
    "develop-au": "arn:aws:dynamodb:ap-southeast-2:337387902522:table/event-repo-EventStore165FCE28-OOIYCQO77FZM/stream/2020-07-20T10:01:57.355",
    "develop-us": "arn:aws:dynamodb:ap-southeast-2:337387902522:table/event-repo-EventStore165FCE28-1AM9YLQGMRS54/stream/2020-07-20T10:01:57.355",
    "prod":       "arn:aws:dynamodb:ap-southeast-2:053651923274:table/event-repo-EventStore165FCE28-191TZ0KO033T6/stream/2020-07-20T10:01:57.355",
    "prod-au":    "arn:aws:dynamodb:ap-southeast-2:053651923274:table/event-repo-EventStore165FCE28-191TZ0KO033T6/stream/2020-07-20T10:01:57.355",
    "prod-us":    "arn:aws:dynamodb:ap-southeast-2:053651923274:table/event-repo-EventStore165FCE28-1NI2YU50S774W/stream/2020-07-20T10:01:57.355",
}

def get_session(env):
    profile = ENV_PROFILES.get(env)
    if not profile:
        raise ValueError(f"Unknown environment: {env}")
    session = boto3.Session(profile_name=profile, region_name=REGION)
    try:
        session.client("sts").get_caller_identity()
    except NoCredentialsError:
        print(f"No credentials for profile '{profile}'. Run: aws sso login --profile sso")
        sys.exit(1)
    return session

def find_listener_state_table(dynamo_client, service):
    paginator = dynamo_client.get_paginator("list_tables")
    candidates = []
    for page in paginator.paginate():
        for t in page["TableNames"]:
            if t.startswith(service) and ("ListenerState" in t or "ProcessManagerState" in t):
                candidates.append(t)
    if not candidates:
        raise ValueError(f"No ListenerState table found for '{service}'")
    def ver(name):
        try: return int(name.replace(service + "-", "").split("-")[0])
        except: return 0
    candidates.sort(key=ver, reverse=True)
    return candidates[0]

def get_listener_state(dynamo_client, table_name):
    resp = dynamo_client.get_item(TableName=table_name, Key={"id": {"S": "0"}})
    item = resp.get("Item", {})
    state = {}
    for k, v in item.items():
        if "S" in v: state[k] = v["S"]
        elif "N" in v: state[k] = int(v["N"])
    return state

def skip_error_event(dynamo_client, table_name, error_sequence_id):
    next_seq = error_sequence_id + 1
    dynamo_client.update_item(
        TableName=table_name,
        Key={"id": {"S": "0"}},
        UpdateExpression="SET #status = :status, sequenceId = :seq REMOVE errorSequenceId",
        ExpressionAttributeNames={"#status": "status"},
        ExpressionAttributeValues={":status": {"S": "STREAMING"}, ":seq": {"N": str(next_seq)}}
    )
    return next_seq

def find_streamer_arn(lambda_client, service):
    paginator = lambda_client.get_paginator("list_functions")
    candidates = []
    for page in paginator.paginate():
        for fn in page["Functions"]:
            name = fn["FunctionName"]
            if name.startswith(service) and name.endswith("-Streamer"):
                candidates.append(fn)
    if not candidates:
        raise ValueError(f"No Streamer lambda found for '{service}'")
    def ver(fn):
        try: return int(fn["FunctionName"].replace(service + "-", "").split("-")[0])
        except: return 0
    candidates.sort(key=ver, reverse=True)
    return candidates[0]["FunctionArn"]

def reattach_streamer(lambda_client, streamer_arn, stream_arn, dry_run=False):
    existing = lambda_client.list_event_source_mappings(
        EventSourceArn=stream_arn, FunctionName=streamer_arn
    ).get("EventSourceMappings", [])
    for m in existing:
        print(f"  Removing old mapping: {m['UUID']}")
        if not dry_run:
            lambda_client.delete_event_source_mapping(UUID=m["UUID"])
    print(f"  Attaching: {streamer_arn.split(':function:')[-1]}")
    if not dry_run:
        resp = lambda_client.create_event_source_mapping(
            EventSourceArn=stream_arn, FunctionName=streamer_arn,
            BatchSize=500, Enabled=True, StartingPosition="LATEST"
        )
        return resp["UUID"]
    return "DRY_RUN"

def reconnect(service, env, dry_run=False):
    print(f"\nReconnecting {service} in {env}{' [DRY RUN]' if dry_run else ''}")
    if env.startswith("prod") and not dry_run:
        confirm = input("PRODUCTION environment. Type 'yes' to continue: ")
        if confirm.strip().lower() != "yes":
            print("Cancelled."); sys.exit(0)
    session = get_session(env)
    dynamo = session.client("dynamodb")
    lam = session.client("lambda")

    print("\n1. Checking ListenerState...")
    table = find_listener_state_table(dynamo, service)
    print(f"   Table: {table}")
    state = get_listener_state(dynamo, table)
    print(f"   Status: {state.get('status')} | errorSequenceId: {state.get('errorSequenceId')}")
    if state.get("status") != "ERROR":
        print(f"\nService not in ERROR state. Nothing to do."); return

    error_seq = state.get("errorSequenceId")
    if not error_seq:
        print("No errorSequenceId. Cannot reconnect."); sys.exit(1)

    print(f"\n2. Skipping bad event (sequenceId {error_seq})...")
    if not dry_run:
        next_seq = skip_error_event(dynamo, table, error_seq)
        print(f"   State -> STREAMING, next sequenceId: {next_seq}")
    else:
        print(f"   [DRY RUN] Would advance to {error_seq + 1}")

    print(f"\n3. Re-attaching Streamer...")
    streamer_arn = find_streamer_arn(lam, service)
    stream_arn = EVENT_STORE_STREAMS.get(env)
    if not stream_arn:
        raise ValueError(f"No stream ARN for env '{env}'")
    mapping_id = reattach_streamer(lam, streamer_arn, stream_arn, dry_run)
    print(f"   Event source mapping: {mapping_id}")
    print(f"\n{service} ({env}) reconnected. Will process on next event trigger.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reconnect a Bamboo listener service")
    parser.add_argument("service")
    parser.add_argument("env")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    reconnect(args.service, args.env, args.dry_run)
