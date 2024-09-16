let mediaRecorder;
let audioChunks = [];
const recordBtn = document.getElementById('recordBtn');
const stopBtn = document.getElementById('stopBtn');
const audioPlayback = document.getElementById('audioPlayback');
const transcript = document.getElementById('transcript');
const fileInput = document.getElementById('fileInput');
const uploadBtn = document.getElementById('uploadBtn');

// Start recording when the record button is clicked
recordBtn.addEventListener('click', async () => {
    try {
        // Request permission to access the microphone
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

        // Create a new MediaRecorder instance with the audio stream
        mediaRecorder = new MediaRecorder(stream);

        // Event listener that triggers when there is data available
        mediaRecorder.ondataavailable = event => {
            // Push audio chunks into the array
            audioChunks.push(event.data);
        };

        // Event listener that triggers when the recording is stopped
        mediaRecorder.onstop = async () => {
            console.log("Recording stopped, processing audio...");

            // Combine the audio chunks into a single Blob
            const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
            console.log("Audio blob size:", audioBlob.size, "bytes");
            audioChunks = []; // Clear the audioChunks array for the next recording

            // Create a URL for the audio and set it as the source for the audio playback
            const audioUrl = URL.createObjectURL(audioBlob);
            audioPlayback.src = audioUrl;
            audioPlayback.style.display = 'block';

            // Send the audio Blob to the backend for transcription
            const formData = new FormData();
            formData.append('audio', audioBlob, 'recording.webm');

            try {
                const response = await fetch('/upload', {
                    method: 'POST',
                    body: formData
                });

                if (response.ok) {
                    const result = await response.json();
                    console.log("Received transcript:", result.transcript);
                    transcript.textContent = result.transcript;
                } else {
                    console.error("Failed to process audio:", response.statusText);
                    transcript.textContent = "Error: Failed to process audio";
                }
            } catch (error) {
                console.error("Error during fetch:", error);
                transcript.textContent = "Error: Failed to send audio to server";
            }
        };

        // Start recording
        mediaRecorder.start();
        recordBtn.disabled = true;
        stopBtn.disabled = false;
    } catch (error) {
        console.error("Error starting recording:", error);
        alert("Failed to start recording. Please make sure you have given permission to use the microphone.");
    }
});

// Stop recording when the stop button is clicked
stopBtn.addEventListener('click', () => {
    if (mediaRecorder && mediaRecorder.state !== "inactive") {
        mediaRecorder.stop();
        recordBtn.disabled = false;
        stopBtn.disabled = true;
    }
});

// Handle file upload
uploadBtn.addEventListener('click', async () => {
    const file = fileInput.files[0];
    if (!file) {
        alert('Please select a file to upload');
        return;
    }

    const formData = new FormData();
    formData.append('audio', file);

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const result = await response.json();
            console.log("Received transcript:", result.transcript);
            transcript.textContent = result.transcript;
        } else {
            console.error("Failed to process audio:", response.statusText);
            transcript.textContent = "Error: Failed to process audio";
        }
    } catch (error) {
        console.error("Error during fetch:", error);
        transcript.textContent = "Error: Failed to send audio to server";
    }
});

// AI Assistant functionality
const sendBtn = document.getElementById('sendBtn');
const userInput = document.getElementById('userInput');
const messages = document.getElementById('messages');

// Function to add a message to the chat
function addMessage(content, isUser = false) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message');
    messageDiv.classList.add(isUser ? 'user-message' : 'bot-message');
    messageDiv.textContent = content;
    messages.appendChild(messageDiv);
    messages.scrollTop = messages.scrollHeight;
}

// Function to handle sending messages
sendBtn.addEventListener('click', () => {
    const question = userInput.value.trim();
    if (question) {
        addMessage(question, true);
        userInput.value = '';

        // Simulate a response (replace this with actual RAG logic)
        setTimeout(() => {
            const response = getResponse(question);
            addMessage(response);
        }, 1000);
    }
});

// Allow sending messages with Enter key
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendBtn.click();
    }
});

// Simulated response function (replace with actual RAG implementation)
function getResponse(question) {
    // Here you would implement your RAG logic to generate a response based on the transcript
    return "This is a simulated response based on your question: " + question;
}

// Add an initial bot message
addMessage("Hello! How can I assist you today?");

// Remove the following lines as they are no longer needed:
// - minimizeBtn event listener
// - window resize event listener
// - Initial body padding adjustment