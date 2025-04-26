from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import os
import uuid
import json
from bson.objectid import ObjectId

from api.db.database import get_db, get_mongo_db
from api.models.user import User
from api.models.transcription import Transcription, CustomVocabulary
from api.schemas.transcription import (
    TranscriptionCreate, 
    TranscriptionUpdate, 
    TranscriptionResponse, 
    TranscriptionResult,
    CustomVocabularyCreate,
    CustomVocabularyResponse
)
from api.routers.auth import get_current_active_user
from api.core.config import settings
from api.services.transcription_service import process_transcription

router = APIRouter()

# Transcription endpoints
@router.post("/", response_model=TranscriptionResponse)
async def create_transcription(
    background_tasks: BackgroundTasks,
    title: str = Form(...),
    language_code: str = Form("en-US"),
    is_public: bool = Form(False),
    custom_vocabulary_id: Optional[int] = Form(None),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check if file extension is allowed
    file_ext = file.filename.split(".")[-1].lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File extension not allowed. Allowed extensions: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    
    # Create upload directory if it doesn't exist
    os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)
    
    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}.{file_ext}"
    file_path = os.path.join(settings.UPLOAD_FOLDER, unique_filename)
    
    # Save file
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
        file_size = len(content)
    
    # Create transcription record
    db_transcription = Transcription(
        user_id=current_user.id,
        title=title,
        language_code=language_code,
        is_public=is_public,
        custom_vocabulary_id=custom_vocabulary_id,
        original_filename=file.filename,
        file_path=file_path,
        file_size_bytes=file_size,
        file_format=file_ext,
        status="pending",
        # Duration will be updated during processing
        duration_seconds=0.0
    )
    
    db.add(db_transcription)
    db.commit()
    db.refresh(db_transcription)
    
    # Start transcription process in background
    background_tasks.add_task(
        process_transcription,
        db_transcription.id,
        file_path,
        language_code,
        custom_vocabulary_id
    )
    
    return db_transcription

@router.get("/", response_model=List[TranscriptionResponse])
async def get_transcriptions(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    transcriptions = db.query(Transcription).filter(
        Transcription.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    return transcriptions

@router.get("/{transcription_id}", response_model=TranscriptionResponse)
async def get_transcription(
    transcription_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    transcription = db.query(Transcription).filter(
        Transcription.id == transcription_id,
        Transcription.user_id == current_user.id
    ).first()
    
    if not transcription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transcription not found"
        )
    
    return transcription

@router.get("/{transcription_id}/result", response_model=TranscriptionResult)
async def get_transcription_result(
    transcription_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    mongo_db = Depends(get_mongo_db)
):
    transcription = db.query(Transcription).filter(
        Transcription.id == transcription_id,
        Transcription.user_id == current_user.id
    ).first()
    
    if not transcription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transcription not found"
        )
    
    if transcription.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Transcription is not completed yet. Current status: {transcription.status}"
        )
    
    if not transcription.mongo_document_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transcription result not found"
        )
    
    # Retrieve transcription result from MongoDB
    result = mongo_db.transcription_results.find_one({"_id": ObjectId(transcription.mongo_document_id)})
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transcription result not found"
        )
    
    # Convert MongoDB document to TranscriptionResult
    return TranscriptionResult(
        text=result["text"],
        segments=result.get("segments", None),
        language_code=transcription.language_code,
        confidence_score=transcription.confidence_score,
        word_count=transcription.word_count,
        speaker_count=transcription.speaker_count
    )

@router.delete("/{transcription_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transcription(
    transcription_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    mongo_db = Depends(get_mongo_db)
):
    transcription = db.query(Transcription).filter(
        Transcription.id == transcription_id,
        Transcription.user_id == current_user.id
    ).first()
    
    if not transcription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transcription not found"
        )
    
    # Delete file if it exists
    if os.path.exists(transcription.file_path):
        os.remove(transcription.file_path)
    
    # Delete MongoDB document if it exists
    if transcription.mongo_document_id:
        mongo_db.transcription_results.delete_one({"_id": ObjectId(transcription.mongo_document_id)})
    
    # Delete from database
    db.delete(transcription)
    db.commit()
    
    return None

# Custom vocabulary endpoints
@router.post("/vocabulary", response_model=CustomVocabularyResponse)
async def create_custom_vocabulary(
    vocabulary: CustomVocabularyCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Validate JSON format of terms
    try:
        json.loads(vocabulary.terms)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Terms must be a valid JSON string"
        )
    
    db_vocabulary = CustomVocabulary(
        user_id=current_user.id,
        name=vocabulary.name,
        description=vocabulary.description,
        language_code=vocabulary.language_code,
        terms=vocabulary.terms
    )
    
    db.add(db_vocabulary)
    db.commit()
    db.refresh(db_vocabulary)
    
    return db_vocabulary

@router.get("/vocabulary", response_model=List[CustomVocabularyResponse])
async def get_custom_vocabularies(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    vocabularies = db.query(CustomVocabulary).filter(
        CustomVocabulary.user_id == current_user.id
    ).all()
    
    return vocabularies
