import React, { useState } from 'react';
import { sendAudioToBackend } from '../services/api';

function AudioRecorder({ setTranscription, setGptResponse }) {
  const [isRecording, setIsRecording] = useState(false);
  let mediaRecorder;
  let audioChunks = [];

  const startRecording = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.start();
    setIsRecording(true);

    mediaRecorder.ondataavailable = (event) => {
      audioChunks.push(event.data);
    };

    mediaRecorder.onstop = async () => {
      const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
      audioChunks = [];
      try {
        // Send audio to backend API
        const result = await sendAudioToBackend(audioBlob);
        setTranscription(result.transcription);
        setGptResponse(result.response);
      } catch (error) {
        console.error('Error in transcription:', error);
      }
    };
  };

  const stopRecording = () => {
    mediaRecorder.stop();
    setIsRecording(false);
  };

  return (
    <div>
      <button onClick={isRecording ? stopRecording : startRecording}>
        {isRecording ? 'Stop Recording' : 'Start Recording'}
      </button>
    </div>
  );
}

export default AudioRecorder;
