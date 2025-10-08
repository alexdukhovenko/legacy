#!/usr/bin/env python3
"""
Скрипт миграции базы данных для добавления системы аутентификации
"""

import os
import sys
import logging
from pathlib import Path

# Добавляем путь к проекту
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from database.database import SessionLocal, engine
from database.models import Base

logger = logging.getLogger(__name__)

def migrate_database():
    """Миграция базы данных для добавления новых таблиц аутентификации"""
    try:
        logger.info("🔄 Начинаем миграцию базы данных...")
        
        # Создаем все новые таблицы
        Base.metadata.create_all(bind=engine)
        
        logger.info("✅ Миграция базы данных завершена успешно!")
        logger.info("📋 Добавлены новые таблицы:")
        logger.info("   - users (обновлена с полями аутентификации)")
        logger.info("   - user_tokens (JWT токены)")
        logger.info("   - user_logs (логи активности)")
        logger.info("   - user_chat_history (история чатов с контекстом)")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка миграции: {e}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    success = migrate_database()
    if success:
        logger.info("🎉 Миграция завершена успешно!")
        sys.exit(0)
    else:
        logger.error("💥 Миграция завершилась с ошибкой!")
        sys.exit(1)
