# Research: Raspberry Deployment Profiles

## Decision 1: profilo `.env` come input comune ai due transport

**Rationale**: l'installatore può preparare un dispositivo offline oppure raggiungerlo via SSH senza imparare due formati. Il profilo viene validato prima e poi trasformato in file runtime, NetworkManager e systemd.

**Alternatives considered**: due configurazioni separate avrebbero creato divergenza fra immagine e deployment remoto; un database centrale avrebbe aggiunto infrastruttura non adatta a un progetto per Raspberry isolati.

## Decision 2: bootstrap target-side per immagini cross-architettura

**Rationale**: un PC x86 non deve tentare di installare nel proprio virtual environment pacchetti binari destinati ad ARM. Il provisioning offline copia codice, requirements e profilo nell'immagine e installa automaticamente le dipendenze al primo boot tramite un'unità systemd one-shot dopo la rete. Su un PC compatibile con il target può essere usata l'installazione diretta, mantenendo lo stesso manifest.

**Alternatives considered**: QEMU/chroot aumenterebbe prerequisiti e complessità del PC; wheel cross-platform precompilate richiederebbero una pipeline di build e una matrice di artefatti più ampia.

## Decision 3: NetworkManager + systemd come primitive target

**Rationale**: NetworkManager gestisce connessioni Wi-Fi persistenti e autoconnect; systemd fornisce ordering dopo la rete, utente dedicato, restart delay e singola unità. Sono componenti standard e osservabili su Raspberry Pi OS supportato.

**Alternatives considered**: scrivere direttamente `wpa_supplicant.conf` e usare cron/rc.local avrebbe ridotto l'osservabilità, la gestione dei retry e l'idempotenza.

## Decision 4: staging e commit atomico del provisioning

**Rationale**: i file vengono preparati in una directory temporanea della destinazione, validati, impostati con ownership/permessi e poi attivati con rename; una validazione iniziale fallita non modifica il target e un'interruzione durante il commit lascia il precedente deployment utilizzabile.

**Alternatives considered**: copiare direttamente i file finali è più semplice ma può lasciare profili parziali, segreti con permessi errati o servizi puntati a versioni miste.

## Decision 5: esecuzione privilegiata minima e utente dedicato

**Rationale**: solo le operazioni necessarie su NetworkManager, systemd e directory di servizio usano privilegi sul target; il processo LeoLM gira con un utente dedicato e non riceve privilegi amministrativi.

**Alternatives considered**: eseguire LeoLM come root semplificherebbe l'accesso a file/device ma viola il principio di least privilege e aumenta l'impatto di un errore audio o di rete.

## Decision 6: verifica sanificata e dry-run obbligatori

**Rationale**: hostname, stato del servizio, connettività e presenza degli asset possono essere controllati senza mostrare password o API key. Il dry-run e il filesystem temporaneo permettono test automatici e review prima di scrivere su un Raspberry.

**Alternatives considered**: verificare solo con `systemctl status` avrebbe esposto output non controllato e non avrebbe coperto profili offline.

## Decision 7: matrice target limitata a Raspberry Pi OS Bookworm

**Rationale**: fissare inizialmente Raspberry Pi OS Bookworm Lite 32-bit e 64-bit, con systemd e NetworkManager, rende riproducibili bootstrap, keyfile e servizio. Versioni precedenti o derivate restano non supportate finché non vengono testate.

**Alternatives considered**: supportare ogni versione Linux avrebbe moltiplicato le varianti di rete, systemd e pacchetti senza una matrice verificata.

## Decision 8: MCP fuori scope

**Rationale**: il deployment non apre porte, endpoint o servizi per capacità non ancora implementate. Un futuro adapter potrà essere aggiunto al manifest senza cambiare la base di sicurezza.

**Alternatives considered**: predisporre subito un server MCP avrebbe allargato la superficie di rete senza requisito funzionale.
