# Feature Specification: Offline Panda Wake Word

**Feature Branch**: 005-offline-wakeword

**Created**: 2026-10-30

**Status**: Draft

**Input**: User description: "Sostituire Porcupine con una wake word offline Vosk che riconosca “Panda” su Raspberry Pi 3 ARM64, senza chiavi Picovoice e con deployment riproducibile del modello italiano."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Activate LeoLM offline with Panda (Priority: P1)

As a Raspberry Pi 3 owner, I want LeoLM to wait for the spoken word “Panda” using only local resources, so that wake-word activation works without a third-party account or internet access.

**Why this priority**: Activation is the first step of every voice interaction and must not depend on unavailable Picovoice credentials.

**Independent Test**: With a configured microphone and local Italian language asset, speak “Panda” and verify that LeoLM begins command capture while no network traffic or third-party credential is needed for activation.

**Acceptance Scenarios**:

1. **Given** a Raspberry Pi 3 with the configured microphone and a valid local language asset, **When** a user says “Panda”, **Then** LeoLM begins listening for a command.
2. **Given** a valid local language asset and no network connectivity, **When** a user says “Panda”, **Then** wake-word activation continues to work.
3. **Given** no Picovoice credential is configured, **When** LeoLM starts with the offline wake word configured, **Then** it reaches the waiting-for-wake-word state without a credential error.

---

### User Story 2 - Deploy the offline language asset reproducibly (Priority: P2)

As an operator, I want the required Italian language asset to be obtained and verified during provisioning, so that a deployed device has all wake-word assets before its service starts.

**Why this priority**: A local recognizer is only useful when its asset is available, intact, and does not require a runtime download.

**Independent Test**: Provision a target from a prepared deployment payload and verify the asset is present, integrity-checked, readable by the service account, and not fetched when the service runs.

**Acceptance Scenarios**:

1. **Given** a deployment with a valid asset source and integrity record, **When** provisioning completes, **Then** the asset is installed in the managed application directory before the service is enabled.
2. **Given** an asset that is missing, corrupted, or fails integrity verification, **When** provisioning runs, **Then** provisioning fails safely and does not report the device as ready.
3. **Given** an offline-staged target containing the verified asset, **When** the target first boots, **Then** it can finish provisioning without downloading the asset again.

---

### User Story 3 - Recover safely from audio or asset failures (Priority: P3)

As an operator, I want safe diagnostics when the microphone or local language asset is unavailable, so that I can correct the installation without exposing credentials or leaving audio resources open.

**Why this priority**: USB audio devices can be disconnected or renumbered, and failures must not make the service appear healthy.

**Independent Test**: Start the application with a missing asset and separately with an unavailable input device; verify safe errors, closed resources, and service recovery behavior.

**Acceptance Scenarios**:

1. **Given** a missing or unreadable local language asset, **When** LeoLM starts, **Then** it reports a safe configuration error and does not capture audio.
2. **Given** an unavailable configured microphone, **When** LeoLM starts or resumes listening, **Then** it releases any acquired resources and reports a safe audio error.

### Edge Cases

