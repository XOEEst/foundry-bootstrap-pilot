from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


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

    def test_bootstrap_managed_files_are_not_precreated(self) -> None:
        forbidden = (
            ".foundry-opt/registry.yaml",
            ".foundry-opt/bootstrap.lock.json",
            ".github/foundry-opt.lock.yml",
        )
        for relative_path in forbidden:
            with self.subTest(path=relative_path):
                self.assertFalse((REPO_ROOT / relative_path).exists())

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
