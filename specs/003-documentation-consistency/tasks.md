# Tasks: Documentation Consistency

**Input**: Design documents from `/specs/003-documentation-consistency/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

**Tests**: inclusi perché la specifica richiede un controllo automatico offline e fixture per errori/warning.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: predisporre il set documentale canonico e la struttura del validator.

- [X] T001 Creare la struttura `tests/documentation/fixtures/` e `tests/documentation/` secondo `specs/003-documentation-consistency/plan.md`
- [X] T002 [P] Creare `docs/configuration.md` come contratto canonico con nome, obbligatorietà, default, formato, esempio sicuro e comportamento d'errore per ogni variabile
- [X] T003 [P] Creare `docs/troubleshooting.md` con rete, timeout/retry, audio, wake word, cleanup, contesto di 10 minuti e recupero
- [X] T004 [P] Creare la checklist release documentale in `docs/release-checklist.md` con installazione, comandi, link, dipendenze, privacy, compatibilità e segreti
- [X] T005 [P] Creare lo scheletro del validator offline in `scripts/check_docs.py` con CLI `--root` e `--json`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: definire parsing, finding e regole comuni prima delle user story.

- [X] T006 Definire `ValidationFinding` e `DocumentationValidationReport` in `scripts/check_docs.py` con severità `error`/`warning`, codice, file, riga e output senza segreti
- [X] T007 [P] Implementare il caricamento delle due tabelle Markdown `## Runtime variables`/`## Deployment variables` con colonne fisse e parsing dello `scope` in `scripts/check_docs.py`
- [X] T008 [P] Implementare la scansione dei file Markdown, template `.env` e profili deployment in `scripts/check_docs.py` senza inizializzare audio o rete
- [X] T009 [P] Creare fixture documentali valide e invalide in `tests/documentation/fixtures/`, includendo link rotto, variabile sconosciuta, placeholder e valore sensibile
- [X] T010 [P] Definire in `tests/documentation/conftest.py` fixture temporanee per repository e contratto canonico

**Checkpoint**: il validator può leggere un repository fixture e produrre un report strutturato senza dipendenze hardware o rete.

---

## Phase 3: User Story 1 - Guida unica e affidabile (Priority: P1) 🎯 MVP

**Goal**: rendere README e guide coerenti con il comportamento implementato e con il contratto di configurazione.

**Independent Test**: un lettore segue `readme.md`, trova installazione, configurazione, avvio, test, deployment e troubleshooting, e ogni variabile/comando rimanda a un documento corrente.

### Tests for User Story 1

- [X] T011 [P] [US1] Testare presenza e contenuto minimo di `readme.md`, `docs/configuration.md`, `docs/deployment.md`, `docs/privacy.md`, `docs/system-dependencies.md`, `docs/troubleshooting.md` e `docs/release-checklist.md` in `tests/documentation/test_documentation_set.py`
- [X] T012 [P] [US1] Testare coerenza di scope, nomi/default e allowlist tra `docs/configuration.md`, `examples/.env.example` e `deploy/profiles/example.env` in `tests/documentation/test_configuration_contract.py`

### Implementation for User Story 1

- [X] T013 [US1] Aggiornare `readme.md` per usare `docs/configuration.md` come fonte canonica e includere installazione, avvio, test, deployment e troubleshooting correnti
- [X] T014 [US1] Allineare `examples/.env.example` solo alla tabella `Runtime variables` di `docs/configuration.md`, mantenendo placeholder fittizi e nessun segreto reale
- [X] T015 [US1] Allineare `deploy/profiles/example.env` alle tabelle runtime/deployment di `docs/configuration.md` e documentare la differenza tra template e profili reali
- [X] T016 [US1] Aggiornare `docs/deployment.md`, `docs/system-dependencies.md` e `docs/troubleshooting.md` con comandi, percorsi, versioni e messaggi effettivamente supportati
- [X] T017 [US1] Aggiornare `docs/privacy.md` per distinguere dati locali, audio/testo inviati online, retention del contesto, retention dei provider e segreti di deployment
- [X] T018 [US1] Aggiungere in `docs/release-checklist.md` la verifica della documentazione dopo stabilizzazione e deployment, prima della release o distribuzione immagini

