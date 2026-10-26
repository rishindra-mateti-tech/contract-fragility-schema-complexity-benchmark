# Difference Register: SLOT_BOX_01 (post_folders)

**Pipeline Version:** `2.0.0`  
**Conversion Policy:** `OAS30_TO_DRAFT07_CONVERSION_POLICY_001`  
**Source Dialect:** `OpenAPI 3.0.2`  
**Target Dialect:** `JSON Schema Draft-07`  

| Candidate Pointer | Source Pointer | Classification | Policy | Rationale |
| :--- | :--- | :--- | :--- | :--- |
| `/additionalProperties` | `#/paths/~1folders/post` | `WRAPPER_NORMALIZATION` | `WRAPPER_CLOSED_OBJECT_POLICY_001` | Enforced additionalProperties: false at root schema under WRAPPER_CLOSED_OBJECT_POLICY_001 for strict tool-argument evaluation. |
| `/properties/body/additionalProperties` | `#/paths/~1folders/post` | `WRAPPER_NORMALIZATION` | `WRAPPER_CLOSED_OBJECT_POLICY_001` | Synthesized canonical 'body' transport wrapper with additionalProperties: false under WRAPPER_CLOSED_OBJECT_POLICY_001. |
| `/properties/body/properties/folder_upload_email` | `#/paths/~1folders/post/requestBody/content/application~1json/schema/properties/folder_upload_email` | `PRESERVED` | `STAGE_B_EXTRACTION_SPEC.md` | Preserved request body property 'folder_upload_email' verbatim into canonical body container. |
| `/properties/body/properties/name` | `#/paths/~1folders/post/requestBody/content/application~1json/schema/properties/name` | `PRESERVED` | `STAGE_B_EXTRACTION_SPEC.md` | Preserved request body property 'name' verbatim into canonical body container. |
| `/properties/body/properties/parent` | `#/paths/~1folders/post/requestBody/content/application~1json/schema/properties/parent` | `PRESERVED` | `STAGE_B_EXTRACTION_SPEC.md` | Preserved request body property 'parent' verbatim into canonical body container. |
| `/properties/body/properties/sync_state` | `#/paths/~1folders/post/requestBody/content/application~1json/schema/properties/sync_state` | `WRAPPER_NORMALIZATION` | `results_stage_b/OAS30_TO_DRAFT07_CONVERSION_POLICY_001.md` | Quarantined redundant OpenAPI 3.0 'nullable: false' keyword. |
| `/properties/header/additionalProperties` | `#/paths/~1folders/post` | `WRAPPER_NORMALIZATION` | `WRAPPER_CLOSED_OBJECT_POLICY_001` | Synthesized canonical 'header' transport wrapper with additionalProperties: false under WRAPPER_CLOSED_OBJECT_POLICY_001. |
| `/properties/path/additionalProperties` | `#/paths/~1folders/post` | `WRAPPER_NORMALIZATION` | `WRAPPER_CLOSED_OBJECT_POLICY_001` | Synthesized canonical 'path' transport wrapper with additionalProperties: false under WRAPPER_CLOSED_OBJECT_POLICY_001. |
| `/properties/query/additionalProperties` | `#/paths/~1folders/post` | `WRAPPER_NORMALIZATION` | `WRAPPER_CLOSED_OBJECT_POLICY_001` | Synthesized canonical 'query' transport wrapper with additionalProperties: false under WRAPPER_CLOSED_OBJECT_POLICY_001. |
| `/properties/query/properties/fields` | `#/paths/~1folders/post/parameters/0` | `PRESERVED` | `STAGE_B_EXTRACTION_SPEC.md` | Preserved parameter 'fields' verbatim into canonical query container. |
