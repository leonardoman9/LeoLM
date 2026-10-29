# Voice Session Contract

## Lifecycle

```text
IDLE
  -> WAKE_DETECTED
  -> LISTENING
  -> RECOGNIZING
  -> REQUESTING
  -> SPEAKING
  -> IDLE
```

Qualsiasi stato operativo può passare a `ERROR`, quindi a `CLEANUP`, e infine a `IDLE` se il processo
può continuare o a `CLOSED` se l'errore è terminale.

## Turn contract

Un turno valido contiene:

1. testo riconosciuto dell'utente;
2. contesto in memoria non scaduto;
3. richiesta al modello con timeout;
4. risposta testuale non vuota;
5. sintesi e riproduzione, con rimozione del file temporaneo;
6. aggiunta dei messaggi al contesto e reset del timer a 600 secondi.

Una risposta remota fallita è classificata. Gli errori recuperabili eseguono al massimo tre tentativi
totali; dopo l'ultimo tentativo il turno viene abbandonato, le risorse vengono rilasciate e il sistema
torna a `IDLE`/ascolto della wake word.

## Privacy contract

- Audio e testo del turno non sono persistiti come storico locale.
- Il testo dei turni resta solo nel contesto in memoria della sessione attiva.
- Dopo 600 secondi dall'ultima interazione valida il contesto viene cancellato.
- Il timer non cancella un turno in elaborazione; la scadenza viene applicata subito dopo il suo
  completamento se non è arrivata una nuova interazione.
- I servizi online ricevono solo i dati necessari al turno e al contesto; la loro retention resta
  soggetta alle rispettive policy e deve essere documentata.
