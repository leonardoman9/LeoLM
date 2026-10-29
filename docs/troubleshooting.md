# Troubleshooting

## Configurazione

Usare `docs/configuration.md` come riferimento. Un errore indica il nome della variabile, mai il suo valore. Gli asset wake word devono esistere nei percorsi configurati e i selettori audio devono corrispondere al dispositivo disponibile.

## Rete e provider

Le richieste remote hanno timeout configurabile e retry limitati. Dopo l'ultimo errore LeoLM rilascia le risorse audio e torna alla wake word/ascolto. Verificare endpoint, DNS, connettività e policy del provider senza inserire API key nei comandi o nei log.

## Deployment e boot

Controllare NetworkManager, poi `systemctl status leolm.service` e `journalctl -u leolm.service`. Su immagini cross-architettura verificare prima `leolm-bootstrap.service`; il bootstrap installa il virtual environment al primo boot dopo `network-online.target` e si disabilita dopo il successo.

## Privacy

Il contesto conversazionale scade dopo 600 secondi dall'ultima interazione valida. Audio e TTS sono temporanei; la retention dei servizi online dipende dai provider. Per la procedura PC→Raspberry consultare [deployment.md](deployment.md) e per i dati consultare [privacy.md](privacy.md).
