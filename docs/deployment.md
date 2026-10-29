# PC → Raspberry deployment

Run deployment from the PC. After cloning, create a private copy of `deploy/profiles/example.env`,
replace the placeholders, validate the profile, and use one command for the selected transport.
The source profile remains on the PC; temporary archives are removed even when a step fails.

```bash
python scripts/leolm-deploy.py validate --profile /path/leolm-living-room.env
python scripts/leolm-deploy.py dry-run --profile /path/leolm-living-room.env --json
python scripts/leolm-deploy.py deploy-ssh --profile /path/leolm-living-room.env --host leolm-living-room --user pi
python scripts/leolm-deploy.py verify --profile /path/leolm-living-room.env --target leolm-living-room
```

SSH access must already be configured with a key, and the account must be able to perform
administrative operations without an interactive prompt. The command checks Python, systemd,
NetworkManager, and privileges before installing. It copies the code and generated files, creates
the virtual environment on the Raspberry architecture, installs dependencies, configures Wi-Fi,
and enables `leolm.service` at boot. A virtual environment created on the PC is never copied.

For an image or mounted filesystem:

```bash
python scripts/leolm-deploy.py provision-offline --profile /path/leolm-living-room.env --root /mnt/leolm-root
python scripts/leolm-deploy.py verify --profile /path/leolm-living-room.env --target /mnt/leolm-root
```

Offline staging creates `leolm-bootstrap.service`. On first boot, after networking is available,
the bootstrap creates the managed user, installs target dependencies, completes configuration, and
starts LeoLM; it is then disabled. Until this happens, `verify` reports `bootstrap: pending`, not a
healthy state.

`leolm.service` starts after `network-online.target`, uses the configured user, and restarts with
a bounded delay. For recovery, inspect NetworkManager, the service state, and service logs without
putting passwords, tokens, or API keys into commands or reports. Online APIs may receive audio or
text according to the configuration and their policies; see `docs/privacy.md`.
