#!/usr/bin/env python3
"""
Скрипт для принудительного перезапуска с проверкой переменных окружения
"""

import os
import sys
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_environment():
    """Проверяем переменные окружения"""
    logger.info("🔍 Проверяем переменные окружения...")
    
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    environment = os.getenv("ENVIRONMENT")
    
    logger.info(f"OPENAI_API_KEY: {'✅ Найден' if openai_key and openai_key != 'your_openai_api_key_here' else '❌ Не найден'}")
    logger.info(f"ANTHROPIC_API_KEY: {'✅ Найден' if anthropic_key and anthropic_key != 'your_anthropic_api_key_here' else '❌ Не найден'}")
    logger.info(f"ENVIRONMENT: {environment}")
    
    if openai_key and openai_key != 'your_openai_api_key_here':
        logger.info(f"OpenAI ключ начинается с: {openai_key[:10]}...")
        return True
    else:
        logger.error("❌ OpenAI API ключ не найден или неправильный!")
        return False

def main():
    """Основная функция"""
    logger.info("🚀 Принудительный перезапуск с проверкой...")
    
    if check_environment():
        logger.info("✅ Переменные окружения в порядке, запускаем приложение...")
        
        # Добавляем путь к проекту
        project_root = os.path.dirname(os.path.abspath(__file__))
        sys.path.append(project_root)
        
        # Запускаем основное приложение
        from start_simple import main as start_app
        start_app()
    else:
        logger.error("❌ Переменные окружения не настроены!")
        sys.exit(1)

if __name__ == "__main__":
    main()
