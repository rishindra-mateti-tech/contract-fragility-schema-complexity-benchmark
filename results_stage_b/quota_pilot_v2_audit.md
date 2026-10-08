# Stage B Quota Pilot v2 Audit

## Overview
This v2 pilot corrects previous configuration errors by explicitly imposing `max_tokens=150` to prevent accidental quota overallocation. It exposes models to the largest realistic Stage B payloads (Task 1), highly cluttered distractor sets with deterministic shuffling (Task 2), and explicit out-of-domain abstention requests (Task 4), all bounded to 15 HTTP requests maximum.

## Provider Observations
### Groq
- **Endpoint Reliability**: Over 6 requests, encountered 0 errors.
- **Rate-Limit Behavior (RPM/TPM limits)**: Remained stable at 6s pacing. Previous 429 errors were successfully categorized as request-configuration (max_tokens overallocation) rather than pure RPM saturation.
- **Token Output Profile**: Requested capped at 150. Actual usage observed: average ~46.7 tokens per successful call.
- **Daily Quota Capacity**: UNKNOWN. This test explicitly bounded execution to 15 requests to measure pacing and configuration, not absolute limits.

### Cohere
- **Endpoint Reliability**: Over 6 requests, encountered 0 errors.
- **Rate-Limit Behavior (RPM/TPM limits)**: Remained stable at 6s pacing. Previous 429 errors were successfully categorized as request-configuration (max_tokens overallocation) rather than pure RPM saturation.
- **Token Output Profile**: Requested capped at 150. Actual usage observed: average ~83.7 tokens per successful call.
- **Daily Quota Capacity**: UNKNOWN. This test explicitly bounded execution to 15 requests to measure pacing and configuration, not absolute limits.
