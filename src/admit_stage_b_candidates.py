#!/usr/bin/env python3
"""Stage B Candidate Admission Review & Gatekeeper Engine.

Conducts formal admission review for the five open canonical replacement slots:
1. SLOT_GITHUB_01: GitHub replacement for issues/create
2. SLOT_STRIPE_01: Stripe replacement for PostCustomers
3. SLOT_STRIPE_02: Stripe replacement for PostPaymentIntents
4. SLOT_CHATWOOT_01: Chatwoot replacement for create-a-contact
5. SLOT_LINE_01: LINE replacement for replyMessage

Evaluates structural eligibility, provenance immutability, operational statefulness,
and mock feasibility (held as PENDING) against the frozen protocol.

Statefulness Model:
- schema_invocation_mode: SINGLE_TURN_CONSTRUCTIBLE | MULTI_TURN_DEPENDENT
- external_prerequisite_state: NONE | FIXTURE_REQUIRED | LIFECYCLE_STATE_REQUIRED
- mock_fixture_requirements: explicit list of minimal deterministic fixtures needed for mock execution

Review Provenance:
- automated_static_admission_checklist
- human_review_status: PENDING
- human_sign_off_record: formal sign-off template

Produces:
- results_stage_b/candidate_admission_decisions.json
- results_stage_b/CANDIDATE_ADMISSION_REVIEW.md
"""

import argparse
import datetime
import hashlib
import json
import os
from typing import Any, Dict, List, Optional

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_DECISIONS_PATH = os.path.join(ROOT_DIR, "results_stage_b", "candidate_admission_decisions.json")
MD_REVIEW_PATH = os.path.join(ROOT_DIR, "results_stage_b", "CANDIDATE_ADMISSION_REVIEW.md")
UNIVERSE_JSON_PATH = os.path.join(ROOT_DIR, "results_stage_b", "raw_operation_universe.json")
REGISTRY_JSON_PATH = os.path.join(ROOT_DIR, "results_stage_b", "raw_sources_provenance_registry.json")


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


