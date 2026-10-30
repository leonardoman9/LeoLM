# Implementation Plan: Offline Panda Wake Word

**Branch**: 005-offline-wakeword | **Date**: 2026-10-30 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from specs/005-offline-wakeword/spec.md

## Summary

Replace the credential-gated wake-word path with a local Vosk recognizer constrained to the configured word, defaulting to Panda. Package the lightweight Italian model as a verified provisioning asset, remove Picovoice configuration from the runtime contract, and preserve the existing independently-testable audio, conversation, and speech-output boundaries.

## Technical Context

**Language/Version**: Python 3.11–3.13; target currently runs Python 3.13.5.

**Primary Dependencies**: PyAudio/PortAudio for capture; Vosk 0.3.45 ARM64 wheel; existing SpeechRecognition, requests, gTTS, and mpg123 adapters.

**Storage**: Files only. The verified Vosk model is installed below the managed application root; temporary archives are removed after provisioning.

**Testing**: pytest unit, integration, deployment, documentation, and opt-in Raspberry Pi hardware tests with fakeable Vosk and audio adapters.

**Target Platform**: Raspberry Pi 3 B+ ARM64 running Debian 13/Trixie. Pi Zero 2 W and armhf validation are explicitly out of scope for this release under the temporary exception in spec.md.

**Project Type**: Python voice-assistant runtime plus provisioning CLI.

**Performance Goals**: Local activation begins command capture in normal use with at least 18 successful detections in 20 spoken attempts, no more than one unintended activation in a 10-minute idle test, p95 activation latency at most 2 seconds, and resident memory at most 650 MiB on the Pi 3.

**Constraints**: No Picovoice account or credential; wake-word operation is offline after provisioning; 16 kHz mono 16-bit microphone frames; no model download, package installation, or system modification during service startup; secrets never appear in output.

**Scale/Scope**: One local Italian wake word, Panda, per managed device; no replacement of the existing online command recognition, model, or TTS providers.

## Constitution Check

*GATE: PASS before Phase 0 research. Re-checked after Phase 1: PASS.*

- Credentials: removes the Picovoice secret and retains redacted profile/report behavior.
- Reproducibility: pins the Vosk runtime and records a verified model asset before provisioning.
- Hardware isolation: Vosk and microphone interactions remain replaceable; default tests use fakes.
- Resource lifecycle: the wake-word adapter owns and closes one input stream and recognizer session.
- Explicit configuration: model path, input selector, wake label, and audio rate are validated before capture.
- Modularity: configuration, adapter, asset acquisition, payload staging, and verification retain separate responsibilities.
- Error handling: missing/corrupt assets, dependency failures, and unavailable microphones become safe errors.
- Documentation: configuration, deployment, dependency, and Pi compatibility documentation change with the code.
- Low-resource targets: use the small Italian model and restricted vocabulary. Pi Zero 2 W is not supported by this release; its deferred hardware validation is documented as a temporary exception in spec.md.

## Project Structure

### Documentation (this feature)

    specs/005-offline-wakeword/
    ├── plan.md
    ├── research.md
    ├── data-model.md
    ├── quickstart.md
    ├── contracts/
    │   └── runtime-configuration.md
    └── tasks.md

### Source Code (repository root)

    src/leolm/
    ├── config.py
    ├── wakeword.py
    ├── audio.py
    └── deployment/
        ├── profile.py
        ├── manifest.py
        ├── render.py
        ├── ssh.py
        └── verify.py

    scripts/
    ├── leolm-deploy.py
    └── fetch-vosk-model.py

    deploy/
    └── profiles/example.env

    tests/
    ├── unit/
    ├── integration/
    ├── deployment/
    ├── documentation/
    └── hardware/

**Structure Decision**: Replace the existing wake-word adapter in place and extend the existing deployment package. A single verified asset-acquisition path is shared by SSH and offline provisioning so neither flow downloads at runtime or silently diverges.

## Complexity Tracking

No constitution violations require an exception.

