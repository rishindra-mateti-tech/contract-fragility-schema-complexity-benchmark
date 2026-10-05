"""
linter.py - Static Schema Fragility Linter (SchemaFragilityLinter).
Audits tool contracts against empirically proven structural failure patterns.
"""

import json
import sys

AMBIGUOUS_NAMES = {
    "id", "data", "target", "payload", "qty", "loc", "val", "p1", "p2",
    "param", "arg", "item", "spec", "ns", "info", "conf", "str_val", "num"
}

class SchemaFragilityLinter:
    def __init__(self):
        self.diagnostics = []

    def audit_schema(self, schema_dict, tool_name="unknown_tool"):
        self.diagnostics = []
        parameters = schema_dict.get("parameters", schema_dict)
        props = parameters.get("properties", {})
        required = set(parameters.get("required", []))
        
        # Rule 1: Check Nesting Depth
        self._check_nesting(props, depth=1, path="")
        
        # Rule 2: Check Optionality Density
        num_required = len(required)
        num_optional = len(props) - num_required
        if len(props) > 4 and num_optional > (2 * max(1, num_required)):
            self.diagnostics.append({
                "severity": "WARNING",
                "rule": "EXCESSIVE_OPTIONALITY_BLOAT",
                "message": (
                    f"Tool '{tool_name}' has high optionality density ({num_optional} optional vs {num_required} required). "
                    "Empirical evidence demonstrates that high optional field density increases prompt token bloat "
                    "and induces argument hallucination."
                )
            })
            
        # Rule 3: Check Identifier Specificity
        for p_name, p_def in props.items():
            if p_name.lower() in AMBIGUOUS_NAMES:
                self.diagnostics.append({
                    "severity": "WARNING",
                    "rule": "AMBIGUOUS_IDENTIFIER",
                    "message": (
                        f"Parameter '{p_name}' in tool '{tool_name}' uses a generic or truncated identifier. "
                        "Replace with an explicit domain noun (e.g., 'charge_id', 'recipient_number')."
                    )
                })
                
            # Rule 4: Missing Documentation
            desc = p_def.get("description", "")
            if not desc or len(desc.strip()) < 8:
                self.diagnostics.append({
                    "severity": "ERROR",
                    "rule": "MISSING_PARAMETER_DOCSTRING",
                    "message": f"Parameter '{p_name}' lacks a descriptive docstring, increasing parameter extraction failure rate."
                })
                
            # Rule 5: Free-text options instead of Enum
            p_type = p_def.get("type", "").upper()
            if p_type == "STRING" and "enum" not in p_def:
                for indicator in ["must be one of", "can be either", "allowed values:", "choices:"]:
                    if indicator in desc.lower():
                        self.diagnostics.append({
                            "severity": "INFO",
                            "rule": "UNBOUND_ENUM_SPECIFICATION",
                            "message": (
                                f"Parameter '{p_name}' appears to specify discrete choices in text ('{indicator}') "
                                "without an explicit 'enum' array in JSON Schema."
                            )
                        })
                        
        return self.diagnostics

    def _check_nesting(self, props, depth, path):
        for k, v in props.items():
            cur_path = f"{path}.{k}" if path else k
            if isinstance(v, dict) and v.get("type", "").upper() == "OBJECT":
                if depth >= 2:
                    self.diagnostics.append({
                        "severity": "CRITICAL",
                        "rule": "DEEP_HIERARCHICAL_NESTING",
                        "message": (
                            f"Object hierarchy at '{cur_path}' reaches depth {depth}. "
                            "Empirical results prove that nested object schemas increase structural validation "
                            "failure rates significantly compared to flat parameter contracts."
                        )
                    })
                sub_props = v.get("properties", {})
                self._check_nesting(sub_props, depth + 1, cur_path)

def lint_file(file_path):
    linter = SchemaFragilityLinter()
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    tools = data if isinstance(data, list) else [data]
    total_issues = 0
    print(f"Linting tool contracts in {file_path}...\n")
    
    for tool in tools:
        t_name = tool.get("name", "unnamed")
        diags = linter.audit_schema(tool, tool_name=t_name)
        if diags:
            print(f"[{t_name}] ({len(diags)} issues):")
            for d in diags:
                print(f"  [{d['severity']}] {d['rule']}: {d['message']}")
            print()
            total_issues += len(diags)
        else:
            print(f"[{t_name}] PASS - Clean schema contract.")
            
    print(f"Audit Complete: Found {total_issues} schema fragility warnings across {len(tools)} tools.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        lint_file(sys.argv[1])
    else:
        print("Usage: python linter.py <path_to_schema_json>")
