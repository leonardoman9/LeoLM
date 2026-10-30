# System dependencies and compatibility

## Supported matrix

The current offline wake-word release is validated only on Raspberry Pi 3 ARM64 with systemd and
NetworkManager active. The available target uses Debian 13 (Trixie), Python 3.13, and a 64-bit
kernel. Raspberry Pi Zero 2 W and armhf validation are deferred and must not be treated as supported
until their separate hardware verification is complete.

The provisioning PC requires Python 3.11+, `ssh`, and write access to a mounted filesystem when
preparing an image. SSH provisioning installs `python3`, `python3-dev`, `python3-venv`,
`python3-pip`, `build-essential`, `libportaudio2`, `portaudio19-dev`, `flac`, `alsa-utils`,
`mpg123`, and `network-manager` on the target, then installs `requirements.txt` in the target
virtual environment. Python 3.11 through 3.13 is supported by the project metadata.
`requirements-dev.txt` is for development and tests only. Offline staging performs the same
installation on first boot through the bootstrap service.

## Audio and tests

The real voice flow requires Linux, ALSA/PortAudio, PyAudio, Vosk with the verified local Italian
model, `flac` for speech recognition, `mpg123` for playback, and a USB microphone plus a USB audio
output visible to ALSA. The input
selector is matched by PortAudio device index or name; the output selector is passed to `mpg123 -a`
and should therefore be a valid ALSA output device. System packages are installed during
provisioning, never when the assistant starts, and never by the automatic test suite.

Offline verification checks configuration only (`configured`). The `hardware_verified` state
requires the opt-in tests on the Raspberry Pi 3 with its real microphone and speaker. The Vosk
model is acquired and checked on the deployment PC; it is never downloaded when LeoLM starts.
