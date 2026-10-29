"""Stage C Release 2 Prompt Renderer.

Renders fluent, natural-language benchmark prompts for Release 2 task instances:
- Eliminates target tool-name leakage in Argument Construction and Tool Selection.
- Eliminates verbatim snake_case schema property key dumps.
- Translates semantic slot values into natural conversational descriptions.
- Provides multi-frame prompt template variations across domains.
- Enforces strict leakage and abstention-hint prevention checks.
"""

from typing import Any, Dict, List, Optional, Tuple
import hashlib
import json
import re


class StageCRelease2PromptRenderer:
    """Renderer for Release 2 benchmark prompts with natural phrasing."""

    SLOT_NATURAL_TRANSLATIONS = {
        "key": "with lookup key '{val}'",
        "value": "setting the value payload to '{val}'",
        "ttl_seconds": "with a time-to-live expiration of {val} seconds",
        "overwrite": "allowing existing records to be overwritten" if "{val}" == "True" else "without overwriting existing records",
        "table_name": "for the '{val}' table",
        "slice_index": "targeting partition slice {val}",
        "force_truncate": "forcing immediate truncation" if "{val}" == "True" else "performing standard truncation",
        "call_id": "for active call session '{val}'",
        "record_audio": "enabling audio recording" if "{val}" == "True" else "disabling audio recording",
        "status_code": "setting terminal status code {val}",
        "flush_immediately": "flushing all buffers immediately" if "{val}" == "True" else "using standard buffer flushing",
        "increment_by": "incrementing the counter by {val}",
        "lock_hours": "holding the lock for {val} hours",
        "priority": "with {val} priority",
        "cluster_id": "on cluster '{val}'",
        "dataset_name": "in dataset '{val}'",
        "recipient_number": "to destination number '{val}'",
        "message_body": "with message text '{val}'",
        "metric_name": "for metric '{val}'",
        "metric_series": "in metric series '{val}'",
        "sample_count": "collecting {val} samples",
        "algorithm": "using the {val} algorithm",
        "endpoint": "at endpoint '{val}'",
        "token_id": "for token identifier '{val}'",
        "token_ttl_days": "valid for {val} days",
        "pipeline_id": "for pipeline '{val}'",
        "workflow_id": "in workflow '{val}'",
        "session_id": "for session '{val}'",
        "user_id": "for user account '{val}'",
        "tenant_id": "within tenant '{val}'",
        "device_id": "for device '{val}'",
        "timeout_seconds": "with a timeout of {val} seconds",
        "reason": "providing reason '{val}'",
        "event_type": "categorized as event '{val}'",
        "index_mode": "using {val} indexing",
        "stage_name": "at stage '{val}'",
        "max_retries": "allowing up to {val} retries",
        "format_spec": "formatted according to '{val}'",
        "cron_expression": "scheduled via cron expression '{val}'",
        "client_name": "for client '{val}'",
        "alert_title": "titled '{val}'",
        "severity_level": "marked with {val} severity",
    }

    AC_FRAMES = [
        "Please {action_verb} {action_target}. Specifically, configure this by {params_desc}.",
        "We need to {action_verb} {action_target}. Execute this request {params_desc}.",
        "Perform a task to {action_verb} {action_target}, ensuring that you are {params_desc}.",
        "Kindly {action_verb} {action_target}. The operational requirements are: {params_desc}."
    ]

    TS_FRAMES = [
        "We need to {action_verb} {action_target} for operations batch {task_idx:03d}. Please configure: {params_desc}.",
        "A user requested to {action_verb} {action_target} under dispatch tag #{task_idx:03d}. Apply the following specifications: {params_desc}.",
        "Dispatch an automated request to {action_verb} {action_target} (reference ref_{task_idx:03d}). Required configuration: {params_desc}.",
        "The system needs to {action_verb} {action_target} for execution run {task_idx:03d}. Ensure you {params_desc}."
    ]

    @classmethod
    def naturalize_slots(cls, slot_values: Dict[str, Any]) -> str:
        """Converts raw parameter dictionary into fluent English clauses."""
        clauses = []
        for k, v in slot_values.items():
            if k in cls.SLOT_NATURAL_TRANSLATIONS:
                tmpl = cls.SLOT_NATURAL_TRANSLATIONS[k]
                if "{val}" in tmpl:
                    clause = tmpl.replace("{val}", str(v))
                else:
                    clause = tmpl
            else:
                spaced_key = k.replace("_", " ")
                if isinstance(v, bool):
                    clause = f"enabling {spaced_key}" if v else f"disabling {spaced_key}"
                else:
                    clause = f"setting {spaced_key} to '{v}'"
            clauses.append(clause)
        return ", ".join(clauses)

    @classmethod
    def extract_action_phrases(cls, title: str, description: str) -> Tuple[str, str]:
        """Extracts action verb and action target from contract title and description."""
        clean_title = title.strip()
        words = clean_title.split()
        if len(words) >= 2:
            verb = words[0].lower()
            target = " ".join(words[1:]).lower()
        else:
            verb = "process"
            target = clean_title.lower()
        return verb, target

    @classmethod
    def render_argument_construction_prompt(
        cls,
        contract: Dict[str, Any],
        slot_values: Dict[str, Any],
        seed_int: int
    ) -> Tuple[str, str]:
        """Renders an Argument Construction prompt with zero tool name or snake_case key leaks."""
        verb, target = cls.extract_action_phrases(contract["title"], contract.get("description", ""))
        params_desc = cls.naturalize_slots(slot_values)
        frame_idx = seed_int % len(cls.AC_FRAMES)
        template_id = f"AC_FRAME_{frame_idx:02d}"
        frame = cls.AC_FRAMES[frame_idx]

        prompt = frame.format(
            action_verb=verb,
            action_target=target,
            params_desc=params_desc
        )
        return prompt, template_id

    @classmethod
    def render_tool_selection_prompt(
        cls,
        contract: Dict[str, Any],
        slot_values: Dict[str, Any],
        seed_int: int,
        task_idx: int = 1
    ) -> Tuple[str, str]:
        """Renders a Tool Selection prompt with zero target tool-name leak."""
        verb, target = cls.extract_action_phrases(contract["title"], contract.get("description", ""))
        params_desc = cls.naturalize_slots(slot_values)
        frame_idx = seed_int % len(cls.TS_FRAMES)
        template_id = f"TS_FRAME_{frame_idx:02d}"
        frame = cls.TS_FRAMES[frame_idx]

        prompt = frame.format(
            action_verb=verb,
            action_target=target,
            params_desc=params_desc,
            task_idx=task_idx
        )
        return prompt, template_id

    @classmethod
    def render_abstention_prompt(
        cls,
        contract: Dict[str, Any],
        pattern: str,
        seed_int: int,
        task_idx: int = 1
    ) -> Tuple[str, str]:
        """Renders an Abstention prompt without artificial hints."""
        verb, target = cls.extract_action_phrases(contract["title"], contract.get("description", ""))
        template_id = f"AB_{pattern}_{seed_int % 4:02d}"

        if pattern == "MISSING_MANDATORY_PARAMETERS":
            prompts = [
                f"Please {verb} {target} for batch run {task_idx:03d} immediately without waiting for specific payload details.",
                f"Initiate the action to {verb} {target} (reference tag ref_{task_idx:03d}) right away without additional configuration parameters.",
                f"Dispatch a request to {verb} {target} for environment env_{task_idx:03d} using default assumptions where possible.",
                f"We want to {verb} {target} in partition part_{task_idx:03d}. Run this operation now without providing parameter values."
            ]
            prompt = prompts[seed_int % len(prompts)]
        elif pattern == "OUT_OF_DOMAIN_UNSUPPORTED":
            prompts = [
                f"Generate a machine learning forecast model for {target} (task #{task_idx:03d}) and export the neural weights to disk.",
                f"Transcribe all related audio communications for {target} (run #{task_idx:03d}) into French subtitles in real time.",
                f"Perform an automated physical hardware diagnostic for batch {task_idx:03d} on the motherboard powering {target}.",
                f"Render a three-dimensional holographic visualization (dataset {task_idx:03d}) of telemetry for {target}."
            ]
            prompt = prompts[seed_int % len(prompts)]
        elif pattern == "CONTRADICTORY_BOUNDS":
            prompts = [
                f"Configure {target} for job {task_idx:03d} with an expiration lifetime of -9999 seconds and negative zero concurrency.",
                f"Execute {verb} for {target} (request #{task_idx:03d}) setting maximum capacity to -1 and minimum threshold to 999999.",
                f"Apply configuration to {target} (dispatch #{task_idx:03d}) requiring simultaneous immediate completion and indefinite suspension.",
                f"Update {target} for partition {task_idx:03d} with a lock duration of zero seconds while enforcing permanent exclusivity."
            ]
            prompt = prompts[seed_int % len(prompts)]
        else:  # AMBIGUOUS_ACTION_REQUEST
            prompts = [
                f"Handle the recent events on {target} for batch {task_idx:03d} using whatever system seems most appropriate.",
                f"Take care of the open items regarding {target} (incident #{task_idx:03d}) across all services.",
                f"Process everything related to {target} for cycle {task_idx:03d} as soon as convenient.",
                f"Do what is necessary for {target} for ticket #{task_idx:03d} based on current status."
            ]
            prompt = prompts[seed_int % len(prompts)]

        return prompt, template_id

    @classmethod
    def check_for_leakage(
        cls,
        prompt: str,
        target_tool: Optional[str] = None,
        schema_props: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """Validates that prompt contains zero tool-name leaks, snake_case leaks, or abstention hints."""
        violations = []
        p_lower = prompt.lower()

        # Check tool name
        if target_tool:
            if target_tool.lower() in p_lower:
                violations.append(f"Target tool name '{target_tool}' found in prompt.")
            clean_name = re.sub(r"^synth_", "", target_tool)
            if clean_name.lower() in p_lower:
                violations.append(f"Clean tool name '{clean_name}' found in prompt.")

        # Check verbatim snake_case property keys
        if schema_props:
            for k in schema_props.keys():
                if "_" in k and len(k) > 4:
                    if re.search(r"\b" + re.escape(k.lower()) + r"\b", p_lower):
                        violations.append(f"Verbatim snake_case parameter key '{k}' found in prompt.")

        # Check forbidden abstention cues
        forbidden_cues = ["none of these", "cannot fulfill", "unavailable", "abstain", "no tool matches"]
        for cue in forbidden_cues:
            if cue in p_lower:
                violations.append(f"Forbidden abstention hint '{cue}' found in prompt.")

        return violations
