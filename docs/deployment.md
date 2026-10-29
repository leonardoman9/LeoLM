# Deployment PC → Raspberry

Il deployment è pensato per essere eseguito dal PC. Dopo il clone, crea una copia privata di
`deploy/profiles/example.env`, sostituisci i placeholder, verifica il profilo e usa un solo comando
per il metodo scelto. Il profilo sorgente resta sul PC; l'archivio temporaneo viene eliminato anche
quando un passaggio fallisce.

```bash
python scripts/leolm-deploy.py validate --profile /percorso/leolm-soggiorno.env
python scripts/leolm-deploy.py dry-run --profile /percorso/leolm-soggiorno.env --json
python scripts/leolm-deploy.py deploy-ssh --profile /percorso/leolm-soggiorno.env --host leolm-soggiorno --user pi
python scripts/leolm-deploy.py verify --profile /percorso/leolm-soggiorno.env --target leolm-soggiorno
```

L'accesso SSH deve essere già configurato con una chiave e l'account deve poter eseguire le
operazioni amministrative senza prompt interattivi. Il comando controlla Python, systemd,
NetworkManager e i privilegi prima di installare. Copia il codice e i file generati, crea il virtual
environment sull'architettura del Raspberry, installa le dipendenze, configura Wi-Fi e abilita
`leolm.service` all'avvio. Non vengono copiati virtual environment creati sul PC.

Per un'immagine o filesystem montato:

```bash
python scripts/leolm-deploy.py provision-offline --profile /percorso/leolm-soggiorno.env --root /mnt/leolm-root
python scripts/leolm-deploy.py verify --profile /percorso/leolm-soggiorno.env --target /mnt/leolm-root
```

Lo staging offline crea `leolm-bootstrap.service`. Al primo avvio, dopo la rete, il bootstrap crea
l'utente gestito, installa le dipendenze nel target, completa la configurazione e avvia LeoLM; il
bootstrap viene poi disabilitato. Finché questo passaggio non avviene, `verify` mostra
`bootstrap: pending`, non uno stato sano.

Il servizio `leolm.service` parte dopo `network-online.target`, usa l'utente configurato e riavvia
con ritardo limitato. Per il recupero controllare lo stato di NetworkManager, del servizio e i log
del servizio senza copiare password, token o API key nei comandi o nei report. Le API online possono
ricevere audio o testo secondo la configurazione e le loro policy: consultare `docs/privacy.md`.
