// src/services/api.js

const API_URL = 'http://127.0.0.1:5000';  // Your Flask backend URL

export const liveTranscribe = async () => {
  try {
    const response = await fetch(`${API_URL}/api/live-transcribe`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error calling live-transcribe API:', error);
  }
};
