# Contract: Provisioning CLI

Il tool pianificato in `scripts/leolm-deploy.py` deve esporre comandi equivalenti per filesystem e SSH.

```text
python scripts/leolm-deploy.py validate --profile PATH
python scripts/leolm-deploy.py dry-run --profile PATH --target PATH|HOST
python scripts/leolm-deploy.py provision-offline --profile PATH --root PATH
python scripts/leolm-deploy.py deploy-ssh --profile PATH --host HOST
python scripts/leolm-deploy.py verify --profile PATH --target PATH|HOST
```

## Invariants

- la validazione completa precede ogni modifica;
- `--dry-run` non scrive, non installa pacchetti e non contatta servizi online;
- offline e SSH usano lo stesso manifest e le stesse regole di rendering;
- il manifest comprende codice LeoLM, virtual environment, dipendenze versionate, asset, environment runtime, configurazione Wi-Fi e unità systemd;
- la preparazione del virtual environment e l'installazione delle dipendenze sono riproducibili e non dipendono da pacchetti già presenti sul target; se PC e target hanno architetture diverse, il manifest installa tramite `leolm-bootstrap.service` al primo boot;
- il bootstrap target-side è one-shot, idempotente, eseguito dopo `network-online.target`, registra solo errori sanificati e viene disabilitato dopo il successo;
- i keyfile NetworkManager con password Wi-Fi sono creati con ownership root e permessi `0600`, fuori dall'environment leggibile dal servizio LeoLM;
- il commit è idempotente e non crea unità duplicate;
- gli errori riportano il campo o l'operazione, mai il valore segreto;
- l'output normale contiene solo stato sanificato.

Exit code: `0` successo, `1` profilo/target non valido o provisioning fallito, `2` uso del CLI non valido.