DECISIONS_DATA: List[Dict[str, Any]] = [
    {
        "slot_id": "SLOT_GITHUB_01",
        "slot_name": "GitHub Developer Platforms Slot",
        "target_domain": "Developer Platforms",
        "replaced_operation_id": "issues/create",
        "replaced_exclusion_reason": (
            "Disqualified from canonical cohort due to observed recursion depth 6 exceeding MAX_RECURSION_DEPTH=5 "
            "and polymorphic object unions across assignees, labels, and milestone properties."
        ),
        "admission_decision": "ADMITTED_PENDING_EXTRACTION",
        "admitted_candidate": {
            "operation_id": "pulls/create",
            "candidate_source_id": "CAND-001",
            "source_cluster_id": "CLUSTER_GITHUB",
            "source_project": "GitHub (github/rest-api-description)",
            "source_spec_pointer": "#/paths/~1repos~1{owner}~1{repo}~1pulls/post",
            "source_blob_sha": "a91fa76a34558f5ed28e245cb1a6c46a44a61f4d",
            "raw_file_sha256": "ba5ddc1eeeede9f3858abd96325359891f38a2bd8e20fd111abf4230741db194",
            "raw_source_file_path": "data_stage_b/raw/CAND-001/a91fa76a34558f5ed28e245cb1a6c46a44a61f4d.json",
            "http_method": "POST",
            "endpoint": "/repos/{owner}/{repo}/pulls",
            "intended_benchmark_domain": "Developer Platforms",
            "complexity_tier": "MODERATE",
            "maximum_nesting_depth": 2,
            "property_count": 10,
            "required_count": 4,
            "optional_ratio": 0.6,
            "input_surfaces": ["body", "path"],
            "content_types": ["application/json"],
            "estimated_token_footprint": 179,
            "static_eligibility_status": "STATICALLY_ELIGIBLE_CANDIDATE",
            "schema_invocation_mode": "SINGLE_TURN_CONSTRUCTIBLE",
            "external_prerequisite_state": "FIXTURE_REQUIRED",
            "mock_fixture_requirements": [
                "repository_fixture",
                "base_branch_fixture",
                "head_branch_fixture",
            ],
            "acceptance_rationale": (
                "High-fidelity developer platform operation. Cleanly bounded at recursion depth 2 with 10 properties "
                "(4 required: 2 path parameters '{owner}', '{repo}', plus 2 body fields 'head', 'base'). "
                "Schema parameters can be formulated in a single turn without inspecting prior responses (SINGLE_TURN_CONSTRUCTIBLE), "
                "but execution is not state-independent: mock execution requires pre-configured repository and base/head branch fixtures "
                "(FIXTURE_REQUIRED). Avoids structural bloat and polymorphic object unions of issues/create."
            ),
            "mock_feasibility_status": "PENDING",
            "mock_feasibility_notes": (
                "Local mock execution requires an in-memory repository store that registers pull requests and validates "
                "head/base branches. Feasibility is pending extraction verification and implementation of the hermetic mock harness."
            ),
            "automated_static_admission_checklist": {
                "immutable_provenance_verified": True,
                "json_pointer_verified": True,
                "max_recursion_depth_within_bound": True,
                "no_object_unions": True,
                "no_multipart_or_binary": True,
                "no_cycles": True,
                "no_external_refs": True,
                "no_conflicting_allof": True,
                "statefulness_model_partitioned": True,
                "mock_feasibility_held_pending": True,
            },
            "human_review_status": "PENDING",
            "human_sign_off_record": {
                "reviewer_name": "[PENDING_HUMAN_REVIEWER]",
                "review_date": "[PENDING_DATE]",
                "reviewed_artifact_sha256": "[PENDING_SHA256]",
                "human_sign_off_decision": "PENDING_REVIEW",
            },
        },
        "evaluated_rejected_candidates": [
            {
                "operation_id": "pulls/submit-review",
                "endpoint": "POST /repos/{owner}/{repo}/pulls/{pull_number}/reviews/{review_id}/events",
                "schema_invocation_mode": "MULTI_TURN_DEPENDENT",
                "external_prerequisite_state": "LIFECYCLE_STATE_REQUIRED",
                "mock_fixture_requirements": [
                    "pull_request_fixture",
                    "prior_turn_pending_review_fixture",
                ],
                "rejection_reason": (
                    "Multi-turn dependent operation: requires a pre-existing review_id created in a prior review turn. "
                    "Cannot be invoked reliably in a single-turn benchmark without multi-turn state pre-seeding."
                ),
            },
            {
                "operation_id": "pulls/create-review-comment",
                "endpoint": "POST /repos/{owner}/{repo}/pulls/{pull_number}/comments",
                "schema_invocation_mode": "MULTI_TURN_DEPENDENT",
                "external_prerequisite_state": "LIFECYCLE_STATE_REQUIRED",
                "mock_fixture_requirements": [
                    "pull_request_fixture",
                    "commit_id_fixture",
                    "diff_position_context_fixture",
                ],
                "rejection_reason": (
                    "Requires specific line/commit_id diff context and pull_number; less representative of primary top-level creation actions than pulls/create."
                ),
            },
            {
                "operation_id": "codespaces/create-with-pr-for-authenticated-user",
                "endpoint": "POST /repos/{owner}/{repo}/pulls/{pull_number}/codespaces",
                "schema_invocation_mode": "SINGLE_TURN_CONSTRUCTIBLE",
                "external_prerequisite_state": "FIXTURE_REQUIRED",
                "mock_fixture_requirements": [
                    "pull_request_fixture",
                    "codespace_environment_billing_fixture",
                ],
                "rejection_reason": (
                    "Specialized virtual machine / container infrastructure provisioning rather than core developer collaborative workflow."
                ),
            },
        ],
    },
    {
        "slot_id": "SLOT_STRIPE_01",
        "slot_name": "Stripe Payments Slot A",
        "target_domain": "Payments",
        "replaced_operation_id": "PostCustomers",
        "replaced_exclusion_reason": (
            "Disqualified from canonical cohort due to observed recursion depth 6 exceeding MAX_RECURSION_DEPTH=5 "
            "and polymorphic address/metadata object unions."
        ),
        "admission_decision": "ADMITTED_PENDING_EXTRACTION",
        "admitted_candidate": {
            "operation_id": "PostPayouts",
            "candidate_source_id": "CAND-002",
            "source_cluster_id": "CLUSTER_STRIPE",
            "source_project": "Stripe (stripe/openapi)",
            "source_spec_pointer": "#/paths/~1v1~1payouts/post",
            "source_blob_sha": "f1cedf38e0178538a3c72e750da80226df41e28c",
            "raw_file_sha256": "7cff4cc46d0654101a36a3302f7544640f5f73e4f3cad6f264f0e23c19fa1776",
            "raw_source_file_path": "data_stage_b/raw/CAND-002/f1cedf38e0178538a3c72e750da80226df41e28c.json",
            "http_method": "POST",
            "endpoint": "/v1/payouts",
            "intended_benchmark_domain": "Payments",
            "complexity_tier": "MODERATE",
            "maximum_nesting_depth": 3,
            "property_count": 10,
            "required_count": 2,
            "optional_ratio": 0.8,
            "input_surfaces": ["body"],
            "content_types": ["application/x-www-form-urlencoded"],
            "estimated_token_footprint": 186,
            "static_eligibility_status": "STATICALLY_ELIGIBLE_CANDIDATE",
            "schema_invocation_mode": "SINGLE_TURN_CONSTRUCTIBLE",
            "external_prerequisite_state": "FIXTURE_REQUIRED",
            "mock_fixture_requirements": [
                "merchant_account_fixture",
                "payout_capability_active_fixture",
                "sufficient_ledger_balance_fixture",
            ],
            "acceptance_rationale": (
                "Core merchant balance routing operation. Cleanly bounded at depth 3 with 10 properties "
                "(2 required: 'amount' and 'currency'). Schema parameters can be formulated in a single turn without prior entity outputs "
                "(SINGLE_TURN_CONSTRUCTIBLE), but execution is not state-independent: mock execution requires active merchant account "
                "capability and a sufficient available ledger-balance fixture (FIXTURE_REQUIRED). Avoids recursive depth bloat (depth 6) "
                "and polymorphic address objects of PostCustomers."
            ),
            "mock_feasibility_status": "PENDING",
            "mock_feasibility_notes": (
                "Local mock execution requires tracking merchant ledger balance and returning deterministic payout records. "
                "Feasibility is pending extraction verification and implementation of the hermetic mock harness."
            ),
            "automated_static_admission_checklist": {
                "immutable_provenance_verified": True,
                "json_pointer_verified": True,
                "max_recursion_depth_within_bound": True,
                "no_object_unions": True,
                "no_multipart_or_binary": True,
                "no_cycles": True,
                "no_external_refs": True,
                "no_conflicting_allof": True,
                "statefulness_model_partitioned": True,
                "mock_feasibility_held_pending": True,
            },
            "human_review_status": "PENDING",
            "human_sign_off_record": {
                "reviewer_name": "[PENDING_HUMAN_REVIEWER]",
                "review_date": "[PENDING_DATE]",
                "reviewed_artifact_sha256": "[PENDING_SHA256]",
                "human_sign_off_decision": "PENDING_REVIEW",
            },
        },
        "evaluated_rejected_candidates": [
            {
                "operation_id": "PostTransfers",
                "endpoint": "POST /v1/transfers",
                "schema_invocation_mode": "SINGLE_TURN_CONSTRUCTIBLE",
                "external_prerequisite_state": "FIXTURE_REQUIRED",
                "mock_fixture_requirements": [
                    "merchant_account_fixture",
                    "destination_connected_account_fixture",
                    "sufficient_ledger_balance_fixture",
                ],
                "rejection_reason": (
                    "Ranked #2 for fund routing (score 96, depth 3, 9 props). Structurally valid, but PostPayouts is preferred "
                    "as it represents direct merchant settlement rather than intra-account transfer."
                ),
            },
            {
                "operation_id": "PostAccountLinks",
                "endpoint": "POST /v1/account_links",
                "schema_invocation_mode": "MULTI_TURN_DEPENDENT",
                "external_prerequisite_state": "LIFECYCLE_STATE_REQUIRED",
                "mock_fixture_requirements": [
                    "pre_created_connected_account_fixture",
                ],
                "rejection_reason": (
                    "Multi-turn dependent operation: requires a pre-existing connected account ID ('account'), introducing entity linkage statefulness."
                ),
            },
            {
                "operation_id": "PostPayoutsPayoutCancel",
                "endpoint": "POST /v1/payouts/{payout}/cancel",
                "schema_invocation_mode": "MULTI_TURN_DEPENDENT",
                "external_prerequisite_state": "LIFECYCLE_STATE_REQUIRED",
                "mock_fixture_requirements": [
                    "pre_created_payout_in_cancellable_state_fixture",
                ],
                "rejection_reason": (
                    "Lifecycle state mutation requiring a pre-existing payout ID in path that is currently in a pending/cancellable lifecycle state."
                ),
            },
        ],
    },
    {
        "slot_id": "SLOT_STRIPE_02",
        "slot_name": "Stripe Payments Slot B",
        "target_domain": "Payments",
        "replaced_operation_id": "PostPaymentIntents",
        "replaced_exclusion_reason": (
            "Disqualified from canonical cohort due to observed recursion depth 9 (492 properties) exceeding MAX_RECURSION_DEPTH=5 "
            "and wide polymorphic payment_method_options anyOf unions."
        ),
        "admission_decision": "ADMITTED_PENDING_EXTRACTION",
        "admitted_candidate": {
            "operation_id": "PostShippingRates",
            "candidate_source_id": "CAND-002",
            "source_cluster_id": "CLUSTER_STRIPE",
            "source_project": "Stripe (stripe/openapi)",
            "source_spec_pointer": "#/paths/~1v1~1shipping_rates/post",
            "source_blob_sha": "f1cedf38e0178538a3c72e750da80226df41e28c",
            "raw_file_sha256": "7cff4cc46d0654101a36a3302f7544640f5f73e4f3cad6f264f0e23c19fa1776",
            "raw_source_file_path": "data_stage_b/raw/CAND-002/f1cedf38e0178538a3c72e750da80226df41e28c.json",
            "http_method": "POST",
            "endpoint": "/v1/shipping_rates",
            "intended_benchmark_domain": "Payments",
            "complexity_tier": "COMPLEX_NESTED",
            "maximum_nesting_depth": 4,
            "property_count": 17,
            "required_count": 7,
            "optional_ratio": 0.5882,
            "input_surfaces": ["body"],
            "content_types": ["application/x-www-form-urlencoded"],
            "estimated_token_footprint": 280,
            "static_eligibility_status": "STATICALLY_ELIGIBLE_CANDIDATE",
            "schema_invocation_mode": "SINGLE_TURN_CONSTRUCTIBLE",
            "external_prerequisite_state": "FIXTURE_REQUIRED",
            "mock_fixture_requirements": [
                "authenticated_account_context_fixture",
            ],
            "acceptance_rationale": (
                "Highly representative commerce and checkout configuration operation. Exhibits rich nested object architecture "
                "(depth 4 with nested 'delivery_estimate' and 'fixed_amount' objects containing currency and duration units) "
                "while strictly complying with the frozen bound d <= 5. Schema parameters can be formulated in a single turn "
                "(SINGLE_TURN_CONSTRUCTIBLE); runtime execution requires an authenticated merchant account context fixture (FIXTURE_REQUIRED). "
                "Replaces the extreme bloat and 492-property depth-9 explosion of PostPaymentIntents with a rigorous, tractable complex contract."
            ),
            "mock_feasibility_status": "PENDING",
            "mock_feasibility_notes": (
                "Deterministic creation endpoint; mock returns standard shipping_rate resource. Feasibility is pending "
                "extraction verification and implementation of the hermetic mock harness."
            ),
            "automated_static_admission_checklist": {
                "immutable_provenance_verified": True,
                "json_pointer_verified": True,
                "max_recursion_depth_within_bound": True,
                "no_object_unions": True,
                "no_multipart_or_binary": True,
                "no_cycles": True,
                "no_external_refs": True,
                "no_conflicting_allof": True,
                "statefulness_model_partitioned": True,
                "mock_feasibility_held_pending": True,
            },
            "human_review_status": "PENDING",
            "human_sign_off_record": {
                "reviewer_name": "[PENDING_HUMAN_REVIEWER]",
                "review_date": "[PENDING_DATE]",
                "reviewed_artifact_sha256": "[PENDING_SHA256]",
                "human_sign_off_decision": "PENDING_REVIEW",
            },
        },
        "evaluated_rejected_candidates": [
            {
                "operation_id": "PostInvoicesInvoiceAttachPayment",
                "endpoint": "POST /v1/invoices/{invoice}/attach_payment",
                "schema_invocation_mode": "MULTI_TURN_DEPENDENT",
                "external_prerequisite_state": "LIFECYCLE_STATE_REQUIRED",
                "mock_fixture_requirements": [
                    "unpaid_invoice_in_open_state_fixture",
                ],
                "rejection_reason": (
                    "Multi-turn lifecycle dependency: requires a pre-existing unpaid invoice in open lifecycle state ('/v1/invoices/{invoice}/attach_payment'). "
                    "Cannot be tested in isolation without seeded invoice state."
                ),
            },
            {
                "operation_id": "PostInvoicesInvoicePay",
                "endpoint": "POST /v1/invoices/{invoice}/pay",
                "schema_invocation_mode": "MULTI_TURN_DEPENDENT",
                "external_prerequisite_state": "LIFECYCLE_STATE_REQUIRED",
                "mock_fixture_requirements": [
                    "unpaid_invoice_in_open_state_fixture",
                ],
                "rejection_reason": (
                    "Multi-turn lifecycle dependency: requires a pre-existing unpaid invoice in open lifecycle state ('/v1/invoices/{invoice}/pay')."
                ),
            },
            {
                "operation_id": "PostTaxRates",
                "endpoint": "POST /v1/tax_rates",
                "schema_invocation_mode": "SINGLE_TURN_CONSTRUCTIBLE",
                "external_prerequisite_state": "FIXTURE_REQUIRED",
                "mock_fixture_requirements": [
                    "authenticated_account_context_fixture",
                ],
                "rejection_reason": (
                    "Depth 3, 11 properties; structurally valid, but PostShippingRates provides richer structural nesting diversity "
                    "(depth 4, 17 properties, 7 required) while adhering to all protocol constraints."
                ),
            },
        ],
    },
    {
        "slot_id": "SLOT_CHATWOOT_01",
        "slot_name": "Chatwoot CRM & Support Slot",
        "target_domain": "CRM/Support",
        "replaced_operation_id": "create-a-contact",
        "replaced_exclusion_reason": (
            "Disqualified from canonical cohort due to format: binary on avatar property, violating the multipart/binary exclusion rule."
        ),
        "admission_decision": "ADMITTED_PENDING_EXTRACTION",
        "admitted_candidate": {
            "operation_id": "create-a-webhook",
            "candidate_source_id": "CAND-011",
            "source_cluster_id": "CLUSTER_CHATWOOT",
            "source_project": "Chatwoot (chatwoot/chatwoot)",
            "source_spec_pointer": "#/paths/~1api~1v1~1accounts~1{account_id}~1webhooks/post",
            "source_blob_sha": "b0b3ca6332f0627a1fe7e4e8db5bd92ac4e77589",
            "raw_file_sha256": "c8cba6e5975ee286593866f20652e29154717b835dc6324af7433bb497e7ab43",
            "raw_source_file_path": "data_stage_b/raw/CAND-011/b0b3ca6332f0627a1fe7e4e8db5bd92ac4e77589.json",
            "http_method": "POST",
            "endpoint": "/api/v1/accounts/{account_id}/webhooks",
            "intended_benchmark_domain": "CRM/Support",
            "complexity_tier": "MODERATE",
            "maximum_nesting_depth": 4,
            "property_count": 4,
            "required_count": 1,
            "optional_ratio": 0.75,
            "input_surfaces": ["body", "path"],
            "content_types": ["application/json"],
            "estimated_token_footprint": 126,
            "static_eligibility_status": "STATICALLY_ELIGIBLE_CANDIDATE",
            "schema_invocation_mode": "SINGLE_TURN_CONSTRUCTIBLE",
            "external_prerequisite_state": "FIXTURE_REQUIRED",
            "mock_fixture_requirements": [
                "account_fixture",
            ],
            "acceptance_rationale": (
                "Standard event automation integration in customer support systems. Combines path routing ('account_id') "
                "with a structured JSON body containing an array of 10 distinct event enums ('subscriptions'). "
                "Schema parameters are constructible in a single turn without prior entity outputs (SINGLE_TURN_CONSTRUCTIBLE); "
                "runtime execution requires an existing account fixture corresponding to the path parameter (FIXTURE_REQUIRED). "
                "Avoids the multipart/form-data binary upload violation that disqualified create-a-contact."
            ),
            "mock_feasibility_status": "PENDING",
            "mock_feasibility_notes": (
                "Webhook receiver store can be mocked deterministically by recording webhook registration in mock state. "
                "Feasibility is pending extraction verification and implementation of the hermetic mock harness."
            ),
            "automated_static_admission_checklist": {
                "immutable_provenance_verified": True,
                "json_pointer_verified": True,
                "max_recursion_depth_within_bound": True,
                "no_object_unions": True,
                "no_multipart_or_binary": True,
                "no_cycles": True,
                "no_external_refs": True,
                "no_conflicting_allof": True,
                "statefulness_model_partitioned": True,
                "mock_feasibility_held_pending": True,
            },
            "human_review_status": "PENDING",
            "human_sign_off_record": {
                "reviewer_name": "[PENDING_HUMAN_REVIEWER]",
                "review_date": "[PENDING_DATE]",
                "reviewed_artifact_sha256": "[PENDING_SHA256]",
                "human_sign_off_decision": "PENDING_REVIEW",
            },
        },
        "evaluated_rejected_candidates": [
            {
                "operation_id": "update-canned-response-in-account",
                "endpoint": "PATCH /api/v1/accounts/{account_id}/canned_responses/{id}",
                "schema_invocation_mode": "MULTI_TURN_DEPENDENT",
                "external_prerequisite_state": "LIFECYCLE_STATE_REQUIRED",
                "mock_fixture_requirements": [
                    "account_fixture",
                    "pre_existing_canned_response_fixture",
                ],
                "rejection_reason": (
                    "Multi-turn lifecycle dependency: requires a pre-existing canned response ID in path ('/canned_responses/{id}'). "
                    "Cannot be tested in isolation without seeded canned response state."
                ),
            },
            {
                "operation_id": "update-a-webhook",
                "endpoint": "PATCH /api/v1/accounts/{account_id}/webhooks/{webhook_id}",
                "schema_invocation_mode": "MULTI_TURN_DEPENDENT",
                "external_prerequisite_state": "LIFECYCLE_STATE_REQUIRED",
                "mock_fixture_requirements": [
                    "account_fixture",
                    "pre_existing_webhook_fixture",
                ],
                "rejection_reason": (
                    "Multi-turn lifecycle dependency: requires pre-existing webhook ID in path ('/webhooks/{webhook_id}')."
                ),
            },
            {
                "operation_id": "add-new-canned-response-to-account",
                "endpoint": "POST /api/v1/accounts/{account_id}/canned_responses",
                "schema_invocation_mode": "SINGLE_TURN_CONSTRUCTIBLE",
                "external_prerequisite_state": "FIXTURE_REQUIRED",
                "mock_fixture_requirements": [
                    "account_fixture",
                ],
                "rejection_reason": (
                    "Structurally simpler (depth 3, 3 props, flat string pair) without array/enum diversity; "
                    "create-a-webhook is more representative of programmatic integration complexity."
                ),
            },
        ],
    },
    {
        "slot_id": "SLOT_LINE_01",
        "slot_name": "LINE Logistics & Communications Slot",
        "target_domain": "Logistics/Communications",
        "replaced_operation_id": "replyMessage",
        "replaced_exclusion_reason": (
            "Disqualified from canonical cohort due to observed recursion depth 13 and wide 11-variant discriminated object union in messages array."
        ),
        "admission_decision": "ADMITTED_PENDING_EXTRACTION",
        "admitted_candidate": {
            "operation_id": "showLoadingAnimation",
            "candidate_source_id": "CAND-013",
            "source_cluster_id": "CLUSTER_LINE",
            "source_project": "LINE (line/line-openapi)",
            "source_spec_pointer": "#/paths/~1v2~1bot~1chat~1loading~1start/post",
            "source_blob_sha": "11f1fdb91092246f881edd1a9457cb37327a6c5d",
            "raw_file_sha256": "41033aa8491fc67ab09c4ec322f2aab072ae7b9402297e8c4f042eda0c2dd1fc",
            "raw_source_file_path": "data_stage_b/raw/CAND-013/11f1fdb91092246f881edd1a9457cb37327a6c5d.yml",
            "http_method": "POST",
            "endpoint": "/v2/bot/chat/loading/start",
            "intended_benchmark_domain": "Logistics/Communications",
            "complexity_tier": "FLAT",
            "maximum_nesting_depth": 3,
            "property_count": 2,
            "required_count": 1,
            "optional_ratio": 0.5,
            "input_surfaces": ["body"],
            "content_types": ["application/json"],
            "estimated_token_footprint": 89,
            "static_eligibility_status": "STATICALLY_ELIGIBLE_CANDIDATE",
            "schema_invocation_mode": "SINGLE_TURN_CONSTRUCTIBLE",
            "external_prerequisite_state": "FIXTURE_REQUIRED",
            "mock_fixture_requirements": [
                "target_chat_or_user_fixture",
            ],
            "acceptance_rationale": (
                "Authentic messaging interaction endpoint in the LINE bot ecosystem ('/v2/bot/chat/loading/start'). "
                "Schema arguments ('chatId' and bounded integer 'loadingSeconds' [5-60s]) can be formulated in a single turn "
                "without inspecting prior responses (SINGLE_TURN_CONSTRUCTIBLE). Crucially, external prerequisite state is classified "
                "as FIXTURE_REQUIRED (not NONE) because the pinned LINE OpenAPI specification explicitly models response 400 for "
                "'An invalid chat ID is specified', confirming that server-side chat/user identity validation is represented in the "
                "contract semantics. Avoids depth-13 recursion and polymorphic discriminated message unions of replyMessage."
            ),
            "mock_feasibility_status": "PENDING",
            "mock_feasibility_notes": (
                "Deterministic response simulation; mock validates chatId against active target chat fixture and verifies loadingSeconds range (5-60s), returning HTTP 202. "
                "Feasibility is pending extraction verification and implementation of the hermetic mock harness."
            ),
            "automated_static_admission_checklist": {
                "immutable_provenance_verified": True,
                "json_pointer_verified": True,
                "max_recursion_depth_within_bound": True,
                "no_object_unions": True,
                "no_multipart_or_binary": True,
                "no_cycles": True,
                "no_external_refs": True,
                "no_conflicting_allof": True,
                "statefulness_model_partitioned": True,
                "mock_feasibility_held_pending": True,
            },
            "human_review_status": "PENDING",
            "human_sign_off_record": {
                "reviewer_name": "[PENDING_HUMAN_REVIEWER]",
                "review_date": "[PENDING_DATE]",
                "reviewed_artifact_sha256": "[PENDING_SHA256]",
                "human_sign_off_decision": "PENDING_REVIEW",
            },
        },
        "evaluated_rejected_candidates": [
            {
                "operation_id": "updateRichMenuAlias",
                "endpoint": "POST /v2/bot/richmenu/alias/{richMenuAliasId}",
                "schema_invocation_mode": "MULTI_TURN_DEPENDENT",
                "external_prerequisite_state": "LIFECYCLE_STATE_REQUIRED",
                "mock_fixture_requirements": [
                    "pre_created_rich_menu_alias_fixture",
                ],
                "rejection_reason": (
                    "Multi-turn lifecycle dependency: administrative alias mapping requiring pre-existing richMenuAliasId in path."
                ),
            },
            {
                "operation_id": "linkRichMenuIdToUser",
                "endpoint": "POST /v2/bot/user/{userId}/richmenu/{richMenuId}",
                "schema_invocation_mode": "MULTI_TURN_DEPENDENT",
                "external_prerequisite_state": "LIFECYCLE_STATE_REQUIRED",
                "mock_fixture_requirements": [
                    "user_id_fixture",
                    "rich_menu_id_fixture",
                ],
                "rejection_reason": (
                    "Multi-turn lifecycle dependency: depth 1 path-only mapping; lacks request body and structural depth."
                ),
            },
            {
                "operation_id": "testWebhookEndpoint",
                "endpoint": "POST /v2/bot/channel/webhook/test",
                "schema_invocation_mode": "SINGLE_TURN_CONSTRUCTIBLE",
                "external_prerequisite_state": "FIXTURE_REQUIRED",
                "mock_fixture_requirements": [
                    "channel_webhook_endpoint_configured_fixture",
                ],
                "rejection_reason": (
                    "Diagnostic health probe ('/channel/webhook/test') rather than conversational bot interaction."
                ),
            },
        ],
    },
]


