# Stage C Offline Local Human-Review Application

## 1. Overview and Operational Security

This local web application provides an offline, privacy-preserving interface for human validation of the Stage C benchmark task suite.
The application operates under the following security and integrity invariants:
- **Zero Internet Requirement**: Runs purely on localhost (`127.0.0.1`).
- **No Cloud Dependencies**: No external APIs, third-party analytics, tracking pixels, or remote databases.
- **Strict Client-Side Blinding**: Gold tool names, gold arguments, mutation family labels, and original task IDs are never embedded into HTML or JSON served to the browser.
- **Local Pseudonymity**: Reviewers are identified by locally chosen pseudonyms; no personally identifiable information (PII) is recorded.
- **Tamper-Evident Export**: Completed reviews are exported as hash-verified JSON bundles signed with SHA-256 integrity digests.

## 2. Setup and Execution Instructions

### Prerequisites
Install local dependencies:
```bash
pip install -r review_app/requirements.txt
```

### Launching the Application
From the repository root directory, run:
```bash
python review_app/app.py
```
Open a browser and navigate to:
```
http://127.0.0.1:8000
```

## 3. Reviewer Workflow

1. **Session Initialization**: Enter your assigned reviewer pseudonym (e.g., `rev_alpha`) to begin or resume a review session.
2. **Task Evaluation**:
   - Read the natural-language user prompt.
   - Inspect candidate tool definitions and JSON schemas.
   - Select the appropriate tool, or choose 'Abstain from Invocation' if the request cannot be safely fulfilled.
   - For tool calls, input valid JSON arguments.
   - Rate confidence (1 to 5) and flag potential ambiguities.
3. **Session Progress and Resumption**: Reviews are auto-saved to local disk under `review_app/sessions/`. You may pause and resume at any time.
4. **Bundle Export**: Click 'Export Completed Review Bundle' to download your signed submission file.
