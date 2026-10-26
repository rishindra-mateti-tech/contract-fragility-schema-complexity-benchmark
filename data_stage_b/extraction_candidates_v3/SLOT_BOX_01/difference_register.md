# Difference Register: SLOT_BOX_01 (post_folders)

**Pipeline Version:** `3.0.0`  
**Dialect Conversion Policy:** `OAS30_TO_DRAFT07_CONVERSION_POLICY_001`  
**Adapters Used:** `None`  

## 1. Structural Modifications
- Top-level closed wrapper object under `WRAPPER_CLOSED_OBJECT_POLICY_001`.

## 2. Dialect Transformations
- `#/paths/~1folders/post/requestBody/content/application/json/schema/properties/folder_upload_email/allOf/0/properties/access`: QUARANTINED_REDUNDANT_NULLABLE_FALSE
- `#/paths/~1folders/post/requestBody/content/application/json/schema/properties/sync_state`: QUARANTINED_REDUNDANT_NULLABLE_FALSE

## 3. Adapter Decisions
- Parameter `fields` (query): origin `OPERATION`, status `OPERATION_LEVEL`
