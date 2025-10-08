#!/usr/bin/env python3
"""
Система загрузки данных из внешнего репозитория
"""

import os
import sys
import logging
import requests
import tempfile
import zipfile
from pathlib import Path
from typing import Dict, List, Any
from sqlalchemy.orm import Session

# Импорты моделей
from database.models import QuranVerse, Hadith, Commentary, OrthodoxText, OrthodoxDocument

logger = logging.getLogger(__name__)

class ExternalDataLoader:
    """Загрузчик данных из внешнего репозитория"""
    
    def __init__(self, db: Session):
        self.db = db
        self.data_repos = {
            'orthodox': "https://github.com/alexdukhovenko/legacy-orthodox-data",
            'sunni': "https://github.com/alexdukhovenko/legacy-sunni-data", 
            'shia': "https://github.com/alexdukhovenko/legacy-shia-data",
            'common': "https://github.com/alexdukhovenko/legacy-common-data"
        }
        self.temp_dir = None
    
    def load_all_data_from_repo(self) -> Dict[str, int]:
        """Загружает все данные из внешнего репозитория"""
        logger.info("🚀 Начинаем загрузку данных из внешнего репозитория...")
        
        try:
            # Скачиваем репозиторий
            self._download_repo()
            
            # Загружаем данные
            stats = {
                'quran_verses': self._load_quran_data(),
                'hadiths': self._load_hadith_data(),
                'orthodox_texts': self._load_orthodox_data()
            }
            
            logger.info(f"✅ Загружено: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки данных: {e}")
            return {}
        finally:
            self._cleanup()
    
    def _download_repo(self):
        """Скачивает репозиторий с данными"""
        logger.info("📥 Скачиваем репозиторий с данными...")
        
        # Создаем временную директорию
        self.temp_dir = tempfile.mkdtemp()
        
        # URL для скачивания ZIP архива
        zip_url = f"{self.data_repo_url}/archive/refs/heads/main.zip"
        
        try:
            response = requests.get(zip_url, stream=True)
            response.raise_for_status()
            
            zip_path = os.path.join(self.temp_dir, "data.zip")
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Распаковываем
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.temp_dir)
            
            logger.info("✅ Репозиторий скачан и распакован")
            
        except Exception as e:
            logger.error(f"❌ Ошибка скачивания репозитория: {e}")
            raise
    
    def _load_quran_data(self) -> int:
        """Загружает данные Корана"""
        logger.info("📖 Загружаем данные Корана...")
        
        data_path = self._get_data_path()
        quran_files = [
            data_path / "Суннизм" / "Коран. Все переводы copy.pdf",
            data_path / "Шиизм" / "Коран. Все переводы.pdf"
        ]
        
        loaded_count = 0
        
        for file_path in quran_files:
            if file_path.exists():
                logger.info(f"📖 Обрабатываем: {file_path.name}")
                # Здесь будет парсинг PDF файлов
                # Пока добавляем примерные данные
                loaded_count += self._add_sample_quran_data()
        
        return loaded_count
    
    def _load_hadith_data(self) -> int:
        """Загружает хадисы"""
        logger.info("📜 Загружаем хадисы...")
        
        data_path = self._get_data_path()
        hadith_dirs = [
            data_path / "Суннизм",
            data_path / "Шиизм"
        ]
        
        loaded_count = 0
        
        for dir_path in hadith_dirs:
            if dir_path.exists():
                for file_path in dir_path.glob("*.pdf"):
                    if "Коран" not in file_path.name:
                        logger.info(f"📜 Обрабатываем: {file_path.name}")
                        # Здесь будет парсинг PDF файлов
                        # Пока добавляем примерные данные
                        loaded_count += self._add_sample_hadith_data()
        
        return loaded_count
    
    def _load_orthodox_data(self) -> int:
        """Загружает православные тексты"""
        logger.info("⛪ Загружаем православные тексты...")
        
        data_path = self._get_data_path()
        orthodox_dir = data_path / "Православие"
        
        loaded_count = 0
        
        if orthodox_dir.exists():
            for file_path in orthodox_dir.glob("*.pdf"):
                logger.info(f"⛪ Обрабатываем: {file_path.name}")
                # Здесь будет парсинг PDF файлов
                # Пока добавляем примерные данные
                loaded_count += self._add_sample_orthodox_data()
        
        return loaded_count
    
    def _get_data_path(self) -> Path:
        """Возвращает путь к данным"""
        if not self.temp_dir:
            raise Exception("Репозиторий не скачан")
        
        # Ищем папку с данными
        for item in Path(self.temp_dir).iterdir():
            if item.is_dir() and "legacy-spiritual-data" in item.name:
                return item
        
        raise Exception("Папка с данными не найдена")
    
    def _add_sample_quran_data(self) -> int:
        """Добавляет примерные данные Корана"""
        sample_verses = [
            QuranVerse(
                surah_number=1, verse_number=1,
                arabic_text="بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ",
                translation_ru="Во имя Аллаха, Милостивого, Милосердного!",
                commentary="Начало каждой суры Корана.",
                confession='sunni'
            ),
            QuranVerse(
                surah_number=2, verse_number=3,
                arabic_text="الَّذِينَ يُؤْمِنُونَ بِالْغَيْبِ وَيُقِيمُونَ الصَّلَاةَ",
                translation_ru="которые веруют в сокровенное и выстаивают молитву",
                commentary="Описание качеств богобоязненных.",
                confession='sunni'
            )
        ]
        
        for verse in sample_verses:
            existing = self.db.query(QuranVerse).filter(
                QuranVerse.surah_number == verse.surah_number,
                QuranVerse.verse_number == verse.verse_number,
                QuranVerse.confession == verse.confession
            ).first()
            
            if not existing:
                self.db.add(verse)
        
        self.db.commit()
        return len(sample_verses)
    
    def _add_sample_hadith_data(self) -> int:
        """Добавляет примерные хадисы"""
        sample_hadiths = [
            Hadith(
                collection="Бухари",
                number=1,
                text_arabic="إنما الأعمال بالنيات",
                text_russian="Поистине, дела оцениваются по намерениям.",
                commentary="Важность намерения в исламе.",
                confession='sunni'
            ),
            Hadith(
                collection="Аль-Кафи",
                number=1,
                text_arabic="عن أبي عبد الله عليه السلام قال: دعائم الكفر ثلاثة",
                text_russian="От Абу Абдуллаха передано: Столпов неверия три",
                commentary="Основы неверия в шиизме.",
                confession='shia'
            )
        ]
        
        for hadith in sample_hadiths:
            existing = self.db.query(Hadith).filter(
                Hadith.collection == hadith.collection,
                Hadith.number == hadith.number,
                Hadith.confession == hadith.confession
            ).first()
            
            if not existing:
                self.db.add(hadith)
        
        self.db.commit()
        return len(sample_hadiths)
    
    def _add_sample_orthodox_data(self) -> int:
        """Добавляет примерные православные тексты"""
        # Создаем документ
        doc = OrthodoxDocument(
            filename="external_orthodox_sources.txt",
            title="Внешние православные источники",
            author="Система",
            document_type="Сборник",
            file_path="/external/data/orthodox.txt",
            file_size=1024,
            confession='orthodox',
            processed=1,
            processed_at=datetime.utcnow(),
            pages_count=1
        )
        self.db.add(doc)
        self.db.flush()
        
        sample_texts = [
            OrthodoxText(
                document_id=doc.id,
                confession='orthodox',
                source_type='Библия',
                book_name='Евангелие от Матфея',
                chapter_number=6,
                verse_number=9,
                original_text='Отче наш, сущий на небесах!',
                translation_ru='Отче наш, сущий на небесах!',
                commentary='Начало молитвы Господней.',
                theme='Молитва'
            ),
            OrthodoxText(
                document_id=doc.id,
                confession='orthodox',
                source_type='Библия',
                book_name='Послание к Евреям',
                chapter_number=11,
                verse_number=1,
                original_text='Вера же есть осуществление ожидаемого',
                translation_ru='Вера же есть осуществление ожидаемого',
                commentary='Определение веры.',
                theme='Вера'
            )
        ]
        
        for text in sample_texts:
            existing = self.db.query(OrthodoxText).filter(
                OrthodoxText.book_name == text.book_name,
                OrthodoxText.chapter_number == text.chapter_number,
                OrthodoxText.verse_number == text.verse_number,
                OrthodoxText.confession == text.confession
            ).first()
            
            if not existing:
                self.db.add(text)
        
        self.db.commit()
        return len(sample_texts)
    
    def _cleanup(self):
        """Очищает временные файлы"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)
            logger.info("🧹 Временные файлы очищены")

# Глобальная функция для использования в других модулях
def load_external_data(db: Session) -> Dict[str, int]:
    """Загружает данные из внешнего репозитория"""
    loader = ExternalDataLoader(db)
    return loader.load_all_data_from_repo()
