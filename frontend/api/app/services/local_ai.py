import logging
import threading

logger = logging.getLogger(__name__)


class LocalAI:
    def __init__(self):
        self.pipeline = None
        self.model_loaded = False
        self._load_async()

    def _load_async(self):
        def load():
            try:
                from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
                import torch
                logger.info("Loading local AI model (this happens once)...")
                model_name = "Qwen/Qwen2.5-0.5B-Instruct"
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    torch_dtype=torch.float32,
                    low_cpu_mem_usage=True,
                )
                self.pipeline = pipeline(
                    "text-generation",
                    model=self.model,
                    tokenizer=self.tokenizer,
                    max_new_tokens=256,
                    do_sample=True,
                    temperature=0.7,
                )
                self.model_loaded = True
                logger.info("Local AI model loaded successfully!")
            except Exception as e:
                logger.warning(f"Could not load local model (will use template fallback): {e}")

        thread = threading.Thread(target=load, daemon=True)
        thread.start()

    def generate_response(self, message: str, chat_history: list[dict] = None,
                          model: str = "default") -> str:
        if not self.model_loaded:
            return self._template_fallback(message)

        try:
            chat_history = chat_history or []
            prompt = self._build_prompt(message, chat_history)
            result = self.pipeline(prompt, max_new_tokens=256, do_sample=True, temperature=0.7)
            generated = result[0]["generated_text"]
            response = generated.replace(prompt, "").strip()
            if response:
                return response
            return self._template_fallback(message)
        except Exception as e:
            logger.error(f"Generation error: {e}")
            return self._template_fallback(message)

    def _build_prompt(self, message: str, chat_history: list[dict]) -> str:
        system = (
            "<|im_start|>system\n"
            "Sen Osmanlı Yapay Zeka asistanısın. Osmanlı İmparatorluğu'nun zarafetini ve bilgeliğini "
            "temsil eden, son derece kibar, saygılı ve bilgili bir kâtipsin. "
            "Daima nazik ve saygılı bir üslup kullan. Türkçe konuş.\n"
            "<|im_end|>\n"
        )
        prompt = system
        for msg in chat_history[-4:]:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            prompt += f"<|im_start|>{role}\n{content}<|im_end|>\n"
        prompt += f"<|im_start|>user\n{message}<|im_end|>\n<|im_start|>assistant\n"
        return prompt

    def _template_fallback(self, message: str) -> str:
        msg = message.lower().strip()

        greetings = ["merhaba", "selam", "hello", "hi ", "hey", "assalamualaikum", "salam", "günaydın", "iyi günler"]
        if any(g in msg for g in greetings):
            return "Ve aleyküm selam efendim! Buyurun, size nasıl yardımcı olabilirim?"

        if any(g in msg for g in ["nasılsın", "nasilsin", "how are you"]):
            return "Allah'a şükür, iyiyim efendim. Siz nasılsınız? Size nasıl hizmet edebilirim?"

        if any(g in msg for g in ["adın ne", "adin ne", "kimsin", "your name", "who are you"]):
            return "Ben Osmanlı Yapay Zeka, Osmanlı İmparatorluğu'nun kadim bilgeliğini modern yapay zeka gücüyle birleştiren bir kâtibim. Adımı sorduğunuza göre ilminize taliplisiniz, ne dersiniz?"

        if any(g in msg for g in ["teşekkür", "thanks", "thank", "sağ ol", "sag ol"]):
            return "Estağfurullah efendim. Size yardımcı olabildiysem ne mutlu bana. Her zaman hizmetinizdeyim."

        if any(g in msg for g in ["allah", "hayırlı", "hayirli"]):
            return "Allah razı olsun efendim. Hayırlı işler dilerim."

        if "?" in msg:
            return f"Efendim, sualinize cevaben: {message}"

        return f"Estağfurullah efendim, dediklerinizi anladım. Müsaadenizle şöyle diyeyim: {message}"


local_ai = LocalAI()
