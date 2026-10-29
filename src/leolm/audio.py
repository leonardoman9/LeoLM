"""Audio device discovery and idempotent resource ownership."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .errors import AudioError


class ResourceLease:
    def __init__(self, resource: Any, closer=None):
        self.resource = resource
        self._closer = closer or getattr(resource, "close", None)
        self.released = False

    def close(self) -> None:
        if self.released:
            return
        self.released = True
        if self._closer:
            self._closer()

    def __enter__(self):
        return self.resource

    def __exit__(self, exc_type, exc, tb):
        self.close()


@dataclass(frozen=True)
class Device:
    index: int
    name: str
    role: str
    sample_rate: int
    channels: int


class AudioManager:
    def __init__(self, backend=None):
        self._backend = backend
        self._pa = None

    def _get_backend(self):
        if self._backend is None:
            try:
                import pyaudio
            except ImportError as exc:
                raise AudioError("PyAudio is not installed", "Dipendenza audio non disponibile") from exc
            self._backend = pyaudio
        if self._pa is None:
            self._pa = self._backend.PyAudio()
        return self._backend

    def close(self) -> None:
        if self._pa is not None:
            self._pa.terminate()
            self._pa = None

    def list_devices(self) -> list[dict[str, Any]]:
        self._get_backend()
        return [self._pa.get_device_info_by_index(i) for i in range(self._pa.get_device_count())]

    def resolve(self, selector: str | None, role: str) -> Device:
        self._get_backend()
        required = "maxInputChannels" if role == "input" else "maxOutputChannels"
        for index, info in enumerate(self.list_devices()):
            name = str(info.get("name", ""))
            matches = selector is None or selector == str(index) or selector.casefold() in name.casefold()
            if matches and int(info.get(required, 0)) > 0:
                return Device(index, name, role, int(float(info.get("defaultSampleRate", 16000))), int(info[required]))
        raise AudioError(f"No {role} audio device matches configured selector", f"Dispositivo {role} non disponibile")

    def open_input(self, device: Device, *, rate: int | None = None, frames: int = 1024) -> ResourceLease:
        pyaudio = self._get_backend()
        try:
            stream = self._pa.open(format=pyaudio.paInt16, channels=1, rate=rate or device.sample_rate,
                                   input=True, input_device_index=device.index, frames_per_buffer=frames)
        except Exception as exc:
            raise AudioError("Unable to open input stream", "Microfono non disponibile") from exc
        return ResourceLease(stream, lambda: self._close_stream(stream))

    def open_output(self, device: Device, *, rate: int | None = None) -> ResourceLease:
        pyaudio = self._get_backend()
        try:
            stream = self._pa.open(format=pyaudio.paFloat32, channels=1, rate=rate or device.sample_rate,
                                   output=True, output_device_index=device.index)
        except Exception as exc:
            raise AudioError("Unable to open output stream", "Speaker non disponibile") from exc
        return ResourceLease(stream, lambda: self._close_stream(stream))

    @staticmethod
    def _close_stream(stream) -> None:
        for method in ("stop_stream", "close"):
            try:
                getattr(stream, method)()
            except Exception:
                pass
