from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, WebSocket
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import os
import uuid
from typing import Optional
import asyncio

from api.db.database import get_db
from api.models.user import User
from api.routers.auth import get_current_active_user
from api.core.config import settings
from api.services.transcription_service import process_real_time_audio

router = APIRouter()

@router.post("/upload")
async def upload_audio(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
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
    
    return {
        "filename": unique_filename,
        "original_filename": file.filename,
        "file_path": file_path,
        "file_size": len(content),
        "content_type": file.content_type
    }

@router.websocket("/stream")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    try:
        # Initialize transcription service for real-time processing
        language_code = "en-US"  # Default language
        
        # Process initial connection message to get settings
        initial_message = await websocket.receive_json()
        if "language_code" in initial_message:
            language_code = initial_message["language_code"]
        
        # Initialize real-time transcription
        async for transcription in process_real_time_audio(websocket, language_code):
            await websocket.send_json(transcription)
            
    except Exception as e:
        await websocket.send_json({"error": str(e)})
    finally:
        await websocket.close()

@router.get("/languages")
async def get_supported_languages():
    return {
        "languages": [
            {"code": "en-US", "name": "English (US)"},
            {"code": "es-ES", "name": "Spanish (Spain)"},
            {"code": "fr-FR", "name": "French (France)"},
            {"code": "de-DE", "name": "German (Germany)"},
            {"code": "it-IT", "name": "Italian (Italy)"},
            {"code": "pt-BR", "name": "Portuguese (Brazil)"},
            {"code": "ja-JP", "name": "Japanese (Japan)"},
            {"code": "zh-CN", "name": "Chinese (Simplified)"}
        ]
    }
