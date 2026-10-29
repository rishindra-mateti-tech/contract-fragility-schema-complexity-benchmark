"""Stage C Release 2 Corpus Balance Audit Engine.

Audits Category ratios, Mutation family distributions, Complexity strata representation,
and structural metrics across all 300 Release 2 tasks.
Generates results_stage_c/RELEASE2_CORPUS_BALANCE_AUDIT.json.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
import json
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
TASKS_DIR = ROOT_DIR / "data_stage_c_release2" / "task_instances"
BASE_DIR = ROOT_DIR / "data_stage_c" / "base_contracts"
REPORT_JSON = ROOT_DIR / "results_stage_c" / "RELEASE2_CORPUS_BALANCE_AUDIT.json"


class StageCRelease2BalanceAuditor:
    """Auditor for Release 2 corpus balance and strata distributions."""

    def audit_corpus(
        self,
        tasks: List[Dict[str, Any]],
        base_contracts: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Audits Release 2 task balance and complexity distributions."""
        total = len(tasks)

        # 1. Category Distribution
        cat_counts: Dict[str, int] = {}
        for t in tasks:
            c = t.get("category", "UNKNOWN")
            cat_counts[c] = cat_counts.get(c, 0) + 1

        # 2. Mutation Family Distribution
        mut_counts: Dict[str, int] = {}
        for t in tasks:
            mf = t.get("mutation_family", "UNKNOWN")
            mut_counts[mf] = mut_counts.get(mf, 0) + 1

        # 3. Stratum Distribution
        strata_counts: Dict[str, int] = {}
        for t in tasks:
            bid = t.get("base_contract_id", "")
            base_c = base_contracts.get(bid, {})
            st = base_c.get("stratum", "UNKNOWN")
            strata_counts[st] = strata_counts.get(st, 0) + 1

        # 4. Paired Groups Count
        paired_groups = set()
        for t in tasks:
            pg = t.get("paired_group_id")
            if pg:
                paired_groups.add(pg)

        report = {
            "audit_version": "2.0.0",
            "benchmark_release": "RELEASE_2",
            "total_tasks": total,
            "category_distribution": cat_counts,
            "mutation_family_distribution": mut_counts,
            "stratum_distribution": strata_counts,
            "paired_groups_count": len(paired_groups),
            "balance_invariants_passed": (
                cat_counts.get("ARGUMENT_CONSTRUCTION") == 100
                and cat_counts.get("TOOL_SELECTION") == 100
                and cat_counts.get("ABSTENTION") == 100
                and total == 300
            )
        }

        with open(REPORT_JSON, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, sort_keys=True)

        return report


def main():
    print("Running Stage C Release 2 Corpus Balance Audit...")
    auditor = StageCRelease2BalanceAuditor()

    task_files = sorted(TASKS_DIR.glob("TASK_R2_*.json"))
    tasks = []
    for tf in task_files:
        with open(tf, "r", encoding="utf-8") as f:
            tasks.append(json.load(f))

    base_contracts = {}
    for cf in sorted(BASE_DIR.glob("BASE_SYNTH_*.json")):
        with open(cf, "r", encoding="utf-8") as f:
            c = json.load(f)
            base_contracts[c["contract_id"]] = c

    report = auditor.audit_corpus(tasks, base_contracts)
    print(f"Total tasks: {report['total_tasks']}")
    print(f"Categories: {report['category_distribution']}")
    print(f"Mutation families: {report['mutation_family_distribution']}")
    print(f"Strata: {report['stratum_distribution']}")
    print(f"Balance invariants passed: {report['balance_invariants_passed']}")
    print(f"Report written to {REPORT_JSON}")


if __name__ == "__main__":
    main()
