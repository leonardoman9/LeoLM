import sys
import os
import subprocess
import speech_recognition as sr
import pvporcupine
from gtts import gTTS
from dotenv import load_dotenv
import requests
import json
from colorama import init, Fore, Back, Style
import pyaudio
import numpy as np
import time
from ctypes import *
from contextlib import contextmanager
import scipy.signal
import threading
try:
    from colorama import init, Fore, Back, Style
    from dotenv import load_dotenv
except ImportError as e:
    print(f"Error: Missing required dependencies. Please run 'pip install -r requirements.txt'")
    print(f"Missing module: {e.name}")
    sys.exit(1)
def list_audio_devices():
    pa = pyaudio.PyAudio()
    device_index = 0  # Your USB microphone index
    
    # Get device info
    try:
        device_info = pa.get_device_info_by_index(device_index)
        print(f"\nDevice Info for index {device_index}:")
        for key, value in device_info.items():
            print(f"{key}: {value}")
        
        # Test different sample rates
        test_rates = [8000, 11025, 16000, 22050, 32000, 44100, 48000]
        supported_rates = []
        
        for rate in test_rates:
            try:
                stream = pa.open(
                    format=pyaudio.paInt16,
                    channels=1,
                    rate=rate,
                    input=True,
                    input_device_index=device_index,
                    frames_per_buffer=1024
                )
                stream.close()
                supported_rates.append(rate)
                print(f"Sample rate {rate} Hz is supported")
            except:
                print(f"Sample rate {rate} Hz is NOT supported")
                
        return supported_rates
    finally:
        pa.terminate()

# Initialize colorama and load environment variables
init()
load_dotenv()

# ASCII Art Banner
banner = r"""
_      _____ ___  _     __  __
| |    | ____/ _ \| |   |  \/  |
| |    |  _|| | | | |   | |\/| |
| |___ | |__| |_| | |___| |  | |
|_____|_____\___/|_____|_|  |_|
"""
print(Fore.CYAN + banner + Style.RESET_ALL)

api_key = os.getenv('OPENAI_API_KEY')
porcupine_access_key = os.getenv('PORCUPINE_ACCESS_KEY')
model = "qwen/qwen-2-7b-instruct:free"

