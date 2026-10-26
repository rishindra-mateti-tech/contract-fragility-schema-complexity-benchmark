# OpenAPI 3.0 to JSON Schema Draft-07 Dialect Compatibility Audit Report

**Audit Status:** `COMPLETED_DIALECT_LIMITATIONS_IDENTIFIED`  
**Audit Scope:** 2 Validated Pilots + 13 Quarantined Batch-V1 Candidates (15 slots total)  
**Total Dialect Occurrences Detected:** `928`  
**Candidates Requiring Dialect Conversion:** `1` (SLOT_GITHUB_02)  
**Candidates Requiring Human Review:** `1`  

---

## 1. Executive Summary & Dialect Discrepancy Findings

This audit evaluates the semantic fidelity of converting OpenAPI 3.0 Schema Objects into JSON Schema Draft-07 tool call contracts. A critical semantic discrepancy exists between OpenAPI 3.0 and JSON Schema Draft-07 regarding `nullable`:

- In **OpenAPI 3.0**, `nullable: true` is an active modifier modifying the `type` declaration: it permits `null` in addition to the specified primitive type.
- In **JSON Schema Draft-07**, `nullable` is an unrecognized keyword and is completely ignored by standard validators.
- To represent nullability in JSON Schema Draft-07, the schema must declare a type union: `type: [<type>, "null"]` (or `anyOf: [{"type": <type>}, {"type": "null"}]`).
- Copying `nullable: true` verbatim into a Draft-07 contract while leaving `type: "string"` causes standard Draft-07 validators to reject `null` payloads, directly violating the source specification semantics.
- Consequently, Batch-V1 extraction candidates containing `nullable: true` are **not semantically preserved** under Draft-07 and cannot claim zero potential loss.

---

## 2. Dialect Keyword Frequency Breakdown

| Dialect Keyword | Occurrences | Semantic Risk Tier | Governing Conversion Action |
| :--- | :---: | :--- | :--- |
| `example` | 51 | LOW (Singular Annotation vs Plural Array) | Document annotation difference; retain or normalize to examples |
| `body` | 16 | UNKNOWN | Review and document |
| `endpoint` | 16 | UNKNOWN | Review and document |
| `status` | 16 | UNKNOWN | Review and document |
| `header` | 15 | UNKNOWN | Review and document |
| `path` | 15 | UNKNOWN | Review and document |
| `query` | 15 | UNKNOWN | Review and document |
| `admission_decision` | 15 | UNKNOWN | Review and document |
| `candidate_source_id` | 15 | UNKNOWN | Review and document |
| `extraction_rule_version` | 15 | UNKNOWN | Review and document |
| `extraction_timestamp` | 15 | UNKNOWN | Review and document |
| `extractor_version` | 15 | UNKNOWN | Review and document |
| `governing_specification` | 15 | UNKNOWN | Review and document |
| `http_method` | 15 | UNKNOWN | Review and document |
| `operation_id` | 15 | UNKNOWN | Review and document |
| `request_content_type` | 15 | UNKNOWN | Review and document |
| `semantic_validation_decision` | 15 | UNKNOWN | Review and document |
| `slot_id` | 15 | UNKNOWN | Review and document |
| `source_cluster_id` | 15 | UNKNOWN | Review and document |
| `source_file_blob_sha` | 15 | UNKNOWN | Review and document |
| `source_file_sha256` | 15 | UNKNOWN | Review and document |
| `source_spec_pointer` | 15 | UNKNOWN | Review and document |
| `source_structural_metrics` | 15 | UNKNOWN | Review and document |
| `target_domain` | 15 | UNKNOWN | Review and document |
| `wrapped_contract_structural_metrics` | 15 | UNKNOWN | Review and document |
| `wrapper_normalization_policy` | 15 | UNKNOWN | Review and document |
| `raw_nesting_depth` | 15 | UNKNOWN | Review and document |
| `raw_parameter_count` | 15 | UNKNOWN | Review and document |
| `surface_containers_present` | 15 | UNKNOWN | Review and document |
| `surface_containers_required` | 15 | UNKNOWN | Review and document |
| `total_property_count` | 15 | UNKNOWN | Review and document |
| `wrapped_nesting_depth` | 15 | UNKNOWN | Review and document |
| `additional_properties_closed` | 15 | UNKNOWN | Review and document |
| `is_strictly_lossless` | 15 | UNKNOWN | Review and document |
| `policy_id` | 15 | UNKNOWN | Review and document |
| `rationale` | 15 | UNKNOWN | Review and document |
| `independent_validation_claimed` | 14 | UNKNOWN | Review and document |
| `serialization_metadata` | 14 | UNKNOWN | Review and document |
| `content_type` | 14 | UNKNOWN | Review and document |
| `encoding` | 14 | UNKNOWN | Review and document |
| `encoding_metadata_present` | 14 | UNKNOWN | Review and document |
| `serialization_strategy` | 14 | UNKNOWN | Review and document |
| `creation_mode` | 13 | UNKNOWN | Review and document |
| `extractor_git_commit` | 13 | UNKNOWN | Review and document |
| `explode` | 12 | UNKNOWN | Review and document |
| `style` | 12 | UNKNOWN | Review and document |
| `expand` | 6 | UNKNOWN | Review and document |
| `metadata` | 6 | UNKNOWN | Review and document |
| `name` | 5 | UNKNOWN | Review and document |
| `nullable` | 4 | HIGH (Validation Divergence) | Convert to Draft-07 `type: [T, "null"]` and quarantine OAS keyword |
| `format` | 3 | LOW (OAS-specific format string ignored by Draft-07) | Preserve format string; document as non-validating Draft-07 annotation |
| `delivery_estimate` | 3 | UNKNOWN | Review and document |
| `fixed_amount` | 3 | UNKNOWN | Review and document |
| `value` | 3 | UNKNOWN | Review and document |
| `amount` | 3 | UNKNOWN | Review and document |
| `id` | 3 | UNKNOWN | Review and document |
| `fields` | 3 | UNKNOWN | Review and document |
| `owner` | 2 | UNKNOWN | Review and document |
| `repo` | 2 | UNKNOWN | Review and document |
| `raw_enum_density` | 2 | UNKNOWN | Review and document |
| `raw_optional_ratio` | 2 | UNKNOWN | Review and document |
| `x-openapi-encoding` | 2 | MEDIUM (Transport Serialization Metadata) | Quarantine in explicit vendor container `x-openapi-encoding` |
| `tax_behavior` | 2 | UNKNOWN | Review and document |
| `unit` | 2 | UNKNOWN | Review and document |
| `currency` | 2 | UNKNOWN | Review and document |
| `role` | 2 | UNKNOWN | Review and document |
| `login` | 2 | UNKNOWN | Review and document |
| `url` | 2 | UNKNOWN | Review and document |
| `ApplicationSid` | 2 | UNKNOWN | Review and document |
| `From` | 2 | UNKNOWN | Review and document |
| `StatusCallback` | 2 | UNKNOWN | Review and document |
| `To` | 2 | UNKNOWN | Review and document |
| `AccountSid` | 2 | UNKNOWN | Review and document |
| `base` | 1 | UNKNOWN | Review and document |
| `draft` | 1 | UNKNOWN | Review and document |
| `head` | 1 | UNKNOWN | Review and document |
| `head_repo` | 1 | UNKNOWN | Review and document |
| `issue` | 1 | UNKNOWN | Review and document |
| `maintainer_can_modify` | 1 | UNKNOWN | Review and document |
| `author_review_sign_off` | 1 | UNKNOWN | Review and document |
| `decision` | 1 | UNKNOWN | Review and document |
| `policy_note` | 1 | UNKNOWN | Review and document |
| `provenance_statement` | 1 | UNKNOWN | Review and document |
| `review_date` | 1 | UNKNOWN | Review and document |
| `reviewed_canonical_contract_sha256` | 1 | UNKNOWN | Review and document |
| `reviewed_packet_blob_sha` | 1 | UNKNOWN | Review and document |
| `reviewed_packet_git_commit` | 1 | UNKNOWN | Review and document |
| `reviewed_packet_sha256` | 1 | UNKNOWN | Review and document |
| `reviewer_name` | 1 | UNKNOWN | Review and document |
| `reviewer_role` | 1 | UNKNOWN | Review and document |
| `display_name` | 1 | UNKNOWN | Review and document |
| `tax_code` | 1 | UNKNOWN | Review and document |
| `currency_options` | 1 | UNKNOWN | Review and document |
| `folder_upload_email` | 1 | UNKNOWN | Review and document |
| `parent` | 1 | UNKNOWN | Review and document |
| `sync_state` | 1 | UNKNOWN | Review and document |
| `access` | 1 | UNKNOWN | Review and document |
| `accessible_by` | 1 | UNKNOWN | Review and document |
| `can_view_path` | 1 | UNKNOWN | Review and document |
| `expires_at` | 1 | UNKNOWN | Review and document |
| `is_access_only` | 1 | UNKNOWN | Review and document |
| `item` | 1 | UNKNOWN | Review and document |
| `notify` | 1 | UNKNOWN | Review and document |
| `address` | 1 | UNKNOWN | Review and document |
| `can_see_managed_users` | 1 | UNKNOWN | Review and document |
| `external_app_user_id` | 1 | UNKNOWN | Review and document |
| `is_exempt_from_device_limits` | 1 | UNKNOWN | Review and document |
| `is_exempt_from_login_verification` | 1 | UNKNOWN | Review and document |
| `is_external_collab_restricted` | 1 | UNKNOWN | Review and document |
| `is_platform_access_only` | 1 | UNKNOWN | Review and document |
| `is_sync_enabled` | 1 | UNKNOWN | Review and document |
| `job_title` | 1 | UNKNOWN | Review and document |
| `language` | 1 | UNKNOWN | Review and document |
| `phone` | 1 | UNKNOWN | Review and document |
| `space_amount` | 1 | UNKNOWN | Review and document |
| `timezone` | 1 | UNKNOWN | Review and document |
| `tracking_codes` | 1 | UNKNOWN | Review and document |
| `subscriptions` | 1 | UNKNOWN | Review and document |
| `account_id` | 1 | UNKNOWN | Review and document |
| `context` | 1 | UNKNOWN | Review and document |
| `state` | 1 | UNKNOWN | Review and document |
| `target_url` | 1 | UNKNOWN | Review and document |
| `sha` | 1 | UNKNOWN | Review and document |
| `allow_auto_merge` | 1 | UNKNOWN | Review and document |
| `allow_merge_commit` | 1 | UNKNOWN | Review and document |
| `allow_rebase_merge` | 1 | UNKNOWN | Review and document |
| `allow_squash_merge` | 1 | UNKNOWN | Review and document |
| `auto_init` | 1 | UNKNOWN | Review and document |
| `delete_branch_on_merge` | 1 | UNKNOWN | Review and document |
| `gitignore_template` | 1 | UNKNOWN | Review and document |
| `has_discussions` | 1 | UNKNOWN | Review and document |
| `has_downloads` | 1 | UNKNOWN | Review and document |
| `has_issues` | 1 | UNKNOWN | Review and document |
| `has_projects` | 1 | UNKNOWN | Review and document |
| `has_wiki` | 1 | UNKNOWN | Review and document |
| `homepage` | 1 | UNKNOWN | Review and document |
| `is_template` | 1 | UNKNOWN | Review and document |
| `license_template` | 1 | UNKNOWN | Review and document |
| `merge_commit_message` | 1 | UNKNOWN | Review and document |
| `merge_commit_title` | 1 | UNKNOWN | Review and document |
| `private` | 1 | UNKNOWN | Review and document |
| `squash_merge_commit_message` | 1 | UNKNOWN | Review and document |
| `squash_merge_commit_title` | 1 | UNKNOWN | Review and document |
| `team_id` | 1 | UNKNOWN | Review and document |
| `chatId` | 1 | UNKNOWN | Review and document |
| `loadingSeconds` | 1 | UNKNOWN | Review and document |
| `chat` | 1 | UNKNOWN | Review and document |
| `externalDocs` | 1 | LOW (Annotation) | Document annotation difference; retain or quarantine |
| `userId` | 1 | UNKNOWN | Review and document |
| `destination` | 1 | UNKNOWN | Review and document |
| `method` | 1 | UNKNOWN | Review and document |
| `payout_method` | 1 | UNKNOWN | Review and document |
| `source_type` | 1 | UNKNOWN | Review and document |
| `statement_descriptor` | 1 | UNKNOWN | Review and document |
| `FriendlyName` | 1 | UNKNOWN | Review and document |
| `Status` | 1 | UNKNOWN | Review and document |
| `Sid` | 1 | UNKNOWN | Review and document |
| `AddressRetention` | 1 | UNKNOWN | Review and document |
| `Attempt` | 1 | UNKNOWN | Review and document |
| `Body` | 1 | UNKNOWN | Review and document |
| `ContentRetention` | 1 | UNKNOWN | Review and document |
| `ContentSid` | 1 | UNKNOWN | Review and document |
| `ContentVariables` | 1 | UNKNOWN | Review and document |
| `FallbackFrom` | 1 | UNKNOWN | Review and document |
| `ForceDelivery` | 1 | UNKNOWN | Review and document |
| `MaxPrice` | 1 | UNKNOWN | Review and document |
| `MediaUrl` | 1 | UNKNOWN | Review and document |
| `MessageIntent` | 1 | UNKNOWN | Review and document |
| `MessagingServiceSid` | 1 | UNKNOWN | Review and document |
| `PersistentAction` | 1 | UNKNOWN | Review and document |
| `ProvideFeedback` | 1 | UNKNOWN | Review and document |
| `RiskCheck` | 1 | UNKNOWN | Review and document |
| `ScheduleType` | 1 | UNKNOWN | Review and document |
| `SendAsMms` | 1 | UNKNOWN | Review and document |
| `SendAt` | 1 | UNKNOWN | Review and document |
| `ShortenUrls` | 1 | UNKNOWN | Review and document |
| `SmartEncoded` | 1 | UNKNOWN | Review and document |
| `TrafficType` | 1 | UNKNOWN | Review and document |
| `ValidityPeriod` | 1 | UNKNOWN | Review and document |
| `ignoreFormat` | 1 | UNKNOWN | Review and document |
| `AsyncAmd` | 1 | UNKNOWN | Review and document |
| `AsyncAmdStatusCallback` | 1 | UNKNOWN | Review and document |
| `AsyncAmdStatusCallbackMethod` | 1 | UNKNOWN | Review and document |
| `Byoc` | 1 | UNKNOWN | Review and document |
| `CallReason` | 1 | UNKNOWN | Review and document |
| `CallToken` | 1 | UNKNOWN | Review and document |
| `CallerId` | 1 | UNKNOWN | Review and document |
| `ClientNotificationUrl` | 1 | UNKNOWN | Review and document |
| `FallbackMethod` | 1 | UNKNOWN | Review and document |
| `FallbackUrl` | 1 | UNKNOWN | Review and document |
| `MachineDetection` | 1 | UNKNOWN | Review and document |
| `MachineDetectionSilenceTimeout` | 1 | UNKNOWN | Review and document |
| `MachineDetectionSpeechEndThreshold` | 1 | UNKNOWN | Review and document |
| `MachineDetectionSpeechThreshold` | 1 | UNKNOWN | Review and document |
| `MachineDetectionTimeout` | 1 | UNKNOWN | Review and document |
| `Method` | 1 | UNKNOWN | Review and document |
| `Passports` | 1 | UNKNOWN | Review and document |
| `Record` | 1 | UNKNOWN | Review and document |
| `RecordingChannels` | 1 | UNKNOWN | Review and document |
| `RecordingConfigurationId` | 1 | UNKNOWN | Review and document |
| `RecordingStatusCallback` | 1 | UNKNOWN | Review and document |
| `RecordingStatusCallbackEvent` | 1 | UNKNOWN | Review and document |
| `RecordingStatusCallbackMethod` | 1 | UNKNOWN | Review and document |
| `RecordingTrack` | 1 | UNKNOWN | Review and document |
| `SendDigits` | 1 | UNKNOWN | Review and document |
| `SipAuthPassword` | 1 | UNKNOWN | Review and document |
| `SipAuthUsername` | 1 | UNKNOWN | Review and document |
| `StatusCallbackEvent` | 1 | UNKNOWN | Review and document |
| `StatusCallbackMethod` | 1 | UNKNOWN | Review and document |
| `TimeLimit` | 1 | UNKNOWN | Review and document |
| `Timeout` | 1 | UNKNOWN | Review and document |
| `Trim` | 1 | UNKNOWN | Review and document |
| `Twiml` | 1 | UNKNOWN | Review and document |
| `Url` | 1 | UNKNOWN | Review and document |

---

## 3. Slot-by-Slot Dialect Profile

| Slot ID | Cluster | Source Dialect | Total Dialect Hits | Critical Divergence? | Status & Required Remediation |
| :--- | :--- | :--- | :---: | :---: | :--- |
| `SLOT_GITHUB_01` | GitHub | OpenAPI 3.0.3 | 61 | **NO** | VALID_PILOT (examples only) |
| `SLOT_STRIPE_02` | Stripe | OpenAPI 3.0.0 | 83 | **NO** | VALID_PILOT (form serialization metadata in x-openapi-encoding) |
| `SLOT_BOX_01` | Box | OpenAPI 3.0.2 | 56 | **NO** | V1_REQUIRES_DIALECT_REVIEW (`nullable: false` quarantined in V2) |
| `SLOT_BOX_02` | Box | OpenAPI 3.0.2 | 63 | **NO** | V1_REQUIRES_DIALECT_REVIEW (singular examples) |
| `SLOT_BOX_03` | Box | OpenAPI 3.0.2 | 85 | **NO** | V1_REQUIRES_DIALECT_REVIEW (singular examples) |
| `SLOT_CHATWOOT_01` | Chatwoot | OpenAPI 3.1.0 | 49 | **NO** | V1_REQUIRES_DIALECT_REVIEW (singular examples) |
| `SLOT_GITHUB_02` | GitHub | OpenAPI 3.0.3 | 51 | **YES** | V1_INVALID_DIVERGENCE (`nullable: true` on description & target_url must convert to `["string", "null"]`) |
| `SLOT_GITHUB_03` | GitHub | OpenAPI 3.0.3 | 79 | **NO** | V1_REQUIRES_DIALECT_REVIEW (singular examples) |
| `SLOT_LINE_01` | LINE | OpenAPI 3.0.0 | 46 | **NO** | V1_REQUIRES_DIALECT_REVIEW (serialization metadata container) |
| `SLOT_LINE_02` | LINE | OpenAPI 3.0.0 | 44 | **NO** | V1_REQUIRES_DIALECT_REVIEW (serialization metadata container) |
| `SLOT_LINE_03` | LINE | OpenAPI 3.0.0 | 47 | **NO** | V1_REQUIRES_DIALECT_REVIEW (externalDocs annotation) |
| `SLOT_STRIPE_01` | Stripe | OpenAPI 3.0.0 | 65 | **NO** | V1_REQUIRES_DIALECT_REVIEW (form serialization metadata in x-openapi-encoding) |
| `SLOT_TWILIO_01` | Twilio | OpenAPI 3.0.1 | 46 | **NO** | V1_REQUIRES_DIALECT_REVIEW (clean primitive schema) |
| `SLOT_TWILIO_02` | Twilio | OpenAPI 3.0.1 | 71 | **NO** | V1_REQUIRES_DIALECT_REVIEW (clean primitive schema) |
| `SLOT_TWILIO_03` | Twilio | OpenAPI 3.0.1 | 82 | **NO** | V1_REQUIRES_DIALECT_REVIEW (clean primitive schema) |

