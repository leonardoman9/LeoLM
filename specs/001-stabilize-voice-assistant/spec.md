# Feature Specification: Stabilize Voice Assistant

**Feature Branch**: `001-stabilize-voice-assistant`

**Created**: 2026-10-29

**Status**: Draft

**Input**: User description: "Analizza il repository LeoLM e prepara una specifica per stabilizzare il progetto esistente. Correggere la documentazione, completare le dipendenze, proteggere le API key, configurare modello/dispositivi/wake word, eliminare riferimenti hardware hard-coded, migliorare cleanup audio, separare test hardware e automatici, rendere l'installazione riproducibile, documentare privacy e servizi online, mantenendo il comportamento vocale attuale e aggiornando le tecnologie."

## Clarifications

### Session 2026-10-29

- Q: Quando un servizio online non è disponibile, come deve comportarsi l’assistente? → A: Effettuare un numero limitato di retry con ritardo, poi tornare all’ascolto.
- Q: Quanto a lungo devono essere conservati localmente audio, trascrizioni e risposte generate? → A: Il testo della conversazione corrente resta disponibile come contesto fino a 10 minuti dall’ultima interazione; ogni nuova interazione valida resetta il timer, poi il contesto viene eliminato.
- Q: Quanti tentativi totali deve effettuare il sistema per una richiesta online prima di tornare all’ascolto? → A: 3 tentativi totali, cioè 2 retry aggiuntivi con ritardo crescente.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Avvio sicuro e installazione riproducibile (Priority: P1)

Come manutentore, voglio installare e avviare LeoLM seguendo istruzioni coerenti, fornendo le
credenziali tramite ambiente, senza che segreti o dettagli sensibili vengano stampati.

**Why this priority**: Un'installazione non riproducibile o un segreto esposto impedisce un uso sicuro
del dispositivo e rende il progetto difficile da mantenere.

**Independent Test**: In un ambiente pulito, seguire la documentazione con credenziali fittizie,
verificare l'installazione delle dipendenze dichiarate e confermare che l'output non contenga i valori
delle credenziali.

**Acceptance Scenarios**:

1. **Given** un ambiente pulito e un file di configurazione di esempio, **When** l'utente esegue la
   procedura documentata, **Then** tutte le dipendenze Python e di sistema richieste sono dichiarate
   e installabili senza modifiche manuali al codice.
2. **Given** credenziali valorizzate nell'ambiente, **When** l'assistente avvia o segnala un errore,
   **Then** mostra solo nomi delle impostazioni o messaggi sanitizzati e non stampa mai i valori.
3. **Given** una configurazione mancante o non valida, **When** l'utente avvia l'assistente,
   **Then** riceve un errore chiaro che indica come correggerla senza rivelare segreti.

---

### User Story 2 - Configurare il dispositivo vocale (Priority: P1)

Come utente o installatore, voglio scegliere modello, lingua, wake word, microfono e speaker tramite
configurazione, così da usare hardware compatibile senza modificare il codice.

**Why this priority**: Il comportamento attuale dipende da un setup audio specifico e non è
trasferibile a installazioni diverse.

**Independent Test**: Fornire una configurazione con valori fittizi e dispositivi simulati, verificare
che venga caricata e validata, quindi verificare che il flusso vocale utilizzi quei valori.

**Acceptance Scenarios**:

1. **Given** un modello, una wake word e dispositivi validi configurati, **When** l'assistente parte,
   **Then** usa quei valori per la rilevazione, l'ascolto, la richiesta al servizio online e la
   riproduzione.
2. **Given** un dispositivo selezionato per nome o identificatore configurato, **When** l'indice
   hardware cambia, **Then** l'assistente risolve il dispositivo senza affidarsi a un indice fisso.
3. **Given** un dispositivo assente o incompatibile, **When** l'assistente tenta di usarlo,
   **Then** segnala il problema, rilascia le risorse già aperte e non termina lasciando stream attivi.

