# Data Model: Raspberry Deployment Profiles

## DeviceProfile

Input `.env` per un solo Raspberry.

- `device_id`: identificatore univoco e sicuro per filesystem/service naming.
- `hostname`: hostname target validato.
- `wifi_ssid`, `wifi_password`, `wifi_country`: dati NetworkManager; password secret.
- `leolm_*`: variabili runtime del contratto LeoLM, incluse API key e access key secret.
- `input_device`, `output_device`: selettori audio configurabili.
- `transport`: `offline` oppure `ssh`.
- `target`: directory root offline o host SSH; non è un segreto.

**Regole**: nomi obbligatori presenti, hostname conforme al formato Linux, encoding UTF-8, valori numerici nei limiti runtime, segreti non vuoti in provisioning reale e mai inclusi nel report.

## DeploymentTarget

Destinazione su cui applicare il profilo.

- `kind`: filesystem/immagine montata oppure host remoto.
- `root`: root directory effettiva dopo controllo del marker target.
- `current_release`: release attiva prima dell'applicazione.
- `staged_release`: directory temporanea preparata.
- `state`: `unvalidated`, `staged`, `committed`, `rolled_back`, `failed`.

Le transizioni irreversibili richiedono validazione iniziale e manifest coerente.

## WifiConnection

Configurazione NetworkManager.

- `connection_id`: nome derivato da `device_id`, non dall'SSID.
- `ssid`: rete da associare.
- `password`: secret trasferito solo nel file target protetto.
- `country`: paese radio.
- `autoconnect`: sempre esplicito e abilitato per il profilo valido.
- `keyfile_permissions`: `0600`, con ownership root, senza contenuto esposto al processo LeoLM.

Reti enterprise e captive portal non supportate devono essere rifiutate o dichiarate esplicitamente.

## LeoLMService

Unità systemd per il servizio.

- `unit_name`: nome stabile per device.
- `user/group`: account dedicato.
- `working_directory`, `environment_file`: percorsi target.
- `after/wants`: dipendenza da `network-online.target`.
- `restart_policy`, `restart_sec`, `start_limit`: recovery senza loop aggressivi.
- `exec_start`: comando applicativo senza segreti inline.

## DeploymentReport

Risultato sanificato di validate/provision/verify.

- `device_id`, `hostname`, `transport`, `state`.
- `checks`: profilo, file, permessi, Wi-Fi, servizio, audio e idempotenza.
- `errors`, `warnings` con campo e causa.

Il report non contiene password, API key, access key, environment completo o comandi con segreti.

## BootstrapJob

Unità one-shot usata quando l'immagine offline è preparata su un'architettura diversa dal Raspberry.

- `architecture_match`: risultato del confronto PC/target.
- `requirements_source`: file runtime versionato.
- `state`: `pending`, `running`, `completed` o `failed`.
- `network_dependency`: `network-online.target`.
- `disable_after_success`: vero; impedisce esecuzioni ripetute.

Il bootstrap deve essere idempotente e non deve registrare segreti.
