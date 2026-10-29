# Research: Automated Deployment

## Decision: Install Python dependencies on the target

The PC never copies a host-created virtual environment or compiled wheel to the Raspberry Pi. SSH provisioning copies source and metadata, discovers the target architecture, and creates/updates the virtual environment on the target. Offline provisioning stages a first-boot bootstrap when the host cannot run the target architecture.

**Rationale**: Python wheels and native audio dependencies are architecture and OS dependent. Target-side installation avoids invalid binaries and keeps the Pi image reproducible.

**Alternatives considered**: Copying `.venv` was rejected because it is not portable. Building all dependencies in a cross toolchain was rejected as unnecessary complexity for this project.

## Decision: Use protected files for secrets

The runtime environment and Wi-Fi keyfile are rendered locally with restrictive permissions, transferred as files, installed with explicit modes, and deleted from temporary paths in `finally` cleanup. Commands and reports contain only paths and redacted statuses.

**Rationale**: Secrets in command-line arguments can be exposed through process listings and shell history; file-based transfer allows permissions and cleanup to be tested.

**Alternatives considered**: Inline shell quoting was rejected because it still exposes values to command logs and is fragile for arbitrary passwords.

## Decision: Share a manifest and injectable transport

Both SSH and offline provisioning consume the same managed file manifest, service plan, and redaction/report rules. Command execution and file transfer are injectable so tests use fakes and temporary directories.

**Rationale**: The current SSH implementation and offline implementation have drifted. A shared contract makes “one command” behavior verifiable without a physical Pi.

**Alternatives considered**: Duplicating the current flows was rejected because it would preserve inconsistent behavior.

## Decision: systemd plus NetworkManager are explicit target prerequisites

The deployment validates the target prerequisites and installs units with network-online ordering. Wi-Fi is represented as a NetworkManager keyfile with restrictive permissions and no hard-coded interface index.

**Rationale**: This matches Raspberry Pi OS deployments and supports automatic boot/network startup without embedding a single device's ALSA or interface names.

**Alternatives considered**: Starting LeoLM from shell startup files was rejected because it lacks supervision, restart semantics, and reliable cleanup.

## Decision: Verification reports states, not secret values

Verification distinguishes missing installation, bootstrap pending, service failure, network failure, and healthy state using stable exit codes and redacted checks.

**Rationale**: A remote low-resource device needs actionable diagnostics without leaking credentials.

**Alternatives considered**: Treating any reachable SSH host as healthy was rejected because it does not prove the service or runtime is ready.
