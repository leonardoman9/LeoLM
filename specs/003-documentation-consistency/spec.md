# Feature Specification: Documentation Consistency

**Feature Branch**: `003-documentation-consistency`

**Created**: 2026-10-29

**Status**: Draft

**Input**: User description: "Sistemare tutta la documentazione alla fine, quando il comportamento del progetto e il deployment saranno stabilizzati."

## Clarifications

### Session 2026-10-29

- Q: Quale deve essere la fonte canonica per nomi, default e descrizione delle variabili di configurazione? → A: Il contratto di configurazione è canonico; README, `.env.example` e profili deployment vengono verificati automaticamente contro di esso.
- Q: Come deve comportarsi il controllo automatico quando trova link esterni non raggiungibili? → A: I link locali sono errori bloccanti; i link esterni producono un warning con URL e motivo senza bloccare la validazione.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Trovare una guida unica e affidabile (Priority: P1)

Come installatore o manutentore, voglio una guida principale coerente con il comportamento reale di
LeoLM, così da poter installare, configurare, avviare e diagnosticare il progetto senza informazioni
obsolete o contraddittorie.

**Why this priority**: La documentazione è il punto di ingresso per ogni nuova installazione e deve
riflettere le decisioni finali del progetto, non gli stati intermedi del prototipo.

**Independent Test**: Un lettore che non conosce il repository segue la guida in un ambiente pulito e
raggiunge una configurazione verificabile senza consultare istruzioni obsolete o modificare il codice.

**Acceptance Scenarios**:

1. **Given** il repository finale, **When** un installatore segue la guida principale, **Then** trova
   prerequisiti, installazione, configurazione, avvio, test e troubleshooting nello stesso percorso.
2. **Given** una variabile d'ambiente o un comando documentato, **When** viene confrontato con il
   comportamento reale, **Then** nome, default, formato, effetto e messaggio d'errore coincidono.
3. **Given** una procedura non più supportata, **When** viene individuata nella documentazione,
   **Then** viene rimossa oppure marcata chiaramente come incompatibile e sostituita dalla procedura
   corrente.

---

### User Story 2 - Capire privacy, rete e deployment (Priority: P1)

Come proprietario di un Raspberry, voglio sapere quali dati escono dal dispositivo, quali segreti devo
proteggere e come distribuire il software su più unità, così da poterlo usare consapevolmente e
ripetere il deployment senza errori.

**Why this priority**: API key, password Wi-Fi, audio, trascrizioni e servizi online richiedono
aspettative esplicite prima di distribuire più dispositivi.

**Independent Test**: Verificare che la documentazione descriva un profilo `.env`, provisioning,
avvio automatico, Wi-Fi, retention del contesto e limiti dei provider senza includere segreti reali.

**Acceptance Scenarios**:

1. **Given** un utente che legge la privacy policy, **When** cerca dati locali, dati inviati e tempi di
   conservazione, **Then** trova risposte esplicite per audio, trascrizioni, contesto e TTS.
2. **Given** un installatore con tre Raspberry, **When** consulta la guida deployment, **Then** sa
   creare profili distinti, proteggerli, trasferirli e verificare ogni dispositivo.
3. **Given** un servizio online indisponibile, **When** l'utente consulta il troubleshooting, **Then**
   trova retry, timeout, messaggi attesi e procedura di recupero senza promesse non supportate.

---

### User Story 3 - Verificare che la documentazione non diverga (Priority: P2)

Come manutentore, voglio controlli automatici e una checklist finale, così da rilevare riferimenti a
file, variabili, comandi o dipendenze inesistenti prima di pubblicare una release.

**Why this priority**: La documentazione tende a divergere dal codice dopo refactoring e nuovi profili
di deployment; una verifica ripetibile riduce regressioni operative.

**Independent Test**: Eseguire il controllo documentale in CI o localmente e verificare che segnali
link locali rotti, placeholder, variabili non dichiarate, comandi non validi e segreti nei documenti.

**Acceptance Scenarios**:

1. **Given** un link locale o una variabile inesistente, **When** viene eseguito il controllo,
   **Then** il controllo fallisce indicando file e riga.
2. **Given** una documentazione completa e coerente, **When** viene eseguito il controllo,
   **Then** termina con esito positivo senza richiedere hardware, rete reale o credenziali.
3. **Given** un valore sensibile inserito per errore in un esempio o documento, **When** viene eseguito
   il controllo, **Then** il valore viene bloccato prima della pubblicazione.

### Edge Cases

- Il comportamento finale cambia dopo l'aggiornamento della documentazione.
- Un file referenziato viene rinominato o spostato.
- Un esempio contiene un placeholder non sostituito o un segreto realistico.
- Il comando documentato dipende da una versione Python, pacchetto di sistema o Raspberry OS diversa.
- La procedura di deployment offline differisce da quella via SSH.
- Un link a policy esterna o servizio online cambia o non è raggiungibile.
- La documentazione descrive MCP prima che MCP sia effettivamente distribuito.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Il progetto MUST definire un documento principale che descriva scopo, prerequisiti,
  installazione, configurazione, avvio, test, deployment e troubleshooting correnti.