**Checkpoint**: la documentazione principale è utilizzabile senza consultare specifiche storiche o modificare codice.

---

## Phase 4: User Story 2 - Privacy, rete e deployment comprensibili (Priority: P1)

**Goal**: spiegare chiaramente profili, Wi-Fi, boot automatico, provider online, segreti e recupero su più Raspberry.

**Independent Test**: la documentazione permette di configurare tre dispositivi distinti, capire quali dati escono dal Raspberry e recuperare rete/servizio senza stampare segreti.

### Tests for User Story 2

- [X] T019 [P] [US2] Testare che documentazione e template non contengano pattern di API key, password, token o dati vocali in `tests/documentation/test_security_docs.py`
- [X] T020 [P] [US2] Testare presenza di privacy, deployment, dipendenze e troubleshooting con riferimenti a retention 600 secondi e provider in `tests/documentation/test_operational_docs.py`

### Implementation for User Story 2

- [X] T021 [US2] Documentare in `docs/deployment.md` provisioning offline e SSH, bootstrap cross-architettura, profili indipendenti, keyfile Wi-Fi `0600`, systemd, log e cleanup
- [X] T022 [US2] Documentare in `docs/privacy.md` che API key, password Wi-Fi e profili reali restano fuori dal repository e che i provider online controllano la propria retention
- [X] T023 [US2] Documentare in `docs/system-dependencies.md` la matrice Raspberry Pi OS Bookworm 32/64-bit, Python, NetworkManager, systemd, audio e dipendenze runtime/dev/hardware
- [X] T024 [US2] Documentare in `docs/troubleshooting.md` timeout, retry limitati, rete assente, errori audio, asset wake word, cleanup e ritorno alla wake word
- [X] T025 [US2] Verificare e correggere i link interni tra `readme.md`, `docs/`, `deploy/`, `examples/` e `scripts/` senza introdurre riferimenti a feature MCP non implementate

**Checkpoint**: un operatore può distribuire e diagnosticare più Raspberry senza confondere credenziali, hostname o dati vocali.

---

## Phase 5: User Story 3 - Validazione automatica della documentazione (Priority: P2)

**Goal**: bloccare regressioni locali e segreti, segnalando invece i link esterni non raggiungibili come warning.

**Independent Test**: `python scripts/check_docs.py` passa sul repository reale e fallisce in modo deterministico sulle fixture con link locale rotto, variabile sconosciuta, placeholder o segreto.

### Tests for User Story 3

- [X] T026 [P] [US3] Testare link locali validi e `BROKEN_LOCAL_LINK` bloccante in `tests/documentation/test_check_docs_links.py`
- [X] T027 [P] [US3] Testare URL esterno non raggiungibile come `EXTERNAL_LINK_UNREACHABLE` warning non bloccante in `tests/documentation/test_check_docs_external.py`
- [X] T028 [P] [US3] Testare variabili sconosciute, default divergenti e variabili obbligatorie mancanti in `tests/documentation/test_check_docs_config.py`
- [X] T029 [P] [US3] Testare placeholder, pattern di segreti e output JSON senza valori sensibili in `tests/documentation/test_check_docs_security.py`
- [X] T030 [P] [US3] Testare exit code `0`, `1` e `2` del CLI in `tests/documentation/test_check_docs_cli.py`

### Implementation for User Story 3

