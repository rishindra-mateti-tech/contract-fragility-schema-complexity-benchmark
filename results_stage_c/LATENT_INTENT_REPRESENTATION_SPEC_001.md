# Stage C Latent Intent Representation Specification (SPEC-001)

## 1. Executive Summary

This specification establishes the formal representation for latent user intent within the Stage C controlled mutation benchmark.
In conventional tool-use benchmarks, gold arguments are tightly coupled to a single concrete schema signature.
Consequently, evaluating schema transformations (such as nesting, optional parameter bloat, or identifier aliasing) risks conflating changes in prompt understanding with syntactic schema artifacts.

The Stage C architecture introduces an explicit separation between:
1. Abstract user intent (what the user desires to achieve, represented as semantic slots and constraints).
2. Concrete schema parameters (how a given interface encodes those slots into JSON parameters).
3. The semantic oracle (a deterministic judge assessing whether model-generated parameters satisfy the abstract intent).

## 2. Epistemic Scope and Decoupling Invariants

- **Synthetic Domain Grounding**: All latent intents defined in Stage C are synthetically grounded within the controlled benchmark framework.
- **Decoupling from Production APIs**: Abstract intents do not imply or depend on live external third-party service endpoints.
- **Deterministic Evaluation**: Scoring is performed via closed-form schema validation and slot-matching oracles without reliance on external LLM evaluators.
- **Fail-Closed Verification**: Any parameter generation that fails schema validation, omits a required intent slot, corrupts a slot value, or introduces unauthorized hallucinations is scored as a failure.

## 3. Data Model Architecture

The latent intent framework consists of two core structures defined in `src/stage_c_latent_intent.py`:

### 3.1 LatentSlot
Represents an individual semantic payload element:
- `name` (str): Abstract identifier of the slot (e.g., `user_id`, `ttl_seconds`).
- `value` (Any): Concrete ground-truth value requested by the user prompt.
- `data_type` (str): Expected data category (`string`, `integer`, `boolean`, `array`, `object`).
- `is_required` (bool): Whether execution is invalid without this slot.
- `description` (str): Semantic definition of the slot for prompt construction.

### 3.2 LatentIntent
Represents the complete task objective:
- `intent_id` (str): Deterministic identifier (e.g., `INTENT_SYNTH_001_01`).
- `domain` (str): Functional domain category (e.g., `data_management`, `workflow_orchestration`).
- `action` (str): Target operation or tool capability.
- `target_entity` (str): Base contract identifier.
- `slots` (Dict[str, LatentSlot]): Collection of all constituent slots.
- `constraints` (Dict[str, Any]): Additional operational constraints (e.g., bounds, required keys).
- `epistemic_provenance` (str): Frozen provenance tag `SYNTHETIC_LATENT_INTENT_REPRESENTATION`.
- `intent_hash` (str): SHA-256 digest computed over the sorted canonical representation.

## 4. Bidirectional Intent Codec (`StageCIntentCodec`)

The codec translates between abstract `LatentIntent` structures and concrete tool invocation arguments:

### 4.1 Forward Encoding (`encode_intent_to_arguments`)
- Takes an abstract `LatentIntent`.
- Projects slots to target argument paths specified by schema mappings (e.g., dot-notation paths for nested structures or aliases for ambiguous identifiers).
- Formats structured payloads conforming to the target contract parameter schema.

### 4.2 Reverse Decoding (`decode_arguments_to_intent`)
- Takes model-generated concrete tool arguments.
- Reconstructs abstract `LatentIntent` slots using inverse mappings.
- Extracts both declared arguments and unexpected top-level or nested properties.

### 4.3 Lossless Round-Trip Invariant
For any canonical contract and valid intent representation:
`decode_arguments_to_intent(encode_intent_to_arguments(intent)) == intent`
This ensures that schema variations preserve underlying semantic expressiveness without loss of user intent.

## 5. Semantic Oracle Classification Hierarchy (`StageCSemanticOracle`)

The deterministic evaluation oracle assesses candidate model invocations through a sequential decision tree:

1. **Tool Selection Evaluation**:
   - If candidate tool does not match target tool: classify as `TOOL_SELECTION_ERROR`.
2. **Invocation Well-Formedness**:
   - If candidate arguments are missing or malformed JSON: classify as `MALFORMED_INVOCATION`.
3. **JSON Schema Draft-07 Validation**:
   - Validate arguments against contract parameter schema (`additionalProperties: false`).
   - If schema validation fails: record validation errors and classify as `SCHEMA_VIOLATION`.
4. **Slot Recovery and Value Verification**:
   - Decode arguments to recovered slots.
   - Check required slots: if missing, classify as `MISSING_REQUIRED_SLOT`.
   - Check value equivalence: if any slot value is corrupted, classify as `VALUE_CORRUPTION`.
   - Check unexpected properties: if extra slots exist, classify as `HALLUCINATED_SLOT`.
5. **Success Classifications**:
   - If candidate arguments exactly match expected projection: `EXACT_MATCH`.
   - If candidate arguments satisfy schema and all slot invariants with minor non-semantic formatting differences: `SEMANTIC_EQUIVALENT`.

### 5.1 Abstention Task Handling
For tasks designated as unfulfillable or ambiguous:
- If model emits no tool call or explicitly abstains: classify as `CORRECT_ABSTENTION` (success).
- If model attempts tool invocation: classify as `FALSE_EXECUTION_UNWARRANTED` (failure).

## 6. Evaluation Metrics

The oracle computes four core metrics per task instance:
- `is_success` (bool): True if classified as `EXACT_MATCH`, `SEMANTIC_EQUIVALENT`, or `CORRECT_ABSTENTION`.
- `slot_precision` (float): Matched slots / Total candidate slots.
- `slot_recall` (float): Matched slots / Total expected slots.
- `slot_f1` (float): Harmonic mean of precision and recall.
