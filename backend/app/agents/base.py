import json
import httpx
from typing import Dict, Any, Optional
from app.config import settings

class BaseAgent:
    """Base AI agent with provider abstraction (OpenAI, Gemini, Ollama, Heuristic)."""
    def __init__(self, name: str, role_description: str):
        self.name = name
        self.role_description = role_description
        self.provider = settings.LLM_PROVIDER.lower()
        self.model = settings.LLM_MODEL
        self.api_key = settings.LLM_API_KEY

    def call_llm(self, prompt: str, system_message: Optional[str] = None) -> str:
        """Call LLM provider or fallback to domain heuristic reasoning engine."""
        sys_msg = system_message or f"You are {self.name}, an expert AI research agent for Healthcare Research."

        if self.provider == "openai" and self.api_key:
            try:
                headers = {"Authorization": f"Bearer {self.api_key}"}
                payload = {
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": sys_msg},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.2
                }
                res = httpx.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers, timeout=20.0)
                if res.status_code == 200:
                    return res.json()["choices"][0]["message"]["content"]
            except Exception:
                pass

        if self.provider == "gemini" and self.api_key:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
                payload = {
                    "contents": [{"parts": [{"text": f"{sys_msg}\n\n{prompt}"}]}]
                }
                res = httpx.post(url, json=payload, timeout=20.0)
                if res.status_code == 200:
                    return res.json()["candidates"][0]["content"]["parts"][0]["text"]
            except Exception:
                pass

        # Return None so child agents execute their deterministic domain-specific heuristics
        return None
