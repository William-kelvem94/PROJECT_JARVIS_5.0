import os
import requests
import logging
import base64
from typing import Optional

logger = logging.getLogger(__name__)


class CloudFallback:
    """
    Backup da integraÃ§Ã£o cloud (Gemini).
    Removido do fluxo principal para estabilidade.
    """

    @staticmethod
    def call_gemini(
        prompt: str,
        api_key: str,
        image_path: Optional[str] = None,
        system_prompt: str = "",
    ):
        if not api_key:
            return "Erro: API Key nÃ£o fornecida."

        try:
            inline_data = None
            if image_path and os.path.exists(image_path):
                with open(image_path, "rb") as image_file:
                    image_data = base64.b64encode(image_file.read()).decode("utf-8")
                    inline_data = {"mime_type": "image/png", "data": image_data}

            # Utiliza v1 para estabilidade
            url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"

            parts = [{"text": f"{system_prompt}\n\nComando: {prompt}"}]
            if inline_data:
                parts.append({"inline_data": inline_data})

            payload = {"contents": [{"parts": parts}]}
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()

            data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]

        except Exception as e:
            logger.error(f"Fallback Gemini falhou: {e}")
            return None
