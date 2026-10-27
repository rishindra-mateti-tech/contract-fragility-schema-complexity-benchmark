"""Tests for Stage C Latent Intent Model and Intent Codec (Track 2).

Verifies slot creation, intent serialization, hashing determinism,
codec encoding/decoding, and lossless round-trip across synthetic base contracts.
"""

import json
from pathlib import Path
import pytest

from src.stage_c_latent_intent import LatentSlot, LatentIntent
from src.stage_c_intent_codec import StageCIntentCodec


REPO_ROOT = Path(__file__).resolve().parent.parent
BASE_CONTRACTS_DIR = REPO_ROOT / "data_stage_c" / "base_contracts"


def test_latent_slot_and_intent_creation():
    slot1 = LatentSlot(name="user_id", value="usr_981", data_type="string", is_required=True)
    slot2 = LatentSlot(name="retries", value=3, data_type="integer", is_required=False)

    intent = LatentIntent(
        intent_id="INTENT_TEST_001",
        domain="access_governance",
        action="grant_permission",
        target_entity="BASE_SYNTH_025",
        slots={"user_id": slot1, "retries": slot2}
    )

    assert intent.intent_id == "INTENT_TEST_001"
    assert intent.get_required_slot_names() == ["user_id"]
    assert intent.get_slot_values() == {"user_id": "usr_981", "retries": 3}

    intent_dict = intent.to_dict()
    assert intent_dict["epistemic_provenance"] == "SYNTHETIC_LATENT_INTENT_REPRESENTATION"
    assert "intent_hash" in intent_dict

    restored = LatentIntent.from_dict(intent_dict)
    assert restored.intent_id == intent.intent_id
    assert restored.get_slot_values() == intent.get_slot_values()


def test_codec_roundtrip_on_base_contracts():
    contract_files = sorted(BASE_CONTRACTS_DIR.glob("BASE_SYNTH_*.json"))
    assert len(contract_files) == 40

    codec = StageCIntentCodec()

    for cf in contract_files:
        with open(cf, "r", encoding="utf-8") as f:
            contract = json.load(f)

        gold_examples = contract.get("gold_examples", [])
        assert len(gold_examples) >= 2

        for idx, gold_args in enumerate(gold_examples):
            intent = StageCIntentCodec.create_intent_from_contract_and_args(
                contract=contract,
                arguments=gold_args,
                intent_id=f"INTENT_{contract['contract_id']}_{idx}"
            )

            is_lossless, errors = codec.verify_lossless_roundtrip(intent)
            assert is_lossless is True, f"Roundtrip failed for {cf.name} gold {idx}: {errors}"


def test_nested_path_encoding_and_decoding():
    mapping_spec = {
        "intent_to_arg_path": {
            "cluster_id": "config.cluster_id",
            "enable_ssl": "config.security.enable_ssl"
        },
        "arg_to_intent_slot": {
            "config.cluster_id": "cluster_id",
            "config.security.enable_ssl": "enable_ssl"
        }
    }
    codec = StageCIntentCodec(mapping_spec)

    intent = LatentIntent(
        intent_id="INTENT_NESTED_01",
        domain="data_management",
        action="update_cluster",
        target_entity="BASE_SYNTH_029"
    )
    intent.add_slot("cluster_id", "cls_991", "string")
    intent.add_slot("enable_ssl", True, "boolean")

    args = codec.encode_intent_to_arguments(intent)
    assert args == {
        "config": {
            "cluster_id": "cls_991",
            "security": {
                "enable_ssl": True
            }
        }
    }

    decoded = codec.decode_arguments_to_intent(args, base_intent_template=intent)
    assert decoded.get_slot_values() == intent.get_slot_values()
