import React from 'react';

function TranscriptDisplay({ transcription }) {
  return (
    <div className="transcript-display">
      <h2>Transcription</h2>
      <p>{transcription ? transcription : 'No transcription available.'}</p>
    </div>
  );
}

export default TranscriptDisplay;
