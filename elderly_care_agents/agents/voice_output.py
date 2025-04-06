import pyttsx3
import pygame
import os
import time

# Initialize pyttsx3 engine globally to avoid "run loop already started" error
engine = pyttsx3.init()
engine.setProperty('rate', 190)
engine.setProperty('voice', 'HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\SPEECH\\Voices\\Tokens\\TTS_MS_EN-US_ZIRA_11.0')

# Initialize pygame mixer once
pygame.mixer.init()

def speak(text):
    try:
        audio_file = 'output.wav'

        # Save the audio to file
        engine.save_to_file(text, audio_file)
        engine.runAndWait()

        # Wait until the file is created (some systems may delay write)
        wait_time = 0
        while not os.path.exists(audio_file) and wait_time < 5:
            time.sleep(0.1)
            wait_time += 0.1

        if not os.path.exists(audio_file):
            print("❌ Error in speak(): output.wav not found.")
            return

        # Play the audio
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            time.sleep(0.1)

    except Exception as e:
        print(f"❌ Error in speak(): {e}")
    finally:
        # Cleanup
        pygame.mixer.music.stop()
        if os.path.exists(audio_file):
            try:
                os.remove(audio_file)
            except Exception as e:
                print(f"❌ Failed to delete {audio_file}: {e}")
