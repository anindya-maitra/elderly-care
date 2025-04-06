from pydub import AudioSegment

# Load your MP3 file
mp3_audio = AudioSegment.from_mp3("output.mp3")

# Export as WAV
mp3_audio.export("output.wav", format="wav")
