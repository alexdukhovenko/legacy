#!/usr/bin/env python3
"""
Скрипт для инициализации базы данных в продакшене
"""

import os
import sys
import logging
from pathlib import Path

# Добавляем путь к проекту
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from database.database import init_database
from scripts.load_quran_data import main as load_quran

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Инициализация базы данных и загрузка данных"""
    try:
        logger.info("🚀 Начинаем инициализацию базы данных...")
        
        # Инициализируем базу данных
        logger.info("📊 Инициализация базы данных...")
        init_database()
        logger.info("✅ База данных инициализирована")
        
        # Загружаем только доступные данные
        logger.info("📚 Загрузка данных Корана...")
        load_quran()
        logger.info("✅ Данные Корана загружены")
        
        # Православные тексты будут загружены позже, когда файлы будут добавлены в репозиторий
        logger.info("ℹ️ Православные тексты пропущены - файлы не найдены в репозитории")
        
        logger.info("🎉 Инициализация завершена успешно!")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при инициализации: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
