# LeoLM — Raspberry Pi voice assistant

LeoLM is a voice assistant validated on Raspberry Pi 3 ARM64. Raspberry Pi Zero 2 W wake-word
validation is deferred. Its main flow is local wake word detection, an
Italian voice command, a request to the configured model, and a spoken response.

## Features

- Wake word detection and speech recognition.
- Configurable model, provider, language, and audio devices.
- Temporary conversation context retained for 10 minutes after the last valid interaction.
- Limited network retries and audio-resource cleanup.
- Automatic tests without hardware and opt-in hardware tests.
- Automated PC-to-Raspberry deployment with SSH or offline image staging.

## Installation

For the easiest Raspberry Pi deployment, see [`docs/deployment.md`](docs/deployment.md). For manual
installation, first install the system prerequisites described in
[`docs/system-dependencies.md`](docs/system-dependencies.md), then create the Python environment:

```bash
python3.11 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-dev.txt
```

Configure the variables listed in [`docs/configuration.md`](docs/configuration.md). Never commit
real credentials to the repository.

## Running

```bash
python openai_request.py
```

Say the configured wake word and then speak the command in Italian. Conversation text remains in
memory for 10 minutes after the last valid interaction and is then deleted.

## Configuration

Supported variables are defined in [`docs/configuration.md`](docs/configuration.md) and in
[`examples/.env.example`](examples/.env.example). For PC-to-Raspberry deployment, see
[`docs/deployment.md`](docs/deployment.md). The model, endpoint, language, wake word, assets, audio
input/output selectors, timeout, retry policy, and context lifetime are configurable.

## Privacy and online services

See [`docs/privacy.md`](docs/privacy.md). Speech recognition, the language model, text-to-speech,
and wake word providers may send data to configured online services and depend on their policies
and network availability.

## Tests

The automatic suite does not require devices or network access:

```bash
pytest -q
```

Hardware tests are opt-in:

```bash
pytest -m hardware tests/hardware -q
```

Dependencies and system prerequisites are listed in `requirements.txt`, `requirements-dev.txt`,
and [`docs/system-dependencies.md`](docs/system-dependencies.md).

## Troubleshooting

- If a key is missing, check the variable name without putting its value in logs.
- If the wake word is unavailable, check `LEOLM_VOSK_MODEL_PATH` and run the documented PC-side model acquisition command.
- If an audio device cannot be found, use a configurable selector and run the opt-in hardware tests.
- If a remote service does not respond, LeoLM performs at most the configured retries and returns to listening.

## Documentation validation

Before a release, run the offline validator and checklist:

```bash
python scripts/check_docs.py --root .
pytest tests/documentation -q
```

See [`docs/release-checklist.md`](docs/release-checklist.md) for the complete release verification.

## License

The project is distributed under the license described in `LICENSE.txt`.
