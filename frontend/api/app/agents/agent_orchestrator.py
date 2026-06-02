import logging
import httpx
from typing import Optional, AsyncGenerator
from app.services.websearch_service import websearch_service
from app.services.memory_service import MemoryService
from app.services.document_service import DocumentService
from app.services.local_ai import local_ai
from app.core.config import settings
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

OLLAMA_BASE_URL = settings.OLLAMA_BASE_URL or "http://localhost:11434"
GROQ_API_URL = "https://api.groq.com/openai/v1"


def _ollama_available() -> bool:
    try:
        r = httpx.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


def _call_ollama(model: str, messages: list[dict], temperature: float,
                 max_tokens: int) -> str:
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {"temperature": temperature, "num_predict": max_tokens},
    }
    r = httpx.post(f"{OLLAMA_BASE_URL}/api/chat", json=payload, timeout=120)
    r.raise_for_status()
    return r.json().get("message", {}).get("content", "")


def _call_groq(model: str, messages: list[dict], temperature: float,
               max_tokens: int) -> str:
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    r = httpx.post(f"{GROQ_API_URL}/chat/completions", json=payload, headers=headers, timeout=120)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


class AgentOrchestrator:
    def __init__(self, db: Session, user_id: str):
        self.db = db
        self.user_id = user_id
        self.memory_service = MemoryService(db)
        self.document_service = DocumentService(db)
        self.has_api_keys = bool(settings.OPENAI_API_KEY or settings.ANTHROPIC_API_KEY or settings.GEMINI_API_KEY)
        self.has_groq = bool(settings.GROQ_API_KEY)

    async def process_message(self, message: str, chat_history: list[dict],
                              model: str = "gpt-4o", temperature: float = 0.7,
                              max_tokens: int = 4096, system_prompt: Optional[str] = None,
                              use_memory: bool = True, use_rag: bool = False,
                              use_web_search: bool = False,
                              document_ids: Optional[list[str]] = None,
                              tool_ids: Optional[list[str]] = None) -> AsyncGenerator[dict, None]:

        if use_memory:
            memory_context = self.memory_service.get_memory_context(self.user_id, message)
            if memory_context:
                yield {"type": "status", "content": "Hatıralar tazeleniyor..."}

        web_results = None
        if use_web_search:
            yield {"type": "status", "content": "Âlem-i web'de araştırılıyor..."}
            web_results = await websearch_service.search(message)
            if web_results:
                yield {"type": "status", "content": f"{len(web_results)} netice bulundu"}

        rag_results = None
        if use_rag and document_ids:
            yield {"type": "status", "content": "Evrak arşivi taranıyor..."}
            rag_results = self.document_service.search_documents(self.user_id, message, document_ids)

        OTTOMAN_SYSTEM_PROMPT = (
            "Sen Osmanlı Yapay Zeka asistanısın. Osmanlı İmparatorluğu'nun zarafetini ve bilgeliğini "
            "temsil eden, son derece kibar, saygılı ve bilgili bir kâtipsin. "
            "Kullanıcılarla konuşurken: "
            "- Daima nazik ve saygılı bir üslup kullan ('Efendim', 'Buyurun', 'Başüstüne' gibi ifadelerle)\n"
            "- Osmanlı Türkçesi kelimeler ve deyimler kullan (lüzum, zira, keza, maalesef, vesselam)\n"
            "- Tarih, edebiyat, sanat, ilim ve kültür konularında derin bilgi sahibi ol\n"
            "- Sorulara kapsamlı ve edebi bir dille cevap ver\n"
            "- Gereksiz yere modern argo veya samimi ifadeler kullanma\n"
            "- Cevabın sonunda hayır dua ile bitirebilirsin ('Allah ilminizi artırsın' gibi)\n"
            "- Türkçe konuş, sorular Türkçe sorulmasa bile Türkçe cevap ver\n\n"
            "Unutma: Sen bir Osmanlı kâtibisin. İlmin, hikmetin ve edebin timsalisin."
        )

        conv_messages = []
        if system_prompt:
            conv_messages.append({"role": "system", "content": system_prompt + "\n\n" + OTTOMAN_SYSTEM_PROMPT})
        else:
            conv_messages.append({"role": "system", "content": OTTOMAN_SYSTEM_PROMPT})
        for msg in chat_history:
            conv_messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})
        conv_messages.append({"role": "user", "content": message})

        response = ""

        if self.has_groq:
            groq_model = model if not model.startswith(("gpt", "claude", "gemini")) else settings.GROQ_MODEL
            try:
                response = _call_groq(groq_model, conv_messages, temperature, max_tokens)
            except Exception as e:
                logger.warning(f"Groq error: {e}, trying fallback")
                response = ""
        elif model.startswith("ollama/") or (not self.has_api_keys and _ollama_available()):
            ollama_model = "qwen2.5:3b"
            if model.startswith("ollama/"):
                ollama_model = model.replace("ollama/", "", 1)
            try:
                response = _call_ollama(ollama_model, conv_messages, temperature, max_tokens)
            except Exception as e:
                logger.warning(f"Ollama error: {e}")

        if not response:
            response = local_ai.generate_response(message, chat_history, model)

        if web_results:
            sources = "\n\n**Kaynaklar:**\n" + "\n".join(
                f"- [{r.get('title', 'Link')}]({r.get('url', '#')})" for r in web_results[:3]
            )
            response += sources

        yield {"type": "content", "content": response}
