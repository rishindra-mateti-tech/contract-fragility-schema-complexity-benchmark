# Difference Register: SLOT_GITHUB_02 (repos/create-commit-status)

**Pipeline Version:** `3.0.0`  
**Dialect Conversion Policy:** `OAS30_TO_DRAFT07_CONVERSION_POLICY_001`  
**Adapters Used:** `None`  

## 1. Structural Modifications
- Top-level closed wrapper object under `WRAPPER_CLOSED_OBJECT_POLICY_001`.

## 2. Dialect Transformations
- `#/paths/~1repos~1{owner}~1{repo}~1statuses~1{sha}/post/requestBody/content/application/json/schema/properties/description`: NULLABLE_TO_MULTI_TYPE
- `#/paths/~1repos~1{owner}~1{repo}~1statuses~1{sha}/post/requestBody/content/application/json/schema/properties/target_url`: NULLABLE_TO_MULTI_TYPE

## 3. Adapter Decisions
- Parameter `owner` (path): origin `OPERATION`, status `OPERATION_LEVEL`
- Parameter `repo` (path): origin `OPERATION`, status `OPERATION_LEVEL`
- Parameter `sha` (path): origin `OPERATION`, status `OPERATION_LEVEL`
