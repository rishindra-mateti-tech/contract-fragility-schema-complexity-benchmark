# Difference Register: SLOT_GITHUB_02 (repos/create-commit-status)

**Pipeline Version:** `2.0.0`  
**Conversion Policy:** `OAS30_TO_DRAFT07_CONVERSION_POLICY_001`  
**Source Dialect:** `OpenAPI 3.0.3`  
**Target Dialect:** `JSON Schema Draft-07`  

| Candidate Pointer | Source Pointer | Classification | Policy | Rationale |
| :--- | :--- | :--- | :--- | :--- |
| `/additionalProperties` | `#/paths/~1repos~1{owner}~1{repo}~1statuses~1{sha}/post` | `WRAPPER_NORMALIZATION` | `WRAPPER_CLOSED_OBJECT_POLICY_001` | Enforced additionalProperties: false at root schema under WRAPPER_CLOSED_OBJECT_POLICY_001 for strict tool-argument evaluation. |
| `/properties/body/additionalProperties` | `#/paths/~1repos~1{owner}~1{repo}~1statuses~1{sha}/post` | `WRAPPER_NORMALIZATION` | `WRAPPER_CLOSED_OBJECT_POLICY_001` | Synthesized canonical 'body' transport wrapper with additionalProperties: false under WRAPPER_CLOSED_OBJECT_POLICY_001. |
| `/properties/body/properties/context` | `#/paths/~1repos~1{owner}~1{repo}~1statuses~1{sha}/post/requestBody/content/application~1json/schema/properties/context` | `PRESERVED` | `STAGE_B_EXTRACTION_SPEC.md` | Preserved request body property 'context' verbatim into canonical body container. |
| `/properties/body/properties/description` | `#/paths/~1repos~1{owner}~1{repo}~1statuses~1{sha}/post/requestBody/content/application~1json/schema/properties/description` | `INTENTIONAL_REPRESENTATION_CHANGE` | `results_stage_b/OAS30_TO_DRAFT07_CONVERSION_POLICY_001.md` | Converted OpenAPI 3.0 'nullable: true' with type 'string' to Draft-07 null-inclusive type array ['string', 'null'] under Policy 001. |
| `/properties/body/properties/state` | `#/paths/~1repos~1{owner}~1{repo}~1statuses~1{sha}/post/requestBody/content/application~1json/schema/properties/state` | `PRESERVED` | `STAGE_B_EXTRACTION_SPEC.md` | Preserved request body property 'state' verbatim into canonical body container. |
| `/properties/body/properties/target_url` | `#/paths/~1repos~1{owner}~1{repo}~1statuses~1{sha}/post/requestBody/content/application~1json/schema/properties/target_url` | `INTENTIONAL_REPRESENTATION_CHANGE` | `results_stage_b/OAS30_TO_DRAFT07_CONVERSION_POLICY_001.md` | Converted OpenAPI 3.0 'nullable: true' with type 'string' to Draft-07 null-inclusive type array ['string', 'null'] under Policy 001. |
| `/properties/header/additionalProperties` | `#/paths/~1repos~1{owner}~1{repo}~1statuses~1{sha}/post` | `WRAPPER_NORMALIZATION` | `WRAPPER_CLOSED_OBJECT_POLICY_001` | Synthesized canonical 'header' transport wrapper with additionalProperties: false under WRAPPER_CLOSED_OBJECT_POLICY_001. |
| `/properties/path/additionalProperties` | `#/paths/~1repos~1{owner}~1{repo}~1statuses~1{sha}/post` | `WRAPPER_NORMALIZATION` | `WRAPPER_CLOSED_OBJECT_POLICY_001` | Synthesized canonical 'path' transport wrapper with additionalProperties: false under WRAPPER_CLOSED_OBJECT_POLICY_001. |
| `/properties/path/properties/owner` | `#/components/parameters/owner` | `PRESERVED` | `STAGE_B_EXTRACTION_SPEC.md` | Preserved parameter 'owner' verbatim into canonical path container. |
| `/properties/path/properties/repo` | `#/components/parameters/repo` | `PRESERVED` | `STAGE_B_EXTRACTION_SPEC.md` | Preserved parameter 'repo' verbatim into canonical path container. |
| `/properties/path/properties/sha` | `#/paths/~1repos~1{owner}~1{repo}~1statuses~1{sha}/post/parameters/2` | `PRESERVED` | `STAGE_B_EXTRACTION_SPEC.md` | Preserved parameter 'sha' verbatim into canonical path container. |
| `/properties/query/additionalProperties` | `#/paths/~1repos~1{owner}~1{repo}~1statuses~1{sha}/post` | `WRAPPER_NORMALIZATION` | `WRAPPER_CLOSED_OBJECT_POLICY_001` | Synthesized canonical 'query' transport wrapper with additionalProperties: false under WRAPPER_CLOSED_OBJECT_POLICY_001. |
