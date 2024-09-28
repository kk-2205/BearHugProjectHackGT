import os
from dotenv import load_dotenv
import logging
import openai
import whisper
import torch
from flask import Flask, request, jsonify
from flask_cors import CORS

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

@app.route('/api/transcribe', methods=['POST'])
def transcribe():
    try:
        # Get audio file from the request
        audio_file = request.files['file']
        audio_path = os.path.join('temp', audio_file.filename)
        audio_file.save(audio_path)

        # Transcribe audio
        result = model.transcribe(audio_path)
        transcription = result['text']

        # Send transcription to OpenAI GPT
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Or another available model
            messages=[{"role": "user", "content": transcription}],
            max_tokens=150
        )
        gpt_response = response['choices'][0]['message']['content'].strip()

        # Clean up temporary audio file
        os.remove(audio_path)

        return jsonify({
            'transcription': transcription,
            'response': gpt_response
        })

    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    if not os.path.exists('temp'):
        os.makedirs('temp')
    app.run(debug=True)
