"""Stage C Prompt Diversity and Template Collapse Audit Engine.

Audits vocabulary entropy, type-token ratio, length distributions,
and syntactic template reuse across the 300 task prompts.
"""

from pathlib import Path
from typing import Any, Dict, List, Set, Tuple
import json
import math
import re
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
TASKS_DIR = ROOT_DIR / "data_stage_c" / "task_instances"
REPORT_JSON = ROOT_DIR / "results_stage_c" / "PROMPT_DIVERSITY_AUDIT_RELEASE1.json"
REPORT_MD = ROOT_DIR / "results_stage_c" / "PROMPT_DIVERSITY_AUDIT_RELEASE1.md"


class StageCPromptDiversityAuditor:
    """Measures lexical entropy, type-token ratio, and template repetition."""

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
        # Take first 80 characters of structural frame
        return masked.strip()[:80]

    def audit_diversity(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Audits prompt diversity metrics across task suite."""
        all_tokens: List[str] = []
        task_metrics: List[Dict[str, Any]] = []
        template_frames: Dict[str, List[str]] = {}

        char_lengths: List[int] = []
        word_lengths: List[int] = []

        for t in tasks:
            tid = t["task_id"]
            cat = t.get("category", "")
            prompt = t.get("user_prompt", "")

            tokens = self.tokenize(prompt)
            all_tokens.extend(tokens)

            char_len = len(prompt)
            word_len = len(tokens)
            char_lengths.append(char_len)
            word_lengths.append(word_len)

            frame = self.extract_template_frame(prompt)
            template_frames.setdefault(frame, []).append(tid)

            task_metrics.append({
                "task_id": tid,
                "category": cat,
                "character_length": char_len,
                "token_length": word_len
            })

        unique_tokens = set(all_tokens)
        total_tokens = len(all_tokens)
        ttr = (len(unique_tokens) / total_tokens) if total_tokens else 0.0
        corpus_entropy = self.compute_entropy(all_tokens)

        # Detect template collapse clusters (> 10 tasks sharing same skeletal frame)
        collapsed_templates = {k: v for k, v in template_frames.items() if len(v) >= 10}

        mean_chars = (sum(char_lengths) / len(char_lengths)) if char_lengths else 0.0
        mean_words = (sum(word_lengths) / len(word_lengths)) if word_lengths else 0.0

        manifest = {
            "audit_version": "1.0.0",
            "benchmark_release": "RELEASE_1",
            "total_prompts": len(tasks),
            "total_tokens": total_tokens,
            "unique_tokens": len(unique_tokens),
            "type_token_ratio": round(ttr, 4),
            "shannon_entropy_bits": corpus_entropy,
            "length_metrics": {
                "mean_character_length": round(mean_chars, 2),
                "min_character_length": min(char_lengths) if char_lengths else 0,
                "max_character_length": max(char_lengths) if char_lengths else 0,
                "mean_token_length": round(mean_words, 2),
                "min_token_length": min(word_lengths) if word_lengths else 0,
                "max_token_length": max(word_lengths) if word_lengths else 0
            },
            "distinct_template_frames": len(template_frames),
            "collapsed_template_clusters": len(collapsed_templates),
            "collapsed_clusters_detail": {k: len(v) for k, v in collapsed_templates.items()}
        }
        return manifest


def main():
    auditor = StageCPromptDiversityAuditor()

    task_files = sorted(TASKS_DIR.glob("TASK_SYNTH_*.json"))
    tasks = []
    for tf in task_files:
        with open(tf, "r", encoding="utf-8") as f:
            tasks.append(json.load(f))

    print(f"Auditing prompt diversity and template collapse across {len(tasks)} tasks...")
    manifest = auditor.audit_diversity(tasks)

    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_JSON, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)

    # Generate Markdown Report
    len_m = manifest["length_metrics"]
    clusters = manifest["collapsed_clusters_detail"]

    cluster_rows = []
    for frame, count in clusters.items():
        cluster_rows.append(f"| `{frame}` | {count} |")

    md_content = f"""# Stage C Prompt Diversity and Template Collapse Audit Report (Release 1)

## 1. Executive Summary

- **Benchmark Release**: Release 1 (300 tasks)
- **Total Prompt Tokens**: {manifest['total_tokens']}
- **Unique Vocabulary Tokens**: {manifest['unique_tokens']}
- **Type-Token Ratio (TTR)**: {manifest['type_token_ratio']}
- **Shannon Entropy**: {manifest['shannon_entropy_bits']} bits
- **Distinct Syntactic Template Frames**: {manifest['distinct_template_frames']}
- **Template Collapse Clusters**: {manifest['collapsed_template_clusters']}

## 2. Prompt Length Distributions

- **Character Length**: Mean {len_m['mean_character_length']}, Min {len_m['min_character_length']}, Max {len_m['max_character_length']}
- **Token Length**: Mean {len_m['mean_token_length']} words, Min {len_m['min_token_length']}, Max {len_m['max_token_length']}

## 3. Template Collapse Analysis

A template collapse cluster represents a skeletal phrase repeated across 10 or more tasks.
In Release 1, synthetic task generation utilized systematic sentence constructors:

| Syntactic Template Skeleton | Cluster Task Count |
| :--- | :---: |
""" + ("\n".join(cluster_rows) if cluster_rows else "| None | 0 |\n") + """

## 4. Release 2 Recommendations
To enhance natural language diversity and eliminate template memorization:
- Introduce multi-sentence colloquial paraphrasing.
- Vary imperative, interrogative, and conditional phrasing across tasks.
- Paraphrase parameter assignments with varied relational prepositions.
"""

    with open(REPORT_MD, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"Prompt diversity audit complete. Saved to {REPORT_JSON} and {REPORT_MD}")


if __name__ == "__main__":
    main()
