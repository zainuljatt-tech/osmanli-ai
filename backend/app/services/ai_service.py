from typing import Optional
from app.core.config import settings
import json
import httpx
import logging

logger = logging.getLogger(__name__)


class AIService:
    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        self.gemini_client = None
        self._init_clients()

    def _init_clients(self):
        if settings.OPENAI_API_KEY:
            from openai import OpenAI
            self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        if settings.ANTHROPIC_API_KEY:
            import anthropic
            self.anthropic_client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        if settings.GEMINI_API_KEY:
            import google.generativeai as genai
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.gemini_client = genai

    def generate_embedding(self, text: str, model: str = "text-embedding-3-small") -> list[float]:
        if not self.openai_client:
            return [0.0] * 1536
        try:
            resp = self.openai_client.embeddings.create(model=model, input=text)
            return resp.data[0].embedding
        except Exception as e:
            logger.error(f"Embedding error: {e}")
            return [0.0] * 1536

    def generate_title(self, message: str) -> str:
        try:
            resp = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Generate a concise Turkish title (max 6 words) for this conversation. Return only the title, no quotes."},
                    {"role": "user", "content": message},
                ],
                max_tokens=20,
            )
            return resp.choices[0].message.content.strip().strip('"')
        except Exception:
            return "Yeni Sohbet"


ai_service = AIService()