- [X] T031 [US3] Implementare controllo di link Markdown e percorsi locali in `scripts/check_docs.py`, classificando i link locali invalidi come errori
- [X] T032 [US3] Implementare il flag `--check-external-links` in `scripts/check_docs.py`, classificando timeout/DNS/HTTP esterni come `EXTERNAL_LINK_UNREACHABLE` warning e mantenendo il comportamento predefinito offline
- [X] T033 [US3] Implementare confronto tra contratto canonico, `examples/.env.example` e `deploy/profiles/example.env` in `scripts/check_docs.py`
- [X] T034 [US3] Implementare scansione di placeholder, pattern di segreti e comandi vietati (`sudo`, `rm -rf`, installazioni runtime, credenziali inline, porte/MCP) con messaggi redatti in `scripts/check_docs.py`
- [X] T035 [US3] Implementare report testuale/JSON e exit status `0` successo, `1` errore di validazione, `2` uso/errore interno in `scripts/check_docs.py`
- [X] T036 [US3] Integrare `python scripts/check_docs.py` nella checklist release e nella documentazione di sviluppo senza richiedere hardware, rete reale o credenziali

**Checkpoint**: il controllo documentale è deterministico offline e adatto alla CI.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: validazione finale, coerenza release e rimozione degli ultimi riferimenti obsoleti.

- [X] T037 [P] Eseguire `pytest tests/documentation -q` e correggere solo regressioni della documentazione in `tests/documentation/`
- [X] T038 [P] Eseguire `python scripts/check_docs.py --root . --json` e verificare che il report non contenga segreti
- [X] T039 [P] Eseguire tutti gli scenari di `specs/003-documentation-consistency/quickstart.md` senza microfono, speaker, Raspberry o rete reale
- [X] T040 [P] Cercare e rimuovere riferimenti operativi obsoleti a `specs/001-stabilize-voice-assistant/` in `readme.md`, `docs/`, `deploy/` ed `examples/`
- [X] T041 Aggiornare `readme.md` con il comando finale del validator e il link alla checklist release
- [X] T042 Verificare la coerenza tra comportamento implementato, `docs/configuration.md`, `docs/deployment.md`, `docs/privacy.md` e `docs/troubleshooting.md`
- [X] T043 Eseguire la checklist release `docs/release-checklist.md` e registrare l'esito senza hardware o credenziali reali

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: nessuna dipendenza; T002–T005 possono procedere in parallelo dopo T001.
- **Foundational (Phase 2)**: dipende da Setup; T007–T010 possono procedere in parallelo dopo lo scheletro T005/T006.
- **User Story 1 (Phase 3)**: dipende da Foundational ed è l'MVP documentale.
- **User Story 2 (Phase 4)**: dipende da US1 per evitare duplicazioni e riferimenti contraddittori.
- **User Story 3 (Phase 5)**: dipende dal contratto/configurazione finale di US1 e dai documenti operativi di US2.
- **Polish (Phase 6)**: dipende da tutte le user story desiderate.

### User Story Dependencies

- **US1 (P1)**: nessuna dipendenza oltre la fase Foundational.
- **US2 (P1)**: dipende da US1 per i nomi canonici e il percorso documentale.
- **US3 (P2)**: dipende da US1/US2 per validare il set documentale finale.

### Parallel Opportunities

- T002–T005 sono parallelizzabili dopo T001.
- T007–T010 sono parallelizzabili dopo T005/T006.
- I test T011/T012 e T019/T020 possono essere scritti in parallelo perché usano file distinti.
- I test T026–T030 sono parallelizzabili tra loro.
- T037–T041 sono parallelizzabili dopo il completamento del validator.

## Parallel Example: User Story 3

```text
Task: T026 [US3] Test link locali in tests/documentation/test_check_docs_links.py
Task: T028 [US3] Test contratto configurazione in tests/documentation/test_check_docs_config.py
Task: T029 [US3] Test sicurezza in tests/documentation/test_check_docs_security.py
```

## Implementation Strategy

### MVP First (User Story 1 only)

1. Completare Setup e Foundational.
2. Consolidare contratto, README e documenti operativi.
3. Verificare che un installatore possa seguire il percorso senza specifiche storiche.

### Incremental Delivery

1. Aggiungere privacy/deployment/compatibilità e verificare tre profili.
2. Implementare il validator offline con test fixture-first.
3. Integrare validator, checklist release e quickstart.
4. Eseguire una revisione finale prima della distribuzione.
