"""
build_dataset.py - Generates base schemas, domain-matched distractors, and queries.
"""

import json
import os

from build_dataset_schemas import BASE_SCHEMAS, DOMAIN_DISTRACTORS

def main():
    data_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Save base schemas
    base_file = os.path.join(data_dir, "base_schemas.json")
    with open(base_file, "w", encoding="utf-8") as f:
        json.dump(BASE_SCHEMAS, f, indent=2)
    print(f"Saved {len(BASE_SCHEMAS)} base schemas to {base_file}")
    
    # Save domain-matched distractors
    dist_file = os.path.join(data_dir, "distractor_tools.json")
    with open(dist_file, "w", encoding="utf-8") as f:
        json.dump(DOMAIN_DISTRACTORS, f, indent=2)
    print(f"Saved domain-matched distractors for {len(DOMAIN_DISTRACTORS)} tools to {dist_file}")

if __name__ == "__main__":
    main()
