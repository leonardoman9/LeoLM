# Feature Specification: Raspberry Deployment Profiles

**Feature Branch**: `002-raspberry-deployment`

**Created**: 2026-10-29

**Status**: Draft

**Input**: User description: "Configurare il Raspberry in modo che si connetta automaticamente al Wi-Fi e avvii LeoLM al boot; predisporre un file .env configurabile da PC prima del trasferimento per rendere semplice il deployment su più Raspberry."

## Clarifications

### Session 2026-10-29

- Q: Quale modalità di provisioning deve supportare la prima versione? → A: Sia filesystem/immagine offline sia deployment remoto via SSH, usando lo stesso profilo `.env`.
- Q: Dopo un provisioning riuscito, come devono essere gestiti i profili `.env` originali contenenti segreti? → A: Restano solo sul PC in una directory protetta e fuori dal repository; le copie temporanee di trasferimento vengono rimosse.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Preparare un profilo da PC (Priority: P1)

Come installatore, voglio creare un profilo per ogni Raspberry dal mio PC, inserendo configurazione
LeoLM, rete Wi-Fi e identificativo del dispositivo senza modificare il codice.

**Why this priority**: Un profilo ripetibile è la base per distribuire più dispositivi senza errori
manuali e senza confondere le configurazioni fra Raspberry diversi.

**Independent Test**: Creare due profili con SSID, nomi dispositivo, selettori audio e impostazioni
LeoLM diversi; verificare che siano validati separatamente e producano configurazioni distinte senza
segreti nei file di esempio o nei log.

**Acceptance Scenarios**:

1. **Given** un profilo basato su un esempio documentato, **When** l'installatore inserisce i valori
   del dispositivo e della rete, **Then** il profilo viene validato e gli errori indicano il campo da
   correggere senza stampare password o API key.
2. **Given** due profili validi, **When** l'installatore prepara due deployment, **Then** ciascun
   deployment conserva il proprio hostname, Wi-Fi, credenziali e configurazione audio.
3. **Given** un profilo copiato nel repository, **When** viene eseguito un controllo dei file da
   distribuire, **Then** vengono accettati solo template senza segreti e i profili reali risultano
   esclusi dal versionamento.

---

### User Story 2 - Provisioning di un Raspberry (Priority: P1)

Come installatore, voglio trasferire un profilo dal PC a una nuova installazione Raspberry Pi OS,
così da ottenere un dispositivo pronto senza configurazione manuale sul Raspberry.

**Why this priority**: Riduce il tempo e gli errori necessari per distribuire il progetto su più unità.

**Independent Test**: Eseguire il provisioning su una root filesystem o immagine di test e verificare
la presenza dei file applicativi, dei permessi dei segreti, della configurazione Wi-Fi e del servizio
LeoLM senza collegarsi a un Raspberry reale.

**Acceptance Scenarios**:

1. **Given** un profilo valido e una destinazione Raspberry supportata, **When** l'installatore avvia
   il provisioning, **Then** copia applicazione, ambiente e configurazione senza richiedere modifiche
   manuali al codice.
2. **Given** un profilo mancante, incompleto o non valido, **When** viene avviato il provisioning,
   **Then** l'operazione si interrompe prima di modificare la destinazione e mostra solo errori sicuri.
3. **Given** una destinazione già configurata, **When** il provisioning offline o SSH viene ripetuto,
   **Then** è idempotente e non duplica servizi, connessioni o file di configurazione.

---

### User Story 3 - Avvio autonomo dopo l'accensione (Priority: P1)

Come utente finale, voglio accendere il Raspberry e trovare LeoLM operativo automaticamente, senza
monitor, tastiera o login manuale.

**Why this priority**: Il dispositivo deve comportarsi come un assistente dedicato e distribuibile,
non come uno script da avviare manualmente.

**Independent Test**: In un ambiente Raspberry equivalente, simulare boot, rete disponibile, rete
ritardata e crash del processo; verificare connessione automatica, avvio ordinato, riavvio controllato
e assenza di segreti nei log.

**Acceptance Scenarios**:

1. **Given** un Raspberry configurato e spento, **When** viene acceso, **Then** il sistema si collega
   automaticamente al Wi-Fi configurato e avvia LeoLM dopo che la rete è disponibile.
2. **Given** il Wi-Fi è temporaneamente indisponibile, **When** il sistema completa il boot,
   **Then** LeoLM non entra in un ciclo di errori aggressivo e viene avviato o riavviato quando la rete
   diventa disponibile secondo una politica documentata.
