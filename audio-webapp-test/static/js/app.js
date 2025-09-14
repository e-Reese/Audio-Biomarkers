document.addEventListener('DOMContentLoaded', function() {
    'use strict';

    // DOM Elements
    const recordButton = document.getElementById('recordButton');
    const audioPlayback = document.getElementById('audioPlayback');
    const audioContainer = document.getElementById('audioContainer');
    const sendButton = document.getElementById('sendButton');
    const loadingContainer = document.getElementById('loadingContainer');
    const resultContainer = document.getElementById('resultContainer');
    const resultText = document.getElementById('resultText');
    const timerElement = document.getElementById('timer');

    // Audio recording variables
    let audioContext;
    let recorder;
    let audioStream;
    let audioBlob;
    let timerInterval;
    let recordingSeconds = 0;

    // Initialize audio context
    function initAudio() {
        try {
            window.AudioContext = window.AudioContext || window.webkitAudioContext;
            audioContext = new AudioContext();
            return true;
        } catch (e) {
            alert('Web Audio API is not supported in this browser');
            return false;
        }
    }

    // Request microphone access
    async function requestMicrophone() {
        try {
            audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
            return true;
        } catch (e) {
            alert('Error accessing microphone: ' + e.message);
            return false;
        }
    }

    // Start recording
    async function startRecording() {
        if (!initAudio()) return;
        if (!await requestMicrophone()) return;

        const input = audioContext.createMediaStreamSource(audioStream);
        
        // Modern browsers support MediaRecorder API
        if (window.MediaRecorder) {
            recorder = new MediaRecorder(audioStream, { mimeType: 'audio/webm' });
            
            const chunks = [];
            recorder.ondataavailable = function(e) {
                if (e.data.size > 0) {
                    chunks.push(e.data);
                }
            };
            
            recorder.onstop = function() {
                audioBlob = new Blob(chunks, { type: 'audio/mp3' });
                const audioURL = URL.createObjectURL(audioBlob);
                audioPlayback.src = audioURL;
                audioContainer.classList.remove('d-none');
            };
            
            recorder.start();
        } else {
            // Fallback to custom recorder implementation
            recorder = new Recorder(input, { mimeType: 'audio/mp3' });
            recorder.record();
        }

        // Update UI
        recordButton.textContent = 'Stop Recording';
        recordButton.classList.add('recording');
        
        // Start timer
        recordingSeconds = 0;
        updateTimer();
        timerInterval = setInterval(updateTimer, 1000);
    }

    // Stop recording
    function stopRecording() {
        if (!recorder) return;

        if (recorder instanceof MediaRecorder) {
            recorder.stop();
            
            // Stop all audio tracks
            if (audioStream) {
                audioStream.getTracks().forEach(track => track.stop());
            }
        } else {
            recorder.stop();
            
            // Export the recording
            recorder.exportMP3(function(blob) {
                audioBlob = blob;
                const audioURL = URL.createObjectURL(blob);
                audioPlayback.src = audioURL;
                audioContainer.classList.remove('d-none');
                
                // Stop all audio tracks
                if (audioStream) {
                    audioStream.getTracks().forEach(track => track.stop());
                }
            });
        }

        // Update UI
        recordButton.textContent = 'Start Recording';
        recordButton.classList.remove('recording');
        
        // Stop timer
        clearInterval(timerInterval);
    }

    // Update timer display
    function updateTimer() {
        recordingSeconds++;
        const minutes = Math.floor(recordingSeconds / 60);
        const seconds = recordingSeconds % 60;
        timerElement.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }

    // Send audio to server
    function sendAudioToServer() {
        if (!audioBlob) {
            alert('No recording available');
            return;
        }

        // Show loading indicator
        loadingContainer.classList.remove('d-none');
        resultContainer.classList.add('d-none');
        
        // Create form data
        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.mp3');
        
        // Send to server
        fetch('/api/evaluate', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Server error: ' + response.status);
            }
            return response.json();
        })
        .then(data => {
            // Hide loading indicator
            loadingContainer.classList.add('d-none');
            
            // Show result
            resultText.textContent = data.result;
            resultContainer.classList.remove('d-none');
        })
        .catch(error => {
            // Hide loading indicator
            loadingContainer.classList.add('d-none');
            
            // Show error
            resultText.textContent = 'Error: ' + error.message;
            resultContainer.classList.remove('d-none');
        });
    }

    // Event listeners
    recordButton.addEventListener('click', function() {
        if (recorder && (recorder.state === 'recording' || recorder.recording)) {
            stopRecording();
        } else {
            startRecording();
        }
    });

    sendButton.addEventListener('click', sendAudioToServer);
});
