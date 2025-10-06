#!/bin/bash

# Скрипт запуска LEGACY M

echo "🚀 Запуск LEGACY M - Исламский ИИ-Наставник"
echo "=============================================="

# Проверяем наличие Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не найден. Установите Python 3.8+"
    exit 1
fi

# Проверяем наличие pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 не найден. Установите pip"
    exit 1
fi

# Устанавливаем зависимости
echo "📦 Установка зависимостей..."
pip3 install -r requirements.txt

# Инициализируем базу данных
echo "🗄️ Инициализация базы данных..."
python3 init_db.py

# Загружаем данные Корана
echo "📖 Загрузка данных Корана..."
python3 scripts/load_quran_data.py

# Запускаем сервер
echo "🌐 Запуск сервера..."
echo "📍 Сервер будет доступен по адресу: http://localhost:8000"
echo "💬 Чат доступен по адресу: http://localhost:8000/frontend/index.html"
echo "📚 API документация: http://localhost:8000/docs"
echo ""
echo "Для остановки сервера нажмите Ctrl+C"
echo ""

python3 backend/main.py
