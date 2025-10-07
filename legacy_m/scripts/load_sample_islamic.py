#!/usr/bin/env python3
"""
Скрипт для загрузки примерных исламских данных
"""

import os
import sys
import logging
from datetime import datetime

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import get_db
from database.models import QuranVerse, Hadith, Commentary

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_sample_islamic_data():
    """Загружает примерные исламские данные"""
    try:
        logger.info("📚 Загружаем примерные исламские данные...")
        
        # Получаем сессию базы данных
        db_gen = get_db()
        db = next(db_gen)
        
        # Примерные аяты Корана
        sample_verses = [
            {
                'surah_number': 2,
                'verse_number': 3,
                'arabic_text': 'الَّذِينَ يُؤْمِنُونَ بِالْغَيْبِ وَيُقِيمُونَ الصَّلَاةَ',
                'translation_ru': 'Которые веруют в сокровенное и выстаивают молитву',
                'confession': None
            },
            {
                'surah_number': 2,
                'verse_number': 255,
                'arabic_text': 'اللَّهُ لَا إِلَٰهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ',
                'translation_ru': 'Аллах - нет божества, кроме Него, живущего, сущего',
                'confession': None
            },
            {
                'surah_number': 1,
                'verse_number': 1,
                'arabic_text': 'بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ',
                'translation_ru': 'Во имя Аллаха, Милостивого, Милосердного',
                'confession': None
            },
            {
                'surah_number': 1,
                'verse_number': 2,
                'arabic_text': 'الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ',
                'translation_ru': 'Хвала Аллаху, Господу миров',
                'confession': None
            },
            {
                'surah_number': 1,
                'verse_number': 3,
                'arabic_text': 'الرَّحْمَٰنِ الرَّحِيمِ',
                'translation_ru': 'Милостивому, Милосердному',
                'confession': None
            }
        ]
        
        # Примерные хадисы
        sample_hadiths = [
            {
                'source': 'Бухари',
                'hadith_number': 1,
                'arabic_text': 'إِنَّمَا الأَعْمَالُ بِالنِّيَّاتِ',
                'translation_ru': 'Поистине, дела оцениваются по намерениям',
                'confession': 'sunni'
            },
            {
                'source': 'Муслим',
                'hadith_number': 1,
                'arabic_text': 'مَنْ حَسَّنَ إِسْلَامَهُ',
                'translation_ru': 'Кто улучшил свой ислам',
                'confession': 'sunni'
            },
            {
                'source': 'Аль-Кафи',
                'hadith_number': 1,
                'arabic_text': 'إِنَّمَا الأَعْمَالُ بِالنِّيَّاتِ',
                'translation_ru': 'Поистине, дела оцениваются по намерениям',
                'confession': 'shia'
            }
        ]
        
        # Загружаем аяты
        loaded_verses = 0
        for verse_data in sample_verses:
            # Проверяем, не существует ли уже такой аят
            existing = db.query(QuranVerse).filter(
                QuranVerse.surah_number == verse_data['surah_number'],
                QuranVerse.verse_number == verse_data['verse_number']
            ).first()
            
            if not existing:
                quran_verse = QuranVerse(**verse_data)
                db.add(quran_verse)
                loaded_verses += 1
        
        # Загружаем хадисы
        loaded_hadiths = 0
        for hadith_data in sample_hadiths:
            # Проверяем, не существует ли уже такой хадис
            existing = db.query(Hadith).filter(
                Hadith.source == hadith_data['source'],
                Hadith.hadith_number == hadith_data['hadith_number']
            ).first()
            
            if not existing:
                hadith = Hadith(**hadith_data)
                db.add(hadith)
                loaded_hadiths += 1
        
        db.commit()
        logger.info(f"✅ Загружено {loaded_verses} аятов Корана и {loaded_hadiths} хадисов")
        
    except Exception as e:
        logger.error(f"❌ Ошибка загрузки исламских данных: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    load_sample_islamic_data()
