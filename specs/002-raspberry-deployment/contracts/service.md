# Contract: LeoLM systemd Service

Il template `deploy/systemd/leolm.service` deve installare una sola unità per dispositivo.

Il template `deploy/systemd/leolm-bootstrap.service` deve installare il virtual environment e le dipendenze runtime quando l'immagine è stata preparata da un PC con architettura diversa. Deve essere one-shot, dipendere da `network-online.target`, usare lo stesso manifest del deployer, essere idempotente e risultare disabilitato dopo il successo.

Requisiti:

- utente e gruppo dedicati, senza privilegi amministrativi;
- `After=network-online.target` e `Wants=network-online.target`;
- `EnvironmentFile` leggibile solo dal servizio;
- working directory e interpreter del virtual environment configurabili;
- `Restart=on-failure` con `RestartSec` e limiti di start configurabili;
- nessun segreto in `ExecStart`, `Description`, output o nome unità;
- stop/restart compatibili con il cleanup audio dell'applicazione;
- MCP non abilitato né esposto.

Il report di verifica deve usare `systemctl is-enabled`, `systemctl is-active` e controlli equivalenti sanificati, senza stampare il contenuto dell'environment file.

La verifica audio distingue `configured` (selettore e percorso presenti) da `hardware_verified` (dispositivo fisico rilevato e testato); il secondo stato è disponibile solo con il test hardware opt-in.
