# Feature Specification: Automated Raspberry Pi Deployment

**Feature Branch**: `004-automated-deployment`

**Created**: 2026-10-29

**Status**: Draft

**Input**: Complete the deployment workflow so a cloned repository plus a configured environment profile can prepare and start LeoLM on supported Raspberry Pi targets with one command.

## User Scenarios & Testing

### User Story 1 - Deploy a target from a PC (Priority: P1)

As an operator, I want to clone LeoLM, fill a non-versioned deployment profile, and run one command from my PC so that a Raspberry Pi is prepared to start LeoLM automatically after boot.

**Why this priority**: The project is not deployable in practice while the SSH path only transfers a partial configuration. A complete, repeatable path is required before distributing multiple devices.

**Independent Test**: Run the deploy command against a fake SSH/filesystem target and inspect generated files, commands, permissions, and service state without real hardware.

**Acceptance Scenarios**:

1. **Given** a valid profile and an SSH-reachable Linux target, **When** the operator runs deployment, **Then** the repository runtime, dependencies, sanitized environment, Wi-Fi configuration, and systemd units are installed and enabled on the target.
2. **Given** a target already provisioned with the same profile, **When** deployment is repeated, **Then** the operation is idempotent and does not duplicate services, credentials, or files.
3. **Given** a failed remote step, **When** deployment exits, **Then** temporary files are removed, secrets are absent from output, and the operator receives the failed step and a safe recovery instruction.

### User Story 2 - Prepare an offline image or mounted filesystem (Priority: P2)

As an operator, I want to stage the same deployment payload into an offline filesystem so that I can prepare a device or image without an active SSH session.

**Why this priority**: Offline provisioning supports batch distribution and recovery workflows while preserving the same runtime contract as SSH provisioning.

**Independent Test**: Stage into a temporary directory and verify the bootstrapping service, application payload, environment permissions, and Wi-Fi artifact without mounting or booting a real image.

**Acceptance Scenarios**:

1. **Given** a writable target root and valid profile, **When** the operator stages an offline deployment, **Then** all required first-boot artifacts are created with documented ownership and modes.
2. **Given** the host cannot execute Raspberry Pi binaries, **When** staging completes, **Then** dependency installation is deferred to a first-boot bootstrap step rather than attempted on the host.

### User Story 3 - Validate and inspect deployment safely (Priority: P3)

As an operator, I want validation, dry-run, and post-deployment verification so that I can detect configuration or connectivity problems before and after changing a device.

**Why this priority**: Operators need a safe diagnostic path when deploying multiple low-resource devices, especially when the target is remote.

**Independent Test**: Feed valid, invalid, and incomplete profiles to the CLI and run verification against a fake target; assert exit codes and redacted output.

**Acceptance Scenarios**:

1. **Given** an invalid or incomplete profile, **When** validation runs, **Then** deployment is refused before any target mutation and the error identifies the non-secret field.
2. **Given** a valid profile, **When** dry-run runs, **Then** it reports the planned target, architecture strategy, files, and service actions without writing or connecting.
3. **Given** a deployed target, **When** verification runs, **Then** it reports service, environment, Wi-Fi, and runtime health without revealing secret values.

### Edge Cases

- SSH is unavailable, times out, or returns a non-zero command status: fail with a bounded timeout and a step-specific message.
- The target architecture differs from the PC: never install host-built artifacts; use target-side installation or defer it to first boot.
- `sudo` is unavailable or requires an interactive password: stop before partial privileged changes and explain the prerequisite.
- Wi-Fi credentials contain spaces, quotes, or shell metacharacters: write them as a protected configuration file, never interpolate them into shell commands.
- Existing service or deployment belongs to another profile: refuse replacement unless an explicit, safe update mode is selected.
- The profile contains a secret or a secret-like value in an invalid field: report only the field name and redact all values.
- Network installation is interrupted: retain enough state for a retry, remove temporary secrets, and do not claim the service is ready.
- Storage or memory is insufficient: fail before copying large payloads where possible and provide a bounded diagnostic.

## Requirements

### Functional Requirements

