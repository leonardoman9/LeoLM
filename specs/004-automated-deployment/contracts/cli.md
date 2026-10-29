# Deployment CLI Contract

Entrypoint: `python scripts/leolm-deploy.py <command>`.

## Commands

- `validate --profile PATH [--json]`: validate profile only; exit `0` on success and `1` on safe validation error.
- `dry-run --profile PATH [--target TARGET] [--json]`: produce a redacted plan without connecting or writing.
- `deploy-ssh --profile PATH --host HOST [--user USER] [--port PORT] [--json]`: complete remote provisioning and startup configuration.
- `provision-offline --profile PATH --root PATH [--json]`: stage a complete first-boot deployment into a writable target root.
- `verify --profile PATH --target PATH_OR_HOST [--json]`: inspect managed files/service/network state without printing secret values.

## Safety contract

- The profile is validated before target mutation.
- API keys, Wi-Fi passwords, tokens, and secret-like values are redacted from text, JSON, exceptions, and command reports.
- SSH commands have bounded timeouts and non-zero results are failures.
- Temporary payloads and secret files are removed in success and failure paths where possible.
- Repeating deployment converges on one managed installation and one systemd service.

## JSON result contract

Successful reports contain only stable fields: `device_id`, `hostname`, `transport`, `state`, `checks`, and `errors`. Check values are statuses, not raw command output. Failures use a non-zero exit code and a safe error message.
