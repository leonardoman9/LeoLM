# Offline Wake-Word Runtime Configuration Contract

## Runtime environment

| Name | Required | Default | Format | Secret | Effect and validation |
|---|---|---|---|---|---|
| LEOLM_WAKE_WORD | no | Panda | non-empty word or phrase | no | Exact normalized local activation phrase; empty value rejects startup. |
| LEOLM_VOSK_MODEL_PATH | yes | models/vosk-model-small-it-0.22 | readable local model directory | no | Missing, unreadable, or incomplete asset rejects startup before microphone capture. |
| LEOLM_WAKE_SAMPLE_RATE | no | 16000 | positive integer Hz | no | Required capture rate for local recognition; unsupported device rate reports a safe audio error. |
| LEOLM_INPUT_DEVICE | no | — | PortAudio index or case-insensitive name selector | no | Selects the microphone; no matching input reports a safe audio error. |

## Removed environment variables

The migration removes LEOLM_PORCUPINE_ACCESS_KEY, LEOLM_WAKE_WORD_PATH, and LEOLM_WAKE_MODEL_PATH. They must not be required by profile validation, emitted into the target environment, or documented as runtime requirements.

## Behavioral contract

- A valid configured local model and microphone are sufficient for wake-word activation without network connectivity.
- Wake-word recognition produces one activation only when the normalized result exactly matches the configured wake word.
- Any asset, dependency, or microphone error is safe to log and releases owned resources.
- The wake-word adapter must not transmit microphone data to a remote service.
- Existing conversation credentials remain required only for the subsequent model-request stage.

