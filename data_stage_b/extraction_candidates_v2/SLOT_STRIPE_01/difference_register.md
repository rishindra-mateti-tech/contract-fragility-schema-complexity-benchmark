# Difference Register: SLOT_STRIPE_01 (PostPayouts)

**Pipeline Version:** `2.0.0`  
**Conversion Policy:** `OAS30_TO_DRAFT07_CONVERSION_POLICY_001`  
**Source Dialect:** `OpenAPI 3.0.0`  
**Target Dialect:** `JSON Schema Draft-07`  

| Candidate Pointer | Source Pointer | Classification | Policy | Rationale |
| :--- | :--- | :--- | :--- | :--- |
| `/additionalProperties` | `#/paths/~1v1~1payouts/post` | `WRAPPER_NORMALIZATION` | `WRAPPER_CLOSED_OBJECT_POLICY_001` | Enforced additionalProperties: false at root schema under WRAPPER_CLOSED_OBJECT_POLICY_001 for strict tool-argument evaluation. |
| `/properties/body/additionalProperties` | `#/paths/~1v1~1payouts/post` | `WRAPPER_NORMALIZATION` | `WRAPPER_CLOSED_OBJECT_POLICY_001` | Synthesized canonical 'body' transport wrapper with additionalProperties: false under WRAPPER_CLOSED_OBJECT_POLICY_001. |
| `/properties/body/properties/amount` | `#/paths/~1v1~1payouts/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/amount` | `PRESERVED` | `STAGE_B_EXTRACTION_SPEC.md` | Preserved request body property 'amount' verbatim into canonical body container. |
| `/properties/body/properties/currency` | `#/paths/~1v1~1payouts/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/currency` | `PRESERVED` | `STAGE_B_EXTRACTION_SPEC.md` | Preserved request body property 'currency' verbatim into canonical body container. |
| `/properties/body/properties/description` | `#/paths/~1v1~1payouts/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/description` | `PRESERVED` | `STAGE_B_EXTRACTION_SPEC.md` | Preserved request body property 'description' verbatim into canonical body container. |
| `/properties/body/properties/destination` | `#/paths/~1v1~1payouts/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/destination` | `PRESERVED` | `STAGE_B_EXTRACTION_SPEC.md` | Preserved request body property 'destination' verbatim into canonical body container. |
| `/properties/body/properties/expand` | `#/paths/~1v1~1payouts/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/expand` | `PRESERVED` | `STAGE_B_EXTRACTION_SPEC.md` | Preserved request body property 'expand' verbatim into canonical body container. |
| `/properties/body/properties/metadata` | `#/paths/~1v1~1payouts/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/metadata` | `PRESERVED` | `STAGE_B_EXTRACTION_SPEC.md` | Preserved request body property 'metadata' verbatim into canonical body container. |
| `/properties/body/properties/method` | `#/paths/~1v1~1payouts/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/method` | `PRESERVED` | `STAGE_B_EXTRACTION_SPEC.md` | Preserved request body property 'method' verbatim into canonical body container. |
| `/properties/body/properties/payout_method` | `#/paths/~1v1~1payouts/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/payout_method` | `PRESERVED` | `STAGE_B_EXTRACTION_SPEC.md` | Preserved request body property 'payout_method' verbatim into canonical body container. |
| `/properties/body/properties/source_type` | `#/paths/~1v1~1payouts/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/source_type` | `PRESERVED` | `STAGE_B_EXTRACTION_SPEC.md` | Preserved request body property 'source_type' verbatim into canonical body container. |
| `/properties/body/properties/statement_descriptor` | `#/paths/~1v1~1payouts/post/requestBody/content/application~1x-www-form-urlencoded/schema/properties/statement_descriptor` | `PRESERVED` | `STAGE_B_EXTRACTION_SPEC.md` | Preserved request body property 'statement_descriptor' verbatim into canonical body container. |
| `/properties/header/additionalProperties` | `#/paths/~1v1~1payouts/post` | `WRAPPER_NORMALIZATION` | `WRAPPER_CLOSED_OBJECT_POLICY_001` | Synthesized canonical 'header' transport wrapper with additionalProperties: false under WRAPPER_CLOSED_OBJECT_POLICY_001. |
| `/properties/path/additionalProperties` | `#/paths/~1v1~1payouts/post` | `WRAPPER_NORMALIZATION` | `WRAPPER_CLOSED_OBJECT_POLICY_001` | Synthesized canonical 'path' transport wrapper with additionalProperties: false under WRAPPER_CLOSED_OBJECT_POLICY_001. |
| `/properties/query/additionalProperties` | `#/paths/~1v1~1payouts/post` | `WRAPPER_NORMALIZATION` | `WRAPPER_CLOSED_OBJECT_POLICY_001` | Synthesized canonical 'query' transport wrapper with additionalProperties: false under WRAPPER_CLOSED_OBJECT_POLICY_001. |
