# Audio Biomarker Web Application

This web application records audio from the user's microphone, sends it to a Flask backend, and evaluates it using a machine learning model.

## Features

- Browser-based audio recording
- MP3 audio format support
- Flask API backend
- ML model integration for audio analysis

## Setup Instructions

1. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Create the placeholder model:
   ```
   python create_model.py
   ```

3. Run the Flask application:
   ```
   python app.py
   ```

4. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

## Project Structure

- `app.py` - Flask application
- `model/` - Directory containing the ML model
- `static/` - Static files (JavaScript, CSS)
  - `js/app.js` - Main application JavaScript
  - `js/recorder.js` - Audio recording library
  - `js/recorderWorker.js` - Web worker for audio processing
- `templates/` - HTML templates
  - `index.html` - Main application page
- `uploads/` - Directory for uploaded audio files

## API Endpoints

- `GET /` - Main application page
- `POST /api/evaluate` - Endpoint for audio evaluation
  - Accepts: `multipart/form-data` with an audio file
  - Returns: JSON with evaluation result

## Requirements

- Python 3.8+
- Modern web browser with microphone access
- Internet connection for loading Bootstrap CSS/JS
