# Stage C Human Review Qualification Packet

## 1. Objective and Instructions

Before participating in the benchmark evaluation process, prospective reviewers must complete this 5-item qualification calibration packet.
The purpose of calibration is to verify that reviewers understand:
- JSON Schema Draft-07 syntax constraints.
- Explicit abstention conditions (missing parameters, contradictory bounds).
- Disambiguation across multi-tool environments.

Reviewers must achieve at least 80% consensus agreement with the gold calibration criteria to receive active review assignments.

## 2. Calibration Items

### Item 1: `BLIND_QUAL_001` (Argument Construction - Simple Flat)
- **Natural Language Request**: "Store the session token 'sess_9912' for key 'auth_token' with 3600 seconds time to live."
- **Available Tool**: `set_cache_entry`
  - Schema requires `key` (string), `value` (string), optional `ttl_seconds` (integer).
- **Calibration Objective**: Accurately map user values to schema types without omitting required properties.

### Item 2: `BLIND_QUAL_002` (Abstention - Missing Mandatory Parameter)
- **Natural Language Request**: "Update the account configuration immediately. No further parameters provided."
- **Available Tool**: `update_account_settings`
  - Schema requires `account_id` (string), `settings` (object).
- **Calibration Objective**: Recognize that mandatory parameters are missing with no defaults, and correctly select 'abstain_from_invocation'.

### Item 3: `BLIND_QUAL_003` (Tool Selection - Multi-Tool Discrimination)
- **Natural Language Request**: "Broadcast an urgent alert to slack channel '#devops' with message 'Cluster high load'."
- **Available Tools**:
  - `send_slack_message`: Posts message to designated channel.
  - `send_sms_alert`: Dispatches SMS to phone number.
  - `publish_metric`: Pushes numerical metric.
- **Calibration Objective**: Discriminate between channel-based messaging and SMS alerts.

### Item 4: `BLIND_QUAL_004` (Abstention - Contradictory Boundary Constraint)
- **Natural Language Request**: "Fetch audit logs with maximum limit -500 records."
- **Available Tool**: `fetch_audit_logs`
  - Schema specifies `limit` integer with `minimum: 1, maximum: 1000`.
- **Calibration Objective**: Recognize schema boundary violation and abstain rather than constructing an invalid payload.

### Item 5: `BLIND_QUAL_005` (Argument Construction - Nested Container)
- **Natural Language Request**: "Configure database replica with node name 'node_a', port 5432, read only enabled."
- **Available Tool**: `configure_replica`
  - Schema contains nested object `replica_parameters` with properties `node_name`, `port`, `read_only`.
- **Calibration Objective**: Successfully format arguments inside the nested container rather than flattening properties at the root level.
