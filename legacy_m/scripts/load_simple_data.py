#!/usr/bin/env python3
"""
Простой загрузчик данных без сложных зависимостей
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime

# Добавляем путь к проекту
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from database.database import SessionLocal
from database.models import QuranVerse, Hadith, OrthodoxText

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_simple_data():
    """Загружаем простые данные для всех конфессий"""
    db = SessionLocal()
    try:
        logger.info("🚀 Начинаем загрузку простых данных...")
        
        # Проверяем, есть ли уже данные
        if db.query(QuranVerse).count() > 0:
            logger.info("✅ Данные уже загружены")
            return
        
        # Загружаем Коран
        logger.info("📖 Загружаем Коран...")
        quran_verses = [
            QuranVerse(
                surah_number=1, verse_number=1,
                arabic_text="بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ",
                translation_ru="Во имя Аллаха, Милостивого, Милосердного!",
                commentary="Начало каждой суры Корана.",
                confession='sunni'
            ),
            QuranVerse(
                surah_number=2, verse_number=3,
                arabic_text="الَّذِينَ يُؤْمِنُونَ بِالْغَيْبِ وَيُقِيمُونَ الصَّلَاةَ وَمِمَّا رَزَقْنَاهُمْ يُنفِقُونَ",
                translation_ru="которые веруют в сокровенное, совершают намаз и расходуют из того, чем Мы их наделили.",
                commentary="Описание качеств богобоязненных.",
                confession='sunni'
            ),
            QuranVerse(
                surah_number=1, verse_number=1,
                arabic_text="بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ",
                translation_ru="Во имя Аллаха, Милостивого, Милосердного!",
                commentary="Начало каждой суры Корана.",
                confession='shia'
            )
        ]
        db.add_all(quran_verses)
        
        # Загружаем хадисы
        logger.info("📜 Загружаем хадисы...")
        hadiths = [
            Hadith(
                collection="Бухари",
                hadith_number=1,
                arabic_text="إنما الأعمال بالنيات",
                translation_ru="Поистине, дела (оцениваются) только по намерениям.",
                commentary="Один из самых важных хадисов в исламе.",
                confession='sunni'
            ),
            Hadith(
                collection="Аль-Кафи",
                hadith_number=1,
                arabic_text="عن أبي عبد الله عليه السلام قال: دعائم الكفر ثلاثة: الحرص والاستكبار والحسد",
                translation_ru="От Абу Абдуллаха (мир ему) передано: Столпов неверия три: алчность, высокомерие и зависть.",
                commentary="Основы неверия в шиитском исламе.",
                confession='shia'
            )
        ]
        db.add_all(hadiths)
        
        # Загружаем православные тексты
        logger.info("⛪ Загружаем православные тексты...")
        orthodox_texts = [
            OrthodoxText(
                source_type='Библия',
                book_name='Евангелие от Матфея',
                chapter_number=6,
                verse_number=9,
                original_text='Отче наш, сущий на небесах! да святится имя Твое;',
                translation_ru='Отче наш, сущий на небесах! да святится имя Твое;',
                commentary='Начало молитвы Господней.',
                theme='Молитва',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Библия',
                book_name='Послание к Евреям',
                chapter_number=11,
                verse_number=1,
                original_text='Вера же есть осуществление ожидаемого и уверенность в невидимом.',
                translation_ru='Вера же есть осуществление ожидаемого и уверенность в невидимом.',
                commentary='Определение веры в христианстве.',
                theme='Вера',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='Лествица',
                author='Преподобный Иоанн Лествичник',
                chapter_number=28,
                verse_number=1,
                original_text='Молитва есть возношение ума к Богу.',
                translation_ru='Молитва есть возношение ума к Богу.',
                commentary='Краткое определение молитвы.',
                theme='Молитва',
                confession='orthodox'
            )
        ]
        db.add_all(orthodox_texts)
        
        db.commit()
        logger.info(f"✅ Загружено: {len(quran_verses)} аятов, {len(hadiths)} хадисов, {len(orthodox_texts)} православных текстов")
        
    except Exception as e:
        logger.error(f"❌ Ошибка загрузки данных: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    load_simple_data()
