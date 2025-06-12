from datetime import datetime
from typing import Optional, List

from pydantic import Field

from schemas.base import BaseSchema, BasePaginatedSchema


# GolfSession schemas
class GolfSessionBase(BaseSchema):
    user_id: Optional[str] = None
    session_id: str
    is_active: bool = True


class InGolfSessionSchema(GolfSessionBase):
    pass


class UpdateGolfSessionSchema(BaseSchema):
    user_id: Optional[str] = None
    is_active: Optional[bool] = None


class OutGolfSessionSchema(GolfSessionBase):
    id: int
    created_at: datetime
    updated_at: datetime


class PaginatedGolfSessionSchema(BasePaginatedSchema[OutGolfSessionSchema]):
    pass


# GolfTranscript schemas
class GolfTranscriptBase(BaseSchema):
    session_id: int
    user_query: str
    assistant_response: Optional[str] = None
    audio_file_path: Optional[str] = None
    contains_wake_word: bool = False


class InGolfTranscriptSchema(GolfTranscriptBase):
    pass


class UpdateGolfTranscriptSchema(BaseSchema):
    assistant_response: Optional[str] = None
    audio_file_path: Optional[str] = None
    contains_wake_word: Optional[bool] = None


class OutGolfTranscriptSchema(GolfTranscriptBase):
    id: int
    created_at: datetime
    updated_at: datetime


class PaginatedGolfTranscriptSchema(BasePaginatedSchema[OutGolfTranscriptSchema]):
    pass


# Audio processing schemas
class AudioStreamSchema(BaseSchema):
    session_id: str
    audio_data: bytes = Field(..., description="Raw audio data in bytes")


class TranscriptionSchema(BaseSchema):
    text: str
    contains_wake_word: bool = False


class AssistantResponseSchema(BaseSchema):
    text: str
    audio_url: Optional[str] = None


# LiveKit schemas
class LiveKitRoomSchema(BaseSchema):
    room_name: str
    empty_timeout: Optional[int] = 300


class LiveKitTokenRequestSchema(BaseSchema):
    room_name: str
    participant_name: str
    participant_identity: Optional[str] = None
    ttl: Optional[int] = 3600
    metadata: Optional[str] = None


class LiveKitTokenResponseSchema(BaseSchema):
    token: str
    room_name: str
    participant_identity: str


class LiveKitRoomInfoSchema(BaseSchema):
    name: str
    sid: str
    empty_timeout: int
    max_participants: int
    created_at: datetime
    turn_password: Optional[str] = None
    enabled_codecs: Optional[List[str]] = None
    metadata: Optional[str] = None


class LiveKitParticipantInfoSchema(BaseSchema):
    identity: str
    name: Optional[str] = None
    state: Optional[str] = None
    metadata: Optional[str] = None
    joined_at: Optional[datetime] = None
