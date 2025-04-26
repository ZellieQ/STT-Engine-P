from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class TranscriptionBase(BaseModel):
    title: str
    language_code: str = "en-US"
    is_public: bool = False
    custom_vocabulary_id: Optional[int] = None

class TranscriptionCreate(TranscriptionBase):
    pass

class TranscriptionUpdate(BaseModel):
    title: Optional[str] = None
    is_public: Optional[bool] = None

class SpeakerSegment(BaseModel):
    speaker_id: str
    start_time: float
    end_time: float
    text: str
    confidence: float

class TranscriptionResult(BaseModel):
    text: str
    segments: Optional[List[SpeakerSegment]] = None
    language_code: str
    confidence_score: float
    word_count: int
    speaker_count: int = 0

class TranscriptionResponse(TranscriptionBase):
    id: int
    user_id: int
    status: str
    original_filename: str
    file_size_bytes: int
    duration_seconds: float
    file_format: str
    word_count: int
    confidence_score: float
    has_speaker_diarization: bool
    speaker_count: int
    created_at: datetime
    processing_started_at: Optional[datetime] = None
    processing_completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    class Config:
        orm_mode = True

class CustomVocabularyBase(BaseModel):
    name: str
    description: Optional[str] = None
    language_code: str = "en-US"
    terms: str  # JSON string of terms

class CustomVocabularyCreate(CustomVocabularyBase):
    pass

class CustomVocabularyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    terms: Optional[str] = None

class CustomVocabularyResponse(CustomVocabularyBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True
