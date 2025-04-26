"""
Web application for speech-to-text transcription using Whisper
"""

import os
import time
import uuid
import json
import ssl
import subprocess
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for

# Fix SSL certificate verification issues on macOS
ssl._create_default_https_context = ssl._create_unverified_context

app = Flask(__name__)

# Configure folders
UPLOAD_FOLDER = 'uploads'
TRANSCRIPTION_FOLDER = 'transcriptions'
TEMP_FOLDER = 'temp'

# Create necessary directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TRANSCRIPTION_FOLDER, exist_ok=True)
os.makedirs(TEMP_FOLDER, exist_ok=True)
os.makedirs('templates', exist_ok=True)
os.makedirs('static', exist_ok=True)

# Maximum file size (2GB to accommodate 90-minute high-quality audio/video)
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 * 1024

# Supported file types
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'ogg', 'flac', 'm4a', 'mp4', 'mov', 'avi', 'mkv', 'webm'}

def allowed_file(filename):
    """Check if a file has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_audio(video_path, output_path):
    """Extract audio from video file using ffmpeg"""
    print(f"Extracting audio from {video_path} to {output_path}...")
    
    # Use ffmpeg to extract audio
    cmd = [
        "ffmpeg",
        "-i", video_path,
        "-vn",                  # No video
        "-acodec", "pcm_s16le", # PCM 16-bit encoding
        "-ar", "16000",         # 16kHz sample rate (good for speech)
        "-ac", "1",             # Mono channel
        "-y",                   # Overwrite output file
        output_path
    ]
    
    try:
        # Use Popen to get real-time output for long extractions
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        
        # Monitor the process
        while True:
            output = process.stderr.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
        
        # Check return code
        if process.returncode != 0:
            print(f"Error extracting audio, return code: {process.returncode}")
            return False
            
        return True
    except Exception as e:
        print(f"Error extracting audio: {e}")
        return False

def transcribe_audio(audio_path, model_size, language=None, chunk_size=30):
    """Transcribe audio using Whisper, with support for chunking long audio"""
    # Import whisper here to avoid loading it unnecessarily
    import whisper
    import torch
    import numpy as np
    from pydub import AudioSegment
    import os
    
    # Get audio duration
    audio = AudioSegment.from_file(audio_path)
    duration_seconds = len(audio) / 1000
    print(f"Audio duration: {duration_seconds:.2f} seconds ({duration_seconds/60:.2f} minutes)")
    
    # Determine if we need chunking (for files longer than 10 minutes)
    use_chunking = duration_seconds > (chunk_size * 60)
    
    # Load model
    print(f"Loading Whisper model: {model_size}")
    model = whisper.load_model(model_size)
    
    # Prepare options
    options = {}
    if language and language != "auto":
        options["language"] = language
    
    # For shorter files, process normally
    if not use_chunking:
        print("Processing entire audio file at once")
        result = model.transcribe(
            audio_path,
            verbose=True,
            fp16=False,
            temperature=0,
            **options
        )
        return result
    
    # For longer files, process in chunks
    print(f"Processing audio in {chunk_size}-minute chunks due to length")
    
    # Create temp directory for chunks
    chunk_dir = os.path.join(TEMP_FOLDER, "chunks")
    os.makedirs(chunk_dir, exist_ok=True)
    
    # Split audio into chunks
    chunk_paths = []
    chunk_duration_ms = chunk_size * 60 * 1000  # Convert minutes to milliseconds
    
    for i, start_ms in enumerate(range(0, len(audio), chunk_duration_ms)):
        # Extract chunk
        end_ms = min(start_ms + chunk_duration_ms, len(audio))
        chunk = audio[start_ms:end_ms]
        
        # Save chunk
        chunk_path = os.path.join(chunk_dir, f"chunk_{i}.wav")
        chunk.export(chunk_path, format="wav")
        chunk_paths.append(chunk_path)
        
        print(f"Created chunk {i+1}: {start_ms/1000:.1f}s to {end_ms/1000:.1f}s")
    
    # Process each chunk
    all_segments = []
    full_text = ""
    
    for i, chunk_path in enumerate(chunk_paths):
        print(f"Processing chunk {i+1}/{len(chunk_paths)}")
        
        # Transcribe chunk
        chunk_result = model.transcribe(
            chunk_path,
            verbose=True,
            fp16=False,
            temperature=0,
            **options
        )
        
        # Adjust timestamps for this chunk
        time_offset = (i * chunk_duration_ms) / 1000  # Convert to seconds
        
        for segment in chunk_result["segments"]:
            segment["start"] += time_offset
            segment["end"] += time_offset
            all_segments.append(segment)
        
        # Add to full text with a separator
        if i > 0:
            full_text += "\n\n"
        full_text += chunk_result["text"]
        
        # Clean up chunk file
        os.remove(chunk_path)
    
    # Clean up chunks directory if empty
    if not os.listdir(chunk_dir):
        os.rmdir(chunk_dir)
    
    # Combine results
    combined_result = {
        "text": full_text,
        "segments": all_segments,
        "language": language if language and language != "auto" else chunk_result.get("language", "en")
    }
    
    return combined_result

def format_time(seconds):
    """Format time in MM:SS.ms format"""
    minutes = int(seconds // 60)
    seconds = seconds % 60
    return f"{minutes:02d}:{seconds:05.2f}"

def save_transcription(result, output_file):
    """Save transcription to a JSON file"""
    # Extract text and segments
    data = {
        'text': result.get('text', ''),
        'segments': result.get('segments', []),
        'language': result.get('language', ''),
        'processing_time': result.get('processing_time', 0)
    }
    
    # Save to file
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    return data

def format_meeting_notes(transcription):
    """Convert transcription to meeting notes format with summary and key points"""
    import re
    from datetime import datetime
    
    # If transcription is a string, use it directly
    if isinstance(transcription, str):
        text = transcription
    # If it's a dict with segments, combine them
    elif isinstance(transcription, dict) and 'segments' in transcription:
        text = ' '.join([segment['text'] for segment in transcription['segments']])
    # If it's a dict with text, use that
    elif isinstance(transcription, dict) and 'text' in transcription:
        text = transcription['text']
    else:
        return {"error": "Invalid transcription format"}
    
    # Generate a basic summary (first 200 characters)
    summary = text[:200] + "..." if len(text) > 200 else text
    
    # Extract potential key points (sentences that might be important)
    sentences = re.split(r'(?<=[.!?])\s+', text)
    key_points = []
    
    # Look for sentences that might indicate key points
    keywords = ['important', 'key', 'must', 'should', 'need to', 'action item', 
                'takeaway', 'decision', 'agreed', 'conclusion', 'summary']
    
    for sentence in sentences:
        if any(keyword in sentence.lower() for keyword in keywords) and len(sentence) > 20:
            key_points.append(sentence)
    
    # If we didn't find enough key points, take some longer sentences
    if len(key_points) < 3:
        longer_sentences = sorted(sentences, key=len, reverse=True)[:5]
        for sentence in longer_sentences:
            if sentence not in key_points and len(sentence) > 30:
                key_points.append(sentence)
                if len(key_points) >= 3:
                    break
    
    # Extract potential action items (sentences with action verbs)
    action_items = []
    action_verbs = ['will', 'shall', 'must', 'need to', 'going to', 'plan to', 
                   'assign', 'create', 'develop', 'implement', 'complete']
    
    for sentence in sentences:
        if any(verb in sentence.lower() for verb in action_verbs) and len(sentence) > 20:
            action_items.append(sentence)
    
    # Format the meeting notes
    meeting_notes = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "summary": summary,
        "key_points": key_points[:5],  # Limit to top 5 key points
        "action_items": action_items[:5],  # Limit to top 5 action items
        "full_transcript": text
    }
    
    return meeting_notes

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index_large.html')

# Dictionary to track background jobs
jobs = {}

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and initiate background transcription"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400
    
    # Get parameters
    model_size = request.form.get('model_size', 'base')
    language = request.form.get('language', 'auto')
    chunk_size = int(request.form.get('chunk_size', '30'))  # Chunk size in minutes
    
    # Generate unique ID for this transcription
    transcription_id = str(uuid.uuid4())
    
    # Save the uploaded file
    file_extension = os.path.splitext(file.filename)[1].lower()
    original_filename = os.path.splitext(file.filename)[0]
    upload_filename = f"{transcription_id}{file_extension}"
    upload_path = os.path.join(UPLOAD_FOLDER, upload_filename)
    file.save(upload_path)
    
    # Create a status file to track progress
    status_file = os.path.join(TRANSCRIPTION_FOLDER, f"{transcription_id}_status.json")
    with open(status_file, 'w') as f:
        json.dump({
            'id': transcription_id,
            'original_filename': original_filename,
            'status': 'uploaded',
            'progress': 0,
            'model_size': model_size,
            'language': language,
            'created_at': datetime.now().isoformat()
        }, f)
    
    # Start background processing
    import threading
    thread = threading.Thread(
        target=process_file_background,
        args=(transcription_id, upload_path, file_extension, model_size, language, chunk_size)
    )
    thread.daemon = True
    thread.start()
    
    # Store job info
    jobs[transcription_id] = {
        'thread': thread,
        'status': 'processing',
        'start_time': time.time()
    }
    
    # Return immediate response with job ID
    return jsonify({
        'id': transcription_id,
        'original_filename': original_filename,
        'status': 'processing',
        'message': 'File uploaded and processing started. Check status endpoint for updates.'
    })

def process_file_background(transcription_id, file_path, file_extension, model_size, language, chunk_size):
    """Process file in background thread"""
    try:
        # Update status to processing
        update_status(transcription_id, "processing", 10)
        
        # Extract audio if it's a video file
        audio_path = file_path
        if file_extension in ['mp4', 'mov', 'avi', 'mkv', 'webm']:
            update_status(transcription_id, "extracting_audio", 20)
            audio_path = os.path.join(TEMP_FOLDER, f"{transcription_id}.wav")
            success = extract_audio(file_path, audio_path)
            
            if not success:
                update_status(transcription_id, "failed", 0, error="Failed to extract audio from video")
                return
        
        # Update status to transcribing
        update_status(transcription_id, "transcribing", 30)
        
        # Transcribe audio
        start_time = time.time()
        result = transcribe_audio(audio_path, model_size, language, int(chunk_size))
        processing_time = time.time() - start_time
        
        # Update status to saving
        update_status(transcription_id, "saving", 80)
        
        # Add processing time to result
        result['processing_time'] = processing_time
        
        # Save transcription
        output_file = os.path.join(TRANSCRIPTION_FOLDER, f"{transcription_id}.json")
        save_transcription(result, output_file)
        
        # Generate meeting notes automatically
        meeting_notes = format_meeting_notes(result)
        notes_file = os.path.join(TRANSCRIPTION_FOLDER, f"{transcription_id}_notes.json")
        with open(notes_file, 'w') as f:
            json.dump(meeting_notes, f, indent=2)
        
        # Update status to completed
        update_status(transcription_id, "completed", 100, result={
            "text": result.get("text", ""),
            "language": result.get("language", ""),
            "processing_time": processing_time,
            "has_notes": True
        })
        
        # Remove job from active jobs
        if transcription_id in jobs:
            del jobs[transcription_id]
            
    except Exception as e:
        print(f"Error processing file: {e}")
        update_status(transcription_id, "failed", 0, error=str(e))
        
        # Remove job from active jobs
        if transcription_id in jobs:
            del jobs[transcription_id]

def update_status(transcription_id, status, progress, error=None, result=None):
    """Update the status file for a transcription job"""
    status_file = os.path.join(TRANSCRIPTION_FOLDER, f"{transcription_id}_status.json")
    
    # Get current time
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Create or update status file
    status_data = {
        "id": transcription_id,
        "status": status,
        "progress": progress,
        "updated_at": now
    }
    
    # Add error message if provided
    if error:
        status_data["error"] = str(error)
    
    # Add result data if provided
    if result:
        status_data["result"] = result
    
    # If file exists, update while preserving some fields
    if os.path.exists(status_file):
        with open(status_file, 'r') as f:
            existing_data = json.load(f)
            
        # Preserve created_at and original_filename
        if "created_at" in existing_data:
            status_data["created_at"] = existing_data["created_at"]
        if "original_filename" in existing_data:
            status_data["original_filename"] = existing_data["original_filename"]
        
        # Track processing time if we're completing the job
        if status == "completed" and "created_at" in existing_data:
            try:
                created_time = datetime.strptime(existing_data["created_at"], "%Y-%m-%d %H:%M:%S")
                updated_time = datetime.strptime(now, "%Y-%m-%d %H:%M:%S")
                processing_time = (updated_time - created_time).total_seconds()
                status_data["processing_time"] = processing_time
            except Exception as e:
                print(f"Error calculating processing time: {e}")
    else:
        # If new file, set created_at
        status_data["created_at"] = now
    
    # Write to file
    with open(status_file, 'w') as f:
        json.dump(status_data, f, indent=2)
    
    return status_data

@app.route('/transcriptions/<transcription_id>')
def get_transcription(transcription_id):
    """Get a specific transcription by ID"""
    transcription_file = os.path.join(TRANSCRIPTION_FOLDER, f"{transcription_id}.json")
    
    if not os.path.exists(transcription_file):
        # Check if it's still processing
        status_file = os.path.join(TRANSCRIPTION_FOLDER, f"{transcription_id}_status.json")
        if os.path.exists(status_file):
            with open(status_file, 'r') as f:
                status_data = json.load(f)
            return jsonify(status_data)
        else:
            return jsonify({'error': 'Transcription not found'}), 404
    
    with open(transcription_file, 'r') as f:
        transcription_data = json.load(f)
    
    return jsonify(transcription_data)

@app.route('/status/<transcription_id>')
def get_status(transcription_id):
    """Get the status of a transcription job"""
    status_file = os.path.join(TRANSCRIPTION_FOLDER, f"{transcription_id}_status.json")
    
    if not os.path.exists(status_file):
        return jsonify({'error': 'Transcription job not found'}), 404
    
    with open(status_file, 'r') as f:
        status_data = json.load(f)
    
    # Add additional info from jobs dictionary
    if transcription_id in jobs:
        job_info = jobs[transcription_id]
        if 'start_time' in job_info:
            status_data['elapsed_time'] = time.time() - job_info['start_time']
    
    return jsonify(status_data)

@app.route('/view/<transcription_id>')
def view_transcription(transcription_id):
    """View a specific transcription"""
    return render_template('view.html', transcription_id=transcription_id)

@app.route('/format_notes/<transcription_id>')
def get_meeting_notes(transcription_id):
    """Generate meeting notes from a transcription"""
    transcription_file = os.path.join(TRANSCRIPTION_FOLDER, f"{transcription_id}.json")
    
    if not os.path.exists(transcription_file):
        return jsonify({'error': 'Transcription not found'}), 404
    
    with open(transcription_file, 'r') as f:
        transcription_data = json.load(f)
    
    meeting_notes = format_meeting_notes(transcription_data)
    
    # Save the meeting notes
    notes_file = os.path.join(TRANSCRIPTION_FOLDER, f"{transcription_id}_notes.json")
    with open(notes_file, 'w') as f:
        json.dump(meeting_notes, f, indent=2)
    
    return jsonify(meeting_notes)

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

# Add additional imports for handling large files
try:
    from pydub import AudioSegment
except ImportError:
    print("Installing pydub for audio processing...")
    subprocess.call([sys.executable, "-m", "pip", "install", "pydub"])
    from pydub import AudioSegment

@app.route('/jobs')
def list_jobs():
    """List all transcription jobs"""
    job_statuses = {}
    
    # Get all status files
    for filename in os.listdir(TRANSCRIPTION_FOLDER):
        if filename.endswith('_status.json'):
            job_id = filename.replace('_status.json', '')
            status_file = os.path.join(TRANSCRIPTION_FOLDER, filename)
            
            with open(status_file, 'r') as f:
                status_data = json.load(f)
            
            job_statuses[job_id] = {
                'id': job_id,
                'status': status_data.get('status', 'unknown'),
                'progress': status_data.get('progress', 0),
                'filename': status_data.get('original_filename', 'unknown'),
                'created_at': status_data.get('created_at', ''),
                'updated_at': status_data.get('updated_at', '')
            }
    
    return jsonify(list(job_statuses.values()))

# Get port from environment variable for compatibility with hosting platforms
import os

# Configure for production if needed
if os.environ.get('FLASK_ENV') == 'production':
    app.config['DEBUG'] = False
    app.config['TESTING'] = False

if __name__ == '__main__':
    # Increase timeout for large files
    app.config['TIMEOUT'] = 600  # 10 minutes timeout
    
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 8090))
    
    # Run the app
    app.run(debug=os.environ.get('FLASK_ENV') != 'production', 
            host='0.0.0.0', 
            port=port, 
            threaded=True)
