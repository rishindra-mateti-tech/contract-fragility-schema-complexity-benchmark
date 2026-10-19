# Stage B Semantic Preservation Report — SLOT_STRIPE_02 (PostShippingRates)

## Executive Summary
- **Benchmark Slot ID**: `SLOT_STRIPE_02`
- **Operation ID**: `PostShippingRates`
- **HTTP Route**: `POST /v1/shipping_rates`
- **Candidate Source ID**: `CAND-002`
- **Source Spec Pointer**: `#/paths/~1v1~1shipping_rates/post`
- **Request Content-Type**: `application/x-www-form-urlencoded`
- **Validation Status**: `PASS`
- **Semantic Validation Decision**: `SEMANTICALLY_VALIDATED_PENDING_HUMAN_REVIEW`
- **Benchmark Lifecycle Status**: `EXTRACTED_PENDING_HUMAN_VALIDATION`
- **Lossless Classification**: `SEMANTICALLY_EQUIVALENT_MODULO_WRAPPER_POLICY`

---

## 1. Exact Keyword Equivalence Audit
- **Total Evaluated Keyword Instances**: `50`
- **Equivalent Keywords Count**: `50`
- **Dropped Keywords Count**: `0`
- **Mismatched Keywords Count**: `0`
- **Status**: `PASS`

### Field Coverage Breakdown
- **Total Raw Input Fields**: `8`
- **Total Canonical Input Fields**: `8`
- **Covered Fields Ratio**: `100.0%`
- **Missing Fields**: `[]`
- **Extraneous Fields**: `[]`

| Parameter Name | Target Surface | Canonical JSON Pointer | Status |
| :--- | :--- | :--- | :--- |
| `delivery_estimate` | body | `/properties/body/properties/delivery_estimate` | COVERED_EQUIVALENT |
| `display_name` | body | `/properties/body/properties/display_name` | COVERED_EQUIVALENT |
| `expand` | body | `/properties/body/properties/expand` | COVERED_EQUIVALENT |
| `fixed_amount` | body | `/properties/body/properties/fixed_amount` | COVERED_EQUIVALENT |
| `metadata` | body | `/properties/body/properties/metadata` | COVERED_EQUIVALENT |
| `tax_behavior` | body | `/properties/body/properties/tax_behavior` | COVERED_EQUIVALENT |
| `tax_code` | body | `/properties/body/properties/tax_code` | COVERED_EQUIVALENT |
| `type` | body | `/properties/body/properties/type` | COVERED_EQUIVALENT |

---

## 2. Transport Wrapper Synthesis Audit
The benchmark requires unifying heterogeneous transport surfaces (URI path templates, query strings, headers, and request bodies) into a single deterministic Draft-07 tool call interface.

- **Surface Containers Present**: `['body', 'header', 'path', 'query']`
- **Path Parameters Count**: `0`
- **Body Properties Count**: `8`
- **Query Parameters Count**: `0`
- **Header Parameters Count**: `0`
- **Total Input Parameters**: `8`
- **Synthesis Status**: `PASS`

---

## 3. Closed Wrapper Policy Effects (`WRAPPER_CLOSED_OBJECT_POLICY_001`)
To prevent LLM argument hallucination and enforce rigid parameter evaluation, the canonical specification enforces `additionalProperties: false` across all root containers and transport surfaces.

- **Policy ID**: `WRAPPER_CLOSED_OBJECT_POLICY_001`
- **Root Object Closed (`additionalProperties: false`)**: `True`
- **Transport Surfaces Closed (`additionalProperties: false`)**: `True`
- **Raw Body `additionalProperties` Value**: `False`
- **Canonical Body `additionalProperties` Value**: `False`
- **Normalization Type**: `PRESERVED_EXPLICIT_FALSE`
- **Strictly Lossless**: `False`
- **Policy Evaluation Status**: `PASS`

> [!NOTE]
> When the raw OpenAPI specification explicitly declares `additionalProperties: false` (as in Stripe PostShippingRates), the body schema's closed behavior is bitwise identical to raw. For container surfaces (root, path, query, header), closing additionalProperties is a deliberate benchmark normalization that tightens schema permissiveness.

---

## 4. Form-Encoding Serialization Preservation Audit
Stripe APIs accept request payloads serialized as `application/x-www-form-urlencoded` using OpenAPI 3.0 `deepObject` style conventions for nested dictionaries and arrays.

