# Tasks: Stabilize Voice Assistant

**Input**: Design documents from `/specs/001-stabilize-voice-assistant/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

**Organization**: Tasks are grouped by user story. Every story has an independent validation path;
cross-story dependencies are explicit below.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Preparare la struttura del package, l'installazione riproducibile e i comandi di test.

- [X] T001 Create the `src/leolm/`, `tests/unit/`, `tests/integration/`, `tests/hardware/`, `docs/`, and `examples/` directories and package markers in `src/leolm/__init__.py`.
- [X] T002 [P] Replace the unversioned dependency ranges in `requirements.txt` with the supported runtime dependency set from `plan.md`, add `SpeechRecognition`, and remove unused `openai` and `vosk` entries.
- [X] T003 [P] Add the development and test dependency definition for `pytest` in `requirements-dev.txt` and document the supported Python baseline in `pyproject.toml`.
- [X] T004 [P] Add the non-secret environment example and variable comments from the configuration contract in `examples/.env.example`.
- [X] T005 [P] Add project test discovery, markers, and hardware-test exclusion defaults in `pytest.ini`.
- [X] T006 [P] Add the supported Linux audio and codec prerequisites, including ALSA/PortAudio, FLAC, and the configured player, to `docs/system-dependencies.md`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Creare i contratti condivisi prima dell'implementazione delle user story.

**Checkpoint**: Nessuna user story deve iniziare prima del completamento della configurazione,
degli errori sanitizzati e dell'infrastruttura di test fake.

- [X] T007 Implement immutable environment loading, typed defaults, and validation for every field in `specs/001-stabilize-voice-assistant/contracts/configuration.md` in `src/leolm/config.py`.
- [X] T008 [P] Define sanitized domain errors and safe user-facing error conversion in `src/leolm/errors.py`.
- [X] T009 [P] Define lifecycle protocols for audio, wake word, speech recognition, conversation, and TTS adapters in `src/leolm/ports.py`.
- [X] T010 [P] Build deterministic fake adapters for network, wake word, speech recognition, audio, and TTS in `tests/fakes/`.
- [X] T011 [P] Add shared fixtures for fake environment variables, monotonic time, temporary files, and cleanup assertions in `tests/conftest.py`.
- [X] T012 Add import-safe package entry points that do not initialize hardware or network at import time in `src/leolm/__init__.py` and `src/leolm/cli.py`.

---

## Phase 3: User Story 1 - Avvio sicuro e installazione riproducibile (Priority: P1) 🎯 MVP

**Goal**: Installare e avviare LeoLM con dipendenze dichiarate, configurazione validata e nessuna
esposizione di credenziali.

**Independent Test**: In un ambiente senza hardware e con chiavi `test-only`, eseguire la procedura
documentata, avviare il bootstrap e verificare errori sanitizzati, dipendenze dichiarate e assenza
dei valori segreti nell'output.

### Tests for User Story 1

- [X] T013 [P] [US1] Add configuration validation tests for missing, malformed, out-of-range, and valid environment values in `tests/unit/test_config.py`.
- [X] T014 [P] [US1] Add secret-sanitization tests covering startup, configuration errors, network errors, and unexpected exceptions in `tests/unit/test_security.py`.
- [X] T015 [P] [US1] Add a clean-environment installation smoke test that verifies declared Python and system prerequisites without invoking `sudo` in `tests/integration/test_installation.py`.

### Implementation for User Story 1

- [X] T016 [US1] Implement startup configuration loading, required-secret checks, and sanitized diagnostics in `src/leolm/cli.py` using `src/leolm/config.py` and `src/leolm/errors.py`.
- [X] T017 [US1] Replace the runtime package installer in `setup.py` with a non-mutating compatibility entry point or remove it and document the supported `venv`/pip workflow in `README.md`.
- [X] T018 [US1] Add a reproducible installation check and supported Python/dependency matrix to `README.md` and `docs/system-dependencies.md`.
- [X] T019 [US1] Add startup and failure-path logging rules that redact credential values and request payloads in `src/leolm/logging.py`.

**Checkpoint**: A clean machine can validate configuration and installation without hardware, network
access, elevated privileges, or secret leakage.

---

## Phase 4: User Story 2 - Configurare il dispositivo vocale (Priority: P1)

**Goal**: Configurare modello, lingua, wake word, asset e dispositivi audio senza cambiare il codice,
con ownership e cleanup deterministici.

**Independent Test**: Usare fake audio/wake-word adapters e due configurazioni con selettori diversi;
verificare risoluzione, validazione, fallback d'errore e rilascio di ogni risorsa.

### Tests for User Story 2

- [X] T020 [P] [US2] Add configuration-contract tests for model, language, wake-word paths, input/output selectors, timeout, retry, and 600-second context defaults in `tests/unit/test_configuration_contract.py`.
- [X] T021 [P] [US2] Add audio-device resolution tests for name/identifier selection, changing hardware indices, missing devices, busy devices, and disconnects in `tests/unit/test_audio.py`.
- [X] T022 [P] [US2] Add wake-word adapter tests for configurable keyword and asset paths without loading Porcupine in `tests/unit/test_wakeword.py`.
- [X] T023 [P] [US2] Add resource-lease tests proving idempotent release after success, exception, and interruption in `tests/unit/test_resources.py`.

### Implementation for User Story 2

- [X] T024 [US2] Implement audio-device discovery, selector matching, sample-rate validation, stream ownership, and idempotent cleanup in `src/leolm/audio.py`.
- [X] T025 [US2] Implement the configurable wake-word adapter, asset validation, callback lifecycle, and Porcupine cleanup in `src/leolm/wakeword.py`.
- [X] T026 [US2] Implement speech-recognition adapter configuration for language, input device, listen timeout, and phrase limit in `src/leolm/speech.py`.
- [X] T027 [US2] Implement TTS output creation, configurable output selection, temporary-file ownership, player process cleanup, and failure handling in `src/leolm/tts.py`.
- [X] T028 [US2] Replace hard-coded device names, indices, wake words, asset paths, sample rates, and `hw:1,0` usage in `src/leolm/audio.py`, `src/leolm/wakeword.py`, `src/leolm/speech.py`, and `src/leolm/tts.py`.
- [X] T029 [US2] Route the existing entry point through the new configurable adapters while preserving the current wake-word and Italian voice flow in `openai_request.py` and `src/leolm/cli.py`.

**Checkpoint**: The voice hardware can be selected through environment configuration, and every audio
or wake-word resource is released on normal and exceptional exits.

---

## Phase 5: User Story 3 - Conversazione vocale invariata e resiliente (Priority: P1)

**Goal**: Mantenere il flusso vocale, aggiungendo retry limitati, contesto temporaneo e gestione
esplicita degli errori remoti.

**Independent Test**: Eseguire una sessione con fake adapters, verificare risposta, contesto entro
10 minuti, scadenza del contesto, 3 tentativi massimi e ritorno alla wake word dopo errore.

### Tests for User Story 3

- [X] T030 [P] [US3] Add remote-service tests for timeout, connection, HTTP, invalid-payload, rate-limit, retry-backoff, and sanitized user messages in `tests/unit/test_llm.py`.
- [X] T031 [P] [US3] Add conversation-context tests for turn ordering, context reuse, 600-second inactivity expiry, timer reset, and in-flight expiry behavior in `tests/unit/test_session.py`.
- [X] T032 [P] [US3] Add voice-session state-machine tests for wake detection, listening, recognition, request, speaking, failure, cleanup, and return to idle in `tests/integration/test_voice_session.py`.
- [X] T033 [P] [US3] Add regression tests proving the Italian wake-word → command → model → spoken-response sequence using only fake adapters in `tests/integration/test_voice_flow.py`.

### Implementation for User Story 3

- [X] T034 [US3] Implement normalized remote-service results, timeout classification, sanitized payload handling, and maximum 3-attempt exponential backoff in `src/leolm/llm.py`.
- [X] T035 [US3] Implement in-memory conversation turns, monotonic inactivity timer, 600-second default, timer reset, and safe expiry after an in-flight turn in `src/leolm/session.py`.
- [X] T036 [US3] Implement the voice-session coordinator and lifecycle transitions from `contracts/voice-session.md` in `src/leolm/session.py` and `src/leolm/cli.py`.
- [X] T037 [US3] Ensure remote failure releases audio/TTS leases and returns to wake-word listening after the third attempt in `src/leolm/cli.py`.
- [X] T038 [US3] Remove global initialization and direct network/audio side effects from `openai_request.py`, retaining it as a compatibility launcher for `src/leolm/cli.py`.

**Checkpoint**: The current vocal interaction works with fake adapters, retry behavior is bounded, and
context is temporary and expires deterministically.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Allineare documentazione, test hardware e controlli finali ai comportamenti implementati.

- [X] T039 [P] Add privacy, data-flow, local-retention, and external-service policy documentation in `docs/privacy.md`.
- [X] T040 [P] Refactor existing hardware-dependent scripts into explicit opt-in tests without `sudo` or package installation in `tests/hardware/test_audio_devices.py` and `tests/hardware/test_audio_playback.py`.
- [X] T041 [P] Update Porcupine hardware validation to use configured asset and wake-word values in `tests/hardware/test_porcupine.py`.
- [X] T042 [P] Rewrite `readme.md` to match the voice assistant behavior, configuration contract, installation workflow, privacy boundary, troubleshooting, and test commands.
- [X] T043 [P] Remove unused imports, duplicate initialization, broad exception handling, shell-string process execution, and hard-coded response paths in `src/leolm/` and `openai_request.py`.
- [X] T044 Run the full automatic suite, secret scan, packaging/install check, and `quickstart.md` validation; record any Raspberry Pi-specific deviations in `docs/system-dependencies.md`.
- [ ] T045 Run the opt-in hardware suite on equivalent Raspberry Pi hardware and document detected device selectors and sample-rate compatibility in `docs/system-dependencies.md`.

> T045 richiede un Raspberry Pi Zero 2 W con ALSA, microfono, speaker e asset Porcupine; resta
> intenzionalmente pendente finché l'hardware non è disponibile.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 Setup**: No dependencies; T001–T006 can proceed in parallel where files do not overlap.
- **Phase 2 Foundational**: Depends on T001–T005; T007–T012 block all user stories.
- **Phase 3 US1**: Depends on Phase 2; delivers the MVP installation and security baseline.
- **Phase 4 US2**: Depends on Phase 2 and T016; can proceed in parallel with the later US1 documentation tasks.
- **Phase 5 US3**: Depends on T009–T012 and the adapter contracts; T034–T038 integrate US2 adapters.
- **Phase 6 Polish**: Depends on all desired user stories; T039–T043 can run in parallel, then T044–T045 validate.

### User Story Dependencies

- **US1 (P1)**: Depends only on Foundational; independent MVP.
- **US2 (P1)**: Depends on Foundational and the startup/configuration contract from US1; independently testable with fake adapters.
- **US3 (P1)**: Depends on the adapter contracts and US2 lifecycle interfaces; independently testable with fakes once those interfaces exist.

### Dependency Graph

```text
Setup (T001-T006)
    |
    v
