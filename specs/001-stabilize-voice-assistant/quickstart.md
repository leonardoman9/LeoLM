# Quickstart Validation: Stabilize Voice Assistant

Questa guida valida il design senza richiedere microfono, speaker, ALSA o servizi online reali.

## Prerequisiti

- Linux/macOS o Raspberry Pi OS con Python 3.11–3.14, secondo la matrice verificata nel piano.
- Repository clonato e ambiente virtuale attivo.
- Dipendenze di sviluppo installate dal file di requisiti del progetto.
- Nessuna API key reale nei test.

## Installazione isolata

```bash
python3.11 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pytest
```

Verificare che la procedura non esegua `sudo`, non avvii ALSA e non richieda un dispositivo fisico.

## Configurazione di test

Usare valori fittizi per le chiavi e dispositivi fake, ad esempio:

```bash
export LEOLM_CONVERSATION_API_KEY='test-only'
export LEOLM_PORCUPINE_ACCESS_KEY='test-only'
export LEOLM_INPUT_DEVICE='fake-input'
export LEOLM_OUTPUT_DEVICE='fake-output'
export LEOLM_CONTEXT_IDLE_TIMEOUT_SECONDS=600
```

I test devono verificare che `test-only` non venga stampato e che la configurazione risolta non venga
serializzata.

## Suite automatica

```bash
pytest tests/unit tests/integration -q
```

Risultati attesi:

- nessun accesso a dispositivi audio o rete reale;
- validazione dei valori e degli errori di configurazione;
- nessun segreto nei messaggi;
- massimo 3 tentativi per errori remoti recuperabili;
- cleanup verificato dopo successo, errore e interruzione;
- contesto mantenuto entro 600 secondi e cancellato dopo inattività.

## Suite hardware opt-in

Eseguire solo su Raspberry Pi con dispositivi e prerequisiti di sistema installati:

```bash
pytest tests/hardware -q
```

Questa suite deve elencare i dispositivi rilevati, verificare acquisizione e riproduzione e fallire
con un messaggio esplicito se l'hardware non è presente. Non deve installare pacchetti o modificare
il sistema.

## Smoke test vocale

Con credenziali configurate e servizi autorizzati:

1. avviare l'assistente;
2. pronunciare la wake word configurata;
3. pronunciare un comando in italiano;
4. verificare risposta audio e continuità del contesto entro 10 minuti;
5. attendere la scadenza o simulare il timer e verificare che il turno successivo non usi lo storico;
6. interrompere il processo e verificare che stream, processi e file temporanei siano rilasciati.

Per la matrice di configurazione consultare [configuration.md](contracts/configuration.md) e per il
ciclo di vita consultare [voice-session.md](contracts/voice-session.md).
