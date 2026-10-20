# Candidate Validation Report - SLOT_CHATWOOT_01 (create-a-webhook)

## 1. Candidate Identification
- **Slot ID**: `SLOT_CHATWOOT_01`
- **Operation ID**: `create-a-webhook`
- **Source Candidate**: `CAND-011`
- **Cluster**: `CLUSTER_CHATWOOT`
- **Lifecycle Status**: `EXTRACTED_PENDING_HUMAN_VALIDATION`
- **Creation Mode**: `BATCH_GENERATED_CANDIDATE`
- **Independent Validation Claimed**: `False`

## 2. Automated Integrity Audit
- **Source File SHA-256**: `c8cba6e5975ee286593866f20652e29154717b835dc6324af7433bb497e7ab43`
- **Source Git Blob SHA**: `b0b3ca6332f0627a1fe7e4e8db5bd92ac4e77589`
- **Canonical Schema SHA-256**: `d6fe73560320f90be65fa78122e2198117d127709a44899ca25e25c91c8b07cd`
- **Field Lineage SHA-256**: `071c8048a170b913656df41ac3963d104bf2eed317e1f741d6c72391a0b71e09`
- **Difference Register SHA-256**: `63b3cbeae1514be1ad548c7ddc3821e55e07ab7eb55f840c7b23f4d5b11f9391`
- **Feature Inventory SHA-256**: `622c9ee52f60ea1125c7dbb35ae063069391f6eb76c5ddff64dcef7639c4e834`
- **Serialization Characterization SHA-256**: `27cc939af568050f09e4262c281d242dd3703185e407581662e4d767cb3dbcae`

## 3. Surface Summary
- **Path Parameters**: 1 (required: ['account_id'])
- **Query Parameters**: 0 (required: [])
- **Header Parameters**: 0 (required: [])
- **Body Properties**: 3 (required: [])
- **Total Properties**: 4
- **Nesting Depth**: 3

## 4. Normalization and Wrapper Policy Review
- All root and transport containers are closed with `additionalProperties: false` under `WRAPPER_CLOSED_OBJECT_POLICY_001`.
- This transformation is an explicit, non-lossless benchmark normalization for strict tool argument evaluation.
