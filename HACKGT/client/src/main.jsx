// src/main.jsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';  // Import the App component
import './index.css';  // Import global styles (if you have index.css)

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />  {/* Render the App component */}
  </React.StrictMode>
);
