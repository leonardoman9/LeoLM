"""Deployment errors with safe user-facing messages."""

from __future__ import annotations


class DeploymentError(Exception):
    def __init__(self, message: str, *, safe_message: str | None = None) -> None:
        super().__init__(message)
        self.safe_message = safe_message or message


class ProfileError(DeploymentError):
    pass


class TargetError(DeploymentError):
    pass


class TransportError(DeploymentError):
    pass
