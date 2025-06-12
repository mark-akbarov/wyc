import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Body, Header, Request
from fastapi.responses import StreamingResponse

from api.dependencies.database import DbSessionDep
from api.dependencies.pagination import PaginationDep
from core.config import settings
from db.crud.golf_assistant import GolfSessionCrud, GolfTranscriptCrud
from schemas.golf_assistant import (
    InGolfSessionSchema,
    OutGolfSessionSchema,
    PaginatedGolfSessionSchema,
    UpdateGolfSessionSchema,
    InGolfTranscriptSchema,
    OutGolfTranscriptSchema,
    PaginatedGolfTranscriptSchema,
    UpdateGolfTranscriptSchema,
    # LiveKit schemas
    LiveKitRoomSchema,
    LiveKitTokenRequestSchema,
    LiveKitTokenResponseSchema,
    LiveKitRoomInfoSchema,
    LiveKitParticipantInfoSchema,
)

# Import services
from services.openai_service import (
    transcribe_audio,
    detect_wake_word,
    get_assistant_response,
)
from services.tts_service import text_to_speech
from services.livekit_service import (
    create_access_token,
    create_room,
    delete_room,
    list_rooms,
    get_room_participants,
    validate_webhook,
)

router = APIRouter(
    prefix="/golf-assistant",
    tags=["Golf Assistant"],
)


# Session management endpoints
@router.post("/sessions", status_code=201, response_model=OutGolfSessionSchema)
async def create_session(
    db: DbSessionDep,
    user_id: Optional[str] = None,
):
    """
    Create a new golf assistant session
    """
    session_id = str(uuid.uuid4())
    crud = GolfSessionCrud(db)
    session_data = InGolfSessionSchema(
        session_id=session_id,
        user_id=user_id,
        is_active=True,
    )
    result = await crud.create(session_data)
    await crud.commit_session()
    return result


@router.get("/sessions", response_model=PaginatedGolfSessionSchema)
async def list_sessions(
    db: DbSessionDep,
    pagination: PaginationDep,
):
    """
    List all golf assistant sessions
    """
    crud = GolfSessionCrud(db)
    return await crud.get_paginated_list(pagination.limit, pagination.offset)


@router.get("/sessions/{session_id}", response_model=OutGolfSessionSchema)
async def get_session(
    session_id: str,
    db: DbSessionDep,
):
    """
    Get a specific golf assistant session by its session_id
    """
    crud = GolfSessionCrud(db)
    result = await crud.get_by_session_id(session_id)
    if not result:
        raise HTTPException(status_code=404, detail="Session not found")
    return result


