# Stage B V4 Human Validation Queue

**Queue Status:** `PENDING_AUTHOR_MANUAL_REVIEW`  
**Pipeline Version:** `4.0.0`  
**Total Candidates in Queue:** 22  
**Mandatory Epistemic Boundary:** No candidate in this queue has been validated, independently audited, or elevated to `CANONICAL_FAITHFUL`. All candidates remain strictly at `EXTRACTED_PENDING_HUMAN_VALIDATION`.

---

## 1. Candidate Queue Inventory

| Queue # | Slot ID | Operation ID | Source Project | Adapters Applied | Candidate Bundle Path |
| :---: | :--- | :--- | :--- | :--- | :--- |
| 1 | `SLOT_BOX_01` | `post_folders` | CAND-005 | None | `data_stage_b/extraction_candidates_v4/SLOT_BOX_01/` |
| 2 | `SLOT_BOX_02` | `post_collaborations` | CAND-005 | None | `data_stage_b/extraction_candidates_v4/SLOT_BOX_02/` |
| 3 | `SLOT_BOX_03` | `post_users` | CAND-005 | None | `data_stage_b/extraction_candidates_v4/SLOT_BOX_03/` |
| 4 | `SLOT_CHATWOOT_01` | `create-a-webhook` | CAND-011 | ParameterInheritanceAdapter | `data_stage_b/extraction_candidates_v4/SLOT_CHATWOOT_01/` |
| 5 | `SLOT_CHATWOOT_02` | `create-an-account-user` | CAND-011 | ParameterInheritanceAdapter | `data_stage_b/extraction_candidates_v4/SLOT_CHATWOOT_02/` |
| 6 | `SLOT_CHATWOOT_03` | `create-a-conversation` | CAND-011 | ParameterInheritanceAdapter | `data_stage_b/extraction_candidates_v4/SLOT_CHATWOOT_03/` |
| 7 | `SLOT_DO_01` | `floating_ips_create` | CAND-003 | LocalReferenceResolver | `data_stage_b/extraction_candidates_v4/SLOT_DO_01/` |
| 8 | `SLOT_GITHUB_02` | `repos/create-commit-status` | CAND-001 | None | `data_stage_b/extraction_candidates_v4/SLOT_GITHUB_02/` |
| 9 | `SLOT_GITHUB_03` | `repos/create-for-authenticated-user` | CAND-001 | None | `data_stage_b/extraction_candidates_v4/SLOT_GITHUB_03/` |
| 10 | `SLOT_LINE_01` | `showLoadingAnimation` | CAND-013 | None | `data_stage_b/extraction_candidates_v4/SLOT_LINE_01/` |
| 11 | `SLOT_LINE_02` | `setWebhookEndpoint` | CAND-013 | None | `data_stage_b/extraction_candidates_v4/SLOT_LINE_02/` |
| 12 | `SLOT_LINE_03` | `markMessagesAsRead` | CAND-013 | None | `data_stage_b/extraction_candidates_v4/SLOT_LINE_03/` |
| 13 | `SLOT_MCP_SQLITE_01` | `read_query` | CAND-009 | PythonAstToolExtractor | `data_stage_b/extraction_candidates_v4/SLOT_MCP_SQLITE_01/` |
| 14 | `SLOT_MCP_SQLITE_02` | `describe_table` | CAND-009 | PythonAstToolExtractor | `data_stage_b/extraction_candidates_v4/SLOT_MCP_SQLITE_02/` |
| 15 | `SLOT_MCP_SQLITE_03` | `write_query` | CAND-009 | PythonAstToolExtractor | `data_stage_b/extraction_candidates_v4/SLOT_MCP_SQLITE_03/` |
| 16 | `SLOT_SLACK_01` | `conversations.create` | CAND-006 | OpenAPI2FormDataAdapter | `data_stage_b/extraction_candidates_v4/SLOT_SLACK_01/` |
| 17 | `SLOT_SLACK_02` | `users.profile.set` | CAND-006 | OpenAPI2FormDataAdapter | `data_stage_b/extraction_candidates_v4/SLOT_SLACK_02/` |
| 18 | `SLOT_SLACK_03` | `reminders.add` | CAND-006 | OpenAPI2FormDataAdapter | `data_stage_b/extraction_candidates_v4/SLOT_SLACK_03/` |
| 19 | `SLOT_STRIPE_01` | `PostPayouts` | CAND-002 | None | `data_stage_b/extraction_candidates_v4/SLOT_STRIPE_01/` |
| 20 | `SLOT_TWILIO_01` | `UpdateAccount` | CAND-004 | None | `data_stage_b/extraction_candidates_v4/SLOT_TWILIO_01/` |
| 21 | `SLOT_TWILIO_02` | `CreateMessage` | CAND-004 | None | `data_stage_b/extraction_candidates_v4/SLOT_TWILIO_02/` |
| 22 | `SLOT_TWILIO_03` | `CreateCall` | CAND-004 | None | `data_stage_b/extraction_candidates_v4/SLOT_TWILIO_03/` |

---

## 2. Reviewer Checklist per Bundle

Each candidate directory contains 13 required artifacts that must be reviewed:
1. `candidate_contract.json`: Verify Draft-07 syntax, property coverage, types, and constraints.
2. `field_lineage.jsonl`: Verify bidirectional traceability from raw source pointer to schema property.
3. `difference_register.md`: Review dialect conversions, parameter mergers, and adapter actions.
4. `feature_inventory.json`: Verify detected dialect keywords.
5. `serialization_characterization.json`: Verify characterization of wire format.
6. `source_reference_closure.json`: Review accessed local specification files.
7. `adapter_decisions.json`: Verify each transformation decision made by applied adapters.
8. `static_source_evidence.json`: Verify exact syntax tree span, node kind, and snippet hash.
9. `intermediate_representation.json`: Inspect normalized source-neutral representation.
10. `candidate_validation_report.md`: Review automated structural validation results.
11. `review_packet.md`: Read synthesis of all candidate properties and invariants.
12. `extraction_metadata.json`: Verify commit hash, timestamp, and policy IDs.
