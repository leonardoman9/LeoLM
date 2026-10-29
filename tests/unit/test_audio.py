from leolm.audio import AudioManager


class FakePA:
    paInt16 = 8
    paFloat32 = 32

    def __init__(self):
        self.devices = [
            {"name": "USB microphone", "maxInputChannels": 1, "maxOutputChannels": 0, "defaultSampleRate": 16000},
            {"name": "speaker-name", "maxInputChannels": 0, "maxOutputChannels": 2, "defaultSampleRate": 44100},
        ]

    def PyAudio(self):
        return self

    def get_device_count(self):
        return len(self.devices)

    def get_device_info_by_index(self, index):
        return self.devices[index]

    def terminate(self):
        pass


def test_audio_resolution_uses_configured_selector_not_fixed_index():
    manager = AudioManager(FakePA())
    assert manager.resolve("speaker-name", "output").index == 1
    assert manager.resolve("USB microphone", "input").sample_rate == 16000


def test_missing_audio_device_is_reported():
    manager = AudioManager(FakePA())
    try:
        manager.resolve("missing", "input")
    except Exception as exc:
        assert "non disponibile" in exc.safe_message
    else:
        raise AssertionError("missing device should fail")
