# Contract: Canonical Configuration Documentation

`docs/configuration.md` è la fonte canonica per la configurazione pubblica di LeoLM.

## Required content and machine-readable format

Il documento deve contenere due tabelle Markdown, una con heading `## Runtime variables` e una con heading `## Deployment variables`. Le tabelle devono usare esattamente queste colonne, nell'ordine indicato:

`Name | Required | Default | Format | Secret | Safe example | Effect and error behavior`

`Name` è il nome esatto; `Required` è `yes`/`no`; `Default` è `—` quando non esiste; `Format` descrive tipo/unità/valori; `Secret` è `yes`/`no`; l'esempio non contiene credenziali reali. La cella finale deve descrivere effetto e messaggio/comportamento d'errore. Le variabili runtime includono quelle `LEOLM_*`; quelle deployment includono `DEVICE_*`, `WIFI_*`, `TARGET_*` e `SSH_*`.

## Consistency rules

1. `examples/.env.example` può contenere solo variabili runtime presenti nella tabella `Runtime variables`.
2. `deploy/profiles/example.env` può contenere variabili runtime e deployment presenti nelle rispettive tabelle.
3. Ogni variabile obbligatoria deve avere una rappresentazione nel template applicabile o una motivazione documentata.
4. README e guide specializzate devono rimandare al contratto invece di ridefinire default concorrenti.
5. Valori che sembrano API key, password Wi-Fi, token o dati vocali reali sono vietati.

Il controllo implementativo deve confrontare i nomi dichiarati nel contratto con template e profili senza stampare i valori.
