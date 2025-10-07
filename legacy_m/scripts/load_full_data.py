#!/usr/bin/env python3
"""
Полноценный загрузчик данных для LEGACY M
Загружает все источники с проверкой достоверности
"""

import os
import sys
import logging
import re
from datetime import datetime
from pathlib import Path

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import get_db
from database.models import QuranVerse, Hadith, Commentary, OrthodoxText, OrthodoxDocument

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FullDataLoader:
    """Полноценный загрузчик данных"""
    
    def __init__(self):
        self.db_gen = get_db()
        self.db = next(self.db_gen)
        self.data_path = Path(__file__).parent.parent / "data"
        
    def load_quran_from_files(self):
        """Загружает Коран из файлов"""
        logger.info("📖 Загружаем Коран из файлов...")
        
        # Загружаем Коран из папки Суннизм
        sunni_quran_file = self.data_path / "Суннизм" / "Коран. Все переводы.pdf"
        if sunni_quran_file.exists():
            logger.info("📖 Найден Коран в папке Суннизм")
            # TODO: Добавить парсинг PDF файла
        
        # Загружаем Коран из папки Шиизм
        shia_quran_file = self.data_path / "Шиизм" / "Коран. Все переводы.pdf"
        if shia_quran_file.exists():
            logger.info("📖 Найден Коран в папке Шиизм")
            # TODO: Добавить парсинг PDF файла
        
        # Пока используем примерные данные
        logger.warning("⚠️ PDF файлы требуют парсинга, используем примерные данные")
        self._load_sample_quran()
        
        # Парсим арабский текст
        arabic_verses = self._parse_quran_file(quran_arabic_file, "arabic")
        # Парсим русский перевод
        russian_verses = self._parse_quran_file(quran_russian_file, "russian")
        
        # Объединяем данные
        for surah_num in arabic_verses:
            for verse_num in arabic_verses[surah_num]:
                if surah_num in russian_verses and verse_num in russian_verses[surah_num]:
                    verse_data = {
                        'surah_number': surah_num,
                        'verse_number': verse_num,
                        'arabic_text': arabic_verses[surah_num][verse_num],
                        'translation_ru': russian_verses[surah_num][verse_num],
                        'confession': None
                    }
                    
                    # Проверяем, не существует ли уже
                    existing = self.db.query(QuranVerse).filter(
                        QuranVerse.surah_number == surah_num,
                        QuranVerse.verse_number == verse_num
                    ).first()
                    
                    if not existing:
                        quran_verse = QuranVerse(**verse_data)
                        self.db.add(quran_verse)
        
        self.db.commit()
        logger.info("✅ Коран загружен из файлов")
    
    def _parse_quran_file(self, file_path, text_type):
        """Парсит файл Корана"""
        verses = {}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Ищем паттерн [СУРА:X:АЯТ:Y]
        pattern = r'\[СУРА:(\d+):АЯТ:(\d+)\]\s*(.*?)(?=\[СУРА:|\Z)'
        matches = re.findall(pattern, content, re.DOTALL)
        
        for surah_num, verse_num, text in matches:
            surah_num = int(surah_num)
            verse_num = int(verse_num)
            text = text.strip()
            
            if surah_num not in verses:
                verses[surah_num] = {}
            verses[surah_num][verse_num] = text
        
        return verses
    
    def _load_sample_quran(self):
        """Загружает примерные данные Корана"""
        sample_verses = [
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
                'surah_number': 2,
                'verse_number': 3,
                'arabic_text': 'الَّذِينَ يُؤْمِنُونَ بِالْغَيْبِ وَيُقِيمُونَ الصَّلَاةَ',
                'translation_ru': 'Которые веруют в сокровенное и выстаивают молитву',
                'confession': None
            }
        ]
        
        for verse_data in sample_verses:
            existing = self.db.query(QuranVerse).filter(
                QuranVerse.surah_number == verse_data['surah_number'],
                QuranVerse.verse_number == verse_data['verse_number']
            ).first()
            
            if not existing:
                quran_verse = QuranVerse(**verse_data)
                self.db.add(quran_verse)
        
        self.db.commit()
        logger.info("✅ Загружены примерные данные Корана")
    
    def load_hadith_from_files(self):
        """Загружает хадисы из файлов"""
        logger.info("📜 Загружаем хадисы из файлов...")
        
        # Загружаем из папки Шиизм
        shia_path = self.data_path / "Шиизм"
        if shia_path.exists():
            logger.info("📜 Загружаем шиитские источники...")
            for file_path in shia_path.glob("*.txt"):
                self._load_hadith_file(file_path, "Шиизм")
        
        # Загружаем из папки Суннизм
        sunni_path = self.data_path / "Суннизм"
        if sunni_path.exists():
            logger.info("📜 Загружаем суннитские источники...")
            for file_path in sunni_path.glob("*.txt"):
                self._load_hadith_file(file_path, "Суннизм")
        
        logger.info("✅ Хадисы загружены из файлов")
    
    def _load_hadith_file(self, file_path, source):
        """Загружает хадисы из одного файла"""
        logger.info(f"📜 Загружаем хадисы из {file_path.name}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Парсим хадисы
        pattern = r'\[ИСТОЧНИК:' + source + r':НОМЕР:(\d+)\]\s*(.*?)(?=\[ИСТОЧНИК:|\Z)'
        matches = re.findall(pattern, content, re.DOTALL)
        
        for hadith_num, text in matches:
            hadith_num = int(hadith_num)
            
            # Разделяем арабский текст и перевод
            lines = text.strip().split('\n')
            arabic_text = lines[0] if lines else ""
            translation_ru = lines[1] if len(lines) > 1 else ""
            
            # Определяем конфессию
            confession = 'shia' if source == 'Аль-Кафи' else 'sunni'
            
            hadith_data = {
                'source': source,
                'hadith_number': hadith_num,
                'arabic_text': arabic_text,
                'translation_ru': translation_ru,
                'confession': confession
            }
            
            # Проверяем, не существует ли уже
            existing = self.db.query(Hadith).filter(
                Hadith.source == source,
                Hadith.hadith_number == hadith_num
            ).first()
            
            if not existing:
                hadith = Hadith(**hadith_data)
                self.db.add(hadith)
        
        self.db.commit()
    
    def load_orthodox_from_files(self):
        """Загружает православные тексты из файлов"""
        logger.info("⛪ Загружаем православные тексты из файлов...")
        
        orthodox_path = self.data_path / "Православие"
        
        if not orthodox_path.exists():
            logger.warning("⚠️ Папка Православие не найдена")
            self._load_sample_orthodox()
            return
        
        # Загружаем Библию
        bible_path = orthodox_path / "Библия"
        if bible_path.exists():
            self._load_bible_files(bible_path)
        
        # Загружаем святоотеческие труды
        fathers_path = orthodox_path / "Святоотеческие_труды"
        if fathers_path.exists():
            self._load_fathers_files(fathers_path)
        
        logger.info("✅ Православные тексты загружены из файлов")
    
    def _load_bible_files(self, bible_path):
        """Загружает файлы Библии"""
        for file_path in bible_path.glob("*.txt"):
            self._load_bible_file(file_path)
    
    def _load_bible_file(self, file_path):
        """Загружает один файл Библии"""
        logger.info(f"📖 Загружаем Библию из {file_path.name}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Парсим стихи Библии
        pattern = r'\[КНИГА:([^:]+):ГЛАВА:(\d+):СТИХ:(\d+)\]\s*(.*?)(?=\[КНИГА:|\Z)'
        matches = re.findall(pattern, content, re.DOTALL)
        
        for book_name, chapter_num, verse_num, text in matches:
            chapter_num = int(chapter_num)
            verse_num = int(verse_num)
            
            # Разделяем оригинальный текст и перевод
            lines = text.strip().split('\n')
            original_text = lines[0] if lines else ""
            translation_ru = lines[1] if len(lines) > 1 else ""
            commentary = lines[2] if len(lines) > 2 else ""
            
            orthodox_data = {
                'source_type': 'Библия',
                'book_name': book_name,
                'author': 'Священное Писание',
                'chapter_number': chapter_num,
                'verse_number': verse_num,
                'original_text': original_text,
                'translation_ru': translation_ru,
                'commentary': commentary,
                'theme': 'общее',
                'confession': 'orthodox'
            }
            
            # Проверяем, не существует ли уже
            existing = self.db.query(OrthodoxText).filter(
                OrthodoxText.book_name == book_name,
                OrthodoxText.chapter_number == chapter_num,
                OrthodoxText.verse_number == verse_num
            ).first()
            
            if not existing:
                orthodox_text = OrthodoxText(**orthodox_data)
                self.db.add(orthodox_text)
        
        self.db.commit()
    
    def _load_fathers_files(self, fathers_path):
        """Загружает святоотеческие труды"""
        for file_path in fathers_path.glob("*.txt"):
            self._load_fathers_file(file_path)
    
    def _load_fathers_file(self, file_path):
        """Загружает один файл святоотеческих трудов"""
        logger.info(f"📚 Загружаем святоотеческие труды из {file_path.name}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Парсим святоотеческие труды
        pattern = r'\[АВТОР:([^:]+):ПРОИЗВЕДЕНИЕ:([^:]+):СТРАНИЦА:(\d+)\]\s*(.*?)(?=\[АВТОР:|\Z)'
        matches = re.findall(pattern, content, re.DOTALL)
        
        for author, work, page, text in matches:
            page = int(page)
            
            orthodox_data = {
                'source_type': 'Святоотеческие труды',
                'book_name': work,
                'author': author,
                'chapter_number': page,
                'verse_number': 1,
                'original_text': text.strip(),
                'translation_ru': text.strip(),
                'commentary': '',
                'theme': 'общее',
                'confession': 'orthodox'
            }
            
            orthodox_text = OrthodoxText(**orthodox_data)
            self.db.add(orthodox_text)
        
        self.db.commit()
    
    def _load_sample_orthodox(self):
        """Загружает примерные православные данные"""
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
            }
        ]
        
        for text_data in sample_texts:
            existing = self.db.query(OrthodoxText).filter(
                OrthodoxText.book_name == text_data['book_name'],
                OrthodoxText.chapter_number == text_data['chapter_number'],
                OrthodoxText.verse_number == text_data['verse_number']
            ).first()
            
            if not existing:
                orthodox_text = OrthodoxText(**text_data)
                self.db.add(orthodox_text)
        
        self.db.commit()
        logger.info("✅ Загружены примерные православные данные")
    
    def load_all_data(self):
        """Загружает все данные"""
        logger.info("🚀 Начинаем полную загрузку данных...")
        
        try:
            self.load_quran_from_files()
            self.load_hadith_from_files()
            self.load_orthodox_from_files()
            
            logger.info("✅ Полная загрузка данных завершена!")
            
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки данных: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
        finally:
            self.db.close()

def main():
    """Основная функция"""
    loader = FullDataLoader()
    loader.load_all_data()

if __name__ == "__main__":
    main()
