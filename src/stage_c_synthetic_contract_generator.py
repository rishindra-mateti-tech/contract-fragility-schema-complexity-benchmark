#!/usr/bin/env python3
"""Stage C Synthetic Base-Contract Generator.

Deterministically synthesizes a corpus of at least 40 synthetic base contracts
spanning controlled strata (flat, medium with arrays/enums, nested objects),
5 functional domains, valid gold examples, invalid counterexamples,
Draft-07 schema specifications, and latent intent definitions.
"""

import copy
import hashlib
import json
import os
import sys
from typing import Any, Dict, List

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.stage_c_contract_validator import (
    StageCContractValidator,
    compute_contract_complexity_metrics,
    EXPECTED_PROVENANCE_STATEMENT,
)

BASE_CONTRACTS_DIR = os.path.join(ROOT_DIR, "data_stage_c", "base_contracts")
MANIFEST_PATH = os.path.join(ROOT_DIR, "data_stage_c", "base_contract_manifest.json")
AUDIT_MD_PATH = os.path.join(ROOT_DIR, "results_stage_c", "BASE_CONTRACT_CORPUS_AUDIT.md")

MASTER_SEED = 42
GENERATOR_VERSION = "1.0.0"


def _create_contract_spec(
    cid_int: int,
    tool_name: str,
    title: str,
    description: str,
    stratum: str,
    domain: str,
    properties: Dict[str, Any],
    required: List[str],
    latent_intent_schema: Dict[str, str],
    gold_examples: List[Dict[str, Any]],
    counterexamples: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Helper to assemble a single validated synthetic contract."""
    contract_id = f"BASE_SYNTH_{cid_int:03d}"
    seed = MASTER_SEED * 1000 + cid_int

    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": tool_name,
        "description": description,
        "type": "object",
        "additionalProperties": False,
        "properties": properties,
        "required": required,
    }

    metrics = compute_contract_complexity_metrics(schema)

    return {
        "contract_id": contract_id,
        "tool_name": tool_name,
        "title": title,
        "description": description,
        "stratum": stratum,
        "domain": domain,
        "schema": schema,
        "latent_intent_schema": latent_intent_schema,
        "gold_examples": gold_examples,
        "counterexamples": counterexamples,
        "provenance_statement": EXPECTED_PROVENANCE_STATEMENT,
        "complexity_metrics": metrics,
        "seed": seed,
        "generator_version": GENERATOR_VERSION,
    }


def build_synthetic_base_corpus() -> List[Dict[str, Any]]:
    """Synthesize the complete 40-contract base corpus."""
    contracts: List[Dict[str, Any]] = []

    # =========================================================================
    # STRATUM 1: SIMPLE FLAT SCHEMAS (Contracts 1 to 12)
    # =========================================================================

    # 1. synth_create_key_value (data_management)
    contracts.append(_create_contract_spec(
        1, "synth_create_key_value", "Create Key-Value Pair",
        "Store a key-value pair in a distributed cache partition.",
        "SIMPLE_FLAT", "data_management",
        {
            "key": {"type": "string", "minLength": 1, "maxLength": 128, "description": "Unique key identifier"},
            "value": {"type": "string", "description": "Serialized value payload"},
            "ttl_seconds": {"type": "integer", "minimum": 1, "maximum": 86400, "description": "Time to live in seconds"},
            "overwrite": {"type": "boolean", "description": "Whether to overwrite existing entry"},
        },
        ["key", "value"],
        {"key": "string", "value": "string", "ttl_seconds": "integer", "overwrite": "boolean"},
        [
            {"key": "user_1024", "value": "session_active", "ttl_seconds": 3600, "overwrite": True},
            {"key": "counter_hit", "value": "42"},
        ],
        [
            {"value": "no_key_provided"},
            {"key": "bad_ttl", "value": "ok", "ttl_seconds": 0},
        ],
    ))

    # 2. synth_delete_cache_entry (data_management)
    contracts.append(_create_contract_spec(
        2, "synth_delete_cache_entry", "Delete Cache Entry",
        "Purge entries matching a specific key pattern from the cache.",
        "SIMPLE_FLAT", "data_management",
        {
            "key_pattern": {"type": "string", "minLength": 1, "description": "Glob or prefix pattern"},
            "cascade_eviction": {"type": "boolean", "description": "Evict child keys recursively"},
            "max_evictions": {"type": "integer", "minimum": 1, "maximum": 1000, "description": "Eviction batch cap"},
        },
        ["key_pattern"],
        {"key_pattern": "string", "cascade_eviction": "boolean", "max_evictions": "integer"},
        [
            {"key_pattern": "session:*", "cascade_eviction": True, "max_evictions": 500},
            {"key_pattern": "temp:auth:99"},
        ],
        [
            {"cascade_eviction": True},
            {"key_pattern": "", "max_evictions": 50},
        ],
    ))

    # 3. synth_truncate_table_slice (data_management)
    contracts.append(_create_contract_spec(
        3, "synth_truncate_table_slice", "Truncate Table Slice",
        "Remove all records from a specific table slice or partition.",
        "SIMPLE_FLAT", "data_management",
        {
            "table_name": {"type": "string", "minLength": 1, "description": "Target relational table name"},
            "slice_index": {"type": "integer", "minimum": 0, "description": "Zero-indexed partition slice"},
            "force_truncate": {"type": "boolean", "description": "Bypass active read-lock confirmation"},
        },
        ["table_name", "slice_index"],
        {"table_name": "string", "slice_index": "integer", "force_truncate": "boolean"},
        [
            {"table_name": "audit_logs_2026", "slice_index": 3, "force_truncate": True},
            {"table_name": "temp_staging", "slice_index": 0},
        ],
        [
            {"table_name": "missing_slice"},
            {"table_name": "bad_slice", "slice_index": -1},
        ],
    ))

    # 4. synth_dispatch_sms_message (communications)
    contracts.append(_create_contract_spec(
        4, "synth_dispatch_sms_message", "Dispatch SMS Message",
        "Send an SMS text message to a designated phone destination.",
        "SIMPLE_FLAT", "communications",
        {
            "recipient_number": {"type": "string", "minLength": 8, "maxLength": 16, "description": "E.164 phone number"},
            "message_body": {"type": "string", "minLength": 1, "maxLength": 160, "description": "SMS text body"},
            "priority": {"type": "integer", "minimum": 1, "maximum": 5, "description": "Queue priority from 1 to 5"},
        },
        ["recipient_number", "message_body"],
        {"recipient_number": "string", "message_body": "string", "priority": "integer"},
        [
            {"recipient_number": "+14693636353", "message_body": "Your verification code is 492011", "priority": 1},
            {"recipient_number": "+12145550199", "message_body": "Appointment reminder for tomorrow."},
        ],
        [
            {"recipient_number": "+14693636353"},
            {"recipient_number": "+1", "message_body": "Short number"},
        ],
    ))

    # 5. synth_update_call_status (communications)
    contracts.append(_create_contract_spec(
        5, "synth_update_call_status", "Update Call Session Status",
        "Modify the signaling status of an active voice call session.",
        "SIMPLE_FLAT", "communications",
        {
            "call_id": {"type": "string", "minLength": 4, "description": "Unique call session identifier"},
            "status_code": {"type": "integer", "minimum": 100, "maximum": 600, "description": "SIP/VoIP status code"},
            "record_audio": {"type": "boolean", "description": "Toggle media recording on bridge"},
        },
        ["call_id", "status_code"],
        {"call_id": "string", "status_code": "integer", "record_audio": "boolean"},
        [
            {"call_id": "call_9941a", "status_code": 200, "record_audio": True},
            {"call_id": "call_1102b", "status_code": 486},
        ],
        [
            {"call_id": "call_no_status"},
            {"call_id": "call_bad_status", "status_code": 50},
        ],
    ))

    # 6. synth_terminate_voice_bridge (communications)
    contracts.append(_create_contract_spec(
        6, "synth_terminate_voice_bridge", "Terminate Voice Bridge",
        "Tear down an established conference audio bridge.",
        "SIMPLE_FLAT", "communications",
        {
            "bridge_id": {"type": "string", "minLength": 4, "description": "Conference bridge identifier"},
            "termination_reason": {"type": "string", "description": "Audit rationale for bridge shutdown"},
            "archive_recording": {"type": "boolean", "description": "Persist audio capture to cold storage"},
        },
        ["bridge_id"],
        {"bridge_id": "string", "termination_reason": "string", "archive_recording": "boolean"},
        [
            {"bridge_id": "bridge_7710", "termination_reason": "Host ended call", "archive_recording": True},
            {"bridge_id": "bridge_8820"},
        ],
        [
            {"termination_reason": "Missing bridge ID"},
            {"bridge_id": "br", "termination_reason": "ID too short"},
        ],
    ))

    # 7. synth_increment_counter_metric (analytics_metrics)
    contracts.append(_create_contract_spec(
        7, "synth_increment_counter_metric", "Increment Counter Metric",
        "Add a delta value to a Prometheus-style counter metric.",
        "SIMPLE_FLAT", "analytics_metrics",
        {
            "metric_name": {"type": "string", "minLength": 1, "description": "Metric identifier"},
            "increment_by": {"type": "integer", "minimum": 1, "description": "Positive integer increment"},
            "flush_immediately": {"type": "boolean", "description": "Flush local buffer to aggregator"},
        },
        ["metric_name"],
        {"metric_name": "string", "increment_by": "integer", "flush_immediately": "boolean"},
        [
            {"metric_name": "http_requests_total", "increment_by": 5, "flush_immediately": True},
            {"metric_name": "auth_failures_total"},
        ],
        [
            {"increment_by": 5},
            {"metric_name": "bad_inc", "increment_by": 0},
        ],
    ))

    # 8. synth_record_heartbeat_timestamp (analytics_metrics)
    contracts.append(_create_contract_spec(
        8, "synth_record_heartbeat_timestamp", "Record Heartbeat Timestamp",
        "Report service agent health heartbeat with unix epoch timestamp.",
        "SIMPLE_FLAT", "analytics_metrics",
        {
            "service_name": {"type": "string", "minLength": 1, "description": "Service instance name"},
            "epoch_seconds": {"type": "integer", "minimum": 1600000000, "description": "Unix timestamp in seconds"},
            "is_healthy": {"type": "boolean", "description": "Self-reported health state"},
        },
        ["service_name", "epoch_seconds", "is_healthy"],
        {"service_name": "string", "epoch_seconds": "integer", "is_healthy": "boolean"},
        [
            {"service_name": "auth_service_node_1", "epoch_seconds": 1761500000, "is_healthy": True},
            {"service_name": "gateway_proxy_0", "epoch_seconds": 1761500010, "is_healthy": False},
        ],
        [
            {"service_name": "missing_epoch", "is_healthy": True},
            {"service_name": "old_epoch", "epoch_seconds": 100, "is_healthy": True},
        ],
    ))

    # 9. synth_reset_quota_usage (analytics_metrics)
    contracts.append(_create_contract_spec(
        9, "synth_reset_quota_usage", "Reset Quota Usage",
        "Reset API invocation consumption counter for a specific tenant.",
        "SIMPLE_FLAT", "analytics_metrics",
        {
            "tenant_id": {"type": "string", "minLength": 3, "description": "Account tenant identifier"},
            "quota_bucket": {"type": "string", "minLength": 1, "description": "Rate limit bucket key"},
            "grace_period_minutes": {"type": "integer", "minimum": 0, "maximum": 1440, "description": "Exemption duration"},
        },
        ["tenant_id", "quota_bucket"],
        {"tenant_id": "string", "quota_bucket": "string", "grace_period_minutes": "integer"},
        [
            {"tenant_id": "ten_9941", "quota_bucket": "daily_api_calls", "grace_period_minutes": 60},
            {"tenant_id": "ten_1102", "quota_bucket": "sms_allowance"},
        ],
        [
            {"quota_bucket": "daily_calls"},
            {"tenant_id": "t1", "quota_bucket": "short_tenant"},
        ],
    ))

    # 10. synth_revoke_access_token (access_governance)
    contracts.append(_create_contract_spec(
        10, "synth_revoke_access_token", "Revoke Access Token",
        "Invalidate an issued OAuth2 or JWT access token immediately.",
        "SIMPLE_FLAT", "access_governance",
        {
            "token_id": {"type": "string", "minLength": 8, "description": "Token unique identifier (jti)"},
            "reason": {"type": "string", "description": "Security revocation rationale"},
            "notify_subject": {"type": "boolean", "description": "Send notification email to token owner"},
        },
        ["token_id"],
        {"token_id": "string", "reason": "string", "notify_subject": "boolean"},
        [
            {"token_id": "tok_9918274619", "reason": "Suspicious login location", "notify_subject": True},
            {"token_id": "tok_12345678"},
        ],
        [
            {"reason": "No token provided"},
            {"token_id": "short"},
        ],
    ))

    # 11. synth_extend_session_lease (access_governance)
    contracts.append(_create_contract_spec(
        11, "synth_extend_session_lease", "Extend Session Lease",
        "Prolong an active authenticated session lease by a given duration.",
        "SIMPLE_FLAT", "access_governance",
        {
            "session_id": {"type": "string", "minLength": 8, "description": "Active session cookie ID"},
            "extension_minutes": {"type": "integer", "minimum": 5, "maximum": 480, "description": "Extension duration"},
            "touch_activity": {"type": "boolean", "description": "Update last active timestamp"},
        },
        ["session_id", "extension_minutes"],
        {"session_id": "string", "extension_minutes": "integer", "touch_activity": "boolean"},
        [
            {"session_id": "sess_8839201948", "extension_minutes": 60, "touch_activity": True},
            {"session_id": "sess_1192837465", "extension_minutes": 15},
        ],
        [
            {"session_id": "sess_missing_minutes"},
            {"session_id": "sess_too_short_ext", "extension_minutes": 2},
        ],
    ))

    # 12. synth_lock_user_account (access_governance)
    contracts.append(_create_contract_spec(
        12, "synth_lock_user_account", "Lock User Account",
        "Impose an administrative lock on a compromised user account.",
        "SIMPLE_FLAT", "access_governance",
        {
            "user_id": {"type": "string", "minLength": 4, "description": "Target user identifier"},
            "lock_hours": {"type": "integer", "minimum": 1, "maximum": 720, "description": "Lock duration in hours"},
            "require_password_reset": {"type": "boolean", "description": "Enforce password reset on unlock"},
        },
        ["user_id", "lock_hours"],
        {"user_id": "string", "lock_hours": "integer", "require_password_reset": "boolean"},
        [
            {"user_id": "usr_9918", "lock_hours": 24, "require_password_reset": True},
            {"user_id": "usr_5501", "lock_hours": 72},
        ],
        [
            {"user_id": "usr_no_hours"},
            {"user_id": "usr_bad_hours", "lock_hours": 0},
        ],
    ))

    # =========================================================================
    # STRATUM 2: MEDIUM SCHEMAS WITH ARRAYS AND ENUMS (Contracts 13 to 28)
    # =========================================================================

    # 13. synth_batch_index_records (data_management)
    contracts.append(_create_contract_spec(
        13, "synth_batch_index_records", "Batch Index Records",
        "Submit a collection of document IDs for search indexing.",
        "MEDIUM_ARRAYS_ENUMS", "data_management",
        {
            "collection_name": {"type": "string", "minLength": 1, "description": "Search index name"},
            "record_ids": {"type": "array", "items": {"type": "string"}, "minItems": 1, "maxItems": 100, "description": "List of record identifiers"},
            "index_mode": {"type": "string", "enum": ["synchronous", "asynchronous", "lazy"], "description": "Indexing commitment mode"},
            "refresh_view": {"type": "boolean", "description": "Force immediate index view refresh"},
        },
        ["collection_name", "record_ids", "index_mode"],
        {"collection_name": "string", "record_ids": "array[string]", "index_mode": "string", "refresh_view": "boolean"},
        [
            {"collection_name": "knowledge_docs", "record_ids": ["doc_1", "doc_2"], "index_mode": "asynchronous", "refresh_view": True},
            {"collection_name": "products_catalog", "record_ids": ["sku_100"], "index_mode": "synchronous"},
        ],
        [
            {"collection_name": "empty_records", "record_ids": [], "index_mode": "lazy"},
            {"collection_name": "bad_mode", "record_ids": ["d1"], "index_mode": "invalid_mode"},
        ],
    ))

    # 14. synth_archive_data_partition (data_management)
    contracts.append(_create_contract_spec(
        14, "synth_archive_data_partition", "Archive Data Partition",
        "Move a data partition to cold archival storage with compression.",
        "MEDIUM_ARRAYS_ENUMS", "data_management",
        {
            "partition_key": {"type": "string", "minLength": 2, "description": "Partition identifier"},
            "compression_format": {"type": "string", "enum": ["gzip", "zstd", "snappy"], "description": "Compression algorithm"},
            "metadata_tags": {"type": "array", "items": {"type": "string"}, "description": "Classification tags"},
            "retention_years": {"type": "integer", "minimum": 1, "maximum": 10, "description": "Archival compliance retention period"},
        },
        ["partition_key", "compression_format"],
        {"partition_key": "string", "compression_format": "string", "metadata_tags": "array[string]", "retention_years": "integer"},
        [
            {"partition_key": "part_2025_q4", "compression_format": "zstd", "metadata_tags": ["financial", "audited"], "retention_years": 7},
            {"partition_key": "part_2026_q1", "compression_format": "gzip"},
        ],
        [
            {"partition_key": "p1", "compression_format": "bzip2"},
            {"compression_format": "zstd"},
        ],
    ))

    # 15. synth_broadcast_alert_notification (communications)
    contracts.append(_create_contract_spec(
        15, "synth_broadcast_alert_notification", "Broadcast Alert Notification",
        "Broadcast a critical operational alert across multiple notification channels.",
        "MEDIUM_ARRAYS_ENUMS", "communications",
        {
            "alert_title": {"type": "string", "minLength": 1, "description": "Short alert title"},
            "severity_level": {"type": "string", "enum": ["INFO", "WARNING", "CRITICAL", "FATAL"], "description": "Alert severity tier"},
            "target_channels": {"type": "array", "items": {"type": "string"}, "minItems": 1, "description": "Broadcast destination channels"},
            "auto_resolve_minutes": {"type": "integer", "minimum": 5, "maximum": 1440, "description": "Automatic timeout before auto-resolve"},
        },
        ["alert_title", "severity_level", "target_channels"],
        {"alert_title": "string", "severity_level": "string", "target_channels": "array[string]", "auto_resolve_minutes": "integer"},
        [
            {"alert_title": "Database High Memory", "severity_level": "CRITICAL", "target_channels": ["slack-ops", "pagerduty-sre"], "auto_resolve_minutes": 60},
            {"alert_title": "Certificate Expiring", "severity_level": "WARNING", "target_channels": ["email-admins"]},
        ],
        [
            {"alert_title": "No channels", "severity_level": "INFO", "target_channels": []},
            {"alert_title": "Bad level", "severity_level": "UNKNOWN", "target_channels": ["c1"]},
        ],
    ))

    # 16. synth_enqueue_email_digest (communications)
    contracts.append(_create_contract_spec(
        16, "synth_enqueue_email_digest", "Enqueue Email Digest",
        "Schedule an aggregated email digest for a recipient list.",
        "MEDIUM_ARRAYS_ENUMS", "communications",
        {
            "template_slug": {"type": "string", "minLength": 1, "description": "Email layout template ID"},
            "recipients": {"type": "array", "items": {"type": "string"}, "minItems": 1, "description": "Recipient email addresses"},
            "digest_frequency": {"type": "string", "enum": ["daily", "weekly", "monthly"], "description": "Aggregation cadence"},
            "track_opens": {"type": "boolean", "description": "Embed tracking pixel"},
        },
        ["template_slug", "recipients", "digest_frequency"],
        {"template_slug": "string", "recipients": "array[string]", "digest_frequency": "string", "track_opens": "boolean"},
        [
            {"template_slug": "weekly_developer_digest", "recipients": ["alice@example.com", "bob@example.com"], "digest_frequency": "weekly", "track_opens": False},
            {"template_slug": "monthly_billing", "recipients": ["cfo@example.com"], "digest_frequency": "monthly"},
        ],
        [
            {"template_slug": "digest_missing_recipients", "digest_frequency": "daily"},
            {"template_slug": "digest_bad_freq", "recipients": ["a@b.com"], "digest_frequency": "hourly"},
        ],
    ))

    # 17. synth_register_push_token (communications)
    contracts.append(_create_contract_spec(
        17, "synth_register_push_token", "Register Push Notification Token",
        "Associate a mobile device APNS or FCM push token with an account.",
        "MEDIUM_ARRAYS_ENUMS", "communications",
        {
            "device_id": {"type": "string", "minLength": 8, "description": "Hardware device UUID"},
            "platform": {"type": "string", "enum": ["ios", "android", "web"], "description": "Operating system platform"},
            "subscribed_topics": {"type": "array", "items": {"type": "string"}, "description": "Notification interest topics"},
            "token_ttl_days": {"type": "integer", "minimum": 1, "maximum": 365, "description": "Token validity expiration"},
        },
        ["device_id", "platform"],
        {"device_id": "string", "platform": "string", "subscribed_topics": "array[string]", "token_ttl_days": "integer"},
        [
            {"device_id": "dev_9918274619", "platform": "ios", "subscribed_topics": ["news", "alerts"], "token_ttl_days": 90},
            {"device_id": "dev_1122334455", "platform": "android"},
        ],
        [
            {"platform": "web"},
            {"device_id": "dev_bad_plat", "platform": "windows_phone"},
        ],
    ))

    # 18. synth_query_metric_aggregate (analytics_metrics)
    contracts.append(_create_contract_spec(
        18, "synth_query_metric_aggregate", "Query Metric Aggregate",
        "Execute a timeseries aggregation query over specified dimensions.",
        "MEDIUM_ARRAYS_ENUMS", "analytics_metrics",
        {
            "metric_series": {"type": "string", "minLength": 1, "description": "Metric timeseries identifier"},
            "aggregation": {"type": "string", "enum": ["avg", "sum", "min", "max", "p95", "p99"], "description": "Statistical aggregator"},
            "filter_dimensions": {"type": "array", "items": {"type": "string"}, "description": "Key=value tag filters"},
            "window_seconds": {"type": "integer", "minimum": 60, "maximum": 86400, "description": "Aggregation window width"},
        },
        ["metric_series", "aggregation", "window_seconds"],
        {"metric_series": "string", "aggregation": "string", "filter_dimensions": "array[string]", "window_seconds": "integer"},
        [
            {"metric_series": "api_latency_ms", "aggregation": "p99", "filter_dimensions": ["region=us-east", "env=prod"], "window_seconds": 300},
            {"metric_series": "cpu_utilization", "aggregation": "avg", "window_seconds": 60},
        ],
        [
            {"metric_series": "latency", "aggregation": "median", "window_seconds": 60},
            {"metric_series": "cpu", "aggregation": "avg", "window_seconds": 10},
        ],
    ))

    # 19. synth_evaluate_anomaly_detector (analytics_metrics)
    contracts.append(_create_contract_spec(
        19, "synth_evaluate_anomaly_detector", "Evaluate Anomaly Detector",
        "Run statistical outlier detection on a series with specified sensitivity.",
        "MEDIUM_ARRAYS_ENUMS", "analytics_metrics",
        {
            "detector_id": {"type": "string", "minLength": 3, "description": "Anomaly detection model name"},
            "sensitivity": {"type": "string", "enum": ["low", "medium", "high", "paranoid"], "description": "Standard deviation threshold tier"},
            "training_windows": {"type": "array", "items": {"type": "integer"}, "minItems": 1, "description": "Historical comparative day offsets"},
            "emit_alert": {"type": "boolean", "description": "Trigger alert pipeline if anomaly detected"},
        },
        ["detector_id", "sensitivity", "training_windows"],
        {"detector_id": "string", "sensitivity": "string", "training_windows": "array[integer]", "emit_alert": "boolean"},
        [
            {"detector_id": "traffic_spike_detector", "sensitivity": "high", "training_windows": [1, 7, 14], "emit_alert": True},
            {"detector_id": "db_connections", "sensitivity": "medium", "training_windows": [1]},
        ],
        [
            {"detector_id": "empty_windows", "sensitivity": "low", "training_windows": []},
            {"detector_id": "bad_sensitivity", "sensitivity": "ultra", "training_windows": [1]},
        ],
    ))

    # 20. synth_publish_metric_histogram (analytics_metrics)
    contracts.append(_create_contract_spec(
        20, "synth_publish_metric_histogram", "Publish Metric Histogram",
        "Publish observations into predefined histogram bucket thresholds.",
        "MEDIUM_ARRAYS_ENUMS", "analytics_metrics",
        {
            "histogram_name": {"type": "string", "minLength": 1, "description": "Histogram metric name"},
            "unit": {"type": "string", "enum": ["milliseconds", "seconds", "bytes", "count"], "description": "Measurement unit"},
            "bucket_boundaries": {"type": "array", "items": {"type": "number"}, "minItems": 2, "description": "Ascending bucket threshold values"},
            "sample_count": {"type": "integer", "minimum": 1, "description": "Number of observations"},
        },
        ["histogram_name", "unit", "bucket_boundaries"],
        {"histogram_name": "string", "unit": "string", "bucket_boundaries": "array[number]", "sample_count": "integer"},
        [
            {"histogram_name": "rpc_response_size", "unit": "bytes", "bucket_boundaries": [100.0, 500.0, 1000.0, 5000.0], "sample_count": 120},
            {"histogram_name": "db_query_time", "unit": "milliseconds", "bucket_boundaries": [1.0, 5.0, 10.0]},
        ],
        [
            {"histogram_name": "short_buckets", "unit": "seconds", "bucket_boundaries": [1.0]},
            {"histogram_name": "bad_unit", "unit": "liters", "bucket_boundaries": [1.0, 2.0]},
        ],
    ))

    # 21. synth_assign_role_permissions (access_governance)
    contracts.append(_create_contract_spec(
        21, "synth_assign_role_permissions", "Assign Role Permissions",
        "Grant a predefined security role and scope set to a user principal.",
        "MEDIUM_ARRAYS_ENUMS", "access_governance",
        {
            "principal_id": {"type": "string", "minLength": 3, "description": "User or service principal identifier"},
            "role_tier": {"type": "string", "enum": ["viewer", "operator", "admin", "owner"], "description": "Predefined RBAC role tier"},
            "permission_scopes": {"type": "array", "items": {"type": "string"}, "minItems": 1, "description": "Granted scope strings"},
            "enforce_mfa": {"type": "boolean", "description": "Require multi-factor authentication for role usage"},
        },
        ["principal_id", "role_tier", "permission_scopes"],
        {"principal_id": "string", "role_tier": "string", "permission_scopes": "array[string]", "enforce_mfa": "boolean"},
        [
            {"principal_id": "usr_9918", "role_tier": "operator", "permission_scopes": ["read:logs", "restart:service"], "enforce_mfa": True},
            {"principal_id": "usr_5501", "role_tier": "viewer", "permission_scopes": ["read:dashboard"]},
        ],
        [
            {"principal_id": "usr_no_scopes", "role_tier": "admin", "permission_scopes": []},
            {"principal_id": "usr_bad_tier", "role_tier": "superadmin", "permission_scopes": ["read"]},
        ],
    ))

    # 22. synth_provision_api_credential (access_governance)
    contracts.append(_create_contract_spec(
        22, "synth_provision_api_credential", "Provision API Credential",
        "Generate a client API key with environment assignment and rate limits.",
        "MEDIUM_ARRAYS_ENUMS", "access_governance",
        {
            "client_name": {"type": "string", "minLength": 2, "description": "Descriptive client application name"},
            "target_environment": {"type": "string", "enum": ["development", "staging", "production"], "description": "Target tier"},
            "ip_allowlist": {"type": "array", "items": {"type": "string"}, "description": "Allowed CIDR IP ranges"},
            "rate_limit_rpm": {"type": "integer", "minimum": 60, "maximum": 60000, "description": "Maximum allowed requests per minute"},
        },
        ["client_name", "target_environment"],
        {"client_name": "string", "target_environment": "string", "ip_allowlist": "array[string]", "rate_limit_rpm": "integer"},
        [
            {"client_name": "payment_gateway_client", "target_environment": "production", "ip_allowlist": ["192.168.1.0/24"], "rate_limit_rpm": 1200},
            {"client_name": "test_harness", "target_environment": "development"},
        ],
        [
            {"client_name": "bad_env", "target_environment": "qa_sandbox"},
            {"target_environment": "staging"},
        ],
    ))

    # 23. synth_rotate_secret_key (access_governance)
    contracts.append(_create_contract_spec(
        23, "synth_rotate_secret_key", "Rotate Secret Key",
        "Re-encrypt and replace cryptographic secret key with specified algorithm.",
        "MEDIUM_ARRAYS_ENUMS", "access_governance",
        {
            "secret_slug": {"type": "string", "minLength": 2, "description": "Secret vault key identifier"},
            "algorithm": {"type": "string", "enum": ["AES-256-GCM", "ChaCha20-Poly1305", "RSA-4096"], "description": "Cryptographic cipher"},
            "affected_services": {"type": "array", "items": {"type": "string"}, "description": "Downstream services requiring key reload"},
            "grace_period_hours": {"type": "integer", "minimum": 0, "maximum": 168, "description": "Overlap period where old key remains valid"},
        },
        ["secret_slug", "algorithm"],
        {"secret_slug": "string", "algorithm": "string", "affected_services": "array[string]", "grace_period_hours": "integer"},
        [
            {"secret_slug": "jwt_signing_key", "algorithm": "AES-256-GCM", "affected_services": ["auth-srv", "api-gateway"], "grace_period_hours": 24},
            {"secret_slug": "webhook_hmac_secret", "algorithm": "ChaCha20-Poly1305"},
        ],
        [
            {"secret_slug": "bad_algo", "algorithm": "DES-56"},
            {"algorithm": "RSA-4096"},
        ],
    ))

    # 24. synth_trigger_pipeline_stage (workflow_orchestration)
    contracts.append(_create_contract_spec(
        24, "synth_trigger_pipeline_stage", "Trigger Pipeline Stage",
        "Initiate a specific build or validation stage within a CI/CD pipeline.",
        "MEDIUM_ARRAYS_ENUMS", "workflow_orchestration",
        {
            "pipeline_id": {"type": "string", "minLength": 3, "description": "Workflow pipeline definition ID"},
            "stage_name": {"type": "string", "enum": ["lint", "unit_test", "integration_test", "security_scan", "package"], "description": "Target execution stage"},
            "artifact_paths": {"type": "array", "items": {"type": "string"}, "description": "Input artifact files"},
            "timeout_seconds": {"type": "integer", "minimum": 10, "maximum": 3600, "description": "Maximum stage runtime"},
        },
        ["pipeline_id", "stage_name"],
        {"pipeline_id": "string", "stage_name": "string", "artifact_paths": "array[string]", "timeout_seconds": "integer"},
        [
            {"pipeline_id": "pipe_release_v2", "stage_name": "integration_test", "artifact_paths": ["build/bin.tar.gz"], "timeout_seconds": 600},
            {"pipeline_id": "pipe_fast_pr", "stage_name": "lint"},
        ],
        [
            {"pipeline_id": "pipe_bad_stage", "stage_name": "deploy_prod"},
            {"stage_name": "unit_test"},
        ],
    ))

    # 25. synth_cancel_workflow_task (workflow_orchestration)
    contracts.append(_create_contract_spec(
        25, "synth_cancel_workflow_task", "Cancel Workflow Task",
        "Abort a currently queued or executing background task in a workflow.",
        "MEDIUM_ARRAYS_ENUMS", "workflow_orchestration",
        {
            "workflow_id": {"type": "string", "minLength": 3, "description": "Parent workflow execution ID"},
            "task_id": {"type": "string", "minLength": 3, "description": "Subtask identifier"},
            "cancellation_policy": {"type": "string", "enum": ["immediate_kill", "graceful_drain", "compensate_and_stop"], "description": "Teardown mode"},
            "cleanup_tags": {"type": "array", "items": {"type": "string"}, "description": "Resource tags to deallocate"},
        },
        ["workflow_id", "task_id", "cancellation_policy"],
        {"workflow_id": "string", "task_id": "string", "cancellation_policy": "string", "cleanup_tags": "array[string]"},
        [
            {"workflow_id": "wf_10928", "task_id": "task_sub_4", "cancellation_policy": "immediate_kill", "cleanup_tags": ["temp_db", "staging_s3"]},
            {"workflow_id": "wf_99211", "task_id": "task_sub_1", "cancellation_policy": "graceful_drain"},
        ],
        [
            {"workflow_id": "wf_missing_task", "cancellation_policy": "immediate_kill"},
            {"workflow_id": "wf_1", "task_id": "t1", "cancellation_policy": "ignore_and_continue"},
        ],
    ))

    # 26. synth_resume_paused_execution (workflow_orchestration)
    contracts.append(_create_contract_spec(
        26, "synth_resume_paused_execution", "Resume Paused Execution",
        "Resume a suspended workflow from an approval checkpoint or breakpoint.",
        "MEDIUM_ARRAYS_ENUMS", "workflow_orchestration",
        {
            "execution_id": {"type": "string", "minLength": 4, "description": "Suspended workflow execution ID"},
            "resume_point": {"type": "string", "enum": ["checkpoint_start", "next_step", "replay_failed_step"], "description": "Resume target"},
            "override_variables": {"type": "array", "items": {"type": "string"}, "description": "Variable assignments as key=val"},
            "skip_validation": {"type": "boolean", "description": "Bypass intermediate state assertions"},
        },
        ["execution_id", "resume_point"],
        {"execution_id": "string", "resume_point": "string", "override_variables": "array[string]", "skip_validation": "boolean"},
        [
            {"execution_id": "exec_99182", "resume_point": "next_step", "override_variables": ["RETRIES=3"], "skip_validation": True},
            {"execution_id": "exec_44102", "resume_point": "checkpoint_start"},
        ],
        [
            {"execution_id": "exec_bad_pt", "resume_point": "restart_entire_cluster"},
            {"resume_point": "next_step"},
        ],
    ))

    # 27. synth_schedule_cron_job (workflow_orchestration)
    contracts.append(_create_contract_spec(
        27, "synth_schedule_cron_job", "Schedule Cron Job",
        "Register a recurring automated task schedule with target queue.",
        "MEDIUM_ARRAYS_ENUMS", "workflow_orchestration",
        {
            "job_name": {"type": "string", "minLength": 2, "description": "Unique cron job name"},
            "cron_expression": {"type": "string", "minLength": 9, "description": "Standard 5-part cron syntax"},
            "target_queue": {"type": "string", "enum": ["default", "high_priority", "batch_overnight"], "description": "Target dispatch queue"},
            "alert_emails": {"type": "array", "items": {"type": "string"}, "description": "Failure notification recipients"},
        },
        ["job_name", "cron_expression", "target_queue"],
        {"job_name": "string", "cron_expression": "string", "target_queue": "string", "alert_emails": "array[string]"},
        [
            {"job_name": "nightly_backup", "cron_expression": "0 2 * * *", "target_queue": "batch_overnight", "alert_emails": ["ops@example.com"]},
            {"job_name": "health_check", "cron_expression": "*/5 * * * *", "target_queue": "high_priority"},
        ],
        [
            {"job_name": "bad_cron", "cron_expression": "*", "target_queue": "default"},
            {"job_name": "bad_q", "cron_expression": "0 0 * * *", "target_queue": "urgent_queue"},
        ],
    ))

    # 28. synth_dispatch_batch_worker (workflow_orchestration)
    contracts.append(_create_contract_spec(
        28, "synth_dispatch_batch_worker", "Dispatch Batch Worker",
        "Spin up dedicated compute workers to process a batch of task IDs.",
        "MEDIUM_ARRAYS_ENUMS", "workflow_orchestration",
        {
            "worker_pool": {"type": "string", "enum": ["cpu_optimized", "memory_optimized", "standard"], "description": "Compute tier"},
            "job_ids": {"type": "array", "items": {"type": "string"}, "minItems": 1, "description": "Assigned job identifiers"},
            "worker_concurrency": {"type": "integer", "minimum": 1, "maximum": 32, "description": "Parallel thread count"},
            "auto_terminate": {"type": "boolean", "description": "Shut down worker upon queue exhaustion"},
        },
        ["worker_pool", "job_ids"],
        {"worker_pool": "string", "job_ids": "array[string]", "worker_concurrency": "integer", "auto_terminate": "boolean"},
        [
            {"worker_pool": "cpu_optimized", "job_ids": ["job_101", "job_102"], "worker_concurrency": 16, "auto_terminate": True},
            {"worker_pool": "standard", "job_ids": ["job_500"]},
        ],
        [
            {"worker_pool": "gpu_cluster", "job_ids": ["job_1"]},
            {"worker_pool": "standard", "job_ids": []},
        ],
    ))

    # =========================================================================
    # STRATUM 3: NESTED OBJECTS AND MULTI-SURFACES (Contracts 29 to 40)
    # =========================================================================

    # 29. synth_configure_database_replica (data_management)
    contracts.append(_create_contract_spec(
        29, "synth_configure_database_replica", "Configure Database Replica",
        "Provision a read replica node with host connection and replication settings.",
        "NESTED_OBJECTS_SURFACES", "data_management",
        {
            "cluster_id": {"type": "string", "minLength": 3, "description": "Primary database cluster ID"},
            "replica_config": {
                "type": "object",
                "description": "Replica node configuration",
                "additionalProperties": False,
                "properties": {
                    "node_name": {"type": "string", "minLength": 1, "description": "Replica hostname/label"},
                    "port": {"type": "integer", "minimum": 1024, "maximum": 65535, "description": "Port number"},
                    "read_only": {"type": "boolean", "description": "Enforce read-only transactions"},
                },
                "required": ["node_name", "port"],
            },
            "enable_ssl": {"type": "boolean", "description": "Require TLS encryption on replication stream"},
        },
        ["cluster_id", "replica_config"],
        {"cluster_id": "string", "replica_config": "object", "enable_ssl": "boolean"},
        [
            {"cluster_id": "db_prod_main", "replica_config": {"node_name": "replica_east_1", "port": 5432, "read_only": True}, "enable_ssl": True},
            {"cluster_id": "db_analytics", "replica_config": {"node_name": "replica_anal_0", "port": 3306}},
        ],
        [
            {"cluster_id": "db_no_replica"},
            {"cluster_id": "db_1", "replica_config": {"node_name": "rep_1", "port": 80}},
        ],
    ))

    # 30. synth_execute_partition_migration (data_management)
    contracts.append(_create_contract_spec(
        30, "synth_execute_partition_migration", "Execute Partition Migration",
        "Migrate partition slices from source cluster to target destination cluster.",
        "NESTED_OBJECTS_SURFACES", "data_management",
        {
            "migration_id": {"type": "string", "minLength": 3, "description": "Migration operation tracking ID"},
            "source": {
                "type": "object",
                "description": "Source storage specification",
                "additionalProperties": False,
                "properties": {
                    "cluster_name": {"type": "string", "minLength": 1},
                    "slice_id": {"type": "integer", "minimum": 0},
                },
                "required": ["cluster_name", "slice_id"],
            },
            "target": {
                "type": "object",
                "description": "Target storage destination",
                "additionalProperties": False,
                "properties": {
                    "cluster_name": {"type": "string", "minLength": 1},
                    "datacenter": {"type": "string", "minLength": 2},
                },
                "required": ["cluster_name", "datacenter"],
            },
        },
        ["migration_id", "source", "target"],
        {"migration_id": "string", "source": "object", "target": "object"},
        [
            {
                "migration_id": "mig_9941",
                "source": {"cluster_name": "cluster_us_east", "slice_id": 4},
                "target": {"cluster_name": "cluster_eu_central", "datacenter": "fra-1"},
            },
            {
                "migration_id": "mig_8810",
                "source": {"cluster_name": "staging_a", "slice_id": 0},
                "target": {"cluster_name": "staging_b", "datacenter": "iad-2"},
            },
        ],
        [
            {"migration_id": "mig_missing_target", "source": {"cluster_name": "c1", "slice_id": 0}},
            {"migration_id": "mig_bad_target", "source": {"cluster_name": "c1", "slice_id": 0}, "target": {"cluster_name": "c2"}},
        ],
    ))

    # 31. synth_register_storage_snapshot (data_management)
    contracts.append(_create_contract_spec(
        31, "synth_register_storage_snapshot", "Register Storage Snapshot",
        "Create a point-in-time volume snapshot with retention and tag metadata.",
        "NESTED_OBJECTS_SURFACES", "data_management",
        {
            "volume_id": {"type": "string", "minLength": 3, "description": "Target block storage volume"},
            "snapshot_metadata": {
                "type": "object",
                "description": "Descriptive snapshot labels",
                "additionalProperties": False,
                "properties": {
                    "creator": {"type": "string", "minLength": 1},
                    "environment": {"type": "string", "enum": ["prod", "stage", "dev"]},
                },
                "required": ["creator", "environment"],
            },
            "retention": {
                "type": "object",
                "description": "Snapshot expiration parameters",
                "additionalProperties": False,
                "properties": {
                    "days": {"type": "integer", "minimum": 1, "maximum": 365},
                    "lock_deletion": {"type": "boolean"},
                },
                "required": ["days"],
            },
        },
        ["volume_id", "snapshot_metadata", "retention"],
        {"volume_id": "string", "snapshot_metadata": "object", "retention": "object"},
        [
            {
                "volume_id": "vol_root_prod_01",
                "snapshot_metadata": {"creator": "sre_automation", "environment": "prod"},
                "retention": {"days": 30, "lock_deletion": True},
            },
            {
                "volume_id": "vol_data_dev",
                "snapshot_metadata": {"creator": "dev_alice", "environment": "dev"},
                "retention": {"days": 7},
            },
        ],
        [
            {"volume_id": "vol_1", "snapshot_metadata": {"creator": "c"}, "retention": {"days": 10}},
            {"volume_id": "vol_1", "snapshot_metadata": {"creator": "c", "environment": "test"}, "retention": {"days": 10}},
        ],
    ))

    # 32. synth_route_omnichannel_conversation (communications)
    contracts.append(_create_contract_spec(
        32, "synth_route_omnichannel_conversation", "Route Omnichannel Conversation",
        "Dispatch incoming support ticket across routing and priority constraints.",
        "NESTED_OBJECTS_SURFACES", "communications",
        {
            "conversation_id": {"type": "string", "minLength": 3, "description": "Customer inquiry ticket ID"},
            "routing_criteria": {
                "type": "object",
                "description": "Agent matching criteria",
                "additionalProperties": False,
                "properties": {
                    "language": {"type": "string", "minLength": 2, "description": "ISO language code"},
                    "skill_tags": {"type": "array", "items": {"type": "string"}, "description": "Required agent competencies"},
                    "priority_weight": {"type": "integer", "minimum": 1, "maximum": 100},
                },
                "required": ["language"],
            },
            "fallback_queue": {"type": "string", "description": "Default destination if no agent available"},
        },
        ["conversation_id", "routing_criteria"],
        {"conversation_id": "string", "routing_criteria": "object", "fallback_queue": "string"},
        [
            {
                "conversation_id": "conv_9921",
                "routing_criteria": {"language": "en", "skill_tags": ["billing", "enterprise"], "priority_weight": 90},
                "fallback_queue": "general_tier_1",
            },
            {
                "conversation_id": "conv_1102",
                "routing_criteria": {"language": "es"},
            },
        ],
        [
            {"conversation_id": "conv_no_criteria"},
            {"conversation_id": "c1", "routing_criteria": {"priority_weight": 50}},
        ],
    ))

    # 33. synth_publish_webhook_event (communications)
    contracts.append(_create_contract_spec(
        33, "synth_publish_webhook_event", "Publish Webhook Event",
        "Deliver a JSON notification payload to an external subscriber webhook.",
        "NESTED_OBJECTS_SURFACES", "communications",
        {
            "event_type": {"type": "string", "minLength": 3, "description": "Domain event classification"},
            "endpoint": {
                "type": "object",
                "description": "Destination HTTP configuration",
                "additionalProperties": False,
                "properties": {
                    "url": {"type": "string", "minLength": 8, "description": "HTTPS webhook URL"},
                    "signing_secret": {"type": "string", "minLength": 8, "description": "HMAC signature secret"},
                    "timeout_ms": {"type": "integer", "minimum": 100, "maximum": 10000},
                },
                "required": ["url", "signing_secret"],
            },
            "max_retries": {"type": "integer", "minimum": 0, "maximum": 5, "description": "Retry limit on 5xx failures"},
        },
        ["event_type", "endpoint"],
        {"event_type": "string", "endpoint": "object", "max_retries": "integer"},
        [
            {
                "event_type": "payment.succeeded",
                "endpoint": {"url": "https://api.partner.com/hooks", "signing_secret": "whsec_abcdef123456", "timeout_ms": 3000},
                "max_retries": 3,
            },
            {
                "event_type": "user.registered",
                "endpoint": {"url": "https://hooks.slack.com/services/T00/B00/X", "signing_secret": "secret_12345678"},
            },
        ],
        [
            {"event_type": "invoice.created"},
            {"event_type": "order.paid", "endpoint": {"url": "https://api.com"}},
        ],
    ))

    # 34. synth_export_timeseries_dataset (analytics_metrics)
    contracts.append(_create_contract_spec(
        34, "synth_export_timeseries_dataset", "Export Timeseries Dataset",
        "Trigger asynchronous bulk export of metrics data within time bounds.",
        "NESTED_OBJECTS_SURFACES", "analytics_metrics",
        {
            "dataset_name": {"type": "string", "minLength": 2, "description": "Target metrics catalog"},
            "query_window": {
                "type": "object",
                "description": "Temporal boundaries",
                "additionalProperties": False,
                "properties": {
                    "start_epoch": {"type": "integer", "minimum": 1600000000},
                    "end_epoch": {"type": "integer", "minimum": 1600000000},
                    "interval_seconds": {"type": "integer", "minimum": 1, "maximum": 3600},
                },
                "required": ["start_epoch", "end_epoch"],
            },
            "format_spec": {
                "type": "object",
                "description": "Export serialization format",
                "additionalProperties": False,
                "properties": {
                    "format_type": {"type": "string", "enum": ["csv", "parquet", "jsonl"]},
                    "compress": {"type": "boolean"},
                },
                "required": ["format_type"],
            },
        },
        ["dataset_name", "query_window", "format_spec"],
        {"dataset_name": "string", "query_window": "object", "format_spec": "object"},
        [
            {
                "dataset_name": "latency_timeseries_oct",
                "query_window": {"start_epoch": 1761500000, "end_epoch": 1761586400, "interval_seconds": 60},
                "format_spec": {"format_type": "parquet", "compress": True},
            },
            {
                "dataset_name": "error_rates",
                "query_window": {"start_epoch": 1761500000, "end_epoch": 1761510000},
                "format_spec": {"format_type": "csv"},
            },
        ],
        [
            {"dataset_name": "missing_window", "format_spec": {"format_type": "csv"}},
            {"dataset_name": "bad_format", "query_window": {"start_epoch": 1761500000, "end_epoch": 1761510000}, "format_spec": {"format_type": "xml"}},
        ],
    ))

    # 35. synth_generate_audit_scorecard (analytics_metrics)
    contracts.append(_create_contract_spec(
        35, "synth_generate_audit_scorecard", "Generate Audit Scorecard",
        "Compute infrastructure compliance scorecard against defined thresholds.",
        "NESTED_OBJECTS_SURFACES", "analytics_metrics",
        {
            "target_system": {"type": "string", "minLength": 2, "description": "Evaluated subsystem"},
            "compliance_rules": {
                "type": "object",
                "description": "Evaluated framework rules",
                "additionalProperties": False,
                "properties": {
                    "framework": {"type": "string", "enum": ["SOC2", "HIPAA", "PCI_DSS", "ISO_27001"]},
                    "strict_mode": {"type": "boolean"},
                },
                "required": ["framework"],
            },
            "thresholds": {
                "type": "object",
                "description": "Passing score limits",
                "additionalProperties": False,
                "properties": {
                    "min_passing_score": {"type": "integer", "minimum": 50, "maximum": 100},
                },
                "required": ["min_passing_score"],
            },
        },
        ["target_system", "compliance_rules", "thresholds"],
        {"target_system": "string", "compliance_rules": "object", "thresholds": "object"},
        [
            {
                "target_system": "payment_processing_cluster",
                "compliance_rules": {"framework": "PCI_DSS", "strict_mode": True},
                "thresholds": {"min_passing_score": 95},
            },
            {
                "target_system": "analytics_datalake",
                "compliance_rules": {"framework": "SOC2"},
                "thresholds": {"min_passing_score": 80},
            },
        ],
        [
            {"target_system": "sys_no_rules", "thresholds": {"min_passing_score": 80}},
            {"target_system": "sys_bad_fw", "compliance_rules": {"framework": "FEDRAMP"}, "thresholds": {"min_passing_score": 80}},
        ],
    ))

    # 36. synth_configure_sso_identity_provider (access_governance)
    contracts.append(_create_contract_spec(
        36, "synth_configure_sso_identity_provider", "Configure SSO Identity Provider",
        "Set up SAML/OIDC enterprise identity federation for a workspace.",
        "NESTED_OBJECTS_SURFACES", "access_governance",
        {
            "provider_name": {"type": "string", "minLength": 2, "description": "Federation label"},
            "idp_spec": {
                "type": "object",
                "description": "Provider connection details",
                "additionalProperties": False,
                "properties": {
                    "sso_url": {"type": "string", "minLength": 8},
                    "entity_id": {"type": "string", "minLength": 4},
                    "protocol": {"type": "string", "enum": ["SAML2", "OIDC"]},
                },
                "required": ["sso_url", "entity_id", "protocol"],
            },
            "enforce_domain_lock": {"type": "boolean", "description": "Restrict logins strictly to claimed corporate domains"},
        },
        ["provider_name", "idp_spec"],
        {"provider_name": "string", "idp_spec": "object", "enforce_domain_lock": "boolean"},
        [
            {
                "provider_name": "okta_corporate_sso",
                "idp_spec": {"sso_url": "https://company.okta.com/app/sso", "entity_id": "urn:company:okta", "protocol": "SAML2"},
                "enforce_domain_lock": True,
            },
            {
                "provider_name": "google_workspace_oidc",
                "idp_spec": {"sso_url": "https://accounts.google.com/o/oauth2/auth", "entity_id": "google-enterprise", "protocol": "OIDC"},
            },
        ],
        [
            {"provider_name": "missing_spec"},
            {"provider_name": "bad_protocol", "idp_spec": {"sso_url": "https://sso.com", "entity_id": "ent", "protocol": "KERBEROS"}},
        ],
    ))

    # 37. synth_enforce_security_boundary (access_governance)
    contracts.append(_create_contract_spec(
        37, "synth_enforce_security_boundary", "Enforce Security Boundary",
        "Apply subnet network security group filtering and packet inspection rules.",
        "NESTED_OBJECTS_SURFACES", "access_governance",
        {
            "boundary_id": {"type": "string", "minLength": 3, "description": "VPC or subnet identifier"},
            "ingress_policy": {
                "type": "object",
                "description": "Inbound packet rules",
                "additionalProperties": False,
                "properties": {
                    "allowed_cidr": {"type": "string", "minLength": 7},
                    "ports": {"type": "array", "items": {"type": "integer"}, "minItems": 1},
                },
                "required": ["allowed_cidr", "ports"],
            },
            "inspection_tier": {"type": "string", "enum": ["stateless", "stateful_inspection", "deep_packet_dpi"], "description": "Firewall filtering depth"},
        },
        ["boundary_id", "ingress_policy", "inspection_tier"],
        {"boundary_id": "string", "ingress_policy": "object", "inspection_tier": "string"},
        [
            {
                "boundary_id": "vpc_secure_prod",
                "ingress_policy": {"allowed_cidr": "10.0.0.0/16", "ports": [443, 8443]},
                "inspection_tier": "stateful_inspection",
            },
            {
                "boundary_id": "subnet_dmz",
                "ingress_policy": {"allowed_cidr": "0.0.0.0/0", "ports": [80, 443]},
                "inspection_tier": "stateless",
            },
        ],
        [
            {"boundary_id": "missing_ingress", "inspection_tier": "stateless"},
            {"boundary_id": "b1", "ingress_policy": {"allowed_cidr": "10.0.0.0/8", "ports": []}, "inspection_tier": "stateless"},
        ],
    ))

    # 38. synth_orchestrate_etl_pipeline (workflow_orchestration)
    contracts.append(_create_contract_spec(
        38, "synth_orchestrate_etl_pipeline", "Orchestrate ETL Pipeline",
        "Execute end-to-end data extraction, transformation, and load workflow.",
        "NESTED_OBJECTS_SURFACES", "workflow_orchestration",
        {
            "pipeline_name": {"type": "string", "minLength": 3, "description": "Pipeline execution job name"},
            "source_connector": {
                "type": "object",
                "description": "Origin database extractor",
                "additionalProperties": False,
                "properties": {
                    "connector_type": {"type": "string", "enum": ["postgres", "mysql", "mongodb"]},
                    "query_timeout_sec": {"type": "integer", "minimum": 1, "maximum": 300},
                },
                "required": ["connector_type"],
            },
            "sink_connector": {
                "type": "object",
                "description": "Target warehouse loader",
                "additionalProperties": False,
                "properties": {
                    "warehouse": {"type": "string", "enum": ["snowflake", "bigquery", "redshift"]},
                    "table_mode": {"type": "string", "enum": ["append", "overwrite", "merge"]},
                },
                "required": ["warehouse", "table_mode"],
            },
        },
        ["pipeline_name", "source_connector", "sink_connector"],
        {"pipeline_name": "string", "source_connector": "object", "sink_connector": "object"},
        [
            {
                "pipeline_name": "daily_customer_etl",
                "source_connector": {"connector_type": "postgres", "query_timeout_sec": 60},
                "sink_connector": {"warehouse": "snowflake", "table_mode": "append"},
            },
            {
                "pipeline_name": "events_streaming_merge",
                "source_connector": {"connector_type": "mongodb"},
                "sink_connector": {"warehouse": "bigquery", "table_mode": "merge"},
            },
        ],
        [
            {"pipeline_name": "missing_sink", "source_connector": {"connector_type": "mysql"}},
            {"pipeline_name": "bad_wh", "source_connector": {"connector_type": "postgres"}, "sink_connector": {"warehouse": "oracle", "table_mode": "append"}},
        ],
    ))

    # 39. synth_manage_deployment_rollout (workflow_orchestration)
    contracts.append(_create_contract_spec(
        39, "synth_manage_deployment_rollout", "Manage Deployment Rollout",
        "Control canary progression and rollback parameters for an application release.",
        "NESTED_OBJECTS_SURFACES", "workflow_orchestration",
        {
            "application_id": {"type": "string", "minLength": 2, "description": "Deployed microservice ID"},
            "canary_strategy": {
                "type": "object",
                "description": "Progressive traffic shift parameters",
                "additionalProperties": False,
                "properties": {
                    "initial_percentage": {"type": "integer", "minimum": 1, "maximum": 50},
                    "step_duration_minutes": {"type": "integer", "minimum": 5, "maximum": 120},
                },
                "required": ["initial_percentage", "step_duration_minutes"],
            },
            "rollback_thresholds": {
                "type": "object",
                "description": "Error circuit-breaker triggers",
                "additionalProperties": False,
                "properties": {
                    "max_error_rate_percent": {"type": "number", "minimum": 0.1, "maximum": 10.0},
                },
                "required": ["max_error_rate_percent"],
            },
        },
        ["application_id", "canary_strategy", "rollback_thresholds"],
        {"application_id": "string", "canary_strategy": "object", "rollback_thresholds": "object"},
        [
            {
                "application_id": "checkout_api",
                "canary_strategy": {"initial_percentage": 10, "step_duration_minutes": 15},
                "rollback_thresholds": {"max_error_rate_percent": 1.5},
            },
            {
                "application_id": "auth_service",
                "canary_strategy": {"initial_percentage": 5, "step_duration_minutes": 30},
                "rollback_thresholds": {"max_error_rate_percent": 0.5},
            },
        ],
        [
            {"application_id": "no_rollback", "canary_strategy": {"initial_percentage": 10, "step_duration_minutes": 10}},
            {"application_id": "bad_canary", "canary_strategy": {"initial_percentage": 80, "step_duration_minutes": 10}, "rollback_thresholds": {"max_error_rate_percent": 1.0}},
        ],
    ))

    # 40. synth_synchronize_distributed_cluster (workflow_orchestration)
    contracts.append(_create_contract_spec(
        40, "synth_synchronize_distributed_cluster", "Synchronize Distributed Cluster",
        "Coordinate cluster consensus state and membership across peer nodes.",
        "NESTED_OBJECTS_SURFACES", "workflow_orchestration",
        {
            "cluster_domain": {"type": "string", "minLength": 3, "description": "Consensus cluster domain"},
            "consensus_config": {
                "type": "object",
                "description": "Raft/Paxos consensus parameters",
                "additionalProperties": False,
                "properties": {
                    "quorum_size": {"type": "integer", "minimum": 3, "maximum": 9},
                    "election_timeout_ms": {"type": "integer", "minimum": 150, "maximum": 5000},
                },
                "required": ["quorum_size", "election_timeout_ms"],
            },
            "member_nodes": {
                "type": "array",
                "description": "Active peer node connection endpoints",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "node_id": {"type": "string", "minLength": 1},
                        "address": {"type": "string", "minLength": 7},
                    },
                    "required": ["node_id", "address"],
                },
                "minItems": 3,
            },
        },
        ["cluster_domain", "consensus_config", "member_nodes"],
        {"cluster_domain": "string", "consensus_config": "object", "member_nodes": "array[object]"},
        [
            {
                "cluster_domain": "raft_cluster_prod",
                "consensus_config": {"quorum_size": 3, "election_timeout_ms": 300},
                "member_nodes": [
                    {"node_id": "node_1", "address": "10.0.1.10:9000"},
                    {"node_id": "node_2", "address": "10.0.1.11:9000"},
                    {"node_id": "node_3", "address": "10.0.1.12:9000"},
                ],
            },
            {
                "cluster_domain": "raft_cluster_staging",
                "consensus_config": {"quorum_size": 3, "election_timeout_ms": 500},
                "member_nodes": [
                    {"node_id": "stage_1", "address": "127.0.0.1:9001"},
                    {"node_id": "stage_2", "address": "127.0.0.1:9002"},
                    {"node_id": "stage_3", "address": "127.0.0.1:9003"},
                ],
            },
        ],
        [
            {"cluster_domain": "missing_nodes", "consensus_config": {"quorum_size": 3, "election_timeout_ms": 300}},
            {"cluster_domain": "too_few_nodes", "consensus_config": {"quorum_size": 3, "election_timeout_ms": 300}, "member_nodes": [{"node_id": "n1", "address": "10.0.0.1:80"}]},
        ],
    ))

    return contracts


def generate_and_save_base_contracts() -> Dict[str, Any]:
    """Generate all 40 contracts, validate each, and write to disk."""
    os.makedirs(BASE_CONTRACTS_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(AUDIT_MD_PATH), exist_ok=True)

    validator = StageCContractValidator()
    contracts = build_synthetic_base_corpus()

    manifest_entries = []
    stratum_counts = {"SIMPLE_FLAT": 0, "MEDIUM_ARRAYS_ENUMS": 0, "NESTED_OBJECTS_SURFACES": 0}
    domain_counts = {}

    for c in contracts:
        cid = c["contract_id"]
        valid, errors = validator.validate_contract(c)
        if not valid:
            raise ValueError(f"Contract {cid} failed validation: {errors}")

        c_file = os.path.join(BASE_CONTRACTS_DIR, f"{cid}.json")
        with open(c_file, "w", encoding="utf-8") as f:
            json.dump(c, f, indent=2, sort_keys=True)
            f.write("\n")

        with open(c_file, "rb") as f:
            sha256 = hashlib.sha256(f.read()).hexdigest()

        stratum_counts[c["stratum"]] += 1
        d = c["domain"]
        domain_counts[d] = domain_counts.get(d, 0) + 1

        manifest_entries.append({
            "contract_id": cid,
            "tool_name": c["tool_name"],
            "title": c["title"],
            "stratum": c["stratum"],
            "domain": c["domain"],
            "sha256": sha256,
            "seed": c["seed"],
            "relative_path": f"data_stage_c/base_contracts/{cid}.json",
            "complexity_metrics": c["complexity_metrics"],
        })

    manifest = {
        "manifest_version": "1.0.0",
        "generator_version": GENERATOR_VERSION,
        "master_seed": MASTER_SEED,
        "total_contracts": len(manifest_entries),
        "stratum_distribution": stratum_counts,
        "domain_distribution": domain_counts,
        "contracts": manifest_entries,
    }

    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)
        f.write("\n")

    # Generate Audit MD
    with open(AUDIT_MD_PATH, "w", encoding="utf-8") as f:
        f.write("# Stage C Synthetic Base-Contract Corpus Audit\n\n")
        f.write(f"**Generator Version:** `{GENERATOR_VERSION}`  \n")
        f.write(f"**Master Random Seed:** `{MASTER_SEED}`  \n")
        f.write(f"**Total Synthetic Base Contracts:** `{len(manifest_entries)}`  \n")
        f.write(f"**Validation Status:** `100% PASS` across all contracts  \n\n")
        f.write("---\n\n")

        f.write("## 1. Stratum Distribution\n\n")
        f.write("| Stratum | Count | Percentage | Defining Structural Features |\n")
        f.write("| :--- | :---: | :---: | :--- |\n")
        f.write(f"| `SIMPLE_FLAT` | {stratum_counts['SIMPLE_FLAT']} | {stratum_counts['SIMPLE_FLAT']/len(manifest_entries)*100:.1f}% | Flat primitive scalar properties (string, integer, boolean) with length and boundary limits. |\n")
        f.write(f"| `MEDIUM_ARRAYS_ENUMS` | {stratum_counts['MEDIUM_ARRAYS_ENUMS']} | {stratum_counts['MEDIUM_ARRAYS_ENUMS']/len(manifest_entries)*100:.1f}% | Array item collections, fixed categorical enums, numeric bounds, and formatted values. |\n")
        f.write(f"| `NESTED_OBJECTS_SURFACES` | {stratum_counts['NESTED_OBJECTS_SURFACES']} | {stratum_counts['NESTED_OBJECTS_SURFACES']/len(manifest_entries)*100:.1f}% | Multi-level nested object containers, arrays of sub-objects, and composite configurations. |\n")
        f.write(f"| **Total** | **{len(manifest_entries)}** | **100.0%** | Complete synthetic evaluation foundation. |\n\n")

        f.write("---\n\n")
        f.write("## 2. Functional Domain Distribution\n\n")
        f.write("| Domain | Contract Count | Representative Synthetic Tools |\n")
        f.write("| :--- | :---: | :--- |\n")
        for d, cnt in sorted(domain_counts.items()):
            f.write(f"| `{d}` | {cnt} | Synthetic operational patterns for {d.replace('_', ' ')}. |\n")

        f.write("\n---\n\n")
        f.write("## 3. Base Contract Inventory and Complexity Accounting\n\n")
        f.write("| Contract ID | Tool Name | Stratum | Domain | Props | Req | Depth | Has Nested | Has Arrays | Has Enums |\n")
        f.write("| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |\n")
        for m in manifest_entries:
            cm = m["complexity_metrics"]
            f.write(
                f"| `{m['contract_id']}` | `{m['tool_name']}` | `{m['stratum']}` | `{m['domain']}` | "
                f"{cm['property_count']} | {cm['required_count']} | {cm['max_nesting_depth']} | "
                f"{cm['has_nested_objects']} | {cm['has_arrays']} | {cm['has_enums']} |\n"
            )

        f.write("\n---\n\n")
        f.write("## 4. Strict Provenance and Epistemic Invariants\n\n")
        f.write("1. **Zero Production Derivation:** All 40 contracts are explicitly synthetic and generated deterministically from seed.\n")
        f.write("2. **Draft-07 Compliance:** 100% of contracts strictly validate under `jsonschema.Draft7Validator` with `additionalProperties: false`.\n")
        f.write("3. **Gold and Counterexample Verification:** Every contract supplies at least 2 valid gold parameter payloads and at least 2 invalid counterexamples verified against the schema.\n")
        f.write("4. **Zero Model Execution:** Generated purely offline without model inference or token consumption.\n")

    return manifest


def main() -> int:
    manifest = generate_and_save_base_contracts()
    print(f"Synthesized and validated {manifest['total_contracts']} base contracts.")
    print(f"Manifest written to {MANIFEST_PATH}")
    print(f"Audit written to {AUDIT_MD_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
