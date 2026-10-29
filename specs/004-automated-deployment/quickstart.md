# Deployment Validation Quickstart

## Automated validation on a PC

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-dev.txt
pytest -q
python scripts/check_docs.py
```

Use a test-only profile with fake credentials and stage into a temporary directory:

```bash
python scripts/leolm-deploy.py validate --profile deploy/profiles/example.env
python scripts/leolm-deploy.py dry-run --profile deploy/profiles/example.env --json
python scripts/leolm-deploy.py provision-offline --profile deploy/profiles/example.env --root /tmp/leolm-target
python scripts/leolm-deploy.py verify --profile deploy/profiles/example.env --target /tmp/leolm-target
```

The automated suite must exercise these flows with fake transports and must not require `sudo`, SSH, ALSA, NetworkManager, or physical hardware.

## Real Raspberry Pi validation

1. Flash Raspberry Pi OS Lite (64-bit where supported), enable SSH, and connect the target to the same network or use Ethernet/USB networking.
2. Ensure the operator's SSH key works and the deployment user has non-interactive administrative privileges.
3. Copy a profile from `deploy/profiles/example.env` to a PC-only ignored path, fill only target and service values, and check its permissions.
4. Run `python scripts/leolm-deploy.py validate --profile PATH` and then `deploy-ssh` from the PC.
5. Confirm with `verify` that bootstrap, network, service, and runtime are healthy.
6. Reboot the Pi and repeat verification; then perform the hardware-only microphone, speaker, wake-word, and online-service smoke test.

Never commit a real profile or paste its contents into issue reports. Online speech/language/wake-word services may receive audio or text according to the configured runtime; consult the privacy documentation before enabling them.
