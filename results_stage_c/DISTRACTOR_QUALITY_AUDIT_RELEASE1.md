# Stage C Distractor Quality and Task Ambiguity Audit Report (Release 1)

## 1. Executive Summary

- **Benchmark Release**: Release 1
- **Tasks Audited**: 200 (Tool Selection: 100, Abstention: 100)
- **Status Distribution**:
  - `CLEAR`: 197
  - `REQUIRES_HUMAN_REVIEW`: 0
  - `AMBIGUOUS`: 3
  - `INVALID`: 0
- **Signature Collision Count**: 0
- **Duplicate Tool Count**: 0

## 2. Tool Selection Distractor Calibration

- **Candidate Set Size Distribution**: {1: 100, 5: 100}
- **Target Positional Distribution**: {2: 21, 3: 19, 4: 16, 1: 27, 0: 17}
- **Positional Uniformity Assessment**: Target tool placement is distributed across index positions without degenerate single-position clustering.

## 3. Abstention Task Validity Assessment

All 100 Abstention tasks were evaluated against candidate tools.
Zero abstention tasks accidentally provided all required parameters for available candidate tools.
Each task exhibited one of the four pre-registered failure patterns:
- Missing mandatory parameters without defaults.
- Out-of-domain and destructive unsupported requests.
- Contradictory numeric bounds and limits.
- Ambiguous or underspecified requests.
