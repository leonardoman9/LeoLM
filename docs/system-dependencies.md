# Dipendenze e compatibilità di sistema

## Matrice supportata

Il target supportato è Raspberry Pi OS Bookworm Lite 32-bit o 64-bit su Raspberry Pi Zero 2 W, con systemd e NetworkManager attivi. Versioni precedenti o distribuzioni prive di queste componenti non sono supportate automaticamente.

Il PC di provisioning richiede Python 3.11+, `ssh` e accesso in scrittura al filesystem quando si prepara un'immagine montata. Il provisioning SSH installa sul target `python3`, `python3-venv`, `python3-pip`, `libportaudio2`, `portaudio19-dev`, `flac`, `alsa-utils` e `network-manager`, poi installa `requirements.txt` nel virtual environment target; `requirements-dev.txt` è riservato a sviluppo e test. Lo staging offline esegue la stessa installazione al primo boot tramite bootstrap.

## Audio e test

Per il flusso vocale reale servono Linux, ALSA/PortAudio, PyAudio, `flac` per il riconoscimento e un player audio configurato. I pacchetti di sistema vengono installati durante il provisioning, mai all'avvio dell'assistente e mai dalla suite automatica.

La verifica offline controlla solo la configurazione (`configured`). La verifica `hardware_verified` richiede i test opt-in su Raspberry con microfono e speaker reali.