- **FR-001**: The deployment CLI MUST provide validate, dry-run, SSH deployment, offline staging, and verification commands using the existing profile-based workflow.
- **FR-002**: The CLI MUST validate required fields and reject invalid values before mutating a target.
- **FR-003**: SSH deployment MUST transfer the complete runtime payload, install target-compatible runtime dependencies, install configuration and systemd units, enable automatic startup, and report the resulting state.
- **FR-004**: Offline staging MUST create an equivalent first-boot bootstrap path that can complete privileged setup on the Raspberry Pi after network availability.
- **FR-005**: Deployment MUST discover or explicitly configure target architecture and MUST NOT execute Raspberry Pi binaries or install host-specific wheels on the PC.
- **FR-006**: Deployment MUST be repeatable and idempotent; existing managed files and services may be updated only within the deployment root and managed service identity.
- **FR-007**: Runtime secrets MUST be transferred through protected files or stdin-like channels, use restrictive permissions, be excluded from archives and logs, and be removed from temporary locations after use.
- **FR-008**: The CLI MUST redact API keys, Wi-Fi passwords, tokens, and secret-like profile values from stdout, stderr, exceptions, reports, and test output.
- **FR-009**: Wi-Fi configuration MUST be generated from the profile without hard-coded interface names or credentials and must use the target's documented network manager integration.
- **FR-010**: Systemd integration MUST start LeoLM after boot only after required network and bootstrap prerequisites, and MUST support clean stop/restart behavior.
- **FR-011**: Remote and package-install operations MUST have bounded timeouts, explicit non-zero failure handling, and cleanup on interruption or error.
- **FR-012**: The implementation MUST be testable with fake command runners and temporary filesystems; automated tests MUST NOT require SSH, sudo, Wi-Fi, ALSA, or Raspberry Pi hardware.
- **FR-013**: Deployment documentation MUST describe prerequisites, profile fields, supported flows, privacy/data handling, online service dependencies, recovery, and the exact behavior implemented by the CLI.
- **FR-014**: The implementation MUST preserve the existing LeoLM voice interaction behavior and must not add MCP tools as part of this feature.
- **FR-015**: The deployment path MUST remain suitable for Raspberry Pi Zero 2 W limits by avoiding unnecessary build steps on-device, limiting retained artifacts, and allowing dependency installation to occur once during provisioning.

### Key Entities

- **Deployment profile**: A non-versioned operator configuration containing target identity, connection details, Wi-Fi settings, runtime model/endpoints, wake word, and secret references.
- **Deployment plan**: A validated, redacted description of target mutations, architecture strategy, files, permissions, dependencies, and service actions.
- **Managed target**: The Raspberry Pi filesystem and services owned by this LeoLM deployment, including application root, runtime environment, network configuration, and systemd units.
- **Deployment result**: A redacted report containing completed steps, verification state, warnings, and safe recovery information.

## Success Criteria

### Measurable Outcomes

- **SC-001**: A fresh fake target can be fully planned and staged by one documented CLI flow with no manual file edits after profile creation.
- **SC-002**: Automated tests cover success, retry/idempotency, architecture mismatch, timeout, permission, and secret-redaction paths without physical hardware.
- **SC-003**: A deployment failure never leaves API keys or Wi-Fi passwords in CLI output, temporary deployment archives, or generated diagnostic reports.
- **SC-004**: Re-running the deployment on an already managed target produces the same managed file set and one enabled LeoLM service without duplicate units or processes.
- **SC-005**: Documentation examples and the profile template pass the repository documentation validator and match the CLI's actual options and fields.
- **SC-006**: The post-deployment verification command can distinguish not-installed, bootstrap-pending, service-failed, network-unavailable, and healthy states using stable exit codes.

## Assumptions

- The operator has physical or authorized administrative access to the target and has configured SSH access or a writable offline filesystem before running deployment.
- The target is a Debian/Raspberry Pi OS-style Linux system with systemd and NetworkManager available or explicitly marked unsupported by validation.
- For SSH deployment, passwordless `sudo` or an already-authorized privileged execution path is required; the CLI will not collect or log sudo passwords.
- A target-side Python virtual environment is preferred; dependencies are installed for the target architecture rather than copied from the PC.
- The project continues to depend on configured online speech, language, wake-word, or synthesis services as documented; this feature does not make LeoLM offline.
- MCP tools and changes to the voice conversation semantics are out of scope.
- Actual boot, microphone, speaker, Wi-Fi RF, and service latency validation on physical Raspberry Pi hardware remains a release verification step, not an automated test prerequisite.
