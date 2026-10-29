# Configuration Contract

LeoLM legge la configurazione da variabili d'ambiente. I nomi definitivi devono essere mantenuti
stabili dopo l'implementazione e documentati in `.env.example`; i valori segreti non devono essere
inclusi nel file di esempio.

| Variabile | Obbligatoria | Default | Significato |
|---|---:|---|---|
| `LEOLM_CONVERSATION_API_KEY` | per richieste remote | nessuno | chiave del servizio conversazionale |
| `LEOLM_PORCUPINE_ACCESS_KEY` | per wake word | nessuno | credenziale wake word |
| `LEOLM_MODEL` | no | modello compatibile dichiarato | modello remoto |
| `LEOLM_CONVERSATION_ENDPOINT` | no | endpoint documentato | endpoint del servizio |
| `LEOLM_LANGUAGE` | no | `it-IT` | lingua STT/TTS/wake word |
| `LEOLM_WAKE_WORD` | no | wake word distribuita | identificatore wake word |
| `LEOLM_WAKE_WORD_PATH` | no | asset locale supportato | file wake word |
| `LEOLM_WAKE_MODEL_PATH` | no | asset locale supportato | parametri wake word |
| `LEOLM_INPUT_DEVICE` | no | rilevazione configurabile | selettore microfono |
| `LEOLM_OUTPUT_DEVICE` | no | rilevazione configurabile | selettore speaker |
| `LEOLM_NETWORK_TIMEOUT_SECONDS` | no | valore limitato documentato | timeout richiesta |
| `LEOLM_RETRY_COUNT` | no | `2` | retry aggiuntivi, massimo 2 |
| `LEOLM_RETRY_BACKOFF_SECONDS` | no | valore crescente documentato | ritardo tra retry |
| `LEOLM_CONTEXT_IDLE_TIMEOUT_SECONDS` | no | `600` | timeout inattività contesto |

Regole:

1. Le credenziali mancanti producono un errore nominando la variabile, mai il valore.
2. Percorsi, timeout, retry e selettori sono validati prima dell'apertura di risorse.
3. Valori sconosciuti, timeout non positivi, retry oltre 2 o percorsi non leggibili sono errori di
   configurazione.
4. Il processo non stampa mai l'ambiente completo e non persiste la configurazione risolta.
