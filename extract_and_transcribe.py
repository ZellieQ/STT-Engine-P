"""
Script to extract audio from video and then transcribe it with Whisper
"""

import os
import time
import sys
import ssl
import argparse
import subprocess
from datetime import datetime

# Fix SSL certificate verification issues on macOS
ssl._create_default_https_context = ssl._create_unverified_context

def extract_audio(video_path, output_path=None):
    """Extract audio from video file using ffmpeg"""
    if output_path is None:
        base_name = os.path.splitext(os.path.basename(video_path))[0]
        output_path = f"{base_name}_audio.wav"
    
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
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"Audio extraction completed successfully!")
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"Error extracting audio: {e}")
        print(f"STDERR: {e.stderr.decode()}")
        return None

def process_file(args):
    """Process the file: extract audio if needed and transcribe"""
    # Extract audio if it's a video file
    video_extensions = ['.mp4', '.mov', '.avi', '.mkv', '.webm']
    file_ext = os.path.splitext(args.file_path)[1].lower()
    
    if file_ext in video_extensions:
        print("Video file detected, extracting audio first...")
        audio_path = extract_audio(args.file_path)
        if not audio_path:
            print("Audio extraction failed. Exiting.")
            return
    else:
        # Already an audio file
        audio_path = args.file_path
    
    # If segment is specified, extract that segment
    if args.start_time is not None and args.duration is not None:
        segment_path = f"segment_{os.path.basename(audio_path)}"
        print(f"Extracting segment from {args.start_time}s for {args.duration}s...")
        
        cmd = [
            "ffmpeg",
            "-i", audio_path,
            "-ss", str(args.start_time),  # Start time
            "-t", str(args.duration),     # Duration
            "-acodec", "copy",            # Copy audio codec
            "-y",                         # Overwrite output file
            segment_path
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"Segment extraction completed successfully!")
            audio_path = segment_path
        except subprocess.CalledProcessError as e:
            print(f"Error extracting segment: {e}")
            print(f"STDERR: {e.stderr.decode()}")
            return
    
    # Now transcribe the audio
    print(f"\nTranscribing {audio_path} with model {args.model}...")
    
    # Import whisper here to avoid loading it if extraction fails
    import whisper
    
    # Generate output filename if not provided
    if args.output is None:
        base_name = os.path.splitext(os.path.basename(args.file_path))[0]
        output_file = f"{base_name}_transcription.txt"
    else:
        output_file = args.output
    
    # Load model
    print("\nLoading Whisper model...")
    start_time = time.time()
    model = whisper.load_model(args.model)
    model_load_time = time.time() - start_time
    print(f"Model loaded in {model_load_time:.2f} seconds")
    
    # Transcribe audio
    print("\nTranscribing audio... (this may take a while)")
    transcribe_start_time = time.time()
    
    # Use more options for better results
    result = model.transcribe(
        audio_path,
        verbose=True,  # Show progress
        fp16=False,    # Use FP32 (more compatible)
        language=args.language if args.language else None,
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
    
    # Clean up temporary files if needed
    if args.start_time is not None and os.path.exists(segment_path):
        if args.keep_temp:
            print(f"Keeping temporary segment file: {segment_path}")
        else:
            os.remove(segment_path)
            print(f"Removed temporary segment file: {segment_path}")
    
    if file_ext in video_extensions and os.path.exists(audio_path) and audio_path != args.file_path:
        if args.keep_temp:
            print(f"Keeping extracted audio file: {audio_path}")
        else:
            os.remove(audio_path)
            print(f"Removed extracted audio file: {audio_path}")

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

def main():
    parser = argparse.ArgumentParser(description="Extract audio from video and transcribe with Whisper")
    parser.add_argument("file_path", help="Path to the video/audio file to transcribe")
    parser.add_argument("--model", choices=["tiny", "base", "small", "medium", "large"], default="base",
                        help="Whisper model size (default: base)")
    parser.add_argument("--output", help="Output file path for the transcription")
    parser.add_argument("--start_time", type=float, help="Start time in seconds for processing a segment")
    parser.add_argument("--duration", type=float, help="Duration in seconds for processing a segment")
    parser.add_argument("--language", help="Language code (e.g., 'en' for English). If not specified, auto-detect.")
    parser.add_argument("--keep_temp", action="store_true", help="Keep temporary audio files")
    
    args = parser.parse_args()
    
    process_file(args)

if __name__ == "__main__":
    main()
