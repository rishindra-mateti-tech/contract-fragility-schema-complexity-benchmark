"""Stage C Release 1 Finding Adjudication Engine.

Adjudicates every diagnostic finding from Release 1 audits into exactly one of:
1. TRUE_CONSTRUCT_VALIDITY_DEFECT
2. INTENTIONAL_PAIRED_DESIGN_REUSE
3. AUDIT_RULE_FALSE_POSITIVE
4. REQUIRES_HUMAN_JUDGMENT

Preserves historical audit data without modification and provides the scientific
foundation for Release 2 remediation.
"""

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import json
import re
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = ROOT_DIR / "results_stage_c"
TASKS_DIR = ROOT_DIR / "data_stage_c" / "task_instances"

LEAKAGE_AUDIT_PATH = RESULTS_DIR / "TASK_LEAKAGE_AUDIT_RELEASE1.json"
DISTRACTOR_AUDIT_PATH = RESULTS_DIR / "DISTRACTOR_QUALITY_AUDIT_RELEASE1.json"
OUTPUT_JSON = RESULTS_DIR / "RELEASE1_FINDING_ADJUDICATION.json"
OUTPUT_MD = RESULTS_DIR / "RELEASE1_FINDING_ADJUDICATION.md"


@dataclass
class AdjudicatedFinding:
    finding_id: str
    task_id: str
    category: str
    mutation_family: str
    audit_dimension: str
    audit_classification: str
    adjudicated_category: str
    rationale: str
    release1_evidence: str
    remediation_required: bool
    remediation_strategy: str


