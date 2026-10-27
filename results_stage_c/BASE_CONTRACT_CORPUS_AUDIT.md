# Stage C Synthetic Base-Contract Corpus Audit

**Generator Version:** `1.0.0`  
**Master Random Seed:** `42`  
**Total Synthetic Base Contracts:** `40`  
**Validation Status:** `100% PASS` across all contracts  

---

## 1. Stratum Distribution

| Stratum | Count | Percentage | Defining Structural Features |
| :--- | :---: | :---: | :--- |
| `SIMPLE_FLAT` | 12 | 30.0% | Flat primitive scalar properties (string, integer, boolean) with length and boundary limits. |
| `MEDIUM_ARRAYS_ENUMS` | 16 | 40.0% | Array item collections, fixed categorical enums, numeric bounds, and formatted values. |
| `NESTED_OBJECTS_SURFACES` | 12 | 30.0% | Multi-level nested object containers, arrays of sub-objects, and composite configurations. |
| **Total** | **40** | **100.0%** | Complete synthetic evaluation foundation. |

---

## 2. Functional Domain Distribution

| Domain | Contract Count | Representative Synthetic Tools |
| :--- | :---: | :--- |
| `access_governance` | 8 | Synthetic operational patterns for access governance. |
| `analytics_metrics` | 8 | Synthetic operational patterns for analytics metrics. |
| `communications` | 8 | Synthetic operational patterns for communications. |
| `data_management` | 8 | Synthetic operational patterns for data management. |
| `workflow_orchestration` | 8 | Synthetic operational patterns for workflow orchestration. |

---

## 3. Base Contract Inventory and Complexity Accounting

