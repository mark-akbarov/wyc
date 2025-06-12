# 🧠 Hey Ceddy - AI Voice Golf Assistant (MVP TODO)

This project is a voice-activated assistant for helping golf players make better in-game decisions. Users trigger the assistant with "Hey Ceddy" and receive real-time coaching through voice.

---

## ✅ Tech Stack

- **Frontend**: React (Vite or CRA) + LiveKit Client SDK + Web Audio API
- **Backend**: FastAPI (Dockerized) + PostgreSQL
- **Voice/AI**: OpenAI Assistants API, Whisper API, (optional: ElevenLabs TTS)
- **Streaming**: LiveKit Cloud (free tier for dev)
- **Hosting**: Vercel (React), Railway/Fly.io/Render (FastAPI)

---

## 🚀 MVP TODO List

### 📦 Project Setup

- [ ] Set up FastAPI backend with Docker
- [ ] Set up PostgreSQL (local or cloud)
- [ ] Set up React frontend with audio recording capability
- [ ] Create `.env` files with API keys for:
  - OpenAI
  - ElevenLabs (optional)
  - LiveKit (Cloud key + secret)

---

### 🎙️ Audio Flow (LiveKit)

- [ ] Set up LiveKit Cloud project
- [ ] Add LiveKit client to React project
- [ ] Join LiveKit room and capture mic audio
- [ ] Stream audio to FastAPI backend

---

### 🧠 AI Integration

- [ ] Add FastAPI endpoint to receive and buffer audio stream
- [ ] Integrate OpenAI Whisper API for transcription
- [ ] Add wake word detection: “Hey Ceddy” (basic text match)
- [ ] Create OpenAI Assistant with golf coaching context
- [ ] Connect transcribed prompt → OpenAI Assistant → get response

---

### 🔊 Voice Response

- [ ] Integrate TTS (e.g. ElevenLabs or Google TTS) to convert reply to audio
- [ ] Return audio file/stream to React client
- [ ] Play response using Web Audio API

---

### 🧩 Golf Logic (Coaching)

- [ ] Define a few assistant functions like:
  - `suggest_club(distance: float) -> str`
  - `check_wind_conditions() -> str`
- [ ] Use OpenAI Assistant function calling to call these when needed

---

### 💾 Optional (Post-MVP Enhancements)

- [ ] Add user profiles + sessions
- [ ] Save transcripts and responses in PostgreSQL
- [ ] Add a feedback or rating option after each response
- [ ] Enable multi-user rooms (group coaching) via LiveKit

---

### 🔧 Dev Utilities

- [ ] Create OpenAI Assistant with golf instructions
- [ ] Create reusable audio stream handler
- [ ] Add loading/recording states in React UI
- [ ] Write unit tests for backend logic

---

## 🧪 Example Prompts

- “Hey Ceddy, what club should I use for 150 yards?”
- “What’s the wind like today?”
- “Give me a golf swing tip.”

---

## 🧠 Assistant Prompt Template

> You are Ceddy, an AI golf coach helping players during games. Suggest golf clubs, analyze environmental conditions, and give concise golf tips. Respond only when the player says "Hey Ceddy."

---

## 📍 Milestone Plan

| Week | Goal |
|------|------|
| 1    | Set up basic frontend/backend + audio recording |
| 2    | LiveKit integration + Whisper transcription |
| 3    | Connect to OpenAI Assistant + return reply |
| 4    | Add TTS + playback | 
| 5    | Add golf-specific logic + function calling |
| 6    | Test with real users and refine UX |

