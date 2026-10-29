# Data Model: Documentation Consistency

## ConfigContract

La tabella canonica delle variabili in `docs/configuration.md`.

- `name`: nome esatto della variabile d'ambiente.
- `scope`: `runtime` oppure `deployment`.
- `required`: se l'avvio richiede il valore.
- `default`: valore documentato quando presente, senza segreti reali.
- `type/format`: tipo, unità e valori ammessi.
- `secret`: se il valore non deve apparire in output o fixture.
- `description`: effetto runtime e comportamento in caso di errore.

**Regole**: nessun nome duplicato nello stesso scope; i default devono coincidere con il parser applicativo o con il deployer; le variabili segrete devono avere esempi fittizi e non possono essere ristampate.

## DocumentationArtifact

Un file appartenente al set documentale.

- `path`: percorso relativo nel repository.
- `role`: guida principale, configurazione, deployment, privacy, dipendenze, troubleshooting o esempio.
- `references`: link e percorsi locali citati.
- `status`: presente e validabile; un riferimento a file assente è errore.

## DeploymentProfile

Profilo `.env` per un singolo dispositivo.

- `target`: hostname o identificatore del Raspberry.
- `variables`: valori non segreti e placeholder conformi al contratto.
- `transport`: provisioning offline/image oppure SSH.
- `secret_source`: file protetto sul PC, mai committato.

## ValidationFinding

Risultato atomico del controllo.

- `severity`: `error` oppure `warning`.
- `code`: categoria stabile, ad esempio `BROKEN_LOCAL_LINK`, `UNKNOWN_ENV`, `SECRET_PATTERN`, `EXTERNAL_LINK_UNREACHABLE`.
- `file` e `line`: posizione nel documento.
- `message`: spiegazione senza valori segreti.

I finding `error` producono exit code non zero; i warning esterni sono riportati ma non bloccano.

## DocumentationValidationReport

Report finale del CLI.

- `files_scanned`: numero di file analizzati.
- `errors`: finding bloccanti.
- `warnings`: finding non bloccanti.
- `passed`: vero solo quando `errors` è vuoto.

Il report deve essere leggibile in CI e non deve includere API key, password, token o contenuto audio.
