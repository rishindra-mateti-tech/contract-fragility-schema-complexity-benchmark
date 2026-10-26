# Review Packet: SLOT_BOX_01 (post_folders)

**Lifecycle Status:** `EXTRACTED_PENDING_HUMAN_VALIDATION`  
**Pipeline Version:** `2.0.0`  
**Conversion Policy:** `OAS30_TO_DRAFT07_CONVERSION_POLICY_001`  

## 1. Immutable Provenance
- Source Blob SHA: `e740e641b82d30e398a2a0d1b14b4c052e310422`
- Source Spec Pointer: `#/paths/~1folders/post`
- Extractor Commit: `5b7e020a91b09066fc38d5e23fbe9cab157a99b1`
- Candidate Contract SHA: `7593d0ffb8a83df44ffa3430be9b8d7f6928eeb22925c874ce8100b6b4997de8`

## 2. Dialect Transformations
- Transformation at `#/paths/~1folders/post/requestBody/content/application~1json/schema/properties/folder_upload_email/allOf/0/properties/access`: `QUARANTINE_REDUNDANT_NULLABLE`
- Transformation at `#/paths/~1folders/post/requestBody/content/application~1json/schema/properties/sync_state`: `QUARANTINE_REDUNDANT_NULLABLE`

## 3. Human Decision Options
- APPROVE_CONVERSION_AND_WRAPPER_POLICY
- REQUEST_CHANGES
- REJECT_CANDIDATE
