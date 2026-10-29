# Release checklist documentale

- [ ] Eseguire `python scripts/check_docs.py --root . --json` senza rete e senza credenziali reali.
- [ ] Eseguire `pytest tests/documentation -q` e la suite automatica completa.
- [ ] Verificare README, configurazione, deployment, privacy, dipendenze e troubleshooting.
- [ ] Verificare link locali, comandi, percorsi, profili e dipendenze in un ambiente isolato o con test equivalente.
- [ ] Verificare che template e profili pubblici non contengano API key, password Wi-Fi, token o audio.
- [ ] Verificare timeout/retry, contesto di 600 secondi, cleanup audio e limiti dei provider.
- [ ] Eseguire separatamente i test hardware opt-in prima di distribuire immagini.
- [ ] Confermare che MCP sia descritto come fuori scope finché non esiste un'integrazione verificata.
