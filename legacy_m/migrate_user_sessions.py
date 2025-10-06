#!/usr/bin/env python3
"""
Миграция для добавления поля confession в таблицу UserSession
"""

import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.database import DATABASE_URL

def migrate_user_sessions():
    """Добавляет поле confession в таблицу UserSession"""
    
    # Создаем подключение к базе данных
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # Проверяем, существует ли уже поле confession
        result = conn.execute(text("""
            PRAGMA table_info(user_sessions);
        """))
        
        columns = [row[1] for row in result.fetchall()]
        
        if 'confession' not in columns:
            print("Добавляем поле confession в таблицу user_sessions...")
            
            # Добавляем поле confession
            conn.execute(text("""
                ALTER TABLE user_sessions 
                ADD COLUMN confession VARCHAR(50);
            """))
            
            # Создаем индекс для поля confession
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_user_sessions_confession 
                ON user_sessions(confession);
            """))
            
            # Устанавливаем значение 'sunni' для всех существующих сессий
            conn.execute(text("""
                UPDATE user_sessions 
                SET confession = 'sunni' 
                WHERE confession IS NULL;
            """))
            
            conn.commit()
            print("✅ Поле confession успешно добавлено в таблицу user_sessions")
        else:
            print("✅ Поле confession уже существует в таблице user_sessions")
        
        # Проверяем структуру таблицы
        result = conn.execute(text("""
            PRAGMA table_info(user_sessions);
        """))
        
        print("\nСтруктура таблицы user_sessions:")
        for row in result.fetchall():
            print(f"  {row[1]} - {row[2]}")

if __name__ == "__main__":
    migrate_user_sessions()
