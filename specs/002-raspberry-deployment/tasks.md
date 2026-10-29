# Tasks: Raspberry Deployment Profiles

**Input**: Design documents from `/specs/002-raspberry-deployment/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

**Tests**: inclusi perché la specifica richiede validazione automatica senza Raspberry reale e test separati per hardware.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: predisporre struttura, template e convenzioni del tool di deployment.

- [X] T001 Creare la struttura `deploy/profiles/`, `deploy/systemd/`, `tests/deployment/`, `tests/deployment/fixtures/` e `src/leolm/deployment/` secondo `specs/002-raspberry-deployment/plan.md`
- [X] T002 [P] Creare il template sicuro `deploy/profiles/example.env` con tutte le variabili del contratto e placeholder fittizi
- [X] T003 [P] Creare i template `deploy/systemd/leolm.service` e `deploy/systemd/leolm-bootstrap.service`, con segnaposto per utente, working directory, environment file, restart policy e bootstrap one-shot cross-architettura
- [X] T004 [P] Aggiornare `.gitignore` per escludere profili reali, copie temporanee, environment runtime e artefatti di staging senza escludere `deploy/profiles/example.env`
- [X] T005 [P] Documentare i prerequisiti PC e target in `deploy/README.md`, inclusi Python, NetworkManager, systemd, SSH e matrice Raspberry Pi OS Bookworm 32-bit/64-bit

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: costruire i contratti e le primitive condivise prima delle user story.

- [X] T006 Implementare il parser immutabile `DeviceProfile` in `src/leolm/deployment/profile.py` per `.env`, con sezioni device, Wi-Fi e LeoLM definite in `specs/002-raspberry-deployment/contracts/profile.md`
- [X] T007 Implementare la validazione dei campi in `src/leolm/deployment/profile.py`, includendo campi obbligatori, UTF-8, hostname Linux, paese radio, valori runtime e selettori audio senza stampare valori segreti
- [X] T008 [P] Definire errori sicuri e report sanificati in `src/leolm/deployment/errors.py` e `src/leolm/deployment/report.py`, assicurando che password, API key, access key ed environment completo non compaiano nei messaggi
- [X] T009 [P] Definire le interfacce `Transport`, `TargetFileSystem` e `CommandRunner` in `src/leolm/deployment/ports.py` per supportare filesystem temporaneo, SSH fake e target reale senza accoppiarli al runtime vocale
- [X] T010 Aggiungere test unitari del contratto profilo in `tests/deployment/test_profile_validation.py` per campi validi, campi mancanti, hostname/encoding errati e redazione dei segreti
- [X] T011 [P] Aggiungere fixture di profili validi, incompleti, con placeholder e con valori invalidi in `tests/deployment/fixtures/`
- [X] T012 Aggiornare `src/leolm/deployment/__init__.py` e il packaging in `pyproject.toml` per includere il nuovo package senza aggiungere dipendenze runtime non necessarie

**Checkpoint**: il profilo viene letto e validato offline; nessuna operazione modifica una destinazione non ancora validata.

---

## Phase 3: User Story 1 - Preparare un profilo da PC (Priority: P1) 🎯 MVP

**Goal**: creare, validare e mantenere profili indipendenti per più Raspberry senza segreti nel repository o nei log.

**Independent Test**: due fixture con hostname, SSID, selettori audio e impostazioni LeoLM diversi vengono validate separatamente; i report non contengono password/API key e i profili reali risultano esclusi dal versionamento.

### Tests for User Story 1

- [X] T013 [US1] Testare due profili indipendenti e la loro serializzazione sanificata in `tests/deployment/test_profile_validation.py`
- [X] T014 [US1] Testare il rifiuto di segreti reali nel template e la non esposizione nei log in `tests/deployment/test_sanitized_reports.py`
- [X] T015 [P] [US1] Testare il comando `validate` e gli exit code del CLI in `tests/deployment/test_cli.py`

### Implementation for User Story 1

- [X] T016 [US1] Implementare il renderer del profilo e la allowlist delle variabili in `src/leolm/deployment/profile.py`, mantenendo i nomi `LEOLM_*` coerenti con `src/leolm/config.py`
- [X] T017 [US1] Implementare il comando CLI `validate` con argparse, errori per campo e output sanificato in `scripts/leolm-deploy.py`
- [X] T018 [US1] Implementare `--dry-run` nel CLI `scripts/leolm-deploy.py` per mostrare piano, file, permessi e unità senza scrivere, installare pacchetti o contattare rete
- [X] T019 [US1] Verificare nel codice e nei test che `.gitignore`, template e profili in directory protetta rispettino `specs/002-raspberry-deployment/contracts/profile.md`
- [X] T020 [US1] Aggiornare `examples/.env.example` e `readme.md` per rimandare al profilo deployment senza duplicare nomi o default incompatibili

**Checkpoint**: un installatore può preparare almeno tre profili locali distinti e validarli senza modificare codice o rivelare segreti.

---

## Phase 4: User Story 2 - Provisioning di un Raspberry (Priority: P1)

**Goal**: applicare lo stesso profilo a filesystem/immagine offline o target SSH con staging, permessi, Wi-Fi e servizio equivalenti.

**Independent Test**: un filesystem temporaneo viene provisionato due volte con lo stesso profilo; la seconda esecuzione è idempotente, il file segreto ha permessi restrittivi e una validazione fallita non modifica il target.

### Tests for User Story 2

- [X] T021 [P] [US2] Testare staging, commit atomico, rollback e idempotenza su filesystem temporaneo in `tests/deployment/test_offline_provisioning.py`
- [X] T022 [P] [US2] Testare il backend SSH con un fake `CommandRunner`, timeout e cleanup delle copie temporanee in `tests/deployment/test_ssh_transport.py`
- [X] T023 [P] [US2] Testare validazione iniziale fallita e destinazione non valida senza modifiche in `tests/deployment/test_provisioning_safety.py`
- [X] T024 [P] [US2] Testare permessi e ownership attesi per environment, profilo e directory runtime in `tests/deployment/test_permissions.py`

### Implementation for User Story 2

- [X] T025 [US2] Implementare backend filesystem offline con rilevamento architettura, marker target, staging temporaneo, manifest, copia del codice LeoLM, requirements e asset, installazione diretta solo su architettura compatibile oppure preparazione del bootstrap cross-architettura, e commit/rollback in `src/leolm/deployment/offline.py`; `requirements-dev.txt` resta requisito del PC/test
- [X] T026 [US2] Implementare backend SSH con comandi allowlisted, timeout, trasferimento temporaneo di codice/asset, creazione del virtual environment, installazione runtime riproducibile da `requirements.txt` e rimozione garantita in `src/leolm/deployment/ssh.py`
- [X] T027 [US2] Implementare rendering dell'environment runtime e degli asset in `src/leolm/deployment/render.py`, con file segreto separato e permessi `0600`
- [X] T028 [US2] Implementare configurazione NetworkManager in `src/leolm/deployment/network.py`, con SSID/password/country/autoconnect, keyfile root-owned `0600`, cleanup sicuro e rifiuto documentato dei casi non supportati
- [X] T029 [US2] Implementare creazione dell'utente/gruppo dedicati, directory runtime, ownership, installazione delle unità `deploy/systemd/leolm.service` e `deploy/systemd/leolm-bootstrap.service`, `network-online.target`, restart delay, start limits e disabilitazione del bootstrap riuscito in `src/leolm/deployment/service.py`
- [X] T030 [US2] Implementare i comandi `provision-offline` e `deploy-ssh` in `scripts/leolm-deploy.py` usando gli stessi manifest e renderer
- [X] T031 [US2] Implementare la verifica sanificata di file, permessi, Wi-Fi, servizio e audio in `src/leolm/deployment/verify.py` e collegarla al comando `verify` in `scripts/leolm-deploy.py`
- [X] T032 [US2] Implementare il comando `deploy-ssh` affinché conservi il profilo sorgente solo sul PC e rimuova le copie temporanee contenenti segreti al termine, anche in caso di errore

**Checkpoint**: provisioning offline e SSH producono configurazioni equivalenti, sono ripetibili e non lasciano segreti nei report o nei file temporanei.

---

## Phase 5: User Story 3 - Avvio autonomo dopo l'accensione (Priority: P1)

**Goal**: fare connettere il Raspberry al Wi-Fi e avviare LeoLM automaticamente dopo la rete, con restart controllato e una sola istanza.

**Independent Test**: fake systemd/NetworkManager simula rete disponibile, rete ritardata e crash; il servizio attende la rete, riavvia con ritardo e non produce processi concorrenti o output con segreti.

### Tests for User Story 3

- [X] T033 [P] [US3] Testare il rendering dell'unità systemd e l'ordering `network-online.target` in `tests/deployment/test_service_unit.py`
- [X] T034 [US3] Testare rete ritardata, restart delay, start limits, una sola istanza e avvio entro 60 secondi con fake clock/runner in `tests/deployment/test_boot_recovery.py`
- [X] T035 [US3] Testare verifiche sanificate per hostname, Wi-Fi, servizio e audio in `tests/deployment/test_sanitized_reports.py`
- [X] T036 [P] [US3] Testare che MCP non venga installato, esposto o aggiunto al servizio in `tests/deployment/test_mcp_boundary.py`

### Implementation for User Story 3

- [X] T037 [US3] Completare `deploy/systemd/leolm.service` con `EnvironmentFile`, utente dedicato, `Restart=on-failure`, `RestartSec`, `StartLimit*` e comando runtime configurabile
- [X] T038 [US3] Implementare controlli e polling con backoff limitato per rete disponibile in `src/leolm/deployment/network.py`, evitando loop aggressivi e rispettando l'ordering del bootstrap one-shot
- [X] T039 [US3] Collegare bootstrap, environment installato e asset wake word al servizio in `src/leolm/deployment/service.py` senza hard-code di hostname, device audio o directory
- [X] T040 [US3] Aggiungere al comando `verify` controlli di boot, rete e stato servizio in `scripts/leolm-deploy.py`, usando solo output redatto
- [X] T041 [US3] Documentare primo boot, recupero SSH, log, sostituzione profilo e rimozione sicura dei segreti in `deploy/README.md` e `docs/deployment.md`

**Checkpoint**: un Raspberry provisionato può avviarsi senza login manuale e recuperare rete/processo secondo una politica verificabile.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: chiudere compatibilità, documentazione e regressioni senza hardware reale.

- [X] T042 [P] Aggiornare `docs/system-dependencies.md` con matrice supportata Raspberry Pi OS Bookworm 32-bit/64-bit, NetworkManager, systemd, Python, audio e prerequisiti SSH
- [X] T043 [P] Aggiornare `docs/privacy.md` con trasferimento dei profili, retention dei segreti sul PC, dati vocali, servizi online e log del deployment
- [X] T044 [P] Aggiungere in `scripts/leolm-deploy.py` un controllo automatico dei profili reali, verificando che solo template e placeholder siano versionati
- [X] T045 [P] Separare e documentare i test hardware in `tests/hardware/README.md`, assicurando che `pytest` di default non richieda dispositivi fisici e distinguendo i risultati `configured`/`hardware_verified`
- [X] T046 Eseguire `pytest -q` e correggere solo le regressioni del runtime direttamente causate dal deployment in `tests/unit/` e `tests/integration/`
- [X] T047 Eseguire tutti gli scenari di `specs/002-raspberry-deployment/quickstart.md` con filesystem temporaneo e fake transport, registrando exit code e tempo totale del percorso di provisioning
- [X] T048 Verificare con tre profili fittizi che hostname, Wi-Fi, audio, segreti e report restino isolati e che nessun log contenga valori sensibili in `tests/deployment/`
- [X] T049 Aggiornare `readme.md` con il percorso PC→Raspberry e i limiti MCP, senza promettere funzionalità non implementate
- [X] T050 [P] Aggiungere una prova hardware opt-in per misurare l'avvio entro 60 secondi dalla rete disponibile in `tests/hardware/test_boot_timing.py`, senza renderla parte della suite automatica predefinita
- [X] T051 Aggiungere in `tests/deployment/test_bootstrap.py` test per rilevamento architettura, staging del bootstrap, esecuzione one-shot, idempotenza e disabilitazione dopo successo

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: nessuna dipendenza; T002–T005 possono procedere in parallelo dopo T001.
- **Foundational (Phase 2)**: dipende da Setup; T008–T011 possono procedere in parallelo dopo i contratti iniziali.
- **User Story 1 (Phase 3)**: dipende da Phase 2; costituisce l'MVP per parsing, validazione e dry-run.
- **User Story 2 (Phase 4)**: dipende da US1 per il profilo validato; offline e SSH possono essere sviluppati in parallelo dopo T027.
- **User Story 3 (Phase 5)**: dipende da US2 per file, rete e unità installati; test di template e fake possono procedere in parallelo.
- **Polish (Phase 6)**: dipende dalle user story richieste; documentazione e test indipendenti possono procedere in parallelo.

### User Story Dependencies

- **US1 (P1)**: dipende solo dalla fase Foundational ed è l'MVP.
- **US2 (P1)**: dipende dal contratto/profile loader di US1, ma resta testabile con filesystem temporaneo.
- **US3 (P1)**: dipende dall'installazione prodotta da US2, ma la policy systemd è testabile con fake.

### Parallel Opportunities

- T002, T003, T004 e T005 sono parallelizzabili dopo T001.
- T008–T011 sono parallelizzabili dopo la definizione del parser e delle interfacce.
- I test di ogni user story possono essere scritti in parallelo prima dell'implementazione.
- In US2, offline transport, SSH transport, renderer e NetworkManager possono essere sviluppati in parallelo rispettando le interfacce condivise; T029 dipende dal renderer e dal manifest definiti da T027.
- In US3, test systemd, recovery e boundary MCP sono parallelizzabili.
- In Polish, documentazione, controllo profili e separazione test hardware sono parallelizzabili.

## Parallel Example: User Story 1

```text
Task: T013 [US1] Test profili indipendenti in tests/deployment/test_profile_validation.py
Task: T014 [US1] Test redazione segreti in tests/deployment/test_sanitized_reports.py
Task: T015 [US1] Test CLI validate in tests/deployment/test_cli.py
```

## Parallel Example: User Story 2

```text
Task: T021 [US2] Test filesystem temporaneo in tests/deployment/test_offline_provisioning.py
Task: T022 [US2] Test SSH fake in tests/deployment/test_ssh_transport.py
Task: T024 [US2] Test permessi in tests/deployment/test_permissions.py
```

## Implementation Strategy

### MVP First (User Story 1 only)

1. Completare Setup e Foundational.
2. Implementare parser, validazione, report sanificato e CLI `validate`/`dry-run`.
3. Verificare due o tre profili fittizi senza hardware.
4. Fermarsi al checkpoint US1 prima di introdurre scritture su target.

### Incremental Delivery

1. Aggiungere US2 con filesystem offline e poi backend SSH.
2. Verificare idempotenza, permessi, cleanup e rollback.
3. Aggiungere US3 con NetworkManager e systemd.
4. Eseguire Polish e solo dopo pianificare prove hardware su Raspberry reale.

### Parallel Team Strategy

1. Un contributore completa parser/contratti e un altro i template/documentazione.
2. Dopo Foundational, un contributore lavora su offline, uno su SSH/NetworkManager e uno sui test.
3. La parte systemd/recovery viene integrata dopo il contract condiviso del provisioning.
