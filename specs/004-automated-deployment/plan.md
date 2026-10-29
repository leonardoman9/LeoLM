# Implementation Plan: Automated Raspberry Pi Deployment

**Branch**: `004-automated-deployment` | **Date**: 2026-10-29 | **Spec**: [spec.md](./spec.md)

## Summary

Complete the existing deployment subsystem so `scripts/leolm-deploy.py` can validate a profile, create a reproducible target payload, install target-compatible dependencies, configure Wi-Fi and systemd, clean up secrets, and verify readiness. The implementation will share rendering and manifest logic between SSH and offline provisioning, use an injectable command transport for tests, and retain the current voice runtime unchanged.

## Technical Context

**Language/Version**: Python 3.11+ on the PC; target-supported Python declared by the existing project metadata.

**Primary Dependencies**: Python standard library for deployment; existing project runtime dependencies; `ssh`/`scp` or an equivalent target transport, `systemd`, `NetworkManager`, and `venv` on the target.

**Storage**: Filesystem only; managed application root under `/opt/leolm/<device_id>`, protected runtime `.env`, NetworkManager keyfile, systemd units, and bounded temporary staging directories.

**Testing**: pytest with fake command runners and temporary filesystems; no SSH, sudo, Wi-Fi, ALSA, or Raspberry Pi hardware in automated tests.

**Target Platform**: PC running Linux/macOS/Windows-compatible Python tooling for planning; Debian/Raspberry Pi OS-style Linux with systemd and NetworkManager on Raspberry Pi Zero 2 W.

**Project Type**: Python voice assistant plus deployment CLI/library.

**Performance Goals**: Bounded command timeouts; no unnecessary on-device source builds; repeat deployment should converge without duplicate processes or units.

**Constraints**: Low CPU/RAM/storage on Pi Zero 2 W; no secrets in arguments/logs/artifacts; no host-architecture binaries copied to target; deployment must be resumable/idempotent.

**Scale/Scope**: One managed LeoLM installation per target, repeatable across multiple targets and profiles; MCP tools and voice behavior are out of scope.

## Constitution Check

*GATE: PASS before design.*

- Secrets remain profile/env-file based, redacted, and protected; no secret logging or archive inclusion.
- Installation is represented by versioned scripts, manifests, requirements, service units, and docs.
- All deployment behavior is isolated behind fakeable command/filesystem adapters.
- Audio runtime is not changed; service stop/start and failed provisioning clean temporary resources.
- Target-specific values remain configurable through profile/environment fields.
- SSH, offline, rendering, verification, and CLI responsibilities remain modular.
- Remote/package operations use bounded timeouts and explicit failures.
- Documentation and generated examples will be updated with the implemented behavior.
- Target-side dependency installation avoids copying incompatible binaries and limits retained artifacts.

## Project Structure

```text
src/leolm/deployment/
├── profile.py       # profile loading and validation
├── render.py        # env, bootstrap, and unit rendering
├── network.py       # NetworkManager keyfile rendering
├── service.py       # systemd/user installation plans
├── transport.py     # injectable local/SSH command and file transport
├── manifest.py      # managed payload and architecture plan
├── offline.py       # mounted filesystem provisioning
├── ssh.py           # remote provisioning and cleanup
├── verify.py        # redacted health checks
└── report.py        # safe deployment result

scripts/leolm-deploy.py       # CLI entrypoint
deploy/profiles/              # example only; real profiles ignored
deploy/systemd/               # versioned service/bootstrap templates if needed
tests/deployment/             # fake transport and provisioning tests
tests/documentation/          # CLI/docs consistency tests
docs/configuration.md         # profile and env contract
docs/deployment.md            # one-command workflows and recovery
```

**Structure Decision**: Extend the existing `src/leolm/deployment` package rather than adding another deployment layer. Shared manifests and transports prevent SSH and offline flows from silently diverging; the voice application modules remain unchanged.

## Phase 0: Research Decisions

Research conclusions are recorded in [research.md](./research.md): use target-side installation, protected file transfer, systemd ordering, NetworkManager keyfiles, and fakeable transports.

## Phase 1: Design Outputs

- [data-model.md](./data-model.md) defines profile, plan, managed target, and report state.
- [contracts/cli.md](./contracts/cli.md) defines the user-facing commands, exit behavior, redaction, and idempotency contract.
- [quickstart.md](./quickstart.md) defines automated and Raspberry Pi validation steps.

## Complexity Tracking

No constitution violations. The additional manifest/transport modules are required to make SSH and offline provisioning share one safe contract and remain testable without hardware.
