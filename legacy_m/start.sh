#!/bin/bash

echo "🚀 Starting LEGACY M deployment..."

# Инициализация базы данных
echo "📊 Initializing database..."
python init_production.py

# Проверяем, что инициализация прошла успешно
if [ $? -eq 0 ]; then
    echo "✅ Database initialization completed"
else
    echo "❌ Database initialization failed"
    exit 1
fi

# Запускаем приложение
echo "🌐 Starting application..."
python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT

echo "🎯 Application started successfully"