---

### User Story 3 - Conversazione vocale invariata e resiliente (Priority: P1)

Come utente, voglio continuare a pronunciare la wake word, parlare in italiano e ascoltare la
risposta dell'assistente, anche quando rete o audio hanno problemi temporanei.

**Why this priority**: La stabilizzazione deve migliorare affidabilità senza cambiare il flusso
vocale attuale.

**Independent Test**: Simulare rilevazione wake word, input vocale, risposta del servizio e output
audio con adapter controllabili; ripetere lo scenario con timeout, risposta non valida e dispositivo
occupato.

**Acceptance Scenarios**:

1. **Given** l'assistente in ascolto, **When** viene rilevata la wake word e l'utente pronuncia un
   comando, **Then** il comando viene trascritto, inviato al servizio configurato e la risposta viene
   convertita in audio e riprodotta.
2. **Given** una connessione assente, un timeout o una risposta remota non valida, **When** il comando
   viene elaborato, **Then** l'assistente esegue retry limitati con ritardo, informa l'utente con un
   messaggio comprensibile e, se il servizio resta indisponibile, rilascia le risorse e torna
   all'ascolto della wake word senza esporre credenziali.
3. **Given** un'interruzione durante acquisizione o riproduzione, **When** il processo viene fermato,
   **Then** microfono, speaker, stream, processi e file temporanei vengono chiusi o rimossi.
4. **Given** una conversazione attiva, **When** l'utente invia una nuova interazione entro 10 minuti,
   **Then** il testo precedente viene usato come contesto e il timer di inattività viene azzerato.
5. **Given** 10 minuti senza una nuova interazione valida, **When** l'utente pronuncia nuovamente la
   wake word, **Then** il contesto precedente è stato eliminato e la nuova conversazione parte senza
   testo storico.

### Edge Cases

- Il file della wake word o il modello locale non esiste, non è leggibile o non corrisponde alla
  lingua configurata.
- Nessun microfono o speaker compatibile è disponibile, oppure un dispositivo viene scollegato
  durante l'ascolto.
- Il servizio di riconoscimento vocale, il servizio conversazionale o il servizio TTS è offline,
  restituisce un errore HTTP, supera il timeout o invia un payload inatteso.
- La risposta è vuota, eccessivamente lunga o contiene caratteri che il player non riesce a gestire.
- Due operazioni audio si sovrappongono o un callback audio solleva un'eccezione.
- L'utente interrompe il programma durante una richiesta di rete o mentre è attivo uno stream.
- Il timer di inattività scade durante una richiesta o una riproduzione: il contesto non deve essere
  eliminato prima che l'interazione corrente sia completata, ma deve essere eliminato allo scadere
  dei 10 minuti successivi.
- La configurazione contiene valori mancanti, numeri fuori intervallo, percorsi relativi ambigui o
  segreti inseriti in un log di debug.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Il sistema MUST mantenere il flusso vocale esistente: rilevazione wake word, ascolto
  del comando, riconoscimento, richiesta al modello e risposta vocale.
- **FR-002**: Il sistema MUST caricare API key e token esclusivamente da variabili d'ambiente o da
  un meccanismo locale equivalente non versionato, con nomi e valori documentati.
- **FR-003**: Il sistema MUST impedire che API key, token, audio acquisito e dati di richiesta
  sensibili compaiano nell'output normale, nei messaggi d'errore, nei test o nei log; il testo della
  conversazione può restare solo nel contesto temporaneo della sessione corrente.
- **FR-004**: Il sistema MUST rendere configurabili almeno modello, endpoint del servizio
  conversazionale, lingua, wake word, percorso del modello wake word, dispositivo di input,
  dispositivo di output e timeout.
- **FR-005**: Il sistema MUST validare la configurazione prima di inizializzare risorse hardware o
  servizi remoti e MUST indicare impostazioni mancanti o non valide senza rivelarne i valori sensibili.
