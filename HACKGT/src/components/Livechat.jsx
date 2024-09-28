// src/components/LiveChat.jsx
import React, { useState, useEffect } from 'react';
import './LiveChat.css';

const LiveChat = () => {
  const [transcriptions, setTranscriptions] = useState([]);  // Store transcription texts
  const [gptResponses, setGptResponses] = useState([]);      // Store GPT responses
  const [isRecording, setIsRecording] = useState(false);     // Check if recording is active
  const [error, setError] = useState(null);                  // To store any errors
  
  // Start live transcription
  const startLiveTranscription = async () => {
    setIsRecording(true);
    setError(null);  // Reset any previous error
    try {
      const response = await fetch('http://127.0.0.1:5000/api/start-transcription', {
        method: 'POST',
      });
      if (response.ok) {
        console.log('Live transcription started!');
      } else {
        throw new Error('Failed to start transcription');
      }
    } catch (err) {
      setError('Failed to start live transcription.');
      console.error('Failed to start live transcription:', err);
    }
  };

  // Stop live transcription
  const stopLiveTranscription = async () => {
    setIsRecording(false);
    setError(null);  // Reset any previous error
    try {
      const response = await fetch('http://127.0.0.1:5000/api/stop-transcription', {
        method: 'POST',
      });
      if (response.ok) {
        console.log('Live transcription stopped!');
      } else {
        throw new Error('Failed to stop transcription');
      }
    } catch (err) {
      setError('Failed to stop live transcription.');
      console.error('Failed to stop live transcription:', err);
    }
  };

  // Continuously get live updates for the transcriptions and responses
  useEffect(() => {
    if (isRecording) {
      const interval = setInterval(async () => {
        try {
          const response = await fetch('http://127.0.0.1:5000/api/get-updates');
          if (response.ok) {
            const data = await response.json();
            setTranscriptions(data.transcriptions);
            setGptResponses(data.responses);
          } else {
            throw new Error('Failed to fetch updates');
          }
        } catch (err) {
          setError('Error fetching live updates.');
          console.error('Error fetching live updates:', err);
        }
      }, 2000); // Poll every 2 seconds

      // Cleanup the interval when component unmounts or recording stops
      return () => clearInterval(interval);
    }
  }, [isRecording]);

  return (
    <div className="live-chat-container">
      <h2>Live Chat</h2>

      {error && <div className="error">{error}</div>} {/* Show error message if any */}

      <div className="chat-box">
        {/* Show transcription and response pairs */}
        {transcriptions.map((text, index) => (
          <div key={index} className="user-message">
            <strong>User:</strong> {text}
          </div>
        ))}
        {gptResponses.map((response, index) => (
          <div key={index} className="gpt-response">
            <strong>Assistant:</strong> {response}
          </div>
        ))}

        {/* Optional message if no data available */}
        {!isRecording && transcriptions.length === 0 && (
          <div className="no-data">Press "Start Conversation" to begin...</div>
        )}
      </div>

      <div className="control-buttons">
        <button onClick={startLiveTranscription} disabled={isRecording}>
          Start Conversation
        </button>
        <button onClick={stopLiveTranscription} disabled={!isRecording}>
          Stop Conversation
        </button>
      </div>
    </div>
  );
};

export default LiveChat;
