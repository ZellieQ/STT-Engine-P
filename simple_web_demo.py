"""
Simple web application to demonstrate speech-to-text functionality
without requiring model download during startup
"""

import os
import time
import json
from flask import Flask, render_template, request, jsonify, send_from_directory

app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
SAMPLES_FOLDER = 'samples'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    """Render the main page"""
    return render_template('simple_index.html')

@app.route('/samples')
def list_samples():
    """List available sample audio files"""
    samples = []
    for filename in os.listdir(SAMPLES_FOLDER):
        if filename.endswith(('.wav', '.mp3', '.ogg', '.flac')):
            samples.append({
                'name': filename,
                'path': f'/samples/{filename}'
            })
    return jsonify(samples)

@app.route('/samples/<path:filename>')
def serve_sample(filename):
    """Serve a sample audio file"""
    return send_from_directory(SAMPLES_FOLDER, filename)

@app.route('/transcribe', methods=['POST'])
def transcribe():
    """Simulate transcription of a sample file"""
    sample_name = request.form.get('sample_name')
    
    # Simulate processing time
    time.sleep(2)
    
    # For demo purposes, return a predefined transcription
    sample_transcriptions = {
        'smoke_test.wav': {
            'text': 'The quick brown fox jumps over the lazy dog.',
            'language': 'en',
            'processing_time': 2.1,
            'segments': [
                {
                    'start': 0.0,
                    'end': 2.5,
                    'text': 'The quick brown fox jumps over the lazy dog.'
                }
            ]
        },
        'LDC93S1.wav': {
            'text': 'She had your dark suit in greasy wash water all year.',
            'language': 'en',
            'processing_time': 1.8,
            'segments': [
                {
                    'start': 0.0,
                    'end': 3.2,
                    'text': 'She had your dark suit in greasy wash water all year.'
                }
            ]
        }
    }
    
    # Return the predefined transcription or a default one
    return jsonify(sample_transcriptions.get(sample_name, {
        'text': 'This is a simulated transcription for demonstration purposes.',
        'language': 'en',
        'processing_time': 2.0,
        'segments': [
            {
                'start': 0.0,
                'end': 3.0,
                'text': 'This is a simulated transcription for demonstration purposes.'
            }
        ]
    }))

@app.route('/run_whisper', methods=['POST'])
def run_whisper():
    """Run the Whisper model via command line"""
    sample_name = request.form.get('sample_name')
    model_size = request.form.get('model_size', 'tiny')
    
    # Construct the command to run the run_whisper.py script
    sample_path = os.path.join(SAMPLES_FOLDER, sample_name)
    command = f"cd {os.getcwd()} && source venv/bin/activate && python run_whisper.py {sample_path} en {model_size}"
    
    try:
        # Run the command and capture output
        import subprocess
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        # Parse the output to extract the transcription
        output = result.stdout
        
        # Print full output for debugging
        print(f"Command output: {output}")
        
        # Extract the transcription text
        transcription = "Transcription not found in output"
        if "Transcription:" in output:
            parts = output.split("Transcription:")
            if len(parts) > 1:
                # Look for the END_TRANSCRIPTION marker
                if "END_TRANSCRIPTION" in parts[1]:
                    transcription_part = parts[1].split("END_TRANSCRIPTION")[0].strip()
                    # Remove the dashes and any extra whitespace
                    transcription_part = transcription_part.replace("--------------", "").strip()
                    transcription = transcription_part
                # Try different delimiters as fallback
                elif "===" in parts[1]:
                    transcription_part = parts[1].split("===")[0].strip()
                    transcription = transcription_part
                elif "---" in parts[1]:
                    transcription_part = parts[1].split("---")[0].strip()
                    transcription = transcription_part
                elif "\n\n" in parts[1]:
                    transcription_part = parts[1].split("\n\n")[0].strip()
                    transcription = transcription_part
                else:
                    # Just take everything after "Transcription:" as the transcription
                    transcription_part = parts[1].strip()
                    transcription = transcription_part
        
        # Extract processing time
        processing_time = 0.0
        if "Processing time:" in output:
            time_parts = output.split("Processing time:")
            if len(time_parts) > 1:
                time_str = time_parts[1].split("seconds")[0].strip()
                try:
                    processing_time = float(time_str)
                except:
                    pass
        
        return jsonify({
            'text': transcription,
            'language': 'en',
            'processing_time': processing_time,
            'command_output': output,
            'segments': [
                {
                    'start': 0.0,
                    'end': 3.0,
                    'text': transcription
                }
            ]
        })
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'command': command
        }), 500

if __name__ == '__main__':
    # Create templates directory
    os.makedirs('templates', exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=8080)
