# Audio Biomarkers Next.js App

This application analyzes audio recordings to detect health biomarkers, including COVID-19 detection and age prediction.

## Features

- Record audio directly in the browser
- Analyze cough audio for COVID-19 detection
- Predict age from voice audio
- Modern, responsive UI built with Next.js and Tailwind CSS

## Prerequisites

- Node.js 18.x or higher
- Python 3.8 or higher
- pip (Python package manager)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd audio-webapp-nextjs
   ```

2. Install JavaScript dependencies:
   ```bash
   npm install
   ```

3. Install Python dependencies:
   ```bash
   npm run setup
   # or directly:
   pip install -r python/requirements.txt
   ```

## Running the Application

1. Start the development server:
   ```bash
   npm run dev
   ```

2. Open [http://localhost:3000](http://localhost:3000) in your browser to see the application.

## Project Structure

- `/src/app` - Next.js app directory structure
- `/src/components` - React components
- `/python` - Python scripts for audio analysis
- `/models` - ML models for prediction
- `/uploads` - Temporary storage for audio uploads

## How It Works

1. The user records audio in the browser
2. The audio is sent to the server via API
3. Python scripts analyze the audio using ML models
4. Results are returned to the frontend and displayed

## Technologies Used

- Next.js
- React
- TypeScript
- Tailwind CSS
- Python
- scikit-learn
- librosa (audio processing)
- transformers (Hugging Face)
- torch/torchaudio