import logging
import os
import tempfile
from typing import Optional

import httpx
from core.config import settings

logger = logging.getLogger(__name__)


async def text_to_speech(text: str) -> Optional[bytes]:
    """
    Convert text to speech using ElevenLabs API or fallback to a simpler TTS service
    
    Args:
        text: Text to convert to speech
        
    Returns:
        Audio data in bytes or None if conversion failed
    """
    # Try ElevenLabs if configured
    if settings.ELEVENLABS_API_KEY:
        try:
            return await elevenlabs_tts(text)
        except Exception as e:
            logger.error(f"Error using ElevenLabs TTS: {str(e)}")
            # Fall back to Google TTS
    
    # Fallback to a simpler implementation
    try:
        return await google_tts(text)
    except Exception as e:
        logger.error(f"Error using fallback TTS: {str(e)}")
        return None


async def elevenlabs_tts(text: str) -> bytes:
    """
    Convert text to speech using ElevenLabs API
    
    Args:
        text: Text to convert to speech
        
    Returns:
        Audio data in bytes
    """
    api_key = settings.ELEVENLABS_API_KEY.get_secret_value()
    voice_id = settings.ELEVENLABS_VOICE_ID or "21m00Tcm4TlvDq8ikWAM"  # Default voice ID
    
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }
    
    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=data, headers=headers)
        response.raise_for_status()
        return response.content


async def google_tts(text: str) -> bytes:
    """
    Convert text to speech using Google Text-to-Speech (gTTS)
    This is a fallback method that uses a subprocess to call gTTS
    
    Args:
        text: Text to convert to speech
        
    Returns:
        Audio data in bytes
    """
    try:
        # Import here to avoid dependency if ElevenLabs is used
        from gtts import gTTS
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
            temp_path = temp_file.name
        
        # Generate speech
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(temp_path)
        
        # Read the file
        with open(temp_path, "rb") as f:
            audio_data = f.read()
        
        # Clean up
        os.remove(temp_path)
        
        return audio_data
    except ImportError:
        logger.error("gTTS not installed. Please install it with 'pip install gtts'")
        # Return empty bytes as fallback
        return b""
    except Exception as e:
        logger.error(f"Error in Google TTS: {str(e)}")
        return b""