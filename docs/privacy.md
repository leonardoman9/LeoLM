# Privacy e servizi online

LeoLM mantiene in memoria il testo della conversazione corrente per fornire contesto alle interazioni successive. Ogni interazione valida resetta il timer; dopo 600 secondi di inattività il contesto viene cancellato. Audio e risposte TTS sono temporanei e non viene salvato uno storico locale persistente.

Il testo e il contesto possono essere inviati ai servizi configurati per riconoscimento vocale, modello conversazionale, sintesi vocale e wake word, se il provider lo richiede. Timeout e retry sono limitati; dopo l'ultimo errore il sistema torna all'ascolto. La retention dei provider esterni dipende dalle loro policy e non è controllata da LeoLM.

API key, token, password Wi-Fi e profili reali devono restare fuori dal repository e non devono comparire in log, output, test o template pubblici. Durante un deployment SSH può esistere una copia temporanea sul target, che viene rimossa al termine; i keyfile Wi-Fi sono protetti con permessi restrittivi.

Il deployment non invia audio o trascrizioni: installa solo configurazione e codice. Il runtime continua invece a inviare audio/testo ai provider configurati. MCP non viene installato né esposto.
