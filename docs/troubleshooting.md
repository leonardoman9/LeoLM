# Troubleshooting

## Configuration

Use `docs/configuration.md` as the reference. An error identifies the variable name, never its
value. Wake word assets must exist at the configured paths, and audio selectors must match an
available device.

## Network and providers

Remote requests have configurable timeouts and limited retries. After the final error, LeoLM
releases audio resources and returns to wake word detection/listening. Check the endpoint, DNS,
connectivity, and provider policy without putting API keys into commands or logs.

## Deployment and boot

Check NetworkManager, then `systemctl status leolm.service` and `journalctl -u leolm.service`. On
cross-architecture images, check `leolm-bootstrap.service` first; the bootstrap installs the
virtual environment after `network-online.target` on first boot and disables itself after success.

## Privacy

Conversation context expires 600 seconds after the last valid interaction. Audio and TTS data are
temporary; online-service retention depends on the providers. See [deployment.md](deployment.md)
for PC-to-Raspberry procedures and [privacy.md](privacy.md) for data handling.
