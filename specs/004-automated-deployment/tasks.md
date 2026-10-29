# Tasks: Automated Raspberry Pi Deployment

**Input**: Design documents from `specs/004-automated-deployment/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

## Phase 1: Setup

- [X] T001 Add the feature deployment contract and generated artifact paths to `pyproject.toml` or the existing packaging configuration.
- [X] T002 [P] Add fake command/transport fixtures for deployment tests in `tests/fakes/deployment.py`.
- [X] T003 [P] Add deployment test markers and shared redaction assertions in `tests/deployment/conftest.py`.

## Phase 2: Foundational

- [X] T004 Implement a bounded, injectable command/file transport with non-zero and timeout errors in `src/leolm/deployment/transport.py`.
- [X] T005 [P] Implement redaction of API keys, Wi-Fi passwords, tokens, and secret-like values for messages and JSON reports in `src/leolm/deployment/report.py`.
- [X] T006 [P] Extend profile validation for target user/host/port, architecture strategy, configurable model/audio/wake-word fields, and safe field-only errors in `src/leolm/deployment/profile.py`.
- [X] T007 Build a shared managed-file manifest and idempotent deployment plan in `src/leolm/deployment/manifest.py`, including explicit owner/mode and secret classification.
- [X] T008 Update renderers in `src/leolm/deployment/render.py`, `src/leolm/deployment/network.py`, and `src/leolm/deployment/service.py` so generated files have no hard-coded device names and include network/bootstrap ordering.
- [X] T009 Add unit tests for transport failures, profile validation, manifest convergence, renderer escaping, file modes, and redaction in `tests/deployment/test_foundation.py`.

## Phase 3: User Story 1 - Deploy a target from a PC (P1) MVP

**Goal**: A valid profile and one SSH command provision the complete target, install target-compatible dependencies, enable LeoLM at boot, and clean secrets.

**Independent Test**: Use the fake SSH transport to run deployment twice and assert complete payload, target-side install commands, service state, no duplicate units, cleanup, and no secret in output.

- [X] T010 [P] [US1] Add fake SSH contract tests for complete payload transfer, target architecture discovery, timeout, non-zero command, idempotent rerun, and secret cleanup in `tests/deployment/test_ssh_provisioner.py`.
- [X] T011 [US1] Refactor `src/leolm/deployment/ssh.py` to use the shared transport and manifest, transfer the application payload, render protected env/Wi-Fi files, install target-side dependencies, and configure managed systemd units.
- [X] T012 [US1] Add explicit SSH preflight checks for systemd, NetworkManager, venv/pip, sudo capability, target architecture, storage, and network prerequisites in `src/leolm/deployment/ssh.py`.
- [X] T013 [US1] Implement failure cleanup and safe retry/rollback reporting for remote temporary archives and secret files in `src/leolm/deployment/ssh.py`.
- [X] T014 [US1] Update `scripts/leolm-deploy.py` so `deploy-ssh` exposes the complete one-command flow, bounded timeout/options, redacted JSON, and stable failure exit codes.
- [X] T015 [US1] Add end-to-end fake-target tests for `deploy-ssh`, repeat deployment, and CLI redaction in `tests/deployment/test_cli_deploy.py`.

## Phase 4: User Story 2 - Prepare an offline image (P2)

**Goal**: Offline staging creates an equivalent first-boot deployment without running target binaries on the PC.

**Independent Test**: Stage twice into temporary roots and inspect application files, bootstrap marker, systemd units, Wi-Fi permissions, and no host `.venv` copied to the target.

- [X] T016 [P] [US2] Add offline staging tests for foreign architecture, first-boot bootstrap, protected files, atomic commit, rollback, and idempotency in `tests/deployment/test_offline_provisioner.py`.
- [X] T017 [US2] Refactor `src/leolm/deployment/offline.py` to consume the shared manifest, copy the complete runtime payload, and defer incompatible dependency installation to first boot.
- [X] T018 [US2] Implement target-side bootstrap actions for user creation, venv/dependency installation, Wi-Fi activation, service enablement, marker update, and cleanup in `src/leolm/deployment/render.py` and `src/leolm/deployment/service.py`.
- [X] T019 [US2] Ensure offline staging applies explicit ownership/modes where possible and records privileged first-boot actions without claiming they ran in `src/leolm/deployment/offline.py`.
- [X] T020 [US2] Extend `scripts/leolm-deploy.py provision-offline` and `verify` to report staged, bootstrap-pending, and committed states without exposing profile secrets.

## Phase 5: User Story 3 - Validate and inspect deployment safely (P3)

**Goal**: Operators can validate, dry-run, and distinguish deployment health states before or after mutation.

**Independent Test**: Run CLI commands against valid/invalid profiles and fake offline/SSH targets; assert stable statuses, exit codes, and redacted output.

- [X] T021 [P] [US3] Add contract tests for validate, dry-run, verify states, invalid secrets, and JSON schema in `tests/deployment/test_cli_contract.py`.
- [X] T022 [US3] Implement a redacted dry-run plan from the shared manifest in `scripts/leolm-deploy.py` and `src/leolm/deployment/manifest.py`.
- [X] T023 [US3] Expand `src/leolm/deployment/verify.py` to distinguish not-installed, bootstrap-pending, service-failed, network-unavailable, and healthy states for offline and SSH targets.
- [X] T024 [US3] Add explicit documentation/privacy/service dependency coverage and exact command examples in `docs/deployment.md`, `docs/configuration.md`, `docs/troubleshooting.md`, and `readme.md`.
- [X] T025 [US3] Make `scripts/check_docs.py` validate deployment options, profile fields, and documented states against the implementation in `tests/documentation/test_deployment_docs.py`.

## Phase 6: Polish and validation

- [X] T026 [P] Update `deploy/profiles/example.env` and `.gitignore` to keep real profiles/secrets out of version control and expose all configurable target/model/audio/wake-word fields.
- [X] T027 [P] Add a release checklist for the real Raspberry Pi smoke test, reboot/autostart, Wi-Fi reconnection, microphone/speaker lifecycle, and online-service privacy acceptance in `docs/release-checklist.md`.
- [X] T028 Run the full pytest suite, documentation validator, CLI dry-run, and temporary-root quickstart; fix any mismatch between generated artifacts and actual behavior.
- [X] T029 Confirm the current voice runtime tests remain unchanged and pass, and document the physical Raspberry Pi validation still required before release.

## Dependencies & Execution Order

- Phase 1 has no dependencies.
- Phase 2 depends on Phase 1 and blocks all user stories.
- US1, US2, and US3 depend on Phase 2; US2/US3 reuse US1 contracts but remain independently testable through fakes.
- Phase 6 depends on all implementation phases.

## Parallel Opportunities

- T002/T003 can run in parallel; T005/T006/T008 can run in parallel after the initial package inspection.
- T010 and T016 and T021 are independent test groups once shared fixtures exist.
- T024/T026/T027 can run in parallel after CLI contracts stabilize.

## Implementation Strategy

Deliver US1 as the MVP first: complete SSH deployment and prove it with a fake target. Then complete offline first-boot staging, then verification/documentation. No task changes the voice conversation behavior or adds MCP tools.