| Contract ID | Tool Name | Stratum | Domain | Props | Req | Depth | Has Nested | Has Arrays | Has Enums |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `BASE_SYNTH_001` | `synth_create_key_value` | `SIMPLE_FLAT` | `data_management` | 4 | 2 | 1 | False | False | False |
| `BASE_SYNTH_002` | `synth_delete_cache_entry` | `SIMPLE_FLAT` | `data_management` | 3 | 1 | 1 | False | False | False |
| `BASE_SYNTH_003` | `synth_truncate_table_slice` | `SIMPLE_FLAT` | `data_management` | 3 | 2 | 1 | False | False | False |
| `BASE_SYNTH_004` | `synth_dispatch_sms_message` | `SIMPLE_FLAT` | `communications` | 3 | 2 | 1 | False | False | False |
| `BASE_SYNTH_005` | `synth_update_call_status` | `SIMPLE_FLAT` | `communications` | 3 | 2 | 1 | False | False | False |
| `BASE_SYNTH_006` | `synth_terminate_voice_bridge` | `SIMPLE_FLAT` | `communications` | 3 | 1 | 1 | False | False | False |
| `BASE_SYNTH_007` | `synth_increment_counter_metric` | `SIMPLE_FLAT` | `analytics_metrics` | 3 | 1 | 1 | False | False | False |
| `BASE_SYNTH_008` | `synth_record_heartbeat_timestamp` | `SIMPLE_FLAT` | `analytics_metrics` | 3 | 3 | 1 | False | False | False |
| `BASE_SYNTH_009` | `synth_reset_quota_usage` | `SIMPLE_FLAT` | `analytics_metrics` | 3 | 2 | 1 | False | False | False |
| `BASE_SYNTH_010` | `synth_revoke_access_token` | `SIMPLE_FLAT` | `access_governance` | 3 | 1 | 1 | False | False | False |
| `BASE_SYNTH_011` | `synth_extend_session_lease` | `SIMPLE_FLAT` | `access_governance` | 3 | 2 | 1 | False | False | False |
| `BASE_SYNTH_012` | `synth_lock_user_account` | `SIMPLE_FLAT` | `access_governance` | 3 | 2 | 1 | False | False | False |
| `BASE_SYNTH_013` | `synth_batch_index_records` | `MEDIUM_ARRAYS_ENUMS` | `data_management` | 4 | 3 | 3 | False | True | True |
| `BASE_SYNTH_014` | `synth_archive_data_partition` | `MEDIUM_ARRAYS_ENUMS` | `data_management` | 4 | 2 | 3 | False | True | True |
| `BASE_SYNTH_015` | `synth_broadcast_alert_notification` | `MEDIUM_ARRAYS_ENUMS` | `communications` | 4 | 3 | 3 | False | True | True |
| `BASE_SYNTH_016` | `synth_enqueue_email_digest` | `MEDIUM_ARRAYS_ENUMS` | `communications` | 4 | 3 | 3 | False | True | True |
| `BASE_SYNTH_017` | `synth_register_push_token` | `MEDIUM_ARRAYS_ENUMS` | `communications` | 4 | 2 | 3 | False | True | True |
| `BASE_SYNTH_018` | `synth_query_metric_aggregate` | `MEDIUM_ARRAYS_ENUMS` | `analytics_metrics` | 4 | 3 | 3 | False | True | True |
| `BASE_SYNTH_019` | `synth_evaluate_anomaly_detector` | `MEDIUM_ARRAYS_ENUMS` | `analytics_metrics` | 4 | 3 | 3 | False | True | True |
| `BASE_SYNTH_020` | `synth_publish_metric_histogram` | `MEDIUM_ARRAYS_ENUMS` | `analytics_metrics` | 4 | 3 | 3 | False | True | True |
| `BASE_SYNTH_021` | `synth_assign_role_permissions` | `MEDIUM_ARRAYS_ENUMS` | `access_governance` | 4 | 3 | 3 | False | True | True |
| `BASE_SYNTH_022` | `synth_provision_api_credential` | `MEDIUM_ARRAYS_ENUMS` | `access_governance` | 4 | 2 | 3 | False | True | True |
| `BASE_SYNTH_023` | `synth_rotate_secret_key` | `MEDIUM_ARRAYS_ENUMS` | `access_governance` | 4 | 2 | 3 | False | True | True |
| `BASE_SYNTH_024` | `synth_trigger_pipeline_stage` | `MEDIUM_ARRAYS_ENUMS` | `workflow_orchestration` | 4 | 2 | 3 | False | True | True |
| `BASE_SYNTH_025` | `synth_cancel_workflow_task` | `MEDIUM_ARRAYS_ENUMS` | `workflow_orchestration` | 4 | 3 | 3 | False | True | True |
| `BASE_SYNTH_026` | `synth_resume_paused_execution` | `MEDIUM_ARRAYS_ENUMS` | `workflow_orchestration` | 4 | 2 | 3 | False | True | True |
| `BASE_SYNTH_027` | `synth_schedule_cron_job` | `MEDIUM_ARRAYS_ENUMS` | `workflow_orchestration` | 4 | 3 | 3 | False | True | True |
| `BASE_SYNTH_028` | `synth_dispatch_batch_worker` | `MEDIUM_ARRAYS_ENUMS` | `workflow_orchestration` | 4 | 2 | 3 | False | True | True |
| `BASE_SYNTH_029` | `synth_configure_database_replica` | `NESTED_OBJECTS_SURFACES` | `data_management` | 3 | 2 | 2 | True | False | False |
| `BASE_SYNTH_030` | `synth_execute_partition_migration` | `NESTED_OBJECTS_SURFACES` | `data_management` | 3 | 3 | 2 | True | False | False |
| `BASE_SYNTH_031` | `synth_register_storage_snapshot` | `NESTED_OBJECTS_SURFACES` | `data_management` | 3 | 3 | 2 | True | False | True |
| `BASE_SYNTH_032` | `synth_route_omnichannel_conversation` | `NESTED_OBJECTS_SURFACES` | `communications` | 3 | 2 | 4 | True | True | False |
| `BASE_SYNTH_033` | `synth_publish_webhook_event` | `NESTED_OBJECTS_SURFACES` | `communications` | 3 | 2 | 2 | True | False | False |
| `BASE_SYNTH_034` | `synth_export_timeseries_dataset` | `NESTED_OBJECTS_SURFACES` | `analytics_metrics` | 3 | 3 | 2 | True | False | True |
| `BASE_SYNTH_035` | `synth_generate_audit_scorecard` | `NESTED_OBJECTS_SURFACES` | `analytics_metrics` | 3 | 3 | 2 | True | False | True |
| `BASE_SYNTH_036` | `synth_configure_sso_identity_provider` | `NESTED_OBJECTS_SURFACES` | `access_governance` | 3 | 2 | 2 | True | False | True |
| `BASE_SYNTH_037` | `synth_enforce_security_boundary` | `NESTED_OBJECTS_SURFACES` | `access_governance` | 3 | 3 | 4 | True | True | True |
| `BASE_SYNTH_038` | `synth_orchestrate_etl_pipeline` | `NESTED_OBJECTS_SURFACES` | `workflow_orchestration` | 3 | 3 | 2 | True | False | True |
| `BASE_SYNTH_039` | `synth_manage_deployment_rollout` | `NESTED_OBJECTS_SURFACES` | `workflow_orchestration` | 3 | 3 | 2 | True | False | False |
| `BASE_SYNTH_040` | `synth_synchronize_distributed_cluster` | `NESTED_OBJECTS_SURFACES` | `workflow_orchestration` | 3 | 3 | 3 | True | True | False |

---

## 4. Strict Provenance and Epistemic Invariants

1. **Zero Production Derivation:** All 40 contracts are explicitly synthetic and generated deterministically from seed.
2. **Draft-07 Compliance:** 100% of contracts strictly validate under `jsonschema.Draft7Validator` with `additionalProperties: false`.
3. **Gold and Counterexample Verification:** Every contract supplies at least 2 valid gold parameter payloads and at least 2 invalid counterexamples verified against the schema.
4. **Zero Model Execution:** Generated purely offline without model inference or token consumption.
