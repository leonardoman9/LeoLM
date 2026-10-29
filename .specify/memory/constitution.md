<!--
Sync Impact Report
- Version change: not ratified -> 1.0.0
- Modified principles: none; initial constitution
- Added sections: Core Principles, Operational Constraints, Development Workflow, Governance
- Removed sections: none
- Follow-up TODOs: confirm the original ratification date
-->
# LeoLM Constitution

## Core Principles

### I. Sicurezza delle credenziali e dei dati vocali
Le API key, i token e ogni altra credenziale MUST essere forniti tramite variabili d'ambiente o
meccanismi equivalenti non versionati; non devono comparire nel codice, nei log, nei test, negli
artifact audio o nella documentazione di esempio. L'audio acquisito e il testo trascritto MUST essere
trasmessi solo ai servizi configurati e per il tempo necessario alla richiesta, senza persistenza
implicita. I test MUST usare valori fittizi e verificare che le credenziali non vengano esposte.
Questo protegge l'utente e riduce il rischio di compromissione del dispositivo e degli account.

### II. Installazione riproducibile
L'installazione MUST essere descritta da file versionati, con dipendenze e prerequisiti di sistema
espliciti, versioni compatibili dichiarate e una procedura verificabile su Raspberry Pi Zero 2 W.
L'ambiente di sviluppo e quello di esecuzione devono poter essere ricreati senza passaggi manuali
nascosti o installazioni automatiche avviate durante il normale funzionamento.

### III. Test automatici senza hardware reale
Ogni comportamento applicativo significativo MUST essere testabile in CI o su una macchina senza
microfono, speaker, ALSA, Porcupine o rete reale. Le integrazioni hardware e i servizi esterni MUST
essere isolati dietro interfacce sostituibili e coperte da fake, mock o fixture deterministiche.
I test automatici non devono installare pacchetti con privilegi elevati, modificare il sistema o
produrre dipendenza da dispositivi fisici.

### IV. Risorse audio gestite in modo robusto
Microfono, speaker, stream PyAudio, file temporanei e processi audio MUST avere ownership chiara,
rilascio garantito e comportamento definito in caso di errore o interruzione. Il programma MUST
gestire assenza, occupazione o cambiamento dei dispositivi senza terminare con risorse lasciate
aperte; ogni operazione audio deve avere timeout o limite di durata quando applicabile. Il codice
non deve assumere indici o nomi hardware fissi senza una configurazione o una rilevazione verificata.

### V. Configurazione esplicita tramite ambiente
Le impostazioni dipendenti dall'ambiente, incluse chiavi, endpoint, modello, lingua, dispositivi,
timeout e livelli audio, MUST essere configurabili tramite variabili d'ambiente documentate. Il
programma MUST validare i valori all'avvio, applicare default sicuri e comunicare quale configurazione
non è valida senza stampare segreti. La logica applicativa non deve dipendere da valori hard-coded
legati a una singola installazione.

### VI. Modularità e manutenibilità
Le responsabilità di configurazione, rete, riconoscimento vocale, sintesi, riproduzione audio e
interfaccia utente MUST essere separabili tramite moduli e contratti piccoli. Le nuove funzionalità
devono poter essere testate senza inizializzare l'intero dispositivo; lo stato globale e gli effetti
collaterali all'importazione MUST essere evitati. Ogni modifica deve mantenere nomi, eccezioni e
confini comprensibili e preferire la soluzione più semplice compatibile con i requisiti.

### VII. Errori di rete espliciti e recuperabili
Timeout, errori DNS o di connessione, risposte HTTP non riuscite, payload non validi e limiti del
servizio MUST essere distinti e convertiti in errori o messaggi applicativi comprensibili. Le
richieste verso servizi esterni MUST avere timeout configurati e non devono esporre API key o dati
sensibili nei log. Retry e fallback sono ammessi solo se limitati, ritardati e idempotenti; in caso
di indisponibilità il sistema deve rilasciare le risorse audio e restituire uno stato operativo
prevedibile.

### VIII. Documentazione coerente con il comportamento reale
README, esempi, file di configurazione e troubleshooting MUST descrivere comandi, dipendenze,
variabili, limiti e flussi effettivamente implementati. Ogni modifica osservabile del comportamento
deve aggiornare la documentazione nella stessa modifica o dichiarare il lavoro residuo. Le istruzioni
non devono suggerire credenziali reali, installazioni distruttive o capacità non supportate.

### IX. Compatibilità con Raspberry Pi Zero 2 W
Ogni scelta architetturale MUST rispettare CPU, RAM, storage, alimentazione e latenza limitati del
Raspberry Pi Zero 2 W. Il sistema deve limitare processi concorrenti, buffer, file temporanei e
consumo di rete; deve evitare dipendenze inutilmente pesanti e rendere configurabili timeout e
qualità audio. Le prestazioni e i fallback devono essere verificabili con test o misurazioni
riproducibili su hardware equivalente, senza sacrificare sicurezza e correttezza.

## Vincoli operativi

Il runtime target è Raspberry Pi Zero 2 W con Linux e Python supportati dal set di dipendenze del
progetto. Le integrazioni cloud, speech-to-text, text-to-speech, wake word e audio locale sono
confini esterni: ciascuna deve avere un adapter sostituibile. Nessun componente deve installare
dipendenze di sistema o modificare privilegi durante l'esecuzione dell'assistente.

## Flusso di sviluppo

Ogni cambiamento deve includere test automatici per il comportamento modificato e aggiornamenti alla
documentazione quando cambiano configurazione, installazione, output o gestione degli errori. Prima
dell'integrazione devono essere eseguiti i test senza hardware e i controlli statici disponibili;
le prove su Raspberry Pi sono aggiuntive e non sostituiscono la suite isolata. Le revisioni devono
verificare esplicitamente segreti, cleanup delle risorse, timeout di rete, compatibilità con il
target e coerenza fra codice e documentazione.

## Governance

Questa costituzione prevale sulle pratiche locali incompatibili. Un emendamento MUST descrivere
motivazione, impatto, principi coinvolti e piano di migrazione quando modifica contratti o comporta
un rischio operativo; deve aggiornare questo documento e i test o la documentazione necessari nella
stessa modifica. Le revisioni del progetto devono controllare la conformità ai principi prima del
rilascio.

La versione segue il versionamento semantico: MAJOR per rimozioni o ridefinizioni incompatibili dei
principi, MINOR per nuovi principi o ampliamenti sostanziali, PATCH per chiarimenti e correzioni
non semantiche. La data di ultima modifica è aggiornata a ogni emendamento accettato. Le eccezioni
temporanee MUST essere documentate con motivazione, ambito, responsabile e data di riesame; non
possono diventare comportamento implicito.

**Version**: 1.0.0 | **Ratified**: TODO(RATIFICATION_DATE): data di adozione originale non presente nel repository | **Last Amended**: 2026-10-29
