# Difference Register: SLOT_CHATWOOT_01 (create-a-webhook)

**Pipeline Version:** `2.0.0`  
**Conversion Policy:** `OAS30_TO_DRAFT07_CONVERSION_POLICY_001`  
**Source Dialect:** `OpenAPI 3.1.0`  
**Target Dialect:** `JSON Schema Draft-07`  

| Candidate Pointer | Source Pointer | Classification | Policy | Rationale |
| :--- | :--- | :--- | :--- | :--- |
| `/additionalProperties` | `#/paths/~1api~1v1~1accounts~1{account_id}~1webhooks/post` | `WRAPPER_NORMALIZATION` | `WRAPPER_CLOSED_OBJECT_POLICY_001` | Enforced additionalProperties: false at root schema under WRAPPER_CLOSED_OBJECT_POLICY_001 for strict tool-argument evaluation. |
| `/properties/body/additionalProperties` | `#/paths/~1api~1v1~1accounts~1{account_id}~1webhooks/post` | `WRAPPER_NORMALIZATION` | `WRAPPER_CLOSED_OBJECT_POLICY_001` | Synthesized canonical 'body' transport wrapper with additionalProperties: false under WRAPPER_CLOSED_OBJECT_POLICY_001. |
| `/properties/body/properties/name` | `#/components/schemas/webhook_create_update_payload/properties/name` | `PRESERVED` | `STAGE_B_EXTRACTION_SPEC.md` | Preserved request body property 'name' verbatim into canonical body container. |
| `/properties/body/properties/subscriptions` | `#/components/schemas/webhook_create_update_payload/properties/subscriptions` | `PRESERVED` | `STAGE_B_EXTRACTION_SPEC.md` | Preserved request body property 'subscriptions' verbatim into canonical body container. |
| `/properties/body/properties/url` | `#/components/schemas/webhook_create_update_payload/properties/url` | `PRESERVED` | `STAGE_B_EXTRACTION_SPEC.md` | Preserved request body property 'url' verbatim into canonical body container. |
| `/properties/header/additionalProperties` | `#/paths/~1api~1v1~1accounts~1{account_id}~1webhooks/post` | `WRAPPER_NORMALIZATION` | `WRAPPER_CLOSED_OBJECT_POLICY_001` | Synthesized canonical 'header' transport wrapper with additionalProperties: false under WRAPPER_CLOSED_OBJECT_POLICY_001. |
| `/properties/path/additionalProperties` | `#/paths/~1api~1v1~1accounts~1{account_id}~1webhooks/post` | `WRAPPER_NORMALIZATION` | `WRAPPER_CLOSED_OBJECT_POLICY_001` | Synthesized canonical 'path' transport wrapper with additionalProperties: false under WRAPPER_CLOSED_OBJECT_POLICY_001. |
| `/properties/path/properties/account_id` | `#/components/parameters/account_id` | `PRESERVED` | `STAGE_B_EXTRACTION_SPEC.md` | Preserved parameter 'account_id' verbatim into canonical path container. |
| `/properties/query/additionalProperties` | `#/paths/~1api~1v1~1accounts~1{account_id}~1webhooks/post` | `WRAPPER_NORMALIZATION` | `WRAPPER_CLOSED_OBJECT_POLICY_001` | Synthesized canonical 'query' transport wrapper with additionalProperties: false under WRAPPER_CLOSED_OBJECT_POLICY_001. |
