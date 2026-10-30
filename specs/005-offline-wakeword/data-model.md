# Data Model: Offline Wake Word

## OfflineWakeWordConfig

Runtime configuration for local activation.

- wake_word: non-empty display and recognition word; default Panda.
- vosk_model_path: readable local directory containing a complete Italian model.
- input_selector: configured microphone selector; no fixed device index.
- wake_sample_rate: positive integer; default 16000.
- wake_phrase: normalized recognition phrase derived from wake_word.

Validation rejects empty words, non-positive sample rates, absent/unreadable model paths, and paths outside the installed managed asset location when running as a service. Validation errors name fields only and never reveal secrets.

## ModelAssetRecord

Versioned public-asset metadata used at provisioning time.

- name: model identifier.
- source_url: official model archive URL.
- sha256: expected archive digest.
- archive_size_bytes: expected compressed-size bound.
- install_relative_path: target directory below the managed application root.

The record is not secret. Acquisition succeeds only when the downloaded archive matches the expected digest. The extracted directory is valid only when required model files are present.

## WakeWordListeningSession

An owned local recognition session.

- device: resolved input audio device.
- stream: opened mono PCM capture stream.
- recognizer: local grammar-constrained recognizer.
- state: initializing, listening, activated, failed, or closed.

Transitions: initializing to listening to activated to closed; errors transition from initializing or listening to failed then closed. Closing is idempotent.

## ProvisionedWakeWordAsset

The target-side installed asset.

- root: managed application root.
- model_path: installed model directory.
- integrity: verified, missing, or invalid.
- readable_by_service: boolean.
- source: ssh-payload or offline-payload.

A service may be enabled only when integrity is verified and readable_by_service is true.

## ReadinessReport

Redacted post-deployment status additions.

- wakeword_asset: healthy, missing, or invalid.
- wakeword_runtime: importable, unavailable, or not-tested.
- audio_input: configured, unavailable, or hardware-verified.

Values are statuses only; they contain no archive paths, secret values, or raw command output.

