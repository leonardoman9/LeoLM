# Contratto canonico di configurazione

Questo documento è la fonte canonica per nomi, scope, obbligatorietà, default, formato, segreti ed errori. Il validator legge le due tabelle con queste colonne esatte:

`Name | Required | Default | Format | Secret | Safe example | Effect and error behavior`

## Runtime variables

| Name | Required | Default | Format | Secret | Safe example | Effect and error behavior |
|---|---|---|---|---|---|---|
| `LEOLM_CONVERSATION_API_KEY` | yes | — | non-empty string | yes | `replace-on-device` | Provider conversation; startup error if missing |
| `LEOLM_PORCUPINE_ACCESS_KEY` | yes | — | non-empty string | yes | `replace-on-device` | Wake word provider; startup error if missing |
| `LEOLM_MODEL` | no | `google/gemini-2.0-flash-thinking-exp:free` | provider model id | no | `test/model` | Model used for conversation |
| `LEOLM_CONVERSATION_ENDPOINT` | no | `https://openrouter.ai/api/v1/chat/completions` | HTTP(S) URL | no | `https://example.invalid/chat` | Invalid URL prevents startup |
| `LEOLM_LANGUAGE` | no | `it-IT` | BCP-47 language tag | no | `it-IT` | Speech and TTS language |
| `LEOLM_WAKE_WORD` | no | `Panda` | non-empty string | no | `Panda` | Wake word label |
| `LEOLM_WAKE_WORD_PATH` | no | `Panda_it_raspberry-pi_v3_0_0.ppn` | readable file path | no | `wake.ppn` | Missing asset produces configuration error |
| `LEOLM_WAKE_MODEL_PATH` | no | `porcupine_params_it.pv` | readable file path | no | `model.pv` | Missing asset produces configuration error |
| `LEOLM_INPUT_DEVICE` | no | — | audio selector | no | `fake-input` | Selects microphone; unavailable device is reported safely |
| `LEOLM_OUTPUT_DEVICE` | no | — | audio selector | no | `fake-output` | Selects speaker; unavailable device is reported safely |
| `LEOLM_NETWORK_TIMEOUT_SECONDS` | no | `30` | positive seconds | no | `30` | Bounds remote request duration |
| `LEOLM_RETRY_COUNT` | no | `2` | integer `0..2` | no | `1` | Limits network retries |
| `LEOLM_RETRY_BACKOFF_SECONDS` | no | `1` | non-negative seconds | no | `1` | Delay between retries |
| `LEOLM_CONTEXT_IDLE_TIMEOUT_SECONDS` | no | `600` | positive seconds | no | `600` | Clears context after inactivity |

## Deployment variables

| Name | Required | Default | Format | Secret | Safe example | Effect and error behavior |
|---|---|---|---|---|---|---|
| `DEVICE_ID` | yes | — | alphanumeric id with `-`/`_` | no | `pi-soggiorno` | Isolates files and reports; invalid id rejects provisioning |
| `DEVICE_HOSTNAME` | yes | — | Linux hostname | no | `leolm-soggiorno` | Target hostname; invalid value rejects provisioning |
| `WIFI_SSID` | yes | — | UTF-8 SSID | no | `replace-on-device` | NetworkManager connection name |
| `WIFI_PASSWORD` | yes | — | Wi-Fi credential | yes | `replace-on-device` | Stored only in protected keyfile |
| `WIFI_COUNTRY` | yes | — | two-letter country code | no | `IT` | Radio country; invalid value rejects provisioning |
| `WIFI_HIDDEN` | no | `false` | boolean | no | `false` | Enables hidden SSID handling |
| `TARGET_USER` | no | `leolm` | Linux account name | no | `leolm` | Service account |
| `TARGET_ARCH` | no | `armhf` | `armhf` or `arm64` | no | `arm64` | Selects compatible/bootstrap installation |
| `SSH_USER` | no | `pi` | SSH account | no | `pi` | Remote provisioning account |
| `SSH_PORT` | no | `22` | TCP port | no | `22` | Remote SSH port |

I profili reali restano fuori dal repository. `examples/.env.example` contiene solo variabili runtime; `deploy/profiles/example.env` contiene entrambe le scope con placeholder fittizi.
