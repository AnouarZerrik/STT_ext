import sounddevice as sd
import soundfile as sf
import threading
import queue
import pyperclip
import pyautogui
import keyboard  # For global hotkeys
import os
import platform
from groq import Groq  # Import the Groq client
from pydub import AudioSegment  # For audio conversion

# Initialize the Groq client
client = Groq(api_key='YOUR_GROQ_API_KEY')  # Replace with your actual Groq API key

# Initialize global variables
q = queue.Queue()
recording = False
filename = 'output.wav'  # We record in WAV format
m4a_filename = 'output.m4a'  # Converted file

def callback(indata, frames, time, status):
    """This callback function is called for each audio block."""
    if status:
        print(status)
    q.put(indata.copy())

def record_audio(filename):
    """Records audio from the microphone and saves it to a file."""
    with sf.SoundFile(filename, mode='w', samplerate=44100, channels=1, subtype='PCM_16') as file:
        with sd.InputStream(samplerate=44100, channels=1, callback=callback):
            while recording:
                file.write(q.get())

def start_recording():
    """Starts the audio recording in a separate thread."""
    global recording
    if not recording:
        recording = True
        threading.Thread(target=record_audio_thread).start()
        print("Recording started... Press 'Ctrl+Alt+R' to stop.")

def stop_recording():
    """Stops the audio recording."""
    global recording
    if recording:
        recording = False
        print("Recording stopped. Transcribing...")

def toggle_recording():
    """Starts or stops recording when the hotkey is pressed."""
    if not recording:
        start_recording()
    else:
        stop_recording()

def record_audio_thread():
    """Handles the recording and transcription process."""
    if os.path.exists(filename):
        os.remove(filename)
    if os.path.exists(m4a_filename):
        os.remove(m4a_filename)
    record_audio(filename)
    convert_wav_to_m4a(filename, m4a_filename)
    transcription = transcribe_audio(m4a_filename)
    insert_text(transcription)
    print("Transcription complete.")

def convert_wav_to_m4a(wav_filename, m4a_filename):
    """Converts a WAV file to M4A format."""
    audio = AudioSegment.from_wav(wav_filename)
    audio.export(m4a_filename, format='mp4')  # Export as M4A

def transcribe_audio(filename):
    """Transcribes the recorded audio using the Groq API."""
    with open(filename, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=(filename, file.read()),  # Required audio file
            model="distil-whisper-large-v3-en",  # Required model to use for transcription
            prompt="",  # Optional
            response_format="json",  # Optional
            language="en",  # Optional
            temperature=0.0  # Optional
        )
    return transcription.text

def insert_text(text):
    """Inserts the transcribed text into the selected field."""
    pyperclip.copy(text)
    system = platform.system()
    if system == 'Windows':
        pyautogui.hotkey('ctrl', 'v')
    elif system == 'Darwin':  # macOS
        pyautogui.hotkey('command', 'v')
    else:
        pyautogui.hotkey('ctrl', 'v')

# Set the global hotkey (Ctrl+Alt+R) to toggle recording
keyboard.add_hotkey('ctrl+alt+r', toggle_recording)

# Keep the script running
print("Voice-to-Text service is running. Press Ctrl+Alt+R to start/stop recording.")
keyboard.wait()  # This will keep the script running




