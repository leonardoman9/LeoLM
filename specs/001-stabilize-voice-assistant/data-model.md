# Data Model: Stabilize Voice Assistant

## RuntimeConfiguration

Rappresenta la configurazione validata per un processo.

| Campo | Tipo/logica | Vincoli |
|---|---|---|
| `conversation_api_key` | segreto opzionale fino all'uso | mai serializzato o stampato |
| `porcupine_access_key` | segreto opzionale fino all'uso | mai serializzato o stampato |
| `model` | stringa | non vuota |
| `conversation_endpoint` | URL | schema e host validi |
| `language` | codice lingua | supportato da wake word/STT/TTS |
| `wake_word` | identificatore | coerente con il file locale |
| `wake_word_path` | percorso | file leggibile |
| `wake_model_path` | percorso | file leggibile |
| `input_selector` | nome o identificatore | risolvibile quando l'audio parte |
| `output_selector` | nome o identificatore | risolvibile quando l'audio parte |
| `network_timeout` | durata | positiva |
| `retry_count` | intero | massimo 2 retry aggiuntivi |
| `retry_backoff` | durata | non negativa e crescente |
| `context_idle_timeout` | durata | default 600 secondi |

La configurazione viene creata una volta all'avvio e non contiene valori segreti nei messaggi di
diagnostica. La configurazione di test usa valori fittizi e sostituisce i selettori con dispositivi
fake.

## AudioDevice

Rappresenta un microfono o speaker rilevato.

- `role`: `input` oppure `output`.
- `selector`: nome/identificatore configurato.
- `resolved_id`: identificatore ottenuto dalla rilevazione, non assunto stabile tra avvii.
- `sample_rate`: frequenza supportata e validata.
- `channels`: canali disponibili.
- `state`: `unresolved`, `ready`, `busy`, `disconnected`, `closed`.

Transizioni valide: `unresolved → ready`, `ready → busy`, `busy → ready`, `ready/busy → disconnected`,
ogni stato operativo → `closed` durante cleanup.

## VoiceSession

Rappresenta una conversazione vocale attiva.

- `state`: `idle`, `listening`, `recognizing`, `requesting`, `speaking`, `failed`, `closed`.
- `turns`: lista in memoria di messaggi utente/assistente necessari al contesto.
- `last_activity_at`: timestamp monotono dell'ultima interazione valida.
- `context_deadline`: scadenza calcolata a 600 secondi dall'ultima attività.
- `retry_attempt`: tentativo corrente della richiesta remota.

Il contesto passa a vuoto quando il timer scade; un'interazione in corso completa il proprio ciclo
prima della cancellazione. Un'interruzione o errore terminale chiude le risorse e lascia la sessione
in `failed` o `closed` senza persistenza dei turni.

## ExternalServiceResult

Risultato normalizzato di un servizio esterno.

- `kind`: `success`, `timeout`, `connection_error`, `http_error`, `invalid_payload`, `rate_limited`.
- `retryable`: booleano derivato dal tipo di errore e dal metodo.
- `user_message`: testo sanitizzato per l'utente.
- `payload`: contenuto utile solo in memoria e solo per il turno corrente.

## ResourceLease

Ownership temporanea di stream audio, client wake word, processo player e file TTS. Ogni lease deve
essere chiudibile in modo idempotente e registrare lo stato `acquired`/`released`; il coordinatore
rilascia le lease in ordine inverso anche durante eccezioni o `KeyboardInterrupt`.