- **Is Form-Encoded Endpoint**: `True`
- **Request Content-Type**: `application/x-www-form-urlencoded`
- **Serialization Strategy**: `FORM_URLENCODED_DEEP_OBJECT`
- **Encoding Preservation Status**: `PASS`

### Encoding Metadata Verification
| Parameter Name | Target Style | Explode | Raw Present | Canonical Present | Verification |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `delivery_estimate` | `deepObject` | `True` | Yes | Yes | PASS |
| `expand` | `deepObject` | `True` | Yes | Yes | PASS |
| `fixed_amount` | `deepObject` | `True` | Yes | Yes | PASS |
| `metadata` | `deepObject` | `True` | Yes | Yes | PASS |

---

## 5. Unsupported Constructs Audit
- **Total Unsupported Constructs Encountered**: `0`
- **Status**: `PASS`

- Zero unsupported constructs detected. All raw OpenAPI constructs mapped cleanly to Draft-07.

---

## 6. Approved Transformations Summary
- **Total Transformations Approved**: `4`

| ID | Category | Canonical Pointer | Lossless? | Rationale |
| :--- | :--- | :--- | :--- | :--- |
| `TRANSFORM_ROOT_WRAPPER_SYNTHESIS` | `BENCHMARK_WRAPPER_NORMALIZATION` | `/` | No (Policy) | HTTP operations accept inputs across URI path templates, query parameters, headers, and request bodies. The canonical representation wraps these disjoint surfaces into a single Draft-07 object with four discrete transport containers (path, query, header, body). |
| `TRANSFORM_WRAPPER_CLOSED_OBJECT` | `BENCHMARK_WRAPPER_NORMALIZATION` | `/additionalProperties` | No (Policy) | Tool-calling parameter interfaces require closed object schemas (additionalProperties: false) across root and transport surface containers to prevent LLM argument hallucination and enforce strict argument validation. Raw body schema already declared additionalProperties: false; canonical envelope extends closed validation across root and empty transport surfaces. |
| `TRANSFORM_TOOL_DESCRIPTION_SELECTION` | `DETERMINISTIC_METADATA_MAPPING` | `/description` | Yes | Selected raw operation summary per deterministic precedence hierarchy (Step 1: summary, Step 2: description, Step 3: template fallback). |
| `TRANSFORM_FORM_ENCODING_DEEP_OBJECT_METADATA` | `BENCHMARK_SERIALIZATION_PRESERVATION` | `/properties/body/x-openapi-encoding` | Yes | Stripe endpoint uses application/x-www-form-urlencoded with OpenAPI 3.0 deepObject encoding style and explode: true for complex parameters (delivery_estimate, expand, fixed_amount, metadata). The canonical contract preserves structured nested Draft-07 objects without lossy string flattening, and embeds explicit x-openapi-encoding metadata so execution drivers can serialize nested arguments faithfully. |

---

## 7. Cryptographic Continuity & Provenance
- **Raw File SHA-256**: `7cff4cc46d0654101a36a3302f7544640f5f73e4f3cad6f264f0e23c19fa1776`
- **Raw Git Blob SHA**: `f1cedf38e0178538a3c72e750da80226df41e28c`
- **Canonical Schema SHA-256**: `c7e2a3a33078a892ca861684ca963dd00a3ea7cdbd0a9cb2e215b2912547cdbc`
- **Field Lineage SHA-256**: `53dfb827902401b0928cdcb9df1c33a7f8f22fcd8ad7eb4e6421881e1cd663ac`
- **Lineage Records Count**: `27`
- **Extractor Script**: `src/extract_stage_b_canonical_contract.py`
- **Extractor Script SHA-256**: `a1416adfa296995d3ae7e73d72d2625c5f002d2b3e718f7b6e36c458fd8a6b54`
- **Extraction Rule Version**: `1.2.0`
- **Extracted At (UTC)**: `2026-10-19T18:04:16Z`

## Sign-Off State
- **Author Review Sign-Off**: `PENDING_HUMAN_VALIDATION` (No independent or author sign-off recorded until formal review packet)
- **Lifecycle Stage**: `EXTRACTED_PENDING_HUMAN_VALIDATION`

