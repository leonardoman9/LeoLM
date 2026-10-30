# Research: Offline Panda Wake Word

## Decision: Use Vosk 0.3.45 with the small Italian model

**Decision**: Use the published Vosk 0.3.45 ARM64 wheel and the official vosk-model-small-it-0.22 language model, constrained to the configured wake word.

**Rationale**: Vosk publishes a manylinux ARM64 wheel for 0.3.45 and identifies Linux ARM64/Raspberry Pi as supported. Its official model catalog lists the small Italian model as 48 MB and suitable for Raspberry Pi. A restricted vocabulary limits recognition work to wake-word activation rather than continuous general transcription.

**Alternatives considered**: Picovoice Porcupine was rejected because the current runtime requires an unavailable AccessKey. openWakeWord was rejected because its shipped models are English and Panda would need separate custom training. Push-to-talk was rejected because it removes spoken wake-word activation.

## Decision: Provision a verified local model asset

**Decision**: Fetch the official model archive on the deployment PC before staging, compare it to a versioned SHA-256 lock record, and include the verified archive or extracted asset in both SSH and offline payloads.

**Rationale**: The service must work offline after provisioning and must not download files on startup. A PC-side acquisition step makes the payload equivalent for both transports and enables deterministic integrity failures.

**Alternatives considered**: Downloading on first service start breaks offline startup and mixes installation with runtime. Committing the model archive to Git unnecessarily inflates repository history. Downloading independently on each target diverges from offline provisioning.

## Decision: Trigger only on exact normalized wake-word output

**Decision**: Feed 16 kHz mono 16-bit microphone frames to a constrained recognizer; trigger only when a normalized partial or final result equals the configured wake word.

**Rationale**: Exact matching reduces accidental activation from arbitrary transcription. The adapter returns a single activation event, after which the existing application controls command capture and releases or reopens wake-word resources according to its lifecycle.

**Alternatives considered**: Substring matching was rejected because unrelated speech can contain the word. Full unrestricted transcription was rejected because it increases CPU use and false-activation surface. A cloud confirmation was rejected because activation must remain offline.

## Decision: Remove Picovoice fields rather than retain a fallback

**Decision**: Remove Picovoice dependency, access key, model path, and keyword path from runtime and deployment contracts.

**Rationale**: Retaining them would leave a credential requirement and ambiguous startup behavior. The migration goal is an account-free activation path.

**Alternatives considered**: A selectable Picovoice fallback preserves unsupported secret-bearing configuration and expands the test surface. Unused assets in the payload make documentation disagree with runtime behavior.

## Decision: Prove Python 3.13 compatibility on target before readiness

**Decision**: Add a provisioning preflight that installs the pinned wheel in the target virtual environment and imports it before enabling the service; retain this as a required Pi 3 hardware check.

**Rationale**: The current device runs Debian 13 and Python 3.13.5. The selected Vosk wheel is platform-specific, so target-side installation and import are the authoritative compatibility proof.

**Alternatives considered**: Building native bindings on the PC is not portable to ARM64 Linux. Declaring readiness from unit tests cannot prove target wheel loading.

## Sources

- Vosk model catalog: Italian small model, size, and Raspberry Pi suitability.
- Vosk PyPI release files: 0.3.45 manylinux2014 ARM64 wheel.
- Vosk project documentation: offline streaming recognition, Raspberry Pi/Linux ARM64 support.
- openWakeWord documentation: Pi 3 capability but pre-trained English wake words.

