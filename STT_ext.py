# import sounddevice as sd
# import soundfile as sf
# import threading
# import queue
# import pyperclip
# import pyautogui
# import keyboard  # For global hotkeys
# import os
# import platform
# from groq import Groq  # Import the Groq client
# from pydub import AudioSegment  # For audio conversion
# import customtkinter as ctk  # Modern GUI library

# # Initialize the Groq client
# client = Groq(api_key='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')  # Replace with your actual Groq API key

# # Initialize global variables
# q = queue.Queue()
# recording = False
# filename = 'output.wav'  # We record in WAV format
# m4a_filename = 'output.m4a'  # Converted file

# def callback(indata, frames, time, status):
#     """This callback function is called for each audio block."""
#     if status:
#         print(status)
#     q.put(indata.copy())

# def record_audio(filename):
#     """Records audio from the microphone and saves it to a file."""
#     with sf.SoundFile(filename, mode='w', samplerate=44100, channels=1, subtype='PCM_16') as file:
#         with sd.InputStream(samplerate=44100, channels=1, callback=callback):
#             while recording:
#                 file.write(q.get())


# def show_window():
#     """Displays the window on top without stealing focus."""
#     root.deiconify()
#     root.lift()
#     root.attributes('-topmost', True)
#     # Don't force focus to the window
#     root.after(100, lambda: root.attributes('-topmost', False))  # Allow other windows to take focus


# def start_recording():
#     """Starts the audio recording in a separate thread."""
#     global recording
#     recording = True
#     show_window()
#     stop_button.configure(state=ctk.NORMAL)
#     status_label.configure(text="Recording... Press 'Enter' to Stop", text_color="red")
#     threading.Thread(target=record_audio_thread).start()
#     # Add hotkey for 'Enter' key to stop recording
#     keyboard.add_hotkey('enter', on_enter_key)

# def stop_recording():
#     """Stops the audio recording."""
#     global recording
#     recording = False
#     stop_button.configure(state=ctk.DISABLED)
#     status_label.configure(text="Transcribing...", text_color="orange")
#     # Remove the 'Enter' key hotkey
#     keyboard.remove_hotkey('enter')

# def on_enter_key():
#     """Callback function when 'Enter' key is pressed."""
#     if recording:
#         stop_recording()

# def record_audio_thread():
#     """Handles the recording and transcription process."""
#     if os.path.exists(filename):
#         os.remove(filename)
#     if os.path.exists(m4a_filename):
#         os.remove(m4a_filename)
#     record_audio(filename)
#     convert_wav_to_m4a(filename, m4a_filename)
#     transcription = transcribe_audio(m4a_filename)
#     insert_text(transcription)
#     status_label.configure(text="Transcription Complete", text_color="green")
#     root.after(2000, lambda: root.withdraw())  # Hide the window after 2 seconds

# def convert_wav_to_m4a(wav_filename, m4a_filename):
#     """Converts a WAV file to M4A format."""
#     audio = AudioSegment.from_wav(wav_filename)
#     audio.export(m4a_filename, format='mp4')  # Export as M4A

# def transcribe_audio(filename):
#     """Transcribes the recorded audio using the Groq API."""
#     with open(filename, "rb") as file:
#         transcription = client.audio.transcriptions.create(
#             file=(filename, file.read()),  # Required audio file
#             model="distil-whisper-large-v3-en",  # Required model to use for transcription
#             prompt="",  # Optional
#             response_format="json",  # Optional
#             language="en",  # Optional
#             temperature=0.0  # Optional
#         )
#     return transcription.text

# def insert_text(text):
#     """Inserts the transcribed text into the selected field."""
#     pyperclip.copy(text)
#     system = platform.system()
#     if system == 'Windows':
#         pyautogui.hotkey('ctrl', 'v')
#     elif system == 'Darwin':  # macOS
#         pyautogui.hotkey('command', 'v')
#     else:  # Linux or other
#         pyautogui.hotkey('ctrl', 'v')