class StageCRelease1Adjudicator:
    """Evaluates and adjudicates Release 1 diagnostic audit findings."""

    COMMON_DOMAIN_STEMS = {
        "metric", "token", "partition", "pipeline", "configure",
        "table", "slice", "message", "call", "status", "data", "event"
    }

    def __init__(self):
        self.adjudications: List[AdjudicatedFinding] = []

    def adjudicate_all(self) -> Dict[str, Any]:
        """Runs adjudication over all Release 1 findings."""
        if not LEAKAGE_AUDIT_PATH.is_file():
            raise FileNotFoundError(f"Missing Release 1 audit: {LEAKAGE_AUDIT_PATH}")

        with open(LEAKAGE_AUDIT_PATH, "r", encoding="utf-8") as f:
            leakage_data = json.load(f)

        self.adjudications = []
        finding_seq = 1

        # 1. Adjudicate all findings from TASK_LEAKAGE_AUDIT_RELEASE1.json
        for tid, summary in leakage_data.get("task_summaries", {}).items():
            cat = summary.get("category", "")
            mut = summary.get("mutation_family", "")
            for f in summary.get("findings", []):
                fid = f"ADJ_FINDING_{finding_seq:04d}"
                adj = self._adjudicate_single_leakage_finding(fid, tid, cat, mut, f)
                self.adjudications.append(adj)
                finding_seq += 1

        # 2. Adjudicate known distractor ambiguity items (TASK_AMBIGUITY_REGISTER.md)
        ambig_tasks = ["TASK_SYNTH_AB_001", "TASK_SYNTH_AB_041", "TASK_SYNTH_AB_081"]
        for tid in ambig_tasks:
            fid = f"ADJ_FINDING_{finding_seq:04d}"
            self.adjudications.append(AdjudicatedFinding(
                finding_id=fid,
                task_id=tid,
                category="ABSTENTION",
                mutation_family="CANONICAL",
                audit_dimension="DISTRACTOR_SEMANTIC_AMBIGUITY",
                audit_classification="AMBIGUOUS",
                adjudicated_category="TRUE_CONSTRUCT_VALIDITY_DEFECT",
                rationale=(
                    "The prompt mentions all required parameters for available candidate tool "
                    "'synth_create_key_value', creating genuine task ambiguity where an abstention "
                    "task could be erroneously resolved."
                ),
                release1_evidence="Prompt mentions all required parameters for tool(s): ['synth_create_key_value']",
                remediation_required=True,
                remediation_strategy="Replace candidate toolset with verified non-matching distractors in Release 2."
            ))
            finding_seq += 1

        # Compile summaries
        summary_by_category: Dict[str, int] = {}
        summary_by_dimension: Dict[str, Dict[str, int]] = {}
        remediation_count = 0

        for adj in self.adjudications:
            summary_by_category[adj.adjudicated_category] = (
                summary_by_category.get(adj.adjudicated_category, 0) + 1
            )
            dim_dict = summary_by_dimension.setdefault(adj.audit_dimension, {})
            dim_dict[adj.adjudicated_category] = dim_dict.get(adj.adjudicated_category, 0) + 1
            if adj.remediation_required:
                remediation_count += 1

        payload = {
            "adjudication_version": "1.0.0",
            "source_release": "RELEASE_1",
            "total_findings_adjudicated": len(self.adjudications),
            "remediation_required_count": remediation_count,
            "category_distribution": summary_by_category,
            "dimension_breakdown": summary_by_dimension,
            "adjudications": [asdict(a) for a in self.adjudications]
        }

        # Write artifacts
        with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, sort_keys=True)

        self._generate_markdown_report(payload)

        return payload

    def _adjudicate_single_leakage_finding(
        self, fid: str, tid: str, cat: str, mut: str, f: Dict[str, Any]
    ) -> AdjudicatedFinding:
        dim = f.get("dimension", "")
        evidence = f.get("evidence", "")
        audit_class = f.get("classification", "")
        details = f.get("details", {})

        # Rule 1: TOOL_NAME_EXACT_LEAK in ARGUMENT_CONSTRUCTION
        if dim == "TOOL_NAME_EXACT_LEAK":
            if cat == "ARGUMENT_CONSTRUCTION":
                return AdjudicatedFinding(
                    finding_id=fid,
                    task_id=tid,
                    category=cat,
                    mutation_family=mut,
                    audit_dimension=dim,
                    audit_classification=audit_class,
                    adjudicated_category="AUDIT_RULE_FALSE_POSITIVE",
                    rationale=(
                        "Argument Construction tasks present exactly one tool schema, meaning tool "
                        "selection is not tested. Stating the tool name in the prompt is an audit "
                        "false positive regarding tool selection leakage. However, it represents an "
                        "unnatural prompt styling that should be naturalized in Release 2."
                    ),
                    release1_evidence=evidence,
                    remediation_required=True,
                    remediation_strategy=(
                        "In Release 2, omit the tool name from the natural-language user prompt and "
                        "let the single available tool schema provide the tool declaration."
                    )
                )
            else:
                return AdjudicatedFinding(
                    finding_id=fid,
                    task_id=tid,
                    category=cat,
                    mutation_family=mut,
                    audit_dimension=dim,
                    audit_classification=audit_class,
                    adjudicated_category="TRUE_CONSTRUCT_VALIDITY_DEFECT",
                    rationale="Exact target tool name was leaked in a selection task prompt.",
                    release1_evidence=evidence,
                    remediation_required=True,
                    remediation_strategy="Remove tool name from prompt in Release 2."
                )

        # Rule 2: INTENT_CONFLICT across mutation variants
        if dim == "INTENT_CONFLICT":
            return AdjudicatedFinding(
                finding_id=fid,
                task_id=tid,
                category=cat,
                mutation_family=mut,
                audit_dimension=dim,
                audit_classification=audit_class,
                adjudicated_category="INTENTIONAL_PAIRED_DESIGN_REUSE",
                rationale=(
                    "The shared latent intent across mutation variants represents intentional paired "
                    "experimental design, testing whether different schema complexity transformations "
                    "affect tool-call reliability for the identical underlying user goal. The audit "
                    "classified this as a conflict because expected arguments differed across mutations, "
                    "which is the intended dependent variable."
                ),
                release1_evidence=evidence,
                remediation_required=True,
                remediation_strategy=(
                    "In Release 2, replace unmodeled intent sharing with an explicit paired_group_id "
                    "attribute that formally records intentional multi-condition pairings."
                )
            )

        # Rule 3: DUPLICATE_PROMPTS
        if dim == "DUPLICATE_PROMPTS":
            dup_of = details.get("duplicate_of", "")
            return AdjudicatedFinding(
                finding_id=fid,
                task_id=tid,
                category=cat,
                mutation_family=mut,
                audit_dimension=dim,
                audit_classification=audit_class,
                adjudicated_category="TRUE_CONSTRUCT_VALIDITY_DEFECT",
                rationale=(
                    f"Prompt is identical to {dup_of} within the same category and mutation family. "
                    "This duplication occurred from naive modulo cycling over 40 contracts, creating "
                    "unintended redundant tasks in the same experimental condition."
                ),
                release1_evidence=evidence,
                remediation_required=True,
                remediation_strategy=(
                    "In Release 2, assign unique prompt seeds, varied slot values, and distinct "
                    "template frames across all tasks within the same experimental condition."
                )
            )

        # Rule 4: FIELD_NAME_EXACT_LEAK
        if dim == "FIELD_NAME_EXACT_LEAK":
            shortcut_keys = details.get("shortcut_keys", [])
            return AdjudicatedFinding(
                finding_id=fid,
                task_id=tid,
                category=cat,
                mutation_family=mut,
                audit_dimension=dim,
                audit_classification=audit_class,
                adjudicated_category="TRUE_CONSTRUCT_VALIDITY_DEFECT",
                rationale=(
                    f"Verbatim parameter keys {shortcut_keys} were inserted into user prompts via template "
                    "formatting (e.g. 'key set to val'). In Tool Selection, this allows models to select "
                    "tools via parameter key matching rather than semantic reasoning."
                ),
                release1_evidence=evidence,
                remediation_required=True,
                remediation_strategy=(
                    "In Release 2, rephrase prompts to express arguments via natural-language descriptions "
                    "rather than verbatim snake_case schema property keys."
                )
            )

        # Rule 5: CONSTRUCTION_OMITTED_GOLD_VALUE
        if dim == "CONSTRUCTION_OMITTED_GOLD_VALUE":
            missing_props = details.get("missing_required_parameters", [])
            if missing_props == ["payload_parameters"]:
                return AdjudicatedFinding(
                    finding_id=fid,
                    task_id=tid,
                    category=cat,
                    mutation_family=mut,
                    audit_dimension=dim,
                    audit_classification=audit_class,
                    adjudicated_category="AUDIT_RULE_FALSE_POSITIVE",
                    rationale=(
                        "'payload_parameters' is a synthetic wrapper object introduced by the "
                        "NESTED_HIERARCHY mutation. All underlying leaf values were present in the prompt. "
                        "The audit rule tested only top-level dictionary keys, falsely flagging the "
                        "synthetic schema wrapper as an omitted user value."
                    ),
                    release1_evidence=evidence,
                    remediation_required=False,
                    remediation_strategy=(
                        "Update the leakage audit rule in Release 2 to traverse nested object schemas "
                        "and verify leaf semantic values rather than top-level synthetic wrapper names."
                    )
                )
            else:
                return AdjudicatedFinding(
                    finding_id=fid,
                    task_id=tid,
                    category=cat,
                    mutation_family=mut,
                    audit_dimension=dim,
                    audit_classification=audit_class,
                    adjudicated_category="TRUE_CONSTRUCT_VALIDITY_DEFECT",
                    rationale=f"Required gold parameter values {missing_props} were omitted from the prompt.",
                    release1_evidence=evidence,
                    remediation_required=True,
                    remediation_strategy="Ensure all non-inferable gold values are expressed in Release 2 prompts."
                )

        # Rule 6: TOOL_NAME_SUBSTRING_LEAK
        if dim == "TOOL_NAME_SUBSTRING_LEAK":
            matched_stems = details.get("matched_stems", [])
            is_common = all(stem.lower() in self.COMMON_DOMAIN_STEMS for stem in matched_stems)
            if is_common:
                return AdjudicatedFinding(
                    finding_id=fid,
                    task_id=tid,
                    category=cat,
                    mutation_family=mut,
                    audit_dimension=dim,
                    audit_classification=audit_class,
                    adjudicated_category="AUDIT_RULE_FALSE_POSITIVE",
                    rationale=(
                        f"Matched stems {matched_stems} represent unavoidable natural domain vocabulary "
                        "(e.g. 'message', 'token', 'table') necessary to express the user request. "
                        "Treating common domain nouns as leakage is an audit-rule false positive."
                    ),
                    release1_evidence=evidence,
                    remediation_required=False,
                    remediation_strategy="Allowlist common domain vocabulary in the Release 2 leakage auditor."
                )
            else:
                return AdjudicatedFinding(
                    finding_id=fid,
                    task_id=tid,
                    category=cat,
                    mutation_family=mut,
                    audit_dimension=dim,
                    audit_classification=audit_class,
                    adjudicated_category="REQUIRES_HUMAN_JUDGMENT",
                    rationale=(
                        f"Matched stems {matched_stems} may provide specific hints that distinguish "
                        "the target tool from distractors, requiring human verification."
                    ),
                    release1_evidence=evidence,
                    remediation_required=True,
                    remediation_strategy="Paraphrase prompt in Release 2 to minimize stem overlap."
                )

        # Fallback
        return AdjudicatedFinding(
            finding_id=fid,
            task_id=tid,
            category=cat,
            mutation_family=mut,
            audit_dimension=dim,
            audit_classification=audit_class,
            adjudicated_category="REQUIRES_HUMAN_JUDGMENT",
            rationale="Finding requires contextual human adjudication.",
            release1_evidence=evidence,
            remediation_required=True,
            remediation_strategy="Review during blinded validation."
        )

    def _generate_markdown_report(self, payload: Dict[str, Any]) -> None:
        """Generates narrative markdown adjudication report."""
        lines = [
            "# Stage C Release 1 Diagnostic Finding Adjudication Report",
            "",
            "## 1. Executive Summary",
            "",
            "This report documents the formal adjudication of all diagnostic findings from the Stage C",
            "Release 1 audits. Release 1 remains immutable historical evidence. The purpose of this",
            "adjudication is to separate true construct-validity defects from intentional paired experimental",
            "design reuse and audit-rule false positives, establishing rigorous specifications for Release 2.",
            "",
            f"- **Total Audit Findings Adjudicated**: `{payload['total_findings_adjudicated']}`",
            f"- **Remediation Required for Release 2**: `{payload['remediation_required_count']}`",
            "",
            "## 2. Adjudication Category Breakdown",
            "",
            "| Adjudication Category | Count | Proportion | Scientific Meaning |",
            "| :--- | :---: | :---: | :--- |",
        ]

        total = payload["total_findings_adjudicated"]
        for cat, cnt in sorted(payload["category_distribution"].items(), key=lambda x: -x[1]):
            pct = (cnt / total * 100) if total > 0 else 0
            if cat == "TRUE_CONSTRUCT_VALIDITY_DEFECT":
                meaning = "Actual leakage, unintended prompt duplication, or task ambiguity."
            elif cat == "INTENTIONAL_PAIRED_DESIGN_REUSE":
                meaning = "Intentional reuse of latent user intents across controlled mutation families."
            elif cat == "AUDIT_RULE_FALSE_POSITIVE":
                meaning = "Over-sensitive audit heuristic (e.g. synthetic wrapper keys or common domain nouns)."
            else:
                meaning = "Edge case flagged for independent human judgment."
            lines.append(f"| `{cat}` | {cnt} | {pct:.1f}% | {meaning} |")

        lines.extend([
            "",
            "## 3. Dimension-Level Adjudication Analysis",
            "",
            "| Audit Dimension | TRUE DEFECT | PAIRED REUSE | FALSE POSITIVE | HUMAN JUDGMENT | Total |",
            "| :--- | :---: | :---: | :---: | :---: | :---: |",
        ])

        for dim, counts in sorted(payload["dimension_breakdown"].items()):
            td = counts.get("TRUE_CONSTRUCT_VALIDITY_DEFECT", 0)
            pr = counts.get("INTENTIONAL_PAIRED_DESIGN_REUSE", 0)
            fp = counts.get("AUDIT_RULE_FALSE_POSITIVE", 0)
            hj = counts.get("REQUIRES_HUMAN_JUDGMENT", 0)
            subtot = td + pr + fp + hj
            lines.append(f"| `{dim}` | {td} | {pr} | {fp} | {hj} | {subtot} |")

        lines.extend([
            "",
            "## 4. Key Adjudication Findings and Release 2 Directives",
            "",
            "### 1. Tool-Name Mentions in Argument Construction",
            "- **Adjudication**: `AUDIT_RULE_FALSE_POSITIVE` for tool selection leakage; prompt styling flaw.",
            "- **Directive for Release 2**: Omit tool name from user prompt. Exactly one tool schema is presented",
            "  in available tools, which naturally defines the tool identity without artificial prompt hints.",
            "",
            "### 2. Shared Latent Intent Across Mutation Variants",
            "- **Adjudication**: `INTENTIONAL_PAIRED_DESIGN_REUSE`.",
            "- **Directive for Release 2**: Introduce explicit `paired_group_id` metadata. Evaluating the same",
            "  semantic request across base, nested, and ambiguous schema variants is the primary research goal.",
            "",
            "### 3. Duplicate Prompts within Experimental Cells",
            "- **Adjudication**: `TRUE_CONSTRUCT_VALIDITY_DEFECT`.",
            "- **Directive for Release 2**: Eliminate cyclic template repetitions. Ensure every task within the same",
            "  experimental condition has a unique prompt seed, varied parameter values, or distinct phrasing.",
            "",
            "### 4. Schema Parameter Key Overlap in User Requests",
            "- **Adjudication**: `TRUE_CONSTRUCT_VALIDITY_DEFECT`.",
            "- **Directive for Release 2**: Rephrase user prompts into natural human language. Avoid verbatim",
            "  snake_case parameter keys (e.g. `ttl_seconds`, `force_truncate`) that allow shortcut matching.",
            "",
            "### 5. Synthetic Wrapper Keys in Nested Hierarchy",
            "- **Adjudication**: `AUDIT_RULE_FALSE_POSITIVE`.",
            "- **Directive for Release 2**: Update audit rules to traverse nested objects and verify semantic values.",
            "",
            "### 6. Distractor Ambiguity in Abstention Tasks",
            "- **Adjudication**: `TRUE_CONSTRUCT_VALIDITY_DEFECT`.",
            "- **Directive for Release 2**: Filter distractor toolsets so no abstention prompt satisfies all required",
            "  parameters for any candidate tool."
        ])

        with open(OUTPUT_MD, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")


def main():
    print("Running Stage C Release 1 Finding Adjudication...")
    adj = StageCRelease1Adjudicator()
    payload = adj.adjudicate_all()
    print(f"Total findings adjudicated: {payload['total_findings_adjudicated']}")
    print(f"Category distribution: {payload['category_distribution']}")
    print(f"Artifacts written to {OUTPUT_JSON} and {OUTPUT_MD}")


if __name__ == "__main__":
    main()
