import json
import hashlib
import random
import os

def hash_dict(d):
    return hashlib.sha256(json.dumps(d, sort_keys=True).encode('utf-8')).hexdigest()

def main():
    with open('data/mutated_schemas.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    domains = {
        'Infra_DevOps': ['github_create_issue', 'k8s_scale_deployment', 'aws_create_s3_bucket', 'datadog_create_alert', 'cloudflare_purge_cache', 'pagerduty_trigger_incident', 'docker_run_container'],
        'Enterprise_CRM_Sales': ['stripe_create_refund', 'crm_update_lead', 'zendesk_create_ticket', 'mailchimp_add_subscriber', 'shopify_create_discount', 'jira_transition_issue'],
        'Data_Identity': ['database_execute_query', 'elasticsearch_index_doc', 'auth0_create_user', 'notion_create_page'],
        'Comms_Logistics': ['slack_post_message', 'twilio_send_sms', 'shipping_create_label']
    }
    
    schema_map = {d['base_id']: d for d in data}
    random.seed(42)
    selected_schemas = []
    
    for domain, ids in domains.items():
        ids.sort()
        sampled = random.sample(ids, 2)
        for s_id in sampled:
            item = schema_map[s_id]
            canonical_tool = item['variants']['canonical']['tool']
            mutations = {}
            for k, v in item['variants'].items():
                mutations[k] = hash_dict(v['tool'])
                
            selected_schemas.append({
                'base_id': s_id,
                'domain': domain,
                'query': item['query'],
                'expected_args': item['variants']['canonical']['expected_args'],
                'canonical_hash': hash_dict(canonical_tool),
                'mutation_hashes': mutations
            })
            
    manifest = {
        'metadata': {
            'purpose': 'Stage A Pilot Selection',
            'selection_method': 'Stratified random sampling',
            'random_seed': 42,
            'total_selected': len(selected_schemas)
        },
        'schemas': selected_schemas
    }
    
    with open('data/pilot_manifest.json', 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)
    print("Created data/pilot_manifest.json")

if __name__ == '__main__':
    main()