- **FR-002**: La documentazione MUST usare un unico nome canonico per ogni variabile, file, comando,
  servizio, asset wake word e stato operativo.
- **FR-002a**: Il contratto di configurazione MUST essere la fonte canonica per nomi, scope, default,
  formato, obbligatorietà e descrizione delle variabili; deve distinguere variabili runtime LeoLM e
  variabili deployment. README, `.env.example` e profili deployment MUST essere verificati
  automaticamente contro la rispettiva allowlist del contratto.
- **FR-003**: La documentazione MUST elencare tutte le dipendenze Python e di sistema realmente necessarie
  e MUST distinguere dipendenze runtime, sviluppo e test hardware.
- **FR-004**: Ogni variabile d'ambiente MUST indicare significato, obbligatorietà, default, formato,
  esempio sicuro e comportamento in caso di errore.
- **FR-005**: Gli esempi MUST usare placeholder chiaramente fittizi e MUST escludere API key, access key,
  password Wi-Fi e dati vocali reali.
- **FR-006**: La documentazione MUST spiegare il flusso vocale, il contesto temporaneo di 10 minuti,
  i retry di rete, il ritorno alla wake word e il cleanup delle risorse.
- **FR-007**: La privacy documentation MUST distinguere dati elaborati localmente, dati inviati ai
  servizi online, retention locale e retention non controllabile del provider.
- **FR-008**: La documentazione MUST descrivere deployment PC → Raspberry, profili per dispositivo,
  Wi-Fi automatico, avvio al boot, log e recupero senza esporre segreti.
- **FR-009**: Il progetto MUST documentare chiaramente i limiti di compatibilità per Python, Raspberry
  Pi OS, audio, rete, wake word, servizi cloud e provider non supportati.
- **FR-010**: Il progetto MUST fornire una checklist release che verifichi ogni comando e percorso
  documentato su un ambiente isolato o con un test equivalente.
- **FR-011**: Il progetto MUST fornire un controllo automatico per link locali rotti, placeholder,
  variabili non dichiarate, comandi vietati e pattern che possono contenere segreti. I link locali
  rotti MUST bloccare il controllo; i link esterni non raggiungibili MUST produrre un warning con URL
  e motivo senza bloccare la validazione.
- **FR-012**: Il controllo documentale MUST essere eseguibile senza microfono, speaker, Raspberry,
  rete reale o credenziali reali.
- **FR-013**: La documentazione MUST indicare che MCP è fuori scope finché non esiste un'integrazione
  implementata e verificata; non deve promettere strumenti non disponibili.
- **FR-014**: La revisione documentale MUST essere eseguita dopo il completamento delle feature di
  stabilizzazione e deployment, prima della release o distribuzione di immagini.

### Key Entities

- **Canonical documentation set**: insieme di README, guide, contratti di configurazione, privacy,
  deployment, dipendenze e troubleshooting.
- **Documentation source of truth**: file o contratto da cui derivano nomi, default e procedure.
- **Release documentation checklist**: elenco verificabile di link, comandi, variabili, dipendenze,
  privacy e compatibilità.
- **Documentation validation report**: risultato con errori, file, righe e stato finale, senza segreti.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Un nuovo installatore completa la procedura principale senza incontrare istruzioni
  contraddittorie e senza modificare il codice.
- **SC-002**: Il 100% delle variabili d'ambiente e delle dipendenze supportate è documentato con nome,
  formato e comportamento di errore.
- **SC-003**: Il 100% dei link locali e dei percorsi citati passa il controllo automatico.
- **SC-003a**: Il controllo classifica correttamente ogni link locale non valido come errore bloccante
  e ogni link esterno non raggiungibile come warning non bloccante nei casi di test previsti.
- **SC-004**: Il controllo documentale rileva il 100% dei placeholder e dei pattern di segreti introdotti
  nei fixture di test.
- **SC-005**: Un profilo deployment per almeno tre Raspberry può essere seguito dalla documentazione
  senza confondere hostname, Wi-Fi, audio o credenziali.
- **SC-006**: La documentazione privacy permette di identificare in meno di 5 minuti quali dati restano
  locali, quali vengono inviati online e quando scade il contesto conversazionale.
- **SC-007**: La checklist release passa senza hardware o credenziali reali e produce un report leggibile
  in caso di errore.

## Assumptions

- Questa feature viene eseguita dopo la stabilizzazione applicativa e dopo il deployment multi-Raspberry.
- Il README è il punto di ingresso; documenti specializzati possono dettagliare privacy, deployment,
  dipendenze e contratti senza duplicare valori contraddittori. Il contratto di configurazione è la
  fonte canonica per la configurazione pubblica e gli altri documenti vengono verificati contro di esso.
- I comandi documentati devono essere verificabili in un ambiente isolato; le prove hardware restano
  esplicitamente separate.
- Il progetto mantiene documentazione in italiano con termini tecnici e comandi originali quando utili.
- MCP non è documentato come funzionalità disponibile finché una feature successiva non lo implementa.
