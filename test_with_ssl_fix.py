"""
Simple script to test the Whisper speech-to-text functionality directly
with SSL certificate verification fix for macOS
"""

import os
import time
import sys
import ssl
import certifi
import urllib.request

# Fix SSL certificate verification issues on macOS
ssl._create_default_https_context = ssl._create_unverified_context

# Import whisper after SSL fix
import whisper

def transcribe_audio(file_path, model_size="tiny"):
    """
    Transcribe audio using Whisper model
    """
    print(f"\n=== Testing Whisper Speech-to-Text ===")
    print(f"Processing file: {file_path}")
    print(f"Model size: {model_size}")
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found")
        return
    
    # Load model
    print("\nLoading Whisper model...")
    start_time = time.time()
    model = whisper.load_model(model_size)
    model_load_time = time.time() - start_time
    print(f"Model loaded in {model_load_time:.2f} seconds")
    
    # Transcribe audio
    print("\nTranscribing audio...")
    transcribe_start_time = time.time()
    result = model.transcribe(file_path)
    transcribe_time = time.time() - transcribe_start_time
    total_time = time.time() - start_time
    
    # Print results
    print("\n=== Transcription Results ===")
    print(f"Detected language: {result.get('language', 'unknown')}")
    print(f"Transcription time: {transcribe_time:.2f} seconds")
    print(f"Total processing time: {total_time:.2f} seconds")
    
    print("\nTranscription:")
    print("-" * 50)
    print(result["text"])
    print("-" * 50)
    
    # Print segments if available
    if "segments" in result and result["segments"]:
        print("\nSegments:")
        for i, segment in enumerate(result["segments"]):
            print(f"[{format_time(segment['start'])} --> {format_time(segment['end'])}] {segment['text']}")
    
    return result

def format_time(seconds):
    """Format time in MM:SS.ms format"""
    minutes = int(seconds // 60)
    seconds = seconds % 60
    return f"{minutes:02d}:{seconds:05.2f}"

def main():
    # Check command line arguments
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        # Use default sample file
        samples_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "samples")
        available_samples = [f for f in os.listdir(samples_dir) 
                            if f.endswith((".wav", ".mp3", ".flac", ".ogg"))]
        
        if not available_samples:
            print("No sample audio files found in the samples directory.")
            return
        
        # Use the first available sample
        file_path = os.path.join(samples_dir, available_samples[0])
        print(f"Using sample file: {file_path}")
    
    # Get model size from command line or use default
    model_size = sys.argv[2] if len(sys.argv) > 2 else "tiny"
    
    # Transcribe the audio
    transcribe_audio(file_path, model_size)

if __name__ == "__main__":
    main()