Foundational (T007-T012)
    |
    +--> US1 security/install (T013-T019) ----+
    |                                         |
    +--> US2 configuration/audio (T020-T029) -+--> US3 conversation (T030-T038)
                                              |
                                              v
                                  Polish and validation (T039-T045)
```

### Parallel Opportunities

- T002–T006 are parallel after T001 creates the directories.
- T008–T011 are parallel after the package skeleton exists.
- T013–T015, T020–T023, and T030–T033 are parallel test-writing groups.
- T039–T043 are parallel documentation and cleanup tasks after the story implementations.

## Parallel Example: User Story 1

```text
Task T013: configuration validation tests in tests/unit/test_config.py
Task T014: secret-sanitization tests in tests/unit/test_security.py
Task T015: installation smoke test in tests/integration/test_installation.py
```

## Parallel Example: User Story 2

```text
Task T021: audio resolution tests in tests/unit/test_audio.py
Task T022: wake-word tests in tests/unit/test_wakeword.py
Task T023: resource cleanup tests in tests/unit/test_resources.py
```

## Parallel Example: User Story 3

```text
Task T030: remote-service error tests in tests/unit/test_llm.py
Task T031: context timer tests in tests/unit/test_session.py
Task T033: end-to-end fake voice-flow regression tests in tests/integration/test_voice_flow.py
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Setup and Foundational phases.
2. Complete US1 security, configuration validation, and reproducible installation tasks.
3. Run the independent US1 test criteria without hardware or real credentials.
4. Stop for review before enabling hardware or remote-service changes.

### Incremental Delivery

1. Add US2 adapters and resource cleanup; validate device selection with fakes.
2. Add US3 retry policy, temporary context, and voice-session lifecycle; validate the preserved flow.
3. Complete documentation and hardware opt-in validation.
4. Run the complete automatic suite before any Raspberry Pi smoke test.

## Notes

- Every task uses the required checklist format, sequential ID, story label where applicable, and at least one concrete file path.
- Tests are included because the specification explicitly requires automatic tests without real hardware and separate hardware tests.
- The original application behavior remains the acceptance baseline; refactoring must not silently change the Italian voice flow.
