import os
import pickle
import numpy as np
import librosa
import torch
import torchaudio
from transformers import Wav2Vec2Processor, Wav2Vec2Model
import argparse

def extract_features(audio_path, processor=None, wav2vec2_model=None):
    """Extract features from audio using wav2vec2 model or MFCC fallback"""
    try:
        if os.path.exists(audio_path):
            if processor is not None and wav2vec2_model is not None:
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
                    outputs = wav2vec2_model(**inputs)
                
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

def main():
    parser = argparse.ArgumentParser(description="Run COVID cough classifier on an audio file")
    parser.add_argument("audio_file", help="Path to the audio file to analyze")
    parser.add_argument("--model", default="covid_cough_classifier_v1.pkl", 
                        help="Name of the classifier model file in the models directory")
    args = parser.parse_args()
    
    # Set paths
    MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
    MODEL_PATH = os.path.join(MODEL_DIR, args.model)
    
    # Check if model exists
    if not os.path.exists(MODEL_PATH):
        print(f"Error: Model file not found at {MODEL_PATH}")
        return
    
    # Check if audio file exists
    if not os.path.exists(args.audio_file):
        print(f"Error: Audio file not found at {args.audio_file}")
        return
    
    # Load model
    print(f"Loading classifier model from {MODEL_PATH}...")
    try:
        with open(MODEL_PATH, 'rb') as f:
            model = pickle.load(f)
        print("Model loaded successfully")
    except Exception as e:
        print(f"Error loading model: {e}")
        return
    
    # Initialize audio processor
    try:
        print("Loading wav2vec2 model...")
        processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base-960h")
        wav2vec2_model = Wav2Vec2Model.from_pretrained("facebook/wav2vec2-base-960h")
        print("Loaded wav2vec2 model successfully")
    except Exception as e:
        print(f"Error loading wav2vec2 model: {e}")
        print("Falling back to MFCC features")
        processor = None
        wav2vec2_model = None
    
    # Extract features
    print(f"Extracting features from {args.audio_file}...")
    features = extract_features(args.audio_file, processor, wav2vec2_model)
    
    if features is None:
        print("Failed to extract features from audio")
        return
    
    # Make prediction
    print("Making prediction...")
    features = features.reshape(1, -1)  # Reshape for single sample prediction
    prediction = int(model.predict(features)[0])
    probabilities = model.predict_proba(features)[0]
    
    # Display results
    print("\n===== Prediction Results =====")
    print(f"Prediction: {'COVID-19 Positive' if prediction == 1 else 'Healthy'} (class {prediction})")
    print(f"Probability of healthy: {probabilities[0]:.4f}")
    print(f"Probability of COVID-19 positive: {probabilities[1]:.4f}")

if __name__ == "__main__":
    main()
