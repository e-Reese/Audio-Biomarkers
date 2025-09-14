import os
from flask import Flask, request, jsonify, render_template
import pickle
import numpy as np
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

# Load the model (replace with your actual model path)
MODEL_PATH = 'model/covid_cough_classifier_v1.pkl'

def load_model():
    try:
        with open(MODEL_PATH, 'rb') as f:
            model = pickle.load(f)
        return model
    except FileNotFoundError:
        print(f"Model file not found at {MODEL_PATH}")
        return None
    except Exception as e:
        print(f"Error loading model: {e}")
        return None

# Function to process audio and get prediction
def evaluate_audio(audio_path):
    """
    Process audio file and return prediction
    Replace this with your actual audio processing and model prediction logic
    """
    try:
        model = load_model()
        if model is None:
            return "Error: Model could not be loaded"
        
        # Here you would typically:
        # 1. Load and preprocess the audio file
        # 2. Extract features
        # 3. Make prediction using the model
        
        # Placeholder for actual model prediction
        result = "asdfasdfasdfas"
        return result
    except Exception as e:
        return f"Error processing audio: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/evaluate', methods=['POST'])
def evaluate():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
    
    audio_file = request.files['audio']
    if audio_file.filename == '':
        return jsonify({'error': 'No audio file selected'}), 400
    
    if audio_file:
        filename = secure_filename(audio_file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        audio_file.save(filepath)
        
        # Process the audio file
        result = evaluate_audio(filepath)
        
        return jsonify({'result': result})

if __name__ == '__main__':
    # Create uploads directory if it doesn't exist
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    
    # Create model directory if it doesn't exist
    model_dir = os.path.dirname(MODEL_PATH)
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
    
    app.run(debug=True)
