# Stage B Serialization Conformance Specification

## 1. Overview and Scope

This specification defines the serialization and deserialization conformance layer for the Stage B benchmark (`src/openapi_serialization.py`). In tool-augmented LLM evaluation, models generate discrete JSON arguments. However, real-world web APIs communicate across heterogeneous transport formats, including standard JSON (`application/json`) and URL-encoded forms (`application/x-www-form-urlencoded`).

To rigorously evaluate contract fragility across transport surfaces without executing live HTTP requests or introducing stateful mock servers, the serialization layer provides deterministic, mathematically verifiable transforms between in-memory function call arguments and transport-level wire strings.

---

## 2. Supported Formats and Standards

### 2.1 RFC 8259 JSON (`application/json`)
- Used by standard RESTful operations (e.g. GitHub `pulls/create`, Chatwoot `create-a-webhook`).
- Emitted with deterministic key sorting (`sort_keys=True`) and compact separators (`separators=(',', ':')`).
- Bidirectional reversibility is 100% lossless for all standard JSON data types.

### 2.2 RFC 1866 URL-Encoded Forms (`application/x-www-form-urlencoded`)
- Used by payment gateway APIs (e.g. Stripe `PostShippingRates`, Stripe `PostPayouts`).
- Emitted using standard URL percent-encoding (`quote_plus`), mapping spaces to `+` and reserved characters to `%XX`.
- Keys are sorted deterministically in alphabetical order.

---

## 3. OpenAPI Parameter Styles and Encoding Rules

### 3.1 deepObject Style (Nested Objects and Dictionaries)
OpenAPI 3.0 specifies `style: deepObject` with `explode: true` as the canonical representation for nested object parameters in form-encoded requests.
- A nested object `{"fixed_amount": {"amount": 500, "currency": "usd"}}` is serialized as:
  `fixed_amount[amount]=500&fixed_amount[currency]=usd`
- Multi-level hierarchical nesting `{"delivery_estimate": {"minimum": {"unit": "day", "value": 3}}}` is serialized as:
  `delivery_estimate[minimum][unit]=day&delivery_estimate[minimum][value]=3`
- Dynamic string maps (e.g. Stripe `metadata: {"order_id": "6735"}`) are serialized as:
  `metadata[order_id]=6735`

### 3.2 Array Serialization Styles
1. `explode=true` with Bracket Indexing (Default Stripe Convention):
   `{"expand": ["data", "customer"]}` -> `expand[0]=data&expand[1]=customer`
2. `explode=true` with Repeated Keys (Standard OpenAPI Form Style):
   `{"expand": ["data", "customer"]}` -> `expand=data&expand=customer`
3. `explode=false` with Comma Separation:
   `{"expand": ["data", "customer"]}` -> `expand=data,customer`

---

## 4. Reversibility and Mathematical Limits

### 4.1 Schema-Guided Lossless Round-Trip
Because URL encoding treats all leaf values as string tokens on the wire, schema-free deserialization is inherently lossy:
- `amount=500` deserializes to `{"amount": "500"}` without a schema.
- `tax_behavior=true` deserializes to `{"tax_behavior": "true"}`.

When paired with a canonical Draft-07 schema (`canonical_contract.json`), the conformance layer performs deterministic type coercion:
- `type: "integer"` coerces `"500"` -> `500`
- `type: "number"` coerces `"12.5"` -> `12.5`
- `type: "boolean"` coerces `"true"` -> `True`
- `type: "array"` reconstructs parsed list items according to `items` schema.

Under schema-guided deserialization:
$$\text{deserialize}(\text{serialize}(\text{payload}, \text{schema}), \text{schema}) \equiv \text{payload}$$
for all canonical Draft-07 payloads.

### 4.2 Known Edge Cases and Boundary Conditions
1. Empty Objects: Form-urlencoded representations omit empty objects (`{}`) because no leaf key-value pairs exist.
2. Null Values: Null scalars are serialized as empty strings (`key=`) or omitted, depending on API provider requirements.
3. Whitespace Preservation: Leading/trailing whitespace within strings is preserved through percent-encoding.

---

## 5. Verification Against SLOT_STRIPE_02 Canonical Contract

The conformance layer is validated directly against the extracted canonical contract for `SLOT_STRIPE_02` (`PostShippingRates`):
- Contract location: `data_stage_b/canonical/SLOT_STRIPE_02/canonical_contract.json`
- Target properties tested:
  * `display_name` (string)
  * `type` (fixed string enum)
  * `fixed_amount` (nested object with amount, currency, and currency_options map)
  * `delivery_estimate` (multi-level nested object with minimum/maximum units and integer values)
  * `metadata` (dynamic key-value string map)
  * `expand` (array of strings)
- Outcome: Proves 100% round-trip fidelity between canonical Draft-07 arguments and Stripe form-urlencoded wire strings without mock executors or API calls.
