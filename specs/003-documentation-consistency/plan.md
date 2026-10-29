# Implementation Plan: Documentation Consistency

**Branch**: `003-documentation-consistency` | **Date**: 2026-10-29 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/003-documentation-consistency/spec.md`

## Summary

Consolidare la documentazione operativa di LeoLM dopo la stabilizzazione applicativa e il deployment, usando un contratto di configurazione canonico e un controllo offline automatico. Il piano mantiene il comportamento vocale esistente, rende verificabili link, variabili, comandi, dipendenze, placeholder e pattern di segreti, e separa chiaramente le verifiche documentali dalle prove hardware.

## Technical Context

**Language/Version**: Python 3.11–3.14, coerente con `pyproject.toml`

**Primary Dependencies**: libreria standard Python per il validatore; `pytest` per i test; nessuna nuova dipendenza runtime prevista

**Storage**: file Markdown, template `.env` e report testuali; nessun database

**Testing**: `pytest` senza hardware o rete; test del validatore tramite fixture temporanee

**Target Platform**: workstation/CI Linux e Raspberry Pi Zero 2 W per la documentazione di deployment

**Project Type**: progetto Python CLI/voice assistant con documentazione operativa e tool di validazione

**Performance Goals**: controllo completo del repository in pochi secondi su workstation e con consumo minimo sul Raspberry; nessuna richiesta di rete necessaria

**Constraints**: niente credenziali reali, niente inizializzazione audio, niente hardware, niente installazione automatica durante il controllo; link esterni non devono rendere non deterministica la validazione

**Scale/Scope**: una documentazione principale, documenti specializzati, template e profili di deployment per più Raspberry; un validatore locale e una suite di test

## Constitution Check

*GATE: PASS prima della ricerca e PASS dopo il design.*

- **Sicurezza**: PASS. Il validatore cerca pattern di segreti e gli esempi usano solo placeholder fittizi; l'output non ristampa valori sensibili.
- **Installazione riproducibile**: PASS. Dipendenze, versioni compatibili, profili e comandi sono documentati e controllati da file versionati.
- **Test senza hardware**: PASS. Il validatore e i suoi test usano solo filesystem e fixture; nessun accesso a microfono, speaker o rete reale.
- **Risorse audio**: PASS. La feature documenta il cleanup già previsto e non introduce codice che possieda risorse audio.
- **Configurazione esplicita**: PASS. `docs/configuration.md` è il contratto canonico per nomi, default, formato e obbligatorietà.
- **Modularità**: PASS. Il controllo documentale è separato dal runtime e invocabile come tool indipendente.
- **Errori di rete**: PASS. La documentazione descrive timeout/retry e il validatore tratta i link esterni non raggiungibili come warning.
- **Documentazione reale**: PASS. Il controllo confronta la documentazione con il contratto e con i file realmente presenti.
- **Raspberry Pi Zero 2 W**: PASS. La soluzione è leggera, offline e non aggiunge dipendenze runtime.

## Project Structure

### Documentation (this feature)

```text
specs/003-documentation-consistency/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── configuration.md
│   └── validation.md
└── tasks.md                 # creato da $speckit-tasks, non da questo piano
```

### Source Code (repository root)

```text
readme.md                    # punto di ingresso operativo
docs/
├── configuration.md         # fonte canonica del contratto .env
├── deployment.md            # provisioning PC → Raspberry e boot automatico
├── privacy.md               # dati locali, dati inviati e retention
├── system-dependencies.md   # dipendenze OS/Python e compatibilità
└── troubleshooting.md       # rete, audio, wake word e recupero
examples/
└── .env.example             # esempio sicuro verificato contro il contratto
scripts/
└── check_docs.py            # validatore offline con exit code deterministico
tests/
├── documentation/
│   ├── fixtures/             # documenti volutamente validi/invalidi
│   └── test_check_docs.py
└── hardware/                # separati e non richiesti dal controllo documentale
```

**Structure Decision**: mantenere il layout Python esistente e aggiungere un piccolo tool in `scripts/` con test dedicati. `docs/configuration.md` diventa la fonte canonica operativa; README, template `.env` e profili deployment la referenziano e vengono validati contro di essa. La specifica storica sotto `specs/001-stabilize-voice-assistant/` resta materiale di progetto, non una guida per l'installatore.

## Complexity Tracking

Nessuna violazione della costituzione. Non si introduce un framework documentale o un servizio remoto: il controllo usa la libreria standard per limitare dipendenze, memoria e superfici di errore.
