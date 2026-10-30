---
description: "Task list for Offline Panda Wake Word implementation"
---

# Tasks: Offline Panda Wake Word

**Input**: Design documents from specs/005-offline-wakeword/

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/runtime-configuration.md, quickstart.md

**Tests**: Required. The specification requires isolated automated coverage and opt-in hardware verification.

**Organization**: Tasks are grouped by user story so each increment can be implemented and tested independently.

## Format: ID, parallel marker, story label, description

- **[P]**: Can run in parallel because it changes a different file with no unmet dependency.
- **[USn]**: Maps to a user story in spec.md.
- Every task names its target file path.

## Phase 1: Setup

**Purpose**: Establish the pinned public-asset and dependency baseline.

- [X] T001 Record the official Vosk 0.3.45 ARM64 package and Italian model source metadata in deploy/assets/vosk-model-small-it-0.22.lock.json.
- [X] T002 [P] Add a failing deployment-asset test fixture and integrity expectations in tests/deployment/test_vosk_asset.py.
- [X] T003 [P] Add a failing fake-recognizer and microphone-frame test scaffold in tests/unit/test_wakeword.py.

---

## Phase 2: Foundational

**Purpose**: Shared configuration, dependency, and verified-asset plumbing that blocks all stories.

- [X] T004 Replace the Picovoice package requirement with the pinned Vosk requirement in requirements.txt and update dependency-install assertions in tests/integration/test_installation.py.
- [X] T005 Update runtime configuration parsing and validation in src/leolm/config.py so wake_word is non-empty, vosk_model_path is a readable complete model directory, and wake_sample_rate is positive; remove Picovoice-specific validation.
- [X] T006 Update configuration coverage in tests/unit/test_config.py and tests/unit/test_configuration_contract.py for missing/unreadable model paths, non-positive sample rates, and safe errors without secret values.
- [X] T007 Update deployment profile validation and runtime environment rendering in src/leolm/deployment/profile.py and src/leolm/deployment/render.py to remove LEOLM_PORCUPINE_ACCESS_KEY, LEOLM_WAKE_WORD_PATH, and LEOLM_WAKE_MODEL_PATH and add LEOLM_VOSK_MODEL_PATH and LEOLM_WAKE_SAMPLE_RATE.
- [X] T008 Update deploy/profiles/example.env and tests/deployment/test_profile_validation.py so a valid profile requires no Picovoice field and exposes no placeholder or secret value in validation output.
- [X] T009 Implement PC-side acquisition, SHA-256 verification, archive-size bounds, and safe cleanup for the locked Italian model in scripts/fetch-vosk-model.py.
- [X] T010 Add deterministic acquisition, hash-mismatch, malformed-archive, and redaction tests in tests/deployment/test_vosk_asset.py using local fixture archives only.

**Checkpoint**: Configuration accepts only a valid local model contract, and a verified public model asset can be acquired without exposing secrets.

---

## Phase 3: User Story 1 - Activate LeoLM offline with Panda (Priority: P1) MVP

**Goal**: Detect the configured wake word locally from the selected microphone without a Picovoice key or internet access.

**Independent Test**: Use fake Vosk and audio adapters to feed 16 kHz PCM frames representing Panda, assert exactly one activation, and verify that no remote call or credential is needed for activation.

### Tests for User Story 1

- [X] T011 [P] [US1] Add fake Vosk model/recognizer tests for exact normalized partial and final Panda activation in tests/unit/test_wakeword.py.
- [X] T012 [US1] Add tests for incorrect phrase, short PCM frame, recognizer initialization failure, microphone read failure, and idempotent stream cleanup in tests/unit/test_wakeword.py.
- [X] T013 [P] [US1] Add voice-lifecycle integration tests proving wake-word activation remains independent of model, command recognition, and TTS dependencies in tests/integration/test_voice_flow.py.

### Implementation for User Story 1

- [X] T014 [US1] Replace PorcupineWakeWord with the Vosk-backed local wake-word adapter in src/leolm/wakeword.py; open a configured 16 kHz mono input stream, constrain recognition to the normalized wake word, and return one activation only on exact match.
- [X] T015 [US1] Preserve explicit ResourceLease ownership and idempotent cleanup for the recognizer and input stream in src/leolm/wakeword.py.
- [X] T016 [US1] Wire the local wake-word configuration and adapter into src/leolm/cli.py without changing the subsequent command-recognition, conversation, or TTS flow.
- [X] T017 [US1] Remove Porcupine imports, assets, and obsolete configuration references from src/leolm/__init__.py, openai_request.py, and repository asset locations if present.
- [X] T018 [US1] Run pytest -q and fix only failures attributable to src/leolm/wakeword.py, src/leolm/config.py, src/leolm/cli.py, tests/unit/test_wakeword.py, and tests/integration/test_voice_flow.py.

**Checkpoint**: With fakes, LeoLM enters command capture only after the local exact Panda result and has no Picovoice dependency.

---

## Phase 4: User Story 2 - Deploy the offline language asset reproducibly (Priority: P2)

**Goal**: Install the same verified local Italian model through SSH and offline provisioning before the service is enabled.

**Independent Test**: Stage a fake verified archive through each transport and assert one readable model directory, matching digest record, no runtime download step, and a safe integrity failure when the archive is altered.

### Tests for User Story 2

- [X] T019 [P] [US2] Add SSH payload staging and service-enable ordering tests in tests/deployment/test_automated_deployment.py and tests/deployment/test_service_unit.py.
- [X] T020 [P] [US2] Add offline payload and first-boot integrity tests in tests/deployment/test_offline_provisioning.py and tests/deployment/test_bootstrap.py.

