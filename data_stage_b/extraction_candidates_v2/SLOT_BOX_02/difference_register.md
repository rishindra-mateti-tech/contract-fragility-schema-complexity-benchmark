# Difference Register: SLOT_BOX_02 (post_collaborations)

**Pipeline Version:** `2.0.0`  
**Conversion Policy:** `OAS30_TO_DRAFT07_CONVERSION_POLICY_001`  
**Source Dialect:** `OpenAPI 3.0.2`  
**Target Dialect:** `JSON Schema Draft-07`  

| Candidate Pointer | Source Pointer | Classification | Policy | Rationale |
| :--- | :--- | :--- | :--- | :--- |
| `/additionalProperties` | `#/paths/~1collaborations/post` | `WRAPPER_NORMALIZATION` | `WRAPPER_CLOSED_OBJECT_POLICY_001` | Enforced additionalProperties: false at root schema under WRAPPER_CLOSED_OBJECT_POLICY_001 for strict tool-argument evaluation. |
| `/properties/body/additionalProperties` | `#/paths/~1collaborations/post` | `WRAPPER_NORMALIZATION` | `WRAPPER_CLOSED_OBJECT_POLICY_001` | Synthesized canonical 'body' transport wrapper with additionalProperties: false under WRAPPER_CLOSED_OBJECT_POLICY_001. |
| `/properties/body/properties/accessible_by` | `#/paths/~1collaborations/post/requestBody/content/application~1json/schema/properties/accessible_by` | `PRESERVED` | `STAGE_B_EXTRACTION_SPEC.md` | Preserved request body property 'accessible_by' verbatim into canonical body container. |
| `/properties/body/properties/can_view_path` | `#/paths/~1collaborations/post/requestBody/content/application~1json/schema/properties/can_view_path` | `PRESERVED` | `STAGE_B_EXTRACTION_SPEC.md` | Preserved request body property 'can_view_path' verbatim into canonical body container. |
| `/properties/body/properties/expires_at` | `#/paths/~1collaborations/post/requestBody/content/application~1json/schema/properties/expires_at` | `PRESERVED` | `STAGE_B_EXTRACTION_SPEC.md` | Preserved request body property 'expires_at' verbatim into canonical body container. |
| `/properties/body/properties/is_access_only` | `#/paths/~1collaborations/post/requestBody/content/application~1json/schema/properties/is_access_only` | `PRESERVED` | `STAGE_B_EXTRACTION_SPEC.md` | Preserved request body property 'is_access_only' verbatim into canonical body container. |
| `/properties/body/properties/item` | `#/paths/~1collaborations/post/requestBody/content/application~1json/schema/properties/item` | `PRESERVED` | `STAGE_B_EXTRACTION_SPEC.md` | Preserved request body property 'item' verbatim into canonical body container. |
| `/properties/body/properties/role` | `#/paths/~1collaborations/post/requestBody/content/application~1json/schema/properties/role` | `PRESERVED` | `STAGE_B_EXTRACTION_SPEC.md` | Preserved request body property 'role' verbatim into canonical body container. |
| `/properties/header/additionalProperties` | `#/paths/~1collaborations/post` | `WRAPPER_NORMALIZATION` | `WRAPPER_CLOSED_OBJECT_POLICY_001` | Synthesized canonical 'header' transport wrapper with additionalProperties: false under WRAPPER_CLOSED_OBJECT_POLICY_001. |
| `/properties/path/additionalProperties` | `#/paths/~1collaborations/post` | `WRAPPER_NORMALIZATION` | `WRAPPER_CLOSED_OBJECT_POLICY_001` | Synthesized canonical 'path' transport wrapper with additionalProperties: false under WRAPPER_CLOSED_OBJECT_POLICY_001. |
| `/properties/query/additionalProperties` | `#/paths/~1collaborations/post` | `WRAPPER_NORMALIZATION` | `WRAPPER_CLOSED_OBJECT_POLICY_001` | Synthesized canonical 'query' transport wrapper with additionalProperties: false under WRAPPER_CLOSED_OBJECT_POLICY_001. |
| `/properties/query/properties/fields` | `#/paths/~1collaborations/post/parameters/0` | `PRESERVED` | `STAGE_B_EXTRACTION_SPEC.md` | Preserved parameter 'fields' verbatim into canonical query container. |
| `/properties/query/properties/notify` | `#/paths/~1collaborations/post/parameters/1` | `PRESERVED` | `STAGE_B_EXTRACTION_SPEC.md` | Preserved parameter 'notify' verbatim into canonical query container. |
