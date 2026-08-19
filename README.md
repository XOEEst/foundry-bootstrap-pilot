# Foundry bootstrap pilot repository

This repository is the retained customer pilot for bootstrap discovery, semantic patching, mocked E2E, and live Foundry validation. Its managed bootstrap contract is committed at an exact reviewed runtime SHA while operation journals and local receipts remain untracked.

## Pilot agent roots

| Root | Intended classification | Notes |
| --- | --- | --- |
| `agents/travel-approver-live` | `bound-aligned` and active | Bound to retained hosted agent `foundry-opt-bootstrap-pilot-aligned:4`; its receipt-derived evaluation sidecar is deployment-enabled. |
| `agents/claims-review-fixture` | `bound-unknown` fixture and inactive | Existing metadata remains available for unknown/diverged discovery coverage, but the root is disabled in the registry. |
| `services/policy-ready-unbound` | `ready-unbound` fixture and inactive | No Foundry binding is provisioned, so the root remains disabled. |

Every sample agent returns a local Responses-shaped envelope through an offline `invoke()` entrypoint so local tests can verify startup without cloud access.

## Retained acceptance status

- Runtime pin: `6f6e5249356b4680184cd4b3376b60c33b2fa4fb`
- Validation: [run 32258753039](https://github.com/XOEEst/foundry-bootstrap-pilot/actions/runs/32258753039) passed
- Preserved Copilot setup: [run 32258753085](https://github.com/XOEEst/foundry-bootstrap-pilot/actions/runs/32258753085) passed
- Evaluation activation: `travel-approver-live` enabled with a deterministic 20/10 split and all five required safety evaluators
- Live agent: `foundry-opt-bootstrap-pilot-aligned:4` remains routed at 100%

Merge publication is blocked before any Foundry mutation by Microsoft Entra
error `AADSTS7002381`. This tenant requires a GitHub OIDC `enterprise` claim of
`microsoft`, `github`, or `microsoftopensource`; the personal `XOEEst`
repository emits an empty claim. The runtime fails closed and does not use
static Azure credentials, broaden RBAC, create another version, or mutate the
route.

## Local validation

Run the focused smoke suite from the repository root:

```powershell
python -m unittest discover -s tests -v
```

The suite verifies that each pilot agent imports, exposes the Responses protocol markers, starts locally, and that unrelated customer-owned instructions, skills, workflows, and setup steps remain present. It also validates every committed managed-file digest, the stable runtime pin, and the retained activation binding.