# def on_hotkey():
#     """Starts recording when the hotkey is pressed."""
#     root.deiconify()
#     root.lift()
#     start_recording()

# # Setup the GUI application with customtkinter
# ctk.set_appearance_mode("System")  # Modes: "System" (default), "Dark", "Light"
# ctk.set_default_color_theme("blue")  # Themes: "blue" (default), "green", "dark-blue"

# root = ctk.CTk()
# root.title("Audio Transcriber")
# root.geometry("400x200")
# root.resizable(False, False)
# root.withdraw()  # Start minimized

# # Create a frame for the content
# frame = ctk.CTkFrame(root)
# frame.pack(pady=20, padx=20, fill="both", expand=True)

# status_label = ctk.CTkLabel(frame, text="Press 'Ctrl+Alt+R' to Start Recording", font=("Arial", 14))
# status_label.pack(pady=10)

# stop_button = ctk.CTkButton(frame, text="Stop Recording", command=stop_recording, state=ctk.DISABLED)
# stop_button.pack(pady=10)

# # Set the global hotkey (Ctrl+Alt+R) to start recording
# keyboard.add_hotkey('ctrl+alt+r', on_hotkey)

# # Run the application
# root.mainloop()


import asyncio
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
import customtkinter as ctk  # Modern GUI library
from tkinter import messagebox
import io
import time

# Initialize the Groq client securely using environment variables
client = Groq(api_key="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")  # Ensure you set GROQ_API_KEY in your environment

# Initialize global variables
q = queue.Queue()
recording = False
filename = 'output.wav'  # We record in WAV format
m4a_filename = 'output.m4a'  # Converted file

# Define the sample rate and channels
SAMPLE_RATE = 44100
CHANNELS = 1

def callback(indata, frames, time_info, status):
    """This callback function is called for each audio block."""
    if status:
        print(status)
    q.put(indata.copy())

def record_audio(filename):
    """Records audio from the microphone and saves it to a file."""
    with sf.SoundFile(filename, mode='w', samplerate=SAMPLE_RATE, channels=CHANNELS, subtype='PCM_16') as file:
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, callback=callback):
            while recording:
                file.write(q.get())

def show_window():
    """Displays the window on top with a fade-in animation."""
    root.deiconify()
    root.lift()
    root.attributes('-topmost', True)
    for i in range(0, 101, 10):
        root.attributes('-alpha', i/100)
        root.update()
        time.sleep(0.02)
    root.attributes('-topmost', False)

def hide_window():
    """Hides the window with a fade-out animation."""
    for i in range(100, -1, -10):
        root.attributes('-alpha', i/100)
        root.update()
        time.sleep(0.02)
    root.withdraw()

def start_recording():
    """Starts the audio recording in a separate thread."""
    global recording
    if not recording:
        recording = True
        show_window()
        stop_button.configure(state=ctk.NORMAL)
        status_label.configure(text="Recording... Press 'Enter' to Stop", text_color="#FF5555")
        update_progress("recording")
        threading.Thread(target=lambda: asyncio.run(record_audio_thread()), daemon=True).start()
        # Add hotkey for 'Enter' key to stop recording
        keyboard.add_hotkey('enter', on_enter_key)

def stop_recording():
    """Stops the audio recording."""
    global recording
    if recording:
        recording = False
        stop_button.configure(state=ctk.DISABLED)
        status_label.configure(text="Transcribing...", text_color="#FFA500")
        update_progress("transcribing")
        # Remove the 'Enter' key hotkey
        keyboard.remove_hotkey('enter')

def on_enter_key():
    """Callback function when 'Enter' key is pressed."""
    stop_recording()

