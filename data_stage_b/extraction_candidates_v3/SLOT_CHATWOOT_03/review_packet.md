# Review Packet: SLOT_CHATWOOT_03 (create-a-conversation)

**Lifecycle Status:** `EXTRACTED_PENDING_HUMAN_VALIDATION`  
**Pipeline Version:** `3.0.0`  
**Adapters Used:** `ParameterInheritanceAdapter`  

## 1. Immutable Provenance
- Source Blob SHA: `b0b3ca6332f0627a1fe7e4e8db5bd92ac4e77589`
- Source Spec Pointer: `#/paths/~1public~1api~1v1~1inboxes~1{inbox_identifier}~1contacts~1{contact_identifier}~1conversations/post`
- Candidate Contract SHA: `20000abf2bc02129a1c7d413657bb5279e51e31803bf87ca50f52cce3d5edfc8`
- Reference Closure SHA: `a8f280b111fef6d1c7785f2e0e9f6a59519defb9f94d032231ee4ba7a485fa52`

## 2. Decisions and Transformations
- Decision for `contact_identifier`: PATH_ITEM
- Decision for `inbox_identifier`: PATH_ITEM

## 3. Human Decision Options
- APPROVE_CANDIDATE_FOR_PILOT_EVALUATION
- REQUEST_CHANGES
- REJECT_CANDIDATE
