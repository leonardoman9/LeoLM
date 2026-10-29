# Deployment Data Model

## Deployment profile

Input loaded from a non-versioned `.env` profile.

- Identity: `DEVICE_ID`, `HOSTNAME`, `TARGET_USER`, `TARGET_HOST`, `TARGET_PORT`.
- Network: Wi-Fi SSID, password, country, connection name, and optional interface configuration.
- Runtime: model, endpoint, wake word, audio input/output device selectors, timeouts, and service settings.
- Secrets: API keys and service tokens, present only when required by validation.

Validation rejects missing required fields, invalid ports/hostnames, unsupported values, and malformed endpoints. Error messages identify field names, never values.

## Deployment plan

Redacted immutable description of one run:

- target transport (`ssh` or `offline`);
- target architecture strategy (`target-install` or `first-boot-bootstrap`);
- managed application root;
- files with owner/mode and secret classification;
- package/system prerequisite actions;
- Wi-Fi and systemd actions;
- timeout and cleanup policy.

## Managed target

The target state owned by LeoLM:

- application source/metadata and target virtual environment;
- protected `.env` and NetworkManager keyfile;
- bootstrap and runtime systemd units;
- one managed service identity and one device-specific root;
- marker/version file for safe idempotent updates.

## Deployment result

Redacted report with device id, hostname, transport, state, checks, warnings, and safe errors. States are `planned`, `staged`, `committed`, `verification_failed`, and `rolled_back`. Secret values are never retained in serialized output.

## State transitions

`validated -> planned -> staged -> committed -> verified`

Any provisioning failure transitions to `rolled_back` when cleanup succeeds, or `verification_failed` with an explicit cleanup warning when cleanup cannot be confirmed.
