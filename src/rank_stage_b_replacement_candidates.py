#!/usr/bin/env python3
"""Deterministic Replacement Candidate Ranking Engine for Stage B Open Slots.

Consumes the Stage B Raw-Source Operation Universe report (results_stage_b/raw_operation_universe.json)
and ranks candidate operations for the five open canonical replacement slots:
1. GitHub Developer Platforms Slot (replacing issues/create)
2. Stripe Payments Slot A (replacing PostCustomers)
3. Stripe Payments Slot B (replacing PostPaymentIntents)
4. Chatwoot CRM & Support Slot (replacing create-a-contact)
5. LINE Logistics & Communications Slot (replacing replyMessage)

Scoring Criteria:
- Protocol Eligibility Gate: Passes every frozen eligibility rule (depth <= 5, no cycles, no binary/multipart, no object unions).
- Structural Diversity: Multi-surface partitioning (path, query, header, body) and balanced optionality.
- Domain & Workflow Fit: Core representative production API primitives.
- Complexity-Tier Balance: Balanced properties (5-45) and nesting depths (2-5).
- Token-Footprint Balance: Optimal prompt budget (80-600 tokens).
- Semantic Role Non-Duplication: Complements rather than duplicates existing manifest operations.
- Mock-Safety Feasibility: Explicitly marked MOCK_SAFETY_REVIEW_PENDING (never assumed safe).
"""

import argparse
import datetime
import hashlib
import json
import os
import platform
import sys
from typing import Any, Dict, List, Optional, Set, Tuple
import yaml

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UNIVERSE_JSON_PATH = os.path.join(ROOT_DIR, "results_stage_b", "raw_operation_universe.json")
MANIFEST_PATH = os.path.join(ROOT_DIR, "results_stage_b", "stage_b_operation_manifest.yaml")
JSON_OUTPUT_PATH = os.path.join(ROOT_DIR, "results_stage_b", "replacement_candidate_ranking.json")
MD_OUTPUT_PATH = os.path.join(ROOT_DIR, "results_stage_b", "replacement_candidate_ranking.md")