async def record_audio_thread():
    """Handles the recording and transcription process asynchronously."""
    try:
        # Cleanup existing files if any
        if os.path.exists(filename):
            os.remove(filename)
        if os.path.exists(m4a_filename):
            os.remove(m4a_filename)

        # Start recording
        record_audio(filename)

        # Convert WAV to M4A and transcribe in executor to prevent blocking
        transcription_text = await asyncio.get_event_loop().run_in_executor(None, convert_and_transcribe, filename)

        # Insert transcribed text
        insert_text(transcription_text)
        status_label.configure(text="Transcription Complete", text_color="#00FF00")
        update_progress("complete")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
        status_label.configure(text="Error Occurred", text_color="#FF0000")
        update_progress("error")
    finally:
        # Cleanup temporary files
        if os.path.exists(filename):
            os.remove(filename)
        if os.path.exists(m4a_filename):
            os.remove(m4a_filename)
        # Hide the window after a short delay
        root.after(3000, hide_window)

def convert_and_transcribe(wav_filename):
    """Converts WAV to M4A and transcribes the audio."""
    # Convert WAV to M4A
    audio = AudioSegment.from_wav(wav_filename)
    audio.export(m4a_filename, format='mp4')  # Export as M4A

    # Transcribe audio
    transcription = transcribe_audio(m4a_filename)
    return transcription

def transcribe_audio(filename):
    """Transcribes the recorded audio using the Groq API."""
    with open(filename, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=(filename, file.read()),
            model="distil-whisper-large-v3-en",
            prompt="",
            response_format="json",
            language="en",
            temperature=0.0
        )
    return transcription.text

def insert_text(text):
    """Copies the transcribed text to the clipboard and provides user feedback."""
    # Copy to clipboard
    pyperclip.copy(text)

    # Provide visual feedback that the text has been copied
    copy_status_label.configure(text="Text copied to clipboard!", text_color="#4CAF50")
    root.after(3000, lambda: copy_status_label.configure(text=""))

def update_progress(status):
    """Updates the progress bar based on the current status."""
    if status == "transcribing":
        progress_bar.start()
    elif status == "complete" or status == "error":
        progress_bar.stop()
    elif status == "recording":
        progress_bar.stop()

def on_hotkey():
    """Starts recording when the hotkey is pressed."""
    start_recording()

# Setup the GUI application with customtkinter
ctk.set_appearance_mode("Dark")  # Modes: "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue", "green", "dark-blue"

root = ctk.CTk()
root.title("Audio Transcriber")
root.geometry("600x300")
root.resizable(False, False)
root.attributes('-alpha', 0.0)  # Start fully transparent
root.withdraw()  # Hide initially

# Create a frame for the content with padding
frame = ctk.CTkFrame(root, corner_radius=10)
frame.pack(pady=20, padx=20, fill="both", expand=True)

# Application Title
title_label = ctk.CTkLabel(
    frame,
    text="Audio Transcriber",
    font=("Helvetica", 24, "bold"),
    text_color="white"
)
title_label.pack(pady=(0, 20))

# Status Label with dynamic text
status_label = ctk.CTkLabel(
    frame,
    text="Press 'Ctrl+Alt+R' to Start Recording",
    font=("Arial", 16),
    text_color="lightgray"
)
status_label.pack(pady=(0, 10))

# Stop Recording Button with hover effect
stop_button = ctk.CTkButton(
    frame,
    text="Stop Recording",
    command=stop_recording,
    state=ctk.DISABLED,
    fg_color="#FF5555",
    hover_color="#FF3030",
    text_color="white",
    width=150,
    height=40
)
stop_button.pack(pady=(0, 20))

# Add a progress bar for transcription status
progress_bar = ctk.CTkProgressBar(
    frame,
    mode="indeterminate"
)
progress_bar.pack(pady=(0, 20), fill="x", padx=20)
progress_bar.set(0)
progress_bar.stop()

# Copy Status Label (for feedback)
copy_status_label = ctk.CTkLabel(
    frame,
    text="",
    font=("Arial", 12),
    text_color="#4CAF50"
)
copy_status_label.pack(pady=(0, 10))

# Set the global hotkey (Ctrl+Alt+R) to start recording
keyboard.add_hotkey('ctrl+alt+r', on_hotkey)

# Run the application
root.mainloop()