@router.patch("/sessions/{session_id}", response_model=OutGolfSessionSchema)
async def update_session(
    session_id: str,
    update_data: UpdateGolfSessionSchema,
    db: DbSessionDep,
):
    """
    Update a golf assistant session
    """
    crud = GolfSessionCrud(db)
    session = await crud.get_by_session_id(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    await crud.update_by_id(session.id, update_data)
    result = await crud.get_by_id(session.id)
    await crud.commit_session()
    return result


# Audio processing endpoints
@router.post("/interaction", response_class=StreamingResponse)
async def process_interaction(
    db: DbSessionDep,
    session_id: str = Body(...),
    audio_file: UploadFile = File(...),
):
    """
    Process a user interaction:
    1. Receives an audio file and session ID.
    2. Transcribes the audio.
    3. Detects a wake word.
    4. If wake word is detected, get a response from an AI assistant.
    5. Convert the response to speech.
    6. Streams the audio response back.
    """
    # 1. Verify session
    session_crud = GolfSessionCrud(db)
    session = await session_crud.get_by_session_id(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # 2. Read and transcribe audio
    audio_data = await audio_file.read()
    transcription = await transcribe_audio(audio_data)

    # 3. Detect wake word
    contains_wake_word = detect_wake_word(transcription, settings.WAKE_WORD)

    # 4. Save transcript
    transcript_crud = GolfTranscriptCrud(db)
    transcript_data = InGolfTranscriptSchema(
        session_id=session.id,
        user_query=transcription,
        contains_wake_word=contains_wake_word,
    )
    transcript = await transcript_crud.create(transcript_data)
    await transcript_crud.commit_session()  # Commit early

    # 5. Get AI response if wake word is present
    if not contains_wake_word:
        # Return empty stream if no wake word
        return StreamingResponse(iter(b""), media_type="audio/mpeg")

    assistant_response_text = await get_assistant_response(transcription)

    # 6. Convert response to speech
    response_audio_generator = await text_to_speech(assistant_response_text)

    # 7. Update transcript with response
    update_data = UpdateGolfTranscriptSchema(
        assistant_response=assistant_response_text,
    )
    await transcript_crud.update_by_id(transcript.id, update_data)
    await transcript_crud.commit_session()

    # 8. Stream audio back
    return StreamingResponse(response_audio_generator, media_type="audio/mpeg")


@router.get("/transcripts", response_model=PaginatedGolfTranscriptSchema)
async def list_transcripts(
    db: DbSessionDep,
    pagination: PaginationDep,
    session_id: Optional[str] = None,
):
    """
    List transcripts, optionally filtered by session_id
    """
    transcript_crud = GolfTranscriptCrud(db)

    if session_id:
        session_crud = GolfSessionCrud(db)
        session = await session_crud.get_by_session_id(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        transcripts = await transcript_crud.get_by_session_id(
            session.id,
            limit=pagination.limit
        )
        return PaginatedGolfTranscriptSchema(
            total=len(transcripts),
            items=transcripts,
        )

    return await transcript_crud.get_paginated_list(pagination.limit, pagination.offset)


# Golf logic endpoints
@router.get("/suggest-club/{distance}")
async def suggest_club(
    distance: float,
):
    """
    Suggest a golf club based on distance
    """
    if distance < 100:
        return {"club": "Wedge", "explanation": "For short distances under 100 yards, a wedge is appropriate."}
    elif distance < 150:
        return {"club": "9 Iron", "explanation": "For distances between 100-150 yards, a 9 iron is a good choice."}
    elif distance < 180:
        return {"club": "7 Iron", "explanation": "For distances between 150-180 yards, a 7 iron is recommended."}
    elif distance < 220:
        return {"club": "5 Iron", "explanation": "For distances between 180-220 yards, a 5 iron provides good distance."}
    else:
        return {"club": "Driver", "explanation": "For distances over 220 yards, use your driver for maximum distance."}


@router.get("/wind-conditions")
async def check_wind_conditions():
    """
    Check wind conditions (placeholder)
    """
    # This would be replaced with actual weather API integration or OpenAI Assistant function
    return {
        "speed": "10 mph",
        "direction": "North-East",
        "recommendation": "Adjust your aim slightly to the left to account for the crosswind."
    }


# LiveKit endpoints
@router.post("/livekit/rooms", response_model=LiveKitRoomInfoSchema)
async def create_livekit_room(
    room_data: LiveKitRoomSchema,
):
    """
    Create a LiveKit room for real-time audio communication
    """
    # Check if LiveKit is configured
    if not settings.LIVEKIT_API_KEY or not settings.LIVEKIT_API_SECRET or not settings.LIVEKIT_URL:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LiveKit is not configured"
        )

    # Create the room
    success = await create_room(room_data.room_name, room_data.empty_timeout)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create LiveKit room"
        )

    # Get room info
    rooms = await list_rooms()
    if not rooms:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get room information"
        )

    # Find the created room
    room_info = None
    for room in rooms:
        if room.name == room_data.room_name:
            room_info = room
            break

    if not room_info:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Room was created but could not be found"
        )

    return room_info


@router.post("/livekit/token", response_model=LiveKitTokenResponseSchema)
async def generate_livekit_token(
    token_request: LiveKitTokenRequestSchema,
):
    """
    Generate a LiveKit access token for a participant to join a room
    """
    # Check if LiveKit is configured
    if not settings.LIVEKIT_API_KEY or not settings.LIVEKIT_API_SECRET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LiveKit is not configured"
        )

    # Generate a unique identity if not provided
    participant_identity = token_request.participant_identity or str(uuid.uuid4())

    # Create the token
    token = await create_access_token(
        room_name=token_request.room_name,
        participant_name=token_request.participant_name,
        participant_identity=participant_identity,
        ttl=token_request.ttl,
        metadata=token_request.metadata
    )

    if not token:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create LiveKit access token"
        )

    return LiveKitTokenResponseSchema(
        token=token,
        room_name=token_request.room_name,
        participant_identity=participant_identity
    )


@router.get("/livekit/rooms", response_model=List[LiveKitRoomInfoSchema])
async def list_livekit_rooms():
    """
    List all LiveKit rooms
    """
    # Check if LiveKit is configured
    if not settings.LIVEKIT_API_KEY or not settings.LIVEKIT_API_SECRET or not settings.LIVEKIT_URL:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LiveKit is not configured"
        )

    # Get rooms
    rooms = await list_rooms()
    if rooms is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list LiveKit rooms"
        )

    return rooms


@router.get("/livekit/rooms/{room_name}/participants", response_model=List[LiveKitParticipantInfoSchema])
async def get_livekit_room_participants(
    room_name: str,
):
    """
    Get participants in a LiveKit room
    """
    # Check if LiveKit is configured
    if not settings.LIVEKIT_API_KEY or not settings.LIVEKIT_API_SECRET or not settings.LIVEKIT_URL:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LiveKit is not configured"
        )

    # Get participants
    participants = await get_room_participants(room_name)
    if participants is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get LiveKit room participants"
        )

    return participants


@router.post("/livekit/webhook")
async def livekit_webhook(
    request: Request,
    authorization: Optional[str] = Header(None),
):
    """
    Handle LiveKit webhook events
    """
    # Check if LiveKit is configured
    if not settings.LIVEKIT_API_KEY or not settings.LIVEKIT_API_SECRET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LiveKit is not configured"
        )

    # Get request body
    body = await request.body()

    # Validate webhook
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )

    event = validate_webhook(body, authorization)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook signature"
        )

    # Process webhook event
    # This is where you would handle different event types
    # For now, we just return the event data
    return event
