import os
import logging
import threading
import openai
import whisper
import torch
import pyaudio
import numpy as np
from gtts import gTTS
import simpleaudio as sa
from pydub import AudioSegment
from pydub.utils import which
from flask import Flask, jsonify, request, render_template
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

# Ensure ffmpeg is in the path for pydub
AudioSegment.converter = which("ffmpeg")

# Set up logging
logging.basicConfig(level=logging.INFO)

# Set up OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

stop_flag = threading.Event()

app = Flask(__name__)

# Global lists to store transcriptions and GPT responses for the session
transcriptions = []
responses = []

def get_live_audio(seconds=10, rate=16000):
    """Capture live audio from the microphone."""
    chunk = 1024  # Record in chunks of 1024 samples
    format = pyaudio.paInt16  # 16-bit resolution
    channels = 1  # Mono channel
    audio_interface = pyaudio.PyAudio()

    stream = audio_interface.open(format=format, channels=channels,
                                  rate=rate, input=True,
                                  frames_per_buffer=chunk)

    logging.info("Recording...")
    frames = []

    for _ in range(0, int(rate / chunk * seconds)):
        data = stream.read(chunk)
        frames.append(np.frombuffer(data, dtype=np.int16))
        if stop_flag.is_set():
            break

    logging.info("Recording finished.")
    
    stream.stop_stream()
    stream.close()
    audio_interface.terminate()

    audio_data = np.hstack(frames)
    return audio_data.astype(np.float32) / 32768.0  # Normalize to -1 to 1

def transcribe_audio(model, audio):
    """Transcribe audio using Whisper model."""
    result = model.transcribe(audio)
    logging.info(f"Transcription result: {result['text']}")
    return result['text']

def query_chatgpt(prompt):
    """Send a prompt to the OpenAI GPT model and return the response."""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=150
    )
    return response['choices'][0]['message']['content'].strip()

def speak_text(text):
    """Convert text to speech and play it back using gTTS and simpleaudio."""
    try:
        tts = gTTS(text=text, lang='en')
        tts.save("response.mp3")
        sound = AudioSegment.from_mp3("response.mp3")
        sound.export("response.wav", format="wav")
        wave_obj = sa.WaveObject.from_wave_file("response.wav")
        play_obj = wave_obj.play()
        play_obj.wait_done()
        os.remove("response.mp3")
        os.remove("response.wav")
    except Exception as e:
        logging.error(f"Error in text-to-speech: {str(e)}")

running = False  # NEW: Added a running flag to control the overall state

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/start', methods=['POST'])
def start_transcription():
    """Start transcription loop."""
    global running
    running = True  # NEW: Set running to True when starting transcription
    transcriptions.clear()
    responses.clear()
    stop_flag.clear()
    threading.Thread(target=transcription_loop).start()
    return jsonify({'status': 'Transcription started'}), 200

@app.route('/api/stop', methods=['POST'])
def stop_transcription():
    """Stop transcription."""
    global running
    running = False  # NEW: Set running to False to ensure the loop stops completely
    stop_flag.set()
    return jsonify({'status': 'Transcription stopped'}), 200

@app.route('/api/updates', methods=['GET'])
def get_updates():
    """Fetch the latest transcriptions and GPT responses."""
    return jsonify({'transcriptions': transcriptions, 'responses': responses}), 200

def transcription_loop():
    """Continuously transcribe audio and respond until stop is called."""
    global running  # NEW: Use global running to control the state within the loop
    model = whisper.load_model("base")
    while not stop_flag.is_set() and running:
        try:
            # Capture live audio
            audio = get_live_audio(seconds=10)
            transcription = transcribe_audio(model, audio)
            gpt_response = query_chatgpt(transcription)
            
            # Append to global lists
            transcriptions.append(transcription)
            responses.append(gpt_response)

            # Convert GPT response to speech
            speak_text(gpt_response)

        except Exception as e:
            logging.error(f"Error during transcription: {e}")

if __name__ == '__main__':
    app.run(debug=True)