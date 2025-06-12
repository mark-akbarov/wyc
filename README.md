# Hey Ceddy - AI Voice Golf Assistant

A voice-activated assistant for helping golf players make better in-game decisions. Users trigger the assistant with "Hey Ceddy" and receive real-time coaching through voice.

Built with [FastAPI](https://fastapi.tiangolo.com) for the backend.

## Features

1. Voice-activated golf assistant with wake word detection ("Hey Ceddy")
2. OpenAI Whisper API for accurate speech-to-text transcription
3. OpenAI Assistant API for intelligent golf coaching responses
4. Text-to-speech conversion for audio responses
5. LiveKit integration for real-time audio communication
6. Session management for tracking user interactions
7. Golf-specific logic functions (club suggestions, wind conditions)
8. RESTful API endpoints for frontend integration
9. PostgreSQL database for storing sessions and transcripts

### Technical Stack

1. Pipenv for dependency management. Simply run `pipenv install --dev` to install get started.
2. Docker compose for local development and testing
3. SQLAlchemy for ORM (uses async engine) and Alembic for database migrations
4. Simple authentication for docs page
5. CRUD operations generic class with pagination
6. Support for API versioning (`https://api.yourdomain.com/v1/`)
7. Async testing suite with Pytest

## Setup

### Environment Variables

Create a `.env` file in the root directory with the following variables:

```
OPENAI_API_KEY=your_openai_api_key
OPENAI_ASSISTANT_ID=your_assistant_id_optional
ELEVENLABS_API_KEY=your_elevenlabs_api_key_optional
ELEVENLABS_VOICE_ID=your_voice_id_optional
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
LIVEKIT_URL=your_livekit_url
```

The OpenAI API key is required for transcription and assistant functionality. The ElevenLabs API key is optional (the system will fall back to Google TTS if not provided). The LiveKit credentials are required for real-time audio communication features, enabling users to join virtual rooms for interactive voice sessions.

### Development Notes

Make sure to mark the `app/` folder as source in your IDE otherwise you'll get import errors.
And since all your code (except tests) lives inside `app/` folder, you should import modules like this:
```python
from core.config import settings
```

and NOT like this:
```python
# this will throw an error!
from app.core.config import settings
```

### Local setup

The following command will run a PostgreSQL database on your docker engine:
```shell
docker compose -f docker-compose-local.yml up -d
```
so that you can do
```shell
cd app; uvicorn main:app
```
or
```shell
ENVIRONMENT=test pytest
```

If you just want to build a docker container with your app and run it, just run:
```shell
docker compose up -d
```

### API Endpoints

The golf assistant API is available at `/v1/golf-assistant` with the following endpoints:

#### Session Management
- `POST /v1/golf-assistant/sessions` - Create a new session
- `GET /v1/golf-assistant/sessions` - List all sessions
- `GET /v1/golf-assistant/sessions/{session_id}` - Get a specific session
- `PATCH /v1/golf-assistant/sessions/{session_id}` - Update a session

#### Audio Processing
- `POST /v1/golf-assistant/audio` - Process an audio file and return transcription
- `POST /v1/golf-assistant/audio/stream` - Process streaming audio and return assistant response
- `GET /v1/golf-assistant/transcripts` - List transcripts, optionally filtered by session_id

#### Golf Logic
- `GET /v1/golf-assistant/suggest-club/{distance}` - Suggest a golf club based on distance
- `GET /v1/golf-assistant/wind-conditions` - Check wind conditions (placeholder)

#### LiveKit Integration
- `POST /v1/golf-assistant/livekit/rooms` - Create a LiveKit room for real-time audio communication
- `POST /v1/golf-assistant/livekit/token` - Generate a LiveKit access token for a participant to join a room
- `GET /v1/golf-assistant/livekit/rooms` - List all LiveKit rooms
- `GET /v1/golf-assistant/livekit/rooms/{room_name}/participants` - Get participants in a LiveKit room
- `POST /v1/golf-assistant/livekit/webhook` - Handle LiveKit webhook events

### Example Usage

1. Create a new session:
```
POST /v1/golf-assistant/sessions
```

2. Send audio for processing:
```
POST /v1/golf-assistant/audio
Content-Type: multipart/form-data

audio_file: [binary audio data]
session_id: "your-session-id"
```

3. Get a club suggestion:
```
GET /v1/golf-assistant/suggest-club/150
```

4. Create a LiveKit room for real-time communication:
```
POST /v1/golf-assistant/livekit/rooms
Content-Type: application/json

{
  "room_name": "golf-session-123",
  "empty_timeout": 300
}
```

5. Generate a LiveKit token for a participant:
```
POST /v1/golf-assistant/livekit/token
Content-Type: application/json

{
  "room_name": "golf-session-123",
  "participant_name": "Player 1",
  "participant_identity": "player-1-uuid"
}
```

6. List all LiveKit rooms:
```
GET /v1/golf-assistant/livekit/rooms
```

### Auto-generated docs

If you run the code without any changes, you'll find the
[documentation page here](http://localhost:8001/docs). The default username is `docs_user`
and the password is `simple_password`.
