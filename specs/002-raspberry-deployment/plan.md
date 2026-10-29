# Implementation Plan: Raspberry Deployment Profiles

**Branch**: `002-raspberry-deployment` | **Date**: 2026-10-29 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/002-raspberry-deployment/spec.md`

## Summary

Aggiungere un flusso di provisioning riproducibile dal PC per Raspberry Pi Zero 2 W, basato su profili `.env` indipendenti e validati. Lo stesso profilo alimenterà sia la preparazione offline di un filesystem/immagine sia il deployment remoto via SSH. La destinazione riceverà applicazione, ambiente Python, segreti protetti, configurazione Wi-Fi e unità systemd per l'avvio automatico dopo la rete; il comportamento vocale dell'applicazione resterà invariato.

## Technical Context

**Language/Version**: Python 3.11–3.14 per i tool e il runtime, coerente con `pyproject.toml`

**Primary Dependencies**: libreria standard Python per parsing/validazione e filesystem; `rsync`/`ssh` per il trasporto remoto; NetworkManager e systemd sul target; dipendenze LeoLM già definite nei requirements; bootstrap target-side per immagini cross-architettura

**Storage**: profili `.env` sul PC fuori dal repository; file `.env` runtime e asset sotto una directory di servizio sul Raspberry; configurazione Wi-Fi gestita dal NetworkManager

**Testing**: `pytest` con filesystem temporaneo e fake transport/systemd; test hardware separati e opt-in

**Target Platform**: PC Linux/macOS per provisioning; Raspberry Pi OS Bookworm Lite a 32-bit o 64-bit su Raspberry Pi Zero 2 W, con systemd e NetworkManager

**Project Type**: tool CLI di provisioning e deployment per applicazione Python voice assistant

**Performance Goals**: validazione profilo e dry-run in pochi secondi; avvio del servizio entro 60 secondi dalla disponibilità della rete; nessun busy-loop durante retry o crash

**Constraints**: CPU/RAM/storage limitati, niente segreti nei log o nei keyfile Wi-Fi non protetti, nessuna modifica parziale dopo una validazione fallita, idempotenza, compatibilità con provisioning offline e SSH anche cross-architettura, nessuna porta o servizio MCP esposto

**Scale/Scope**: profili indipendenti per almeno tre dispositivi; un contratto di profilo, due transport backend e un'unità systemd per dispositivo

## Constitution Check

*GATE: PASS prima della ricerca e PASS dopo il design.*

- **Sicurezza**: PASS. I profili reali restano fuori dal repository; trasferimenti e report redigono segreti; il file runtime ha permessi restrittivi.
- **Installazione riproducibile**: PASS. Il profilo, il manifest dei file, i requisiti e il servizio systemd sono versionati e applicati da un CLI deterministico.
- **Test senza hardware**: PASS. Il backend filesystem temporaneo e fake per SSH/systemd coprono il flusso senza Raspberry reale.
- **Risorse audio**: PASS. Il servizio avvia una sola istanza e systemd riavvia dopo cleanup del processo; il provisioning non apre dispositivi audio.
- **Configurazione esplicita**: PASS. Modello, rete, wake word, selettori audio, endpoint e timeout vengono dal profilo e dal contratto runtime.
- **Modularità**: PASS. Parsing/validation, transport, rendering dei file e report sono separati; l'applicazione LeoLM non incorpora logica di provisioning.
- **Errori di rete**: PASS. NetworkManager precede il servizio; SSH e runtime hanno timeout e retry limitati, con recovery documentato.
- **Documentazione reale**: PASS. La feature include template, contratto, procedure PC→Raspberry e quickstart verificabile.
- **Raspberry Pi Zero 2 W**: PASS. Un solo processo applicativo, ambiente dedicato, logging controllato e nessun componente remoto aggiuntivo.

## Project Structure

### Documentation (this feature)

```text
specs/002-raspberry-deployment/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── profile.md
│   ├── provisioning.md
│   └── service.md
└── tasks.md                 # creato da $speckit-tasks
```

### Source Code (repository root)

```text
deploy/
├── profiles/
│   └── example.env           # solo placeholder, nessun profilo reale
├── systemd/
│   ├── leolm.service         # template con percorsi/utente configurabili
│   └── leolm-bootstrap.service # installazione cross-arch al primo boot
└── README.md                 # procedura operativa sintetica
scripts/
└── leolm-deploy.py           # validate, dry-run, provision-offline, deploy-ssh, verify
src/leolm/
└── ...                       # runtime invariato; eventuali aggiunte solo per bootstrap .env
tests/
├── deployment/
│   ├── fixtures/
│   ├── test_profile_validation.py
│   ├── test_offline_provisioning.py
│   ├── test_ssh_transport.py
│   ├── test_sanitized_reports.py
│   └── test_bootstrap.py
└── hardware/                 # prove fisiche separate
```

**Structure Decision**: il deployer resta un tool di supporto in `scripts/`, con moduli interni piccoli o un package dedicato se necessario durante l'implementazione. I template di destinazione vengono renderizzati da un unico modello per evitare divergenze fra offline e SSH. Il provisioning offline rileva l'architettura: installa direttamente solo quando compatibile, altrimenti prepara `leolm-bootstrap.service` per l'installazione target-side al primo boot. Il runtime LeoLM legge la configurazione installata ma non gestisce provisioning, Wi-Fi o privilegi.

## Complexity Tracking

Nessuna violazione della costituzione. Due transport backend sono richiesti esplicitamente per supportare offline e SSH; condividono validazione, manifest e rendering per non duplicare la logica.
