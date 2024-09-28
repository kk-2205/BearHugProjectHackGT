import React from 'react';

function SuggestionsDisplay({ response }) {
  return (
    <div className="suggestions-display">
      <h2>WINGBOT Response</h2>
      <p>{response ? response : 'No response available.'}</p>
    </div>
  );
}

export default SuggestionsDisplay;
