import httpx
import logging
from app.core.config import settings
import base64

logger = logging.getLogger(__name__)


class SpeechService:
    def __init__(self):
        self.openai_client = None
        if settings.OPENAI_API_KEY:
            from openai import AsyncOpenAI
            self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def speech_to_text(self, audio_data: bytes, filename: str = "audio.wav") -> dict:
        if self.openai_client:
            try:
                transcript = await self.openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=(filename, audio_data, "audio/wav"),
                )
                return {"text": transcript.text, "success": True}
            except Exception as e:
                logger.error(f"STT error: {e}")

        return {"text": "", "success": False, "error": "Speech-to-text not available"}

    async def text_to_speech(self, text: str, voice: str = "alloy") -> bytes:
        if self.openai_client:
            try:
                response = await self.openai_client.audio.speech.create(
                    model="tts-1",
                    voice=voice,
                    input=text,
                )
                return response.content
            except Exception as e:
                logger.error(f"TTS error: {e}")

        return b""

    async def get_available_voices(self) -> list[dict]:
        return [
            {"id": "alloy", "name": "Alloy", "description": "Balanced and neutral"},
            {"id": "echo", "name": "Echo", "description": "Warm and expressive"},
            {"id": "fable", "name": "Fable", "description": "British accent, storytelling"},
            {"id": "onyx", "name": "Onyx", "description": "Deep and authoritative"},
            {"id": "nova", "name": "Nova", "description": "Bright and energetic"},
            {"id": "shimmer", "name": "Shimmer", "description": "Soft and calming"},
        ]


speech_service = SpeechService()
