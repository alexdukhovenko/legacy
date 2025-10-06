#!/usr/bin/env python3
"""
Скрипт для загрузки православных текстов из PDF файлов
Анализирует все PDF файлы в папке Православие и загружает их в базу данных
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime
import PyPDF2
import fitz  # PyMuPDF
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import get_db
from database.models import OrthodoxDocument, OrthodoxText, Base

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Путь к папке с православными текстами
ORTHODOX_FOLDER = "/Users/kamong/Library/Mobile Documents/com~apple~CloudDocs/Downloads/Коран (легаси М)/Православие"

class OrthodoxTextLoader:
    def __init__(self):
        self.db = next(get_db())
        self.processed_files = 0
        self.total_texts = 0
        
    def extract_text_from_pdf(self, pdf_path):
        """Извлекает текст из PDF файла"""
        try:
            # Пробуем PyMuPDF (fitz) - более надежный
            doc = fitz.open(pdf_path)
            text = ""
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text += page.get_text()
                
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
                        text += page.extract_text()
                        
                return text.strip()
                
            except Exception as e2:
                logger.error(f"Both PDF readers failed for {pdf_path}: {e2}")
                return None
    
    def determine_document_type(self, filename):
        """Определяет тип документа по названию файла"""
        filename_lower = filename.lower()
        
        if any(word in filename_lower for word in ['катехизис', 'catechetical', 'katehizis']):
            return 'catechetical'
        elif any(word in filename_lower for word in ['догматическ', 'dogmatic', 'богословие']):
            return 'dogmatic'
        elif any(word in filename_lower for word in ['святитель', 'преподобный', 'святой', 'патристик', 'patristic']):
            return 'patristic'
        elif any(word in filename_lower for word in ['псалтирь', 'psalm', 'литурги', 'liturgical']):
            return 'liturgical'
        elif any(word in filename_lower for word in ['библия', 'bible', 'евангелие', 'gospel']):
            return 'bible'
        else:
            return 'patristic'  # По умолчанию
    
    def extract_author_from_filename(self, filename):
        """Извлекает автора из названия файла"""
        # Убираем расширение
        name = Path(filename).stem
        
        # Ищем известных авторов
        authors = [
            'Иоанн Дамаскин', 'Григорий Богослов', 'Василий Великий', 'Григорий Нисский',
            'Афанасий Великий', 'Кирилл Александрийский', 'Максим Исповедник',
            'Григорий Палама', 'Феодорит Кирский', 'Иннокентий', 'Петр Могила',
            'Сильвестр Малеванский', 'Михаил Помазанский'
        ]
        
        for author in authors:
            if author.lower() in name.lower():
                return author
                
        return None
    
    def process_pdf_file(self, pdf_path):
        """Обрабатывает один PDF файл"""
        filename = os.path.basename(pdf_path)
        logger.info(f"Обрабатываем файл: {filename}")
        
        # Проверяем, не обработан ли уже этот файл
        existing_doc = self.db.query(OrthodoxDocument).filter(
            OrthodoxDocument.filename == filename
        ).first()
        
        if existing_doc and existing_doc.processed == 1:
            logger.info(f"Файл {filename} уже обработан, пропускаем")
            return
        
        # Извлекаем текст
        text = self.extract_text_from_pdf(pdf_path)
        if not text:
            logger.error(f"Не удалось извлечь текст из {filename}")
            return
        
        # Определяем тип документа и автора
        doc_type = self.determine_document_type(filename)
        author = self.extract_author_from_filename(filename)
        
        # Получаем размер файла
        file_size = os.path.getsize(pdf_path)
        
        # Создаем или обновляем запись документа
        if existing_doc:
            doc = existing_doc
        else:
            doc = OrthodoxDocument(
                filename=filename,
                title=Path(filename).stem,
                author=author,
                document_type=doc_type,
                file_path=pdf_path,
                file_size=file_size,
                confession='orthodox'
            )
            self.db.add(doc)
            self.db.commit()
        
        # Разбиваем текст на части и сохраняем
        self.save_text_chunks(doc, text)
        
        # Отмечаем документ как обработанный
        doc.processed = 1
        doc.processed_at = datetime.utcnow()
        doc.pages_count = len(text.split('\n')) // 50  # Примерная оценка страниц
        self.db.commit()
        
        self.processed_files += 1
        logger.info(f"Файл {filename} успешно обработан")
    
    def save_text_chunks(self, document, text):
        """Разбивает текст на части и сохраняет в базу"""
        # Разбиваем текст на абзацы
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        for i, paragraph in enumerate(paragraphs):
            if len(paragraph) < 50:  # Пропускаем слишком короткие абзацы
                continue
                
            # Создаем запись текста
            orthodox_text = OrthodoxText(
                source_type=document.document_type,
                book_name=document.title,
                author=document.author,
                translation_ru=paragraph,
                theme=self.extract_theme_from_text(paragraph),
                confession='orthodox'
            )
            
            self.db.add(orthodox_text)
            self.total_texts += 1
            
            # Сохраняем каждые 100 записей
            if self.total_texts % 100 == 0:
                self.db.commit()
                logger.info(f"Сохранено {self.total_texts} текстовых фрагментов")
    
    def extract_theme_from_text(self, text):
        """Извлекает тему из текста"""
        text_lower = text.lower()
        
        themes = {
            'богословие': ['бог', 'троица', 'христос', 'святой дух', 'божество'],
            'нравственность': ['грех', 'добродетель', 'нравственность', 'этика', 'мораль'],
            'молитва': ['молитва', 'молиться', 'богослужение', 'литургия'],
            'вера': ['вера', 'веровать', 'исповедание', 'догмат'],
            'спасение': ['спасение', 'спастись', 'вечная жизнь', 'царство небесное'],
            'церковь': ['церковь', 'церковный', 'собор', 'епископ', 'священник']
        }
        
        for theme, keywords in themes.items():
            if any(keyword in text_lower for keyword in keywords):
                return theme
                
        return 'общее'
    
    def load_all_orthodox_texts(self):
        """Загружает все православные тексты из папки"""
        if not os.path.exists(ORTHODOX_FOLDER):
            logger.error(f"Папка {ORTHODOX_FOLDER} не найдена")
            return
        
        logger.info(f"Начинаем загрузку православных текстов из {ORTHODOX_FOLDER}")
        
        # Получаем все PDF файлы
        pdf_files = []
        for root, dirs, files in os.walk(ORTHODOX_FOLDER):
            for file in files:
                if file.lower().endswith('.pdf'):
                    pdf_files.append(os.path.join(root, file))
        
        logger.info(f"Найдено {len(pdf_files)} PDF файлов")
        
        # Обрабатываем каждый файл
        for pdf_path in pdf_files:
            try:
                self.process_pdf_file(pdf_path)
            except Exception as e:
                logger.error(f"Ошибка при обработке {pdf_path}: {e}")
                continue
        
        # Финальное сохранение
        self.db.commit()
        
        logger.info(f"Загрузка завершена. Обработано файлов: {self.processed_files}, "
                   f"сохранено текстовых фрагментов: {self.total_texts}")

def main():
    """Основная функция"""
    try:
        loader = OrthodoxTextLoader()
        loader.load_all_orthodox_texts()
        print("✅ Загрузка православных текстов завершена успешно")
        
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        print(f"❌ Ошибка при загрузке: {e}")

if __name__ == "__main__":
    main()