- The microphone supplies a sample format or rate unsuitable for local wake-word recognition.
- Spoken audio contains “Panda” as part of unrelated speech, background speech, or noise.
- The local asset directory is present but incomplete after an interrupted deployment.
- The device has insufficient free memory or storage for the local language asset.
- The command-recognition, model, or speech-output service is unavailable after wake-word activation; the assistant returns to a safe listening state.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST detect the configured wake word locally from the configured audio input without requiring a Picovoice account, Picovoice credential, or network connectivity.
- **FR-002**: The system MUST retain Panda as the default wake word and allow the wake-word label to be configured without source-code changes.
- **FR-003**: The system MUST require a local Italian language asset at startup and reject a missing, unreadable, or invalid asset with an error that contains no secret values.
- **FR-004**: The system MUST acquire microphone resources only while needed for wake-word listening and release them on activation errors, restart, shutdown, and interruption.
- **FR-005**: The system MUST make wake-word activation independent of the subsequent online command recognition, model request, and speech synthesis stages.
- **FR-006**: The deployment workflow MUST obtain the required local language asset before service activation, verify its integrity, and make it available to both SSH and offline provisioning.
- **FR-007**: The service MUST NOT download a wake-word asset, install system packages, or modify system configuration during ordinary runtime startup.
- **FR-008**: The deployment profile, runtime configuration, documentation, and validation MUST no longer require a Picovoice credential or Picovoice-specific wake-word assets.
- **FR-009**: This feature release MUST support and be hardware-verified on Raspberry Pi 3 64-bit targets. Raspberry Pi Zero 2 W support is explicitly deferred under the temporary exception below and MUST NOT be claimed as supported by this release.
- **FR-010**: Automated tests MUST cover successful local activation, missing asset, unavailable microphone, resource cleanup, configuration validation, asset-integrity failure, and absence of credential leakage without real audio hardware or network access.
- **FR-011**: Hardware verification on the Raspberry Pi MUST demonstrate service startup, microphone capture, spoken wake-word activation, command processing, synthesis, and speaker playback before the deployment is reported as fully working.

### Key Entities

- **Offline wake-word configuration**: The configured word, local asset location, audio selection, and safe validation state required to activate LeoLM locally.
- **Language asset record**: The versioned source, expected integrity value, installed location, and provisioning state of the Italian local language asset.
- **Wake-word listening session**: An owned microphone capture session that ends in activation, safe failure, or cleanup.
- **Deployment readiness report**: A redacted result that distinguishes asset absence, asset integrity failure, unavailable audio, service failure, and hardware-verified readiness.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: On the target Pi 3, 20 spoken attempts of Panda made within normal speaking range result in at least 18 wake-word activations.
- **SC-002**: During a 10-minute idle listening test on the target Pi 3, the assistant records no more than one unintended activation in the normal installation environment.
- **SC-003**: Wake-word activation completes with the target disconnected from the internet after the local asset has been installed.
- **SC-004**: A fresh SSH or offline deployment either installs one verified local asset and enables one service, or exits with a safe failed state and no readiness claim.
- **SC-005**: The default automated test suite completes without microphone, speaker, local language asset, network access, Picovoice account, or secret values.
- **SC-006**: On the target Pi 3, the complete verified voice path—service start, wake word, microphone command, model response, synthesis, and speaker playback—can be completed after provisioning.
- **SC-007**: On the target Pi 3, wake-word activation has a p95 latency of at most 2 seconds and the LeoLM process remains at or below 650 MiB resident memory during the 10-minute idle test, without an out-of-memory termination or sustained swap activity.

## Assumptions

- The Pi 3 has a working 64-bit operating system, a USB microphone, and a USB audio output selected through the deployment profile.
- The lightweight Italian local language asset is suitable for a single-word wake-word vocabulary and is small enough for the available storage and memory budget; this is verified on hardware.
- Online services remain acceptable for command recognition, conversation, and speech synthesis; only wake-word activation is moved offline.
- The deployment PC may obtain the public language asset before provisioning; the running service never needs to fetch it.
- The existing Porcupine-based configuration and assets are removed from the managed runtime rather than retained as a fallback requiring a credential.
- Tuning for different rooms, microphones, accents, and false-activation rates is a hardware verification activity and does not change the no-account requirement.

## Temporary Compatibility Exception

Raspberry Pi Zero 2 W validation is deferred for this feature because only a Raspberry Pi 3 B+ ARM64 is currently available for hardware testing. This release supports and documents only the tested Pi 3 path; it makes no Pi Zero 2 W readiness claim. The LeoLM maintainer owns the exception, which must be reviewed before the next feature release or by 2027-01-31, whichever occurs first. The follow-up must add a Pi Zero 2 W hardware measurement for memory, activation latency, and end-to-end voice flow before restoring a Pi Zero 2 W support claim.

