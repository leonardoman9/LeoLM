# PC → Raspberry deployment

Run deployment from the PC. After cloning, create a private copy of `deploy/profiles/example.env`,
replace the placeholders, validate the profile, and use one command for the selected transport.
The source profile remains on the PC; temporary archives are removed even when a step fails.

Before a deployment, obtain and verify the public local wake-word model on the PC. The generated
`models/` directory is ignored by Git and is included only in the deployment payload:

```bash
python scripts/fetch-vosk-model.py --destination models/vosk-model-small-it-0.22
```

```bash
python scripts/leolm-deploy.py validate --profile /path/leolm-living-room.env
python scripts/leolm-deploy.py dry-run --profile /path/leolm-living-room.env --json
python scripts/leolm-deploy.py deploy-ssh --profile /path/leolm-living-room.env --host leolm-living-room --user pi
python scripts/leolm-deploy.py verify --profile /path/leolm-living-room.env --target leolm-living-room
```

SSH access must already be configured with a key, and the account must be able to perform
administrative operations without an interactive prompt. The command checks Python, systemd,
NetworkManager, and privileges before installing. It copies the code and generated files, creates
the virtual environment on the Raspberry architecture, installs dependencies, validates the Vosk
runtime and staged model, configures Wi-Fi,
and enables `leolm.service` at boot. A virtual environment created on the PC is never copied.

For an image or mounted filesystem:

```bash
python scripts/leolm-deploy.py provision-offline --profile /path/leolm-living-room.env --root /mnt/leolm-root
python scripts/leolm-deploy.py verify --profile /path/leolm-living-room.env --target /mnt/leolm-root
```

Offline staging creates `leolm-bootstrap.service`. On first boot, after networking is available,
the bootstrap creates the managed user, installs target dependencies, validates the staged Vosk
runtime, completes configuration, and
starts LeoLM; it is then disabled. Until this happens, `verify` reports `bootstrap: pending`, not a
healthy state.

`leolm.service` starts after `network-online.target`, uses the configured user, and restarts with
a bounded delay. For recovery, inspect NetworkManager, the service state, and service logs without
putting passwords, tokens, or API keys into commands or reports. Online APIs may receive audio or
text according to the configuration and their policies; see `docs/privacy.md`.
