# Dataset Provenance and Specification Manifest

This document records the design methodology, structural characteristics, and synthetic modeling of the tool specifications used in the Contract Fragility benchmark.

---

## 1. Design Rationale: Synthetic API-Inspired Specifications

In empirical software engineering and function-calling evaluation, benchmarking against live third-party production APIs presents major validity and safety hazards:
1. **Destructive Mutation Risks:** Real-world execution of operations such as deleting cloud storage buckets, dropping database tables, or issuing credit card refunds creates significant operational liability.
2. **Credential & Secret Leakage:** Requiring real API tokens risks credential exposure and prevents open reproducibility.
3. **Lack of Structural Control:** Production schemas evolve organically and cannot be systematically varied along isolated complexity axes.

To resolve these challenges while maintaining authentic real-world fidelity, the **Contract Fragility Dataset** comprises **20 synthetic tool specifications modeled after established enterprise API patterns** (including Stripe, GitHub REST, Slack Web API, Kubernetes, AWS S3, Datadog, Twilio, and Zendesk).

Each schema is formulated in strict accordance with the **JSON Schema Draft-07** specification and OpenAPI 3.0 conventions.

---

## 2. Specification Inventory

| Schema Identifier | Modeled Domain | Modeled Service Pattern | Primary Action | Required Parameters | Optional Parameters |
| :--- | :--- | :--- | :--- | :---: | :---: |
| `stripe_create_refund` | Fintech / Billing | Stripe Billing API | Process payment refund | 3 | 1 |
| `github_create_issue` | Developer Tools | GitHub REST API v3 | Open issue tracking item | 4 | 1 |
| `slack_post_message` | Team Collaboration | Slack Web API | Send channel message | 2 | 2 |
| `k8s_scale_deployment` | Cloud Infrastructure | Kubernetes Workloads API | Scale pod replica count | 3 | 1 |
| `aws_create_s3_bucket` | Cloud Storage | AWS S3 REST API | Provision storage bucket | 2 | 1 |
| `database_execute_query` | Data Systems | PostgreSQL / Database API | Execute SQL statement | 2 | 2 |
| `crm_update_lead` | Enterprise CRM | Salesforce / HubSpot CRM | Update lead stage & value | 3 | 1 |
| `shipping_create_label` | Logistics | FedEx / UPS Logistics API | Generate shipping label | 4 | 0 |
| `jira_transition_issue` | Project Management | Atlassian Jira API | Transition ticket status | 2 | 1 |
| `datadog_create_alert` | Observability | Datadog Monitoring API | Configure threshold alert | 3 | 1 |
| `twilio_send_sms` | Communications | Twilio Messaging API | Dispatch outbound SMS | 2 | 1 |
| `zendesk_create_ticket` | Customer Support | Zendesk Helpdesk API | Open customer support ticket | 4 | 0 |
| `mailchimp_add_subscriber` | Marketing | Mailchimp Marketing API | Add audience subscriber | 3 | 1 |
| `cloudflare_purge_cache` | Edge / CDN | Cloudflare Edge API | Invalidate CDN cache | 2 | 1 |
| `pagerduty_trigger_incident` | Site Reliability | PagerDuty Events API v2 | Trigger on-call incident | 3 | 1 |
| `auth0_create_user` | Identity & Security | Auth0 Management API | Provision directory user | 3 | 1 |
| `elasticsearch_index_doc` | Search Engines | Elasticsearch Documents API | Index JSON document | 2 | 2 |
| `notion_create_page` | Knowledge Base | Notion Database API | Create database page | 3 | 1 |
| `docker_run_container` | Container Runtimes | Docker Engine API | Run container instance | 3 | 1 |
| `shopify_create_discount` | E-Commerce | Shopify Admin API | Create promo discount code | 3 | 1 |

---

## 3. Structural Mutation Taxonomy

Each base specification is programmatically perturbed into four controlled structural variants holding the underlying semantic query intent frozen:

1. **`canonical` (Baseline):** Flat parameter layout, explicit domain nouns, strict type designations, and complete parameter descriptions.
2. **`nested_hierarchy`:** The parameter set is encapsulated into a nested sub-object (`request_payload`), introducing hierarchical depth.
3. **`optionality_bloat`:** Six standard enterprise metadata properties (`tags`, `correlation_id`, `idempotency_key`, `priority_level`, `notify_on_completion`, `audit_comment`) are injected to assess context distraction.
4. **`ambiguous_identifiers`:** Explicit domain nouns are replaced with truncated abbreviations and generic tokens (`target_id`, `qty`, `spec`, `val`) across both tool-level and parameter-level descriptors.
