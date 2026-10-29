"""Stage C Release 2 Prompt Diversity Audit Engine.

Audits vocabulary entropy, type-token ratio, length distributions, and template
frame diversity across all 300 Release 2 tasks.
Generates results_stage_c/RELEASE2_PROMPT_DIVERSITY_AUDIT.json.
"""

from pathlib import Path
from typing import Any, Dict, List, Set, Tuple
import json
import math
import re
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
TASKS_DIR = ROOT_DIR / "data_stage_c_release2" / "task_instances"
REPORT_JSON = ROOT_DIR / "results_stage_c" / "RELEASE2_PROMPT_DIVERSITY_AUDIT.json"


class StageCRelease2PromptDiversityAuditor:
    """Measures lexical entropy, type-token ratio, and template repetition for Release 2."""

    @staticmethod
    def tokenize(text: str) -> List[str]:
        return re.findall(r"[a-z0-9_]+", text.lower())

    @classmethod
    def compute_entropy(cls, tokens: List[str]) -> float:
        """Computes Shannon entropy in bits over token frequency distribution."""
        if not tokens:
            return 0.0
        freqs: Dict[str, int] = {}
        for t in tokens:
            freqs[t] = freqs.get(t, 0) + 1
        total = len(tokens)
        entropy = -sum((cnt / total) * math.log2(cnt / total) for cnt in freqs.values())
        return round(entropy, 4)

    @classmethod
    def extract_template_frame(cls, text: str) -> str:
        """Extracts skeletal template frame by abstracting entity quotes and numbers."""
        masked = re.sub(r"\'[^\']*\'", "<VALUE>", text)
        masked = re.sub(r"\"[^\"]*\"", "<VALUE>", masked)
        masked = re.sub(r"\b\d+\b", "<NUM>", masked)
        return masked.strip()[:80]

    def audit_diversity(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Audits prompt diversity metrics across task suite."""
        all_tokens: List[str] = []
        char_lengths: List[int] = []
        word_lengths: List[int] = []
        template_frames: Dict[str, List[str]] = {}

        for t in tasks:
            tid = t["task_id"]
            prompt = t.get("user_prompt", "")
            tokens = self.tokenize(prompt)
            all_tokens.extend(tokens)
            char_lengths.append(len(prompt))
            word_lengths.append(len(tokens))

            frame = self.extract_template_frame(prompt)
            template_frames.setdefault(frame, []).append(tid)

        total_tokens = len(all_tokens)
        unique_tokens = len(set(all_tokens))
        ttr = round(unique_tokens / total_tokens, 4) if total_tokens > 0 else 0.0
        entropy = self.compute_entropy(all_tokens)
        mean_chars = round(sum(char_lengths) / len(char_lengths), 2) if char_lengths else 0.0
        mean_words = round(sum(word_lengths) / len(word_lengths), 2) if word_lengths else 0.0

        report = {
            "audit_version": "2.0.0",
            "benchmark_release": "RELEASE_2",
            "total_tasks": len(tasks),
            "total_tokens": total_tokens,
            "unique_tokens": unique_tokens,
            "type_token_ratio": ttr,
            "shannon_entropy_bits": entropy,
            "mean_character_length": mean_chars,
            "mean_word_length": mean_words,
            "unique_template_frames_count": len(template_frames),
            "diversity_passed": (entropy >= 4.0 and unique_tokens >= 250)
        }

        with open(REPORT_JSON, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, sort_keys=True)

        return report


def main():
    print("Running Stage C Release 2 Prompt Diversity Audit...")
    auditor = StageCRelease2PromptDiversityAuditor()

    task_files = sorted(TASKS_DIR.glob("TASK_R2_*.json"))
    tasks = []
    for tf in task_files:
        with open(tf, "r", encoding="utf-8") as f:
            tasks.append(json.load(f))

    report = auditor.audit_diversity(tasks)
    print(f"Total tokens: {report['total_tokens']}")
    print(f"Unique vocabulary: {report['unique_tokens']}")
    print(f"Type-token ratio: {report['type_token_ratio']}")
    print(f"Shannon entropy: {report['shannon_entropy_bits']} bits")
    print(f"Unique template frames: {report['unique_template_frames_count']}")
    print(f"Diversity criteria passed: {report['diversity_passed']}")
    print(f"Report written to {REPORT_JSON}")


if __name__ == "__main__":
    main()
