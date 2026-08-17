# Foundry bootstrap pilot repository

This repository is a deterministic local customer pilot used to exercise later bootstrap discovery, semantic patching, mocked E2E, and retained live bootstrap flows without pre-creating managed bootstrap artifacts.

## Pilot agent roots

| Root | Intended classification | Notes |
| --- | --- | --- |
| `agents/travel-approver-live` | `bound-aligned` live pilot target | Existing `.foundry/agent-metadata.yaml` points at a placeholder Foundry project and an exact expected version for later alignment checks. |
| `agents/claims-review-fixture` | `bound-diverged` / `bound-unknown` fixture | Existing metadata lets later mocked discovery supply either missing observed evidence (`bound-unknown`) or mismatched version/fingerprints (`bound-diverged`). |
| `services/policy-ready-unbound` | `ready-unbound` fixture | No existing `.foundry/agent-metadata.yaml`; discovery must rely on the Python entrypoint plus the multi-service `azure.yaml` contract. |

Every sample agent returns a local Responses-shaped envelope through an offline `invoke()` entrypoint so local tests can verify startup without cloud access.

## Local validation

Run the focused smoke suite from the repository root:

```powershell
python -m unittest discover -s tests -v
```

The suite verifies that each pilot agent imports, exposes the Responses protocol markers, starts locally, and that the unrelated customer-owned instructions, skill, workflows, and reserved setup workflow remain present. It also confirms that bootstrap-managed files such as `.foundry-opt/registry.yaml`, `.foundry-opt/bootstrap.lock.json`, and `.github/foundry-opt.lock.yml` do not exist yet.
