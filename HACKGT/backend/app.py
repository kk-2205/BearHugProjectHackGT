from dotenv import load_dotenv
import openai
import whisper
import torch
import warnings
import logging
import pyaudio
import numpy as np
import os
from gtts import gTTS
import simpleaudio as sa
from pydub import AudioSegment
from pydub.utils import which
import threading

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

# Ensure ffmpeg is in the ppipath for pydub
AudioSegment.converter = which("ffmpeg")


# Set up logging
logging.basicConfig(level=logging.INFO)

# Set up OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

stop_flag = threading.Event()


# Initialize the system prompt to guide the conversation
SYSTEM_PROMPT = {
    "role": "system",
    "content": "You are a helpful assistant. Respond to the user with empathy and understanding, offering support and advice where appropriate."
}

# Maintain a conversation history to ensure context
conversation_history = [SYSTEM_PROMPT]

def get_live_audio(seconds=30, rate=16000):
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
    audio_tensor = torch.tensor(audio).unsqueeze(0)
    mel = whisper.log_mel_spectrogram(audio_tensor)
    input_tensor = mel.unsqueeze(0).squeeze(1).permute(0, 2, 1)
    logging.info(f"Input tensor shape: {input_tensor.shape}")

    if not torch.cuda.is_available() or not torch.cuda.is_bf16_supported():
        warnings.warn("FP16 is not supported on CPU; using FP32 instead")

    result = model.transcribe(audio)
    logging.info(f"Transcription result: {result['text']}")
    return result['text']

def query_chatgpt(prompt):
    """Send a prompt to the OpenAI GPT model and return the response."""
    # [MODIFIED] Append the user input to the conversation history
    conversation_history.append({"role": "user", "content": prompt})  # [ADDED]

     # [MODIFIED] Send the entire conversation history (including system prompt) to OpenAI
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Use "gpt-3.5-turbo" or "gpt-4" if available
        messages=conversation_history,  # [MODIFIED] Use conversation history
        max_tokens=150
    )
    # [ADDED] Extract the assistant's response and add it to the conversation history
    gpt_response = response['choices'][0]['message']['content'].strip()
    conversation_history.append({"role": "assistant", "content": gpt_response})  # [ADDED]

    return gpt_response

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

def listen_for_stop():
    """Listen for the stop signal (press Enter to stop)."""
    input("Press Enter to stop...\n")
    stop_flag.set()

def main():
    model = whisper.load_model("base")
    while not stop_flag.is_set():
        try:
            # Capture live audio
            audio = get_live_audio(seconds=5)  # Adjust duration as needed
            
            if stop_flag.is_set():
                break

            # Transcribe audio to text
            transcription = transcribe_audio(model, audio)

             # [MODIFIED] Send transcription to OpenAI GPT using the updated `query_chatgpt` function
            response = query_chatgpt(transcription)

            # Convert GPT response to speech
            logging.info(f"GPT-3 response: {response}")
            speak_text(response)

        except Exception as e:
            logging.error(f"Error in callback: {str(e)}")

if __name__ == "__main__":
    stop_thread = threading.Thread(target=listen_for_stop)
    stop_thread.start()
    main()
    stop_thread.join()
    logging.info("Conversation stopped.")