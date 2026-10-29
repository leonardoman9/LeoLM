# LeoLM deployment

Il deployer usa profili `.env` reali conservati in una directory privata del PC. Il repository contiene solo `profiles/example.env`.

Target supportato: Raspberry Pi OS Bookworm Lite 32-bit o 64-bit su Raspberry Pi Zero 2 W, con systemd e NetworkManager. Il PC deve avere Python 3.11+, `ssh` e, per il trasporto remoto, accesso SSH già configurato.

```bash
python scripts/leolm-deploy.py validate --profile "$HOME/.config/leolm/profiles/pi.env"
python scripts/leolm-deploy.py dry-run --profile "$HOME/.config/leolm/profiles/pi.env" --target /mnt/pi
python scripts/leolm-deploy.py provision-offline --profile "$HOME/.config/leolm/profiles/pi.env" --root /mnt/pi
python scripts/leolm-deploy.py deploy-ssh --profile "$HOME/.config/leolm/profiles/pi.env" --host pi.local
python scripts/leolm-deploy.py verify --profile "$HOME/.config/leolm/profiles/pi.env" --target /mnt/pi
```

Su immagini cross-architettura il codice e i requirements vengono predisposti e `leolm-bootstrap.service` completa automaticamente venv e dipendenze al primo boot dopo il Wi-Fi. I keyfile Wi-Fi sono root-owned `0600`; i log non contengono credenziali. MCP non viene installato né esposto.
