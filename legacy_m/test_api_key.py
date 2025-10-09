#!/usr/bin/env python3
"""
Скрипт для тестирования API ключа в Render
"""

import os
import sys
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_api_key():
    logger.info("🔍 ТЕСТИРУЕМ API КЛЮЧ В RENDER...")
    
    # Получаем API ключ
    openai_key = os.getenv("OPENAI_API_KEY")
    
    if not openai_key:
        logger.error("❌ OPENAI_API_KEY НЕ НАЙДЕН!")
        return False
    
    logger.info(f"✅ API ключ найден!")
    logger.info(f"📏 Длина ключа: {len(openai_key)}")
    logger.info(f"🔤 Начинается с: {openai_key[:15]}...")
    logger.info(f"🔚 Заканчивается на: ...{openai_key[-15:]}")
    
    # Проверяем формат
    if openai_key.startswith("sk-proj-"):
        logger.info("✅ Формат ключа правильный (sk-proj-)")
    else:
        logger.error(f"❌ Неправильный формат ключа! Начинается с: {openai_key[:10]}")
        return False
    
    # Тестируем подключение к OpenAI
    try:
        import openai
        client = openai.OpenAI(api_key=openai_key)
        
        # Простой тест
        response = client.chat.completions.create(
            model="gpt-5",
            messages=[{"role": "user", "content": "Привет"}],
            max_completion_tokens=10
        )
        
        logger.info("✅ OpenAI API работает!")
        logger.info(f"📝 Ответ: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка OpenAI API: {e}")
        return False

if __name__ == "__main__":
    success = test_api_key()
    if success:
        logger.info("🎉 ВСЕ РАБОТАЕТ!")
        sys.exit(0)
    else:
        logger.error("💥 ПРОБЛЕМА С API!")
        sys.exit(1)
