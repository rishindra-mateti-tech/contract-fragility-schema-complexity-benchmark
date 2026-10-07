# Post-Run Audit: official_stage_a

## 1. Global Counts
- Total records expected: 432
- Total records actual: 432

## 2. Per Provider/Model Counts
- **Gemini:gemini-3.1-flash-lite-preview**: 144 total (Expected 144) | Task 1: 96 (Expected 96) | Task 2: 48 (Expected 48)
- **Groq:allam-2-7b**: 144 total (Expected 144) | Task 1: 96 (Expected 96) | Task 2: 48 (Expected 48)
- **Cohere:command-r-plus-08-2024**: 144 total (Expected 144) | Task 1: 96 (Expected 96) | Task 2: 48 (Expected 48)

## 3. Duplicate and Missing Condition Check
- **Duplicates**: 0 (PASS)
- **Missing Conditions**: 0 (PASS - exactly 432 unique keys)

## 4. Track Constraints
- **Track Checks**: Gemini is isolated to Track A; Groq/Cohere are isolated to Track B. (PASS)

## 5. Provenance Verification
- **Git SHA**: All records match manifest SHA `4136bbb523547e51563bc4f18cff839fa1e5bfa1`. (PASS)
- **Document Hashes**: Matches `official_stage_a_manifest.json`. (PASS)

## 6. Denominators & Error Categories
### Gemini:gemini-3.1-flash-lite-preview (Track A)
- **Errors**: 0
- **Task 1 Denominators**:
  - `canonical`: Attempted 24 | Excluded (API Error) 0 | Evaluated 24
  - `nested_hierarchy`: Attempted 24 | Excluded (API Error) 0 | Evaluated 24
  - `optionality_bloat`: Attempted 24 | Excluded (API Error) 0 | Evaluated 24
  - `ambiguous_identifiers`: Attempted 24 | Excluded (API Error) 0 | Evaluated 24
- **Task 2 Denominators**:
  - `canonical`: Attempted 24 | Excluded (API Error) 0 | Evaluated 24
  - `ambiguous_identifiers`: Attempted 24 | Excluded (API Error) 0 | Evaluated 24

### Groq:allam-2-7b (Track B)
- **Errors**: 0
- **Task 1 Denominators**:
  - `canonical`: Attempted 24 | Excluded (API Error) 0 | Evaluated 24
  - `nested_hierarchy`: Attempted 24 | Excluded (API Error) 0 | Evaluated 24
  - `optionality_bloat`: Attempted 24 | Excluded (API Error) 0 | Evaluated 24
  - `ambiguous_identifiers`: Attempted 24 | Excluded (API Error) 0 | Evaluated 24
- **Task 2 Denominators**:
  - `canonical`: Attempted 24 | Excluded (API Error) 0 | Evaluated 24
  - `ambiguous_identifiers`: Attempted 24 | Excluded (API Error) 0 | Evaluated 24

### Cohere:command-r-plus-08-2024 (Track B)
- **Errors**: 0
- **Task 1 Denominators**:
  - `canonical`: Attempted 24 | Excluded (API Error) 0 | Evaluated 24
  - `nested_hierarchy`: Attempted 24 | Excluded (API Error) 0 | Evaluated 24
  - `optionality_bloat`: Attempted 24 | Excluded (API Error) 0 | Evaluated 24
  - `ambiguous_identifiers`: Attempted 24 | Excluded (API Error) 0 | Evaluated 24
- **Task 2 Denominators**:
  - `canonical`: Attempted 24 | Excluded (API Error) 0 | Evaluated 24
  - `ambiguous_identifiers`: Attempted 24 | Excluded (API Error) 0 | Evaluated 24

## 7. Artifact SHA-256 Hashes
- `official_stage_a_results.json`: `a81306219627f4867e9e233a64fe1af2a6dc33a7516c3e639f671e908aa7ac98`
- `official_stage_a_manifest.json`: `9a98e41381389575f103c44503bb18d7f421aeab0a48fffe0c0e9f89849cfe4a`
- `official_stage_a_analysis.json`: `afcf0bdd375d4bb510db36ec438a73119394439b5d3dbf40e7a133ce4aac501e`
