#!/usr/bin/env python3
"""
Скрипт для загрузки данных Корана в базу данных LEGACY M
"""

import sys
import os
import json
import re
from pathlib import Path

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db, QuranVerse, Commentary, VectorEmbedding
from backend.simple_ai_agent import SimpleIslamicAIAgent
from sqlalchemy.orm import Session
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QuranDataLoader:
    """Класс для загрузки данных Корана"""
    
    def __init__(self, db: Session):
        self.db = db
        self.ai_agent = SimpleIslamicAIAgent(db)
    
    def load_from_html(self, html_file_path: str):
        """Загрузка данных из HTML файла"""
        try:
            logger.info(f"📖 Загружаем данные из {html_file_path}")
            
            # Используем парсер HTML
            from parse_quran_html import QuranHTMLParser
            
            parser = QuranHTMLParser(html_file_path)
            verses_data = parser.parse()
            
            loaded_count = 0
            for verse_data in verses_data:
                # Проверяем, не существует ли уже такой аят
                existing = self.db.query(QuranVerse).filter(
                    QuranVerse.surah_number == verse_data["surah_number"],
                    QuranVerse.verse_number == verse_data["verse_number"]
                ).first()
                
                if not existing:
                    quran_verse = QuranVerse(**verse_data)
                    self.db.add(quran_verse)
                    self.db.flush()
                    
                    # Создаем эмбеддинги
                    self.ai_agent.add_text_to_database(
                        verse_data["arabic_text"], 
                        'quran', 
                        quran_verse.id
                    )
                    
                    if verse_data.get("translation_ru"):
                        self.ai_agent.add_text_to_database(
                            verse_data["translation_ru"], 
                            'quran', 
                            quran_verse.id
                        )
                    
                    loaded_count += 1
            
            self.db.commit()
            logger.info(f"✅ Загружено {loaded_count} новых аятов из HTML")
            
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки HTML: {e}")
            self.db.rollback()
    
    def load_from_doc(self, doc_file_path: str):
        """Загрузка данных из DOC файла"""
        try:
            logger.info(f"📄 Загружаем данные из {doc_file_path}")
            
            # Для DOC файлов нужна библиотека python-docx
            # Пока создаем заглушку
            logger.warning("⚠️ Загрузка DOC файлов требует python-docx. Пропускаем.")
            
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки DOC: {e}")
    
    def load_sample_data(self):
        """Загрузка примерных данных для тестирования"""
        try:
            logger.info("📝 Загружаем примерные данные для тестирования")
            
            # Примерные аяты Корана
            sample_verses = [
                {
                    "surah_number": 1,
                    "verse_number": 1,
                    "arabic_text": "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ",
                    "translation_ru": "Во имя Аллаха, Милостивого, Милосердного",
                    "translation_en": "In the name of Allah, the Entirely Merciful, the Especially Merciful",
                    "theme": "открытие"
                },
                {
                    "surah_number": 1,
                    "verse_number": 2,
                    "arabic_text": "الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ",
                    "translation_ru": "Хвала Аллаху, Господу миров",
                    "translation_en": "Praise be to Allah, Lord of the worlds",
                    "theme": "хвала"
                },
                {
                    "surah_number": 2,
                    "verse_number": 255,
                    "arabic_text": "اللَّهُ لَا إِلَٰهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ",
                    "translation_ru": "Аллах - нет божества, кроме Него, Живого, Поддерживающего жизнь",
                    "translation_en": "Allah - there is no deity except Him, the Ever-Living, the Sustainer of existence",
                    "theme": "вера"
                },
                {
                    "surah_number": 3,
                    "verse_number": 185,
                    "arabic_text": "كُلُّ نَفْسٍ ذَائِقَةُ الْمَوْتِ",
                    "translation_ru": "Всякая душа вкусит смерть",
                    "translation_en": "Every soul will taste death",
                    "theme": "смерть"
                },
                {
                    "surah_number": 4,
                    "verse_number": 1,
                    "arabic_text": "يَا أَيُّهَا النَّاسُ اتَّقُوا رَبَّكُمُ الَّذِي خَلَقَكُمْ مِنْ نَفْسٍ وَاحِدَةٍ",
                    "translation_ru": "О люди! Бойтесь вашего Господа, Который сотворил вас из одной души",
                    "translation_en": "O mankind, fear your Lord, who created you from one soul",
                    "theme": "богобоязненность"
                }
            ]
            
            for verse_data in sample_verses:
                # Проверяем, не существует ли уже такой аят
                existing = self.db.query(QuranVerse).filter(
                    QuranVerse.surah_number == verse_data["surah_number"],
                    QuranVerse.verse_number == verse_data["verse_number"]
                ).first()
                
                if not existing:
                    quran_verse = QuranVerse(**verse_data)
                    self.db.add(quran_verse)
                    self.db.flush()
                    
                    # Создаем эмбеддинги для арабского текста и перевода
                    self.ai_agent.add_text_to_database(
                        verse_data["arabic_text"], 
                        'quran', 
                        quran_verse.id
                    )
                    
                    self.ai_agent.add_text_to_database(
                        verse_data["translation_ru"], 
                        'quran', 
                        quran_verse.id
                    )
            
            self.db.commit()
            logger.info(f"✅ Загружено {len(sample_verses)} примерных аятов")
            
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки примерных данных: {e}")
            self.db.rollback()
    
    def load_commentaries(self):
        """Загрузка комментариев"""
        try:
            logger.info("📚 Загружаем комментарии")
            
            sample_commentaries = [
                {
                    "source": "Ибн Касир",
                    "verse_id": 1,
                    "arabic_text": "هذا تفسير الآية الأولى",
                    "translation_ru": "Это комментарий к первому аяту. Во имя Аллаха означает начало всех дел с именем Аллаха.",
                    "translation_en": "This is a commentary on the first verse. In the name of Allah means beginning all affairs with Allah's name."
                },
                {
                    "source": "Ас-Саади",
                    "verse_id": 2,
                    "arabic_text": "تفسير آية الحمد",
                    "translation_ru": "Хвала Аллаху означает признание всех Его благодеяний и совершенств.",
                    "translation_en": "Praise to Allah means acknowledging all His blessings and perfections."
                }
            ]
            
            for commentary_data in sample_commentaries:
                commentary = Commentary(**commentary_data)
                self.db.add(commentary)
                self.db.flush()
                
                # Создаем эмбеддинги для комментария
                self.ai_agent.add_text_to_database(
                    commentary_data["translation_ru"], 
                    'commentary', 
                    commentary.id
                )
            
            self.db.commit()
            logger.info(f"✅ Загружено {len(sample_commentaries)} комментариев")
            
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки комментариев: {e}")
            self.db.rollback()

def main():
    """Основная функция загрузки"""
    try:
        logger.info("🚀 Начинаем загрузку данных Корана в LEGACY M...")
        
        # Получаем сессию базы данных
        db_gen = get_db()
        db = next(db_gen)
        
        # Создаем загрузчик
        loader = QuranDataLoader(db)
        
        # Загружаем примерные данные
        loader.load_sample_data()
        loader.load_commentaries()
        
        # Пытаемся загрузить из HTML файла
        html_file = "/Users/kamong/telegram_ai_assistant/legacy_m/data/Коран. Все переводы.html"
        if os.path.exists(html_file):
            loader.load_from_html(html_file)
        
        logger.info("✅ Загрузка данных завершена успешно!")
        logger.info("🔧 Теперь можно запустить сервер: python backend/main.py")
        
    except Exception as e:
        logger.error(f"❌ Ошибка загрузки: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
