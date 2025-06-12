from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, Text

from db.base_class import TimestampedBase


class GolfSession(TimestampedBase):
    """
    Represents a user session with the golf assistant.
    """
    user_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    session_id: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    
    # Relationships
    transcripts: Mapped[list["GolfTranscript"]] = relationship(
        "GolfTranscript", back_populates="session", cascade="all, delete-orphan"
    )


class GolfTranscript(TimestampedBase):
    """
    Stores transcriptions of user queries and assistant responses.
    """
    session_id: Mapped[int] = mapped_column(ForeignKey("golf_session.id"), nullable=False, index=True)
    user_query: Mapped[str] = mapped_column(Text, nullable=False)
    assistant_response: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    audio_file_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    contains_wake_word: Mapped[bool] = mapped_column(default=False, nullable=False)
    
    # Relationships
    session: Mapped[GolfSession] = relationship("GolfSession", back_populates="transcripts")