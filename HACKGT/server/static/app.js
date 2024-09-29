let intervalId; // Store the interval ID for polling updates

// Function to Start Transcription
function startTranscription() {
    fetch('/api/start', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            console.log("Chat started:", data);
            intervalId = setInterval(fetchUpdates, 3000);  // Poll for updates every 3 seconds
            document.getElementById("status").innerText = "Chat started...";
        })
        .catch(error => console.error("Error starting transcription:", error));
}

// Function to Stop Transcription
function stopTranscription() {
    fetch('/api/stop', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            console.log("Chat stopped:", data);
            clearInterval(intervalId);  // Stop polling for updates
            document.getElementById("status").innerText = "Chat stopped.";
        })
        .catch(error => console.error("Error stopping transcription:", error));
}

// Function to Fetch and Display Updates in the Chat Container
function fetchUpdates() {
    fetch('/api/updates')
        .then(response => response.json())
        .then(data => {
            const conversation = document.getElementById('conversation');
            conversation.innerHTML = '';  // Clear previous messages
            data.transcriptions.forEach((msg, i) => {
                conversation.innerHTML += `<p class="user" style="color: blue;">You: ${msg}</p>`;
                conversation.innerHTML += `<p class="bot" style="color: green;">Bot: ${data.responses[i]}</p>`;
            });
            conversation.scrollTop = conversation.scrollHeight;  // Auto-scroll to the latest message
        })
        .catch(error => console.error("Error fetching updates:", error));
}
