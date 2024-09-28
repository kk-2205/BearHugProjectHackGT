import React, { useState } from 'react';
import AudioRecorder from './components/AudioRecorder';
import TranscriptDisplay from './components/TranscriptDisplay';
import SuggestionsDisplay from './components/SuggestionsDisplay';

function App() {
  const [transcription, setTranscription] = useState('');
  const [gptResponse, setGptResponse] = useState('');

  return (
    <div className="App">
      <h1>WINGBOT AI Conversation Helper</h1>
      <AudioRecorder setTranscription={setTranscription} setGptResponse={setGptResponse} />
      <TranscriptDisplay transcription={transcription} />
      <SuggestionsDisplay response={gptResponse} />
    </div>
  );
}

export default App;