3. **Given** LeoLM termina in modo inatteso, **When** il servizio rileva l'uscita, **Then** applica un
   ritardo e lo riavvia senza avviare copie concorrenti o lasciare stream audio attivi.
4. **Given** un Raspberry appena provisionato, **When** l'installatore verifica lo stato del sistema,
   **Then** può determinare se Wi-Fi, servizio LeoLM e audio sono configurati senza leggere o stampare
   i valori dei segreti.

### Edge Cases

- SSID nascosto, password errata, paese Wi-Fi non configurato o rete che richiede autenticazione non
  supportata dal profilo.
- Il Raspberry non riceve un indirizzo IP, perde la rete o la rete è disponibile solo dopo l'avvio.
- Il profilo contiene password, API key o caratteri speciali con encoding non valido.
- La destinazione contiene una versione precedente, un servizio già attivo o una configurazione
  parzialmente scritta dopo un'interruzione.
- Il dispositivo audio configurato non esiste su quel Raspberry o cambia identificativo al boot.
- Il processo LeoLM fallisce ripetutamente e il riavvio automatico deve evitare un loop ad alta frequenza.
- Un'immagine o filesystem di destinazione non è montato, non è scrivibile o non appartiene al target.
- Il deployment viene eseguito per più Raspberry con profili simili e non deve scambiare segreti o
  hostname.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Il progetto MUST fornire un template di profilo non segreto che descriva configurazione
  LeoLM, Wi-Fi, hostname, paese radio e identificativo del dispositivo.
- **FR-002**: Il profilo di un dispositivo MUST permettere di configurare modello, lingua, wake word,
  asset, dispositivi audio, endpoint, API key, access key, SSID e password senza modificare il codice.
- **FR-003**: Il progetto MUST validare profili prima del provisioning, includendo campi obbligatori,
  valori compatibili, encoding, hostname e selettori audio; gli errori MUST nominare il campo senza
  stampare il valore segreto.
- **FR-004**: Il progetto MUST impedire il versionamento dei profili reali e dei file contenenti
  password Wi-Fi, API key o access key; il template distribuito MUST contenere solo placeholder.
- **FR-005**: Il progetto MUST offrire dal PC due modalità di provisioning con lo stesso profilo:
  preparazione di filesystem/immagine offline e deployment remoto via SSH, entrambe con applicazione,
  ambiente, dipendenze e configurazione equivalenti. Se il PC e il target hanno architetture diverse,
  il provisioning offline MUST installare le dipendenze tramite un bootstrap target-side al primo boot,
  dopo la disponibilità della rete, senza richiedere interventi manuali.
- **FR-006**: Il provisioning MUST essere idempotente, rilevare destinazioni non valide e interrompersi
  senza lasciare una configurazione parziale quando la validazione iniziale fallisce.
- **FR-007**: Il provisioning MUST installare i segreti in un file locale leggibile solo dall'utente
  del servizio e non deve includerli negli output normali o nei log; il profilo sorgente resta sul PC
  in una directory protetta e fuori dal repository, mentre le copie temporanee di trasferimento MUST
  essere rimosse al termine.
- **FR-008**: Il sistema MUST configurare la connessione Wi-Fi del Raspberry usando il gestore di rete
  supportato dal sistema operativo target e MUST abilitarne la connessione automatica al boot.
- **FR-009**: Il sistema MUST impostare il paese radio e documentare i casi supportati e non supportati,
  inclusi SSID nascosti e reti enterprise quando non gestite.
- **FR-010**: Il deployment MUST installare un servizio di sistema per LeoLM con utente dedicato,
  ambiente separato, avvio dopo la rete, riavvio con ritardo e una sola istanza attiva.
- **FR-011**: Il servizio MUST usare i profili e i percorsi configurati senza inserire nel codice nomi
  di device, hostname, directory di deployment o interfacce Wi-Fi specifiche.
- **FR-012**: Il servizio MUST attendere la disponibilità della rete prima delle richieste remote e
  MUST gestire rete assente o ritardata senza loop di riavvio aggressivi.
- **FR-013**: Il deployment MUST produrre verifiche sanificate per hostname, servizio, rete e audio,
  distinguendo stato operativo da segreti e password. La verifica audio offline MUST distinguere
  configurazione statica da verifica di un dispositivo fisico.
