import pyaudio

def list_audio_devices():
    pa = pyaudio.PyAudio()
    print("\nAvailable audio devices:")
    for i in range(pa.get_device_count()):
        dev_info = pa.get_device_info_by_index(i)
        print(f"Device {i}: {dev_info['name']}")
        print(f"Max Input Channels: {dev_info['maxInputChannels']}")
        print(f"Default Sample Rate: {dev_info['defaultSampleRate']}")
        print("---")
    pa.terminate()

if __name__ == "__main__":
    list_audio_devices() 