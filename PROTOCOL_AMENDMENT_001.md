# PROTOCOL_AMENDMENT_001

**Date:** October 2026  
**Reference:** PROTOCOL.md  

## Amendment Context and Adjustments
Due to verifiable access and quota limitations on the currently available free-tier API keys, the initially planned three-provider, functionally-equivalent design cannot be executed. The experimental protocol is hereby amended prior to any API benchmark execution.

1. **Provider Feasibility Limitation:** The planned three-provider (provider-mediated) design cannot be executed with the currently verified free access. (SambaNova returned a zero-balance error and is excluded. Groq and Cohere exhibit restricted or incompatible access to native tool-calling endpoints on the available keys).
2. **Dual-Track Evaluation Design:** Stage A will formally proceed using two distinct tracks:
   *   **Track A:** Provider-mediated function calling (Gemini `gemini-3.1-flash-lite-preview`).
   *   **Track B:** Raw JSON unconstrained generation (prompt-engineered structural compliance) on each successfully preflighted hosted model (e.g., Groq, Cohere).
3. **Strict Track Isolation:** Experimental results and statistical tests will never compare Track A (Provider-Mediated) directly against Track B (Raw JSON) as if they were equivalent conditions. The structural affordances of vendor middleware explicitly prevent a 1:1 comparison with raw transformer attention.
4. **Scope of Claims:** Any derived empirical conclusion, including hypotheses regarding schema fragility and predictive validation, will be strictly limited to the available models and their respective evaluated tracks.