- **FR-014**: Il progetto MUST fornire una modalità di simulazione o filesystem temporaneo per testare
  provisioning, validazione, idempotenza e permessi senza un Raspberry reale.
- **FR-015**: Il progetto MUST documentare la procedura PC → Raspberry, il primo boot, il recupero
  tramite SSH, i log del servizio, la sostituzione di un profilo e la rimozione sicura dei segreti.
- **FR-016**: Il deployment MUST supportare più Raspberry tramite profili indipendenti e MUST rendere
  identificabile ogni dispositivo senza condividere per errore hostname o credenziali.
- **FR-017**: L'integrazione MCP è fuori scope per questa feature; il deployment MUST lasciare un
  punto di estensione per aggiungerla in seguito senza esporre automaticamente porte o servizi.

### Key Entities

- **Device profile**: configurazione per un Raspberry, con hostname, rete, segreti, parametri LeoLM,
  selettori audio e metadati del dispositivo.
- **Deployment target**: directory, filesystem o immagine destinata al Raspberry, con stato validato,
  provisionato o fallito.
- **Wi-Fi connection**: rete configurata con SSID, credenziale, paese radio, priorità e politica di
  connessione automatica.
- **LeoLM service**: unità di avvio con utente, ambiente, percorso, dipendenza dalla rete, politica di
  riavvio e stato operativo.
- **Deployment report**: risultato sanificato delle verifiche, senza password, API key o access key.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Un installatore può preparare un nuovo profilo e completare il provisioning di un
  Raspberry supportato in meno di 15 minuti, escluso il tempo di scrittura dell'immagine.
- **SC-002**: Il 100% dei profili validi di una serie di almeno 3 dispositivi produce configurazioni
  isolate con hostname, Wi-Fi e parametri LeoLM corretti.
- **SC-003**: Il 100% dei profili con segreti o campi invalidi viene rifiutato prima di modificare la
  destinazione e non stampa i valori sensibili.
- **SC-004**: Dopo un boot con rete disponibile, LeoLM risulta avviato automaticamente entro 60 secondi
  dalla disponibilità della rete nel 95% delle prove su hardware equivalente.
- **SC-005**: Dopo un crash simulato, il servizio esegue al massimo un riavvio entro la finestra di
  ritardo configurata e non crea processi concorrenti.
- **SC-006**: La procedura offline di provisioning passa il 100% dei test di validazione, idempotenza,
  permessi e rollback senza richiedere hardware reale.
- **SC-007**: Nessun segreto compare nei report, nei log di provisioning o nei log di stato in 100% dei
  test con credenziali fittizie.
- **SC-008**: Un operatore può sostituire il profilo di un dispositivo senza modificare il codice e
  senza alterare i profili degli altri dispositivi.

## Assumptions

- Il target principale è Raspberry Pi OS Bookworm Lite 32-bit o 64-bit su Raspberry Pi Zero 2 W, con
  NetworkManager e systemd disponibili; altre versioni sono fuori supporto finché non vengono verificate.
- Il Wi-Fi viene configurato dal sistema operativo, non direttamente dal processo LeoLM; LeoLM parte
  dopo la rete e gestisce solo gli errori dei servizi online.
- Il PC di provisioning può accedere alla destinazione tramite filesystem/immagine montata oppure
  tramite SSH; entrambe le modalità sono incluse nella prima versione e condividono lo stesso profilo.
- I profili reali sono segreti operativi locali e non vengono committati; il repository contiene solo
  template e documentazione. Dopo il provisioning il profilo sorgente resta sul PC in una directory
  protetta; solo le copie temporanee usate dal trasferimento vengono eliminate.
- Il file `.env` è un formato di input per il provisioning, non necessariamente il file finale letto
  dal servizio; i segreti finali devono avere permessi restrittivi.
- Per immagini offline preparate su un PC con architettura diversa dal Raspberry, il codice e il
  profilo vengono predisposti nell'immagine e un servizio bootstrap installa al primo boot il virtual
  environment e le dipendenze runtime sul target ARM. Il bootstrap è automatico, idempotente e viene
  disabilitato dopo il completamento.
- Un Raspberry deve avere almeno un metodo di recupero iniziale, come Raspberry Pi Imager, SSH o
  accesso locale, per correggere rete e deployment.
- MCP non viene installato né esposto in questa feature; sarà una feature successiva con policy di
  allowlist e sicurezza proprie.
