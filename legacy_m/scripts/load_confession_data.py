#!/usr/bin/env python3
"""
Скрипт для загрузки текстов из папок конфессий
"""

import sys
import os
import glob
from pathlib import Path
from typing import List, Dict, Any
import logging

# Добавляем путь к корневой папке проекта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db, init_database, QuranVerse, Hadith, Commentary
from backend.simple_ai_agent import SimpleIslamicAIAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Путь к папке с текстами конфессий
CONFESSION_DATA_PATH = "/Users/kamong/Library/Mobile Documents/com~apple~CloudDocs/Downloads/Коран (легаси М)"

class ConfessionDataLoader:
    """Загрузчик данных для конфессий"""
    
    def __init__(self):
        self.db = next(get_db())
        self.ai_agent = SimpleIslamicAIAgent(self.db)
    
    def load_all_confession_data(self):
        """Загружает все данные из папок конфессий"""
        logger.info("🔄 Начинаем загрузку данных конфессий...")
        
        # Загружаем общие тексты
        self.load_common_texts()
        
        # Загружаем тексты сунизма
        self.load_sunni_texts()
        
        # Загружаем тексты шиизма
        self.load_shia_texts()
        
        logger.info("🎉 Загрузка данных конфессий завершена!")
    
    def load_common_texts(self):
        """Загружает общие тексты (Коран)"""
        logger.info("📖 Загружаем общие тексты...")
        
        common_path = os.path.join(CONFESSION_DATA_PATH, "Общий для всех (Коран)")
        if not os.path.exists(common_path):
            logger.warning(f"⚠️ Папка с общими текстами не найдена: {common_path}")
            return
        
        # Загружаем Коран
        quran_files = glob.glob(os.path.join(common_path, "*.pdf"))
        for file_path in quran_files:
            logger.info(f"📄 Обрабатываем файл: {os.path.basename(file_path)}")
            self.process_quran_file(file_path, "common")
    
    def load_sunni_texts(self):
        """Загружает тексты сунизма"""
        logger.info("☪️ Загружаем тексты сунизма...")
        
        sunni_path = os.path.join(CONFESSION_DATA_PATH, 'Конфессия "суниизм"')
        if not os.path.exists(sunni_path):
            logger.warning(f"⚠️ Папка с текстами сунизма не найдена: {sunni_path}")
            return
        
        # Загружаем хадисы и комментарии сунизма
        sunni_files = glob.glob(os.path.join(sunni_path, "*.pdf"))
        for file_path in sunni_files:
            logger.info(f"📄 Обрабатываем файл сунизма: {os.path.basename(file_path)}")
            self.process_hadith_file(file_path, "sunni")
    
    def load_shia_texts(self):
        """Загружает тексты шиизма"""
        logger.info("🕌 Загружаем тексты шиизма...")
        
        shia_path = os.path.join(CONFESSION_DATA_PATH, 'Конфессия "Шиизм"')
        if not os.path.exists(shia_path):
            logger.warning(f"⚠️ Папка с текстами шиизма не найдена: {shia_path}")
            return
        
        # Загружаем хадисы и комментарии шиизма
        shia_files = glob.glob(os.path.join(shia_path, "*.pdf"))
        for file_path in shia_files:
            logger.info(f"📄 Обрабатываем файл шиизма: {os.path.basename(file_path)}")
            self.process_hadith_file(file_path, "shia")
        
        # Загружаем al-kafi
        al_kafi_path = os.path.join(shia_path, "al-kafi")
        if os.path.exists(al_kafi_path):
            logger.info("📚 Загружаем al-kafi...")
            al_kafi_files = glob.glob(os.path.join(al_kafi_path, "*.pdf"))
            for file_path in al_kafi_files:
                logger.info(f"📄 Обрабатываем al-kafi: {os.path.basename(file_path)}")
                self.process_hadith_file(file_path, "shia", collection="al-kafi")
    
    def process_quran_file(self, file_path: str, confession: str):
        """Обрабатывает файл Корана"""
        try:
            # Для демонстрации создаем несколько примеров аятов
            # В реальной реализации здесь был бы парсинг PDF
            
            sample_verses = [
                {
                    "surah_number": 1,
                    "verse_number": 1,
                    "arabic_text": "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ",
                    "translation_ru": "Во имя Аллаха, Милостивого, Милосердного",
                    "theme": "открытие"
                },
                {
                    "surah_number": 2,
                    "verse_number": 255,
                    "arabic_text": "اللَّهُ لَا إِلَٰهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ",
                    "translation_ru": "Аллах - нет божества, кроме Него, Живого, Поддерживающего жизнь",
                    "theme": "единобожие"
                }
            ]
            
            for verse_data in sample_verses:
                # Проверяем, существует ли уже такой аят
                existing = self.db.query(QuranVerse).filter(
                    QuranVerse.surah_number == verse_data["surah_number"],
                    QuranVerse.verse_number == verse_data["verse_number"],
                    QuranVerse.confession == confession
                ).first()
                
                if not existing:
                    verse = QuranVerse(
                        surah_number=verse_data["surah_number"],
                        verse_number=verse_data["verse_number"],
                        arabic_text=verse_data["arabic_text"],
                        translation_ru=verse_data["translation_ru"],
                        theme=verse_data["theme"],
                        confession=confession
                    )
                    self.db.add(verse)
                    logger.info(f"✅ Добавлен аят {verse_data['surah_number']}:{verse_data['verse_number']} ({confession})")
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"❌ Ошибка обработки файла Корана {file_path}: {e}")
            self.db.rollback()
    
    def process_hadith_file(self, file_path: str, confession: str, collection: str = None):
        """Обрабатывает файл хадисов"""
        try:
            # Определяем коллекцию по имени файла
            if not collection:
                filename = os.path.basename(file_path).lower()
                if "bukhari" in filename:
                    collection = "Bukhari"
                elif "muslim" in filename:
                    collection = "Muslim"
                elif "riyad" in filename:
                    collection = "Riyad as-Salihin"
                else:
                    collection = "Unknown"
            
            # Для демонстрации создаем несколько примеров хадисов
            sample_hadiths = [
                {
                    "hadith_number": 1,
                    "arabic_text": "إِنَّمَا الأَعْمَالُ بِالنِّيَّاتِ",
                    "translation_ru": "Поистине, дела оцениваются по намерениям",
                    "narrator": "Umar ibn al-Khattab",
                    "grade": "Sahih",
                    "topic": "намерения"
                },
                {
                    "hadith_number": 2,
                    "arabic_text": "مَنْ كَانَ يُؤْمِنُ بِاللَّهِ وَالْيَوْمِ الآخِرِ فَلْيَقُلْ خَيْرًا أَوْ لِيَصْمُتْ",
                    "translation_ru": "Кто верует в Аллаха и в Последний день, пусть говорит благое или молчит",
                    "narrator": "Abu Huraira",
                    "grade": "Sahih",
                    "topic": "речь"
                }
            ]
            
            for hadith_data in sample_hadiths:
                # Проверяем, существует ли уже такой хадис
                existing = self.db.query(Hadith).filter(
                    Hadith.collection == collection,
                    Hadith.hadith_number == hadith_data["hadith_number"],
                    Hadith.confession == confession
                ).first()
                
                if not existing:
                    hadith = Hadith(
                        collection=collection,
                        hadith_number=hadith_data["hadith_number"],
                        arabic_text=hadith_data["arabic_text"],
                        translation_ru=hadith_data["translation_ru"],
                        narrator=hadith_data["narrator"],
                        grade=hadith_data["grade"],
                        topic=hadith_data["topic"],
                        confession=confession
                    )
                    self.db.add(hadith)
                    logger.info(f"✅ Добавлен хадис {collection}:{hadith_data['hadith_number']} ({confession})")
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"❌ Ошибка обработки файла хадисов {file_path}: {e}")
            self.db.rollback()

def main():
    """Основная функция"""
    try:
        # Инициализируем базу данных
        init_database()
        
        # Создаем загрузчик
        loader = ConfessionDataLoader()
        
        # Загружаем данные
        loader.load_all_confession_data()
        
        logger.info("🎉 Все данные успешно загружены!")
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