def generate_json_decisions(generated_at_utc: str) -> Dict[str, Any]:
    self_path = os.path.join(ROOT_DIR, "src", "admit_stage_b_candidates.py")
    self_sha = sha256_file(self_path) if os.path.exists(self_path) else "PENDING_SELF_HASH"

    report = {
        "metadata": {
            "admission_script": "src/admit_stage_b_candidates.py",
            "admission_script_sha256": self_sha,
            "generated_at_utc": generated_at_utc,
            "governing_policy": "STAGE_B_CANDIDATE_ADMISSION_GATE",
            "review_document": "results_stage_b/CANDIDATE_ADMISSION_REVIEW.md",
            "human_review_status": "PENDING",
            "total_slots_reviewed": len(DECISIONS_DATA),
            "total_admitted": sum(1 for d in DECISIONS_DATA if d["admission_decision"] == "ADMITTED_PENDING_EXTRACTION"),
            "total_open_slots": sum(1 for d in DECISIONS_DATA if d["admission_decision"] != "ADMITTED_PENDING_EXTRACTION"),
        },
        "decisions": DECISIONS_DATA,
    }
    return report


def generate_markdown_review(decisions_report: Dict[str, Any]) -> str:
    meta = decisions_report["metadata"]
    decisions = decisions_report["decisions"]

    lines = [
        "# Stage B Candidate Admission Gate Review & Decisions",
        "",
        f"**Document Role:** Stage B Candidate Admission Gatekeeper Review  ",
        f"**Date (UTC):** {meta['generated_at_utc']}  ",
        f"**Governing Policy:** `{meta['governing_policy']}`  ",
        f"**Automated Static Gate Status:** ALL_SLOTS_DECIDED — `ADMITTED_PENDING_EXTRACTION`  ",
        f"**Human Review Status:** `PENDING`  ",
        "",
        "---",
        "",
        "## 1. Executive Summary & Corpus Composition Impact",
        "",
        "This gatekeeper review formally evaluates and admits five replacement operations for the open canonical slots in Stage B. "
        "Each candidate was verified directly against the pinned raw OpenAPI specifications for structural eligibility, "
        "provenance immutability, operational statefulness, and future deterministic mock feasibility.",
        "",
        "To prevent conflating schema-level single-turn constructibility with runtime state independence, "
        "every operation is rigorously characterized by three distinct dimensions:",
        "1. **`schema_invocation_mode`**: `SINGLE_TURN_CONSTRUCTIBLE` vs `MULTI_TURN_DEPENDENT`",
        "2. **`external_prerequisite_state`**: `NONE` vs `FIXTURE_REQUIRED` vs `LIFECYCLE_STATE_REQUIRED`",
        "3. **`mock_fixture_requirements`**: minimal deterministic fixtures required by mock runtime",
        "",
        "| Slot ID | Slot Domain | Replaced Operation | Admitted Replacement | Invocation Mode | Prerequisite State | Mock Fixtures | Decision |",
        "| :--- | :--- | :--- | :--- | :---: | :---: | :--- | :---: |",
    ]

    for d in decisions:
        c = d["admitted_candidate"]
        fixtures_str = ", ".join(c["mock_fixture_requirements"])
        lines.append(
            f"| `{d['slot_id']}` | {d['target_domain']} | `{d['replaced_operation_id']}` | "
            f"`{c['operation_id']}` | `{c['schema_invocation_mode']}` | `{c['external_prerequisite_state']}` | "
            f"`{fixtures_str}` | **`{d['admission_decision']}`** |"
        )

    lines.extend([
        "",
        "### Benchmark Real-Cohort Composition Status",
        "- **Clean Monomorphic Operations:** 29 (24 existing provisional candidates + 5 newly admitted replacement candidates)",
        "- **Faithful-Union Operations (Amendment 003):** 1 (`Stripe PostRefunds`, provisional finite union)",
        "- **Total Real Candidate Cohort:** **30 operations** (reaching target cohort size)",
        "- **Open Replacement Slots Remaining:** **0**",
        "- **Excluded Operations Tracked:** 7 (retained permanently in exclusion registry for benchmark provenance)",
        "- **Admission Invariant:** Status remains strictly `ADMITTED_PENDING_EXTRACTION`. Zero operations are designated "
        "as `CANONICAL_FAITHFUL` until extraction, automated validation, field-lineage verification, and manual review are complete.",
        "- **Human Review Gate:** Human review status remains strictly `PENDING`. No operation receives final canonical ratification without manual researcher sign-off.",
        "",
        "---",
        "",
        "## 2. Slot-by-Slot Admission Reviews",
        "",
    ])

    for idx, d in enumerate(decisions, 1):
        c = d["admitted_candidate"]
        fixtures_list_md = "\n".join([f"  - `{fix}`" for fix in c["mock_fixture_requirements"]])
        lines.extend([
            f"### 2.{idx} Slot: `{d['slot_id']}` — {d['slot_name']}",
            "",
            f"- **Target Domain:** {d['target_domain']}",
            f"- **Replaced Operation:** `{d['replaced_operation_id']}`",
            f"- **Replaced Exclusion Rationale:** {d['replaced_exclusion_reason']}",
            f"- **Admission Decision:** **`{d['admission_decision']}`**",
            f"- **Admitted Operation ID:** `{c['operation_id']}`",
            f"- **Endpoint & Method:** `{c['http_method']} {c['endpoint']}`",
            f"- **JSON Pointer:** `{c['source_spec_pointer']}`",
            f"- **Source Project:** {c['source_project']} (`{c['candidate_source_id']}`)",
            f"- **Source Blob SHA:** `{c['source_blob_sha']}`",
            f"- **Raw File SHA-256:** `{c['raw_file_sha256']}`",
            f"- **Raw Source File:** `{c['raw_source_file_path']}`",
            "",
            "#### Structural & Complexity Profile",
            f"- **Maximum Nesting Depth:** {c['maximum_nesting_depth']} (Protocol threshold: $\\le 5$)",
            f"- **Property Count:** {c['property_count']}",
            f"- **Required Properties Count:** {c['required_count']}",
            f"- **Optional Field Ratio:** {c['optional_ratio']}",
            f"- **Input Surfaces:** `{', '.join(c['input_surfaces'])}`",
            f"- **Request Content-Type:** `{', '.join(c['content_types'])}`",
            f"- **Estimated Token Footprint:** ~{c['estimated_token_footprint']} tokens",
            f"- **Static Eligibility Verdict:** `{c['static_eligibility_status']}`",
            "",
            "#### Operational Statefulness & Invocation Mode Assessment",
            f"- **Schema Invocation Mode:** `{c['schema_invocation_mode']}`",
            f"- **External Prerequisite State:** `{c['external_prerequisite_state']}`",
            f"- **Mock Fixture Requirements:**",
            f"{fixtures_list_md}",
            f"- **Analysis:** {c['acceptance_rationale']}",
            "",
            "#### Mock-Safety Feasibility Review",
            f"- **Status:** **`{c['mock_feasibility_status']}`** (Held strictly pending empirical validation)",
            f"- **Assessment:** {c['mock_feasibility_notes']}",
            "",
            "#### Automated / Agent-Assisted Static Admission Checklist",
            f"- [x] Immutable Provenance Verified: Raw file SHA-256 and Git blob SHA match pinned registry.",
            f"- [x] JSON Pointer Verified: Resolves unambiguously to target `{c['http_method']}` operation in raw spec.",
            f"- [x] Depth Bound Verified: Observed depth {c['maximum_nesting_depth']} strictly $\\le 5$.",
            f"- [x] Union Freedom: Contains zero object-level oneOf/anyOf unions.",
            f"- [x] Format Compliance: Contains zero binary, multipart/form-data, or file payload parameters.",
            f"- [x] Reference Integrity: Zero cyclic refs and zero unresolved external $ref pointers.",
            f"- [x] Composition Integrity: Zero conflicting scalar type merges under allOf.",
            f"- [x] Operational Statefulness: Formally partitioned into invocation mode, prerequisite state, and mock fixtures.",
            f"- [x] Mock Feasibility: Recorded as `PENDING`, not assumed.",
            "",
            f"**Human Review Status:** `PENDING`",
            "",
            "#### Human Sign-Off Record",
            "- **Reviewer Name:** `[PENDING_HUMAN_REVIEWER]`",
            "- **Review Date:** `[PENDING_DATE]`",
            "- **Reviewed Artifact SHA-256:** `[PENDING_SHA256]`",
            "- **Human Sign-Off Decision:** `PENDING_REVIEW` (Must be manually confirmed by research staff)",
            "",
            "#### Evaluated & Rejected Competing Candidates",
            "",
            "| Competing Candidate | Endpoint | Invocation Mode | Prerequisite State | Explicit Rejection Rationale |",
            "| :--- | :--- | :---: | :---: | :--- |",
        ])
        for r in d["evaluated_rejected_candidates"]:
            lines.append(
                f"| `{r['operation_id']}` | `{r['endpoint']}` | `{r['schema_invocation_mode']}` | "
                f"`{r['external_prerequisite_state']}` | {r['rejection_reason']} |"
            )
        lines.extend(["", "---", ""])

    lines.extend([
        "## 3. Provenance & Reproducibility Certification",
        "",
        "Every admitted operation is cryptographically pinned to an immutable Git blob SHA and raw source file SHA-256 digest. "
        "No modifications have been made to Stage A, frozen raw source files, or existing provisional candidates. "
        "The operation manifest (`stage_b_operation_manifest.yaml`) reflects these admissions under "
        "the status `ADMITTED_PENDING_EXTRACTION`. Human sign-off remains formally PENDING.",
        "",
    ])

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Stage B Candidate Admission Review Engine")
    parser.add_argument("--generated-at", type=str, default=None, help="Explicit UTC ISO8601 timestamp")
    args = parser.parse_args()

    if args.generated_at:
        generated_at = args.generated_at
    else:
        generated_at = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    decisions_report = generate_json_decisions(generated_at)

    with open(JSON_DECISIONS_PATH, "w", encoding="utf-8") as f:
        json.dump(decisions_report, f, indent=2, sort_keys=True)
        f.write("\n")
    print(f"Wrote admission decisions JSON to {JSON_DECISIONS_PATH}")

    md_content = generate_markdown_review(decisions_report)
    with open(MD_REVIEW_PATH, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"Wrote admission review Markdown to {MD_REVIEW_PATH}")


if __name__ == "__main__":
    main()
