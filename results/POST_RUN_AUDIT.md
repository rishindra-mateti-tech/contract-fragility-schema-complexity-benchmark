# Post-Run Audit: official_stage_a

## 1. Global Counts
- Total records expected: 432
- Total records actual: 432

## 2. Per Provider/Model Counts
- **Gemini:gemini-3.1-flash-lite-preview**: 144 total (Expected 144) | Task 1: 96 (Expected 96) | Task 2: 48 (Expected 48)
- **Groq:allam-2-7b**: 144 total (Expected 144) | Task 1: 96 (Expected 96) | Task 2: 48 (Expected 48)
- **Cohere:command-r-plus-08-2024**: 144 total (Expected 144) | Task 1: 96 (Expected 96) | Task 2: 48 (Expected 48)

## 3. Condition Exclusivity Check
- **Duplicates**: 0 (PASS)
- **Missing Conditions**: 0 (PASS)
- **Unexpected Conditions**: 0 (PASS)

## 4. Track Constraints
- **Track Checks**: Gemini is isolated to Track A; Groq/Cohere are isolated to Track B. (PASS)

## 5. Provenance Verification
- **Git SHA**: All records match manifest SHA `4136bbb523547e51563bc4f18cff839fa1e5bfa1`. (PASS)

### Document Hashes
- `PROTOCOL.md`: MATCH (`1d4c04b16ce07d4642256cdddfa98160bb6237aefe4b7617cc645b8aacaa5b53`)
- `PROTOCOL_AMENDMENT_001.md`: MATCH (`3b160c0488dd9527c5afe24460f219772c45df41fb6a6ac8f2e7d9ea69e11ca8`)
- `PROTOCOL_AMENDMENT_002.md`: MATCH (`5a0428c1428e5895a175cd75ad22a93f0d2ed889b018ed5fb376f332b7d9c36f`)
- `pilot_manifest.json`: MATCH (`1b6eed6b7286335bf18bf12366edfad8071e8efd8f7c73dd3def860d592ec7d4`)
- `mutated_schemas.json`: MATCH (`0ea443a22c2031eed02c2741233bb32ebe6d84ddd9da8aa9d64a6efe5eaeac6e`)
- `distractor_tools.json`: MATCH (`755a4d704e5190cbaf34cbf770126eac0f59d52793b28295d1a80aecd3c53cda`)

## 6. Denominators & Error Categories
### Gemini:gemini-3.1-flash-lite-preview (Track A)
- **Unrecoverable API Failures**: 0
- **Task 1 Denominators**:
  - `canonical`: Attempted 24 | Excluded (API Failure) 0 | Evaluated 24
  - `nested_hierarchy`: Attempted 24 | Excluded (API Failure) 0 | Evaluated 24
  - `optionality_bloat`: Attempted 24 | Excluded (API Failure) 0 | Evaluated 24
  - `ambiguous_identifiers`: Attempted 24 | Excluded (API Failure) 0 | Evaluated 24
- **Task 2 Denominators**:
  - `canonical`: Attempted 24 | Excluded (API Failure) 0 | Evaluated 24
  - `ambiguous_identifiers`: Attempted 24 | Excluded (API Failure) 0 | Evaluated 24

### Groq:allam-2-7b (Track B)
- **Unrecoverable API Failures**: 0
- **Task 1 Denominators**:
  - `canonical`: Attempted 24 | Excluded (API Failure) 0 | Evaluated 24
  - `nested_hierarchy`: Attempted 24 | Excluded (API Failure) 0 | Evaluated 24
  - `optionality_bloat`: Attempted 24 | Excluded (API Failure) 0 | Evaluated 24
  - `ambiguous_identifiers`: Attempted 24 | Excluded (API Failure) 0 | Evaluated 24
- **Task 2 Denominators**:
  - `canonical`: Attempted 24 | Excluded (API Failure) 0 | Evaluated 24
  - `ambiguous_identifiers`: Attempted 24 | Excluded (API Failure) 0 | Evaluated 24

### Cohere:command-r-plus-08-2024 (Track B)
- **Unrecoverable API Failures**: 0
- **Task 1 Denominators**:
  - `canonical`: Attempted 24 | Excluded (API Failure) 0 | Evaluated 24
  - `nested_hierarchy`: Attempted 24 | Excluded (API Failure) 0 | Evaluated 24
  - `optionality_bloat`: Attempted 24 | Excluded (API Failure) 0 | Evaluated 24
  - `ambiguous_identifiers`: Attempted 24 | Excluded (API Failure) 0 | Evaluated 24
- **Task 2 Denominators**:
  - `canonical`: Attempted 24 | Excluded (API Failure) 0 | Evaluated 24
  - `ambiguous_identifiers`: Attempted 24 | Excluded (API Failure) 0 | Evaluated 24

## 7. Artifact SHA-256 Hashes
- `official_stage_a_results.json`: `a81306219627f4867e9e233a64fe1af2a6dc33a7516c3e639f671e908aa7ac98`
- `official_stage_a_manifest.json`: `9a98e41381389575f103c44503bb18d7f421aeab0a48fffe0c0e9f89849cfe4a`
- `official_stage_a_analysis.json`: `afcf0bdd375d4bb510db36ec438a73119394439b5d3dbf40e7a133ce4aac501e`
