"""
build_dataset_schemas.py - Loads base schemas and maps domain-matched distractor tool specifications.
"""

import copy
import json
import os

data_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(data_dir, "base_schemas.json"), "r", encoding="utf-8") as f:
    BASE_SCHEMAS = json.load(f)

DOMAIN_DISTRACTORS = {
    "stripe_create_refund": [
        {"name": "cancel_customer_subscription", "description": "Cancel an active recurring Stripe subscription plan.", "parameters": {"type": "OBJECT", "properties": {"subscription_id": {"type": "STRING"}}, "required": ["subscription_id"]}},
        {"name": "create_customer_invoice", "description": "Generate an itemized customer invoice for billing.", "parameters": {"type": "OBJECT", "properties": {"customer_id": {"type": "STRING"}, "amount": {"type": "INTEGER"}}, "required": ["customer_id", "amount"]}},
        {"name": "capture_payment_intent", "description": "Capture an authorized payment intent hold.", "parameters": {"type": "OBJECT", "properties": {"intent_id": {"type": "STRING"}}, "required": ["intent_id"]}},
        {"name": "verify_bank_account", "description": "Verify micro-deposit amounts for a merchant bank link.", "parameters": {"type": "OBJECT", "properties": {"account_id": {"type": "STRING"}, "amounts": {"type": "ARRAY", "items": {"type": "INTEGER"}}}, "required": ["account_id", "amounts"]}}
    ],
    "github_create_issue": [
        {"name": "create_pull_request", "description": "Open a code review pull request merging head branch into base.", "parameters": {"type": "OBJECT", "properties": {"owner": {"type": "STRING"}, "repo": {"type": "STRING"}, "title": {"type": "STRING"}, "head": {"type": "STRING"}}, "required": ["owner", "repo", "title", "head"]}},
        {"name": "list_repo_commits", "description": "Retrieve chronological git commits for a branch.", "parameters": {"type": "OBJECT", "properties": {"owner": {"type": "STRING"}, "repo": {"type": "STRING"}, "sha": {"type": "STRING"}}, "required": ["owner", "repo"]}},
        {"name": "add_issue_comment", "description": "Post a markdown comment on an existing issue or pull request.", "parameters": {"type": "OBJECT", "properties": {"owner": {"type": "STRING"}, "repo": {"type": "STRING"}, "issue_number": {"type": "INTEGER"}, "body": {"type": "STRING"}}, "required": ["owner", "repo", "issue_number", "body"]}},
        {"name": "fork_repository", "description": "Fork a target GitHub repository to the authenticated user account.", "parameters": {"type": "OBJECT", "properties": {"owner": {"type": "STRING"}, "repo": {"type": "STRING"}}, "required": ["owner", "repo"]}}
    ],
    "slack_post_message": [
        {"name": "create_slack_channel", "description": "Provision a new public or private Slack team channel.", "parameters": {"type": "OBJECT", "properties": {"name": {"type": "STRING"}, "is_private": {"type": "BOOLEAN"}}, "required": ["name"]}},
        {"name": "set_user_status", "description": "Update the custom emoji status text for a Slack team member.", "parameters": {"type": "OBJECT", "properties": {"status_text": {"type": "STRING"}, "status_emoji": {"type": "STRING"}}, "required": ["status_text"]}},
        {"name": "upload_slack_file", "description": "Upload a binary file or log snippet to a Slack conversation.", "parameters": {"type": "OBJECT", "properties": {"channels": {"type": "STRING"}, "filename": {"type": "STRING"}}, "required": ["channels", "filename"]}},
        {"name": "archive_slack_channel", "description": "Archive an inactive Slack communication channel.", "parameters": {"type": "OBJECT", "properties": {"channel_id": {"type": "STRING"}}, "required": ["channel_id"]}}
    ],
    "generic_fallback": [
        {"name": "get_account_balance", "description": "Retrieve financial balance.", "parameters": {"type": "OBJECT", "properties": {"account_id": {"type": "STRING"}}, "required": ["account_id"]}},
        {"name": "list_audit_logs", "description": "Fetch chronological audit logs.", "parameters": {"type": "OBJECT", "properties": {"start_date": {"type": "STRING"}}, "required": ["start_date"]}},
        {"name": "export_csv_report", "description": "Generate an export job.", "parameters": {"type": "OBJECT", "properties": {"report_type": {"type": "STRING"}}, "required": ["report_type"]}},
        {"name": "revoke_api_key", "description": "Revoke an API token.", "parameters": {"type": "OBJECT", "properties": {"key_id": {"type": "STRING"}}, "required": ["key_id"]}}
    ]
}

# Populate fallbacks for remaining schemas
for base in BASE_SCHEMAS:
    if base["id"] not in DOMAIN_DISTRACTORS:
        DOMAIN_DISTRACTORS[base["id"]] = copy.deepcopy(DOMAIN_DISTRACTORS["generic_fallback"])
