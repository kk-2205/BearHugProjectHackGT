// src/App.jsx
import React from 'react';
import Livechat from './components/Livechat';  // Import your LiveChat component
import './App.css';  // Import the App CSS file

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Live Conversation Assistant</h1>  {/* Add a header */}
      </header>
      {/* Use the LiveChat component in the main App component */}
      <Livechat />
    </div>
  );
}

export default App;
