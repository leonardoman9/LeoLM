# Quickstart: Documentation Consistency

## Prerequisiti

- checkout del repository;
- Python 3.11–3.14;
- ambiente virtuale del progetto attivo;
- nessun microfono, speaker, Raspberry, servizio online o credenziale reale.

## Validazione locale

Dalla root del repository:

```bash
python scripts/check_docs.py
```

Il comando deve terminare con exit code `0`. Un link locale rotto, una variabile sconosciuta o un pattern di segreto devono produrre exit code `1` con file e riga. Un URL esterno non raggiungibile, quando verificato, deve produrre solo un warning.

Il comando precedente non usa la rete. Per verificare anche gli URL esterni in modo non bloccante:

```bash
python scripts/check_docs.py --check-external-links
```

## Test automatici

```bash
pytest tests/documentation -q
```

I test devono usare fixture temporanee con documenti validi e invalidi per coprire link locali, variabili, placeholder, segreti, report JSON e classificazione degli URL esterni. Non devono aprire dispositivi audio o fare richieste di rete.

## Verifica release

1. Eseguire il controllo documentale e i test automatici.
2. Seguire la guida principale in un ambiente pulito o usare l'equivalente isolato documentato.
3. Verificare che il profilo `.env` non contenga segreti nel repository e che i profili per dispositivi diversi non si sovrascrivano.
4. Controllare privacy, retention del contesto di 10 minuti, timeout/retry e limiti dei provider.
5. Eseguire separatamente le prove hardware sul Raspberry; il passaggio hardware non sostituisce i test automatici.

Per il contratto completo consultare [configuration.md](./contracts/configuration.md) e [validation.md](./contracts/validation.md).
