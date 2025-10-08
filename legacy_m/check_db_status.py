#!/usr/bin/env python3
"""
Скрипт для проверки статуса базы данных
"""

import os
import sys
from sqlalchemy.orm import Session

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.database import get_db
from database.models import QuranVerse, Hadith, Commentary, OrthodoxText, OrthodoxDocument

def check_database_status():
    """Проверяет статус базы данных"""
    try:
        print("🔍 Проверяем статус базы данных...")
        
        # Получаем сессию базы данных
        db_gen = get_db()
        db = next(db_gen)
        
        # Проверяем таблицы
        print("\n📊 СТАТИСТИКА БАЗЫ ДАННЫХ:")
        
        # Коран
        quran_count = db.query(QuranVerse).count()
        print(f"📖 Аятов Корана: {quran_count}")
        
        # Хадисы
        hadith_count = db.query(Hadith).count()
        print(f"📜 Хадисов: {hadith_count}")
        
        # Комментарии
        commentary_count = db.query(Commentary).count()
        print(f"💭 Комментариев: {commentary_count}")
        
        # Православные тексты
        orthodox_count = db.query(OrthodoxText).count()
        print(f"⛪ Православных текстов: {orthodox_count}")
        
        # Православные документы
        orthodox_docs_count = db.query(OrthodoxDocument).count()
        print(f"📚 Православных документов: {orthodox_docs_count}")
        
        # Показываем примеры
        if quran_count > 0:
            print(f"\n📖 ПРИМЕР АЯТА КОРАНА:")
            verse = db.query(QuranVerse).first()
            print(f"Сура {verse.surah_number}, аят {verse.verse_number}: {verse.translation_ru[:100]}...")
        
        if orthodox_count > 0:
            print(f"\n⛪ ПРИМЕР ПРАВОСЛАВНОГО ТЕКСТА:")
            text = db.query(OrthodoxText).first()
            print(f"{text.book_name}: {text.translation_ru[:100]}...")
        
        if hadith_count > 0:
            print(f"\n📜 ПРИМЕР ХАДИСА:")
            hadith = db.query(Hadith).first()
            print(f"{hadith.source} #{hadith.hadith_number}: {hadith.translation_ru[:100]}...")
        
        # Диагностика
        total_records = quran_count + hadith_count + orthodox_count
        print(f"\n📈 ОБЩАЯ СТАТИСТИКА:")
        print(f"Всего записей в базе: {total_records}")
        
        if total_records == 0:
            print("❌ БАЗА ДАННЫХ ПУСТАЯ!")
            print("Нужно загрузить данные из файлов.")
        elif total_records < 10:
            print("⚠️ БАЗА ДАННЫХ СОДЕРЖИТ МАЛО ДАННЫХ!")
            print("Возможно, загружены только примерные данные.")
        else:
            print("✅ БАЗА ДАННЫХ СОДЕРЖИТ ДОСТАТОЧНО ДАННЫХ!")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Ошибка проверки базы данных: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_database_status()
