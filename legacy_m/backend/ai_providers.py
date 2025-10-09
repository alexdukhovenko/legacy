"""
Модуль для работы с различными AI провайдерами
"""

import os
import logging
from typing import Dict, Any, List
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class AIProvider(ABC):
    """Базовый класс для AI провайдеров"""
    
    @abstractmethod
    def generate_response(self, messages: List[Dict[str, str]], max_tokens: int = 800) -> str:
        pass

class OpenAIProvider(AIProvider):
    """OpenAI провайдер"""
    
    def __init__(self):
        try:
            import openai
            self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            self.available = True
        except Exception as e:
            logger.error(f"OpenAI недоступен: {e}")
            self.available = False
    
    def generate_response(self, messages: List[Dict[str, str]], max_tokens: int = 800) -> str:
        if not self.available:
            raise Exception("OpenAI недоступен")
        
        try:
            # Пробуем GPT-5 с правильными параметрами
            response = self.client.chat.completions.create(
                model="gpt-5",
                messages=messages,
                max_completion_tokens=max_tokens,
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.warning(f"GPT-5 недоступна, пробуем GPT-4o: {e}")
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
                logger.error(f"Ошибка OpenAI (GPT-4o fallback): {e2}")
                raise

class AnthropicProvider(AIProvider):
    """Anthropic Claude провайдер"""
    
    def __init__(self):
        try:
            import anthropic
            # Используем новую версию API
            self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            self.available = True
        except Exception as e:
            logger.error(f"Anthropic недоступен: {e}")
            self.available = False
    
    def generate_response(self, messages: List[Dict[str, str]], max_tokens: int = 800) -> str:
        if not self.available:
            raise Exception("Anthropic недоступен")
        
        try:
            # Конвертируем сообщения для Claude
            system_msg = ""
            user_msg = ""
            
            for msg in messages:
                if msg["role"] == "system":
                    system_msg = msg["content"]
                elif msg["role"] == "user":
                    user_msg = msg["content"]
            
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=max_tokens,
                system=system_msg,
                messages=[{"role": "user", "content": user_msg}]
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Ошибка Anthropic: {e}")
            raise

class LocalProvider(AIProvider):
    """Локальный AI провайдер (Ollama)"""
    
    def __init__(self):
        try:
            import requests
            self.base_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
            self.model = os.getenv("OLLAMA_MODEL", "llama2")
            self.available = True
        except Exception as e:
            logger.error(f"Ollama недоступен: {e}")
            self.available = False
    
    def generate_response(self, messages: List[Dict[str, str]], max_tokens: int = 800) -> str:
        if not self.available:
            raise Exception("Ollama недоступен")
        
        try:
            import requests
            
            # Конвертируем сообщения для Ollama
            prompt = ""
            for msg in messages:
                if msg["role"] == "system":
                    prompt += f"System: {msg['content']}\n\n"
                elif msg["role"] == "user":
                    prompt += f"User: {msg['content']}\n\n"
            
            prompt += "Assistant:"
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": max_tokens,
                        "temperature": 0.3
                    }
                }
            )
            
            if response.status_code == 200:
                return response.json()["response"].strip()
            else:
                raise Exception(f"Ошибка Ollama: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Ошибка Ollama: {e}")
            raise

class AIProviderManager:
    """Менеджер AI провайдеров с fallback"""
    
    def __init__(self):
        self.providers = [
            AnthropicProvider(),  # ANTHROPIC ПЕРВЫМ!
            OpenAIProvider(),
            LocalProvider()
        ]
    
    def generate_response(self, messages: List[Dict[str, str]], max_tokens: int = 800) -> str:
        """Генерирует ответ, пробуя провайдеров по очереди"""
        
        for provider in self.providers:
            if provider.available:
                try:
                    logger.info(f"Пробуем провайдер: {type(provider).__name__}")
                    response = provider.generate_response(messages, max_tokens)
                    logger.info(f"Успешно использован провайдер: {type(provider).__name__}")
                    return response
                except Exception as e:
                    logger.warning(f"Провайдер {type(provider).__name__} не сработал: {e}")
                    continue
        
        # Если все провайдеры недоступны
        raise Exception("Все AI провайдеры недоступны")

# Глобальный экземпляр менеджера
ai_manager = AIProviderManager()
