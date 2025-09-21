'use client';

import { useState } from 'react';
import AudioRecorder from '@/components/AudioRecorder';

export default function Home() {
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleRecordingComplete = (blob: Blob) => {
    setAudioBlob(blob);
    setResult(null);
    setError(null);
  };

  const analyzeAudio = async () => {
    if (!audioBlob) {
      setError('No recording available');
      return;
    }

    setIsAnalyzing(true);
    setResult(null);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('audio', audioBlob, 'recording.mp3');

      const response = await fetch('/api/evaluate', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.error) {
        throw new Error(data.error);
      }
      
      setResult(data.result);
    } catch (error: any) {
      setError(error.message || 'An error occurred during analysis');
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <main className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-md mx-auto bg-white p-6 rounded-xl shadow-md">
        <h1 className="text-2xl font-bold text-center mb-6">Audio Biomarker Analysis</h1>
        
        <AudioRecorder onRecordingComplete={handleRecordingComplete} />
        
        {audioBlob && (
          <div className="mt-6">
            <button
              onClick={analyzeAudio}
              disabled={isAnalyzing}
              className="w-full py-3 px-4 rounded-lg font-medium text-white bg-green-600 hover:bg-green-700 disabled:bg-green-400"
            >
              {isAnalyzing ? 'Analyzing...' : 'Analyze Audio'}
            </button>
          </div>
        )}
        
        {isAnalyzing && (
          <div className="mt-6 flex justify-center items-center">
            <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500"></div>
            <span className="ml-2">Analyzing audio...</span>
          </div>
        )}
        
        {result && (
          <div className="mt-6 p-4 bg-gray-50 rounded-lg">
            <h2 className="font-semibold mb-2">Analysis Result:</h2>
            <p className="text-lg">{result}</p>
          </div>
        )}
        
        {error && (
          <div className="mt-6 p-4 bg-red-50 text-red-700 rounded-lg">
            <h2 className="font-semibold mb-2">Error:</h2>
            <p>{error}</p>
          </div>
        )}
      </div>
    </main>
  );
}