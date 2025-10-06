#!/usr/bin/env python3
"""
Скрипт инициализации базы данных LEGACY M
"""

import sys
import os

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import init_database
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Основная функция инициализации"""
    try:
        logger.info("🚀 Начинаем инициализацию базы данных LEGACY M...")
        
        # Инициализируем базу данных
        init_database()
        
        logger.info("✅ База данных успешно инициализирована!")
        logger.info("📝 Структура готова для загрузки священных текстов")
        logger.info("🔧 Для запуска сервера выполните: python backend/main.py")
        
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
