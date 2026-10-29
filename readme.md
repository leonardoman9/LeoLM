# LeoLM — Raspberry Pi voice assistant

LeoLM è un assistente vocale per Raspberry Pi Zero 2 W. Il flusso principale è wake word, comando
vocale in italiano, richiesta al modello configurato e risposta vocale.

## Caratteristiche

- Wake word e riconoscimento vocale.
- Modello, provider, lingua e dispositivi configurabili.
- Contesto conversazionale temporaneo di 10 minuti.
- Retry di rete limitati e cleanup delle risorse audio.
- Suite automatica senza hardware e suite hardware opt-in.

## Installazione

Installare prima i prerequisiti di sistema descritti in
[`docs/system-dependencies.md`](docs/system-dependencies.md), poi creare l'ambiente Python:

```bash
python3.11 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-dev.txt
```

Esportare le variabili indicate in [`docs/configuration.md`](docs/configuration.md) nel processo di
avvio. Non salvare credenziali reali nel repository.

## Avvio

```bash
python openai_request.py
```

Pronunciare la wake word configurata e poi il comando in italiano. Il testo della conversazione resta
in memoria per 10 minuti dall'ultima interazione valida; dopo viene eliminato.

## Configurazione

Le variabili supportate sono definite in [`docs/configuration.md`](docs/configuration.md) e nell'esempio
[`examples/.env.example`](examples/.env.example). Per il deployment PC→Raspberry consultare
[`docs/deployment.md`](docs/deployment.md). Sono configurabili modello, endpoint, lingua, wake word,
asset, input, output, timeout, retry e durata del contesto.

## Privacy e servizi online

Consultare [`docs/privacy.md`](docs/privacy.md). Il riconoscimento, il modello e la sintesi possono
inviare dati ai servizi online configurati e dipendono dalla connettività e dalle loro policy.

## Test

La suite automatica non richiede dispositivi o rete:

```bash
pytest -q
```

I test hardware sono opt-in:

```bash
pytest -m hardware tests/hardware -q
```

Dipendenze e prerequisiti sono elencati in `requirements.txt`, `requirements-dev.txt` e
`docs/system-dependencies.md`.

## Troubleshooting

- Se manca una chiave, verificare il nome della variabile senza inserire il valore nei log.
- Se manca un asset wake word, verificare `LEOLM_WAKE_WORD_PATH` e `LEOLM_WAKE_MODEL_PATH`.
- Se un dispositivo audio non viene trovato, usare un selettore configurabile e controllare i test
  hardware opt-in.
- Se il servizio remoto non risponde, LeoLM esegue al massimo tre tentativi e torna all'ascolto.

## Validazione documentale

Prima di una release eseguire il controllo offline e la checklist:

```bash
python scripts/check_docs.py --root .
pytest tests/documentation -q
```

Consultare [`docs/release-checklist.md`](docs/release-checklist.md) per la verifica completa.

## Licenza

Il progetto è distribuito secondo la licenza indicata in `LICENSE.txt`.
