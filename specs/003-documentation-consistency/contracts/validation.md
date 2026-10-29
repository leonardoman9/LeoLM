# Contract: Documentation Validation CLI

Il tool pianificato in `scripts/check_docs.py` analizza il repository in modalità offline.

## Invocation

```text
python scripts/check_docs.py [--root PATH] [--json] [--check-external-links]
```

`--root` è opzionale e serve ai test; `--json` produce un report strutturato senza segreti. Per default il validator è completamente offline. Solo `--check-external-links` abilita il controllo degli URL esterni e i suoi fallimenti restano warning.

## Checks

- link e percorsi locali esistenti;
- variabili d'ambiente coerenti con `docs/configuration.md`;
- placeholder non sostituiti;
- comandi o procedure vietate/non supportate;
- pattern di segreti in documenti, esempi e profili;
- presenza dei documenti richiesti dal set canonico.

I comandi vietati sono almeno `sudo`, `rm -rf`, installazioni di pacchetti durante il runtime, inserimento di API key/password nei comandi e apertura automatica di porte o servizi MCP. Il controllo deve segnalare il comando e la riga senza ristampare segreti.

I link esterni possono essere rilevati senza essere contattati. Se viene aggiunto un controllo opzionale di raggiungibilità, un fallimento esterno è `EXTERNAL_LINK_UNREACHABLE` con severità `warning` e URL/motivo redatti in modo sicuro.

## Exit status

- `0`: nessun errore bloccante; possono esistere warning esterni.
- `1`: almeno un errore locale, di contratto, placeholder, comando o sicurezza.
- `2`: uso non valido del CLI o errore interno del validatore.

L'output testuale deve indicare file e riga; non deve mostrare valori di variabili segrete.
