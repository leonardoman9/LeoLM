import os
import wave
import struct
import numpy as np

def generate_test_wav():
    # Audio parameters
    duration = 2  # seconds
    sample_rate = 44100
    frequency = 440  # Hz (A4 note)
    amplitude = 0.5

    # Generate samples
    samples = amplitude * np.sin(2 * np.pi * frequency * np.linspace(0, duration, int(duration * sample_rate)))
    
    # Convert to 16-bit PCM
    samples = (samples * 32767).astype(np.int16)

    # Create WAV file
    with wave.open('test_tone.wav', 'w') as wav_file:
        # Set parameters
        wav_file.setnchannels(2)  # Stereo
        wav_file.setsampwidth(2)  # 2 bytes per sample
        wav_file.setframerate(sample_rate)
        
        # Write stereo by duplicating mono samples
        stereo_samples = np.column_stack((samples, samples))
        wav_file.writeframes(stereo_samples.tobytes())

    print("WAV file created successfully")
    return 'test_tone.wav'

def play_audio(filename):
    try:
        # Try different play commands
        commands = [
            ['aplay', '-D', 'plughw:0,0', filename],
            ['aplay', '-D', 'default', filename],
            ['paplay', filename],
            ['ffplay', '-nodisp', '-autoexit', filename]
        ]
        
        for cmd in commands:
            try:
                print(f"Trying to play with {cmd[0]}...")
                os.system(' '.join(cmd))
                return True
            except Exception as e:
                print(f"Failed with {cmd[0]}: {e}")
                continue
                
    except Exception as e:
        print(f"Error playing audio: {e}")
        return False
    
    return False

def main():
    # First, make sure we have the necessary tools
    os.system('sudo apt-get update')
    os.system('sudo apt-get install -y alsa-utils pulseaudio ffmpeg')
    
    # Generate test tone
    wav_file = generate_test_wav()
    
    # Try to play it
    if not play_audio(wav_file):
        print("Failed to play audio with all methods")
    
    # Clean up
    if os.path.exists(wav_file):
        os.remove(wav_file)

if __name__ == "__main__":
    main()
