# Research: Documentation Consistency

## Decision 1: contratto di configurazione canonico in `docs/configuration.md`

**Rationale**: il comportamento applicativo viene già espresso da variabili d'ambiente e profili; un documento operativo versionato è leggibile dagli installatori e può essere analizzato dal validatore. README, `.env.example` e profili non devono diventare fonti concorrenti.

**Alternatives considered**: mantenere il contratto solo nella specifica sotto `specs/001` avrebbe reso la guida di deployment indiretta e fragile; derivarlo dal codice avrebbe richiesto un formato runtime più complesso senza beneficio per questa feature.

## Decision 2: schema Markdown a due scope

**Rationale**: runtime LeoLM e provisioning usano insiemi diversi di variabili. Due tabelle con colonne fisse rendono il contratto leggibile e deterministico per il validator, evitando di forzare variabili Wi-Fi dentro l'esempio runtime.

**Alternatives considered**: un singolo elenco avrebbe prodotto eccezioni implicite; un file YAML aggiuntivo avrebbe introdotto una seconda fonte documentale da mantenere.

## Decision 3: validatore Python offline basato su libreria standard

**Rationale**: il controllo deve funzionare senza Raspberry, audio, rete e credenziali. Un CLI Python separato può verificare Markdown, percorsi locali, variabili, placeholder, comandi vietati e pattern di segreti con output sicuro e exit code adatto alla CI.

**Alternatives considered**: un controllo remoto dei link sarebbe non deterministico; un framework Markdown aggiuntivo aumenterebbe le dipendenze e il costo di installazione per un controllo principalmente testuale.

## Decision 4: severità diversa per link locali ed esterni

**Rationale**: un link locale rotto indica una regressione nel repository e deve bloccare. Un URL esterno può essere temporaneamente irraggiungibile o richiedere autenticazione; viene quindi segnalato come warning con URL e motivo, senza rete obbligatoria per il passaggio base.

**Alternatives considered**: bloccare ogni URL avrebbe reso CI instabile; ignorare gli URL esterni avrebbe nascosto errori utili nella documentazione privacy e dei provider.

## Decision 5: documentazione italiana con nomi tecnici invariati

**Rationale**: il progetto e le richieste operative sono in italiano, mentre comandi, nomi di variabili, percorsi ed eccezioni devono restare identici a quelli eseguiti.

**Alternatives considered**: duplicare ogni guida in due lingue raddoppierebbe il rischio di divergenza senza requisito attuale.

## Decision 6: checklist release e MCP fuori scope

**Rationale**: la documentazione finale deve essere verificata prima di distribuire immagini o profili a più Raspberry. MCP resta esplicitamente non disponibile finché non esiste un'integrazione implementata e testata.

**Alternatives considered**: documentare MCP come roadmap in una guida operativa confonderebbe capacità disponibili e future.
