"""Stage C Human Review Analysis and Adjudication Master Pipeline.

Orchestrates analysis of submitted human reviews, agreement metrics,
adjudication queues, and failure mode accounting.
Outputs NO_HUMAN_REVIEW_RESULTS_PRESENT when no real reviewer submissions exist.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
import json
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.stage_c_review_agreement import StageCReviewAgreement
from src.stage_c_review_adjudication import StageCReviewAdjudication
from src.validate_stage_c_human_review_submission import StageCHumanReviewSubmissionValidator


PACKAGES_DIR = ROOT_DIR / "data_stage_c" / "reviewer_packages"
SUBMISSIONS_DIR = ROOT_DIR / "data_stage_c" / "reviewer_submissions"
RESULTS_SCHEMA = ROOT_DIR / "results_stage_c" / "HUMAN_REVIEW_RESULTS_SCHEMA.json"
RESULTS_TEMPLATE = ROOT_DIR / "results_stage_c" / "HUMAN_REVIEW_RESULTS_TEMPLATE.md"


class StageCHumanReviewAnalyzer:
    """Master evaluator for human validation review data."""

    def __init__(self):
        self.agreement_engine = StageCReviewAgreement()
        self.adjudication_engine = StageCReviewAdjudication()
        self.validator = StageCHumanReviewSubmissionValidator()

    def analyze_submissions(self, submissions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyzes real submissions or returns certified empty status."""
        if not submissions or len(submissions) < 2:
            return {
                "schema_version": "1.0.0",
                "validation_status": "NO_HUMAN_REVIEW_RESULTS_PRESENT",
                "reason": (
                    "Independent human validation is pending. At least two independent reviewer "
                    "submissions are required to compute inter-rater agreement and construct validity."
                ),
                "total_submissions_loaded": len(submissions),
                "inter_rater_agreement": {},
                "adjudication_queue": [],
                "epistemic_notice": (
                    "No human reviews have been fabricated or executed. Author self-inspection "
                    "remains strictly distinct from independent human validation."
                )
            }

        # Validate all submissions first
        for sub in submissions:
            is_valid, errors = self.validator.validate_submission_bundle(sub)
            if not is_valid:
                raise ValueError(f"Submission bundle {sub.get('reviewer_pseudonym')} invalid: {errors}")

        # Pairwise agreement between first two raters
        agreement = self.agreement_engine.compute_pairwise_agreement(submissions[0], submissions[1])
        adj_queue = self.adjudication_engine.generate_adjudication_queue(submissions[0], submissions[1])

        # Exclusions
        exclusions = [
            self.adjudication_engine.apply_reviewer_exclusion_rules(sub)
            for sub in submissions
        ]

        return {
            "schema_version": "1.0.0",
            "validation_status": "ANALYZED",
            "total_submissions_loaded": len(submissions),
            "reviewer_pseudonyms": [s.get("reviewer_pseudonym") for s in submissions],
            "inter_rater_agreement": agreement,
            "adjudication_queue_size": len(adj_queue),
            "adjudication_queue": adj_queue,
            "reviewer_exclusions": exclusions,
            "epistemic_notice": "Independent human review analysis executed on verified submissions."
        }


def main():
    analyzer = StageCHumanReviewAnalyzer()
    SUBMISSIONS_DIR.mkdir(parents=True, exist_ok=True)

    submission_files = list(SUBMISSIONS_DIR.glob("*.json"))
    submissions = []
    for sf in submission_files:
        with open(sf, "r", encoding="utf-8") as f:
            submissions.append(json.load(f))

    print(f"Loaded {len(submissions)} real reviewer submissions.")
    results = analyzer.analyze_submissions(submissions)
    print(f"Status: {results['validation_status']}")


if __name__ == "__main__":
    main()
