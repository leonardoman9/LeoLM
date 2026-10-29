# System dependencies and compatibility

## Supported matrix

The supported target is Raspberry Pi OS Bookworm Lite, 32-bit or 64-bit, on Raspberry Pi Zero 2 W,
with systemd and NetworkManager active. Older versions or distributions without these components
are not automatically supported.

The provisioning PC requires Python 3.11+, `ssh`, and write access to a mounted filesystem when
preparing an image. SSH provisioning installs `python3`, `python3-venv`, `python3-pip`,
`libportaudio2`, `portaudio19-dev`, `flac`, `alsa-utils`, and `network-manager` on the target, then
installs `requirements.txt` in the target virtual environment. `requirements-dev.txt` is for
development and tests only. Offline staging performs the same installation on first boot through
the bootstrap service.

## Audio and tests

The real voice flow requires Linux, ALSA/PortAudio, PyAudio, `flac` for speech recognition, and a
configured audio player. System packages are installed during provisioning, never when the
assistant starts, and never by the automatic test suite.

Offline verification checks configuration only (`configured`). The `hardware_verified` state
requires the opt-in tests on a Raspberry Pi with a real microphone and speaker.
