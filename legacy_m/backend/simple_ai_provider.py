import os
import logging
from typing import List, Dict, Any
import openai

logger = logging.getLogger(__name__)

class SimpleAIProvider:
    """Простой AI провайдер только с OpenAI"""
    
    def __init__(self):
        self.client = None
        self.available = False
        self._init_openai()
    
    def _init_openai(self):
        """Инициализация OpenAI"""
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key and api_key != "your_openai_api_key_here":
                self.client = openai.OpenAI(api_key=api_key)
                self.available = True
                logger.info("✅ OpenAI провайдер инициализирован")
            else:
                logger.warning("⚠️ OpenAI API ключ не найден")
                self.available = False
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации OpenAI: {e}")
            self.available = False
    
    def generate_response(self, messages: List[Dict[str, str]], max_tokens: int = 800) -> str:
        """Генерация ответа"""
        if not self.available:
            raise Exception("OpenAI недоступен")
        
        try:
            # Пробуем ANTHROPIC CLAUDE-3.5-SONNET
            import anthropic
            
            anthropic_key = os.getenv("ANTHROPIC_API_KEY")
            if not anthropic_key:
                raise Exception("ANTHROPIC_API_KEY не найден")
            
            client = anthropic.Anthropic(api_key=anthropic_key)
            
            # Конвертируем сообщения для Claude
            system_msg = ""
            user_msg = ""
            
            for msg in messages:
                if msg["role"] == "system":
                    system_msg = msg["content"]
                elif msg["role"] == "user":
                    user_msg = msg["content"]
            
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=max_tokens,
                system=system_msg,
                messages=[{"role": "user", "content": user_msg}]
            )
            return response.content[0].text
        except Exception as e:
            logger.warning(f"Anthropic недоступен, пробуем GPT-4o: {e}")
            try:
                # Fallback на GPT-4o с стандартными параметрами
                response = self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=0.3
                )
                return response.choices[0].message.content.strip()
            except Exception as e2:
                logger.error(f"❌ Ошибка OpenAI (GPT-4o fallback): {e2}")
                raise

# Глобальный экземпляр
simple_ai_provider = SimpleAIProvider()
