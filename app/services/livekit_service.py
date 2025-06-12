import logging
from typing import Optional, Dict, Any

from livekit import rtc, api
from livekit.api import AccessToken, WebhookReceiver
from livekit.api.room_service import RoomService
from livekit.rtc import Room, RoomOptions

from core.config import settings

logger = logging.getLogger(__name__)


async def create_access_token(
    room_name: str, 
    participant_name: str, 
    participant_identity: str,
    ttl: int = 3600,  # 1 hour by default
    metadata: Optional[str] = None,
    permissions: Optional[Dict[str, bool]] = None
) -> Optional[str]:
    """
    Create a LiveKit access token for a participant to join a room

    Args:
        room_name: Name of the room to join
        participant_name: Display name of the participant
        participant_identity: Unique identity of the participant
        ttl: Time-to-live in seconds
        metadata: Optional metadata for the participant
        permissions: Optional permissions for the participant

    Returns:
        Access token string or None if creation failed
    """
    try:
        if not settings.LIVEKIT_API_KEY or not settings.LIVEKIT_API_SECRET:
            logger.error("LiveKit API key or secret not configured")
            return None

        # Create token with API key and secret
        token = AccessToken(
            api_key=settings.LIVEKIT_API_KEY.get_secret_value(),
            api_secret=settings.LIVEKIT_API_SECRET.get_secret_value()
        )

        # Set token details
        token.name = participant_name
        token.identity = participant_identity
        token.ttl = ttl

        if metadata:
            token.metadata = metadata

        # Set default permissions if not provided
        if permissions is None:
            permissions = {
                "can_publish": True,
                "can_subscribe": True,
                "can_publish_data": True
            }

        # Add permissions
        token.add_grant(
            room_join=True,
            room=room_name,
            can_publish=permissions.get("can_publish", True),
            can_subscribe=permissions.get("can_subscribe", True),
            can_publish_data=permissions.get("can_publish_data", True)
        )

        # Generate the token
        return token.to_jwt()
    except Exception as e:
        logger.error(f"Error creating LiveKit access token: {str(e)}")
        return None


async def create_room(room_name: str, empty_timeout: int = 300) -> bool:
    """
    Create a LiveKit room

    Args:
        room_name: Name of the room to create
        empty_timeout: Time in seconds to keep the room alive when empty

    Returns:
        True if room was created successfully, False otherwise
    """
    try:
        if not settings.LIVEKIT_API_KEY or not settings.LIVEKIT_API_SECRET or not settings.LIVEKIT_URL:
            logger.error("LiveKit API key, secret, or URL not configured")
            return False

        # Create room service client
        room_service = RoomService(
            settings.LIVEKIT_URL,
            settings.LIVEKIT_API_KEY.get_secret_value(),
            settings.LIVEKIT_API_SECRET.get_secret_value()
        )

        # Create room
        await room_service.create_room(
            name=room_name,
            empty_timeout=empty_timeout
        )

        return True
    except Exception as e:
        logger.error(f"Error creating LiveKit room: {str(e)}")
        return False


async def delete_room(room_name: str) -> bool:
    """
    Delete a LiveKit room

    Args:
        room_name: Name of the room to delete

    Returns:
        True if room was deleted successfully, False otherwise
    """
    try:
        if not settings.LIVEKIT_API_KEY or not settings.LIVEKIT_API_SECRET or not settings.LIVEKIT_URL:
            logger.error("LiveKit API key, secret, or URL not configured")
            return False

        # Create room service client
        room_service = RoomService(
            settings.LIVEKIT_URL,
            settings.LIVEKIT_API_KEY.get_secret_value(),
            settings.LIVEKIT_API_SECRET.get_secret_value()
        )

        # Delete room
        await room_service.delete_room(room_name)

        return True
    except Exception as e:
        logger.error(f"Error deleting LiveKit room: {str(e)}")
        return False


async def list_rooms() -> Optional[list]:
    """
    List all LiveKit rooms

    Returns:
        List of rooms or None if listing failed
    """
    try:
        if not settings.LIVEKIT_API_KEY or not settings.LIVEKIT_API_SECRET or not settings.LIVEKIT_URL:
            logger.error("LiveKit API key, secret, or URL not configured")
            return None

        # Create room service client
        room_service = RoomService(
            settings.LIVEKIT_URL,
            settings.LIVEKIT_API_KEY.get_secret_value(),
            settings.LIVEKIT_API_SECRET.get_secret_value()
        )

        # List rooms
        rooms = await room_service.list_rooms()

        return rooms
    except Exception as e:
        logger.error(f"Error listing LiveKit rooms: {str(e)}")
        return None


async def get_room_participants(room_name: str) -> Optional[list]:
    """
    Get participants in a LiveKit room

    Args:
        room_name: Name of the room

    Returns:
        List of participants or None if retrieval failed
    """
    try:
        if not settings.LIVEKIT_API_KEY or not settings.LIVEKIT_API_SECRET or not settings.LIVEKIT_URL:
            logger.error("LiveKit API key, secret, or URL not configured")
            return None

        # Create room service client
        room_service = RoomService(
            settings.LIVEKIT_URL,
            settings.LIVEKIT_API_KEY.get_secret_value(),
            settings.LIVEKIT_API_SECRET.get_secret_value()
        )

        # Get participants
        participants = await room_service.list_participants(room_name)

        return participants
    except Exception as e:
        logger.error(f"Error getting LiveKit room participants: {str(e)}")
        return None


def validate_webhook(request_body: bytes, auth_header: str) -> Optional[Dict[str, Any]]:
    """
    Validate a LiveKit webhook request

    Args:
        request_body: Raw request body bytes
        auth_header: Authorization header from the request

    Returns:
        Parsed webhook event data or None if validation failed
    """
    try:
        if not settings.LIVEKIT_API_KEY or not settings.LIVEKIT_API_SECRET:
            logger.error("LiveKit API key or secret not configured")
            return None

        # Create webhook receiver
        receiver = WebhookReceiver(
            settings.LIVEKIT_API_KEY.get_secret_value(),
            settings.LIVEKIT_API_SECRET.get_secret_value()
        )

        # Validate and parse webhook
        event = receiver.receive(request_body, auth_header)

        return event
    except Exception as e:
        logger.error(f"Error validating LiveKit webhook: {str(e)}")
        return None
