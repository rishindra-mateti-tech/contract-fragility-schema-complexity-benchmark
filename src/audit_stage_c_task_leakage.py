"""Stage C Task Leakage and Shortcut Audit Engine.

Audits all 300 Release 1 task instances across 14 pre-registered leakage dimensions:
1. Exact target tool-name leakage
2. Target tool-name substring / stem leakage
3. Exact schema field-name leakage (distinguishing domain vocabulary from shortcut keys)
4. Mutation-family label leakage
5. Gold argument value raw verbatim copying
6. Distractor lexical contrast
7. Fixed target position / order bias
8. Duplicate or near-duplicate task prompts
9. Duplicate latent intents with conflicting gold outputs
10. Abstention tasks containing a semantically valid tool
11. Selection tasks with multiple equally valid tools
12. Construction tasks omitting required gold semantic values
13. Prompt wording exposing canonical vs mutated schema family
14. Metadata / internal hash leakage into model-facing payloads
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
import copy
import json
import re
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.stage_c_leakage_features import (
    StageCLeakageFeatures,
    LeakageFinding,
    COMMON_DOMAIN_VOCABULARY
)


TASKS_DIR = ROOT_DIR / "data_stage_c" / "task_instances"
REPORT_JSON = ROOT_DIR / "results_stage_c" / "TASK_LEAKAGE_AUDIT_RELEASE1.json"
REPORT_MD = ROOT_DIR / "results_stage_c" / "TASK_LEAKAGE_AUDIT_RELEASE1.md"


class StageCTaskLeakageAuditor:
    """Comprehensive auditor for shortcut and leakage vulnerabilities in benchmark tasks."""

    def __init__(self):
        self.features = StageCLeakageFeatures()

    def audit_all_tasks(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Runs the full 14-dimension leakage audit across all task instances."""
        all_findings: List[LeakageFinding] = []
        task_summaries: Dict[str, Dict[str, Any]] = {}
        prompt_seen: Dict[str, List[str]] = {}
        intent_seen: Dict[str, List[Tuple[str, Any]]] = {}

        # First pass: collect per-task features and global index maps
        for t in tasks:
            tid = t["task_id"]
            prompt = t.get("user_prompt", "")
            prompt_seen.setdefault(prompt.strip(), []).append(tid)

            intent_dict = t.get("expected_latent_intent")
            if intent_dict:
                ihash = intent_dict.get("intent_hash", "")
                if ihash:
                    intent_seen.setdefault(ihash, []).append((tid, t.get("expected_arguments")))

        # Dimension 7: Global Positional Bias Analysis across Selection Tasks
        selection_tasks = [t for t in tasks if t.get("category") == "TOOL_SELECTION"]
        position_counts: Dict[int, int] = {}
        for st in selection_tasks:
            expected_tool = st.get("expected_tool_name")
            available = [tool["tool_name"] for tool in st.get("available_tools", [])]
            if expected_tool in available:
                pos = available.index(expected_tool)
                position_counts[pos] = position_counts.get(pos, 0) + 1

        # Second pass: audit each task
        for t in tasks:
            tid = t["task_id"]
            cat = t.get("category", "")
            prompt = t.get("user_prompt", "")
            expected_tool = t.get("expected_tool_name")
            expected_args = t.get("expected_arguments") or {}
            available_tools = t.get("available_tools", [])
            mutation_family = t.get("mutation_family", "")

            task_findings: List[LeakageFinding] = []

            # 1. Exact Tool Name Leakage
            exact_leak, stem_leak, matched_stems = self.features.check_tool_name_leakage(prompt, expected_tool)
            if exact_leak:
                task_findings.append(LeakageFinding(
                    task_id=tid,
                    dimension="TOOL_NAME_EXACT_LEAK",
                    severity="HIGH" if cat == "TOOL_SELECTION" else "MEDIUM",
                    classification="INVALID" if cat == "TOOL_SELECTION" else "REQUIRES_HUMAN_REVIEW",
                    evidence=f"Exact tool name '{expected_tool}' appears in prompt.",
                    span=expected_tool,
                    remediation_category="MASK_TOOL_NAME",
                    requires_human_review=True,
                    details={"tool_name": expected_tool, "category": cat}
                ))

            # 2. Substring / Stem Tool Name Leakage
            elif stem_leak:
                task_findings.append(LeakageFinding(
                    task_id=tid,
                    dimension="TOOL_NAME_SUBSTRING_LEAK",
                    severity="MEDIUM" if cat == "TOOL_SELECTION" else "LOW",
                    classification="REQUIRES_HUMAN_REVIEW",
                    evidence=f"Meaningful tool stems {matched_stems} appear in prompt.",
                    span=", ".join(matched_stems),
                    remediation_category="PARAPHRASE_VOCABULARY",
                    requires_human_review=True,
                    details={"matched_stems": matched_stems}
                ))

            # 3. Exact Field Name Leakage
            target_tool_decl = next((tl for tl in available_tools if tl.get("tool_name") == expected_tool), None)
            target_props = target_tool_decl.get("schema", {}).get("properties", {}) if target_tool_decl else {}
            field_leaks = self.features.check_field_name_leakage(prompt, target_props)

            shortcut_field_leaks = [f for f, kind in field_leaks if kind == "SHORTCUT_LEAK"]
            domain_field_leaks = [f for f, kind in field_leaks if kind == "UNAVOIDABLE_DOMAIN_WORD"]

            if shortcut_field_leaks:
                task_findings.append(LeakageFinding(
                    task_id=tid,
                    dimension="FIELD_NAME_EXACT_LEAK",
                    severity="MEDIUM",
                    classification="REQUIRES_HUMAN_REVIEW",
                    evidence=f"Schema parameter keys {shortcut_field_leaks} matched verbatim in prompt text.",
                    span=", ".join(shortcut_field_leaks),
                    remediation_category="PARAPHRASE_VOCABULARY",
                    requires_human_review=True,
                    details={"shortcut_keys": shortcut_field_leaks, "domain_words": domain_field_leaks}
                ))

            # 4. Mutation Family Label Leakage
            mut_leaks = self.features.check_mutation_label_leakage(prompt)
            if mut_leaks:
                task_findings.append(LeakageFinding(
                    task_id=tid,
                    dimension="MUTATION_LABEL_LEAK",
                    severity="HIGH",
                    classification="INVALID",
                    evidence=f"Internal mutation family labels {mut_leaks} leaked into prompt.",
                    span=", ".join(mut_leaks),
                    remediation_category="PARAPHRASE_VOCABULARY",
                    requires_human_review=True,
                    details={"leaked_labels": mut_leaks}
                ))

            # 5. Raw Gold Argument Verbatim JSON Copy
            raw_json_str = json.dumps(expected_args)
            if len(raw_json_str) > 10 and raw_json_str in prompt:
                task_findings.append(LeakageFinding(
                    task_id=tid,
                    dimension="GOLD_VALUE_VERBATIM_COPY",
                    severity="CRITICAL",
                    classification="INVALID",
                    evidence="Exact JSON argument dictionary serialized verbatim in user prompt.",
                    span=raw_json_str,
                    remediation_category="MARK_INVALID_REPLACE",
                    requires_human_review=False,
                    details={"raw_json": raw_json_str}
                ))

            # 6. Distractor Lexical Contrast (for Selection tasks)
            if cat == "TOOL_SELECTION" and len(available_tools) > 1:
                target_desc_len = len(target_tool_decl.get("description", "")) if target_tool_decl else 0
                distractor_descs = [len(tl.get("description", "")) for tl in available_tools if tl.get("tool_name") != expected_tool]
                if distractor_descs:
                    avg_dist_len = sum(distractor_descs) / len(distractor_descs)
                    if avg_dist_len > 0 and (target_desc_len / avg_dist_len > 3.0 or target_desc_len / avg_dist_len < 0.33):
                        task_findings.append(LeakageFinding(
                            task_id=tid,
                            dimension="DISTRACTOR_LEXICAL_CONTRAST",
                            severity="LOW",
                            classification="REQUIRES_HUMAN_REVIEW",
                            evidence=f"Target tool description length ({target_desc_len}) diverges substantially from distractors (avg {avg_dist_len:.1f}).",
                            span=target_tool_decl.get("description", "")[:50],
                            remediation_category="ISOLATE_DISTRACTOR",
                            requires_human_review=True,
                            details={"target_len": target_desc_len, "avg_distractor_len": avg_dist_len}
                        ))

            # 7. Positional Bias (Per Task)
            if cat == "TOOL_SELECTION" and expected_tool:
                avail_names = [tl["tool_name"] for tl in available_tools]
                if expected_tool in avail_names:
                    pos = avail_names.index(expected_tool)
                    # If target is always at index 0 across > 50% of tasks, record warning
                    if position_counts.get(0, 0) / len(selection_tasks) > 0.5 and pos == 0:
                        task_findings.append(LeakageFinding(
                            task_id=tid,
                            dimension="POSITIONAL_BIAS",
                            severity="MEDIUM",
                            classification="REQUIRES_HUMAN_REVIEW",
                            evidence=f"Target tool sits at position {pos} amidst elevated positional clustering.",
                            span=f"index_{pos}",
                            remediation_category="RANDOMIZE_POSITIONS",
                            requires_human_review=False,
                            details={"position": pos, "candidate_count": len(available_tools)}
                        ))

            # 8. Duplicate or Near-Duplicate Prompts
            matching_p = prompt_seen.get(prompt.strip(), [])
            if len(matching_p) > 1 and tid != matching_p[0]:
                task_findings.append(LeakageFinding(
                    task_id=tid,
                    dimension="DUPLICATE_PROMPTS",
                    severity="MEDIUM",
                    classification="REQUIRES_HUMAN_REVIEW",
                    evidence=f"Prompt text is identical to task {matching_p[0]}.",
                    span=prompt[:60],
                    remediation_category="PARAPHRASE_VOCABULARY",
                    requires_human_review=False,
                    details={"duplicate_of": matching_p[0]}
                ))

            # 9. Duplicate Latent Intent with Conflicting Gold Outputs
            intent_dict = t.get("expected_latent_intent")
            if intent_dict:
                ihash = intent_dict.get("intent_hash", "")
                conflicts = [item for item in intent_seen.get(ihash, []) if item[0] != tid and item[1] != expected_args]
                if conflicts:
                    task_findings.append(LeakageFinding(
                        task_id=tid,
                        dimension="INTENT_CONFLICT",
                        severity="CRITICAL",
                        classification="INVALID",
                        evidence=f"Latent intent hash matches task {conflicts[0][0]} but gold parameters differ.",
                        span=ihash,
                        remediation_category="MARK_INVALID_REPLACE",
                        requires_human_review=True,
                        details={"conflicting_task": conflicts[0][0]}
                    ))

            # 10. Abstention Task Containing Valid Tool
            if cat == "ABSTENTION":
                # Check whether prompt actually supplied all required fields for an available tool
                for cand_tool in available_tools:
                    cand_schema = cand_tool.get("schema", {})
                    req_props = cand_schema.get("required", [])
                    if req_props and all(re.search(r"\b" + re.escape(rp.lower()) + r"\b", prompt.lower()) for rp in req_props):
                        # Potential accidental validity
                        task_findings.append(LeakageFinding(
                            task_id=tid,
                            dimension="ABSTENTION_VALID_TOOL_LEAK",
                            severity="HIGH",
                            classification="AMBIGUOUS",
                            evidence=f"Prompt contains mentions of all required parameters {req_props} for candidate '{cand_tool['tool_name']}'.",
                            span=", ".join(req_props),
                            remediation_category="MARK_INVALID_REPLACE",
                            requires_human_review=True,
                            details={"candidate_tool": cand_tool["tool_name"], "required_props": req_props}
                        ))

            # 11. Selection Task with Multiple Valid Tools
            if cat == "TOOL_SELECTION" and target_tool_decl:
                target_req = set(target_tool_decl.get("schema", {}).get("required", []))
                for dist in available_tools:
                    if dist.get("tool_name") != expected_tool:
                        dist_req = set(dist.get("schema", {}).get("required", []))
                        if target_req and target_req == dist_req:
                            task_findings.append(LeakageFinding(
                                task_id=tid,
                                dimension="SELECTION_MULTIPLE_VALID_TOOLS",
                                severity="HIGH",
                                classification="AMBIGUOUS",
                                evidence=f"Target tool and distractor '{dist['tool_name']}' share identical required parameters {sorted(list(target_req))}.",
                                span=dist["tool_name"],
                                remediation_category="ISOLATE_DISTRACTOR",
                                requires_human_review=True,
                                details={"colliding_tool": dist["tool_name"], "shared_required": sorted(list(target_req))}
                            ))

            # 12. Construction Task with Omitted Gold Semantic Value
            if cat == "ARGUMENT_CONSTRUCTION" and target_tool_decl:
                req_props = target_tool_decl.get("schema", {}).get("required", [])
                missing_in_prompt = []
                for rp in req_props:
                    val = expected_args.get(rp)
                    if val is not None and str(val).lower() not in prompt.lower() and rp.lower() not in prompt.lower():
                        missing_in_prompt.append(rp)
                if missing_in_prompt:
                    task_findings.append(LeakageFinding(
                        task_id=tid,
                        dimension="CONSTRUCTION_OMITTED_GOLD_VALUE",
                        severity="HIGH",
                        classification="INVALID",
                        evidence=f"Required parameters {missing_in_prompt} have values in gold arguments that are completely absent from prompt.",
                        span=", ".join(missing_in_prompt),
                        remediation_category="MARK_INVALID_REPLACE",
                        requires_human_review=True,
                        details={"missing_required_parameters": missing_in_prompt}
                    ))

            # 13. Prompt Family Wording Leakage
            prompt_lower = prompt.lower()
            family_wording_cues = ["nested container", "bloated schema", "aliased parameter", "distractor set"]
            detected_cues = [cue for cue in family_wording_cues if cue in prompt_lower]
            if detected_cues:
                task_findings.append(LeakageFinding(
                    task_id=tid,
                    dimension="PROMPT_FAMILY_WORDING_LEAK",
                    severity="HIGH",
                    classification="INVALID",
                    evidence=f"Prompt contains structural cue phrases {detected_cues}.",
                    span=", ".join(detected_cues),
                    remediation_category="PARAPHRASE_VOCABULARY",
                    requires_human_review=True,
                    details={"detected_cues": detected_cues}
                ))

            # 14. Metadata / Internal Hash Leakage into Model-Facing Payloads
            metadata_patterns = [r"TASK_SYNTH_", r"MUT_", r"BASE_SYNTH_", r"INTENT_"]
            meta_leaks = []
            for pat in metadata_patterns:
                matches = re.findall(pat, prompt)
                if matches:
                    meta_leaks.extend(matches)
            if meta_leaks:
                task_findings.append(LeakageFinding(
                    task_id=tid,
                    dimension="METADATA_PAYLOAD_LEAK",
                    severity="CRITICAL",
                    classification="INVALID",
                    evidence=f"Benchmark internal metadata tokens {meta_leaks} detected in prompt text.",
                    span=", ".join(meta_leaks),
                    remediation_category="PARAPHRASE_VOCABULARY",
                    requires_human_review=False,
                    details={"metadata_tokens": meta_leaks}
                ))

            # Determine task overall status
            if any(f.classification == "INVALID" for f in task_findings):
                task_status = "INVALID"
            elif any(f.classification == "AMBIGUOUS" for f in task_findings):
                task_status = "AMBIGUOUS"
            elif any(f.classification == "REQUIRES_HUMAN_REVIEW" for f in task_findings):
                task_status = "REQUIRES_HUMAN_REVIEW"
            else:
                task_status = "CLEAR"

            task_summaries[tid] = {
                "task_id": tid,
                "category": cat,
                "mutation_family": mutation_family,
                "overall_status": task_status,
                "findings_count": len(task_findings),
                "findings": [f.to_dict() for f in task_findings]
            }
            all_findings.extend(task_findings)

        # Aggregate summary statistics
        status_counts = {"CLEAR": 0, "REQUIRES_HUMAN_REVIEW": 0, "AMBIGUOUS": 0, "INVALID": 0}
        for s in task_summaries.values():
            st = s["overall_status"]
            status_counts[st] = status_counts.get(st, 0) + 1

        dimension_counts: Dict[str, int] = {}
        for f in all_findings:
            dimension_counts[f.dimension] = dimension_counts.get(f.dimension, 0) + 1

        audit_manifest = {
            "audit_version": "1.0.0",
            "benchmark_release": "RELEASE_1",
            "total_tasks_audited": len(tasks),
            "status_distribution": status_counts,
            "dimension_counts": dimension_counts,
            "total_findings": len(all_findings),
            "positional_distribution": position_counts,
            "task_summaries": task_summaries
        }

        return audit_manifest


