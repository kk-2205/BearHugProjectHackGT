import os
from dotenv import load_dotenv
import logging
import numpy as np
import openai
import whisper
import torch
import pyaudio
from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import tempfile
import soundfile as sf

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS to allow communication with frontend

# Set up logging
logging.basicConfig(level=logging.INFO)

# Set up OpenAI API key from environment variable
openai.api_key = os.getenv('OPENAI_API_KEY')
print("OpenAI API Key:", openai.api_key)


# Load Whisper model
model = whisper.load_model("base")

# Create a flag to stop the live recording if needed
stop_flag = threading.Event()

# Define a system prompt to guide the behavior of the model
SYSTEM_PROMPT = {
    "role": "system",
    "content": "The following contains snippets between a conversation between two friends. Respond appropriately and with empathy to each snippet, making sure to change up the response every scenario to keep the conversation going."
}

# Initialize conversation history with the system prompt
conversation_history = [SYSTEM_PROMPT]


def get_live_audio(seconds=10, rate=16000):
    """Capture live audio from the microphone."""
    chunk = 2048  # Record in chunks of 2048 samples (increase buffer size)
    format = pyaudio.paInt16  # 16-bit resolution
    channels = 1  # Mono channel
    audio_interface = pyaudio.PyAudio()

    stream = audio_interface.open(format=format, channels=channels,
                                  rate=rate, input=True,
                                  frames_per_buffer=chunk)

    logging.info("Recording...")
    frames = []

    try:
        # Capture the audio frames for the specified duration
        for _ in range(0, int(rate / chunk * seconds)):
            try:
                data = stream.read(chunk, exception_on_overflow=False)
                frames.append(np.frombuffer(data, dtype=np.int16))
                if stop_flag.is_set():
                    break
            except IOError as e:
                logging.warning(f"Audio buffer overflowed: {e}")
                continue

    finally:
        logging.info("Recording finished.")
        stream.stop_stream()
        stream.close()
        audio_interface.terminate()

    # Convert audio data to a numpy array and normalize it
    audio_data = np.hstack(frames)
    return audio_data.astype(np.float32) / 32768.0  # Normalize to -1 to 1


@app.route('/api/live-transcribe', methods=['GET'])
def live_transcribe():
    """Transcribe live audio from the microphone and return OpenAI response."""
    try:
        # Record live audio for a specified duration (e.g., 10 seconds)
        logging.info("Starting live audio recording...")
        audio_data = get_live_audio(seconds=10)

        
        # Save audio data to a temporary file for Whisper to read
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        sf.write(temp_file.name, audio_data, 16000)

       # Use Whisper to transcribe the saved temporary file
        result = model.transcribe(temp_file.name)
        transcription = result['text']
        logging.info(f"Transcription: {transcription}")

        # Add the transcription to the conversation history
        conversation_history.append({"role": "user", "content": transcription})

        # Send the conversation history to OpenAI GPT for further processing
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Use "gpt-3.5-turbo" or "gpt-4" if available
            messages=conversation_history,
            max_tokens=150
        )

        gpt_response = response['choices'][0]['message']['content'].strip()
        logging.info(f"GPT Response: {gpt_response}")

        # Add the GPT response to the conversation history
        conversation_history.append({"role": "assistant", "content": gpt_response})


        return jsonify({
            'transcription': transcription,
            'response': gpt_response
        })

    except Exception as e:
        logging.error(f"Error processing live transcription: {str(e)}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)

