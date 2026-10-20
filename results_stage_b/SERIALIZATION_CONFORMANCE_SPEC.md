# Stage B Serialization Conformance Specification

## 1. Overview and Scope

This specification defines the serialization and deserialization conformance layer for the Stage B benchmark (`src/openapi_serialization.py`). In tool-augmented LLM evaluation, models generate discrete JSON arguments. However, real-world web APIs communicate across heterogeneous transport formats, including standard JSON (`application/json`) and URL-encoded forms (`application/x-www-form-urlencoded`).

The serialization layer provides deterministic, in-process transformations between in-memory function call arguments and transport-level wire representations under explicitly supported encoding policies.

---

## 2. Four-Tier Conformance Taxonomy and Epistemic Boundaries

To prevent overclaiming, this specification formally distinguishes four separate levels of conformance:

1. **Tier 1: Canonical JSON Structural Preservation**
   - *Definition:* Structural and keyword preservation between the raw OpenAPI schema and the extracted Draft-07 canonical contract.
   - *Scope:* Evaluated in-memory via schema preservation validator and difference registers.
   - *Status:* Validated for `SLOT_GITHUB_01` (under explicit wrapper policy) and pending human validation for `SLOT_STRIPE_02`.

2. **Tier 2: Local Serializer/Deserializer Representation Preservation**
   - *Definition:* Deterministic in-process round-trip between Python dictionary objects and serialized strings using the benchmark's internal parser (`src/openapi_serialization.py`).
   - *Scope:* Strictly limited to in-process execution under declared representation rules.
   - *Status:* Validated in unit test suite (`tests/test_openapi_serialization.py`).

3. **Tier 3: Actual HTTP Wire Conformance**
   - *Definition:* Conformance of serialized byte streams to the exact wire formats produced by standard HTTP clients (e.g., `requests`, `urllib3`, `curl`).
   - *Scope:* Requires live HTTP client harness and socket-level wire capture.
   - *Status:* **UNVALIDATED.** No live HTTP client wire capture has been conducted in Stage B.

4. **Tier 4: Server-Side Endpoint Semantic Acceptance**
   - *Definition:* Successful acceptance, parsing, and semantic processing of the serialized payload by live production API gateways or official SDKs (e.g., Stripe API servers).
   - *Scope:* Requires live network requests and credentialed API interaction.
   - *Status:* **UNVALIDATED.** Strictly outside current benchmark scope; no live API calls or network requests are permitted.

> **Operational Boundary:** References to round-trip fidelity in this repository refer exclusively to Tier 2 (deterministic in-process round-trip under the declared representation and supported encoding policy). They do NOT imply Tier 3 wire conformance or Tier 4 server-side acceptance.

---

## 3. Supported Formats and Standards

### 3.1 RFC 8259 JSON (`application/json`)
- Used by standard RESTful operations (e.g. GitHub `pulls/create`, Chatwoot `create-a-webhook`).
- Emitted with deterministic key sorting (`sort_keys=True`) and compact separators (`separators=(',', ':')`).
- Tier 2 bidirectional reversibility is deterministic for standard JSON data types within memory.

### 3.2 RFC 1866 URL-Encoded Forms (`application/x-www-form-urlencoded`)
- Used by form-based APIs (e.g. Stripe `PostShippingRates`, Stripe `PostPayouts`).
- Emitted using standard URL percent-encoding (`quote_plus`), mapping spaces to `+` and reserved characters to `%XX`.
- Keys are sorted deterministically in alphabetical order.

---

## 4. OpenAPI Parameter Styles and Encoding Rules

### 4.1 deepObject Style (Nested Objects and Dictionaries)
OpenAPI 3.0 specifies `style: deepObject` with `explode: true` as the canonical representation for nested object parameters in form-encoded requests.
- A nested object `{"fixed_amount": {"amount": 500, "currency": "usd"}}` is serialized as:
  `fixed_amount[amount]=500&fixed_amount[currency]=usd`
- Multi-level hierarchical nesting `{"delivery_estimate": {"minimum": {"unit": "day", "value": 3}}}` is serialized as:
  `delivery_estimate[minimum][unit]=day&delivery_estimate[minimum][value]=3`
- Dynamic string maps (e.g. Stripe `metadata: {"order_id": "6735"}`) are serialized as:
  `metadata[order_id]=6735`

### 4.2 Array Serialization Styles
1. `explode=true` with Bracket Indexing (Stripe SDK convention):
   `{"expand": ["data", "customer"]}` -> `expand[0]=data&expand[1]=customer`
2. `explode=true` with Repeated Keys (OpenAPI standard form style):
   `{"expand": ["data", "customer"]}` -> `expand=data&expand=customer`
3. `explode=false` with Comma Separation:
   `{"expand": ["data", "customer"]}` -> `expand=data,customer`

---

## 5. Reversibility and Mathematical Limits

### 5.1 Schema-Guided In-Process Round-Trip
Because URL encoding treats all leaf values as string tokens on the wire, schema-free deserialization cannot distinguish between string representations of numbers/booleans and raw string scalars:
- `amount=500` deserializes to `{"amount": "500"}` without a schema.
- `tax_behavior=true` deserializes to `{"tax_behavior": "true"}`.

When paired with a canonical Draft-07 schema (`canonical_contract.json`), the conformance layer performs deterministic type coercion:
- `type: "integer"` coerces `"500"` -> `500`
- `type: "number"` coerces `"12.5"` -> `12.5`
- `type: "boolean"` coerces `"true"` -> `True`
- `type: "array"` reconstructs parsed list items according to `items` schema.

Under schema-guided deserialization, in-process mathematical equivalence holds:
$$\text{deserialize}(\text{serialize}(\text{payload}, \text{schema}), \text{schema}) \equiv \text{payload}$$
for all supported canonical Draft-07 payload types.

### 5.2 Known Edge Cases and Boundary Conditions
1. Empty Objects: Form-urlencoded representations omit empty objects (`{}`) because no leaf key-value pairs exist.
2. Null Values: Null scalars are serialized as empty strings (`key=`) or omitted, depending on provider rules.
3. Whitespace Preservation: Leading/trailing whitespace within strings is preserved through percent-encoding.

---

## 6. Verification Against SLOT_STRIPE_02 Canonical Contract

The conformance layer is validated directly against the extracted canonical contract for `SLOT_STRIPE_02` (`PostShippingRates`):
- Contract location: `data_stage_b/canonical/SLOT_STRIPE_02/canonical_contract.json`
- Target properties tested:
  * `display_name` (string)
  * `type` (fixed string enum)
  * `fixed_amount` (nested object with amount, currency, and currency_options map)
  * `delivery_estimate` (multi-level nested object with minimum/maximum units and integer values)
  * `metadata` (dynamic key-value string map)
  * `expand` (array of strings)
- Outcome: Proves deterministic in-process round-trip under the declared representation and supported encoding policy for `SLOT_STRIPE_02` canonical payload properties.
- Non-Claim: Does not claim HTTP wire conformance or Stripe server-side acceptance, which remain unvalidated.
