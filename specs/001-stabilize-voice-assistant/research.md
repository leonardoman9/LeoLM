# Research: Stabilize Voice Assistant

## Decision: Baseline Python moderno e compatibile

**Decision**: usare Python 3.11 come baseline di sviluppo e distribuzione, mantenendo Python 3.9
solo come compatibilità transitoria se il target o una dipendenza non supportano 3.11.

**Rationale**: il repository usa un ambiente 3.9 e una procedura non vincolata; una baseline esplicita
consente installazioni riproducibili e un aggiornamento graduale senza assumere che il Raspberry Pi
abbia l'ultima versione disponibile.

**Alternatives considered**: usare la versione più recente senza verifica sul target è rischioso per
PyAudio, Porcupine e i pacchetti scientifici; restare senza baseline conserva l'installazione non
riproducibile.

## Decision: Dipendenze dichiarate e verificate

**Decision**: mantenere solo dipendenze importate dal percorso supportato, aggiungere il pacchetto di
riconoscimento vocale mancante e dichiarare separatamente i prerequisiti di sistema per FLAC, ALSA,
PortAudio e riproduzione audio. `openai` e `vosk` non sono importati dal percorso attuale e vanno
rimosse dalle dipendenze runtime.

**Rationale**: `openai_request.py` importa `speech_recognition`, `pvporcupine`, `gtts`, `dotenv`,
`requests`, `colorama`, `pyaudio`, `numpy` e `scipy`, ma `requirements.txt` non li rappresenta tutti.
La procedura attuale installa FLAC a runtime e usa un player esterno non documentato.

**Alternatives considered**: installare automaticamente prerequisiti durante l'avvio viola la
costituzione e rende i test non deterministici; lasciare dipendenze inutilizzate aumenta il costo RAM
e la superficie di aggiornamento sul Pi Zero 2 W.

## Decision: Configurazione validata da ambiente

**Decision**: introdurre un oggetto di configurazione immutabile costruito all'avvio da variabili
d'ambiente, con default non sensibili e validazione di percorsi, numeri, timeout, retry e selettori
audio. Le chiavi sono obbligatorie solo quando si avvia il relativo servizio.

**Rationale**: elimina modello, wake word, percorsi `.ppn`/parametri, nomi audio e `hw:1,0` hard-coded;
permette test con configurazioni finte e mantiene il comportamento vocale corrente.

**Alternatives considered**: un file di configurazione versionato non è sufficiente per i segreti;
argomenti CLI da soli non coprono l'avvio automatico del dispositivo.

## Decision: Adapter e ownership delle risorse

**Decision**: isolare audio, wake word, speech recognition, servizio conversazionale e TTS dietro
interfacce minime. Ogni adapter espone un ciclo di vita chiudibile e la sessione coordina cleanup in
ordine inverso all'acquisizione.

**Rationale**: consente fake deterministici e impedisce che il callback audio, PyAudio, Porcupine o un
processo player restino attivi dopo errore o Ctrl-C.

**Alternatives considered**: mantenere inizializzazione globale e cleanup sparsi nel monolite conserva
le perdite attuali e rende impossibili test affidabili senza hardware.

## Decision: Retry e contesto conversazionale

**Decision**: per errori remoti recuperabili eseguire al massimo 3 tentativi totali con ritardo
crescente, poi notificare e tornare alla wake word. Conservare in memoria il testo della conversazione
attiva; ogni interazione valida resetta un timer di inattività di 10 minuti, allo scadere il contesto
viene eliminato.

**Rationale**: la politica è deterministica, limita latenza e consumo di rete, e preserva continuità
senza introdurre persistenza locale di dati vocali o testuali.

**Alternatives considered**: retry illimitati peggiorano l'esperienza e possono bloccare il dispositivo;
nessun contesto romperebbe il comportamento conversazionale richiesto; un database sarebbe eccessivo.

## Decision: Suite automatica distinta dalla suite hardware

**Decision**: usare pytest per unit e integration test con fake, senza import iniziale che apra hardware
o rete. I test hardware vivono in una directory distinta, sono espliciti e richiedono prerequisiti
documentati; non eseguono installazioni o `sudo` automaticamente.

**Rationale**: i test attuali generano audio, chiamano `sudo apt-get` e interrogano dispositivi reali,
quindi non sono adatti a CI.

**Alternatives considered**: un unico comando con test condizionali nasconde dipendenze hardware e
rende difficile sapere quali verifiche siano state realmente eseguite.

## Decision: Documentazione come contratto operativo

**Decision**: aggiornare README e aggiungere privacy/service documentation con matrice delle
dipendenze, variabili d'ambiente, prerequisiti di sistema, dati inviati ai servizi e limiti di
retention esterni al progetto.

**Rationale**: il README attuale descrive una chat testuale diversa dal percorso vocale e omette
dipendenze effettivamente usate.

**Alternatives considered**: mantenere istruzioni narrative non verificabili riprodurrebbe la
divergenza fra comportamento reale e documentazione.
