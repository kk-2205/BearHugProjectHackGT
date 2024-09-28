import React, { useState } from 'react';
import { liveTranscribe } from '../services/api';

const AudioRecorder = () => {
  const [transcription, setTranscription] = useState('');
  const [response, setResponse] = useState('');

  const handleTranscription = async () => {
    const result = await liveTranscribe();
    if (result && result.transcription) {
      setTranscription(result.transcription);
      setResponse(result.response);
    }
  };

  return (
    <div>
      <h2>Live Audio Transcription</h2>
      <button onClick={handleTranscription}>Start Live Transcription</button>

      {transcription && (
        <div>
          <h3>Transcription:</h3>
          <p>{transcription}</p>
        </div>
      )}

      {response && (
        <div>
          <h3>GPT Response:</h3>
          <p>{response}</p>
        </div>
      )}
    </div>
  );
};

export default AudioRecorder;