### Implementation for User Story 2

- [X] T021 [US2] Extend src/leolm/deployment/manifest.py to include only the verified extracted Vosk model and lock record in the managed payload, with no Porcupine assets.
- [X] T022 [US2] Extend scripts/leolm-deploy.py and src/leolm/deployment/ssh.py to acquire/verify the model on the PC, transfer it with the payload, validate target Vosk import, and enable the service only after asset validation.
- [X] T023 [US2] Extend src/leolm/deployment/offline.py and src/leolm/deployment/render.py so first boot consumes the staged verified asset without redownloading it and removes temporary archives on success or failure.
- [X] T024 [US2] Extend src/leolm/deployment/verify.py and tests/deployment/test_sanitized_reports.py with redacted wakeword_asset and wakeword_runtime statuses.

**Checkpoint**: SSH and offline provisioning converge on one verified local model and one enabled service, while corrupt assets prevent readiness.

---

## Phase 5: User Story 3 - Recover safely from audio or asset failures (Priority: P3)

**Goal**: Report safe, actionable failures for missing assets or microphone issues without leaking credentials or retaining resources.

**Independent Test**: Start with an absent/incomplete model and an unavailable input device; assert a safe error, closed stream/recognizer, and a non-healthy verification result.

### Tests for User Story 3

- [X] T025 [P] [US3] Add missing/incomplete model and unavailable input-device regression tests in tests/unit/test_wakeword.py and tests/unit/test_resources.py.
- [X] T026 [P] [US3] Add service failure and redacted readiness-report tests in tests/deployment/test_boot_recovery.py and tests/deployment/test_sanitized_reports.py.

### Implementation for User Story 3

- [X] T027 [US3] Normalize safe model, recognizer, stream, and device errors and release all owned resources in src/leolm/wakeword.py and src/leolm/errors.py.
- [X] T028 [US3] Report unavailable or invalid wake-word asset/runtime states without raw paths, archive contents, or secret values in src/leolm/deployment/verify.py and src/leolm/deployment/report.py.

**Checkpoint**: Hardware and asset faults cannot be mistaken for a healthy voice service and leave no stream or recognizer open.

---

## Phase 6: Polish and Cross-Cutting Validation

**Purpose**: Align documentation, remove obsolete public surface, and prove the complete flow.

- [X] T029 [P] Update README.md, readme.md, docs/configuration.md, docs/deployment.md, docs/system-dependencies.md, and docs/troubleshooting.md for account-free Vosk wake word, verified model provisioning, and correct Pi 3/Zero 2 W limits.
- [X] T030 [P] Update tests/documentation/test_configuration_contract.py, tests/documentation/test_operational_docs.py, and scripts/check_docs.py expectations for the new configuration contract.
- [X] T031 Remove obsolete Porcupine packages, assets, fixtures, and hardware tests from requirements.txt, deploy/profiles/example.env, tests/hardware/test_porcupine.py, and repository asset locations.
- [X] T032 Run pytest -q, pytest tests/documentation -q, python scripts/check_docs.py --root ., and git diff --check; resolve all Vosk migration regressions.
- [ ] T033 Run the opt-in Pi 3 verification in tests/hardware/test_audio_devices.py, tests/hardware/test_audio_playback.py, and a new tests/hardware/test_vosk_wakeword.py; require at least 18 activations in 20 Panda attempts, at most one false activation in 10 idle minutes, p95 activation latency at most 2 seconds, resident memory at most 650 MiB, no OOM or sustained swap, and record service start, offline activation, command, synthesis, and playback outcomes in specs/005-offline-wakeword/quickstart.md.

---

## Dependencies and Execution Order

- Phase 1 has no dependencies.
- Phase 2 depends on T001–T003 and blocks all user stories.
- US1 depends on Phase 2 and is the MVP.
- US2 depends on T009–T010 and the configured model path from Phase 2; it may begin after Phase 2 but must integrate with the completed US1 contract before final validation.
- US3 depends on Phase 2 and can proceed alongside US1 or US2 once their shared error surface is stable.
- Phase 6 depends on all desired user stories.

## Parallel Opportunities

- T002 and T003 can run in parallel.
- T011 and T013 can run in parallel before T014; T012 follows T011 because both modify tests/unit/test_wakeword.py.
- T019 and T020 can run in parallel.
- T025 and T026 can run in parallel.
- T029 and T030 can run in parallel after the contract is stable.

## Parallel Example: User Story 1

    Task: T011 — fake Vosk model/recognizer tests in tests/unit/test_wakeword.py
    Task: T013 — lifecycle integration tests in tests/integration/test_voice_flow.py

T012 follows T011 because both modify the same test file; T013 can proceed independently.

## Implementation Strategy

### MVP first

1. Complete Phase 1 and Phase 2.
2. Complete T011–T018 for US1.
3. Run the isolated suite and demonstrate fake local Panda activation.
4. Stop before deployment if the model asset or Pi target import check fails.

### Incremental delivery

1. Deliver US1 with fakes and configuration validation.
2. Add US2 to make the verified model deployable by SSH and offline staging.
3. Add US3 safe diagnostics and recovery.
4. Complete Phase 6 only after the full Pi 3 hardware flow has been observed.

### Format validation

All 33 tasks use the required checkbox, sequential ID, optional parallel marker, story label for story tasks, and explicit repository file path.

