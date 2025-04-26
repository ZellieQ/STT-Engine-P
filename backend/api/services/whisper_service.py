import os
import tempfile
import subprocess
import json
from typing import Dict, Any, Optional, List
import torch
import numpy as np
import librosa
import whisper
from pydub import AudioSegment

# Check if CUDA is available
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Load Whisper models - we'll use a dictionary to cache models
whisper_models = {}

def get_whisper_model(model_size: str = "base"):
    """
    Get or load a Whisper model.
    
    Args:
        model_size: Size of the model to load. Options: "tiny", "base", "small", "medium", "large"
    
    Returns:
        Loaded Whisper model
    """
    if model_size not in whisper_models:
        print(f"Loading Whisper {model_size} model...")
        whisper_models[model_size] = whisper.load_model(model_size, device=DEVICE)
    
    return whisper_models[model_size]

def preprocess_audio(file_path: str) -> np.ndarray:
    """
    Preprocess audio file for Whisper model.
    
    Args:
        file_path: Path to the audio file
    
    Returns:
        Preprocessed audio as numpy array
    """
    # Convert audio to WAV format if it's not already
    file_ext = os.path.splitext(file_path)[1].lower()
    
    if file_ext != '.wav':
        # Create a temporary WAV file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
            temp_wav_path = temp_wav.name
        
        # Convert to WAV using pydub
        audio = AudioSegment.from_file(file_path)
        audio.export(temp_wav_path, format='wav')
        
        # Use the temporary WAV file
        audio_path = temp_wav_path
    else:
        audio_path = file_path
    
    # Load audio using librosa
    audio, sr = librosa.load(audio_path, sr=16000, mono=True)
    
    # Clean up temporary file if created
    if file_ext != '.wav':
        os.unlink(temp_wav_path)
    
    return audio

def transcribe_audio(
    file_path: str, 
    language_code: Optional[str] = None, 
    model_size: str = "base",
    custom_vocabulary: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Transcribe audio file using Whisper.
    
    Args:
        file_path: Path to the audio file
        language_code: Language code (e.g., "en", "fr", "de")
        model_size: Size of the Whisper model to use
        custom_vocabulary: List of custom vocabulary terms
    
    Returns:
        Dictionary containing transcription results
    """
    # Load the model
    model = get_whisper_model(model_size)
    
    # Preprocess audio
    audio = preprocess_audio(file_path)
    
    # Prepare transcription options
    options = {}
    
    # Set language if provided
    if language_code:
        # Convert language code format (e.g., "en-US" to "en")
        language = language_code.split('-')[0]
        options["language"] = language
    
    # Perform transcription
    result = model.transcribe(audio, **options)
    
    # Extract segments with timing information
    segments = []
    for segment in result["segments"]:
        segments.append({
            "speaker_id": "speaker_1",  # Default single speaker
            "start_time": segment["start"],
            "end_time": segment["end"],
            "text": segment["text"],
            "confidence": float(segment.get("confidence", 0.9))  # Default confidence if not provided
        })
    
    # Prepare the result
    transcription_result = {
        "text": result["text"],
        "segments": segments,
        "confidence": float(np.mean([segment["confidence"] for segment in segments])),
        "language": result.get("language", language_code if language_code else "en")
    }
    
    return transcription_result

def transcribe_with_diarization(
    file_path: str,
    language_code: Optional[str] = None,
    model_size: str = "base",
    num_speakers: Optional[int] = None
) -> Dict[str, Any]:
    """
    Transcribe audio with speaker diarization.
    This requires additional libraries like pyannote.audio for speaker diarization.
    
    For this implementation, we'll use a simplified approach with a subprocess call
    to a hypothetical diarization script.
    
    Args:
        file_path: Path to the audio file
        language_code: Language code (e.g., "en", "fr", "de")
        model_size: Size of the Whisper model to use
        num_speakers: Number of speakers (if known)
    
    Returns:
        Dictionary containing transcription results with speaker information
    """
    # First, get the basic transcription
    result = transcribe_audio(file_path, language_code, model_size)
    
    # For now, we'll simulate speaker diarization by alternating speakers
    # In a real implementation, you would use a proper diarization library
    segments = result["segments"]
    
    # Determine number of speakers (default to 2 if not specified)
    speaker_count = num_speakers if num_speakers is not None else 2
    
    # Assign speakers to segments
    for i, segment in enumerate(segments):
        segment["speaker_id"] = f"speaker_{(i % speaker_count) + 1}"
    
    # Update the result
    result["segments"] = segments
    
    return result
