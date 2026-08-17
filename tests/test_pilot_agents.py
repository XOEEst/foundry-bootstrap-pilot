from __future__ import annotations

import importlib.util
import re
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
AGENTS = (
    {
        "root": "agents/travel-approver-live",
        "module_path": "agents/travel-approver-live/app/main.py",
        "agent_id": "travel-approver-live",
        "expected_phrase": "Travel approval pilot ready.",
        "expects_metadata": True,
    },
    {
        "root": "agents/claims-review-fixture",
        "module_path": "agents/claims-review-fixture/app/main.py",
        "agent_id": "claims-review-fixture",
        "expected_phrase": "Claims review fixture ready.",
        "expects_metadata": True,
    },
    {
        "root": "services/policy-ready-unbound",
        "module_path": "services/policy-ready-unbound/main.py",
        "agent_id": "policy-ready-unbound",
        "expected_phrase": "Policy helper fixture ready.",
        "expects_metadata": False,
    },
)


def load_module(relative_path: str):
    path = REPO_ROOT / relative_path
    name = "pilot_" + re.sub(r"[^0-9a-zA-Z_]+", "_", relative_path)
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"Unable to load module from {relative_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class PilotAgentTests(unittest.TestCase):
    def test_agents_import_start_and_respond_locally(self) -> None:
        payload = {
            "input": [
                {
                    "role": "user",
                    "content": [{"type": "input_text", "text": "pilot ping"}],
                }
            ]
        }
        for agent in AGENTS:
            with self.subTest(agent=agent["agent_id"]):
                module = load_module(agent["module_path"])
                app = module.build_local_app()
                started = app.start()
                self.assertEqual(started["agent_id"], agent["agent_id"])
                self.assertEqual(started["protocol_name"], "responses")
                self.assertEqual(started["protocol_version"], "2.0.0")
                response = module.invoke(payload)
                self.assertEqual(response["protocol"]["name"], "responses")
                self.assertEqual(response["protocol"]["version"], "2.0.0")
                self.assertIn(agent["expected_phrase"], response["output_text"])
                self.assertIn("pilot ping", response["output_text"])

    def test_metadata_presence_matches_intended_classification(self) -> None:
        for agent in AGENTS:
            with self.subTest(agent=agent["agent_id"]):
                metadata_path = REPO_ROOT / agent["root"] / ".foundry" / "agent-metadata.yaml"
                self.assertEqual(metadata_path.exists(), agent["expects_metadata"])
