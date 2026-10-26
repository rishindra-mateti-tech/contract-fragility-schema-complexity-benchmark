# Difference Register: SLOT_LINE_03 (markMessagesAsRead)

**Pipeline Version:** `2.0.0`  
**Conversion Policy:** `OAS30_TO_DRAFT07_CONVERSION_POLICY_001`  
**Source Dialect:** `OpenAPI 3.0.0`  
**Target Dialect:** `JSON Schema Draft-07`  

| Candidate Pointer | Source Pointer | Classification | Policy | Rationale |
| :--- | :--- | :--- | :--- | :--- |
| `/additionalProperties` | `#/paths/~1v2~1bot~1message~1markAsRead/post` | `WRAPPER_NORMALIZATION` | `WRAPPER_CLOSED_OBJECT_POLICY_001` | Enforced additionalProperties: false at root schema under WRAPPER_CLOSED_OBJECT_POLICY_001 for strict tool-argument evaluation. |
| `/properties/body/additionalProperties` | `#/paths/~1v2~1bot~1message~1markAsRead/post` | `WRAPPER_NORMALIZATION` | `WRAPPER_CLOSED_OBJECT_POLICY_001` | Synthesized canonical 'body' transport wrapper with additionalProperties: false under WRAPPER_CLOSED_OBJECT_POLICY_001. |
| `/properties/body/properties/chat` | `#/components/schemas/MarkMessagesAsReadRequest/properties/chat` | `PRESERVED` | `STAGE_B_EXTRACTION_SPEC.md` | Preserved request body property 'chat' verbatim into canonical body container. |
| `/properties/header/additionalProperties` | `#/paths/~1v2~1bot~1message~1markAsRead/post` | `WRAPPER_NORMALIZATION` | `WRAPPER_CLOSED_OBJECT_POLICY_001` | Synthesized canonical 'header' transport wrapper with additionalProperties: false under WRAPPER_CLOSED_OBJECT_POLICY_001. |
| `/properties/path/additionalProperties` | `#/paths/~1v2~1bot~1message~1markAsRead/post` | `WRAPPER_NORMALIZATION` | `WRAPPER_CLOSED_OBJECT_POLICY_001` | Synthesized canonical 'path' transport wrapper with additionalProperties: false under WRAPPER_CLOSED_OBJECT_POLICY_001. |
| `/properties/query/additionalProperties` | `#/paths/~1v2~1bot~1message~1markAsRead/post` | `WRAPPER_NORMALIZATION` | `WRAPPER_CLOSED_OBJECT_POLICY_001` | Synthesized canonical 'query' transport wrapper with additionalProperties: false under WRAPPER_CLOSED_OBJECT_POLICY_001. |
