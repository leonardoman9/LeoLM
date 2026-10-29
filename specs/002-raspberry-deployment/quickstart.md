# Quickstart: Raspberry Deployment Profiles

## Prerequisiti PC

- Python 3.11–3.14 e ambiente virtuale del progetto;
- repository LeoLM;
- per offline: filesystem/immagine Raspberry montato con marker target;
- per SSH: host raggiungibile, account di bootstrap e accesso configurato;
- directory privata fuori dal repository per i profili reali.

## Preparare e validare un profilo

```bash
install -d -m 700 "$HOME/.config/leolm/profiles"
cp deploy/profiles/example.env "$HOME/.config/leolm/profiles/pi-soggiorno.env"
python scripts/leolm-deploy.py validate \
  --profile "$HOME/.config/leolm/profiles/pi-soggiorno.env"
```

Il comando deve fallire prima di qualsiasi scrittura se mancano campi o se un valore non è valido. Gli errori nominano la variabile, mai password o API key.

## Dry-run offline

```bash
python scripts/leolm-deploy.py dry-run \
  --profile "$HOME/.config/leolm/profiles/pi-soggiorno.env" \
  --target /mnt/leolm-pi
```

Il dry-run deve mostrare solo file, permessi e unità che verrebbero installati. Non deve modificare `/mnt/leolm-pi` né richiedere rete o hardware audio.

## Provisioning

```bash
python scripts/leolm-deploy.py provision-offline \
  --profile "$HOME/.config/leolm/profiles/pi-soggiorno.env" \
  --root /mnt/leolm-pi

python scripts/leolm-deploy.py deploy-ssh \
  --profile "$HOME/.config/leolm/profiles/pi-soggiorno.env" \
  --host pi-soggiorno.local
```

Il comando applica staging, permessi, NetworkManager e systemd in modo idempotente. Dopo il trasferimento SSH le copie temporanee contenenti segreti vengono rimosse; il profilo sorgente resta nella directory privata del PC.

Per il provisioning offline, il tool confronta l'architettura del PC con quella dell'immagine. Se non coincidono, copia il codice e i requirements e installa automaticamente virtual environment e dipendenze tramite `leolm-bootstrap.service` al primo boot, dopo la connessione Wi-Fi. Non è necessario eseguire `pip` dal PC contro un'immagine ARM.

## Verifica e recupero

```bash
python scripts/leolm-deploy.py verify \
  --profile "$HOME/.config/leolm/profiles/pi-soggiorno.env" \
  --target pi-soggiorno.local
```

Verificare il report sanificato, poi consultare i log con `journalctl -u leolm.service`. In caso di rete assente, correggere NetworkManager via console/SSH e riavviare il servizio; non copiare API key nei comandi o nei log.

Lo stato audio `configured` indica che selettore e percorso sono presenti; `hardware_verified` richiede la prova opt-in su Raspberry e non viene simulato dal controllo offline.

## Test automatici

```bash
pytest tests/deployment -q
```

I test devono usare filesystem temporanei e fake SSH/systemd. Le prove sotto `tests/hardware/` restano separate e non fanno parte del percorso automatico.