def main():
    auditor = StageCTaskLeakageAuditor()

    task_files = sorted(TASKS_DIR.glob("TASK_SYNTH_*.json"))
    tasks = []
    for tf in task_files:
        with open(tf, "r", encoding="utf-8") as f:
            tasks.append(json.load(f))

    print(f"Auditing {len(tasks)} tasks across 14 leakage dimensions...")
    manifest = auditor.audit_all_tasks(tasks)

    # Save JSON report
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_JSON, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)

    # Save Markdown report
    status_counts = manifest["status_distribution"]
    dim_counts = manifest["dimension_counts"]

    md_content = f"""# Stage C Task Leakage and Shortcut Audit Report (Release 1)

## 1. Executive Summary

- **Benchmark Release**: Release 1 (300 standardized tasks)
- **Audit Date**: 2026-10-27
- **Audited Tasks**: {manifest['total_tasks_audited']}
- **Total Diagnostic Findings**: {manifest['total_findings']}
- **Task Quality Classification Distribution**:
  - `CLEAR`: {status_counts.get('CLEAR', 0)}
  - `REQUIRES_HUMAN_REVIEW`: {status_counts.get('REQUIRES_HUMAN_REVIEW', 0)}
  - `AMBIGUOUS`: {status_counts.get('AMBIGUOUS', 0)}
  - `INVALID`: {status_counts.get('INVALID', 0)}

## 2. Leakage Dimension Findings Breakdown

| Dimension | Description | Finding Count | Typical Severity | Remediation Category |
| :--- | :--- | :---: | :---: | :--- |
| `TOOL_NAME_EXACT_LEAK` | Target tool name verbatim in prompt | {dim_counts.get('TOOL_NAME_EXACT_LEAK', 0)} | High/Med | MASK_TOOL_NAME |
| `TOOL_NAME_SUBSTRING_LEAK` | Tool stem or normalized token in prompt | {dim_counts.get('TOOL_NAME_SUBSTRING_LEAK', 0)} | Med/Low | PARAPHRASE_VOCABULARY |
| `FIELD_NAME_EXACT_LEAK` | Schema parameter keys in prompt text | {dim_counts.get('FIELD_NAME_EXACT_LEAK', 0)} | Medium | PARAPHRASE_VOCABULARY |
| `MUTATION_LABEL_LEAK` | Mutation family name in prompt | {dim_counts.get('MUTATION_LABEL_LEAK', 0)} | High | PARAPHRASE_VOCABULARY |
| `GOLD_VALUE_VERBATIM_COPY` | Verbatim JSON serialization in prompt | {dim_counts.get('GOLD_VALUE_VERBATIM_COPY', 0)} | Critical | MARK_INVALID_REPLACE |
| `DISTRACTOR_LEXICAL_CONTRAST` | Asymmetric tool description length | {dim_counts.get('DISTRACTOR_LEXICAL_CONTRAST', 0)} | Low | ISOLATE_DISTRACTOR |
| `POSITIONAL_BIAS` | Non-uniform target tool position | {dim_counts.get('POSITIONAL_BIAS', 0)} | Medium | RANDOMIZE_POSITIONS |
| `DUPLICATE_PROMPTS` | Identical prompts across distinct tasks | {dim_counts.get('DUPLICATE_PROMPTS', 0)} | Medium | PARAPHRASE_VOCABULARY |
| `INTENT_CONFLICT` | Same intent hash with conflicting gold args | {dim_counts.get('INTENT_CONFLICT', 0)} | Critical | MARK_INVALID_REPLACE |
| `ABSTENTION_VALID_TOOL_LEAK` | Abstention prompt providing valid params | {dim_counts.get('ABSTENTION_VALID_TOOL_LEAK', 0)} | High | MARK_INVALID_REPLACE |
| `SELECTION_MULTIPLE_VALID_TOOLS`| Colliding required-field signatures | {dim_counts.get('SELECTION_MULTIPLE_VALID_TOOLS', 0)} | High | ISOLATE_DISTRACTOR |
| `CONSTRUCTION_OMITTED_GOLD_VALUE`| Gold value missing entirely from prompt | {dim_counts.get('CONSTRUCTION_OMITTED_GOLD_VALUE', 0)} | High | MARK_INVALID_REPLACE |
| `PROMPT_FAMILY_WORDING_LEAK` | Prompt exposes schema mutation type | {dim_counts.get('PROMPT_FAMILY_WORDING_LEAK', 0)} | High | PARAPHRASE_VOCABULARY |
| `METADATA_PAYLOAD_LEAK` | Internal benchmark tokens in prompt | {dim_counts.get('METADATA_PAYLOAD_LEAK', 0)} | Critical | PARAPHRASE_VOCABULARY |

## 3. Methodological Observations and Distinction of Domain Vocabulary

1. **Explicit Tool Mentions in Argument Construction**:
   In Category 1 (Argument Construction), prompts explicitly reference the tool name (e.g., 'Please execute the set_cache_entry operation...').
   While this is expected behavior when isolating parameter construction in a single-tool setting, in Category 2 (Tool Selection) referencing the target tool name bypasses the selection construct. The audit flags tool mentions in selection tasks as `INVALID` and in construction tasks as `REQUIRES_HUMAN_REVIEW`.

2. **Field-Name Mentions versus Natural Language**:
   Many parameters (e.g., 'key', 'value', 'user_id', 'status') naturally occur in conversational instructions.
   The audit separates unavoidable common vocabulary from specialized parameter keys, flagging the latter for paraphrasing.

3. **Release 2 Remediation Recommendation**:
   To eliminate all potential shortcut vectors, a versioned Release 2 corpus (`data_stage_c_release2/`) should be created to:
   - Paraphrase field names with natural synonyms.
   - Strip all tool-name tokens from user prompts across all categories.
   - Positionally randomize tool selection candidate lists.
"""

    with open(REPORT_MD, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"Audit complete. Findings saved to {REPORT_JSON} and {REPORT_MD}")


if __name__ == "__main__":
    main()
