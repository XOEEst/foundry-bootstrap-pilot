from __future__ import annotations

import importlib.util
import os
import re
import sys
import tomllib
import unittest
from unittest.mock import patch
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

    def test_travel_approver_live_remote_settings_follow_sdk_pattern(self) -> None:
        module = load_module("agents/travel-approver-live/app/main.py")

        with patch.dict(
            os.environ,
            {
                "FOUNDRY_PROJECT_ENDPOINT": "https://luechen-eus2-foundry.services.ai.azure.com/api/projects/luechen-eus2-fdp",
                "FOUNDRY_MODEL_NAME": "gpt-4.1",
            },
            clear=True,
        ):
            settings = module.resolve_remote_settings()
            self.assertEqual(settings.project_endpoint, "https://luechen-eus2-foundry.services.ai.azure.com/api/projects/luechen-eus2-fdp")
            self.assertEqual(settings.model, "gpt-4.1")
            self.assertEqual(settings.agent_name, "travel-approver-live")
            self.assertEqual(settings.instructions, module.DEFAULT_REMOTE_INSTRUCTIONS)

        with patch.dict(
            os.environ,
            {
                "FOUNDRY_PROJECT_ENDPOINT": "https://luechen-eus2-foundry.services.ai.azure.com/api/projects/luechen-eus2-fdp",
                "AZURE_AI_MODEL_DEPLOYMENT_NAME": "gpt-4.1",
                "FOUNDRY_MODEL_NAME": "fallback-model",
                "AGENT_NAME": "travel-approver-live-managed",
                "AGENT_INSTRUCTIONS": "Approve only compliant travel.",
            },
            clear=True,
        ):
            settings = module.resolve_remote_settings()
            self.assertEqual(settings.model, "gpt-4.1")
            self.assertEqual(settings.agent_name, "travel-approver-live-managed")
            self.assertEqual(settings.instructions, "Approve only compliant travel.")

    def test_travel_approver_live_dependency_and_metadata_contract(self) -> None:
        pyproject = tomllib.loads((REPO_ROOT / "agents/travel-approver-live/pyproject.toml").read_text(encoding="utf-8"))
        dependencies = pyproject["project"]["dependencies"]
        self.assertIn("agent-framework-foundry==1.10.0", dependencies)
        self.assertIn("agent-framework-foundry-hosting>=1.0.0a260630", dependencies)
        self.assertIn("python-dotenv>=1.0.0", dependencies)

        requirements = (REPO_ROOT / "agents/travel-approver-live/requirements.txt").read_text(encoding="utf-8")
        self.assertIn("agent-framework-foundry==1.10.0", requirements)
        self.assertIn("agent-framework-foundry-hosting>=1.0.0a260630", requirements)
        self.assertIn("python-dotenv>=1.0.0", requirements)

        metadata = (REPO_ROOT / "agents/travel-approver-live/.foundry/agent-metadata.yaml").read_text(encoding="utf-8")
        self.assertIn("source_root: agents/travel-approver-live/app", metadata)
        self.assertIn("package_root: agents/travel-approver-live", metadata)
        self.assertIn("project_endpoint: https://luechen-eus2-foundry.services.ai.azure.com/api/projects/luechen-eus2-fdp", metadata)
        self.assertIn("foundry_account_resource_id: /subscriptions/7b43cfa1-da92-48cc-865d-5499466b3b5c/resourceGroups/luechen-eastus2/providers/Microsoft.CognitiveServices/accounts/luechen-eus2-foundry", metadata)
        self.assertIn("agent_name: foundry-opt-bootstrap-pilot-aligned", metadata)
        self.assertIn('expected_version: "4"', metadata)
        self.assertIn("project_endpoint_environment_variable: FOUNDRY_PROJECT_ENDPOINT", metadata)
        self.assertIn("primary_model_environment_variable: AZURE_AI_MODEL_DEPLOYMENT_NAME", metadata)
        self.assertIn("secondary_model_environment_variable: FOUNDRY_MODEL_NAME", metadata)
        self.assertIn("- AGENT_NAME", metadata)
        self.assertIn("- AGENT_INSTRUCTIONS", metadata)
        self.assertIn("deployment_name: gpt-4.1", metadata)
        self.assertIn("model_name: gpt-4.1", metadata)
        self.assertIn('model_version: "1"', metadata)
