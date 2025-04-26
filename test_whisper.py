"""
Test script for Whisper speech-to-text functionality
"""

import sys
import os
import time
import whisper
from datetime import datetime

def transcribe_audio(file_path, language=None, model_size="base"):
    """
    Transcribe audio using Whisper model.
    """
    print(f"Processing audio file: {file_path}")
    print(f"Model size: {model_size}")
    if language:
        print(f"Language: {language}")
    else:
        print("Language: Auto-detect")
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found")
        return None
    
    start_time = time.time()
    
    # Load the Whisper model
    print("Loading Whisper model...")
    model = whisper.load_model(model_size)
    
    # Transcribe the audio
    print("Transcribing audio...")
    options = {}
    if language:
        options["language"] = language.split("-")[0]  # Convert "en-US" to "en"
    
    result = model.transcribe(file_path, **options)
    
    end_time = time.time()
    processing_duration = end_time - start_time
    
    # Return the transcription result
    return {
        "text": result["text"],
        "language": result.get("language", language if language else "en"),
        "processing_duration": processing_duration,
        "timestamp": datetime.now().isoformat()
    }

def main():
    if len(sys.argv) < 2:
        print("Usage: python test_whisper.py <audio_file> [language] [model_size]")
        print("Example: python test_whisper.py sample.mp3 en-US tiny")
        return
    
    file_path = sys.argv[1]
    language = sys.argv[2] if len(sys.argv) > 2 else None
    model_size = sys.argv[3] if len(sys.argv) > 3 else "tiny"  # Use tiny model by default for faster testing
    
    print("\n=== Whisper Speech-to-Text Test ===\n")
    
    result = transcribe_audio(file_path, language, model_size)
    
    if result:
        print("\n=== Transcription Result ===\n")
        print(f"Language: {result['language']}")
        print(f"Processing time: {result['processing_duration']:.2f} seconds")
        print(f"Timestamp: {result['timestamp']}")
        print("\nTranscription:")
        print("--------------")
        print(result['text'])
        print("\n===============================\n")
    
if __name__ == "__main__":
    main()
