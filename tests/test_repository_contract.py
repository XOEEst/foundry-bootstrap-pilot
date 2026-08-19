from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNTIME_SHA = "ec2287506c6e6e3537f71127ead4051182b70a98"
ACTIVATION_RUNTIME_SHA = "5f03a9188eb720489404980458d94fb3c353469c"


class RepositoryContractTests(unittest.TestCase):
    def test_unrelated_customer_owned_files_exist(self) -> None:
        required = (
            ".github/copilot-instructions.md",
            ".github/workflows/customer-docs-check.yml",
            ".github/workflows/copilot-setup-steps.yml",
            "skills/customer-release-digest/SKILL.md",
            "README.md",
            "azure.yaml",
        )
        for relative_path in required:
            with self.subTest(path=relative_path):
                self.assertTrue((REPO_ROOT / relative_path).exists())

    def test_bootstrap_managed_files_match_the_committed_lock(self) -> None:
        lock_path = REPO_ROOT / ".foundry-opt/bootstrap.lock.json"
        self.assertTrue(lock_path.exists())
        lock = json.loads(lock_path.read_text(encoding="utf-8"))
        self.assertEqual(lock["runtime_commit"], RUNTIME_SHA)
        self.assertEqual(lock["last_activation"]["outcome"], "succeeded")

        for entry in lock["managed_files"]:
            relative_path = entry["path"]
            with self.subTest(path=relative_path):
                managed_path = REPO_ROOT / relative_path
                self.assertTrue(managed_path.exists())
                digest = hashlib.sha256(managed_path.read_bytes()).hexdigest()
                self.assertEqual(digest, entry["applied_sha256"])

        self.assertFalse((REPO_ROOT / ".github/foundry-opt.lock.yml").exists())

    def test_stable_runtime_pin_preserves_the_live_activation(self) -> None:
        pin_locations = (
            ".foundry-opt/registry.yaml",
            ".github/workflows/copilot-setup-steps.yml",
            ".github/workflows/foundry-opt-validation.yml",
            ".github/workflows/foundry-opt-deploy.yml",
        )
        for relative_path in pin_locations:
            with self.subTest(path=relative_path):
                self.assertIn(
                    RUNTIME_SHA,
                    (REPO_ROOT / relative_path).read_text(encoding="utf-8"),
                )

        registry = (REPO_ROOT / ".foundry-opt/registry.yaml").read_text(encoding="utf-8")
        self.assertIn(
            "oidc_subject_prefix: repo:XOEEst@18523445/foundry-bootstrap-pilot@1337678711",
            registry,
        )
        self.assertRegex(
            registry,
            r"agent_id: travel-approver-live[\s\S]*?enabled: true",
        )
        sidecar = (
            REPO_ROOT / "agents/travel-approver-live/.foundry/foundry-opt.yaml"
        ).read_text(encoding="utf-8")
        self.assertIn(
            "operation_id: pilot-evaluation-in-domain-20260818",
            sidecar,
        )
        self.assertIn(f"runtime_commit: {ACTIVATION_RUNTIME_SHA}", sidecar)

    def test_setup_workflow_keeps_customer_steps_around_reserved_slots(self) -> None:
        workflow = (REPO_ROOT / ".github/workflows/copilot-setup-steps.yml").read_text(encoding="utf-8")
        customer_pre = workflow.index("id: customer-preflight")
        managed_checkout = workflow.index("id: foundry-opt-checkout")
        managed_bootstrap = workflow.index("id: foundry-opt-bootstrap")
        customer_post = workflow.index("id: customer-postflight")
        self.assertLess(customer_pre, managed_checkout)
        self.assertLess(managed_checkout, managed_bootstrap)
        self.assertLess(managed_bootstrap, customer_post)

    def test_readme_and_azure_contract_list_all_three_roots(self) -> None:
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        azure = (REPO_ROOT / "azure.yaml").read_text(encoding="utf-8")
        for root_marker in (
            "agents/travel-approver-live",
            "agents/claims-review-fixture",
            "services/policy-ready-unbound",
        ):
            with self.subTest(root=root_marker):
                self.assertIn(root_marker, readme)
                self.assertIn(root_marker.rsplit("/", 1)[-1], azure)
