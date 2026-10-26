# Stage B Batch Pipeline V1 to V2 Dialect Changelog

**Status:** `ENFORCED`  
**Date:** October 26, 2026  
**Governing Policy:** `OAS30_TO_DRAFT07_CONVERSION_POLICY_001`  

## 1. Dialect Conversion Summary

- **SLOT_GITHUB_02 (`repos/create-commit-status`):**
  * V1 Status: `SUPERSEDED_BY_V2_PENDING_REVIEW`
  * Issue in V1: `target_url` and `description` declared `type: "string", nullable: true` in Draft-07.
  * V2 Upgrade: Converted to `type: ["string", "null"]` and excised `nullable` keyword.
  * Lineage Classification: Updated from `SURFACE_WRAPPING` to `INTENTIONAL_REPRESENTATION_CHANGE`.

- **SLOT_BOX_01 (`post_folders`):**
  * V1 Status: `SUPERSEDED_BY_V2_PENDING_REVIEW`
  * Issue in V1: `access` and `sync_state` declared redundant `nullable: false`.
  * V2 Upgrade: Quarantined redundant keyword; retained standard primitive type.
  * Lineage Classification: `REPRESENTATION_NORMALIZATION`.

- **Remaining 11 Candidates (`SLOT_BOX_02..03`, `SLOT_CHATWOOT_01`, `SLOT_GITHUB_03`, `SLOT_LINE_01..03`, `SLOT_STRIPE_01`, `SLOT_TWILIO_01..03`):**
  * V1 Status: `SUPERSEDED_BY_V2_PENDING_REVIEW`
  * V2 Upgrade: Added V2 benchmark metadata with policy hash and verified zero unhandled dialect keywords.

## 2. Preservation Invariants

- All 13 historical V1 candidate directories under `data_stage_b/extraction_candidates/` remain permanently preserved and immutable.
- Zero modifications to Stage A artifacts or raw pinned sources.
- All V2 candidates remain strictly at `EXTRACTED_PENDING_HUMAN_VALIDATION`.
