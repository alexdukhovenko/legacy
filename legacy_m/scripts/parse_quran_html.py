#!/usr/bin/env python3
"""
Скрипт для парсинга HTML файла с переводами Корана
"""

import sys
import os
import re
from pathlib import Path
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QuranHTMLParser:
    """Парсер HTML файла с переводами Корана"""
    
    def __init__(self, html_file_path: str):
        self.html_file_path = html_file_path
        self.verses = []
    
    def parse(self):
        """Парсинг HTML файла"""
        try:
            logger.info(f"📖 Парсим файл: {self.html_file_path}")
            
            with open(self.html_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Используем BeautifulSoup для парсинга
            soup = BeautifulSoup(content, 'html.parser')
            
            # Ищем аяты по различным паттернам
            self._parse_verses_by_patterns(soup)
            
            logger.info(f"✅ Найдено {len(self.verses)} аятов")
            return self.verses
            
        except Exception as e:
            logger.error(f"❌ Ошибка парсинга: {e}")
            return []
    
    def _parse_verses_by_patterns(self, soup):
        """Парсинг аятов по различным паттернам"""
        
        # Паттерн 1: Поиск по классам
        verse_elements = soup.find_all(['div', 'p', 'span'], class_=re.compile(r'verse|ayat|ayah', re.I))
        
        for element in verse_elements:
            verse_data = self._extract_verse_data(element)
            if verse_data:
                self.verses.append(verse_data)
        
        # Паттерн 2: Поиск по тексту с номерами аятов
        text_pattern = r'(\d+):(\d+)\s*(.*?)(?=\d+:\d+|$)'
        text_matches = re.findall(text_pattern, soup.get_text(), re.DOTALL)
        
        for surah_num, verse_num, text in text_matches:
            if text.strip():
                verse_data = {
                    'surah_number': int(surah_num),
                    'verse_number': int(verse_num),
                    'arabic_text': text.strip(),
                    'translation_ru': text.strip(),
                    'theme': 'общий'
                }
                self.verses.append(verse_data)
        
        # Паттерн 3: Поиск арабского текста
        arabic_pattern = r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]+'
        arabic_matches = re.findall(arabic_pattern, soup.get_text())
        
        for i, arabic_text in enumerate(arabic_matches[:50]):  # Ограничиваем для теста
            if len(arabic_text.strip()) > 10:  # Минимальная длина
                verse_data = {
                    'surah_number': 1,
                    'verse_number': i + 1,
                    'arabic_text': arabic_text.strip(),
                    'translation_ru': f"Перевод аята {i + 1}",
                    'theme': 'общий'
                }
                self.verses.append(verse_data)
    
    def _extract_verse_data(self, element):
        """Извлечение данных аята из элемента"""
        try:
            text = element.get_text().strip()
            
            # Ищем номер суры и аята
            surah_verse_match = re.search(r'(\d+):(\d+)', text)
            if surah_verse_match:
                surah_num = int(surah_verse_match.group(1))
                verse_num = int(surah_verse_match.group(2))
                
                # Убираем номер из текста
                clean_text = re.sub(r'\d+:\d+\s*', '', text).strip()
                
                return {
                    'surah_number': surah_num,
                    'verse_number': verse_num,
                    'arabic_text': clean_text,
                    'translation_ru': clean_text,
                    'theme': 'общий'
                }
            
            return None
            
        except Exception as e:
            logger.warning(f"⚠️ Ошибка извлечения данных: {e}")
            return None
    
    def save_to_json(self, output_file: str):
        """Сохранение результатов в JSON файл"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.verses, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ Данные сохранены в {output_file}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения: {e}")

def main():
    """Основная функция"""
    try:
        html_file = "/Users/kamong/telegram_ai_assistant/legacy_m/data/Коран. Все переводы.html"
        
        if not os.path.exists(html_file):
            logger.error(f"❌ Файл не найден: {html_file}")
            return
        
        # Создаем парсер
        parser = QuranHTMLParser(html_file)
        
        # Парсим файл
        verses = parser.parse()
        
        if verses:
            # Сохраняем в JSON
            output_file = "/Users/kamong/telegram_ai_assistant/legacy_m/data/parsed_quran.json"
            parser.save_to_json(output_file)
            
            logger.info(f"✅ Парсинг завершен. Найдено {len(verses)} аятов")
        else:
            logger.warning("⚠️ Аяты не найдены")
        
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    main()
