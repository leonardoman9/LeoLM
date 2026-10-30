# Privacy and online services

LeoLM keeps the current conversation text in memory to provide context for subsequent interactions.
Each valid interaction resets the timer; after 600 seconds of inactivity, the context is deleted.
Audio and TTS responses are temporary, and no persistent local history is stored.

Text and context may be sent to configured speech recognition, conversational model, and text-to-speech
services when required by the provider. Wake-word audio is processed locally by Vosk and is not sent
to a wake-word provider. Network retry attempts and timeouts are
limited; after the
last error, the system returns to listening. Retention by external providers depends on their
policies and is not controlled by LeoLM.

API keys, tokens, Wi-Fi passwords, and real profiles must remain outside the repository and must not
appear in logs, output, tests, or public templates. During SSH deployment, a temporary copy may
exist on the target and is removed at the end; Wi-Fi keyfiles use restrictive permissions.

Deployment does not send audio or transcripts; it transfers configuration and code only. The runtime
does send audio/text to configured providers. MCP is neither installed nor exposed.
