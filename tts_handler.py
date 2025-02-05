import os
import openai
from pathlib import Path
import subprocess

class TTSHandler:
    def __init__(self):
        self.client = openai.OpenAI()
        self.output_dir = Path("audio_output")
        self.output_dir.mkdir(exist_ok=True)
    
    def text_to_speech(self, text, voice="alloy"):
        """
        Convert text to speech using OpenAI's TTS API
        :param text: The text to convert to speech
        :param voice: The voice to use (alloy, echo, fable, onyx, nova, or shimmer)
        :return: Path to the generated audio file
        """
        try:
            output_file = self.output_dir / f"speech_{hash(text)}.mp3"
            
            # Generate speech using OpenAI's API
            response = self.client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text
            )
            
            # Save the audio file
            response.stream_to_file(str(output_file))
            
            return output_file
            
        except Exception as e:
            print(f"Error generating speech: {e}")
            return None
    
    def play_audio(self, audio_file):
        """
        Play the audio file using macOS's afplay command
        :param audio_file: Path to the audio file
        """
        try:
            subprocess.run(['afplay', str(audio_file)], check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error playing audio: {e}")
            return False

def main():
    # Test the TTS functionality
    tts = TTSHandler()
    test_text = "Hello! This is a test of the text to speech system."
    audio_file = tts.text_to_speech(test_text)
    if audio_file:
        tts.play_audio(audio_file)

if __name__ == "__main__":
    main() 