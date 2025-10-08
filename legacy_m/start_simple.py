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
        
        # Загрузка простых данных
        print("📚 Loading simple data...")
        from scripts.load_simple_data import load_simple_data
        load_simple_data()
        print("✅ Simple data loaded")
        
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
