# Quickstart: Offline Panda Wake Word Validation

## Prerequisites

- A Raspberry Pi 3 ARM64 reachable over SSH, with systemd and NetworkManager active.
- USB microphone and USB audio output visible to ALSA.
- A private deployment profile on the PC; it contains Wi-Fi and conversation credentials only, never a Picovoice key.
- The target has adequate free storage for the local model and a working internet connection only while the PC acquires the public asset.

## Prepare the profile

Remove the three Picovoice variables from the private profile and add:

    LEOLM_WAKE_WORD=Panda
    LEOLM_VOSK_MODEL_PATH=models/vosk-model-small-it-0.22
    LEOLM_WAKE_SAMPLE_RATE=16000
    LEOLM_INPUT_DEVICE=USB PnP Sound Device
    LEOLM_OUTPUT_DEVICE=hw:3,0

Do not put any secrets in commands or reports.

## Validate before deploying

1. Run the automated suite on the PC.
2. Validate the profile with the deployment CLI.
3. Run a dry run and confirm that it reports a verified local wake-word asset action and no Picovoice credential requirement.
4. Acquire and verify the pinned Italian asset with the deployment-supported PC-side command.
5. Deploy using the documented SSH workflow.

## Verify on the Pi

1. Confirm that the service is enabled and active.
2. Confirm that the target virtual environment imports the local recognition dependency and that the managed Italian model passes integrity verification.
3. Disconnect the Pi from the internet after deployment and restart the service; it must reach the listening state.
4. Say Panda twenty times at normal distance and record activation count.
5. Say unrelated speech or leave normal room noise for ten minutes and record unintended activations.
6. After an activation, issue a short Italian command and verify model response, synthesized speech, and playback through the configured USB output.

The deployment is fully verified only after all steps above succeed. See runtime-configuration.md and data-model.md for expected configuration and statuses.

