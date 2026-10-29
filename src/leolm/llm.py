"""Conversation service adapter with bounded retries and safe errors."""

from __future__ import annotations

import time

import requests

from .errors import ExternalServiceError


class OpenRouterConversation:
    def __init__(self, config, client=None, sleeper=time.sleep):
        self.config = config
        self.client = client or requests
        self.sleeper = sleeper

    def complete(self, turns):
        headers = {"Authorization": f"Bearer {self.config.conversation_api_key}", "Content-Type": "application/json"}
        payload = {"model": self.config.model, "messages": list(turns), "temperature": 0.7, "max_tokens": 5000}
        last_error = None
        for attempt in range(self.config.retry_count + 1):
            try:
                response = self.client.post(self.config.conversation_endpoint, headers=headers, json=payload,
                                            timeout=self.config.network_timeout)
                response.raise_for_status()
                body = response.json()
                reply = body.get("choices", [{}])[0].get("message", {}).get("content")
                if not isinstance(reply, str) or not reply.strip():
                    raise ExternalServiceError("Invalid conversation response", "Risposta del servizio non valida")
                return reply.strip()
            except ExternalServiceError:
                raise
            except requests.exceptions.Timeout as exc:
                last_error = ExternalServiceError("Conversation request timed out", "Il servizio ha superato il timeout", True)
            except requests.exceptions.ConnectionError as exc:
                last_error = ExternalServiceError("Conversation connection failed", "Servizio non raggiungibile", True)
            except requests.exceptions.HTTPError as exc:
                retryable = getattr(response, "status_code", 500) >= 500 or getattr(response, "status_code", 500) == 429
                last_error = ExternalServiceError("Conversation HTTP request failed", "Il servizio ha restituito un errore", retryable)
            except (ValueError, KeyError, IndexError) as exc:
                last_error = ExternalServiceError("Invalid conversation payload", "Risposta del servizio non valida")
            if not last_error.retryable or attempt >= self.config.retry_count:
                raise last_error
            self.sleeper(self.config.retry_backoff * (2 ** attempt))
        raise last_error or ExternalServiceError("Conversation request failed", "Richiesta non riuscita")
