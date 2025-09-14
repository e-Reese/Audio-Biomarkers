import os
import sys
import numpy as np
import pickle
import torch
import torchaudio
import librosa
import argparse
from transformers import Wav2Vec2Processor, Wav2Vec2Model

# Set paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")
MODEL_PATH = os.path.join(MODELS_DIR, "age_prediction_model.pkl")
FEATURE_INFO_PATH = os.path.join(MODELS_DIR, "age_feature_info.pkl")

def load_model():
    """Load the trained age prediction model"""
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")
    
    if not os.path.exists(FEATURE_INFO_PATH):
        raise FileNotFoundError(f"Feature info file not found at {FEATURE_INFO_PATH}")
    
    # Load model and feature info
    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)
    
    with open(FEATURE_INFO_PATH, 'rb') as f:
        feature_info = pickle.load(f)
    
    return model, feature_info

def load_audio_model():
    """Load a pretrained audio model from Hugging Face"""
    print("Loading audio model...")
    try:
        processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base-960h")
        model = Wav2Vec2Model.from_pretrained("facebook/wav2vec2-base-960h")
        print("Loaded wav2vec2 model successfully")
        return processor, model
    except Exception as e:
        print(f"Error loading wav2vec2 model: {e}")
        print("Falling back to MFCC features")
        return None, None

def extract_features(processor, model, audio_path, feature_type):
    """Extract features from audio using wav2vec2 model or MFCC fallback"""
    try:
        # Load and resample audio
        if os.path.exists(audio_path):
            if processor is not None and model is not None and feature_type == 'wav2vec2':
                # Use wav2vec2 model
                waveform, sample_rate = torchaudio.load(audio_path)
                if sample_rate != 16000:
                    resampler = torchaudio.transforms.Resample(sample_rate, 16000)
                    waveform = resampler(waveform)
                    sample_rate = 16000
                
                # Ensure mono audio
                if waveform.shape[0] > 1:
                    waveform = torch.mean(waveform, dim=0, keepdim=True)
                
                # Process audio with wav2vec2 model
                inputs = processor(waveform.squeeze().numpy(), sampling_rate=sample_rate, return_tensors="pt")
                with torch.no_grad():
                    outputs = model(**inputs)
                
                # Extract embeddings
                embeddings = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
                return embeddings
            else:
                # Fallback to MFCC features
                y, sr = librosa.load(audio_path, sr=16000)
                mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40)
                mfcc_features = np.mean(mfccs, axis=1)
                
                # Add delta features
                delta_mfccs = librosa.feature.delta(mfccs)
                delta_mfcc_features = np.mean(delta_mfccs, axis=1)
                
                # Add delta-delta features
                delta2_mfccs = librosa.feature.delta(mfccs, order=2)
                delta2_mfcc_features = np.mean(delta2_mfccs, axis=1)
                
                # Combine features
                combined_features = np.concatenate([mfcc_features, delta_mfcc_features, delta2_mfcc_features])
                return combined_features
        else:
            print(f"File not found: {audio_path}")
            return None
    except Exception as e:
        print(f"Error processing {audio_path}: {e}")
        return None

def predict_age(audio_path):
    """Predict age from cough audio"""
    # Load the trained model
    model, feature_info = load_model()
    
    # Get feature type
    feature_type = feature_info.get('feature_type', 'mfcc')
    print(f"Using feature type: {feature_type}")
    
    # Load audio model if needed
    processor, audio_model = load_audio_model()
    
    # Extract features
    features = extract_features(processor, audio_model, audio_path, feature_type)
    
    if features is None:
        print(f"Failed to extract features from {audio_path}")
        return None
    
    # Check feature shape
    expected_shape = feature_info.get('input_shape', None)
    if expected_shape and features.shape != expected_shape:
        print(f"Warning: Feature shape mismatch. Expected {expected_shape}, got {features.shape}")
        
        # Try to reshape or pad if possible
        if len(features) > expected_shape[0]:
            print(f"Truncating features from {len(features)} to {expected_shape[0]}")
            features = features[:expected_shape[0]]
        elif len(features) < expected_shape[0]:
            print(f"Padding features from {len(features)} to {expected_shape[0]}")
            padding = np.zeros(expected_shape[0] - len(features))
            features = np.concatenate([features, padding])
    
    # Make prediction
    features = features.reshape(1, -1)  # Reshape for single sample prediction
    age_prediction = model.predict(features)[0]
    
    return age_prediction

def main():
    parser = argparse.ArgumentParser(description="Predict age from cough audio")
    parser.add_argument("--audio", default=os.path.join(MODELS_DIR, "Woman_coughing_three_times.wav"), 
                        help="Path to cough audio file")
    args = parser.parse_args()
    
    audio_path = args.audio
    print(f"Predicting age from {audio_path}")
    
    age = predict_age(audio_path)
    
    if age is not None:
        print(f"Predicted age: {age:.1f} years")
    else:
        print("Failed to predict age")

if __name__ == "__main__":
    main()
