// src/services/api.js
const API_URL = '/api';  // Now proxying to Flask backend

export const liveTranscribe = async () => {
  try {
    const response = await fetch(`${API_URL}/get-updates`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error calling get-updates API:', error);
  }
};
