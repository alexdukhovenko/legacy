#!/usr/bin/env python3
"""
Скрипт для загрузки исламских текстов из PDF файлов
Парсит PDF файлы из папок Суннизм и Шиизм
"""

import os
import sys
import logging
import re
from pathlib import Path
from datetime import datetime
import PyPDF2
import fitz  # PyMuPDF
from sqlalchemy.orm import Session

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import get_db
from database.models import QuranVerse, Hadith

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IslamicPDFLoader:
    def __init__(self):
        self.db = next(get_db())
        self.processed_files = 0
        self.loaded_verses = 0
        self.loaded_hadiths = 0
        
    def extract_text_from_pdf(self, pdf_path):
        """Извлекает текст из PDF файла"""
        try:
            # Пробуем PyMuPDF (fitz) - более надежный
            doc = fitz.open(pdf_path)
            text = ""
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text += page.get_text() + "\n"
                
            doc.close()
            return text.strip()
            
        except Exception as e:
            logger.warning(f"PyMuPDF failed for {pdf_path}: {e}")
            
            # Fallback на PyPDF2
            try:
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text = ""
                    
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
                        
                return text.strip()
                
            except Exception as e2:
                logger.error(f"Both PDF readers failed for {pdf_path}: {e2}")
                return None
    
    def parse_quran_pdf(self, text, confession):
        """Парсит текст Корана из PDF"""
        logger.info(f"Парсим Коран для конфессии: {confession}")
        
        # Паттерны для поиска аятов
        verse_patterns = [
            r'(\d+):(\d+)\s*(.*?)(?=\d+:\d+|\Z)',  # Формат "1:1 текст"
            r'Сура\s*(\d+)[,\s]*аят\s*(\d+)[:\s]*(.*?)(?=Сура|\Z)',  # Формат "Сура 1, аят 1: текст"
            r'(\d+)\s*(\d+)\s*(.*?)(?=\d+\s+\d+|\Z)'  # Формат "1 1 текст"
        ]
        
        verses = []
        for pattern in verse_patterns:
            matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
            for match in matches:
                try:
                    surah_num = int(match[0])
                    verse_num = int(match[1])
                    verse_text = match[2].strip()
                    
                    if len(verse_text) > 10:  # Минимальная длина аята
                        verses.append({
                            'surah_number': surah_num,
                            'verse_number': verse_num,
                            'arabic_text': verse_text[:100] + "..." if len(verse_text) > 100 else verse_text,
                            'translation_ru': verse_text,
                            'commentary': f"Из PDF файла для {confession}",
                            'confession': confession
                        })
                except (ValueError, IndexError):
                    continue
        
        logger.info(f"Найдено {len(verses)} аятов в PDF")
        return verses
    
    def parse_hadith_pdf(self, text, confession, collection_name):
        """Парсит хадисы из PDF"""
        logger.info(f"Парсим хадисы {collection_name} для конфессии: {confession}")
        
        # Паттерны для поиска хадисов
        hadith_patterns = [
            r'Хадис\s*№?\s*(\d+)[:\s]*(.*?)(?=Хадис|$)',  # Формат "Хадис №1: текст"
            r'(\d+)\.\s*(.*?)(?=\d+\.|$)',  # Формат "1. текст"
            r'\[(\d+)\]\s*(.*?)(?=\[\d+\]|$)'  # Формат "[1] текст"
        ]
        
        hadiths = []
        for pattern in hadith_patterns:
            matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
            for match in matches:
                try:
                    hadith_num = int(match[0])
                    hadith_text = match[1].strip()
                    
                    if len(hadith_text) > 20:  # Минимальная длина хадиса
                        hadiths.append({
                            'collection': collection_name,
                            'hadith_number': hadith_num,
                            'arabic_text': hadith_text[:100] + "..." if len(hadith_text) > 100 else hadith_text,
                            'translation_ru': hadith_text,
                            'commentary': f"Из PDF файла {collection_name} для {confession}",
                            'confession': confession
                        })
                except (ValueError, IndexError):
                    continue
        
        logger.info(f"Найдено {len(hadiths)} хадисов в PDF")
        return hadiths
    
    def process_islamic_pdf(self, pdf_path, confession):
        """Обрабатывает один исламский PDF файл"""
        filename = os.path.basename(pdf_path)
        logger.info(f"Обрабатываем файл: {filename} для конфессии: {confession}")
        
        # Извлекаем текст
        text = self.extract_text_from_pdf(pdf_path)
        if not text:
            logger.error(f"Не удалось извлечь текст из {filename}")
            return
        
        # Определяем тип файла по названию
        if 'коран' in filename.lower() or 'quran' in filename.lower():
            # Парсим как Коран
            verses = self.parse_quran_pdf(text, confession)
            for verse_data in verses:
                # Проверяем, не существует ли уже такой аят
                existing = self.db.query(QuranVerse).filter(
                    QuranVerse.surah_number == verse_data['surah_number'],
                    QuranVerse.verse_number == verse_data['verse_number'],
                    QuranVerse.confession == confession
                ).first()
                
                if not existing:
                    quran_verse = QuranVerse(**verse_data)
                    self.db.add(quran_verse)
                    self.loaded_verses += 1
            
        elif any(name in filename.lower() for name in ['бухари', 'bukhari', 'муслим', 'muslim', 'кафи', 'kafi']):
            # Парсим как хадисы
            collection_name = self.get_collection_name(filename)
            hadiths = self.parse_hadith_pdf(text, confession, collection_name)
            
            for hadith_data in hadiths:
                # Проверяем, не существует ли уже такой хадис
                existing = self.db.query(Hadith).filter(
                    Hadith.collection == hadith_data['collection'],
                    Hadith.hadith_number == hadith_data['hadith_number'],
                    Hadith.confession == confession
                ).first()
                
                if not existing:
                    hadith = Hadith(**hadith_data)
                    self.db.add(hadith)
                    self.loaded_hadiths += 1
        
        self.db.commit()
        self.processed_files += 1
    
    def get_collection_name(self, filename):
        """Определяет название сборника по имени файла"""
        filename_lower = filename.lower()
        
        if 'бухари' in filename_lower or 'bukhari' in filename_lower:
            return 'Бухари'
        elif 'муслим' in filename_lower or 'muslim' in filename_lower:
            return 'Муслим'
        elif 'кафи' in filename_lower or 'kafi' in filename_lower:
            return 'Аль-Кафи'
        else:
            return 'Неизвестный сборник'
    
    def load_all_islamic_pdfs(self):
        """Загружает все исламские PDF файлы"""
        data_path = Path(__file__).parent.parent / "data"
        
        # Обрабатываем суннитские файлы
        sunni_path = data_path / "Суннизм"
        if sunni_path.exists():
            logger.info(f"Обрабатываем суннитские файлы из {sunni_path}")
            for pdf_file in sunni_path.glob("*.pdf"):
                try:
                    self.process_islamic_pdf(pdf_file, 'sunni')
                except Exception as e:
                    logger.error(f"Ошибка при обработке {pdf_file}: {e}")
        
        # Обрабатываем шиитские файлы
        shia_path = data_path / "Шиизм"
        if shia_path.exists():
            logger.info(f"Обрабатываем шиитские файлы из {shia_path}")
            for pdf_file in shia_path.glob("*.pdf"):
                try:
                    self.process_islamic_pdf(pdf_file, 'shia')
                except Exception as e:
                    logger.error(f"Ошибка при обработке {pdf_file}: {e}")
        
        logger.info(f"Загрузка завершена:")
        logger.info(f"  Обработано файлов: {self.processed_files}")
        logger.info(f"  Загружено аятов: {self.loaded_verses}")
        logger.info(f"  Загружено хадисов: {self.loaded_hadiths}")

def main():
    """Основная функция"""
    try:
        loader = IslamicPDFLoader()
        loader.load_all_islamic_pdfs()
        logger.info("✅ Загрузка исламских PDF файлов завершена успешно!")
        
    except Exception as e:
        logger.error(f"❌ Ошибка загрузки: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