---

## 4. Complete Dialect Occurrence Inventory

| Occurrence ID | Slot ID | Keyword | Candidate Pointer | Source Dialect | Semantic Risk | Current Valid? | Required Action |
| :--- | :--- | :--- | :--- | :--- | :--- | :---: | :--- |
| `DIALECT-SLOT_GITHUB_01-0001` | `SLOT_GITHUB_01` | `body` | `/properties/body` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_01-0002` | `SLOT_GITHUB_01` | `header` | `/properties/header` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_01-0003` | `SLOT_GITHUB_01` | `path` | `/properties/path` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_01-0004` | `SLOT_GITHUB_01` | `query` | `/properties/query` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_01-0005` | `SLOT_GITHUB_01` | `base` | `/properties/body/properties/base` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_01-0006` | `SLOT_GITHUB_01` | `body` | `/properties/body/properties/body` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_01-0007` | `SLOT_GITHUB_01` | `draft` | `/properties/body/properties/draft` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_01-0008` | `SLOT_GITHUB_01` | `head` | `/properties/body/properties/head` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_01-0009` | `SLOT_GITHUB_01` | `head_repo` | `/properties/body/properties/head_repo` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_01-0010` | `SLOT_GITHUB_01` | `issue` | `/properties/body/properties/issue` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_01-0011` | `SLOT_GITHUB_01` | `maintainer_can_modify` | `/properties/body/properties/maintainer_can_modify` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_01-0012` | `SLOT_GITHUB_01` | `example` | `/properties/body/properties/head_repo/example` | OpenAPI 3.0.3 | `LOW_ANNOTATION` | YES | `DOCUMENT_ANNOTATION_DIFFERENCE` |
| `DIALECT-SLOT_GITHUB_01-0013` | `SLOT_GITHUB_01` | `format` | `/properties/body/properties/issue/format` | OpenAPI 3.0.3 | `LOW_ANNOTATION` | YES | `DOCUMENT_ANNOTATION_DIFFERENCE` |
| `DIALECT-SLOT_GITHUB_01-0014` | `SLOT_GITHUB_01` | `example` | `/properties/body/properties/issue/example` | OpenAPI 3.0.3 | `LOW_ANNOTATION` | YES | `DOCUMENT_ANNOTATION_DIFFERENCE` |
| `DIALECT-SLOT_GITHUB_01-0015` | `SLOT_GITHUB_01` | `owner` | `/properties/path/properties/owner` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_01-0016` | `SLOT_GITHUB_01` | `repo` | `/properties/path/properties/repo` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_01-0017` | `SLOT_GITHUB_01` | `admission_decision` | `/x-benchmark-metadata/admission_decision` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_01-0018` | `SLOT_GITHUB_01` | `author_review_sign_off` | `/x-benchmark-metadata/author_review_sign_off` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_01-0019` | `SLOT_GITHUB_01` | `candidate_source_id` | `/x-benchmark-metadata/candidate_source_id` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_01-0020` | `SLOT_GITHUB_01` | `endpoint` | `/x-benchmark-metadata/endpoint` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_01-0021` | `SLOT_GITHUB_01` | `extraction_rule_version` | `/x-benchmark-metadata/extraction_rule_version` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_01-0022` | `SLOT_GITHUB_01` | `extraction_timestamp` | `/x-benchmark-metadata/extraction_timestamp` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_01-0023` | `SLOT_GITHUB_01` | `extractor_version` | `/x-benchmark-metadata/extractor_version` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_01-0024` | `SLOT_GITHUB_01` | `governing_specification` | `/x-benchmark-metadata/governing_specification` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_01-0025` | `SLOT_GITHUB_01` | `http_method` | `/x-benchmark-metadata/http_method` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_01-0026` | `SLOT_GITHUB_01` | `operation_id` | `/x-benchmark-metadata/operation_id` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_01-0027` | `SLOT_GITHUB_01` | `request_content_type` | `/x-benchmark-metadata/request_content_type` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_01-0028` | `SLOT_GITHUB_01` | `semantic_validation_decision` | `/x-benchmark-metadata/semantic_validation_decision` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_01-0029` | `SLOT_GITHUB_01` | `slot_id` | `/x-benchmark-metadata/slot_id` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_01-0030` | `SLOT_GITHUB_01` | `source_cluster_id` | `/x-benchmark-metadata/source_cluster_id` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_01-0031` | `SLOT_GITHUB_01` | `source_file_blob_sha` | `/x-benchmark-metadata/source_file_blob_sha` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_01-0032` | `SLOT_GITHUB_01` | `source_file_sha256` | `/x-benchmark-metadata/source_file_sha256` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_01-0033` | `SLOT_GITHUB_01` | `source_spec_pointer` | `/x-benchmark-metadata/source_spec_pointer` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_01-0034` | `SLOT_GITHUB_01` | `source_structural_metrics` | `/x-benchmark-metadata/source_structural_metrics` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_01-0035` | `SLOT_GITHUB_01` | `status` | `/x-benchmark-metadata/status` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_01-0036` | `SLOT_GITHUB_01` | `target_domain` | `/x-benchmark-metadata/target_domain` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_01-0037` | `SLOT_GITHUB_01` | `wrapped_contract_structural_metrics` | `/x-benchmark-metadata/wrapped_contract_structural_metrics` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_01-0038` | `SLOT_GITHUB_01` | `wrapper_normalization_policy` | `/x-benchmark-metadata/wrapper_normalization_policy` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_01-0039` | `SLOT_GITHUB_01` | `decision` | `/x-benchmark-metadata/author_review_sign_off/decision` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_01-0040` | `SLOT_GITHUB_01` | `independent_validation_claimed` | `/x-benchmark-metadata/author_review_sign_off/independent_validation_claimed` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_01-0041` | `SLOT_GITHUB_01` | `policy_note` | `/x-benchmark-metadata/author_review_sign_off/policy_note` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_01-0042` | `SLOT_GITHUB_01` | `provenance_statement` | `/x-benchmark-metadata/author_review_sign_off/provenance_statement` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_01-0043` | `SLOT_GITHUB_01` | `review_date` | `/x-benchmark-metadata/author_review_sign_off/review_date` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_01-0044` | `SLOT_GITHUB_01` | `reviewed_canonical_contract_sha256` | `/x-benchmark-metadata/author_review_sign_off/reviewed_canonical_contract_sha256` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_01-0045` | `SLOT_GITHUB_01` | `reviewed_packet_blob_sha` | `/x-benchmark-metadata/author_review_sign_off/reviewed_packet_blob_sha` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_01-0046` | `SLOT_GITHUB_01` | `reviewed_packet_git_commit` | `/x-benchmark-metadata/author_review_sign_off/reviewed_packet_git_commit` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_01-0047` | `SLOT_GITHUB_01` | `reviewed_packet_sha256` | `/x-benchmark-metadata/author_review_sign_off/reviewed_packet_sha256` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_01-0048` | `SLOT_GITHUB_01` | `reviewer_name` | `/x-benchmark-metadata/author_review_sign_off/reviewer_name` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_01-0049` | `SLOT_GITHUB_01` | `reviewer_role` | `/x-benchmark-metadata/author_review_sign_off/reviewer_role` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_01-0050` | `SLOT_GITHUB_01` | `raw_enum_density` | `/x-benchmark-metadata/source_structural_metrics/raw_enum_density` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_01-0051` | `SLOT_GITHUB_01` | `raw_nesting_depth` | `/x-benchmark-metadata/source_structural_metrics/raw_nesting_depth` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_01-0052` | `SLOT_GITHUB_01` | `raw_optional_ratio` | `/x-benchmark-metadata/source_structural_metrics/raw_optional_ratio` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_01-0053` | `SLOT_GITHUB_01` | `raw_parameter_count` | `/x-benchmark-metadata/source_structural_metrics/raw_parameter_count` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_01-0054` | `SLOT_GITHUB_01` | `surface_containers_present` | `/x-benchmark-metadata/wrapped_contract_structural_metrics/surface_containers_present` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_01-0055` | `SLOT_GITHUB_01` | `surface_containers_required` | `/x-benchmark-metadata/wrapped_contract_structural_metrics/surface_containers_required` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_01-0056` | `SLOT_GITHUB_01` | `total_property_count` | `/x-benchmark-metadata/wrapped_contract_structural_metrics/total_property_count` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_01-0057` | `SLOT_GITHUB_01` | `wrapped_nesting_depth` | `/x-benchmark-metadata/wrapped_contract_structural_metrics/wrapped_nesting_depth` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_01-0058` | `SLOT_GITHUB_01` | `additional_properties_closed` | `/x-benchmark-metadata/wrapper_normalization_policy/additional_properties_closed` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_01-0059` | `SLOT_GITHUB_01` | `is_strictly_lossless` | `/x-benchmark-metadata/wrapper_normalization_policy/is_strictly_lossless` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_01-0060` | `SLOT_GITHUB_01` | `policy_id` | `/x-benchmark-metadata/wrapper_normalization_policy/policy_id` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_01-0061` | `SLOT_GITHUB_01` | `rationale` | `/x-benchmark-metadata/wrapper_normalization_policy/rationale` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0062` | `SLOT_STRIPE_02` | `body` | `/properties/body` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0063` | `SLOT_STRIPE_02` | `header` | `/properties/header` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0064` | `SLOT_STRIPE_02` | `path` | `/properties/path` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0065` | `SLOT_STRIPE_02` | `query` | `/properties/query` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0066` | `SLOT_STRIPE_02` | `x-openapi-encoding` | `/properties/body/x-openapi-encoding` | OpenAPI 3.0.0 | `MEDIUM_TRANSPORT_METADATA` | YES | `DOCUMENT_REPRESENTATION_NORMALIZATION` |
| `DIALECT-SLOT_STRIPE_02-0067` | `SLOT_STRIPE_02` | `delivery_estimate` | `/properties/body/properties/delivery_estimate` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0068` | `SLOT_STRIPE_02` | `display_name` | `/properties/body/properties/display_name` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0069` | `SLOT_STRIPE_02` | `expand` | `/properties/body/properties/expand` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0070` | `SLOT_STRIPE_02` | `fixed_amount` | `/properties/body/properties/fixed_amount` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0071` | `SLOT_STRIPE_02` | `metadata` | `/properties/body/properties/metadata` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0072` | `SLOT_STRIPE_02` | `tax_behavior` | `/properties/body/properties/tax_behavior` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0073` | `SLOT_STRIPE_02` | `tax_code` | `/properties/body/properties/tax_code` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0074` | `SLOT_STRIPE_02` | `unit` | `/properties/body/properties/delivery_estimate/properties/maximum/properties/unit` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0075` | `SLOT_STRIPE_02` | `value` | `/properties/body/properties/delivery_estimate/properties/maximum/properties/value` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0076` | `SLOT_STRIPE_02` | `unit` | `/properties/body/properties/delivery_estimate/properties/minimum/properties/unit` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0077` | `SLOT_STRIPE_02` | `value` | `/properties/body/properties/delivery_estimate/properties/minimum/properties/value` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0078` | `SLOT_STRIPE_02` | `amount` | `/properties/body/properties/fixed_amount/properties/amount` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0079` | `SLOT_STRIPE_02` | `currency` | `/properties/body/properties/fixed_amount/properties/currency` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0080` | `SLOT_STRIPE_02` | `currency_options` | `/properties/body/properties/fixed_amount/properties/currency_options` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0081` | `SLOT_STRIPE_02` | `amount` | `/properties/body/properties/fixed_amount/properties/currency_options/additionalProperties/properties/amount` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0082` | `SLOT_STRIPE_02` | `tax_behavior` | `/properties/body/properties/fixed_amount/properties/currency_options/additionalProperties/properties/tax_behavior` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0083` | `SLOT_STRIPE_02` | `delivery_estimate` | `/properties/body/x-openapi-encoding/delivery_estimate` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0084` | `SLOT_STRIPE_02` | `expand` | `/properties/body/x-openapi-encoding/expand` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0085` | `SLOT_STRIPE_02` | `fixed_amount` | `/properties/body/x-openapi-encoding/fixed_amount` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0086` | `SLOT_STRIPE_02` | `metadata` | `/properties/body/x-openapi-encoding/metadata` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0087` | `SLOT_STRIPE_02` | `explode` | `/properties/body/x-openapi-encoding/delivery_estimate/explode` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0088` | `SLOT_STRIPE_02` | `style` | `/properties/body/x-openapi-encoding/delivery_estimate/style` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0089` | `SLOT_STRIPE_02` | `explode` | `/properties/body/x-openapi-encoding/expand/explode` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0090` | `SLOT_STRIPE_02` | `style` | `/properties/body/x-openapi-encoding/expand/style` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0091` | `SLOT_STRIPE_02` | `explode` | `/properties/body/x-openapi-encoding/fixed_amount/explode` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0092` | `SLOT_STRIPE_02` | `style` | `/properties/body/x-openapi-encoding/fixed_amount/style` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0093` | `SLOT_STRIPE_02` | `explode` | `/properties/body/x-openapi-encoding/metadata/explode` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0094` | `SLOT_STRIPE_02` | `style` | `/properties/body/x-openapi-encoding/metadata/style` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0095` | `SLOT_STRIPE_02` | `admission_decision` | `/x-benchmark-metadata/admission_decision` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0096` | `SLOT_STRIPE_02` | `candidate_source_id` | `/x-benchmark-metadata/candidate_source_id` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0097` | `SLOT_STRIPE_02` | `endpoint` | `/x-benchmark-metadata/endpoint` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0098` | `SLOT_STRIPE_02` | `extraction_rule_version` | `/x-benchmark-metadata/extraction_rule_version` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0099` | `SLOT_STRIPE_02` | `extraction_timestamp` | `/x-benchmark-metadata/extraction_timestamp` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0100` | `SLOT_STRIPE_02` | `extractor_version` | `/x-benchmark-metadata/extractor_version` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0101` | `SLOT_STRIPE_02` | `governing_specification` | `/x-benchmark-metadata/governing_specification` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0102` | `SLOT_STRIPE_02` | `http_method` | `/x-benchmark-metadata/http_method` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0103` | `SLOT_STRIPE_02` | `operation_id` | `/x-benchmark-metadata/operation_id` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0104` | `SLOT_STRIPE_02` | `request_content_type` | `/x-benchmark-metadata/request_content_type` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0105` | `SLOT_STRIPE_02` | `semantic_validation_decision` | `/x-benchmark-metadata/semantic_validation_decision` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0106` | `SLOT_STRIPE_02` | `serialization_metadata` | `/x-benchmark-metadata/serialization_metadata` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0107` | `SLOT_STRIPE_02` | `slot_id` | `/x-benchmark-metadata/slot_id` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0108` | `SLOT_STRIPE_02` | `source_cluster_id` | `/x-benchmark-metadata/source_cluster_id` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0109` | `SLOT_STRIPE_02` | `source_file_blob_sha` | `/x-benchmark-metadata/source_file_blob_sha` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0110` | `SLOT_STRIPE_02` | `source_file_sha256` | `/x-benchmark-metadata/source_file_sha256` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0111` | `SLOT_STRIPE_02` | `source_spec_pointer` | `/x-benchmark-metadata/source_spec_pointer` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0112` | `SLOT_STRIPE_02` | `source_structural_metrics` | `/x-benchmark-metadata/source_structural_metrics` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0113` | `SLOT_STRIPE_02` | `status` | `/x-benchmark-metadata/status` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0114` | `SLOT_STRIPE_02` | `target_domain` | `/x-benchmark-metadata/target_domain` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0115` | `SLOT_STRIPE_02` | `wrapped_contract_structural_metrics` | `/x-benchmark-metadata/wrapped_contract_structural_metrics` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0116` | `SLOT_STRIPE_02` | `wrapper_normalization_policy` | `/x-benchmark-metadata/wrapper_normalization_policy` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0117` | `SLOT_STRIPE_02` | `content_type` | `/x-benchmark-metadata/serialization_metadata/content_type` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0118` | `SLOT_STRIPE_02` | `encoding` | `/x-benchmark-metadata/serialization_metadata/encoding` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0119` | `SLOT_STRIPE_02` | `encoding_metadata_present` | `/x-benchmark-metadata/serialization_metadata/encoding_metadata_present` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0120` | `SLOT_STRIPE_02` | `serialization_strategy` | `/x-benchmark-metadata/serialization_metadata/serialization_strategy` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0121` | `SLOT_STRIPE_02` | `delivery_estimate` | `/x-benchmark-metadata/serialization_metadata/encoding/delivery_estimate` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0122` | `SLOT_STRIPE_02` | `expand` | `/x-benchmark-metadata/serialization_metadata/encoding/expand` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0123` | `SLOT_STRIPE_02` | `fixed_amount` | `/x-benchmark-metadata/serialization_metadata/encoding/fixed_amount` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0124` | `SLOT_STRIPE_02` | `metadata` | `/x-benchmark-metadata/serialization_metadata/encoding/metadata` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0125` | `SLOT_STRIPE_02` | `explode` | `/x-benchmark-metadata/serialization_metadata/encoding/delivery_estimate/explode` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0126` | `SLOT_STRIPE_02` | `style` | `/x-benchmark-metadata/serialization_metadata/encoding/delivery_estimate/style` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0127` | `SLOT_STRIPE_02` | `explode` | `/x-benchmark-metadata/serialization_metadata/encoding/expand/explode` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0128` | `SLOT_STRIPE_02` | `style` | `/x-benchmark-metadata/serialization_metadata/encoding/expand/style` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0129` | `SLOT_STRIPE_02` | `explode` | `/x-benchmark-metadata/serialization_metadata/encoding/fixed_amount/explode` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0130` | `SLOT_STRIPE_02` | `style` | `/x-benchmark-metadata/serialization_metadata/encoding/fixed_amount/style` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0131` | `SLOT_STRIPE_02` | `explode` | `/x-benchmark-metadata/serialization_metadata/encoding/metadata/explode` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0132` | `SLOT_STRIPE_02` | `style` | `/x-benchmark-metadata/serialization_metadata/encoding/metadata/style` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0133` | `SLOT_STRIPE_02` | `raw_enum_density` | `/x-benchmark-metadata/source_structural_metrics/raw_enum_density` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0134` | `SLOT_STRIPE_02` | `raw_nesting_depth` | `/x-benchmark-metadata/source_structural_metrics/raw_nesting_depth` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0135` | `SLOT_STRIPE_02` | `raw_optional_ratio` | `/x-benchmark-metadata/source_structural_metrics/raw_optional_ratio` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0136` | `SLOT_STRIPE_02` | `raw_parameter_count` | `/x-benchmark-metadata/source_structural_metrics/raw_parameter_count` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0137` | `SLOT_STRIPE_02` | `surface_containers_present` | `/x-benchmark-metadata/wrapped_contract_structural_metrics/surface_containers_present` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0138` | `SLOT_STRIPE_02` | `surface_containers_required` | `/x-benchmark-metadata/wrapped_contract_structural_metrics/surface_containers_required` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0139` | `SLOT_STRIPE_02` | `total_property_count` | `/x-benchmark-metadata/wrapped_contract_structural_metrics/total_property_count` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0140` | `SLOT_STRIPE_02` | `wrapped_nesting_depth` | `/x-benchmark-metadata/wrapped_contract_structural_metrics/wrapped_nesting_depth` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0141` | `SLOT_STRIPE_02` | `additional_properties_closed` | `/x-benchmark-metadata/wrapper_normalization_policy/additional_properties_closed` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0142` | `SLOT_STRIPE_02` | `is_strictly_lossless` | `/x-benchmark-metadata/wrapper_normalization_policy/is_strictly_lossless` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0143` | `SLOT_STRIPE_02` | `policy_id` | `/x-benchmark-metadata/wrapper_normalization_policy/policy_id` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_02-0144` | `SLOT_STRIPE_02` | `rationale` | `/x-benchmark-metadata/wrapper_normalization_policy/rationale` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_01-0145` | `SLOT_BOX_01` | `body` | `/properties/body` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_01-0146` | `SLOT_BOX_01` | `header` | `/properties/header` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_01-0147` | `SLOT_BOX_01` | `path` | `/properties/path` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_01-0148` | `SLOT_BOX_01` | `query` | `/properties/query` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_01-0149` | `SLOT_BOX_01` | `folder_upload_email` | `/properties/body/properties/folder_upload_email` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_01-0150` | `SLOT_BOX_01` | `name` | `/properties/body/properties/name` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_01-0151` | `SLOT_BOX_01` | `parent` | `/properties/body/properties/parent` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_01-0152` | `SLOT_BOX_01` | `sync_state` | `/properties/body/properties/sync_state` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_01-0153` | `SLOT_BOX_01` | `access` | `/properties/body/properties/folder_upload_email/allOf/0/properties/access` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_01-0154` | `SLOT_BOX_01` | `nullable` | `/properties/body/properties/folder_upload_email/allOf/0/properties/access/nullable` | OpenAPI 3.0.2 | `LOW_REDUNDANT_SYNTAX` | YES | `QUARANTINE_OAS_KEYWORD` |
| `DIALECT-SLOT_BOX_01-0155` | `SLOT_BOX_01` | `example` | `/properties/body/properties/folder_upload_email/allOf/0/properties/access/example` | OpenAPI 3.0.2 | `LOW_ANNOTATION` | YES | `DOCUMENT_ANNOTATION_DIFFERENCE` |
| `DIALECT-SLOT_BOX_01-0156` | `SLOT_BOX_01` | `example` | `/properties/body/properties/name/example` | OpenAPI 3.0.2 | `LOW_ANNOTATION` | YES | `DOCUMENT_ANNOTATION_DIFFERENCE` |
| `DIALECT-SLOT_BOX_01-0157` | `SLOT_BOX_01` | `id` | `/properties/body/properties/parent/properties/id` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_01-0158` | `SLOT_BOX_01` | `example` | `/properties/body/properties/parent/properties/id/example` | OpenAPI 3.0.2 | `LOW_ANNOTATION` | YES | `DOCUMENT_ANNOTATION_DIFFERENCE` |
| `DIALECT-SLOT_BOX_01-0159` | `SLOT_BOX_01` | `nullable` | `/properties/body/properties/sync_state/nullable` | OpenAPI 3.0.2 | `LOW_REDUNDANT_SYNTAX` | YES | `QUARANTINE_OAS_KEYWORD` |
| `DIALECT-SLOT_BOX_01-0160` | `SLOT_BOX_01` | `example` | `/properties/body/properties/sync_state/example` | OpenAPI 3.0.2 | `LOW_ANNOTATION` | YES | `DOCUMENT_ANNOTATION_DIFFERENCE` |
| `DIALECT-SLOT_BOX_01-0161` | `SLOT_BOX_01` | `fields` | `/properties/query/properties/fields` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_01-0162` | `SLOT_BOX_01` | `admission_decision` | `/x-benchmark-metadata/admission_decision` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_01-0163` | `SLOT_BOX_01` | `candidate_source_id` | `/x-benchmark-metadata/candidate_source_id` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_01-0164` | `SLOT_BOX_01` | `creation_mode` | `/x-benchmark-metadata/creation_mode` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_01-0165` | `SLOT_BOX_01` | `endpoint` | `/x-benchmark-metadata/endpoint` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_01-0166` | `SLOT_BOX_01` | `extraction_rule_version` | `/x-benchmark-metadata/extraction_rule_version` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_01-0167` | `SLOT_BOX_01` | `extraction_timestamp` | `/x-benchmark-metadata/extraction_timestamp` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_01-0168` | `SLOT_BOX_01` | `extractor_git_commit` | `/x-benchmark-metadata/extractor_git_commit` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_01-0169` | `SLOT_BOX_01` | `extractor_version` | `/x-benchmark-metadata/extractor_version` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_01-0170` | `SLOT_BOX_01` | `governing_specification` | `/x-benchmark-metadata/governing_specification` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_01-0171` | `SLOT_BOX_01` | `http_method` | `/x-benchmark-metadata/http_method` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_01-0172` | `SLOT_BOX_01` | `independent_validation_claimed` | `/x-benchmark-metadata/independent_validation_claimed` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_01-0173` | `SLOT_BOX_01` | `operation_id` | `/x-benchmark-metadata/operation_id` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_01-0174` | `SLOT_BOX_01` | `request_content_type` | `/x-benchmark-metadata/request_content_type` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_01-0175` | `SLOT_BOX_01` | `semantic_validation_decision` | `/x-benchmark-metadata/semantic_validation_decision` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_01-0176` | `SLOT_BOX_01` | `serialization_metadata` | `/x-benchmark-metadata/serialization_metadata` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_01-0177` | `SLOT_BOX_01` | `slot_id` | `/x-benchmark-metadata/slot_id` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_01-0178` | `SLOT_BOX_01` | `source_cluster_id` | `/x-benchmark-metadata/source_cluster_id` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_01-0179` | `SLOT_BOX_01` | `source_file_blob_sha` | `/x-benchmark-metadata/source_file_blob_sha` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_01-0180` | `SLOT_BOX_01` | `source_file_sha256` | `/x-benchmark-metadata/source_file_sha256` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_01-0181` | `SLOT_BOX_01` | `source_spec_pointer` | `/x-benchmark-metadata/source_spec_pointer` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_01-0182` | `SLOT_BOX_01` | `source_structural_metrics` | `/x-benchmark-metadata/source_structural_metrics` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_01-0183` | `SLOT_BOX_01` | `status` | `/x-benchmark-metadata/status` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_01-0184` | `SLOT_BOX_01` | `target_domain` | `/x-benchmark-metadata/target_domain` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_01-0185` | `SLOT_BOX_01` | `wrapped_contract_structural_metrics` | `/x-benchmark-metadata/wrapped_contract_structural_metrics` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_01-0186` | `SLOT_BOX_01` | `wrapper_normalization_policy` | `/x-benchmark-metadata/wrapper_normalization_policy` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_01-0187` | `SLOT_BOX_01` | `content_type` | `/x-benchmark-metadata/serialization_metadata/content_type` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_01-0188` | `SLOT_BOX_01` | `encoding` | `/x-benchmark-metadata/serialization_metadata/encoding` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_01-0189` | `SLOT_BOX_01` | `encoding_metadata_present` | `/x-benchmark-metadata/serialization_metadata/encoding_metadata_present` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_01-0190` | `SLOT_BOX_01` | `serialization_strategy` | `/x-benchmark-metadata/serialization_metadata/serialization_strategy` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_01-0191` | `SLOT_BOX_01` | `raw_nesting_depth` | `/x-benchmark-metadata/source_structural_metrics/raw_nesting_depth` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_01-0192` | `SLOT_BOX_01` | `raw_parameter_count` | `/x-benchmark-metadata/source_structural_metrics/raw_parameter_count` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_01-0193` | `SLOT_BOX_01` | `surface_containers_present` | `/x-benchmark-metadata/wrapped_contract_structural_metrics/surface_containers_present` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_01-0194` | `SLOT_BOX_01` | `surface_containers_required` | `/x-benchmark-metadata/wrapped_contract_structural_metrics/surface_containers_required` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_01-0195` | `SLOT_BOX_01` | `total_property_count` | `/x-benchmark-metadata/wrapped_contract_structural_metrics/total_property_count` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_01-0196` | `SLOT_BOX_01` | `wrapped_nesting_depth` | `/x-benchmark-metadata/wrapped_contract_structural_metrics/wrapped_nesting_depth` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_01-0197` | `SLOT_BOX_01` | `additional_properties_closed` | `/x-benchmark-metadata/wrapper_normalization_policy/additional_properties_closed` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_01-0198` | `SLOT_BOX_01` | `is_strictly_lossless` | `/x-benchmark-metadata/wrapper_normalization_policy/is_strictly_lossless` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_01-0199` | `SLOT_BOX_01` | `policy_id` | `/x-benchmark-metadata/wrapper_normalization_policy/policy_id` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_01-0200` | `SLOT_BOX_01` | `rationale` | `/x-benchmark-metadata/wrapper_normalization_policy/rationale` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_02-0201` | `SLOT_BOX_02` | `body` | `/properties/body` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_02-0202` | `SLOT_BOX_02` | `header` | `/properties/header` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_02-0203` | `SLOT_BOX_02` | `path` | `/properties/path` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_02-0204` | `SLOT_BOX_02` | `query` | `/properties/query` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_02-0205` | `SLOT_BOX_02` | `accessible_by` | `/properties/body/properties/accessible_by` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_02-0206` | `SLOT_BOX_02` | `can_view_path` | `/properties/body/properties/can_view_path` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_02-0207` | `SLOT_BOX_02` | `expires_at` | `/properties/body/properties/expires_at` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_02-0208` | `SLOT_BOX_02` | `is_access_only` | `/properties/body/properties/is_access_only` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_02-0209` | `SLOT_BOX_02` | `item` | `/properties/body/properties/item` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_02-0210` | `SLOT_BOX_02` | `role` | `/properties/body/properties/role` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_02-0211` | `SLOT_BOX_02` | `id` | `/properties/body/properties/accessible_by/properties/id` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_02-0212` | `SLOT_BOX_02` | `login` | `/properties/body/properties/accessible_by/properties/login` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_02-0213` | `SLOT_BOX_02` | `example` | `/properties/body/properties/accessible_by/properties/id/example` | OpenAPI 3.0.2 | `LOW_ANNOTATION` | YES | `DOCUMENT_ANNOTATION_DIFFERENCE` |
| `DIALECT-SLOT_BOX_02-0214` | `SLOT_BOX_02` | `example` | `/properties/body/properties/accessible_by/properties/login/example` | OpenAPI 3.0.2 | `LOW_ANNOTATION` | YES | `DOCUMENT_ANNOTATION_DIFFERENCE` |
| `DIALECT-SLOT_BOX_02-0215` | `SLOT_BOX_02` | `example` | `/properties/body/properties/accessible_by/properties/type/example` | OpenAPI 3.0.2 | `LOW_ANNOTATION` | YES | `DOCUMENT_ANNOTATION_DIFFERENCE` |
| `DIALECT-SLOT_BOX_02-0216` | `SLOT_BOX_02` | `example` | `/properties/body/properties/can_view_path/example` | OpenAPI 3.0.2 | `LOW_ANNOTATION` | YES | `DOCUMENT_ANNOTATION_DIFFERENCE` |
| `DIALECT-SLOT_BOX_02-0217` | `SLOT_BOX_02` | `example` | `/properties/body/properties/expires_at/example` | OpenAPI 3.0.2 | `LOW_ANNOTATION` | YES | `DOCUMENT_ANNOTATION_DIFFERENCE` |
| `DIALECT-SLOT_BOX_02-0218` | `SLOT_BOX_02` | `example` | `/properties/body/properties/is_access_only/example` | OpenAPI 3.0.2 | `LOW_ANNOTATION` | YES | `DOCUMENT_ANNOTATION_DIFFERENCE` |
| `DIALECT-SLOT_BOX_02-0219` | `SLOT_BOX_02` | `id` | `/properties/body/properties/item/properties/id` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_02-0220` | `SLOT_BOX_02` | `example` | `/properties/body/properties/item/properties/id/example` | OpenAPI 3.0.2 | `LOW_ANNOTATION` | YES | `DOCUMENT_ANNOTATION_DIFFERENCE` |
| `DIALECT-SLOT_BOX_02-0221` | `SLOT_BOX_02` | `example` | `/properties/body/properties/item/properties/type/example` | OpenAPI 3.0.2 | `LOW_ANNOTATION` | YES | `DOCUMENT_ANNOTATION_DIFFERENCE` |
| `DIALECT-SLOT_BOX_02-0222` | `SLOT_BOX_02` | `example` | `/properties/body/properties/role/example` | OpenAPI 3.0.2 | `LOW_ANNOTATION` | YES | `DOCUMENT_ANNOTATION_DIFFERENCE` |
| `DIALECT-SLOT_BOX_02-0223` | `SLOT_BOX_02` | `fields` | `/properties/query/properties/fields` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_02-0224` | `SLOT_BOX_02` | `notify` | `/properties/query/properties/notify` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_02-0225` | `SLOT_BOX_02` | `admission_decision` | `/x-benchmark-metadata/admission_decision` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_02-0226` | `SLOT_BOX_02` | `candidate_source_id` | `/x-benchmark-metadata/candidate_source_id` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_02-0227` | `SLOT_BOX_02` | `creation_mode` | `/x-benchmark-metadata/creation_mode` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_02-0228` | `SLOT_BOX_02` | `endpoint` | `/x-benchmark-metadata/endpoint` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_02-0229` | `SLOT_BOX_02` | `extraction_rule_version` | `/x-benchmark-metadata/extraction_rule_version` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_02-0230` | `SLOT_BOX_02` | `extraction_timestamp` | `/x-benchmark-metadata/extraction_timestamp` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_02-0231` | `SLOT_BOX_02` | `extractor_git_commit` | `/x-benchmark-metadata/extractor_git_commit` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_02-0232` | `SLOT_BOX_02` | `extractor_version` | `/x-benchmark-metadata/extractor_version` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_02-0233` | `SLOT_BOX_02` | `governing_specification` | `/x-benchmark-metadata/governing_specification` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_02-0234` | `SLOT_BOX_02` | `http_method` | `/x-benchmark-metadata/http_method` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_02-0235` | `SLOT_BOX_02` | `independent_validation_claimed` | `/x-benchmark-metadata/independent_validation_claimed` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_02-0236` | `SLOT_BOX_02` | `operation_id` | `/x-benchmark-metadata/operation_id` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_02-0237` | `SLOT_BOX_02` | `request_content_type` | `/x-benchmark-metadata/request_content_type` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_02-0238` | `SLOT_BOX_02` | `semantic_validation_decision` | `/x-benchmark-metadata/semantic_validation_decision` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_02-0239` | `SLOT_BOX_02` | `serialization_metadata` | `/x-benchmark-metadata/serialization_metadata` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_02-0240` | `SLOT_BOX_02` | `slot_id` | `/x-benchmark-metadata/slot_id` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_02-0241` | `SLOT_BOX_02` | `source_cluster_id` | `/x-benchmark-metadata/source_cluster_id` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_02-0242` | `SLOT_BOX_02` | `source_file_blob_sha` | `/x-benchmark-metadata/source_file_blob_sha` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_02-0243` | `SLOT_BOX_02` | `source_file_sha256` | `/x-benchmark-metadata/source_file_sha256` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_02-0244` | `SLOT_BOX_02` | `source_spec_pointer` | `/x-benchmark-metadata/source_spec_pointer` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_02-0245` | `SLOT_BOX_02` | `source_structural_metrics` | `/x-benchmark-metadata/source_structural_metrics` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_02-0246` | `SLOT_BOX_02` | `status` | `/x-benchmark-metadata/status` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_02-0247` | `SLOT_BOX_02` | `target_domain` | `/x-benchmark-metadata/target_domain` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_02-0248` | `SLOT_BOX_02` | `wrapped_contract_structural_metrics` | `/x-benchmark-metadata/wrapped_contract_structural_metrics` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_02-0249` | `SLOT_BOX_02` | `wrapper_normalization_policy` | `/x-benchmark-metadata/wrapper_normalization_policy` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_02-0250` | `SLOT_BOX_02` | `content_type` | `/x-benchmark-metadata/serialization_metadata/content_type` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_02-0251` | `SLOT_BOX_02` | `encoding` | `/x-benchmark-metadata/serialization_metadata/encoding` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_02-0252` | `SLOT_BOX_02` | `encoding_metadata_present` | `/x-benchmark-metadata/serialization_metadata/encoding_metadata_present` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_02-0253` | `SLOT_BOX_02` | `serialization_strategy` | `/x-benchmark-metadata/serialization_metadata/serialization_strategy` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_02-0254` | `SLOT_BOX_02` | `raw_nesting_depth` | `/x-benchmark-metadata/source_structural_metrics/raw_nesting_depth` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_02-0255` | `SLOT_BOX_02` | `raw_parameter_count` | `/x-benchmark-metadata/source_structural_metrics/raw_parameter_count` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_02-0256` | `SLOT_BOX_02` | `surface_containers_present` | `/x-benchmark-metadata/wrapped_contract_structural_metrics/surface_containers_present` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_02-0257` | `SLOT_BOX_02` | `surface_containers_required` | `/x-benchmark-metadata/wrapped_contract_structural_metrics/surface_containers_required` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_02-0258` | `SLOT_BOX_02` | `total_property_count` | `/x-benchmark-metadata/wrapped_contract_structural_metrics/total_property_count` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_02-0259` | `SLOT_BOX_02` | `wrapped_nesting_depth` | `/x-benchmark-metadata/wrapped_contract_structural_metrics/wrapped_nesting_depth` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_02-0260` | `SLOT_BOX_02` | `additional_properties_closed` | `/x-benchmark-metadata/wrapper_normalization_policy/additional_properties_closed` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_02-0261` | `SLOT_BOX_02` | `is_strictly_lossless` | `/x-benchmark-metadata/wrapper_normalization_policy/is_strictly_lossless` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_02-0262` | `SLOT_BOX_02` | `policy_id` | `/x-benchmark-metadata/wrapper_normalization_policy/policy_id` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_02-0263` | `SLOT_BOX_02` | `rationale` | `/x-benchmark-metadata/wrapper_normalization_policy/rationale` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_03-0264` | `SLOT_BOX_03` | `body` | `/properties/body` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_03-0265` | `SLOT_BOX_03` | `header` | `/properties/header` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_03-0266` | `SLOT_BOX_03` | `path` | `/properties/path` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_03-0267` | `SLOT_BOX_03` | `query` | `/properties/query` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_03-0268` | `SLOT_BOX_03` | `address` | `/properties/body/properties/address` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_03-0269` | `SLOT_BOX_03` | `can_see_managed_users` | `/properties/body/properties/can_see_managed_users` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_03-0270` | `SLOT_BOX_03` | `external_app_user_id` | `/properties/body/properties/external_app_user_id` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_03-0271` | `SLOT_BOX_03` | `is_exempt_from_device_limits` | `/properties/body/properties/is_exempt_from_device_limits` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_03-0272` | `SLOT_BOX_03` | `is_exempt_from_login_verification` | `/properties/body/properties/is_exempt_from_login_verification` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_03-0273` | `SLOT_BOX_03` | `is_external_collab_restricted` | `/properties/body/properties/is_external_collab_restricted` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_03-0274` | `SLOT_BOX_03` | `is_platform_access_only` | `/properties/body/properties/is_platform_access_only` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_03-0275` | `SLOT_BOX_03` | `is_sync_enabled` | `/properties/body/properties/is_sync_enabled` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_03-0276` | `SLOT_BOX_03` | `job_title` | `/properties/body/properties/job_title` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_03-0277` | `SLOT_BOX_03` | `language` | `/properties/body/properties/language` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_03-0278` | `SLOT_BOX_03` | `login` | `/properties/body/properties/login` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_03-0279` | `SLOT_BOX_03` | `name` | `/properties/body/properties/name` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_03-0280` | `SLOT_BOX_03` | `phone` | `/properties/body/properties/phone` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_03-0281` | `SLOT_BOX_03` | `role` | `/properties/body/properties/role` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_03-0282` | `SLOT_BOX_03` | `space_amount` | `/properties/body/properties/space_amount` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_03-0283` | `SLOT_BOX_03` | `status` | `/properties/body/properties/status` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_03-0284` | `SLOT_BOX_03` | `timezone` | `/properties/body/properties/timezone` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_03-0285` | `SLOT_BOX_03` | `tracking_codes` | `/properties/body/properties/tracking_codes` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_03-0286` | `SLOT_BOX_03` | `example` | `/properties/body/properties/address/example` | OpenAPI 3.0.2 | `LOW_ANNOTATION` | YES | `DOCUMENT_ANNOTATION_DIFFERENCE` |
| `DIALECT-SLOT_BOX_03-0287` | `SLOT_BOX_03` | `example` | `/properties/body/properties/can_see_managed_users/example` | OpenAPI 3.0.2 | `LOW_ANNOTATION` | YES | `DOCUMENT_ANNOTATION_DIFFERENCE` |
| `DIALECT-SLOT_BOX_03-0288` | `SLOT_BOX_03` | `example` | `/properties/body/properties/external_app_user_id/example` | OpenAPI 3.0.2 | `LOW_ANNOTATION` | YES | `DOCUMENT_ANNOTATION_DIFFERENCE` |
| `DIALECT-SLOT_BOX_03-0289` | `SLOT_BOX_03` | `example` | `/properties/body/properties/is_exempt_from_device_limits/example` | OpenAPI 3.0.2 | `LOW_ANNOTATION` | YES | `DOCUMENT_ANNOTATION_DIFFERENCE` |
| `DIALECT-SLOT_BOX_03-0290` | `SLOT_BOX_03` | `example` | `/properties/body/properties/is_exempt_from_login_verification/example` | OpenAPI 3.0.2 | `LOW_ANNOTATION` | YES | `DOCUMENT_ANNOTATION_DIFFERENCE` |
| `DIALECT-SLOT_BOX_03-0291` | `SLOT_BOX_03` | `example` | `/properties/body/properties/is_external_collab_restricted/example` | OpenAPI 3.0.2 | `LOW_ANNOTATION` | YES | `DOCUMENT_ANNOTATION_DIFFERENCE` |
| `DIALECT-SLOT_BOX_03-0292` | `SLOT_BOX_03` | `example` | `/properties/body/properties/is_platform_access_only/example` | OpenAPI 3.0.2 | `LOW_ANNOTATION` | YES | `DOCUMENT_ANNOTATION_DIFFERENCE` |
| `DIALECT-SLOT_BOX_03-0293` | `SLOT_BOX_03` | `example` | `/properties/body/properties/is_sync_enabled/example` | OpenAPI 3.0.2 | `LOW_ANNOTATION` | YES | `DOCUMENT_ANNOTATION_DIFFERENCE` |
| `DIALECT-SLOT_BOX_03-0294` | `SLOT_BOX_03` | `example` | `/properties/body/properties/job_title/example` | OpenAPI 3.0.2 | `LOW_ANNOTATION` | YES | `DOCUMENT_ANNOTATION_DIFFERENCE` |
| `DIALECT-SLOT_BOX_03-0295` | `SLOT_BOX_03` | `example` | `/properties/body/properties/language/example` | OpenAPI 3.0.2 | `LOW_ANNOTATION` | YES | `DOCUMENT_ANNOTATION_DIFFERENCE` |
| `DIALECT-SLOT_BOX_03-0296` | `SLOT_BOX_03` | `example` | `/properties/body/properties/login/example` | OpenAPI 3.0.2 | `LOW_ANNOTATION` | YES | `DOCUMENT_ANNOTATION_DIFFERENCE` |
| `DIALECT-SLOT_BOX_03-0297` | `SLOT_BOX_03` | `example` | `/properties/body/properties/name/example` | OpenAPI 3.0.2 | `LOW_ANNOTATION` | YES | `DOCUMENT_ANNOTATION_DIFFERENCE` |
| `DIALECT-SLOT_BOX_03-0298` | `SLOT_BOX_03` | `example` | `/properties/body/properties/phone/example` | OpenAPI 3.0.2 | `LOW_ANNOTATION` | YES | `DOCUMENT_ANNOTATION_DIFFERENCE` |
| `DIALECT-SLOT_BOX_03-0299` | `SLOT_BOX_03` | `example` | `/properties/body/properties/role/example` | OpenAPI 3.0.2 | `LOW_ANNOTATION` | YES | `DOCUMENT_ANNOTATION_DIFFERENCE` |
| `DIALECT-SLOT_BOX_03-0300` | `SLOT_BOX_03` | `format` | `/properties/body/properties/space_amount/format` | OpenAPI 3.0.2 | `LOW_ANNOTATION` | YES | `DOCUMENT_ANNOTATION_DIFFERENCE` |
| `DIALECT-SLOT_BOX_03-0301` | `SLOT_BOX_03` | `example` | `/properties/body/properties/space_amount/example` | OpenAPI 3.0.2 | `LOW_ANNOTATION` | YES | `DOCUMENT_ANNOTATION_DIFFERENCE` |
| `DIALECT-SLOT_BOX_03-0302` | `SLOT_BOX_03` | `example` | `/properties/body/properties/status/example` | OpenAPI 3.0.2 | `LOW_ANNOTATION` | YES | `DOCUMENT_ANNOTATION_DIFFERENCE` |
| `DIALECT-SLOT_BOX_03-0303` | `SLOT_BOX_03` | `example` | `/properties/body/properties/timezone/example` | OpenAPI 3.0.2 | `LOW_ANNOTATION` | YES | `DOCUMENT_ANNOTATION_DIFFERENCE` |
| `DIALECT-SLOT_BOX_03-0304` | `SLOT_BOX_03` | `name` | `/properties/body/properties/tracking_codes/items/properties/name` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_03-0305` | `SLOT_BOX_03` | `value` | `/properties/body/properties/tracking_codes/items/properties/value` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_03-0306` | `SLOT_BOX_03` | `example` | `/properties/body/properties/tracking_codes/items/properties/name/example` | OpenAPI 3.0.2 | `LOW_ANNOTATION` | YES | `DOCUMENT_ANNOTATION_DIFFERENCE` |
| `DIALECT-SLOT_BOX_03-0307` | `SLOT_BOX_03` | `example` | `/properties/body/properties/tracking_codes/items/properties/type/example` | OpenAPI 3.0.2 | `LOW_ANNOTATION` | YES | `DOCUMENT_ANNOTATION_DIFFERENCE` |
| `DIALECT-SLOT_BOX_03-0308` | `SLOT_BOX_03` | `example` | `/properties/body/properties/tracking_codes/items/properties/value/example` | OpenAPI 3.0.2 | `LOW_ANNOTATION` | YES | `DOCUMENT_ANNOTATION_DIFFERENCE` |
| `DIALECT-SLOT_BOX_03-0309` | `SLOT_BOX_03` | `fields` | `/properties/query/properties/fields` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_03-0310` | `SLOT_BOX_03` | `admission_decision` | `/x-benchmark-metadata/admission_decision` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_03-0311` | `SLOT_BOX_03` | `candidate_source_id` | `/x-benchmark-metadata/candidate_source_id` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_03-0312` | `SLOT_BOX_03` | `creation_mode` | `/x-benchmark-metadata/creation_mode` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_03-0313` | `SLOT_BOX_03` | `endpoint` | `/x-benchmark-metadata/endpoint` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_03-0314` | `SLOT_BOX_03` | `extraction_rule_version` | `/x-benchmark-metadata/extraction_rule_version` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_03-0315` | `SLOT_BOX_03` | `extraction_timestamp` | `/x-benchmark-metadata/extraction_timestamp` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_03-0316` | `SLOT_BOX_03` | `extractor_git_commit` | `/x-benchmark-metadata/extractor_git_commit` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_03-0317` | `SLOT_BOX_03` | `extractor_version` | `/x-benchmark-metadata/extractor_version` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_03-0318` | `SLOT_BOX_03` | `governing_specification` | `/x-benchmark-metadata/governing_specification` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_03-0319` | `SLOT_BOX_03` | `http_method` | `/x-benchmark-metadata/http_method` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_03-0320` | `SLOT_BOX_03` | `independent_validation_claimed` | `/x-benchmark-metadata/independent_validation_claimed` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_03-0321` | `SLOT_BOX_03` | `operation_id` | `/x-benchmark-metadata/operation_id` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_03-0322` | `SLOT_BOX_03` | `request_content_type` | `/x-benchmark-metadata/request_content_type` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_03-0323` | `SLOT_BOX_03` | `semantic_validation_decision` | `/x-benchmark-metadata/semantic_validation_decision` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_03-0324` | `SLOT_BOX_03` | `serialization_metadata` | `/x-benchmark-metadata/serialization_metadata` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_03-0325` | `SLOT_BOX_03` | `slot_id` | `/x-benchmark-metadata/slot_id` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_03-0326` | `SLOT_BOX_03` | `source_cluster_id` | `/x-benchmark-metadata/source_cluster_id` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_03-0327` | `SLOT_BOX_03` | `source_file_blob_sha` | `/x-benchmark-metadata/source_file_blob_sha` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_03-0328` | `SLOT_BOX_03` | `source_file_sha256` | `/x-benchmark-metadata/source_file_sha256` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_03-0329` | `SLOT_BOX_03` | `source_spec_pointer` | `/x-benchmark-metadata/source_spec_pointer` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_03-0330` | `SLOT_BOX_03` | `source_structural_metrics` | `/x-benchmark-metadata/source_structural_metrics` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_03-0331` | `SLOT_BOX_03` | `status` | `/x-benchmark-metadata/status` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_03-0332` | `SLOT_BOX_03` | `target_domain` | `/x-benchmark-metadata/target_domain` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_03-0333` | `SLOT_BOX_03` | `wrapped_contract_structural_metrics` | `/x-benchmark-metadata/wrapped_contract_structural_metrics` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_03-0334` | `SLOT_BOX_03` | `wrapper_normalization_policy` | `/x-benchmark-metadata/wrapper_normalization_policy` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_03-0335` | `SLOT_BOX_03` | `content_type` | `/x-benchmark-metadata/serialization_metadata/content_type` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_03-0336` | `SLOT_BOX_03` | `encoding` | `/x-benchmark-metadata/serialization_metadata/encoding` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_03-0337` | `SLOT_BOX_03` | `encoding_metadata_present` | `/x-benchmark-metadata/serialization_metadata/encoding_metadata_present` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_03-0338` | `SLOT_BOX_03` | `serialization_strategy` | `/x-benchmark-metadata/serialization_metadata/serialization_strategy` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_03-0339` | `SLOT_BOX_03` | `raw_nesting_depth` | `/x-benchmark-metadata/source_structural_metrics/raw_nesting_depth` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_03-0340` | `SLOT_BOX_03` | `raw_parameter_count` | `/x-benchmark-metadata/source_structural_metrics/raw_parameter_count` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_03-0341` | `SLOT_BOX_03` | `surface_containers_present` | `/x-benchmark-metadata/wrapped_contract_structural_metrics/surface_containers_present` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_03-0342` | `SLOT_BOX_03` | `surface_containers_required` | `/x-benchmark-metadata/wrapped_contract_structural_metrics/surface_containers_required` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_03-0343` | `SLOT_BOX_03` | `total_property_count` | `/x-benchmark-metadata/wrapped_contract_structural_metrics/total_property_count` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_03-0344` | `SLOT_BOX_03` | `wrapped_nesting_depth` | `/x-benchmark-metadata/wrapped_contract_structural_metrics/wrapped_nesting_depth` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_03-0345` | `SLOT_BOX_03` | `additional_properties_closed` | `/x-benchmark-metadata/wrapper_normalization_policy/additional_properties_closed` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_03-0346` | `SLOT_BOX_03` | `is_strictly_lossless` | `/x-benchmark-metadata/wrapper_normalization_policy/is_strictly_lossless` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_03-0347` | `SLOT_BOX_03` | `policy_id` | `/x-benchmark-metadata/wrapper_normalization_policy/policy_id` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_BOX_03-0348` | `SLOT_BOX_03` | `rationale` | `/x-benchmark-metadata/wrapper_normalization_policy/rationale` | OpenAPI 3.0.2 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_CHATWOOT_01-0349` | `SLOT_CHATWOOT_01` | `body` | `/properties/body` | OpenAPI 3.1.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_CHATWOOT_01-0350` | `SLOT_CHATWOOT_01` | `header` | `/properties/header` | OpenAPI 3.1.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_CHATWOOT_01-0351` | `SLOT_CHATWOOT_01` | `path` | `/properties/path` | OpenAPI 3.1.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_CHATWOOT_01-0352` | `SLOT_CHATWOOT_01` | `query` | `/properties/query` | OpenAPI 3.1.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_CHATWOOT_01-0353` | `SLOT_CHATWOOT_01` | `name` | `/properties/body/properties/name` | OpenAPI 3.1.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_CHATWOOT_01-0354` | `SLOT_CHATWOOT_01` | `subscriptions` | `/properties/body/properties/subscriptions` | OpenAPI 3.1.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_CHATWOOT_01-0355` | `SLOT_CHATWOOT_01` | `url` | `/properties/body/properties/url` | OpenAPI 3.1.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_CHATWOOT_01-0356` | `SLOT_CHATWOOT_01` | `example` | `/properties/body/properties/subscriptions/example` | OpenAPI 3.1.0 | `LOW_ANNOTATION` | YES | `DOCUMENT_ANNOTATION_DIFFERENCE` |
| `DIALECT-SLOT_CHATWOOT_01-0357` | `SLOT_CHATWOOT_01` | `example` | `/properties/body/properties/url/example` | OpenAPI 3.1.0 | `LOW_ANNOTATION` | YES | `DOCUMENT_ANNOTATION_DIFFERENCE` |
| `DIALECT-SLOT_CHATWOOT_01-0358` | `SLOT_CHATWOOT_01` | `account_id` | `/properties/path/properties/account_id` | OpenAPI 3.1.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_CHATWOOT_01-0359` | `SLOT_CHATWOOT_01` | `admission_decision` | `/x-benchmark-metadata/admission_decision` | OpenAPI 3.1.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_CHATWOOT_01-0360` | `SLOT_CHATWOOT_01` | `candidate_source_id` | `/x-benchmark-metadata/candidate_source_id` | OpenAPI 3.1.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_CHATWOOT_01-0361` | `SLOT_CHATWOOT_01` | `creation_mode` | `/x-benchmark-metadata/creation_mode` | OpenAPI 3.1.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_CHATWOOT_01-0362` | `SLOT_CHATWOOT_01` | `endpoint` | `/x-benchmark-metadata/endpoint` | OpenAPI 3.1.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_CHATWOOT_01-0363` | `SLOT_CHATWOOT_01` | `extraction_rule_version` | `/x-benchmark-metadata/extraction_rule_version` | OpenAPI 3.1.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_CHATWOOT_01-0364` | `SLOT_CHATWOOT_01` | `extraction_timestamp` | `/x-benchmark-metadata/extraction_timestamp` | OpenAPI 3.1.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_CHATWOOT_01-0365` | `SLOT_CHATWOOT_01` | `extractor_git_commit` | `/x-benchmark-metadata/extractor_git_commit` | OpenAPI 3.1.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_CHATWOOT_01-0366` | `SLOT_CHATWOOT_01` | `extractor_version` | `/x-benchmark-metadata/extractor_version` | OpenAPI 3.1.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_CHATWOOT_01-0367` | `SLOT_CHATWOOT_01` | `governing_specification` | `/x-benchmark-metadata/governing_specification` | OpenAPI 3.1.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_CHATWOOT_01-0368` | `SLOT_CHATWOOT_01` | `http_method` | `/x-benchmark-metadata/http_method` | OpenAPI 3.1.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_CHATWOOT_01-0369` | `SLOT_CHATWOOT_01` | `independent_validation_claimed` | `/x-benchmark-metadata/independent_validation_claimed` | OpenAPI 3.1.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_CHATWOOT_01-0370` | `SLOT_CHATWOOT_01` | `operation_id` | `/x-benchmark-metadata/operation_id` | OpenAPI 3.1.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_CHATWOOT_01-0371` | `SLOT_CHATWOOT_01` | `request_content_type` | `/x-benchmark-metadata/request_content_type` | OpenAPI 3.1.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_CHATWOOT_01-0372` | `SLOT_CHATWOOT_01` | `semantic_validation_decision` | `/x-benchmark-metadata/semantic_validation_decision` | OpenAPI 3.1.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_CHATWOOT_01-0373` | `SLOT_CHATWOOT_01` | `serialization_metadata` | `/x-benchmark-metadata/serialization_metadata` | OpenAPI 3.1.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_CHATWOOT_01-0374` | `SLOT_CHATWOOT_01` | `slot_id` | `/x-benchmark-metadata/slot_id` | OpenAPI 3.1.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_CHATWOOT_01-0375` | `SLOT_CHATWOOT_01` | `source_cluster_id` | `/x-benchmark-metadata/source_cluster_id` | OpenAPI 3.1.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_CHATWOOT_01-0376` | `SLOT_CHATWOOT_01` | `source_file_blob_sha` | `/x-benchmark-metadata/source_file_blob_sha` | OpenAPI 3.1.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_CHATWOOT_01-0377` | `SLOT_CHATWOOT_01` | `source_file_sha256` | `/x-benchmark-metadata/source_file_sha256` | OpenAPI 3.1.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_CHATWOOT_01-0378` | `SLOT_CHATWOOT_01` | `source_spec_pointer` | `/x-benchmark-metadata/source_spec_pointer` | OpenAPI 3.1.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_CHATWOOT_01-0379` | `SLOT_CHATWOOT_01` | `source_structural_metrics` | `/x-benchmark-metadata/source_structural_metrics` | OpenAPI 3.1.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_CHATWOOT_01-0380` | `SLOT_CHATWOOT_01` | `status` | `/x-benchmark-metadata/status` | OpenAPI 3.1.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_CHATWOOT_01-0381` | `SLOT_CHATWOOT_01` | `target_domain` | `/x-benchmark-metadata/target_domain` | OpenAPI 3.1.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_CHATWOOT_01-0382` | `SLOT_CHATWOOT_01` | `wrapped_contract_structural_metrics` | `/x-benchmark-metadata/wrapped_contract_structural_metrics` | OpenAPI 3.1.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_CHATWOOT_01-0383` | `SLOT_CHATWOOT_01` | `wrapper_normalization_policy` | `/x-benchmark-metadata/wrapper_normalization_policy` | OpenAPI 3.1.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_CHATWOOT_01-0384` | `SLOT_CHATWOOT_01` | `content_type` | `/x-benchmark-metadata/serialization_metadata/content_type` | OpenAPI 3.1.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_CHATWOOT_01-0385` | `SLOT_CHATWOOT_01` | `encoding` | `/x-benchmark-metadata/serialization_metadata/encoding` | OpenAPI 3.1.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_CHATWOOT_01-0386` | `SLOT_CHATWOOT_01` | `encoding_metadata_present` | `/x-benchmark-metadata/serialization_metadata/encoding_metadata_present` | OpenAPI 3.1.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_CHATWOOT_01-0387` | `SLOT_CHATWOOT_01` | `serialization_strategy` | `/x-benchmark-metadata/serialization_metadata/serialization_strategy` | OpenAPI 3.1.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_CHATWOOT_01-0388` | `SLOT_CHATWOOT_01` | `raw_nesting_depth` | `/x-benchmark-metadata/source_structural_metrics/raw_nesting_depth` | OpenAPI 3.1.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_CHATWOOT_01-0389` | `SLOT_CHATWOOT_01` | `raw_parameter_count` | `/x-benchmark-metadata/source_structural_metrics/raw_parameter_count` | OpenAPI 3.1.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_CHATWOOT_01-0390` | `SLOT_CHATWOOT_01` | `surface_containers_present` | `/x-benchmark-metadata/wrapped_contract_structural_metrics/surface_containers_present` | OpenAPI 3.1.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_CHATWOOT_01-0391` | `SLOT_CHATWOOT_01` | `surface_containers_required` | `/x-benchmark-metadata/wrapped_contract_structural_metrics/surface_containers_required` | OpenAPI 3.1.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_CHATWOOT_01-0392` | `SLOT_CHATWOOT_01` | `total_property_count` | `/x-benchmark-metadata/wrapped_contract_structural_metrics/total_property_count` | OpenAPI 3.1.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_CHATWOOT_01-0393` | `SLOT_CHATWOOT_01` | `wrapped_nesting_depth` | `/x-benchmark-metadata/wrapped_contract_structural_metrics/wrapped_nesting_depth` | OpenAPI 3.1.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_CHATWOOT_01-0394` | `SLOT_CHATWOOT_01` | `additional_properties_closed` | `/x-benchmark-metadata/wrapper_normalization_policy/additional_properties_closed` | OpenAPI 3.1.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_CHATWOOT_01-0395` | `SLOT_CHATWOOT_01` | `is_strictly_lossless` | `/x-benchmark-metadata/wrapper_normalization_policy/is_strictly_lossless` | OpenAPI 3.1.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_CHATWOOT_01-0396` | `SLOT_CHATWOOT_01` | `policy_id` | `/x-benchmark-metadata/wrapper_normalization_policy/policy_id` | OpenAPI 3.1.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_CHATWOOT_01-0397` | `SLOT_CHATWOOT_01` | `rationale` | `/x-benchmark-metadata/wrapper_normalization_policy/rationale` | OpenAPI 3.1.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_02-0398` | `SLOT_GITHUB_02` | `body` | `/properties/body` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_02-0399` | `SLOT_GITHUB_02` | `header` | `/properties/header` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_02-0400` | `SLOT_GITHUB_02` | `path` | `/properties/path` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_02-0401` | `SLOT_GITHUB_02` | `query` | `/properties/query` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_02-0402` | `SLOT_GITHUB_02` | `context` | `/properties/body/properties/context` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_02-0403` | `SLOT_GITHUB_02` | `state` | `/properties/body/properties/state` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_02-0404` | `SLOT_GITHUB_02` | `target_url` | `/properties/body/properties/target_url` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_02-0405` | `SLOT_GITHUB_02` | `nullable` | `/properties/body/properties/description/nullable` | OpenAPI 3.0.3 | `HIGH_SEMANTIC_DIVERGENCE` | **NO** | `CONVERT_TO_DRAFT07_TYPE_UNION` |
| `DIALECT-SLOT_GITHUB_02-0406` | `SLOT_GITHUB_02` | `nullable` | `/properties/body/properties/target_url/nullable` | OpenAPI 3.0.3 | `HIGH_SEMANTIC_DIVERGENCE` | **NO** | `CONVERT_TO_DRAFT07_TYPE_UNION` |
| `DIALECT-SLOT_GITHUB_02-0407` | `SLOT_GITHUB_02` | `owner` | `/properties/path/properties/owner` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_02-0408` | `SLOT_GITHUB_02` | `repo` | `/properties/path/properties/repo` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_02-0409` | `SLOT_GITHUB_02` | `sha` | `/properties/path/properties/sha` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_02-0410` | `SLOT_GITHUB_02` | `admission_decision` | `/x-benchmark-metadata/admission_decision` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_02-0411` | `SLOT_GITHUB_02` | `candidate_source_id` | `/x-benchmark-metadata/candidate_source_id` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_02-0412` | `SLOT_GITHUB_02` | `creation_mode` | `/x-benchmark-metadata/creation_mode` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_02-0413` | `SLOT_GITHUB_02` | `endpoint` | `/x-benchmark-metadata/endpoint` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_02-0414` | `SLOT_GITHUB_02` | `extraction_rule_version` | `/x-benchmark-metadata/extraction_rule_version` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_02-0415` | `SLOT_GITHUB_02` | `extraction_timestamp` | `/x-benchmark-metadata/extraction_timestamp` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_02-0416` | `SLOT_GITHUB_02` | `extractor_git_commit` | `/x-benchmark-metadata/extractor_git_commit` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_02-0417` | `SLOT_GITHUB_02` | `extractor_version` | `/x-benchmark-metadata/extractor_version` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_02-0418` | `SLOT_GITHUB_02` | `governing_specification` | `/x-benchmark-metadata/governing_specification` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_02-0419` | `SLOT_GITHUB_02` | `http_method` | `/x-benchmark-metadata/http_method` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_02-0420` | `SLOT_GITHUB_02` | `independent_validation_claimed` | `/x-benchmark-metadata/independent_validation_claimed` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_02-0421` | `SLOT_GITHUB_02` | `operation_id` | `/x-benchmark-metadata/operation_id` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_02-0422` | `SLOT_GITHUB_02` | `request_content_type` | `/x-benchmark-metadata/request_content_type` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_02-0423` | `SLOT_GITHUB_02` | `semantic_validation_decision` | `/x-benchmark-metadata/semantic_validation_decision` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_02-0424` | `SLOT_GITHUB_02` | `serialization_metadata` | `/x-benchmark-metadata/serialization_metadata` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_02-0425` | `SLOT_GITHUB_02` | `slot_id` | `/x-benchmark-metadata/slot_id` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_02-0426` | `SLOT_GITHUB_02` | `source_cluster_id` | `/x-benchmark-metadata/source_cluster_id` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_02-0427` | `SLOT_GITHUB_02` | `source_file_blob_sha` | `/x-benchmark-metadata/source_file_blob_sha` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_02-0428` | `SLOT_GITHUB_02` | `source_file_sha256` | `/x-benchmark-metadata/source_file_sha256` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_02-0429` | `SLOT_GITHUB_02` | `source_spec_pointer` | `/x-benchmark-metadata/source_spec_pointer` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_02-0430` | `SLOT_GITHUB_02` | `source_structural_metrics` | `/x-benchmark-metadata/source_structural_metrics` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_02-0431` | `SLOT_GITHUB_02` | `status` | `/x-benchmark-metadata/status` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_02-0432` | `SLOT_GITHUB_02` | `target_domain` | `/x-benchmark-metadata/target_domain` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_02-0433` | `SLOT_GITHUB_02` | `wrapped_contract_structural_metrics` | `/x-benchmark-metadata/wrapped_contract_structural_metrics` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_02-0434` | `SLOT_GITHUB_02` | `wrapper_normalization_policy` | `/x-benchmark-metadata/wrapper_normalization_policy` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_02-0435` | `SLOT_GITHUB_02` | `content_type` | `/x-benchmark-metadata/serialization_metadata/content_type` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_02-0436` | `SLOT_GITHUB_02` | `encoding` | `/x-benchmark-metadata/serialization_metadata/encoding` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_02-0437` | `SLOT_GITHUB_02` | `encoding_metadata_present` | `/x-benchmark-metadata/serialization_metadata/encoding_metadata_present` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_02-0438` | `SLOT_GITHUB_02` | `serialization_strategy` | `/x-benchmark-metadata/serialization_metadata/serialization_strategy` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_02-0439` | `SLOT_GITHUB_02` | `raw_nesting_depth` | `/x-benchmark-metadata/source_structural_metrics/raw_nesting_depth` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_02-0440` | `SLOT_GITHUB_02` | `raw_parameter_count` | `/x-benchmark-metadata/source_structural_metrics/raw_parameter_count` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_02-0441` | `SLOT_GITHUB_02` | `surface_containers_present` | `/x-benchmark-metadata/wrapped_contract_structural_metrics/surface_containers_present` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_02-0442` | `SLOT_GITHUB_02` | `surface_containers_required` | `/x-benchmark-metadata/wrapped_contract_structural_metrics/surface_containers_required` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_02-0443` | `SLOT_GITHUB_02` | `total_property_count` | `/x-benchmark-metadata/wrapped_contract_structural_metrics/total_property_count` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_02-0444` | `SLOT_GITHUB_02` | `wrapped_nesting_depth` | `/x-benchmark-metadata/wrapped_contract_structural_metrics/wrapped_nesting_depth` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_02-0445` | `SLOT_GITHUB_02` | `additional_properties_closed` | `/x-benchmark-metadata/wrapper_normalization_policy/additional_properties_closed` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_02-0446` | `SLOT_GITHUB_02` | `is_strictly_lossless` | `/x-benchmark-metadata/wrapper_normalization_policy/is_strictly_lossless` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_02-0447` | `SLOT_GITHUB_02` | `policy_id` | `/x-benchmark-metadata/wrapper_normalization_policy/policy_id` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_02-0448` | `SLOT_GITHUB_02` | `rationale` | `/x-benchmark-metadata/wrapper_normalization_policy/rationale` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_03-0449` | `SLOT_GITHUB_03` | `body` | `/properties/body` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_03-0450` | `SLOT_GITHUB_03` | `header` | `/properties/header` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_03-0451` | `SLOT_GITHUB_03` | `path` | `/properties/path` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_03-0452` | `SLOT_GITHUB_03` | `query` | `/properties/query` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_03-0453` | `SLOT_GITHUB_03` | `allow_auto_merge` | `/properties/body/properties/allow_auto_merge` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_03-0454` | `SLOT_GITHUB_03` | `allow_merge_commit` | `/properties/body/properties/allow_merge_commit` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_03-0455` | `SLOT_GITHUB_03` | `allow_rebase_merge` | `/properties/body/properties/allow_rebase_merge` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_03-0456` | `SLOT_GITHUB_03` | `allow_squash_merge` | `/properties/body/properties/allow_squash_merge` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_03-0457` | `SLOT_GITHUB_03` | `auto_init` | `/properties/body/properties/auto_init` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_03-0458` | `SLOT_GITHUB_03` | `delete_branch_on_merge` | `/properties/body/properties/delete_branch_on_merge` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_03-0459` | `SLOT_GITHUB_03` | `gitignore_template` | `/properties/body/properties/gitignore_template` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_03-0460` | `SLOT_GITHUB_03` | `has_discussions` | `/properties/body/properties/has_discussions` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_03-0461` | `SLOT_GITHUB_03` | `has_downloads` | `/properties/body/properties/has_downloads` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_03-0462` | `SLOT_GITHUB_03` | `has_issues` | `/properties/body/properties/has_issues` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_03-0463` | `SLOT_GITHUB_03` | `has_projects` | `/properties/body/properties/has_projects` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_03-0464` | `SLOT_GITHUB_03` | `has_wiki` | `/properties/body/properties/has_wiki` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_03-0465` | `SLOT_GITHUB_03` | `homepage` | `/properties/body/properties/homepage` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_03-0466` | `SLOT_GITHUB_03` | `is_template` | `/properties/body/properties/is_template` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_03-0467` | `SLOT_GITHUB_03` | `license_template` | `/properties/body/properties/license_template` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_03-0468` | `SLOT_GITHUB_03` | `merge_commit_message` | `/properties/body/properties/merge_commit_message` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_03-0469` | `SLOT_GITHUB_03` | `merge_commit_title` | `/properties/body/properties/merge_commit_title` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_03-0470` | `SLOT_GITHUB_03` | `name` | `/properties/body/properties/name` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_03-0471` | `SLOT_GITHUB_03` | `private` | `/properties/body/properties/private` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_03-0472` | `SLOT_GITHUB_03` | `squash_merge_commit_message` | `/properties/body/properties/squash_merge_commit_message` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_03-0473` | `SLOT_GITHUB_03` | `squash_merge_commit_title` | `/properties/body/properties/squash_merge_commit_title` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_03-0474` | `SLOT_GITHUB_03` | `team_id` | `/properties/body/properties/team_id` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_03-0475` | `SLOT_GITHUB_03` | `example` | `/properties/body/properties/allow_auto_merge/example` | OpenAPI 3.0.3 | `LOW_ANNOTATION` | YES | `DOCUMENT_ANNOTATION_DIFFERENCE` |
| `DIALECT-SLOT_GITHUB_03-0476` | `SLOT_GITHUB_03` | `example` | `/properties/body/properties/allow_merge_commit/example` | OpenAPI 3.0.3 | `LOW_ANNOTATION` | YES | `DOCUMENT_ANNOTATION_DIFFERENCE` |
| `DIALECT-SLOT_GITHUB_03-0477` | `SLOT_GITHUB_03` | `example` | `/properties/body/properties/allow_rebase_merge/example` | OpenAPI 3.0.3 | `LOW_ANNOTATION` | YES | `DOCUMENT_ANNOTATION_DIFFERENCE` |
| `DIALECT-SLOT_GITHUB_03-0478` | `SLOT_GITHUB_03` | `example` | `/properties/body/properties/allow_squash_merge/example` | OpenAPI 3.0.3 | `LOW_ANNOTATION` | YES | `DOCUMENT_ANNOTATION_DIFFERENCE` |
| `DIALECT-SLOT_GITHUB_03-0479` | `SLOT_GITHUB_03` | `example` | `/properties/body/properties/delete_branch_on_merge/example` | OpenAPI 3.0.3 | `LOW_ANNOTATION` | YES | `DOCUMENT_ANNOTATION_DIFFERENCE` |
| `DIALECT-SLOT_GITHUB_03-0480` | `SLOT_GITHUB_03` | `example` | `/properties/body/properties/gitignore_template/example` | OpenAPI 3.0.3 | `LOW_ANNOTATION` | YES | `DOCUMENT_ANNOTATION_DIFFERENCE` |
| `DIALECT-SLOT_GITHUB_03-0481` | `SLOT_GITHUB_03` | `example` | `/properties/body/properties/has_discussions/example` | OpenAPI 3.0.3 | `LOW_ANNOTATION` | YES | `DOCUMENT_ANNOTATION_DIFFERENCE` |
| `DIALECT-SLOT_GITHUB_03-0482` | `SLOT_GITHUB_03` | `example` | `/properties/body/properties/has_downloads/example` | OpenAPI 3.0.3 | `LOW_ANNOTATION` | YES | `DOCUMENT_ANNOTATION_DIFFERENCE` |
| `DIALECT-SLOT_GITHUB_03-0483` | `SLOT_GITHUB_03` | `example` | `/properties/body/properties/has_issues/example` | OpenAPI 3.0.3 | `LOW_ANNOTATION` | YES | `DOCUMENT_ANNOTATION_DIFFERENCE` |
| `DIALECT-SLOT_GITHUB_03-0484` | `SLOT_GITHUB_03` | `example` | `/properties/body/properties/has_projects/example` | OpenAPI 3.0.3 | `LOW_ANNOTATION` | YES | `DOCUMENT_ANNOTATION_DIFFERENCE` |
| `DIALECT-SLOT_GITHUB_03-0485` | `SLOT_GITHUB_03` | `example` | `/properties/body/properties/has_wiki/example` | OpenAPI 3.0.3 | `LOW_ANNOTATION` | YES | `DOCUMENT_ANNOTATION_DIFFERENCE` |
| `DIALECT-SLOT_GITHUB_03-0486` | `SLOT_GITHUB_03` | `example` | `/properties/body/properties/is_template/example` | OpenAPI 3.0.3 | `LOW_ANNOTATION` | YES | `DOCUMENT_ANNOTATION_DIFFERENCE` |
| `DIALECT-SLOT_GITHUB_03-0487` | `SLOT_GITHUB_03` | `example` | `/properties/body/properties/license_template/example` | OpenAPI 3.0.3 | `LOW_ANNOTATION` | YES | `DOCUMENT_ANNOTATION_DIFFERENCE` |
| `DIALECT-SLOT_GITHUB_03-0488` | `SLOT_GITHUB_03` | `example` | `/properties/body/properties/name/example` | OpenAPI 3.0.3 | `LOW_ANNOTATION` | YES | `DOCUMENT_ANNOTATION_DIFFERENCE` |
| `DIALECT-SLOT_GITHUB_03-0489` | `SLOT_GITHUB_03` | `admission_decision` | `/x-benchmark-metadata/admission_decision` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_03-0490` | `SLOT_GITHUB_03` | `candidate_source_id` | `/x-benchmark-metadata/candidate_source_id` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_03-0491` | `SLOT_GITHUB_03` | `creation_mode` | `/x-benchmark-metadata/creation_mode` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_03-0492` | `SLOT_GITHUB_03` | `endpoint` | `/x-benchmark-metadata/endpoint` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_03-0493` | `SLOT_GITHUB_03` | `extraction_rule_version` | `/x-benchmark-metadata/extraction_rule_version` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_03-0494` | `SLOT_GITHUB_03` | `extraction_timestamp` | `/x-benchmark-metadata/extraction_timestamp` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_03-0495` | `SLOT_GITHUB_03` | `extractor_git_commit` | `/x-benchmark-metadata/extractor_git_commit` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_03-0496` | `SLOT_GITHUB_03` | `extractor_version` | `/x-benchmark-metadata/extractor_version` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_03-0497` | `SLOT_GITHUB_03` | `governing_specification` | `/x-benchmark-metadata/governing_specification` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_03-0498` | `SLOT_GITHUB_03` | `http_method` | `/x-benchmark-metadata/http_method` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_03-0499` | `SLOT_GITHUB_03` | `independent_validation_claimed` | `/x-benchmark-metadata/independent_validation_claimed` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_03-0500` | `SLOT_GITHUB_03` | `operation_id` | `/x-benchmark-metadata/operation_id` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_03-0501` | `SLOT_GITHUB_03` | `request_content_type` | `/x-benchmark-metadata/request_content_type` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_03-0502` | `SLOT_GITHUB_03` | `semantic_validation_decision` | `/x-benchmark-metadata/semantic_validation_decision` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_03-0503` | `SLOT_GITHUB_03` | `serialization_metadata` | `/x-benchmark-metadata/serialization_metadata` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_03-0504` | `SLOT_GITHUB_03` | `slot_id` | `/x-benchmark-metadata/slot_id` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_03-0505` | `SLOT_GITHUB_03` | `source_cluster_id` | `/x-benchmark-metadata/source_cluster_id` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_03-0506` | `SLOT_GITHUB_03` | `source_file_blob_sha` | `/x-benchmark-metadata/source_file_blob_sha` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_03-0507` | `SLOT_GITHUB_03` | `source_file_sha256` | `/x-benchmark-metadata/source_file_sha256` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_03-0508` | `SLOT_GITHUB_03` | `source_spec_pointer` | `/x-benchmark-metadata/source_spec_pointer` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_03-0509` | `SLOT_GITHUB_03` | `source_structural_metrics` | `/x-benchmark-metadata/source_structural_metrics` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_03-0510` | `SLOT_GITHUB_03` | `status` | `/x-benchmark-metadata/status` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_03-0511` | `SLOT_GITHUB_03` | `target_domain` | `/x-benchmark-metadata/target_domain` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_03-0512` | `SLOT_GITHUB_03` | `wrapped_contract_structural_metrics` | `/x-benchmark-metadata/wrapped_contract_structural_metrics` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_03-0513` | `SLOT_GITHUB_03` | `wrapper_normalization_policy` | `/x-benchmark-metadata/wrapper_normalization_policy` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_03-0514` | `SLOT_GITHUB_03` | `content_type` | `/x-benchmark-metadata/serialization_metadata/content_type` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_03-0515` | `SLOT_GITHUB_03` | `encoding` | `/x-benchmark-metadata/serialization_metadata/encoding` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_03-0516` | `SLOT_GITHUB_03` | `encoding_metadata_present` | `/x-benchmark-metadata/serialization_metadata/encoding_metadata_present` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_03-0517` | `SLOT_GITHUB_03` | `serialization_strategy` | `/x-benchmark-metadata/serialization_metadata/serialization_strategy` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_03-0518` | `SLOT_GITHUB_03` | `raw_nesting_depth` | `/x-benchmark-metadata/source_structural_metrics/raw_nesting_depth` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_03-0519` | `SLOT_GITHUB_03` | `raw_parameter_count` | `/x-benchmark-metadata/source_structural_metrics/raw_parameter_count` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_03-0520` | `SLOT_GITHUB_03` | `surface_containers_present` | `/x-benchmark-metadata/wrapped_contract_structural_metrics/surface_containers_present` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_03-0521` | `SLOT_GITHUB_03` | `surface_containers_required` | `/x-benchmark-metadata/wrapped_contract_structural_metrics/surface_containers_required` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_03-0522` | `SLOT_GITHUB_03` | `total_property_count` | `/x-benchmark-metadata/wrapped_contract_structural_metrics/total_property_count` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_03-0523` | `SLOT_GITHUB_03` | `wrapped_nesting_depth` | `/x-benchmark-metadata/wrapped_contract_structural_metrics/wrapped_nesting_depth` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_03-0524` | `SLOT_GITHUB_03` | `additional_properties_closed` | `/x-benchmark-metadata/wrapper_normalization_policy/additional_properties_closed` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_03-0525` | `SLOT_GITHUB_03` | `is_strictly_lossless` | `/x-benchmark-metadata/wrapper_normalization_policy/is_strictly_lossless` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_03-0526` | `SLOT_GITHUB_03` | `policy_id` | `/x-benchmark-metadata/wrapper_normalization_policy/policy_id` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_GITHUB_03-0527` | `SLOT_GITHUB_03` | `rationale` | `/x-benchmark-metadata/wrapper_normalization_policy/rationale` | OpenAPI 3.0.3 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_01-0528` | `SLOT_LINE_01` | `body` | `/properties/body` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_01-0529` | `SLOT_LINE_01` | `header` | `/properties/header` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_01-0530` | `SLOT_LINE_01` | `path` | `/properties/path` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_01-0531` | `SLOT_LINE_01` | `query` | `/properties/query` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_01-0532` | `SLOT_LINE_01` | `chatId` | `/properties/body/properties/chatId` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_01-0533` | `SLOT_LINE_01` | `loadingSeconds` | `/properties/body/properties/loadingSeconds` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_01-0534` | `SLOT_LINE_01` | `format` | `/properties/body/properties/loadingSeconds/format` | OpenAPI 3.0.0 | `LOW_ANNOTATION` | YES | `DOCUMENT_ANNOTATION_DIFFERENCE` |
| `DIALECT-SLOT_LINE_01-0535` | `SLOT_LINE_01` | `admission_decision` | `/x-benchmark-metadata/admission_decision` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_01-0536` | `SLOT_LINE_01` | `candidate_source_id` | `/x-benchmark-metadata/candidate_source_id` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_01-0537` | `SLOT_LINE_01` | `creation_mode` | `/x-benchmark-metadata/creation_mode` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_01-0538` | `SLOT_LINE_01` | `endpoint` | `/x-benchmark-metadata/endpoint` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_01-0539` | `SLOT_LINE_01` | `extraction_rule_version` | `/x-benchmark-metadata/extraction_rule_version` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_01-0540` | `SLOT_LINE_01` | `extraction_timestamp` | `/x-benchmark-metadata/extraction_timestamp` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_01-0541` | `SLOT_LINE_01` | `extractor_git_commit` | `/x-benchmark-metadata/extractor_git_commit` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_01-0542` | `SLOT_LINE_01` | `extractor_version` | `/x-benchmark-metadata/extractor_version` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_01-0543` | `SLOT_LINE_01` | `governing_specification` | `/x-benchmark-metadata/governing_specification` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_01-0544` | `SLOT_LINE_01` | `http_method` | `/x-benchmark-metadata/http_method` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_01-0545` | `SLOT_LINE_01` | `independent_validation_claimed` | `/x-benchmark-metadata/independent_validation_claimed` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_01-0546` | `SLOT_LINE_01` | `operation_id` | `/x-benchmark-metadata/operation_id` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_01-0547` | `SLOT_LINE_01` | `request_content_type` | `/x-benchmark-metadata/request_content_type` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_01-0548` | `SLOT_LINE_01` | `semantic_validation_decision` | `/x-benchmark-metadata/semantic_validation_decision` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_01-0549` | `SLOT_LINE_01` | `serialization_metadata` | `/x-benchmark-metadata/serialization_metadata` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_01-0550` | `SLOT_LINE_01` | `slot_id` | `/x-benchmark-metadata/slot_id` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_01-0551` | `SLOT_LINE_01` | `source_cluster_id` | `/x-benchmark-metadata/source_cluster_id` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_01-0552` | `SLOT_LINE_01` | `source_file_blob_sha` | `/x-benchmark-metadata/source_file_blob_sha` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_01-0553` | `SLOT_LINE_01` | `source_file_sha256` | `/x-benchmark-metadata/source_file_sha256` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_01-0554` | `SLOT_LINE_01` | `source_spec_pointer` | `/x-benchmark-metadata/source_spec_pointer` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_01-0555` | `SLOT_LINE_01` | `source_structural_metrics` | `/x-benchmark-metadata/source_structural_metrics` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_01-0556` | `SLOT_LINE_01` | `status` | `/x-benchmark-metadata/status` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_01-0557` | `SLOT_LINE_01` | `target_domain` | `/x-benchmark-metadata/target_domain` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_01-0558` | `SLOT_LINE_01` | `wrapped_contract_structural_metrics` | `/x-benchmark-metadata/wrapped_contract_structural_metrics` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_01-0559` | `SLOT_LINE_01` | `wrapper_normalization_policy` | `/x-benchmark-metadata/wrapper_normalization_policy` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_01-0560` | `SLOT_LINE_01` | `content_type` | `/x-benchmark-metadata/serialization_metadata/content_type` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_01-0561` | `SLOT_LINE_01` | `encoding` | `/x-benchmark-metadata/serialization_metadata/encoding` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_01-0562` | `SLOT_LINE_01` | `encoding_metadata_present` | `/x-benchmark-metadata/serialization_metadata/encoding_metadata_present` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_01-0563` | `SLOT_LINE_01` | `serialization_strategy` | `/x-benchmark-metadata/serialization_metadata/serialization_strategy` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_01-0564` | `SLOT_LINE_01` | `raw_nesting_depth` | `/x-benchmark-metadata/source_structural_metrics/raw_nesting_depth` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_01-0565` | `SLOT_LINE_01` | `raw_parameter_count` | `/x-benchmark-metadata/source_structural_metrics/raw_parameter_count` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_01-0566` | `SLOT_LINE_01` | `surface_containers_present` | `/x-benchmark-metadata/wrapped_contract_structural_metrics/surface_containers_present` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_01-0567` | `SLOT_LINE_01` | `surface_containers_required` | `/x-benchmark-metadata/wrapped_contract_structural_metrics/surface_containers_required` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_01-0568` | `SLOT_LINE_01` | `total_property_count` | `/x-benchmark-metadata/wrapped_contract_structural_metrics/total_property_count` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_01-0569` | `SLOT_LINE_01` | `wrapped_nesting_depth` | `/x-benchmark-metadata/wrapped_contract_structural_metrics/wrapped_nesting_depth` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_01-0570` | `SLOT_LINE_01` | `additional_properties_closed` | `/x-benchmark-metadata/wrapper_normalization_policy/additional_properties_closed` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_01-0571` | `SLOT_LINE_01` | `is_strictly_lossless` | `/x-benchmark-metadata/wrapper_normalization_policy/is_strictly_lossless` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_01-0572` | `SLOT_LINE_01` | `policy_id` | `/x-benchmark-metadata/wrapper_normalization_policy/policy_id` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_01-0573` | `SLOT_LINE_01` | `rationale` | `/x-benchmark-metadata/wrapper_normalization_policy/rationale` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_02-0574` | `SLOT_LINE_02` | `body` | `/properties/body` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_02-0575` | `SLOT_LINE_02` | `header` | `/properties/header` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_02-0576` | `SLOT_LINE_02` | `path` | `/properties/path` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_02-0577` | `SLOT_LINE_02` | `query` | `/properties/query` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_02-0578` | `SLOT_LINE_02` | `endpoint` | `/properties/body/properties/endpoint` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_02-0579` | `SLOT_LINE_02` | `admission_decision` | `/x-benchmark-metadata/admission_decision` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_02-0580` | `SLOT_LINE_02` | `candidate_source_id` | `/x-benchmark-metadata/candidate_source_id` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_02-0581` | `SLOT_LINE_02` | `creation_mode` | `/x-benchmark-metadata/creation_mode` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_02-0582` | `SLOT_LINE_02` | `endpoint` | `/x-benchmark-metadata/endpoint` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_02-0583` | `SLOT_LINE_02` | `extraction_rule_version` | `/x-benchmark-metadata/extraction_rule_version` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_02-0584` | `SLOT_LINE_02` | `extraction_timestamp` | `/x-benchmark-metadata/extraction_timestamp` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_02-0585` | `SLOT_LINE_02` | `extractor_git_commit` | `/x-benchmark-metadata/extractor_git_commit` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_02-0586` | `SLOT_LINE_02` | `extractor_version` | `/x-benchmark-metadata/extractor_version` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_02-0587` | `SLOT_LINE_02` | `governing_specification` | `/x-benchmark-metadata/governing_specification` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_02-0588` | `SLOT_LINE_02` | `http_method` | `/x-benchmark-metadata/http_method` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_02-0589` | `SLOT_LINE_02` | `independent_validation_claimed` | `/x-benchmark-metadata/independent_validation_claimed` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_02-0590` | `SLOT_LINE_02` | `operation_id` | `/x-benchmark-metadata/operation_id` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_02-0591` | `SLOT_LINE_02` | `request_content_type` | `/x-benchmark-metadata/request_content_type` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_02-0592` | `SLOT_LINE_02` | `semantic_validation_decision` | `/x-benchmark-metadata/semantic_validation_decision` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_02-0593` | `SLOT_LINE_02` | `serialization_metadata` | `/x-benchmark-metadata/serialization_metadata` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_02-0594` | `SLOT_LINE_02` | `slot_id` | `/x-benchmark-metadata/slot_id` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_02-0595` | `SLOT_LINE_02` | `source_cluster_id` | `/x-benchmark-metadata/source_cluster_id` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_02-0596` | `SLOT_LINE_02` | `source_file_blob_sha` | `/x-benchmark-metadata/source_file_blob_sha` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_02-0597` | `SLOT_LINE_02` | `source_file_sha256` | `/x-benchmark-metadata/source_file_sha256` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_02-0598` | `SLOT_LINE_02` | `source_spec_pointer` | `/x-benchmark-metadata/source_spec_pointer` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_02-0599` | `SLOT_LINE_02` | `source_structural_metrics` | `/x-benchmark-metadata/source_structural_metrics` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_02-0600` | `SLOT_LINE_02` | `status` | `/x-benchmark-metadata/status` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_02-0601` | `SLOT_LINE_02` | `target_domain` | `/x-benchmark-metadata/target_domain` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_02-0602` | `SLOT_LINE_02` | `wrapped_contract_structural_metrics` | `/x-benchmark-metadata/wrapped_contract_structural_metrics` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_02-0603` | `SLOT_LINE_02` | `wrapper_normalization_policy` | `/x-benchmark-metadata/wrapper_normalization_policy` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_02-0604` | `SLOT_LINE_02` | `content_type` | `/x-benchmark-metadata/serialization_metadata/content_type` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_02-0605` | `SLOT_LINE_02` | `encoding` | `/x-benchmark-metadata/serialization_metadata/encoding` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_02-0606` | `SLOT_LINE_02` | `encoding_metadata_present` | `/x-benchmark-metadata/serialization_metadata/encoding_metadata_present` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_02-0607` | `SLOT_LINE_02` | `serialization_strategy` | `/x-benchmark-metadata/serialization_metadata/serialization_strategy` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_02-0608` | `SLOT_LINE_02` | `raw_nesting_depth` | `/x-benchmark-metadata/source_structural_metrics/raw_nesting_depth` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_02-0609` | `SLOT_LINE_02` | `raw_parameter_count` | `/x-benchmark-metadata/source_structural_metrics/raw_parameter_count` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_02-0610` | `SLOT_LINE_02` | `surface_containers_present` | `/x-benchmark-metadata/wrapped_contract_structural_metrics/surface_containers_present` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_02-0611` | `SLOT_LINE_02` | `surface_containers_required` | `/x-benchmark-metadata/wrapped_contract_structural_metrics/surface_containers_required` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_02-0612` | `SLOT_LINE_02` | `total_property_count` | `/x-benchmark-metadata/wrapped_contract_structural_metrics/total_property_count` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_02-0613` | `SLOT_LINE_02` | `wrapped_nesting_depth` | `/x-benchmark-metadata/wrapped_contract_structural_metrics/wrapped_nesting_depth` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_02-0614` | `SLOT_LINE_02` | `additional_properties_closed` | `/x-benchmark-metadata/wrapper_normalization_policy/additional_properties_closed` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_02-0615` | `SLOT_LINE_02` | `is_strictly_lossless` | `/x-benchmark-metadata/wrapper_normalization_policy/is_strictly_lossless` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_02-0616` | `SLOT_LINE_02` | `policy_id` | `/x-benchmark-metadata/wrapper_normalization_policy/policy_id` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_02-0617` | `SLOT_LINE_02` | `rationale` | `/x-benchmark-metadata/wrapper_normalization_policy/rationale` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_03-0618` | `SLOT_LINE_03` | `body` | `/properties/body` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_03-0619` | `SLOT_LINE_03` | `header` | `/properties/header` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_03-0620` | `SLOT_LINE_03` | `path` | `/properties/path` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_03-0621` | `SLOT_LINE_03` | `query` | `/properties/query` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_03-0622` | `SLOT_LINE_03` | `chat` | `/properties/body/properties/chat` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_03-0623` | `SLOT_LINE_03` | `externalDocs` | `/properties/body/properties/chat/externalDocs` | OpenAPI 3.0.0 | `LOW_ANNOTATION` | YES | `DOCUMENT_ANNOTATION_DIFFERENCE` |
| `DIALECT-SLOT_LINE_03-0624` | `SLOT_LINE_03` | `url` | `/properties/body/properties/chat/externalDocs/url` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_03-0625` | `SLOT_LINE_03` | `userId` | `/properties/body/properties/chat/properties/userId` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_03-0626` | `SLOT_LINE_03` | `admission_decision` | `/x-benchmark-metadata/admission_decision` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_03-0627` | `SLOT_LINE_03` | `candidate_source_id` | `/x-benchmark-metadata/candidate_source_id` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_03-0628` | `SLOT_LINE_03` | `creation_mode` | `/x-benchmark-metadata/creation_mode` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_03-0629` | `SLOT_LINE_03` | `endpoint` | `/x-benchmark-metadata/endpoint` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_03-0630` | `SLOT_LINE_03` | `extraction_rule_version` | `/x-benchmark-metadata/extraction_rule_version` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_03-0631` | `SLOT_LINE_03` | `extraction_timestamp` | `/x-benchmark-metadata/extraction_timestamp` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_03-0632` | `SLOT_LINE_03` | `extractor_git_commit` | `/x-benchmark-metadata/extractor_git_commit` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_03-0633` | `SLOT_LINE_03` | `extractor_version` | `/x-benchmark-metadata/extractor_version` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_03-0634` | `SLOT_LINE_03` | `governing_specification` | `/x-benchmark-metadata/governing_specification` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_03-0635` | `SLOT_LINE_03` | `http_method` | `/x-benchmark-metadata/http_method` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_03-0636` | `SLOT_LINE_03` | `independent_validation_claimed` | `/x-benchmark-metadata/independent_validation_claimed` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_03-0637` | `SLOT_LINE_03` | `operation_id` | `/x-benchmark-metadata/operation_id` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_03-0638` | `SLOT_LINE_03` | `request_content_type` | `/x-benchmark-metadata/request_content_type` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_03-0639` | `SLOT_LINE_03` | `semantic_validation_decision` | `/x-benchmark-metadata/semantic_validation_decision` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_03-0640` | `SLOT_LINE_03` | `serialization_metadata` | `/x-benchmark-metadata/serialization_metadata` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_03-0641` | `SLOT_LINE_03` | `slot_id` | `/x-benchmark-metadata/slot_id` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_03-0642` | `SLOT_LINE_03` | `source_cluster_id` | `/x-benchmark-metadata/source_cluster_id` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_03-0643` | `SLOT_LINE_03` | `source_file_blob_sha` | `/x-benchmark-metadata/source_file_blob_sha` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_03-0644` | `SLOT_LINE_03` | `source_file_sha256` | `/x-benchmark-metadata/source_file_sha256` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_03-0645` | `SLOT_LINE_03` | `source_spec_pointer` | `/x-benchmark-metadata/source_spec_pointer` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_03-0646` | `SLOT_LINE_03` | `source_structural_metrics` | `/x-benchmark-metadata/source_structural_metrics` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_03-0647` | `SLOT_LINE_03` | `status` | `/x-benchmark-metadata/status` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_03-0648` | `SLOT_LINE_03` | `target_domain` | `/x-benchmark-metadata/target_domain` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_03-0649` | `SLOT_LINE_03` | `wrapped_contract_structural_metrics` | `/x-benchmark-metadata/wrapped_contract_structural_metrics` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_03-0650` | `SLOT_LINE_03` | `wrapper_normalization_policy` | `/x-benchmark-metadata/wrapper_normalization_policy` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_03-0651` | `SLOT_LINE_03` | `content_type` | `/x-benchmark-metadata/serialization_metadata/content_type` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_03-0652` | `SLOT_LINE_03` | `encoding` | `/x-benchmark-metadata/serialization_metadata/encoding` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_03-0653` | `SLOT_LINE_03` | `encoding_metadata_present` | `/x-benchmark-metadata/serialization_metadata/encoding_metadata_present` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_03-0654` | `SLOT_LINE_03` | `serialization_strategy` | `/x-benchmark-metadata/serialization_metadata/serialization_strategy` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_03-0655` | `SLOT_LINE_03` | `raw_nesting_depth` | `/x-benchmark-metadata/source_structural_metrics/raw_nesting_depth` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_03-0656` | `SLOT_LINE_03` | `raw_parameter_count` | `/x-benchmark-metadata/source_structural_metrics/raw_parameter_count` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_03-0657` | `SLOT_LINE_03` | `surface_containers_present` | `/x-benchmark-metadata/wrapped_contract_structural_metrics/surface_containers_present` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_03-0658` | `SLOT_LINE_03` | `surface_containers_required` | `/x-benchmark-metadata/wrapped_contract_structural_metrics/surface_containers_required` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_03-0659` | `SLOT_LINE_03` | `total_property_count` | `/x-benchmark-metadata/wrapped_contract_structural_metrics/total_property_count` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_03-0660` | `SLOT_LINE_03` | `wrapped_nesting_depth` | `/x-benchmark-metadata/wrapped_contract_structural_metrics/wrapped_nesting_depth` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_03-0661` | `SLOT_LINE_03` | `additional_properties_closed` | `/x-benchmark-metadata/wrapper_normalization_policy/additional_properties_closed` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_03-0662` | `SLOT_LINE_03` | `is_strictly_lossless` | `/x-benchmark-metadata/wrapper_normalization_policy/is_strictly_lossless` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_03-0663` | `SLOT_LINE_03` | `policy_id` | `/x-benchmark-metadata/wrapper_normalization_policy/policy_id` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_LINE_03-0664` | `SLOT_LINE_03` | `rationale` | `/x-benchmark-metadata/wrapper_normalization_policy/rationale` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_01-0665` | `SLOT_STRIPE_01` | `body` | `/properties/body` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_01-0666` | `SLOT_STRIPE_01` | `header` | `/properties/header` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_01-0667` | `SLOT_STRIPE_01` | `path` | `/properties/path` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_01-0668` | `SLOT_STRIPE_01` | `query` | `/properties/query` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_01-0669` | `SLOT_STRIPE_01` | `x-openapi-encoding` | `/properties/body/x-openapi-encoding` | OpenAPI 3.0.0 | `MEDIUM_TRANSPORT_METADATA` | YES | `DOCUMENT_REPRESENTATION_NORMALIZATION` |
| `DIALECT-SLOT_STRIPE_01-0670` | `SLOT_STRIPE_01` | `amount` | `/properties/body/properties/amount` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_01-0671` | `SLOT_STRIPE_01` | `currency` | `/properties/body/properties/currency` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_01-0672` | `SLOT_STRIPE_01` | `destination` | `/properties/body/properties/destination` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_01-0673` | `SLOT_STRIPE_01` | `expand` | `/properties/body/properties/expand` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_01-0674` | `SLOT_STRIPE_01` | `metadata` | `/properties/body/properties/metadata` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_01-0675` | `SLOT_STRIPE_01` | `method` | `/properties/body/properties/method` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_01-0676` | `SLOT_STRIPE_01` | `payout_method` | `/properties/body/properties/payout_method` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_01-0677` | `SLOT_STRIPE_01` | `source_type` | `/properties/body/properties/source_type` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_01-0678` | `SLOT_STRIPE_01` | `statement_descriptor` | `/properties/body/properties/statement_descriptor` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_01-0679` | `SLOT_STRIPE_01` | `expand` | `/properties/body/x-openapi-encoding/expand` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_01-0680` | `SLOT_STRIPE_01` | `metadata` | `/properties/body/x-openapi-encoding/metadata` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_01-0681` | `SLOT_STRIPE_01` | `explode` | `/properties/body/x-openapi-encoding/expand/explode` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_01-0682` | `SLOT_STRIPE_01` | `style` | `/properties/body/x-openapi-encoding/expand/style` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_01-0683` | `SLOT_STRIPE_01` | `explode` | `/properties/body/x-openapi-encoding/metadata/explode` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_01-0684` | `SLOT_STRIPE_01` | `style` | `/properties/body/x-openapi-encoding/metadata/style` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_01-0685` | `SLOT_STRIPE_01` | `admission_decision` | `/x-benchmark-metadata/admission_decision` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_01-0686` | `SLOT_STRIPE_01` | `candidate_source_id` | `/x-benchmark-metadata/candidate_source_id` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_01-0687` | `SLOT_STRIPE_01` | `creation_mode` | `/x-benchmark-metadata/creation_mode` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_01-0688` | `SLOT_STRIPE_01` | `endpoint` | `/x-benchmark-metadata/endpoint` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_01-0689` | `SLOT_STRIPE_01` | `extraction_rule_version` | `/x-benchmark-metadata/extraction_rule_version` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_01-0690` | `SLOT_STRIPE_01` | `extraction_timestamp` | `/x-benchmark-metadata/extraction_timestamp` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_01-0691` | `SLOT_STRIPE_01` | `extractor_git_commit` | `/x-benchmark-metadata/extractor_git_commit` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_01-0692` | `SLOT_STRIPE_01` | `extractor_version` | `/x-benchmark-metadata/extractor_version` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_01-0693` | `SLOT_STRIPE_01` | `governing_specification` | `/x-benchmark-metadata/governing_specification` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_01-0694` | `SLOT_STRIPE_01` | `http_method` | `/x-benchmark-metadata/http_method` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_01-0695` | `SLOT_STRIPE_01` | `independent_validation_claimed` | `/x-benchmark-metadata/independent_validation_claimed` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_01-0696` | `SLOT_STRIPE_01` | `operation_id` | `/x-benchmark-metadata/operation_id` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_01-0697` | `SLOT_STRIPE_01` | `request_content_type` | `/x-benchmark-metadata/request_content_type` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_01-0698` | `SLOT_STRIPE_01` | `semantic_validation_decision` | `/x-benchmark-metadata/semantic_validation_decision` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_01-0699` | `SLOT_STRIPE_01` | `serialization_metadata` | `/x-benchmark-metadata/serialization_metadata` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_01-0700` | `SLOT_STRIPE_01` | `slot_id` | `/x-benchmark-metadata/slot_id` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_01-0701` | `SLOT_STRIPE_01` | `source_cluster_id` | `/x-benchmark-metadata/source_cluster_id` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_01-0702` | `SLOT_STRIPE_01` | `source_file_blob_sha` | `/x-benchmark-metadata/source_file_blob_sha` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_01-0703` | `SLOT_STRIPE_01` | `source_file_sha256` | `/x-benchmark-metadata/source_file_sha256` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_01-0704` | `SLOT_STRIPE_01` | `source_spec_pointer` | `/x-benchmark-metadata/source_spec_pointer` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_01-0705` | `SLOT_STRIPE_01` | `source_structural_metrics` | `/x-benchmark-metadata/source_structural_metrics` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_01-0706` | `SLOT_STRIPE_01` | `status` | `/x-benchmark-metadata/status` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_01-0707` | `SLOT_STRIPE_01` | `target_domain` | `/x-benchmark-metadata/target_domain` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_01-0708` | `SLOT_STRIPE_01` | `wrapped_contract_structural_metrics` | `/x-benchmark-metadata/wrapped_contract_structural_metrics` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_01-0709` | `SLOT_STRIPE_01` | `wrapper_normalization_policy` | `/x-benchmark-metadata/wrapper_normalization_policy` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_01-0710` | `SLOT_STRIPE_01` | `content_type` | `/x-benchmark-metadata/serialization_metadata/content_type` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_01-0711` | `SLOT_STRIPE_01` | `encoding` | `/x-benchmark-metadata/serialization_metadata/encoding` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_01-0712` | `SLOT_STRIPE_01` | `encoding_metadata_present` | `/x-benchmark-metadata/serialization_metadata/encoding_metadata_present` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_01-0713` | `SLOT_STRIPE_01` | `serialization_strategy` | `/x-benchmark-metadata/serialization_metadata/serialization_strategy` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_01-0714` | `SLOT_STRIPE_01` | `expand` | `/x-benchmark-metadata/serialization_metadata/encoding/expand` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_01-0715` | `SLOT_STRIPE_01` | `metadata` | `/x-benchmark-metadata/serialization_metadata/encoding/metadata` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_01-0716` | `SLOT_STRIPE_01` | `explode` | `/x-benchmark-metadata/serialization_metadata/encoding/expand/explode` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_01-0717` | `SLOT_STRIPE_01` | `style` | `/x-benchmark-metadata/serialization_metadata/encoding/expand/style` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_01-0718` | `SLOT_STRIPE_01` | `explode` | `/x-benchmark-metadata/serialization_metadata/encoding/metadata/explode` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_01-0719` | `SLOT_STRIPE_01` | `style` | `/x-benchmark-metadata/serialization_metadata/encoding/metadata/style` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_01-0720` | `SLOT_STRIPE_01` | `raw_nesting_depth` | `/x-benchmark-metadata/source_structural_metrics/raw_nesting_depth` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_01-0721` | `SLOT_STRIPE_01` | `raw_parameter_count` | `/x-benchmark-metadata/source_structural_metrics/raw_parameter_count` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_01-0722` | `SLOT_STRIPE_01` | `surface_containers_present` | `/x-benchmark-metadata/wrapped_contract_structural_metrics/surface_containers_present` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_01-0723` | `SLOT_STRIPE_01` | `surface_containers_required` | `/x-benchmark-metadata/wrapped_contract_structural_metrics/surface_containers_required` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_01-0724` | `SLOT_STRIPE_01` | `total_property_count` | `/x-benchmark-metadata/wrapped_contract_structural_metrics/total_property_count` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_01-0725` | `SLOT_STRIPE_01` | `wrapped_nesting_depth` | `/x-benchmark-metadata/wrapped_contract_structural_metrics/wrapped_nesting_depth` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_01-0726` | `SLOT_STRIPE_01` | `additional_properties_closed` | `/x-benchmark-metadata/wrapper_normalization_policy/additional_properties_closed` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_01-0727` | `SLOT_STRIPE_01` | `is_strictly_lossless` | `/x-benchmark-metadata/wrapper_normalization_policy/is_strictly_lossless` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_01-0728` | `SLOT_STRIPE_01` | `policy_id` | `/x-benchmark-metadata/wrapper_normalization_policy/policy_id` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_STRIPE_01-0729` | `SLOT_STRIPE_01` | `rationale` | `/x-benchmark-metadata/wrapper_normalization_policy/rationale` | OpenAPI 3.0.0 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_01-0730` | `SLOT_TWILIO_01` | `body` | `/properties/body` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_01-0731` | `SLOT_TWILIO_01` | `header` | `/properties/header` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_01-0732` | `SLOT_TWILIO_01` | `path` | `/properties/path` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_01-0733` | `SLOT_TWILIO_01` | `query` | `/properties/query` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_01-0734` | `SLOT_TWILIO_01` | `FriendlyName` | `/properties/body/properties/FriendlyName` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_01-0735` | `SLOT_TWILIO_01` | `Status` | `/properties/body/properties/Status` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_01-0736` | `SLOT_TWILIO_01` | `Sid` | `/properties/path/properties/Sid` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_01-0737` | `SLOT_TWILIO_01` | `admission_decision` | `/x-benchmark-metadata/admission_decision` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_01-0738` | `SLOT_TWILIO_01` | `candidate_source_id` | `/x-benchmark-metadata/candidate_source_id` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_01-0739` | `SLOT_TWILIO_01` | `creation_mode` | `/x-benchmark-metadata/creation_mode` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_01-0740` | `SLOT_TWILIO_01` | `endpoint` | `/x-benchmark-metadata/endpoint` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_01-0741` | `SLOT_TWILIO_01` | `extraction_rule_version` | `/x-benchmark-metadata/extraction_rule_version` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_01-0742` | `SLOT_TWILIO_01` | `extraction_timestamp` | `/x-benchmark-metadata/extraction_timestamp` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_01-0743` | `SLOT_TWILIO_01` | `extractor_git_commit` | `/x-benchmark-metadata/extractor_git_commit` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_01-0744` | `SLOT_TWILIO_01` | `extractor_version` | `/x-benchmark-metadata/extractor_version` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_01-0745` | `SLOT_TWILIO_01` | `governing_specification` | `/x-benchmark-metadata/governing_specification` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_01-0746` | `SLOT_TWILIO_01` | `http_method` | `/x-benchmark-metadata/http_method` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_01-0747` | `SLOT_TWILIO_01` | `independent_validation_claimed` | `/x-benchmark-metadata/independent_validation_claimed` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_01-0748` | `SLOT_TWILIO_01` | `operation_id` | `/x-benchmark-metadata/operation_id` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_01-0749` | `SLOT_TWILIO_01` | `request_content_type` | `/x-benchmark-metadata/request_content_type` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_01-0750` | `SLOT_TWILIO_01` | `semantic_validation_decision` | `/x-benchmark-metadata/semantic_validation_decision` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_01-0751` | `SLOT_TWILIO_01` | `serialization_metadata` | `/x-benchmark-metadata/serialization_metadata` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_01-0752` | `SLOT_TWILIO_01` | `slot_id` | `/x-benchmark-metadata/slot_id` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_01-0753` | `SLOT_TWILIO_01` | `source_cluster_id` | `/x-benchmark-metadata/source_cluster_id` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_01-0754` | `SLOT_TWILIO_01` | `source_file_blob_sha` | `/x-benchmark-metadata/source_file_blob_sha` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_01-0755` | `SLOT_TWILIO_01` | `source_file_sha256` | `/x-benchmark-metadata/source_file_sha256` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_01-0756` | `SLOT_TWILIO_01` | `source_spec_pointer` | `/x-benchmark-metadata/source_spec_pointer` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_01-0757` | `SLOT_TWILIO_01` | `source_structural_metrics` | `/x-benchmark-metadata/source_structural_metrics` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_01-0758` | `SLOT_TWILIO_01` | `status` | `/x-benchmark-metadata/status` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_01-0759` | `SLOT_TWILIO_01` | `target_domain` | `/x-benchmark-metadata/target_domain` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_01-0760` | `SLOT_TWILIO_01` | `wrapped_contract_structural_metrics` | `/x-benchmark-metadata/wrapped_contract_structural_metrics` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_01-0761` | `SLOT_TWILIO_01` | `wrapper_normalization_policy` | `/x-benchmark-metadata/wrapper_normalization_policy` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_01-0762` | `SLOT_TWILIO_01` | `content_type` | `/x-benchmark-metadata/serialization_metadata/content_type` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_01-0763` | `SLOT_TWILIO_01` | `encoding` | `/x-benchmark-metadata/serialization_metadata/encoding` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_01-0764` | `SLOT_TWILIO_01` | `encoding_metadata_present` | `/x-benchmark-metadata/serialization_metadata/encoding_metadata_present` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_01-0765` | `SLOT_TWILIO_01` | `serialization_strategy` | `/x-benchmark-metadata/serialization_metadata/serialization_strategy` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_01-0766` | `SLOT_TWILIO_01` | `raw_nesting_depth` | `/x-benchmark-metadata/source_structural_metrics/raw_nesting_depth` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_01-0767` | `SLOT_TWILIO_01` | `raw_parameter_count` | `/x-benchmark-metadata/source_structural_metrics/raw_parameter_count` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_01-0768` | `SLOT_TWILIO_01` | `surface_containers_present` | `/x-benchmark-metadata/wrapped_contract_structural_metrics/surface_containers_present` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_01-0769` | `SLOT_TWILIO_01` | `surface_containers_required` | `/x-benchmark-metadata/wrapped_contract_structural_metrics/surface_containers_required` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_01-0770` | `SLOT_TWILIO_01` | `total_property_count` | `/x-benchmark-metadata/wrapped_contract_structural_metrics/total_property_count` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_01-0771` | `SLOT_TWILIO_01` | `wrapped_nesting_depth` | `/x-benchmark-metadata/wrapped_contract_structural_metrics/wrapped_nesting_depth` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_01-0772` | `SLOT_TWILIO_01` | `additional_properties_closed` | `/x-benchmark-metadata/wrapper_normalization_policy/additional_properties_closed` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_01-0773` | `SLOT_TWILIO_01` | `is_strictly_lossless` | `/x-benchmark-metadata/wrapper_normalization_policy/is_strictly_lossless` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_01-0774` | `SLOT_TWILIO_01` | `policy_id` | `/x-benchmark-metadata/wrapper_normalization_policy/policy_id` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_01-0775` | `SLOT_TWILIO_01` | `rationale` | `/x-benchmark-metadata/wrapper_normalization_policy/rationale` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0776` | `SLOT_TWILIO_02` | `body` | `/properties/body` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0777` | `SLOT_TWILIO_02` | `header` | `/properties/header` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0778` | `SLOT_TWILIO_02` | `path` | `/properties/path` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0779` | `SLOT_TWILIO_02` | `query` | `/properties/query` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0780` | `SLOT_TWILIO_02` | `AddressRetention` | `/properties/body/properties/AddressRetention` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0781` | `SLOT_TWILIO_02` | `ApplicationSid` | `/properties/body/properties/ApplicationSid` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0782` | `SLOT_TWILIO_02` | `Attempt` | `/properties/body/properties/Attempt` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0783` | `SLOT_TWILIO_02` | `Body` | `/properties/body/properties/Body` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0784` | `SLOT_TWILIO_02` | `ContentRetention` | `/properties/body/properties/ContentRetention` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0785` | `SLOT_TWILIO_02` | `ContentSid` | `/properties/body/properties/ContentSid` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0786` | `SLOT_TWILIO_02` | `ContentVariables` | `/properties/body/properties/ContentVariables` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0787` | `SLOT_TWILIO_02` | `FallbackFrom` | `/properties/body/properties/FallbackFrom` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0788` | `SLOT_TWILIO_02` | `ForceDelivery` | `/properties/body/properties/ForceDelivery` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0789` | `SLOT_TWILIO_02` | `From` | `/properties/body/properties/From` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0790` | `SLOT_TWILIO_02` | `MaxPrice` | `/properties/body/properties/MaxPrice` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0791` | `SLOT_TWILIO_02` | `MediaUrl` | `/properties/body/properties/MediaUrl` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0792` | `SLOT_TWILIO_02` | `MessageIntent` | `/properties/body/properties/MessageIntent` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0793` | `SLOT_TWILIO_02` | `MessagingServiceSid` | `/properties/body/properties/MessagingServiceSid` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0794` | `SLOT_TWILIO_02` | `PersistentAction` | `/properties/body/properties/PersistentAction` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0795` | `SLOT_TWILIO_02` | `ProvideFeedback` | `/properties/body/properties/ProvideFeedback` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0796` | `SLOT_TWILIO_02` | `RiskCheck` | `/properties/body/properties/RiskCheck` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0797` | `SLOT_TWILIO_02` | `ScheduleType` | `/properties/body/properties/ScheduleType` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0798` | `SLOT_TWILIO_02` | `SendAsMms` | `/properties/body/properties/SendAsMms` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0799` | `SLOT_TWILIO_02` | `SendAt` | `/properties/body/properties/SendAt` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0800` | `SLOT_TWILIO_02` | `ShortenUrls` | `/properties/body/properties/ShortenUrls` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0801` | `SLOT_TWILIO_02` | `SmartEncoded` | `/properties/body/properties/SmartEncoded` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0802` | `SLOT_TWILIO_02` | `StatusCallback` | `/properties/body/properties/StatusCallback` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0803` | `SLOT_TWILIO_02` | `To` | `/properties/body/properties/To` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0804` | `SLOT_TWILIO_02` | `TrafficType` | `/properties/body/properties/TrafficType` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0805` | `SLOT_TWILIO_02` | `ValidityPeriod` | `/properties/body/properties/ValidityPeriod` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0806` | `SLOT_TWILIO_02` | `ignoreFormat` | `/properties/body/properties/MediaUrl/items/x-twilio/ignoreFormat` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0807` | `SLOT_TWILIO_02` | `AccountSid` | `/properties/path/properties/AccountSid` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0808` | `SLOT_TWILIO_02` | `admission_decision` | `/x-benchmark-metadata/admission_decision` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0809` | `SLOT_TWILIO_02` | `candidate_source_id` | `/x-benchmark-metadata/candidate_source_id` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0810` | `SLOT_TWILIO_02` | `creation_mode` | `/x-benchmark-metadata/creation_mode` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0811` | `SLOT_TWILIO_02` | `endpoint` | `/x-benchmark-metadata/endpoint` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0812` | `SLOT_TWILIO_02` | `extraction_rule_version` | `/x-benchmark-metadata/extraction_rule_version` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0813` | `SLOT_TWILIO_02` | `extraction_timestamp` | `/x-benchmark-metadata/extraction_timestamp` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0814` | `SLOT_TWILIO_02` | `extractor_git_commit` | `/x-benchmark-metadata/extractor_git_commit` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0815` | `SLOT_TWILIO_02` | `extractor_version` | `/x-benchmark-metadata/extractor_version` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0816` | `SLOT_TWILIO_02` | `governing_specification` | `/x-benchmark-metadata/governing_specification` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0817` | `SLOT_TWILIO_02` | `http_method` | `/x-benchmark-metadata/http_method` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0818` | `SLOT_TWILIO_02` | `independent_validation_claimed` | `/x-benchmark-metadata/independent_validation_claimed` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0819` | `SLOT_TWILIO_02` | `operation_id` | `/x-benchmark-metadata/operation_id` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0820` | `SLOT_TWILIO_02` | `request_content_type` | `/x-benchmark-metadata/request_content_type` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0821` | `SLOT_TWILIO_02` | `semantic_validation_decision` | `/x-benchmark-metadata/semantic_validation_decision` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0822` | `SLOT_TWILIO_02` | `serialization_metadata` | `/x-benchmark-metadata/serialization_metadata` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0823` | `SLOT_TWILIO_02` | `slot_id` | `/x-benchmark-metadata/slot_id` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0824` | `SLOT_TWILIO_02` | `source_cluster_id` | `/x-benchmark-metadata/source_cluster_id` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0825` | `SLOT_TWILIO_02` | `source_file_blob_sha` | `/x-benchmark-metadata/source_file_blob_sha` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0826` | `SLOT_TWILIO_02` | `source_file_sha256` | `/x-benchmark-metadata/source_file_sha256` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0827` | `SLOT_TWILIO_02` | `source_spec_pointer` | `/x-benchmark-metadata/source_spec_pointer` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0828` | `SLOT_TWILIO_02` | `source_structural_metrics` | `/x-benchmark-metadata/source_structural_metrics` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0829` | `SLOT_TWILIO_02` | `status` | `/x-benchmark-metadata/status` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0830` | `SLOT_TWILIO_02` | `target_domain` | `/x-benchmark-metadata/target_domain` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0831` | `SLOT_TWILIO_02` | `wrapped_contract_structural_metrics` | `/x-benchmark-metadata/wrapped_contract_structural_metrics` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0832` | `SLOT_TWILIO_02` | `wrapper_normalization_policy` | `/x-benchmark-metadata/wrapper_normalization_policy` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0833` | `SLOT_TWILIO_02` | `content_type` | `/x-benchmark-metadata/serialization_metadata/content_type` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0834` | `SLOT_TWILIO_02` | `encoding` | `/x-benchmark-metadata/serialization_metadata/encoding` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0835` | `SLOT_TWILIO_02` | `encoding_metadata_present` | `/x-benchmark-metadata/serialization_metadata/encoding_metadata_present` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0836` | `SLOT_TWILIO_02` | `serialization_strategy` | `/x-benchmark-metadata/serialization_metadata/serialization_strategy` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0837` | `SLOT_TWILIO_02` | `raw_nesting_depth` | `/x-benchmark-metadata/source_structural_metrics/raw_nesting_depth` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0838` | `SLOT_TWILIO_02` | `raw_parameter_count` | `/x-benchmark-metadata/source_structural_metrics/raw_parameter_count` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0839` | `SLOT_TWILIO_02` | `surface_containers_present` | `/x-benchmark-metadata/wrapped_contract_structural_metrics/surface_containers_present` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0840` | `SLOT_TWILIO_02` | `surface_containers_required` | `/x-benchmark-metadata/wrapped_contract_structural_metrics/surface_containers_required` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0841` | `SLOT_TWILIO_02` | `total_property_count` | `/x-benchmark-metadata/wrapped_contract_structural_metrics/total_property_count` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0842` | `SLOT_TWILIO_02` | `wrapped_nesting_depth` | `/x-benchmark-metadata/wrapped_contract_structural_metrics/wrapped_nesting_depth` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0843` | `SLOT_TWILIO_02` | `additional_properties_closed` | `/x-benchmark-metadata/wrapper_normalization_policy/additional_properties_closed` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0844` | `SLOT_TWILIO_02` | `is_strictly_lossless` | `/x-benchmark-metadata/wrapper_normalization_policy/is_strictly_lossless` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0845` | `SLOT_TWILIO_02` | `policy_id` | `/x-benchmark-metadata/wrapper_normalization_policy/policy_id` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_02-0846` | `SLOT_TWILIO_02` | `rationale` | `/x-benchmark-metadata/wrapper_normalization_policy/rationale` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0847` | `SLOT_TWILIO_03` | `body` | `/properties/body` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0848` | `SLOT_TWILIO_03` | `header` | `/properties/header` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0849` | `SLOT_TWILIO_03` | `path` | `/properties/path` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0850` | `SLOT_TWILIO_03` | `query` | `/properties/query` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0851` | `SLOT_TWILIO_03` | `ApplicationSid` | `/properties/body/properties/ApplicationSid` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0852` | `SLOT_TWILIO_03` | `AsyncAmd` | `/properties/body/properties/AsyncAmd` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0853` | `SLOT_TWILIO_03` | `AsyncAmdStatusCallback` | `/properties/body/properties/AsyncAmdStatusCallback` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0854` | `SLOT_TWILIO_03` | `AsyncAmdStatusCallbackMethod` | `/properties/body/properties/AsyncAmdStatusCallbackMethod` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0855` | `SLOT_TWILIO_03` | `Byoc` | `/properties/body/properties/Byoc` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0856` | `SLOT_TWILIO_03` | `CallReason` | `/properties/body/properties/CallReason` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0857` | `SLOT_TWILIO_03` | `CallToken` | `/properties/body/properties/CallToken` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0858` | `SLOT_TWILIO_03` | `CallerId` | `/properties/body/properties/CallerId` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0859` | `SLOT_TWILIO_03` | `ClientNotificationUrl` | `/properties/body/properties/ClientNotificationUrl` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0860` | `SLOT_TWILIO_03` | `FallbackMethod` | `/properties/body/properties/FallbackMethod` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0861` | `SLOT_TWILIO_03` | `FallbackUrl` | `/properties/body/properties/FallbackUrl` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0862` | `SLOT_TWILIO_03` | `From` | `/properties/body/properties/From` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0863` | `SLOT_TWILIO_03` | `MachineDetection` | `/properties/body/properties/MachineDetection` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0864` | `SLOT_TWILIO_03` | `MachineDetectionSilenceTimeout` | `/properties/body/properties/MachineDetectionSilenceTimeout` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0865` | `SLOT_TWILIO_03` | `MachineDetectionSpeechEndThreshold` | `/properties/body/properties/MachineDetectionSpeechEndThreshold` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0866` | `SLOT_TWILIO_03` | `MachineDetectionSpeechThreshold` | `/properties/body/properties/MachineDetectionSpeechThreshold` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0867` | `SLOT_TWILIO_03` | `MachineDetectionTimeout` | `/properties/body/properties/MachineDetectionTimeout` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0868` | `SLOT_TWILIO_03` | `Method` | `/properties/body/properties/Method` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0869` | `SLOT_TWILIO_03` | `Passports` | `/properties/body/properties/Passports` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0870` | `SLOT_TWILIO_03` | `Record` | `/properties/body/properties/Record` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0871` | `SLOT_TWILIO_03` | `RecordingChannels` | `/properties/body/properties/RecordingChannels` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0872` | `SLOT_TWILIO_03` | `RecordingConfigurationId` | `/properties/body/properties/RecordingConfigurationId` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0873` | `SLOT_TWILIO_03` | `RecordingStatusCallback` | `/properties/body/properties/RecordingStatusCallback` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0874` | `SLOT_TWILIO_03` | `RecordingStatusCallbackEvent` | `/properties/body/properties/RecordingStatusCallbackEvent` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0875` | `SLOT_TWILIO_03` | `RecordingStatusCallbackMethod` | `/properties/body/properties/RecordingStatusCallbackMethod` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0876` | `SLOT_TWILIO_03` | `RecordingTrack` | `/properties/body/properties/RecordingTrack` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0877` | `SLOT_TWILIO_03` | `SendDigits` | `/properties/body/properties/SendDigits` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0878` | `SLOT_TWILIO_03` | `SipAuthPassword` | `/properties/body/properties/SipAuthPassword` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0879` | `SLOT_TWILIO_03` | `SipAuthUsername` | `/properties/body/properties/SipAuthUsername` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0880` | `SLOT_TWILIO_03` | `StatusCallback` | `/properties/body/properties/StatusCallback` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0881` | `SLOT_TWILIO_03` | `StatusCallbackEvent` | `/properties/body/properties/StatusCallbackEvent` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0882` | `SLOT_TWILIO_03` | `StatusCallbackMethod` | `/properties/body/properties/StatusCallbackMethod` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0883` | `SLOT_TWILIO_03` | `TimeLimit` | `/properties/body/properties/TimeLimit` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0884` | `SLOT_TWILIO_03` | `Timeout` | `/properties/body/properties/Timeout` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0885` | `SLOT_TWILIO_03` | `To` | `/properties/body/properties/To` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0886` | `SLOT_TWILIO_03` | `Trim` | `/properties/body/properties/Trim` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0887` | `SLOT_TWILIO_03` | `Twiml` | `/properties/body/properties/Twiml` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0888` | `SLOT_TWILIO_03` | `Url` | `/properties/body/properties/Url` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0889` | `SLOT_TWILIO_03` | `AccountSid` | `/properties/path/properties/AccountSid` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0890` | `SLOT_TWILIO_03` | `admission_decision` | `/x-benchmark-metadata/admission_decision` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0891` | `SLOT_TWILIO_03` | `candidate_source_id` | `/x-benchmark-metadata/candidate_source_id` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0892` | `SLOT_TWILIO_03` | `creation_mode` | `/x-benchmark-metadata/creation_mode` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0893` | `SLOT_TWILIO_03` | `endpoint` | `/x-benchmark-metadata/endpoint` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0894` | `SLOT_TWILIO_03` | `extraction_rule_version` | `/x-benchmark-metadata/extraction_rule_version` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0895` | `SLOT_TWILIO_03` | `extraction_timestamp` | `/x-benchmark-metadata/extraction_timestamp` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0896` | `SLOT_TWILIO_03` | `extractor_git_commit` | `/x-benchmark-metadata/extractor_git_commit` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0897` | `SLOT_TWILIO_03` | `extractor_version` | `/x-benchmark-metadata/extractor_version` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0898` | `SLOT_TWILIO_03` | `governing_specification` | `/x-benchmark-metadata/governing_specification` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0899` | `SLOT_TWILIO_03` | `http_method` | `/x-benchmark-metadata/http_method` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0900` | `SLOT_TWILIO_03` | `independent_validation_claimed` | `/x-benchmark-metadata/independent_validation_claimed` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0901` | `SLOT_TWILIO_03` | `operation_id` | `/x-benchmark-metadata/operation_id` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0902` | `SLOT_TWILIO_03` | `request_content_type` | `/x-benchmark-metadata/request_content_type` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0903` | `SLOT_TWILIO_03` | `semantic_validation_decision` | `/x-benchmark-metadata/semantic_validation_decision` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0904` | `SLOT_TWILIO_03` | `serialization_metadata` | `/x-benchmark-metadata/serialization_metadata` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0905` | `SLOT_TWILIO_03` | `slot_id` | `/x-benchmark-metadata/slot_id` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0906` | `SLOT_TWILIO_03` | `source_cluster_id` | `/x-benchmark-metadata/source_cluster_id` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0907` | `SLOT_TWILIO_03` | `source_file_blob_sha` | `/x-benchmark-metadata/source_file_blob_sha` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0908` | `SLOT_TWILIO_03` | `source_file_sha256` | `/x-benchmark-metadata/source_file_sha256` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0909` | `SLOT_TWILIO_03` | `source_spec_pointer` | `/x-benchmark-metadata/source_spec_pointer` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0910` | `SLOT_TWILIO_03` | `source_structural_metrics` | `/x-benchmark-metadata/source_structural_metrics` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0911` | `SLOT_TWILIO_03` | `status` | `/x-benchmark-metadata/status` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0912` | `SLOT_TWILIO_03` | `target_domain` | `/x-benchmark-metadata/target_domain` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0913` | `SLOT_TWILIO_03` | `wrapped_contract_structural_metrics` | `/x-benchmark-metadata/wrapped_contract_structural_metrics` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0914` | `SLOT_TWILIO_03` | `wrapper_normalization_policy` | `/x-benchmark-metadata/wrapper_normalization_policy` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0915` | `SLOT_TWILIO_03` | `content_type` | `/x-benchmark-metadata/serialization_metadata/content_type` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0916` | `SLOT_TWILIO_03` | `encoding` | `/x-benchmark-metadata/serialization_metadata/encoding` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0917` | `SLOT_TWILIO_03` | `encoding_metadata_present` | `/x-benchmark-metadata/serialization_metadata/encoding_metadata_present` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0918` | `SLOT_TWILIO_03` | `serialization_strategy` | `/x-benchmark-metadata/serialization_metadata/serialization_strategy` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0919` | `SLOT_TWILIO_03` | `raw_nesting_depth` | `/x-benchmark-metadata/source_structural_metrics/raw_nesting_depth` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0920` | `SLOT_TWILIO_03` | `raw_parameter_count` | `/x-benchmark-metadata/source_structural_metrics/raw_parameter_count` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0921` | `SLOT_TWILIO_03` | `surface_containers_present` | `/x-benchmark-metadata/wrapped_contract_structural_metrics/surface_containers_present` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0922` | `SLOT_TWILIO_03` | `surface_containers_required` | `/x-benchmark-metadata/wrapped_contract_structural_metrics/surface_containers_required` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0923` | `SLOT_TWILIO_03` | `total_property_count` | `/x-benchmark-metadata/wrapped_contract_structural_metrics/total_property_count` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0924` | `SLOT_TWILIO_03` | `wrapped_nesting_depth` | `/x-benchmark-metadata/wrapped_contract_structural_metrics/wrapped_nesting_depth` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0925` | `SLOT_TWILIO_03` | `additional_properties_closed` | `/x-benchmark-metadata/wrapper_normalization_policy/additional_properties_closed` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0926` | `SLOT_TWILIO_03` | `is_strictly_lossless` | `/x-benchmark-metadata/wrapper_normalization_policy/is_strictly_lossless` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0927` | `SLOT_TWILIO_03` | `policy_id` | `/x-benchmark-metadata/wrapper_normalization_policy/policy_id` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |
| `DIALECT-SLOT_TWILIO_03-0928` | `SLOT_TWILIO_03` | `rationale` | `/x-benchmark-metadata/wrapper_normalization_policy/rationale` | OpenAPI 3.0.1 | `UNKNOWN_OAS_KEYWORD` | YES | `AUDIT_AND_QUARANTINE` |

---

## 5. Methodological Conclusions & Action Plan

1. **Retraction of Absolute Zero-Potential-Loss Claims:** The claim that Batch-V1 candidates achieved 'zero potential loss' is retracted for slots containing OpenAPI 3.0 `nullable: true` (specifically `SLOT_GITHUB_02`).
2. **Formal Conversion Policy Required:** `results_stage_b/OAS30_TO_DRAFT07_CONVERSION_POLICY_001.md` must govern all conversions from OpenAPI 3.0 modifiers to Draft-07 type representations.
3. **Batch Pipeline V2 Required:** A versioned batch pipeline must regenerate candidate contracts into `data_stage_b/extraction_candidates_v2/` applying explicit `nullable` type union conversion (`type: [<type>, "null"]`) and quarantining OAS-specific keywords.
4. **Preservation of Historical V1 Evidence:** Existing V1 candidate directories must be permanently preserved to maintain an uncompromised scientific record.

