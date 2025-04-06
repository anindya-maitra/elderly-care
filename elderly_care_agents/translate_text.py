from deep_translator import GoogleTranslator
from agents.voice_output import speak

def translate_and_speak(text, source_language, target_language):
    translated_text = GoogleTranslator(source=source_language, target=target_language).translate(text)
    print(f"Translated Text: {translated_text}")
    speak(translated_text)
