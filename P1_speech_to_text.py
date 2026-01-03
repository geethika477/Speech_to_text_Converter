!pip install SpeechRecognition
!pip install pyaudio
import tkinter as tk
from tkinter import filedialog, messagebox
import speech_recognition as sr
import threading
import pyaudio
import wave
import os

recognizer = sr.Recognizer()
recording = False
audio_filename = "temp_audio.wav"

def choose_file():
    filepath = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
    if filepath:
        entry_var.set(filepath)

def convert_audio_file():
    audio_file = entry_var.get()
    if not audio_file:
        messagebox.showwarning("No file selected", "Please choose an audio file.")
        return

    try:
        with sr.AudioFile(audio_file) as source:
            audio = recognizer.record(source)
        text = recognizer.recognize_google(audio)
        show_result(text)
    except sr.UnknownValueError:
        messagebox.showerror("Error", "Could not understand the audio.")
    except sr.RequestError:
        messagebox.showerror("Error", "Request to Google failed.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def show_result(text):
    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, text)

def export_text():
    text = output_text.get("1.0", tk.END).strip()
    if text:
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(text)
            messagebox.showinfo("Success", "Text exported successfully.")
    else:
        messagebox.showwarning("No text", "There's no text to export.")

def start_recording():
    global recording, audio_thread
    recording = True
    start_button.config(state=tk.DISABLED)
    stop_button.config(state=tk.NORMAL)
    audio_thread = threading.Thread(target=record_microphone)
    audio_thread.start()

def stop_recording():
    global recording
    recording = False
    stop_button.config(state=tk.DISABLED)
    start_button.config(state=tk.NORMAL)
    audio_thread.join()
    process_recorded_audio()

def record_microphone():
    chunk = 1024
    format = pyaudio.paInt16
    channels = 1
    rate = 44100

    p = pyaudio.PyAudio()
    stream = p.open(format=format,
                    channels=channels,
                    rate=rate,
                    input=True,
                    frames_per_buffer=chunk)

    frames = []
    while recording:
        data = stream.read(chunk)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(audio_filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(format))
    wf.setframerate(rate)
    wf.writeframes(b''.join(frames))
    wf.close()

def process_recorded_audio():
    try:
        with sr.AudioFile(audio_filename) as source:
            audio = recognizer.record(source)
        text = recognizer.recognize_google(audio)
        show_result(text)
    except sr.UnknownValueError:
        messagebox.showerror("Error", "Could not understand your voice.")
    except sr.RequestError:
        messagebox.showerror("Error", "Could not connect to Google.")
    except Exception as e:
        messagebox.showerror("Error", str(e))
    finally:
        if os.path.exists(audio_filename):
            os.remove(audio_filename)

# GUI Setup
root = tk.Tk()
root.title("Speech to Text Assistant")

entry_var = tk.StringVar()

tk.Label(root, text="Choose WAV File:").pack(pady=5)
tk.Entry(root, textvariable=entry_var, width=40).pack(pady=5)
tk.Button(root, text="Browse", command=choose_file).pack(pady=5)
tk.Button(root, text="Convert File to Text", command=convert_audio_file).pack(pady=5)

tk.Label(root, text="Or").pack(pady=50)

start_button = tk.Button(root, text="Start Recording", command=start_recording, bg="lightgreen")
start_button.pack(pady=5)

stop_button = tk.Button(root, text="Stop Recording", command=stop_recording, bg="lightcoral", state=tk.DISABLED)
stop_button.pack(pady=5)

output_text = tk.Text(root, height=10, width=60)
output_text.pack(pady=10)

tk.Button(root, text="Export Text", command=export_text).pack(pady=5)

root.mainloop()
