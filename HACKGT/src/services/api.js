// src/services/api.js

export async function sendAudioToBackend(audioBlob) {
    const formData = new FormData();
    formData.append('file', audioBlob, 'audio.wav');
  
    const response = await fetch('http://localhost:5000/api/transcribe', {
      method: 'POST',
      body: formData,
    });
  
    if (!response.ok) {
      throw new Error(`Server error: ${response.status}`);
    }
  
    return response.json(); // Returns the transcription and GPT response
  }
  