- **FR-006**: Il sistema MUST selezionare i dispositivi audio tramite configurazione o rilevazione
  verificabile, senza dipendere da nomi, indici, percorsi o identificativi hardware incorporati nel
  codice quando esiste un'alternativa configurabile.
- **FR-007**: Il sistema MUST chiudere microfono, speaker, stream, client wake word, processi esterni
  e file temporanei in caso di successo, errore, timeout, scollegamento o interruzione dell'utente.
- **FR-008**: Il sistema MUST applicare timeout espliciti alle operazioni di rete e distinguere
  almeno timeout, mancata connessione, risposta HTTP non riuscita e payload non valido; per gli errori
  recuperabili MUST eseguire al massimo 3 tentativi totali, con 2 retry aggiuntivi e ritardo crescente,
  quindi tornare all'ascolto se il servizio resta indisponibile.
- **FR-019**: Il sistema MUST mantenere il testo della conversazione corrente come contesto per le
  interazioni successive, senza persisterlo oltre la sessione attiva.
- **FR-020**: Il sistema MUST applicare un timer di inattività di 10 minuti al contesto conversazionale;
  ogni interazione valida MUST resettare il timer e, allo scadere, il sistema MUST eliminare il testo
  storico prima di elaborare una nuova conversazione.
- **FR-021**: Il sistema MUST garantire che il timer non elimini il contesto mentre l'interazione
  corrente è ancora in elaborazione e MUST cancellare o invalidare il timer quando il contesto viene
  eliminato.
- **FR-009**: Il sistema MUST evitare installazioni o aggiornamenti con privilegi elevati durante
  l'esecuzione; ogni prerequisito di sistema MUST essere dichiarato nella procedura di installazione.
- **FR-010**: Il sistema MUST dichiarare tutte le dipendenze Python realmente importate e tutti i
  programmi o pacchetti di sistema realmente necessari al flusso vocale e alla riproduzione audio.
- **FR-011**: Il progetto MUST definire una procedura di installazione riproducibile con versioni o
  intervalli di compatibilità supportati, controllo delle dipendenze e configurazione di esempio.
- **FR-012**: Il progetto MUST separare i test automatici, eseguibili senza hardware, rete reale o
  privilegi di sistema, dai test hardware espliciti per microfono, speaker e dispositivi ALSA.
- **FR-013**: I test automatici MUST coprire configurazione, sanitizzazione dei segreti, errori di
  rete, selezione dispositivi, cleanup e continuità del flusso vocale tramite sostituti deterministici.
- **FR-014**: I test hardware MUST essere identificati separatamente, richiedere esplicitamente
  l'hardware necessario e non essere inclusi nel percorso automatico predefinito.
- **FR-015**: La documentazione MUST corrispondere ai comandi e al comportamento effettivo, includere
  tutte le dipendenze e variabili, descrivere privacy e conservazione dei dati e indicare che wake
  word, riconoscimento, modello e sintesi possono dipendere da servizi online.
- **FR-016**: Il progetto MUST aggiornare le dipendenze e gli strumenti di runtime a versioni
  supportate e compatibili con Raspberry Pi Zero 2 W, registrando eventuali incompatibilità o
  vincoli di piattaforma invece di introdurre aggiornamenti non verificati.
- **FR-017**: Il sistema MUST limitare memoria, processi concorrenti, durata dei buffer e file
  temporanei in modo compatibile con le risorse del Raspberry Pi Zero 2 W.
- **FR-018**: Il sistema MUST preservare i messaggi e le notifiche utili all'utente, ma deve
  sostituire dettagli tecnici o sensibili con messaggi sanitizzati e azioni di recupero comprensibili.

### Key Entities

- **Runtime configuration**: impostazioni valide per credenziali, servizi, lingua, modello, wake word,
  dispositivi audio, timeout e percorsi locali.
