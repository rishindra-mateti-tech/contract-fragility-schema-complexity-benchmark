# Stage B Quota Pilot Audit

## Overview
This is a bounded, tiny-scale quota pilot executed on Track B validated candidates to measure real-world rate limiting behavior at a pacing of ~6 seconds between requests, capped at a hard maximum of 15 HTTP requests per provider.

## Provider Observations
### Groq
- **Endpoint Reliability**: Over 2 requests, encountered 1 errors.
- **Rate-Limit Behavior**: Fatal quota or rate-limit hit. Aborted early.
- **Estimated Minimum Runtime**: Could not be estimated stably due to early abort or errors.
- **Zero-Cost Feasibility**: Still UNKNOWN (Daily limits were explicitly not exhausted to test absolute capacity).

### Cohere
- **Endpoint Reliability**: Over 12 requests, encountered 0 errors.
- **Rate-Limit Behavior**: Remained stable across all 12 requests at 6s pacing.
- **Estimated Minimum Runtime**: The baseline execution of 5,760 total base calls (across 2 models = 2,880 calls per model) at a 6s pace equates to ~4.8 hours of active polling per model. (Total sequential pipeline ~9.6 hours).
- **Zero-Cost Feasibility**: Still UNKNOWN (Daily limits were explicitly not exhausted to test absolute capacity).
