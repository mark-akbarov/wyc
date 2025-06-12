import os
import logging
from openai import AsyncOpenAI

from core.config import settings

# Initialize OpenAI client
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY.get_secret_value() if settings.OPENAI_API_KEY else None)

logger = logging.getLogger(__name__)


async def transcribe_audio(audio_data: bytes) -> str:
    """
    Transcribe audio using OpenAI Whisper API
    
    Args:
        audio_data: Raw audio data in bytes
        
    Returns:
        Transcribed text
    """
    try:
        # Save audio data to a temporary file
        temp_file_path = "/tmp/audio_temp.wav"
        with open(temp_file_path, "wb") as f:
            f.write(audio_data)
        
        # Transcribe using OpenAI Whisper API
        with open(temp_file_path, "rb") as audio_file:
            response = await client.audio.transcriptions.create(
                file=audio_file,
                model="whisper-1",
                language="en"
            )
        
        # Clean up temporary file
        os.remove(temp_file_path)
        
        return response.text
    except Exception as e:
        logger.error(f"Error transcribing audio: {str(e)}")
        return ""


def detect_wake_word(text: str, wake_word: str = "Hey Ceddy") -> bool:
    """
    Detect if the wake word is present in the transcribed text
    
    Args:
        text: Transcribed text
        wake_word: Wake word to detect (default: "Hey Ceddy")
        
    Returns:
        True if wake word is detected, False otherwise
    """
    return wake_word.lower() in text.lower()


async def get_assistant_response(query: str) -> str:
    """
    Get a response from the OpenAI Assistant
    
    Args:
        query: User query
        
    Returns:
        Assistant response
    """
    try:
        # Check if assistant ID is configured
        assistant_id = settings.OPENAI_ASSISTANT_ID
        if not assistant_id:
            # Create a new assistant if not configured
            assistant = await client.beta.assistants.create(
                name="Ceddy Golf Assistant",
                instructions="""
                You are Ceddy, an AI golf coach helping players during games. 
                Suggest golf clubs, analyze environmental conditions, and give concise golf tips. 
                Respond only when the player says "Hey Ceddy."
                """,
                tools=[
                    {
                        "type": "function",
                        "function": {
                            "name": "suggest_club",
                            "description": "Suggest a golf club based on distance",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "distance": {
                                        "type": "number",
                                        "description": "Distance in yards"
                                    }
                                },
                                "required": ["distance"]
                            }
                        }
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "check_wind_conditions",
                            "description": "Check current wind conditions",
                            "parameters": {
                                "type": "object",
                                "properties": {}
                            }
                        }
                    }
                ],
                model="gpt-4-turbo-preview"
            )
            assistant_id = assistant.id
            logger.info(f"Created new assistant with ID: {assistant_id}")
        else:
            logger.info(f"Using existing assistant with ID: {assistant_id}")
        
        # Create a thread
        thread = await client.beta.threads.create()
        
        # Add a message to the thread
        await client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=query
        )
        
        # Run the assistant
        run = await client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant_id
        )
        
        # Wait for the run to complete
        while run.status in ["queued", "in_progress"]:
            run = await client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
        
        # Get the messages
        messages = await client.beta.threads.messages.list(
            thread_id=thread.id
        )
        
        # Return the assistant's response
        for message in messages.data:
            if message.role == "assistant":
                return message.content[0].text.value
        
        return "I'm sorry, I couldn't process your request."
    except Exception as e:
        logger.error(f"Error getting assistant response: {str(e)}")
        return "I'm sorry, I encountered an error while processing your request."


async def suggest_club(distance: float) -> dict:
    """
    Suggest a golf club based on distance
    
    Args:
        distance: Distance in yards
        
    Returns:
        Dictionary with club suggestion and explanation
    """
    # This is a simple implementation that would be replaced with a call to the OpenAI Assistant
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


async def check_wind_conditions() -> dict:
    """
    Check wind conditions (placeholder)
    
    Returns:
        Dictionary with wind speed, direction, and recommendation
    """
    # This would be replaced with actual weather API integration or OpenAI Assistant function
    return {
        "speed": "10 mph",
        "direction": "North-East",
        "recommendation": "Adjust your aim slightly to the left to account for the crosswind."
    }