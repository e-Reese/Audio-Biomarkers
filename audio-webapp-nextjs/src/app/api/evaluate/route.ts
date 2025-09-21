import { NextRequest, NextResponse } from 'next/server';
import { writeFile } from 'fs/promises';
import path from 'path';
import { exec } from 'child_process';
import { promisify } from 'util';

const execPromise = promisify(exec);

// Create uploads directory if it doesn't exist
const UPLOADS_DIR = path.join(process.cwd(), 'uploads');
const PYTHON_SCRIPT_DIR = path.join(process.cwd(), 'python');

export async function POST(request: NextRequest) {
  try {
    // Create uploads directory if it doesn't exist
    try {
      await writeFile(path.join(UPLOADS_DIR, '.keep'), '');
    } catch (error) {
      console.error('Error creating uploads directory:', error);
    }

    const formData = await request.formData();
    const audioFile = formData.get('audio') as File;

    if (!audioFile) {
      return NextResponse.json({ error: 'No audio file provided' }, { status: 400 });
    }

    // Save the file
    const filePath = path.join(UPLOADS_DIR, 'recording.mp3');
    const audioBuffer = Buffer.from(await audioFile.arrayBuffer());
    await writeFile(filePath, audioBuffer);

    // Run the Python prediction scripts
    try {
      // COVID prediction
      const covidResult = await execPromise(`python ${path.join(PYTHON_SCRIPT_DIR, 'predict_covid.py')} "${filePath}"`);
      
      // Age prediction
      const ageResult = await execPromise(`python ${path.join(PYTHON_SCRIPT_DIR, 'predict_age.py')} --audio "${filePath}"`);

      // Format the results
      const covidPrediction = covidResult.stdout.trim();
      const agePrediction = ageResult.stdout.trim();
      
      // Extract the actual predictions from the output
      const covidMatch = covidPrediction.match(/COVID: (Positive|Negative) \(Confidence: (\d+\.\d+)\)/);
      const ageMatch = agePrediction.match(/Predicted age: (\d+\.\d+) years/);
      
      let result = '';
      
      if (covidMatch) {
        result += covidMatch[0];
      } else {
        result += 'COVID prediction failed';
      }
      
      result += ' | ';
      
      if (ageMatch) {
        result += `Age Prediction: ${ageMatch[1]} years`;
      } else {
        result += 'Age prediction failed';
      }

      return NextResponse.json({ result });
    } catch (error: any) {
      console.error('Error running prediction scripts:', error);
      return NextResponse.json({ error: `Error processing audio: ${error.message}` }, { status: 500 });
    }
  } catch (error: any) {
    console.error('Error processing request:', error);
    return NextResponse.json({ error: `Server error: ${error.message}` }, { status: 500 });
  }
}

