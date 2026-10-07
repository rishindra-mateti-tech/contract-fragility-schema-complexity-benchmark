# PROTOCOL_AMENDMENT_002

**Date:** October 2026  
**Reference:** PROTOCOL.md  

## Amendment Context and Adjustments
This amendment explicitly clarifies the experimental parameters for Stage A to ensure total alignment with the implemented runner and preflight results.

1. **Repeat Count & Total Calls:** Stage A execution is explicitly amended from 1 repeat to 3 repeats per condition to ensure statistical stability of the exploratory metrics. The total API call count for Stage A is exactly 432 calls (8 schemas $\times$ 6 task variants $\times$ 3 repeats $\times$ 3 models).
2. **Track Definitions:** Stage A will formally use two tracks:
   *   **Track A:** Provider-mediated function calling.
   *   **Track B:** Raw JSON hosted-model conditions (unconstrained text-to-JSON compliance on proprietary or open-weights hosted endpoints).
3. **Verified Models & Selection Rules:** The final preflighted models approved for Stage A are:
   *   Gemini (Track A): `gemini-3.1-flash-lite-preview`
   *   Cohere (Track B): `command-r-plus-08-2024` (Proprietary raw JSON hosted condition).
   *   Groq (Track B): `allam-2-7b` (Open-weights raw JSON hosted condition).
   *   *Groq Selection Rule:* The exact model ID was determined by querying the authenticated `https://api.groq.com/openai/v1/models` endpoint using the designated API key, filtering the returned JSON data array for model IDs containing `qwen`, `allam`, or `gpt-oss`, and deterministically selecting the final index `[-1]`. This ensures the model represents a verifiable, active open-weight endpoint accessible to the test key.
