from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from api.db.database import Base

class Transcription(Base):
    __tablename__ = "transcriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, index=True)
    language_code = Column(String, default="en-US")
    status = Column(String, default="pending")  # pending, processing, completed, failed
    
    # File information
    original_filename = Column(String)
    file_path = Column(String)
    file_size_bytes = Column(Integer)
    duration_seconds = Column(Float)
    file_format = Column(String)
    
    # Processing information
    processing_started_at = Column(DateTime(timezone=True), nullable=True)
    processing_completed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(String, nullable=True)
    
    # Transcription result
    # The actual transcription text is stored in MongoDB for better performance with large texts
    mongo_document_id = Column(String, nullable=True)
    
    # Metadata
    word_count = Column(Integer, default=0)
    confidence_score = Column(Float, default=0.0)
    has_speaker_diarization = Column(Boolean, default=False)
    speaker_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="transcriptions")
    
    # Additional features
    is_public = Column(Boolean, default=False)
    custom_vocabulary_id = Column(Integer, ForeignKey("custom_vocabularies.id"), nullable=True)
    custom_vocabulary = relationship("CustomVocabulary")


class CustomVocabulary(Base):
    __tablename__ = "custom_vocabularies"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    terms = Column(Text)  # JSON string of terms and optional pronunciations
    language_code = Column(String, default="en-US")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="custom_vocabularies")
    transcriptions = relationship("Transcription", back_populates="custom_vocabulary")
