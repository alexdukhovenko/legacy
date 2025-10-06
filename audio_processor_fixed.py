#!/usr/bin/env python3
"""
Улучшенный аудио процессор с обработкой ошибок Whisper API
"""

import logging
import asyncio
import os
import tempfile
from typing import Optional, Dict, Any
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

class AudioProcessorFixed:
    """Улучшенный аудио процессор с обработкой ошибок"""
    
    def __init__(self):
        self.max_file_size = 20 * 1024 * 1024  # 20MB
        self.max_duration = 25 * 60  # 25 минут
        
    async def process_audio_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> Optional[str]:
        """
        Обрабатывает аудиосообщение с улучшенной обработкой ошибок
        """
        try:
            # Получаем файл
            audio_file = await self._get_audio_file(update)
            if not audio_file:
                return "Не удалось получить аудиофайл"
            
            # Проверяем размер файла
            if audio_file.file_size > self.max_file_size:
                return "Аудио слишком длинное. Максимум 20MB."
            
            # Скачиваем файл
            file_path = await self._download_audio_file(audio_file, context)
            if not file_path:
                return "Ошибка скачивания аудиофайла"
            
            try:
                # Пытаемся обработать через Whisper
                text = await self._process_with_whisper(file_path)
                if text:
                    return text
                
                # Если Whisper не работает, предлагаем альтернативы
                return await self._handle_whisper_error()
                
            finally:
                # Удаляем временный файл
                if os.path.exists(file_path):
                    os.remove(file_path)
                    
        except Exception as e:
            logger.error(f"Error processing audio: {e}")
            return f"Ошибка обработки аудио: {str(e)}"
    
    async def _get_audio_file(self, update: Update):
        """Получает аудиофайл из сообщения"""
        if update.message.voice:
            return update.message.voice
        elif update.message.audio:
            return update.message.audio
        elif update.message.video_note:
            return update.message.video_note
        return None
    
    async def _download_audio_file(self, audio_file, context: ContextTypes.DEFAULT_TYPE) -> Optional[str]:
        """Скачивает аудиофайл во временную папку"""
        try:
            # Создаем временный файл
            temp_dir = tempfile.gettempdir()
            file_path = os.path.join(temp_dir, f"audio_{audio_file.file_id}.ogg")
            
            # Скачиваем файл
            file = await context.bot.get_file(audio_file.file_id)
            await file.download_to_drive(file_path)
            
            return file_path
            
        except Exception as e:
            logger.error(f"Error downloading audio file: {e}")
            return None
    
    async def _process_with_whisper(self, file_path: str) -> Optional[str]:
        """Обрабатывает аудио через Whisper API"""
        try:
            from openai import AsyncOpenAI
            from config import OPENAI_API_KEY
            
            client = AsyncOpenAI(api_key=OPENAI_API_KEY)
            
            with open(file_path, "rb") as audio_file:
                response = await client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="ru"  # Указываем русский язык
                )
            
            return response.text.strip()
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Whisper API error: {error_msg}")
            
            # Проверяем тип ошибки
            if "unsupported_country_region_territory" in error_msg:
                return None  # Специальная обработка для региональных ограничений
            elif "rate_limit" in error_msg.lower():
                return "Превышен лимит запросов к Whisper API. Попробуй позже."
            elif "invalid_request" in error_msg.lower():
                return "Некорректный запрос к Whisper API."
            else:
                return None  # Другие ошибки - пробуем альтернативы
    
    async def _handle_whisper_error(self) -> str:
        """Обрабатывает ошибки Whisper API и предлагает альтернативы"""
        return """
❌ **Whisper API недоступен в твоем регионе**

**Альтернативы:**

1. **Напиши текстом** - просто отправь сообщение текстом
2. **Используй встроенное распознавание** - запиши голосовое в Telegram и скопируй текст
3. **Разбей на части** - отправь короткие голосовые сообщения

**Или попробуй:**
• Переформулировать задачу текстом
• Использовать команду `/test <задача>` для проверки

Бот работает с текстовыми сообщениями без ограничений! 🚀
        """
    
    async def process_text_fallback(self, text: str) -> str:
        """Обрабатывает текст как fallback для аудио"""
        return f"Обработано как текст: {text}"


# Тест процессора
async def test_audio_processor():
    """Тестирует аудио процессор"""
    processor = AudioProcessorFixed()
    
    # Тест обработки ошибки Whisper
    error_response = await processor._handle_whisper_error()
    print("🧪 Тест обработки ошибки Whisper:")
    print(error_response)

if __name__ == "__main__":
    asyncio.run(test_audio_processor())
