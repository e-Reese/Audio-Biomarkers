import os
from flask import Flask, request, jsonify, render_template
import pickle
import numpy as np
from werkzeug.utils import secure_filename
from flask_cors import CORS
import predict_covid
import predict_age

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

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
    """
    try:
        print(f"Processing audio file: {audio_path}")
        
        # Get COVID prediction
        covid_result = predict_covid.predict_covid(audio_path)
        if covid_result is None:
            print("COVID prediction returned None")
            covid_result = "COVID prediction: Error"
        
        # Get age prediction
        age_result = predict_age.predict_age(audio_path)
        if age_result is None:
            print("Age prediction returned None")
            age_result = "Age prediction: Error"
        
        # Combine results
        result = f"{covid_result} | Age: {age_result} years"
        print(f"Prediction result: {result}")
        return result
    except Exception as e:
        import traceback
        print(f"Error processing audio: {str(e)}")
        print(traceback.format_exc())
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
    
    # Check file extension
    allowed_extensions = {'mp3', 'wav', 'ogg', 'flac', 'm4a'}
    if '.' not in audio_file.filename or \
       audio_file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
        return jsonify({'error': 'Invalid audio file format. Allowed formats: mp3, wav, ogg, flac, m4a'}), 400
    
    try:
        filename = secure_filename(audio_file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        audio_file.save(filepath)
        
        # Process the audio file
        result = evaluate_audio(filepath)
        
        # Check if result is an error message
        if isinstance(result, str) and result.startswith("Error"):
            return jsonify({'error': result}), 500
        
        return jsonify({'result': result})
    except Exception as e:
        print(f"Exception in evaluate route: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

if __name__ == '__main__':
    # Create uploads directory if it doesn't exist
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    
    # Create model directory if it doesn't exist
    model_dir = os.path.dirname(MODEL_PATH)
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
    
    app.run(debug=True, port=5001)
