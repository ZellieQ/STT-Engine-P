"""
Script to process a large video/audio file with Whisper speech-to-text
"""

import os
import time
import sys
import ssl
import argparse
from datetime import datetime

# Fix SSL certificate verification issues on macOS
ssl._create_default_https_context = ssl._create_unverified_context

# Import whisper after SSL fix
import whisper

def format_time(seconds):
    """Format time in MM:SS.ms format"""
    minutes = int(seconds // 60)
    seconds = seconds % 60
    return f"{minutes:02d}:{seconds:05.2f}"

def save_transcription(result, output_file):
    """Save transcription to a text file"""
    with open(output_file, 'w') as f:
        # Write full transcription
        f.write("# Full Transcription\n\n")
        f.write(result["text"])
        f.write("\n\n")
        
        # Write segments with timestamps
        if "segments" in result and result["segments"]:
            f.write("# Segments with Timestamps\n\n")
            for i, segment in enumerate(result["segments"]):
                f.write(f"[{format_time(segment['start'])} --> {format_time(segment['end'])}] {segment['text']}\n")
    
    print(f"Transcription saved to {output_file}")

def transcribe_audio(file_path, model_size="tiny", output_file=None):
    """
    Transcribe audio using Whisper model
    """
    print(f"\n=== Testing Whisper Speech-to-Text ===")
    print(f"Processing file: {file_path}")
    print(f"Model size: {model_size}")
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found")
        return None
    
    # Generate output filename if not provided
    if output_file is None:
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        output_file = f"{base_name}_transcription.txt"
    
    # Load model
    print("\nLoading Whisper model...")
    start_time = time.time()
    model = whisper.load_model(model_size)
    model_load_time = time.time() - start_time
    print(f"Model loaded in {model_load_time:.2f} seconds")
    
    # Transcribe audio
    print("\nTranscribing audio... (this may take a while for large files)")
    transcribe_start_time = time.time()
    
    # Use more options for better results
    result = model.transcribe(
        file_path,
        verbose=True,  # Show progress
        fp16=False,    # Use FP32 (more compatible)
        temperature=0  # Disable sampling for deterministic results
    )
    
    transcribe_time = time.time() - transcribe_start_time
    total_time = time.time() - start_time
    
    # Print results
    print("\n=== Transcription Results ===")
    print(f"Detected language: {result.get('language', 'unknown')}")
    print(f"Transcription time: {transcribe_time:.2f} seconds")
    print(f"Total processing time: {total_time:.2f} seconds")
    
    # Print a preview of the transcription (first 500 characters)
    preview_text = result["text"][:500] + "..." if len(result["text"]) > 500 else result["text"]
    print("\nTranscription Preview:")
    print("-" * 50)
    print(preview_text)
    print("-" * 50)
    
    # Save the full transcription to a file
    save_transcription(result, output_file)
    
    return result

def main():
    parser = argparse.ArgumentParser(description="Process a large video/audio file with Whisper speech-to-text")
    parser.add_argument("file_path", help="Path to the audio/video file to transcribe")
    parser.add_argument("--model", choices=["tiny", "base", "small", "medium", "large"], default="tiny",
                        help="Whisper model size (default: tiny)")
    parser.add_argument("--output", help="Output file path for the transcription (default: input_filename_transcription.txt)")
    
    args = parser.parse_args()
    
    # Transcribe the audio
    transcribe_audio(args.file_path, args.model, args.output)

if __name__ == "__main__":
    main()