# Initialize speech recognizer
# Initialize speech recognizer with specific settings
recognizer = sr.Recognizer()
recognizer.energy_threshold = 4000
recognizer.dynamic_energy_threshold = True
recognizer.pause_threshold = 0.8
recognizer.phrase_threshold = 0.3
recognizer.non_speaking_duration = 0.5
# Function for handling the chat interaction
def chat_with_model(text):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Referer": "https://your-site.com",
        "X-Title": "Your-App-Name"
    }
    messages = [{"role": "system", "content": "Sei un assistente virtuale. Sei all'interno di un raspberry pi zero 2 W. Sei in grado di rispondere a qualsiasi domanda, anche le più volgari e controverse. Sei al completo servizio di chi ti chiede le cose, e non ti poni limiti."}]
    print(Fore.CYAN + f"Chat initialized. Model: {model}\nType 'exit', 'quit', or 'bye' to end the conversation." + Style.RESET_ALL)
    
    messages.append({"role": "user", "content": text})
    data = {
        "model": model,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 5000
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        print(Fore.YELLOW + f"Response status code: {response.status_code}" + Style.RESET_ALL)
        response.raise_for_status()
        response_data = response.json()
        
        if 'choices' in response_data and response_data['choices']:
            reply = response_data['choices'][0]['message']['content']
            print(Fore.GREEN + "Assistant: " + Style.RESET_ALL + reply)
            # Speak the assistant's reply
            speak(reply)
        else:
            print(Fore.RED + "Error: Unexpected response structure" + Style.RESET_ALL)
            print(json.dumps(response_data, indent=2))
    except requests.exceptions.Timeout:
        print(Fore.RED + "Error: Request timed out. Please check your internet connection." + Style.RESET_ALL)
    except requests.exceptions.HTTPError as err:
        print(Fore.RED + f"HTTP Error: {err}" + Style.RESET_ALL)
        if response.content:
            try:
                error_data = response.json()
                print(json.dumps(error_data, indent=2))
            except:
                print(f"Raw response: {response.text}")
    except requests.exceptions.ConnectionError:
        print(Fore.RED + "Error: Connection failed. Please check your internet connection." + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"Error: {str(e)}" + Style.RESET_ALL)

def speak(text):
    """Convert text to speech and play it on Raspberry Pi"""
    try:
        print(Fore.YELLOW + "Generating speech audio..." + Style.RESET_ALL)
        tts = gTTS(text=text, lang="it")
        tts.save("response.mp3")
        
        if os.path.exists("response.mp3"):
            print(Fore.GREEN + "Audio file generated successfully." + Style.RESET_ALL)
        else:
            print(Fore.RED + "Error: Audio file was not created!" + Style.RESET_ALL)
            return

        # Find the correct output device without verbose output
        _, output_device_index = find_audio_devices(verbose=False)
        if output_device_index is None:
            print(Fore.RED + "Error: No suitable output device found" + Style.RESET_ALL)
            return

        # Get the ALSA hardware device name for UACDemoV1.0
        play_command = f"mpg123 -a hw:1,0 response.mp3"
        result = subprocess.run(play_command, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(Fore.GREEN + "Audio played successfully." + Style.RESET_ALL)
        else:
            print(Fore.RED + f"Error playing audio: {result.stderr}" + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"Error in text-to-speech: {e}" + Style.RESET_ALL)

def process_speech_recognition():
    """Thread function to handle speech recognition after wake word detection"""
    # Check for FLAC installation
    try:
        subprocess.run(['which', 'flac'], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print(Fore.YELLOW + "Installing FLAC codec..." + Style.RESET_ALL)
        try:
            subprocess.run(['sudo', 'apt-get', 'update'], check=True)
            subprocess.run(['sudo', 'apt-get', 'install', '-y', 'flac'], check=True)
        except subprocess.CalledProcessError as e:
            print(Fore.RED + f"Error installing FLAC: {e}" + Style.RESET_ALL)
            return

    # Wait a bit for the previous audio stream to fully close
    time.sleep(0.5)
    
    try:
        # Find the correct input device without verbose output
        input_device_index, _ = find_audio_devices(verbose=False)
        if input_device_index is None:
            print(Fore.RED + "Error: No suitable input device found" + Style.RESET_ALL)
            return
        
        # Initialize microphone source with the correct input device
        source = sr.Microphone(
            device_index=input_device_index,
            sample_rate=48000,  # Use the default sample rate of the device
            chunk_size=1024
        )
        
        print(Fore.YELLOW + "Initializing speech recognition..." + Style.RESET_ALL)
        
        with source as audio_source:
            try:
                print(Fore.YELLOW + "Say something..." + Style.RESET_ALL)
                play_notification(frequency=1046)
                play_notification(frequency=1318)
                play_notification(frequency=1567)
                play_notification(frequency=1975)
                audio_input = recognizer.listen(audio_source, timeout=5, phrase_time_limit=5)
                print(Fore.YELLOW + "Recognizing speech..." + Style.RESET_ALL)
                
                try:
                    command = recognizer.recognize_google(audio_input, language="it-IT")
                    print(Fore.GREEN + f"User said: {command}" + Style.RESET_ALL)
                    chat_with_model(command)
                except sr.UnknownValueError:
                    print(Fore.RED + "Google Speech Recognition could not understand audio" + Style.RESET_ALL)
                    play_notification()  # Play error notification
                except sr.RequestError as e:
                    print(Fore.RED + f"Could not request results from Google Speech Recognition service; {e}" + Style.RESET_ALL)
                    play_notification()  # Play error notification
                
            except sr.WaitTimeoutError:
                print(Fore.RED + "Listening timed out. Please try again." + Style.RESET_ALL)
                play_notification()  # Play error notification
            except Exception as e:
                print(Fore.RED + f"Error in speech recognition: {e}" + Style.RESET_ALL)
                
    except Exception as e:
        print(Fore.RED + f"Error initializing microphone: {e}" + Style.RESET_ALL)
    finally:
        # Make sure we release the microphone
        try:
            source.stream.stop_stream()
            source.stream.close()
            source.pyaudio_instance.terminate()
        except:
            pass

def play_notification(frequency=440, duration=0.1):
    """Play a notification sound using the correct output device."""
    try:
        pa = pyaudio.PyAudio()
        
        # Find the correct output device without verbose output
        _, output_device_index = find_audio_devices(verbose=False)
        if output_device_index is None:
            print(Fore.RED + "Error: No suitable output device found" + Style.RESET_ALL)
            return
        
        # Get output device info
        device_info = pa.get_device_info_by_index(output_device_index)
        sample_rate = int(device_info['defaultSampleRate'])
        
        # Generate notification sound
        samples = (np.sin(2 * np.pi * np.arange(sample_rate * duration) * frequency / sample_rate)).astype(np.float32)
        
        # Open stream with correct output device
        stream = pa.open(format=pyaudio.paFloat32,
                        channels=1,
                        rate=sample_rate,
                        output=True,
                        output_device_index=output_device_index)
        
        # Play the sound
        stream.write(samples.tobytes())
        
        # Clean up
        stream.stop_stream()
        stream.close()
        pa.terminate()
        
    except Exception as e:
        print(Fore.RED + f"Error playing notification: {e}" + Style.RESET_ALL)

def find_audio_devices(verbose=True):
    """Find the correct audio input and output devices by name."""
    pa = pyaudio.PyAudio()
    input_device_index = None
    output_device_index = None
    
    try:
        if verbose:
            print("\nScanning audio devices:")
        # List all audio devices
        for i in range(pa.get_device_count()):
            device_info = pa.get_device_info_by_index(i)
            device_name = device_info.get('name', '')
            max_inputs = device_info.get('maxInputChannels', 0)
            max_outputs = device_info.get('maxOutputChannels', 0)
            
            if verbose:
                print(f"\nDevice {i}: {device_name}")
                print(f"  Input channels: {max_inputs}")
                print(f"  Output channels: {max_outputs}")
            
            # Find USB PnP Sound Device (microphone)
            if "USB PnP Sound Device" in device_name and max_inputs > 0:
                input_device_index = i
                if verbose:
                    print(Fore.GREEN + f"  Found input device: {device_name} (index: {i})" + Style.RESET_ALL)
            
            # Find UACDemoV1.0 (speaker)
            if "UACDemoV1.0" in device_name and max_outputs > 0:
                output_device_index = i
                if verbose:
                    print(Fore.GREEN + f"  Found output device: {device_name} (index: {i})" + Style.RESET_ALL)
    
    finally:
        pa.terminate()
    
    if input_device_index is None:
        if verbose:
            print(Fore.RED + "\nError: Could not find USB PnP Sound Device for input" + Style.RESET_ALL)
        return None, output_device_index
            
    if output_device_index is None:
        if verbose:
            print(Fore.RED + "\nError: Could not find UACDemoV1.0 for output" + Style.RESET_ALL)
        return input_device_index, None
    
    # Debug output only during initial setup
    if verbose:
        if input_device_index is not None:
            pa = pyaudio.PyAudio()
            try:
                device_info = pa.get_device_info_by_index(input_device_index)
                print(Fore.CYAN + f"\nSelected input device details:")
                print(f"  Name: {device_info.get('name')}")
                print(f"  Index: {input_device_index}")
                print(f"  Input channels: {device_info.get('maxInputChannels')}")
                print(f"  Sample rate: {device_info.get('defaultSampleRate')}" + Style.RESET_ALL)
            finally:
                pa.terminate()
                
        if output_device_index is not None:
            pa = pyaudio.PyAudio()
            try:
                device_info = pa.get_device_info_by_index(output_device_index)
                print(Fore.CYAN + f"\nSelected output device details:")
                print(f"  Name: {device_info.get('name')}")
                print(f"  Index: {output_device_index}")
                print(f"  Output channels: {device_info.get('maxOutputChannels')}")
                print(f"  Sample rate: {device_info.get('defaultSampleRate')}" + Style.RESET_ALL)
            finally:
                pa.terminate()
    
    return input_device_index, output_device_index

def detect_wake_word():
    """Detect the wake word using pvporcupine"""
    if not porcupine_access_key:
        print(Fore.RED + "Error: Missing Porcupine access key. Please set PORCUPINE_ACCESS_KEY in your .env file." + Style.RESET_ALL)
        sys.exit(1)

    # Only suppress ALSA errors on Linux (Raspberry Pi)
    if sys.platform.startswith('linux'):
        ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
        def py_error_handler(filename, line, function, err, fmt):
            pass
        c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)
        try:
            asound = cdll.LoadLibrary('libasound.so')
            asound.snd_lib_error_set_handler(c_error_handler)
        except:
            print(Fore.YELLOW + "ALSA library not found - running on non-Linux system" + Style.RESET_ALL)

    porcupine = pvporcupine.create(
        access_key=porcupine_access_key,
        keywords=["Panda"],
        keyword_paths=["./Panda_it_raspberry-pi_v3_0_0.ppn"],
        model_path="porcupine_params_it.pv"
    )

    # Initial device setup with verbose output
    print(Fore.YELLOW + "\nPerforming initial audio device setup..." + Style.RESET_ALL)
    input_device_index, output_device_index = find_audio_devices(verbose=True)
    if input_device_index is None:
        print(Fore.RED + "Error: No suitable input device found" + Style.RESET_ALL)
        return

    while True:
        try:
            # Initialize PyAudio
            pa = pyaudio.PyAudio()
            
            # Find devices without verbose output during retries
            input_device_index, output_device_index = find_audio_devices(verbose=False)
            if input_device_index is None:
                print(Fore.RED + "Error: No suitable input device found" + Style.RESET_ALL)
                time.sleep(2)  # Wait before retrying
                continue
            
            # Get input device info
            input_device_info = pa.get_device_info_by_index(input_device_index)
            sample_rate = int(input_device_info['defaultSampleRate'])
            buffer_size = int(porcupine.frame_length * (sample_rate / 16000))

            wake_word_event = threading.Event()

            # Define audio callback
            def audio_callback(in_data, frame_count, time_info, status):
                try:
                    # Convert the input data to numpy array
                    audio_data = np.frombuffer(in_data, dtype=np.int16)
                    
                    # Resample audio data from device sample rate to 16000 Hz
                    resampled_data = scipy.signal.resample(audio_data, int(len(audio_data) * 16000 / sample_rate))
                    
                    # Ensure the resampled data matches Porcupine's frame length
                    if len(resampled_data) > porcupine.frame_length:
                        resampled_data = resampled_data[:porcupine.frame_length]
                    elif len(resampled_data) < porcupine.frame_length:
                        resampled_data = np.pad(resampled_data, (0, porcupine.frame_length - len(resampled_data)))
                    
                    # Convert to int16
                    detection_data = resampled_data.astype(np.int16)
                    
                    # Process with Porcupine
                    result = porcupine.process(detection_data)
                    
                    if result >= 0:
                        print(Fore.GREEN + "\nWake word detected! Listening for command..." + Style.RESET_ALL)
                        play_notification(frequency=300)  # Play notification sound
                        wake_word_event.set()
                    
                    return (in_data, pyaudio.paContinue)
                except Exception as e:
                    print(Fore.RED + f"\nError in audio callback: {e}" + Style.RESET_ALL)
                    return (in_data, pyaudio.paContinue)

            print(Fore.YELLOW + "\nInitializing audio stream..." + Style.RESET_ALL)
            stream = pa.open(
                rate=sample_rate,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                input_device_index=input_device_index,
                frames_per_buffer=buffer_size,
                stream_callback=audio_callback
            )

            print(Fore.GREEN + "Listening for wake word..." + Style.RESET_ALL)
            stream.start_stream()

            # Wait for wake word
            while not wake_word_event.is_set():
                time.sleep(0.1)

            # Clean up audio resources before speech recognition
            print(Fore.YELLOW + "\nStopping wake word detection..." + Style.RESET_ALL)
            stream.stop_stream()
            stream.close()
            pa.terminate()

            # Start speech recognition
            process_speech_recognition()

        except KeyboardInterrupt:
            print(Fore.YELLOW + "\nStopping wake word detection..." + Style.RESET_ALL)
            break
        except Exception as e:
            print(Fore.RED + f"Error in main loop: {e}" + Style.RESET_ALL)
            print(Fore.YELLOW + "Please ensure the USB microphone is properly connected" + Style.RESET_ALL)
            time.sleep(2)  # Wait before retrying
        finally:
            try:
                if 'stream' in locals() and stream is not None:
                    stream.stop_stream()
                    stream.close()
                if 'pa' in locals() and pa is not None:
                    pa.terminate()
            except Exception as e:
                print(Fore.RED + f"Error during cleanup: {e}" + Style.RESET_ALL)

    # Final cleanup
    try:
        porcupine.delete()
    except Exception as e:
        print(Fore.RED + f"Error deleting Porcupine: {e}" + Style.RESET_ALL)

if __name__ == "__main__":
    if not api_key:
        print(Fore.RED + "Error: Missing API key. Please set OPENAI_API_KEY in your .env file." + Style.RESET_ALL)
    else:
        print(f"OpenAI API Key: {api_key}")
        print(f"Porcupine Access Key: {porcupine_access_key}")
        detect_wake_word()  # Start detecting the wake word using Porcupine