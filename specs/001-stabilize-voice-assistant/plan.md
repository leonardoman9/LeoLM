# Implementation Plan: Stabilize Voice Assistant

**Branch**: `001-stabilize-voice-assistant` | **Date**: 2026-10-29 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-stabilize-voice-assistant/spec.md`

**Note**: This template is filled in by the `$speckit-plan` command; its definition describes the execution workflow.

## Summary

Stabilizzare l'assistente vocale mantenendo il flusso wake word → riconoscimento → richiesta al
modello → risposta vocale, separando configurazione, servizi remoti, sessione conversazionale e
risorse audio. La migrazione partirà dal monolite esistente e introdurrà adapter sostituibili,
cleanup deterministico, contesto temporaneo di 10 minuti, retry di rete limitati e test automatici
senza hardware.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.11 baseline; Python 3.14 è l'ultima versione verificata nell'ambiente
di sviluppo corrente. Python 3.9 non è supportato perché il codice usa annotazioni moderne.

**Primary Dependencies**: `python-dotenv`, `requests`, `SpeechRecognition`, `PyAudio`, `pvporcupine`,
`gTTS`, `numpy`, `scipy`, `colorama`; `pytest` per i test. `openai` e `vosk` non sono importati dal
percorso attuale e vanno rimossi dalle dipendenze runtime finché non esiste un requisito che li usi.
I prerequisiti di sistema includono ALSA/PortAudio,
`flac` e un player audio configurato.

**Storage**: Nessun database. Configurazione da variabili d'ambiente; contesto conversazionale solo
in memoria per 10 minuti dall'ultima interazione valida; audio e file TTS temporanei rimossi dopo l'uso.

**Testing**: `pytest` con mock/fake per rete, wake word, speech recognition e audio; suite hardware
separata e opt-in per dispositivi ALSA reali.

**Target Platform**: Raspberry Pi Zero 2 W, Linux, rete necessaria per i servizi online e dispositivi
audio locali compatibili.

**Project Type**: Assistente vocale CLI/daemon locale.

**Performance Goals**: Nessuna operazione automatica deve bloccarsi oltre i timeout configurati;
massimo 3 tentativi per richiesta remota; il percorso audio deve usare buffer e processi compatibili
con la RAM del target; il contesto deve scadere esattamente dopo 10 minuti di inattività.

**Constraints**: Nessuna API key nei log; nessuna installazione con privilegi durante il runtime;
nessun accesso hardware nella suite automatica; nessuna dipendenza da indici o nomi audio fissi;
servizi online soggetti a timeout, errori e limiti di rete.

**Scale/Scope**: Un utente e una sessione vocale per processo, con una sola conversazione attiva;
scope limitato alla stabilizzazione dell'attuale flusso italiano e alla sua installazione/testabilità.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Sicurezza: PASS — segreti solo da ambiente, sanitizzazione obbligatoria, contesto temporaneo.
- Installazione riproducibile: PASS — dipendenze e prerequisiti saranno dichiarati e versionati.
- Test senza hardware: PASS — adapter e fake separano la suite automatica da ALSA e servizi reali.
- Risorse audio: PASS — ownership esplicita e cleanup in ogni percorso di uscita.
- Configurazione: PASS — modello, servizi, wake word, dispositivi e timeout sono configurabili.
- Modularità: PASS — confini per configurazione, rete, sessione e audio.
- Errori di rete: PASS — timeout, 3 tentativi massimi, backoff e fallback all'ascolto.
- Documentazione: PASS — README, ambiente, privacy e dipendenze fanno parte del piano.
- Risorse Raspberry Pi: PASS — una sola sessione, buffer limitati, file temporanei e dipendenze
  verificate sul target.

## Project Structure

### Documentation (this feature)

```text
specs/001-stabilize-voice-assistant/
├── plan.md              # This file ($speckit-plan command output)
├── research.md          # Phase 0 output ($speckit-plan command)
├── data-model.md        # Phase 1 output ($speckit-plan command)
├── quickstart.md        # Phase 1 output ($speckit-plan command)
├── contracts/           # Phase 1 output ($speckit-plan command)
└── tasks.md             # Phase 2 output ($speckit-tasks command - NOT created by $speckit-plan)
```

### Source Code (repository root)

```text
src/leolm/
├── __init__.py
├── config.py          # environment loading and validation
├── errors.py          # sanitized domain errors
├── audio.py           # device resolution and resource ownership
├── wakeword.py        # wake-word adapter
├── speech.py          # speech recognition adapter
├── llm.py             # remote model adapter and retry policy
├── tts.py             # synthesis and temporary output cleanup
├── session.py         # conversation context and inactivity timer
└── cli.py             # startup, lifecycle and user-facing messages

tests/
├── unit/              # no hardware, network or system mutation
├── integration/       # fakes across the voice-session boundary
└── hardware/          # explicit opt-in ALSA/device checks

docs/
└── privacy.md         # service data flow and retention boundary

examples/
└── .env.example       # non-secret configuration contract
```

**Structure Decision**: Evolvere il singolo script verso un package `src/leolm` con adapter sottili,
lasciando `openai_request.py` come entry point compatibile durante la migrazione. I test sono separati
per isolamento, integrazione con fake e hardware reale; non si introduce un database o un servizio web.

## Complexity Tracking

Nessuna violazione della costituzione richiede una giustificazione.
