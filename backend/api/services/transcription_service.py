import os
import json
import time
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any, AsyncGenerator, List
from sqlalchemy.orm import Session
from fastapi import WebSocket
import numpy as np
import librosa
from bson.objectid import ObjectId

# Import the Whisper service for speech recognition
from api.services.whisper_service import transcribe_audio, transcribe_with_diarization

from api.db.database import SessionLocal, get_mongo_db
from api.models.transcription import Transcription, CustomVocabulary
from api.core.config import settings

async def process_transcription(
    transcription_id: int,
    file_path: str,
    language_code: str,
    custom_vocabulary_id: Optional[int] = None
):
    """
    Process an audio file and generate a transcription.
    This is a background task that updates the transcription record in the database.
    """
    # Create a new database session
    db = SessionLocal()
    mongo_db = get_mongo_db()
    
    try:
        # Get the transcription record
        transcription = db.query(Transcription).filter(Transcription.id == transcription_id).first()
        
        if not transcription:
            print(f"Transcription {transcription_id} not found")
            return
        
        # Update status to processing
        transcription.status = "processing"
        transcription.processing_started_at = datetime.now()
        db.commit()
        
        # Get custom vocabulary if provided
        custom_vocabulary = None
        if custom_vocabulary_id:
            custom_vocabulary = db.query(CustomVocabulary).filter(
                CustomVocabulary.id == custom_vocabulary_id
            ).first()
        
        # Load audio file and get duration
        try:
            y, sr = librosa.load(file_path, sr=None)
            duration = librosa.get_duration(y=y, sr=sr)
            transcription.duration_seconds = duration
            db.commit()
        except Exception as e:
            transcription.status = "failed"
            transcription.error_message = f"Failed to load audio file: {str(e)}"
            db.commit()
            return
        
        # Get custom vocabulary terms if provided
        custom_vocabulary_terms = []
        if custom_vocabulary:
            try:
                vocab_terms = json.loads(custom_vocabulary.terms)
                custom_vocabulary_terms = list(vocab_terms.keys())
            except json.JSONDecodeError:
                print(f"Error parsing custom vocabulary terms: {custom_vocabulary.terms}")
        
        # Determine if we should use speaker diarization
        use_diarization = True  # You can make this configurable
        
        try:
            # Choose model size based on audio duration
            model_size = "base"  # Default
            if duration > 600:  # 10+ minutes
                model_size = "small"
            elif duration > 1800:  # 30+ minutes
                model_size = "medium"
            
            # Process the audio with Whisper
            if use_diarization:
                transcription_result = transcribe_with_diarization(
                    file_path=file_path,
                    language_code=language_code,
                    model_size=model_size
                )
            else:
                transcription_result = transcribe_audio(
                    file_path=file_path,
                    language_code=language_code,
                    model_size=model_size,
                    custom_vocabulary=custom_vocabulary_terms if custom_vocabulary_terms else None
                )
        except Exception as e:
            print(f"Error during transcription: {str(e)}")
            transcription.status = "failed"
            transcription.error_message = f"Transcription failed: {str(e)}"
            db.commit()
            return
        
        # Store the transcription result in MongoDB
        result_id = mongo_db.transcription_results.insert_one({
            "text": transcription_result["text"],
            "segments": transcription_result["segments"],
            "created_at": datetime.now()
        }).inserted_id
        
        # Update the transcription record
        transcription.status = "completed"
        transcription.processing_completed_at = datetime.now()
        transcription.mongo_document_id = str(result_id)
        transcription.word_count = len(transcription_result["text"].split())
        transcription.confidence_score = transcription_result["confidence"]
        transcription.has_speaker_diarization = True if transcription_result["segments"] else False
        transcription.speaker_count = len(set(segment["speaker_id"] for segment in transcription_result["segments"])) if transcription_result["segments"] else 0
        
        # Update user's usage statistics
        user = transcription.user
        user.total_transcription_seconds += transcription.duration_seconds
        user.total_transcription_count += 1
        
        db.commit()
        
    except Exception as e:
        # Handle any exceptions
        try:
            transcription.status = "failed"
            transcription.error_message = str(e)
            db.commit()
        except:
            pass
        print(f"Error processing transcription {transcription_id}: {str(e)}")
    
    finally:
        # Close the database session
        db.close()

async def process_real_time_audio(websocket: WebSocket, language_code: str) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Process audio in real-time from a WebSocket connection.
    Yields transcription results as they become available.
    """
    buffer = []
    audio_data = bytearray()
    model_size = "tiny"  # Use the smallest model for real-time processing
    
    try:
        # Create a temporary file for storing audio chunks
        temp_file_path = os.path.join("uploads", f"realtime_{datetime.now().strftime('%Y%m%d%H%M%S')}.wav")
        os.makedirs(os.path.dirname(temp_file_path), exist_ok=True)
        
        # Initialize transcription state
        full_transcript = ""
        
        while True:
            # Receive audio data from WebSocket
            try:
                data = await websocket.receive_bytes()
            except Exception as e:
                print(f"Error receiving data: {str(e)}")
                break
            
            if not data:
                # End of stream
                break
            
            # Add data to buffer
            audio_data.extend(data)
            buffer.append(data)
            
            # Process buffer when it reaches a certain size (approximately 2 seconds of audio)
            if len(buffer) >= 20:  # Adjust based on your audio chunk size
                # Save current audio data to temporary file
                with open(temp_file_path, "wb") as f:
                    f.write(audio_data)
                
                try:
                    # Process with Whisper
                    result = transcribe_audio(
                        file_path=temp_file_path,
                        language_code=language_code,
                        model_size=model_size
                    )
                    
                    # Update full transcript
                    full_transcript = result["text"]
                    
                    # Yield intermediate result
                    yield {
                        "text": full_transcript,
                        "is_final": False,
                        "confidence": result["confidence"]
                    }
                except Exception as e:
                    print(f"Error in real-time transcription: {str(e)}")
                    yield {"error": str(e)}
                
                # Keep the buffer but don't clear audio_data to maintain context
                buffer = buffer[-5:]  # Keep last few chunks for context
        
        # Process any remaining audio for final result
        if audio_data:
            # Save final audio data
            with open(temp_file_path, "wb") as f:
                f.write(audio_data)
            
            try:
                # Process with Whisper
                result = transcribe_audio(
                    file_path=temp_file_path,
                    language_code=language_code,
                    model_size=model_size
                )
                
                # Yield final result
                yield {
                    "text": result["text"],
                    "is_final": True,
                    "confidence": result["confidence"]
                }
            except Exception as e:
                print(f"Error in final transcription: {str(e)}")
                yield {"error": str(e)}
            
            # Clean up temporary file
            try:
                os.remove(temp_file_path)
            except:
                pass
            
    except Exception as e:
        print(f"Error in real-time transcription: {str(e)}")
        yield {"error": str(e)}