- **Audio device**: microfono o speaker selezionabile, con capacità, identificativo e stato di
  disponibilità rilevati al momento dell'uso.
- **Voice session**: ciclo dalla wake word al comando trascritto, alla risposta remota e alla
  riproduzione, con stato di errore, contesto temporaneo e cleanup associato.
- **External service dependency**: servizio di wake word, trascrizione, modello conversazionale o
  sintesi vocale, con endpoint, credenziale, timeout e comportamento d'indisponibilità.
- **Test profile**: configurazione che identifica un test automatico isolato oppure una prova hardware
  esplicita con prerequisiti documentati.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Una nuova installazione su un Raspberry Pi Zero 2 W supportato può essere completata
  seguendo una sola procedura documentata, senza modificare il codice e senza installazioni avviate
  durante il normale avvio dell'assistente.
- **SC-002**: Il 100% dei test automatici predefiniti passa su una macchina senza microfono, speaker,
  ALSA, servizi online o privilegi elevati.
- **SC-003**: In una scansione del codice, dei log e dei test con credenziali fittizie, non compare
  alcun valore segreto in 100% dei percorsi di avvio, successo ed errore coperti.
- **SC-004**: Almeno il 95% dei casi di errore simulati per rete, configurazione e audio termina con
  risorse chiuse e un messaggio classificato e azionabile.
- **SC-005**: Un installatore può cambiare modello, wake word e dispositivi audio modificando solo la
  configurazione documentata, senza modificare il codice sorgente.
- **SC-006**: Il flusso vocale principale mantiene la sequenza wake word → comando → risposta audio
  nei test di integrazione con adapter simulati, senza regressioni funzionali rispetto al comportamento
  attuale.
- **SC-007**: La documentazione elenca il 100% delle dipendenze importate dal programma e dei
  prerequisiti di sistema necessari alle modalità supportate.
- **SC-008**: La suite automatica e quella hardware sono distinguibili con comandi separati e la
  suite automatica non tenta accesso a dispositivi fisici.
- **SC-009**: Nei test di sessione, il 100% delle interazioni entro 10 minuti usa il contesto corrente,
  mentre il 100% delle conversazioni avviate dopo 10 minuti di inattività non include il testo storico.

## Assumptions

- Il target principale resta Raspberry Pi Zero 2 W con Linux; eventuali aggiornamenti tecnologici
  devono restare compatibili con questa piattaforma o dichiarare esplicitamente un limite.
- Il comportamento vocale attuale, inclusa la lingua italiana e il ciclo wake word–risposta, è il
  contratto funzionale da preservare; non è richiesto introdurre nuove modalità conversazionali.
- Le credenziali continuano a essere fornite dall'operatore tramite variabili d'ambiente; la
  specifica non introduce un gestore segreti esterno.
- I servizi online restano parte del sistema: senza rete l'assistente deve fornire un errore chiaro,
  non simulare una risposta remota e non perdere risorse locali.
- Un errore di rete recuperabile può essere ritentato al massimo 2 volte dopo il primo tentativo, con
  ritardo crescente tra i tentativi; dopo il terzo tentativo il sistema torna all'ascolto.
- Il contesto conversazionale è temporaneo e viene mantenuto solo durante l'attività corrente; il
  timeout predefinito di inattività è 10 minuti e viene rinnovato dopo ogni interazione valida.
- L'aggiornamento a tecnologie più recenti significa adottare versioni supportate e compatibili delle
  dipendenze e degli strumenti di installazione, con verifica su hardware equivalente; non implica
  una migrazione a un nuovo provider o la riscrittura del comportamento vocale.
- I file locali di wake word e parametri già presenti restano utilizzabili, ma il loro percorso e la
  wake word selezionata diventano configurabili.
- La documentazione deve distinguere dati elaborati localmente da dati inviati a servizi remoti e
  dichiarare eventuali retention policy non controllabili dal progetto.