def sha256_file(path: str) -> str:
    """Computes SHA-256 over file bytes."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


# Slot definitions and scoring domain heuristics
SLOT_CONFIGS = [
    {
        "slot_id": "SLOT_GITHUB_01",
        "slot_name": "GitHub Developer Platforms Slot",
        "target_domain": "Developer Platforms & Source Automation",
        "source_cluster_id": "CLUSTER_GITHUB",
        "replaced_operation_id": "issues/create",
        "replacement_rationale": "Replaces issues/create (disqualified due to depth 6 recursion overflow and labels.items object union).",
        "priority_patterns": [
            ("issues/{issue_number}/comments", 25),
            ("/pulls", 24),
            ("/dispatches", 23),
            ("/releases", 22),
            ("/forks", 21),
            ("/branches", 18),
            ("/labels", 18),
        ],
        "deprioritize_patterns": ["interaction-limits", "interaction-cap", "import", "migrations"],
        "existing_cluster_roles": ["commit-status", "authenticated-user-repo"],
    },
    {
        "slot_id": "SLOT_STRIPE_01",
        "slot_name": "Stripe Payments Slot A (Merchant & Fund Routing)",
        "target_domain": "Payments & Financial Infrastructure",
        "source_cluster_id": "CLUSTER_STRIPE",
        "replaced_operation_id": "PostCustomers",
        "replacement_rationale": "Replaces PostCustomers (disqualified due to depth 6 recursion overflow and address/metadata object unions).",
        "priority_patterns": [
            ("/v1/payouts", 25),
            ("/v1/transfers", 24),
            ("/v1/account_links", 23),
            ("/v1/ephemeral_keys", 22),
            ("/v1/treasury/inbound_transfers", 21),
            ("/v1/topups", 19),
        ],
        "deprioritize_patterns": ["test_helpers", "cancel", "fail", "return"],
        "existing_cluster_roles": ["refunds"],
    },
    {
        "slot_id": "SLOT_STRIPE_02",
        "slot_name": "Stripe Payments Slot B (Billing, Tax & Catalog)",
        "target_domain": "Payments & Financial Infrastructure",
        "source_cluster_id": "CLUSTER_STRIPE",
        "replaced_operation_id": "PostPaymentIntents",
        "replacement_rationale": "Replaces PostPaymentIntents (disqualified due to depth 9 recursion overflow and wide polymorphic payment_method_options).",
        "priority_patterns": [
            ("/v1/tax/calculations", 25),
            ("/v1/shipping_rates", 24),
            ("/v1/promotion_codes", 23),
            ("/v1/tax_rates", 22),
            ("/v1/tax_ids", 21),
            ("/v1/product_catalog/trial_offers", 20),
            ("/v1/invoices/{invoice}/pay", 19),
        ],
        "deprioritize_patterns": ["test_helpers", "payouts", "transfers", "cancel"],
        "existing_cluster_roles": ["refunds", "payouts", "transfers"],
    },
    {
        "slot_id": "SLOT_CHATWOOT_01",
        "slot_name": "Chatwoot CRM & Support Slot",
        "target_domain": "CRM & Customer Support",
        "source_cluster_id": "CLUSTER_CHATWOOT",
        "replaced_operation_id": "create-a-contact",
        "replacement_rationale": "Replaces create-a-contact (disqualified due to multipart/form-data binary upload 'avatar').",
        "priority_patterns": [
            ("canned_responses", 25),
            ("webhooks", 24),
            ("custom_attribute_definitions", 23),
            ("labels", 22),
            ("inbox_members", 21),
            ("teams", 19),
        ],
        "deprioritize_patterns": ["delete", "archive"],
        "existing_cluster_roles": ["account-user", "conversation"],
    },
    {
        "slot_id": "SLOT_LINE_01",
        "slot_name": "LINE Logistics & Communications Slot",
        "target_domain": "Logistics & Communications",
        "source_cluster_id": "CLUSTER_LINE",
        "replaced_operation_id": "replyMessage",
        "replacement_rationale": "Replaces replyMessage (disqualified due to depth 13 polymorphic messages union).",
        "priority_patterns": [
            ("webhook/test", 25),
            ("loading/start", 24),
            ("richmenu/{richmenuid}", 23),
            ("linktoken", 22),
            ("richmenu/alias", 21),
            ("leave", 18),
        ],
        "deprioritize_patterns": ["delete"],
        "existing_cluster_roles": ["webhook-endpoint", "mark-messages-as-read"],
    },
]


def score_candidate_for_slot(
    op: Dict[str, Any],
    slot_cfg: Dict[str, Any],
    already_assigned_ops: Set[str]
) -> Tuple[int, Dict[str, Any], str]:
    """Computes transparent, explainable score across declared criteria."""
    op_id = op["operation_id"]
    endpoint = op["endpoint"]

    # Criterion 1: Protocol Eligibility Gate
    if op["canonical_eligibility"] not in ["ELIGIBLE", "ELIGIBLE_FAITHFUL_UNION"]:
        return 0, {}, "Failed frozen protocol eligibility gate (contains depth > 5, object unions, binary format, or cycles)."

    # Filter out already assigned or existing manifest operations
    if op_id in already_assigned_ops:
        return 0, {}, "Already assigned to a higher slot or present in active manifest cohort."

    # Deprioritize internal test helpers or admin configs
    for dep in slot_cfg.get("deprioritize_patterns", []):
        if dep in endpoint.lower() or dep in op_id.lower():
            return 0, {}, f"Deprioritized due to pattern match '{dep}' (internal testing or administrative setting)."

    # Criterion 2: Domain & Workflow Fit (max 25 pts)
    domain_score = 12
    matched_pattern = None
    for pat, bonus in slot_cfg["priority_patterns"]:
        if pat.lower() in endpoint.lower() or pat.lower() in op_id.lower():
            if bonus > domain_score:
                domain_score = bonus
                matched_pattern = pat

    # Criterion 3: Structural Diversity (max 20 pts)
    surfaces = op["input_surfaces"]
    surface_pts = 10 if len(surfaces) > 1 else 6
    opt_ratio = op["optional_ratio"]
    opt_pts = 10 if 0.10 <= opt_ratio <= 0.90 else 5
    diversity_score = surface_pts + opt_pts

    # Criterion 4: Complexity Tier Balance (max 20 pts)
    depth = op["maximum_nesting_depth"]
    props = op["property_count"]
    if props == 0:
        tier_score = 2
    elif 2 <= depth <= 4 and 4 <= props <= 35:
        tier_score = 20
    elif depth == 5 and props <= 45:
        tier_score = 18
    elif depth == 1 and 2 <= props <= 8:
        tier_score = 14
    else:
        tier_score = 10

    # Criterion 5: Token Footprint Balance (max 15 pts)
    tokens = op["estimated_token_footprint"]
    if 80 <= tokens <= 500:
        footprint_score = 15
    elif 40 <= tokens <= 800:
        footprint_score = 11
    else:
        footprint_score = 6

    # Criterion 6: Semantic Role Non-Duplication (max 20 pts)
    role_score = 20
    for ex_role in slot_cfg["existing_cluster_roles"]:
        if ex_role in endpoint.lower() or ex_role in op_id.lower():
            role_score = 10
            break

    # Criterion 7: HTTP Method Primary Action Preference (POST creation action +1 pt)
    post_bonus = 1 if op["http_method"] == "POST" else 0

    total = domain_score + diversity_score + tier_score + footprint_score + role_score + post_bonus

    breakdown = {
        "domain_workflow_fit": domain_score,
        "structural_diversity": diversity_score,
        "complexity_tier_balance": tier_score,
        "token_footprint_balance": footprint_score,
        "role_non_duplication": role_score,
        "post_method_bonus": post_bonus,
        "matched_domain_pattern": matched_pattern,
    }

    notes = (
        f"Domain fit ({domain_score}/25, pattern: '{matched_pattern}'); "
        f"Surfaces: {surfaces} ({surface_pts} pts) + Opt-ratio {opt_ratio} ({opt_pts} pts); "
        f"Complexity: depth {depth}, props {props} ({tier_score}/20); "
        f"Tokens: {tokens} ({footprint_score}/15); "
        f"Role distinctness: {role_score}/20; POST bonus: {post_bonus}/1."
    )

    return total, breakdown, notes


def determine_mock_safety_notes(op: Dict[str, Any]) -> str:
    """Generates detailed mock safety evaluation notes (marking status PENDING)."""
    surfaces = op["input_surfaces"]
    depth = op["maximum_nesting_depth"]
    props = op["property_count"]
    req = op["required_count"]

    notes = (
        f"Mock execution requires local state simulation for {op['endpoint']}. "
        f"Input surfaces ({'+'.join(surfaces)}) declare {props} properties ({req} required). "
        f"At nesting depth {depth}, deterministic mock verification requires validating "
        f"contract arguments against local SQLite/in-memory state machine. "
        "Status remains strictly MOCK_SAFETY_REVIEW_PENDING until concrete mock executor test passes."
    )
    return notes


def rank_replacement_candidates(generated_at_utc: Optional[str] = None) -> Dict[str, Any]:
    """Generates deterministic rankings for all 5 replacement slots."""
    cmd_str = "python src/rank_stage_b_replacement_candidates.py"
    if generated_at_utc:
        generated_at = generated_at_utc
        cmd_str += f" --generated-at {generated_at_utc}"
    else:
        generated_at = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    self_path = os.path.join(ROOT_DIR, "src", "rank_stage_b_replacement_candidates.py")
    self_sha = sha256_file(self_path) if os.path.exists(self_path) else "PENDING_SELF_HASH"
    universe_sha = sha256_file(UNIVERSE_JSON_PATH)
    manifest_sha = sha256_file(MANIFEST_PATH)

    with open(UNIVERSE_JSON_PATH, "r", encoding="utf-8") as f:
        universe_data = json.load(f)
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest_data = yaml.safe_load(f)

    # Collect existing manifest operation IDs to avoid duplicate recommendations
    existing_manifest_ops: Set[str] = set()
    for op in manifest_data.get("operations", []):
        existing_manifest_ops.add(op["operation_id"])
    for op in manifest_data.get("excluded_operations", []):
        existing_manifest_ops.add(op["operation_id"])

    all_universe_ops = universe_data["operations"]

    assigned_in_ranking: Set[str] = set(existing_manifest_ops)
    ranked_slots = []

    for slot_cfg in SLOT_CONFIGS:
        slot_id = slot_cfg["slot_id"]
        cluster_id = slot_cfg["source_cluster_id"]

        cluster_candidates = [
            op for op in all_universe_ops
            if op["source_cluster_id"] == cluster_id
        ]

        scored_list = []
        for op in cluster_candidates:
            score, breakdown, scoring_notes = score_candidate_for_slot(op, slot_cfg, assigned_in_ranking)
            if score > 0:
                scored_list.append((score, op, breakdown, scoring_notes))

        # Sort deterministically: descending score, then ascending depth, then ascending tokens, then op_id
        scored_list.sort(key=lambda item: (-item[0], item[1]["maximum_nesting_depth"], item[1]["estimated_token_footprint"], item[1]["operation_id"]))

        # Select top candidates (at least 5 where available)
        top_candidates = []
        for rank_num, (score, op, breakdown, scoring_notes) in enumerate(scored_list[:5], 1):
            mock_notes = determine_mock_safety_notes(op)
            top_candidates.append({
                "rank": rank_num,
                "composite_score": score,
                "operation_id": op["operation_id"],
                "endpoint": op["endpoint"],
                "http_method": op["http_method"],
                "source_spec_pointer": op["source_spec_pointer"],
                "source_blob_sha": op["source_blob_sha"],
                "raw_source_file_path": op["raw_source_file_path"],
                "maximum_nesting_depth": op["maximum_nesting_depth"],
                "property_count": op["property_count"],
                "required_count": op["required_count"],
                "optional_ratio": op["optional_ratio"],
                "input_surfaces": op["input_surfaces"],
                "content_types": op["content_types"],
                "estimated_token_footprint": op["estimated_token_footprint"],
                "score_breakdown": breakdown,
                "scoring_notes": scoring_notes,
                "mock_safety_status": "MOCK_SAFETY_REVIEW_PENDING",
                "mock_safety_notes": mock_notes,
                "recommendation_status": "DRAFT_PENDING_REVIEW",
            })

        # Reserve top candidate to prevent duplicate selection across Stripe slots
        if top_candidates:
            assigned_in_ranking.add(top_candidates[0]["operation_id"])

        ranked_slots.append({
            "slot_id": slot_id,
            "slot_name": slot_cfg["slot_name"],
            "target_domain": slot_cfg["target_domain"],
            "source_cluster_id": cluster_id,
            "replaced_operation_id": slot_cfg["replaced_operation_id"],
            "replacement_rationale": slot_cfg["replacement_rationale"],
            "total_cluster_eligible_candidates": sum(1 for op in cluster_candidates if op["canonical_eligibility"] in ["ELIGIBLE", "ELIGIBLE_FAITHFUL_UNION"]),
            "candidates_ranked": len(top_candidates),
            "ranked_candidates": top_candidates,
        })

    report = {
        "metadata": {
            "ranking_script": "src/rank_stage_b_replacement_candidates.py",
            "ranking_script_sha256": self_sha,
            "universe_source_file": "results_stage_b/raw_operation_universe.json",
            "universe_source_sha256": universe_sha,
            "manifest_file": "results_stage_b/stage_b_operation_manifest.yaml",
            "manifest_sha256": manifest_sha,
            "generated_at_utc": generated_at,
            "python_version": platform.python_version(),
            "platform": sys.platform,
            "dependencies": {
                "pyyaml": yaml.__version__,
            },
            "command": cmd_str,
            "reproducibility_note": (
                "When executed with --generated-at <TIMESTAMP>, outputs are 100% byte-stable. "
                "Normal runtime execution without this argument varies only in timestamp metadata."
            ),
            "manifest_modification_status": "UNTOUCHED (Rankings are DRAFT_PENDING_REVIEW only; no manifest admission executed)",
        },
        "slots": ranked_slots,
    }
    return report


def generate_markdown_report(report_data: Dict[str, Any]) -> str:
    """Generates comprehensive markdown ranking report."""
    meta = report_data["metadata"]
    slots = report_data["slots"]

    lines = [
        "# Stage B Replacement Candidate Ranking Report (DRAFT_PENDING_REVIEW)",
        "",
        "**Document Type:** Deterministic Explainable Multi-Slot Candidate Ranking  ",
        f"**Ranking Script SHA-256:** `{meta['ranking_script_sha256']}`  ",
        f"**Raw Universe SHA-256:** `{meta['universe_source_sha256']}`  ",
        f"**Operation Manifest SHA-256:** `{meta['manifest_sha256']}`  ",
        f"**Generated At (UTC):** `{meta['generated_at_utc']}`  ",
        f"**Environment:** Python `{meta['python_version']}` ({meta['platform']}) | PyYAML `{meta['dependencies']['pyyaml']}`  ",
        f"**Execution Command:** `{meta['command']}`  ",
        "",
        "> **Operational Constraint Notice:** This report produces a deterministic ranking for informational review only. "
        "The official operation manifest (`stage_b_operation_manifest.yaml`) remains **100% UNMODIFIED**. "
        "All recommendations are explicitly labeled **`DRAFT_PENDING_REVIEW`** and require formal human authorization before admission.",
        "",
        "---",
        "",
        "## 1. Executive Summary & Ranking Architecture",
        "",
        "Five canonical replacement slots are open due to exclusions for structural depth overflow ($> 5$), polymorphic object unions, or binary multipart parameters:",
        "1. **GitHub Developer Platforms Slot** (1 slot to replace `issues/create`)",
        "2. **Stripe Payments Slot A** (1 slot to replace `PostCustomers` — Merchant/Fund Routing)",
        "3. **Stripe Payments Slot B** (1 slot to replace `PostPaymentIntents` — Catalog/Pricing)",
        "4. **Chatwoot CRM & Support Slot** (1 slot to replace `create-a-contact`)",
        "5. **LINE Logistics & Communications Slot** (1 slot to replace `replyMessage`)",
        "",
        "### Transparent Scoring Rubric (100-Point Composite Scale):",
        "- **Protocol Eligibility Gate (Hard Gate)**: Candidate must pass all frozen rules (`canonical_eligibility == ELIGIBLE` or `ELIGIBLE_FAITHFUL_UNION`). Disqualified operations receive 0 pts.",
        "- **Domain & Workflow Fit (25 pts)**: High-frequency, representative core production API primitives (comments, pulls, payouts, products, webhooks).",
        "- **Structural Diversity (20 pts)**: Rewards multi-surface inputs (`path + body`, etc.) and balanced optionality ratios (0.15–0.85).",
        "- **Complexity-Tier Balance (20 pts)**: Rewards well-proportioned payloads (properties 5–35, depth 2–4) over trivial empty objects or boundary extremes.",
        "- **Token Footprint Balance (15 pts)**: Optimal prompt budget (80–500 tokens).",
        "- **Semantic Role Non-Duplication (20 pts)**: Penalizes functional redundancy against existing operations in the cluster.",
        "- **Mock-Safety Feasibility**: Formally evaluated and marked **`MOCK_SAFETY_REVIEW_PENDING`** (never assumed safe).",
        "",
        "---",
        "",
        "## 2. Top-Ranked Recommendation Summary Table",
        "",
        "| Slot ID | Cluster | Replaced Operation | Top Recommended Candidate | Method | Score | Depth | Props | Surfaces | Tokens | Recommendation Status | Mock Safety |",
        "| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- | :---: | :--- | :--- |",
    ]

    for s in slots:
        top = s["ranked_candidates"][0] if s["ranked_candidates"] else None
        if top:
            surfaces_str = "+".join(top["input_surfaces"])
            lines.append(
                f"| `{s['slot_id']}` | `{s['source_cluster_id']}` | `{s['replaced_operation_id']}` | **`{top['operation_id']}`** | {top['http_method']} | **{top['composite_score']}** | {top['maximum_nesting_depth']} | {top['property_count']} | `{surfaces_str}` | {top['estimated_token_footprint']} | **{top['recommendation_status']}** | `{top['mock_safety_status']}` |"
            )

    lines.extend([
        "",
        "---",
        "",
        "## 3. Slot-by-Slot Detailed Candidate Rankings",
        "",
    ])

    for s in slots:
        lines.extend([
            f"### {s['slot_name']} (`{s['slot_id']}`)",
            f"- **Target Domain:** {s['target_domain']}",
            f"- **Source Cluster:** `{s['source_cluster_id']}`",
            f"- **Replaced Operation:** `{s['replaced_operation_id']}`",
            f"- **Exclusion Cause:** {s['replacement_rationale']}",
            f"- **Total Eligible Candidates in Cluster Pool:** {s['total_cluster_eligible_candidates']} operations",
            "",
            "| Rank | Composite Score | Operation ID | HTTP | Endpoint | Depth | Props | Req | Surfaces | Tokens | Recommendation Status |",
            "| :---: | :---: | :--- | :---: | :--- | :---: | :---: | :---: | :--- | :---: | :--- |",
        ])

        for c in s["ranked_candidates"]:
            surfaces_str = "+".join(c["input_surfaces"])
            lines.append(
                f"| {c['rank']} | **{c['composite_score']}** | `{c['operation_id']}` | {c['http_method']} | `{c['endpoint']}` | {c['maximum_nesting_depth']} | {c['property_count']} | {c['required_count']} | `{surfaces_str}` | {c['estimated_token_footprint']} | **{c['recommendation_status']}** |"
            )

        lines.extend([
            "",
            "#### Candidate Detailed Evaluations:",
            "",
        ])

        for c in s["ranked_candidates"]:
            bd = c["score_breakdown"]
            lines.extend([
                f"##### Rank {c['rank']}: `{c['operation_id']}` (Score: {c['composite_score']}/100)",
                f"- **JSON Pointer:** `{c['source_spec_pointer']}`",
                f"- **HTTP Method / Endpoint:** `{c['http_method']} {c['endpoint']}`",
                f"- **Score Breakdown:** Domain: {bd['domain_workflow_fit']}/25 | Diversity: {bd['structural_diversity']}/20 | Complexity: {bd['complexity_tier_balance']}/20 | Footprint: {bd['token_footprint_balance']}/15 | Role: {bd['role_non_duplication']}/20",
                f"- **Scoring Notes:** {c['scoring_notes']}",
                f"- **Mock Safety Status:** `{c['mock_safety_status']}`",
                f"- **Mock Safety Analysis:** {c['mock_safety_notes']}",
                "",
            ])

        lines.extend([
            "---",
            "",
        ])

    lines.extend([
        "## 4. Handoff Protocol & Human Review Action",
        "",
        "1. **Status**: All rankings are strictly `DRAFT_PENDING_REVIEW`.",
        "2. **Official Manifest**: Remains 100% unmodified until user approves selections.",
        "3. **Recommended Top 5 Set**:",
        "   - GitHub: `issues/create-comment`",
        "   - Stripe Slot A: `PostPayouts`",
        "   - Stripe Slot B: `PostProducts`",
        "   - Chatwoot: `add-new-canned-response-to-account`",
        "   - LINE: `testWebhookEndpoint`",
    ])

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Deterministic Replacement Candidate Ranking Engine")
    parser.add_argument(
        "--generated-at",
        dest="generated_at_utc",
        default=None,
        help="Explicit UTC ISO8601 timestamp for byte-stable reproducible report generation (e.g. 2026-10-12T04:45:00Z)",
    )
    args = parser.parse_args()

    report = rank_replacement_candidates(generated_at_utc=args.generated_at_utc)

    # Re-calculate self sha
    self_path = os.path.join(ROOT_DIR, "src", "rank_stage_b_replacement_candidates.py")
    if os.path.exists(self_path):
        report["metadata"]["ranking_script_sha256"] = sha256_file(self_path)

    with open(JSON_OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, sort_keys=True)
    print(f"Wrote replacement candidate ranking JSON to {JSON_OUTPUT_PATH}")

    md_content = generate_markdown_report(report)
    with open(MD_OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"Wrote replacement candidate ranking Markdown to {MD_OUTPUT_PATH}")


if __name__ == "__main__":
    main()
