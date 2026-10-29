# LeoLM deployment

The deployer uses real `.env` profiles stored in a private directory on the PC. The repository
contains only `profiles/example.env`.

Supported target: Raspberry Pi OS Bookworm Lite, 32-bit or 64-bit, on Raspberry Pi Zero 2 W with
systemd and NetworkManager. The PC requires Python 3.11+, `ssh`, and preconfigured SSH access for
remote transport.

```bash
python scripts/leolm-deploy.py validate --profile "$HOME/.config/leolm/profiles/pi.env"
python scripts/leolm-deploy.py dry-run --profile "$HOME/.config/leolm/profiles/pi.env" --target /mnt/pi
python scripts/leolm-deploy.py provision-offline --profile "$HOME/.config/leolm/profiles/pi.env" --root /mnt/pi
python scripts/leolm-deploy.py deploy-ssh --profile "$HOME/.config/leolm/profiles/pi.env" --host pi.local
python scripts/leolm-deploy.py verify --profile "$HOME/.config/leolm/profiles/pi.env" --target /mnt/pi
```

For cross-architecture images, the code and requirements are staged and
`leolm-bootstrap.service` completes the virtual environment and dependency installation on the
first boot after Wi-Fi is available. Wi-Fi keyfiles are root-owned with mode `0600`; logs contain
no credentials. MCP is neither installed nor exposed.
