"""Feedback sounds generated in memory and played via aplay."""

from __future__ import annotations

import io
import math
import struct
import subprocess
import wave


SAMPLE_RATE = 48000
CHANNELS = 2


def _tone(frequency: float, duration: float, volume: float = 0.5) -> list[int]:
    """Generate mono samples for a sine tone."""
    count = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(count):
        fade = min(i, count - i, int(SAMPLE_RATE * 0.005)) / max(int(SAMPLE_RATE * 0.005), 1)
        value = volume * fade * math.sin(2 * math.pi * frequency * i / SAMPLE_RATE)
        samples.append(int(value * 32767))
    return samples


def _stereo(mono: list[int]) -> bytes:
    """Duplicate mono samples to stereo interleaved int16."""
    frames = []
    for s in mono:
        frames.append(struct.pack("<hh", s, s))
    return b"".join(frames)


def _to_wav(pcm: bytes, n_frames: int) -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(pcm)
    return buf.getvalue()


def _make_startup() -> bytes:
    """Ascending two-tone chime."""
    t1 = _tone(523, 0.15, 0.4)   # C5
    gap = [0] * int(SAMPLE_RATE * 0.05)
    t2 = _tone(784, 0.25, 0.5)   # G5
    mono = t1 + gap + t2
    return _to_wav(_stereo(mono), len(mono))


def _make_wake() -> bytes:
    """Short bright ding — wake word acknowledged."""
    mono = _tone(880, 0.12, 0.5)  # A5
    return _to_wav(_stereo(mono), len(mono))


def _make_thinking() -> bytes:
    """Two quick low beeps — processing started."""
    t1 = _tone(660, 0.08, 0.35)  # E5
    gap = [0] * int(SAMPLE_RATE * 0.06)
    t2 = _tone(660, 0.08, 0.35)
    mono = t1 + gap + t2
    return _to_wav(_stereo(mono), len(mono))


# Pre-generate at import time — tiny cost, avoids repeated work.
_SOUNDS: dict[str, bytes] = {}


def _ensure_sounds() -> None:
    if not _SOUNDS:
        _SOUNDS["startup"] = _make_startup()
        _SOUNDS["wake"] = _make_wake()
        _SOUNDS["thinking"] = _make_thinking()


class SoundPlayer:
    def __init__(self, device: str | None = None):
        self.device = device

    def play(self, name: str) -> None:
        _ensure_sounds()
        wav_data = _SOUNDS.get(name)
        if wav_data is None:
            return
        cmd = ["aplay", "-q"]
        if self.device:
            cmd.extend(["-D", self.device])
        try:
            subprocess.run(cmd, input=wav_data, check=False, timeout=5,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass  # Never crash the app for a feedback sound.
