#!/usr/bin/env python3
"""
Простой скрипт запуска для Render
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    print("🚀 Starting LEGACY M...")
    
    # Добавляем путь к проекту
    project_root = Path(__file__).parent
    sys.path.append(str(project_root))
    
    try:
        # Инициализация базы данных
        print("📊 Initializing database...")
        from database.database import init_database
        init_database()
        print("✅ Database initialized")
        
        # Миграция для системы аутентификации
        print("🔐 Running authentication migration...")
        from scripts.migrate_auth import migrate_database
        migrate_database()
        print("✅ Authentication migration completed")
        
        # Загрузка простых данных
        print("📚 Loading simple data...")
        from scripts.load_simple_data import load_simple_data
        load_simple_data()
        print("✅ Simple data loaded")
        
        # Загрузка расширенных православных данных
        print("📚 Loading extended Orthodox data...")
        from scripts.load_extended_data import load_extended_orthodox_data
        load_extended_orthodox_data()
        print("✅ Extended Orthodox data loaded")
        
        # Проверяем количество загруженных данных
        print("🔍 Checking loaded data...")
        from database.database import SessionLocal
        from database.models import QuranVerse, Hadith, OrthodoxText
        
        db = SessionLocal()
        try:
            quran_count = db.query(QuranVerse).count()
            hadith_count = db.query(Hadith).count()
            orthodox_count = db.query(OrthodoxText).count()
            
            print(f"📊 Loaded documents: Quran={quran_count}, Hadith={hadith_count}, Orthodox={orthodox_count}")
            print(f"📊 TOTAL={quran_count + hadith_count + orthodox_count}")
            
            # КРИТИЧЕСКАЯ ПРОВЕРКА
            if orthodox_count < 10:
                print(f"🚨 CRITICAL: Only {orthodox_count} Orthodox texts loaded! Expected 750+.")
                print("🚨 This will cause search to return only 3 results!")
                print("🚨 Check data loading scripts and database connection!")
            else:
                print(f"✅ Orthodox texts: {orthodox_count} (OK)")
                
        finally:
            db.close()
        
        print("✅ Initialization completed successfully!")
        
    except Exception as e:
        print(f"❌ Initialization error: {e}")
        # НЕ завершаем процесс, продолжаем запуск приложения
    
    # Запускаем приложение
    print("🌐 Starting FastAPI application...")
    
    # Получаем порт
    port = os.getenv("PORT", "8000")
    host = "0.0.0.0"
    
    # Запускаем uvicorn
    import uvicorn
    from backend.main import app
    
    uvicorn.run(
        app,
        host=host,
        port=int(port),
        access_log=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()
