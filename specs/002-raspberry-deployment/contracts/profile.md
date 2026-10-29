# Contract: Device Profile

Il template versionato è `deploy/profiles/example.env`. I profili reali devono essere creati in una directory protetta del PC, esclusa dal repository.

## Required sections

```text
DEVICE_ID
DEVICE_HOSTNAME
WIFI_SSID
WIFI_PASSWORD
WIFI_COUNTRY
LEOLM_CONVERSATION_API_KEY
LEOLM_PORCUPINE_ACCESS_KEY
LEOLM_MODEL
LEOLM_LANGUAGE
LEOLM_WAKE_WORD
LEOLM_WAKE_WORD_PATH
LEOLM_WAKE_MODEL_PATH
LEOLM_INPUT_DEVICE
LEOLM_OUTPUT_DEVICE
```

I nomi `LEOLM_*` devono coincidere con `src/leolm/config.py`; default e valori ammessi devono essere verificati anche contro il contratto runtime della feature 001.

## Secret rules

`WIFI_PASSWORD`, `LEOLM_CONVERSATION_API_KEY` e `LEOLM_PORCUPINE_ACCESS_KEY` sono segreti. Il template usa valori fittizi come `replace-on-device`; il deployer non stampa mai il valore. I profili reali restano fuori dal repository e le copie temporanee di trasferimento vengono rimosse.
