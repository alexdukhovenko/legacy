#!/usr/bin/env python3
"""
Скрипт для загрузки примерных православных данных
"""

import os
import sys
import logging
from datetime import datetime

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import get_db
from database.models import OrthodoxText, OrthodoxDocument

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_sample_orthodox_data():
    """Загружает примерные православные данные"""
    try:
        logger.info("📚 Загружаем примерные православные данные...")
        
        # Получаем сессию базы данных
        db_gen = get_db()
        db = next(db_gen)
        
        # Примерные православные тексты
        sample_texts = [
            {
                'source_type': 'Библия',
                'book_name': 'Евангелие от Матфея',
                'author': 'Святой Матфей',
                'chapter_number': 6,
                'verse_number': 9,
                'original_text': 'Отче наш, сущий на небесах! да святится имя Твое;',
                'translation_ru': 'Отче наш, сущий на небесах! да святится имя Твое;',
                'commentary': 'Молитва Господня - основа христианской молитвы',
                'theme': 'молитва',
                'confession': 'orthodox'
            },
            {
                'source_type': 'Библия',
                'book_name': 'Евангелие от Матфея',
                'author': 'Святой Матфей',
                'chapter_number': 6,
                'verse_number': 6,
                'original_text': 'Ты же, когда молишься, войди в комнату твою и, затворив дверь твою, помолись Отцу твоему, Который в тайном месте;',
                'translation_ru': 'Ты же, когда молишься, войди в комнату твою и, затворив дверь твою, помолись Отцу твоему, Который в тайном месте;',
                'commentary': 'Иисус учит о важности уединенной молитвы',
                'theme': 'молитва',
                'confession': 'orthodox'
            },
            {
                'source_type': 'Библия',
                'book_name': 'Псалтирь',
                'author': 'Царь Давид',
                'chapter_number': 55,
                'verse_number': 17,
                'original_text': 'Вечером и утром и в полдень буду умолять и вопиять, и Он услышит голос мой,',
                'translation_ru': 'Вечером и утром и в полдень буду умолять и вопиять, и Он услышит голос мой,',
                'commentary': 'Давид показывает важность регулярной молитвы в течение дня',
                'theme': 'молитва',
                'confession': 'orthodox'
            },
            {
                'source_type': 'Святоотеческие труды',
                'book_name': 'Добротолюбие',
                'author': 'Святые отцы',
                'chapter_number': 1,
                'verse_number': 1,
                'original_text': 'Молитва есть возношение ума и сердца к Богу',
                'translation_ru': 'Молитва есть возношение ума и сердца к Богу',
                'commentary': 'Классическое определение молитвы в православной традиции',
                'theme': 'молитва',
                'confession': 'orthodox'
            },
            {
                'source_type': 'Библия',
                'book_name': 'Евангелие от Луки',
                'author': 'Святой Лука',
                'chapter_number': 18,
                'verse_number': 1,
                'original_text': 'Сказал также им притчу о том, что должно всегда молиться и не унывать,',
                'translation_ru': 'Сказал также им притчу о том, что должно всегда молиться и не унывать,',
                'commentary': 'Иисус подчеркивает важность постоянной молитвы',
                'theme': 'молитва',
                'confession': 'orthodox'
            }
        ]
        
        # Загружаем тексты
        loaded_count = 0
        for text_data in sample_texts:
            # Проверяем, не существует ли уже такой текст
            existing = db.query(OrthodoxText).filter(
                OrthodoxText.book_name == text_data['book_name'],
                OrthodoxText.chapter_number == text_data['chapter_number'],
                OrthodoxText.verse_number == text_data['verse_number']
            ).first()
            
            if not existing:
                orthodox_text = OrthodoxText(**text_data)
                db.add(orthodox_text)
                loaded_count += 1
        
        db.commit()
        logger.info(f"✅ Загружено {loaded_count} православных текстов")
        
    except Exception as e:
        logger.error(f"❌ Ошибка загрузки православных данных: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    load_sample_orthodox_data()
