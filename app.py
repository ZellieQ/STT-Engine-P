"""
Simple web application to test speech-to-text functionality
"""

import os
import time
import uuid
import ssl
import whisper
import certifi
import urllib.request
from flask import Flask, render_template, request, jsonify

# Fix SSL certificate verification issues on macOS
ssl_context = ssl.create_default_context(cafile=certifi.where())
urllib.request.urlopen = lambda url, *args, **kwargs: urllib.request.urlopen(url, *args, **kwargs, context=ssl_context)

app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Global variable to store the loaded model
model = None

def get_model(model_size="base"):
    """Get or load the Whisper model"""
    global model
    if model is None:
        print(f"Loading Whisper model ({model_size})...")
        model = whisper.load_model(model_size)
    return model

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and transcription"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Get parameters
    model_size = request.form.get('model_size', 'base')
    language = request.form.get('language', None)
    
    # Save the file
    filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    
    try:
        # Load the model
        model = get_model(model_size)
        
        # Start timing
        start_time = time.time()
        
        # Transcribe
        options = {}
        if language and language != 'auto':
            options['language'] = language.split('-')[0]  # Convert 'en-US' to 'en'
        
        result = model.transcribe(filepath, **options)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Prepare response
        response = {
            'text': result['text'],
            'language': result.get('language', language if language else 'auto'),
            'processing_time': processing_time,
            'segments': result.get('segments', [])
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    finally:
        # Clean up the file
        try:
            os.remove(filepath)
        except:
            pass

@app.route('/languages')
def get_languages():
    """Return the list of supported languages"""
    languages = [
        {'code': 'auto', 'name': 'Auto-detect'},
        {'code': 'en', 'name': 'English'},
        {'code': 'es', 'name': 'Spanish'},
        {'code': 'fr', 'name': 'French'},
        {'code': 'de', 'name': 'German'},
        {'code': 'it', 'name': 'Italian'},
        {'code': 'pt', 'name': 'Portuguese'},
        {'code': 'nl', 'name': 'Dutch'},
        {'code': 'ja', 'name': 'Japanese'},
        {'code': 'zh', 'name': 'Chinese'},
        {'code': 'ru', 'name': 'Russian'},
        {'code': 'ar', 'name': 'Arabic'}
    ]
    return jsonify(languages)

if __name__ == '__main__':
    # Create templates and static directories
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    # Preload the model
    get_model('base')
    
    app.run(debug=True, host='0.0.0.0', port=5000)
