import speech_recognition as sr
import subprocess


def get_length(filename):
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                             "format=duration", "-of",
                             "default=noprint_wrappers=1:nokey=1", filename],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    return float(result.stdout)


FILE_NAME = "Time Turning What-Ifs - Majoras Mask  - Part 64"
old_extension = ".mp3"
new_extension = ".wav"
source_audio_file_path = "E:\\Testing Shit\\" + FILE_NAME + old_extension
dest_audio_file_path = "E:\\Testing Shit\\" + FILE_NAME + new_extension

# Convert audio file to wav because Google Speech to Text doesn't do mp3
result = subprocess.run(["ffmpeg", "-i", source_audio_file_path, dest_audio_file_path])

# initialize the recognizer
r = sr.Recognizer()

with sr.AudioFile(dest_audio_file_path) as source:
    # listen for the data (load the audio to memory)
    audio_data = r.record(source)
    # recognize (convert from speech to text)
    text = r.recognize_google(audio_data)
    with open("Time Turning What-Ifs - Majoras Mask  - Part 64.txt", 'w') as file:
        file.write(text)
