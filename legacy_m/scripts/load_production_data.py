#!/usr/bin/env python3
"""
Скрипт для загрузки данных в продакшене
Загружает данные из внешних источников или создает расширенные примерные данные
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime
import requests
from sqlalchemy.orm import Session

# Добавляем путь к проекту
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from database.database import SessionLocal
from database.models import QuranVerse, Hadith, Commentary, OrthodoxText, OrthodoxDocument

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProductionDataLoader:
    """Загрузчик данных для продакшена"""
    
    def __init__(self):
        self.db = SessionLocal()
        self.loaded_count = 0
    
    def load_extended_sample_data(self):
        """Загружает расширенные примерные данные"""
        logger.info("📚 Загружаем расширенные примерные данные...")
        
        # Загружаем расширенные данные Корана
        self._load_extended_quran_data()
        
        # Загружаем расширенные хадисы
        self._load_extended_hadith_data()
        
        # Загружаем расширенные православные тексты
        self._load_extended_orthodox_data()
        
        logger.info(f"✅ Загружено {self.loaded_count} записей")
    
    def _load_extended_quran_data(self):
        """Загружает расширенные данные Корана"""
        logger.info("📖 Загружаем расширенные данные Корана...")
        
        # Расширенные аяты Корана
        extended_quran_verses = [
            # Сура 1 - Аль-Фатиха
            QuranVerse(
                surah_number=1, verse_number=1,
                arabic_text="بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ",
                translation_ru="Во имя Аллаха, Милостивого, Милосердного!",
                commentary="Начало каждой суры Корана, кроме девятой.",
                confession='sunni'
            ),
            QuranVerse(
                surah_number=1, verse_number=2,
                arabic_text="الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ",
                translation_ru="Хвала Аллаху, Господу миров,",
                commentary="Прославление Аллаха как Творца всего сущего.",
                confession='sunni'
            ),
            QuranVerse(
                surah_number=1, verse_number=3,
                arabic_text="الرَّحْمَٰنِ الرَّحِيمِ",
                translation_ru="Милостивому, Милосердному,",
                commentary="Подчеркивание милости и милосердия Аллаха.",
                confession='sunni'
            ),
            QuranVerse(
                surah_number=1, verse_number=4,
                arabic_text="مَالِكِ يَوْمِ الدِّينِ",
                translation_ru="Владыке Дня воздаяния!",
                commentary="Аллах - единственный судья в Судный день.",
                confession='sunni'
            ),
            QuranVerse(
                surah_number=1, verse_number=5,
                arabic_text="إِيَّاكَ نَعْبُدُ وَإِيَّاكَ نَسْتَعِينُ",
                translation_ru="Тебе одному мы поклоняемся и Тебя одного молим о помощи.",
                commentary="Признание единобожия и просьба о помощи.",
                confession='sunni'
            ),
            QuranVerse(
                surah_number=1, verse_number=6,
                arabic_text="اهْدِنَا الصِّرَاطَ الْمُسْتَقِيمَ",
                translation_ru="Веди нас прямым путем,",
                commentary="Просьба о наставлении на правильный путь.",
                confession='sunni'
            ),
            QuranVerse(
                surah_number=1, verse_number=7,
                arabic_text="صِرَاطَ الَّذِينَ أَنْعَمْتَ عَلَيْهِمْ غَيْرِ الْمَغْضُوبِ عَلَيْهِمْ وَلَا الضَّالِّينَ",
                translation_ru="путем тех, кого Ты облагодетельствовал, не тех, на кого пал гнев, и не заблудших.",
                commentary="Просьба следовать путем праведников, а не заблудших.",
                confession='sunni'
            ),
            
            # Сура 2 - Аль-Бакара
            QuranVerse(
                surah_number=2, verse_number=1,
                arabic_text="الم",
                translation_ru="Алиф. Лям. Мим.",
                commentary="Загадочные буквы в начале суры.",
                confession='sunni'
            ),
            QuranVerse(
                surah_number=2, verse_number=2,
                arabic_text="ذَٰلِكَ الْكِتَابُ لَا رَيْبَ ۛ فِيهِ ۛ هُدًى لِّلْمُتَّقِينَ",
                translation_ru="Это Писание, в котором нет сомнения, является верным руководством для богобоязненных,",
                commentary="Коран - руководство для богобоязненных.",
                confession='sunni'
            ),
            QuranVerse(
                surah_number=2, verse_number=3,
                arabic_text="الَّذِينَ يُؤْمِنُونَ بِالْغَيْبِ وَيُقِيمُونَ الصَّلَاةَ وَمِمَّا رَزَقْنَاهُمْ يُنفِقُونَ",
                translation_ru="которые веруют в сокровенное, совершают намаз и расходуют из того, чем Мы их наделили.",
                commentary="Описание качеств богобоязненных.",
                confession='sunni'
            ),
            
            # Дополнительные аяты для шиитов
            QuranVerse(
                surah_number=1, verse_number=1,
                arabic_text="بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ",
                translation_ru="Во имя Аллаха, Милостивого, Милосердного!",
                commentary="Начало каждой суры Корана в шиитской традиции.",
                confession='shia'
            ),
            QuranVerse(
                surah_number=2, verse_number=3,
                arabic_text="الَّذِينَ يُؤْمِنُونَ بِالْغَيْبِ وَيُقِيمُونَ الصَّلَاةَ وَمِمَّا رَزَقْنَاهُمْ يُنفِقُونَ",
                translation_ru="которые веруют в сокровенное, совершают намаз и расходуют из того, чем Мы их наделили.",
                commentary="Вера в сокровенное включает веру в имамат в шиизме.",
                confession='shia'
            ),
        ]
        
        for verse in extended_quran_verses:
            # Проверяем, не существует ли уже такой аят
            existing = self.db.query(QuranVerse).filter(
                QuranVerse.surah_number == verse.surah_number,
                QuranVerse.verse_number == verse.verse_number,
                QuranVerse.confession == verse.confession
            ).first()
            
            if not existing:
                self.db.add(verse)
                self.loaded_count += 1
        
        self.db.commit()
        logger.info(f"✅ Загружено {len(extended_quran_verses)} аятов Корана")
    
    def _load_extended_hadith_data(self):
        """Загружает расширенные хадисы"""
        logger.info("📜 Загружаем расширенные хадисы...")
        
        extended_hadiths = [
            # Суннитские хадисы
            Hadith(
                collection="Бухари",
                chapter="Начало Откровения",
                number=1,
                text_arabic="إنما الأعمال بالنيات",
                text_russian="Поистине, дела (оцениваются) только по намерениям.",
                commentary="Важность намерения в исламе.",
                confession='sunni'
            ),
            Hadith(
                collection="Бухари",
                chapter="Вера",
                number=2,
                text_arabic="بني الإسلام على خمس",
                text_russian="Ислам построен на пяти (столпах).",
                commentary="Пять столпов ислама.",
                confession='sunni'
            ),
            Hadith(
                collection="Муслим",
                chapter="Вера",
                number=1,
                text_arabic="الإيمان بضع وسبعون شعبة",
                text_russian="Вера имеет более семидесяти ответвлений.",
                commentary="Вера включает в себя множество аспектов.",
                confession='sunni'
            ),
            Hadith(
                collection="Бухари",
                chapter="Молитва",
                number=1,
                text_arabic="الصلاة عمود الدين",
                text_russian="Молитва - столп религии.",
                commentary="Важность молитвы в исламе.",
                confession='sunni'
            ),
            Hadith(
                collection="Муслим",
                chapter="Семья",
                number=1,
                text_arabic="خيركم خيركم لأهله",
                text_russian="Лучший из вас - тот, кто лучше всех относится к своей семье.",
                commentary="Важность хорошего отношения к семье.",
                confession='sunni'
            ),
            
            # Шиитские хадисы
            Hadith(
                collection="Аль-Кафи",
                chapter="Книга разума и невежества",
                number=1,
                text_arabic="عن أبي عبد الله عليه السلام قال: دعائم الكفر ثلاثة: الحرص والاستكبار والحسد",
                text_russian="От Абу Абдуллаха (мир ему) передано: Столпов неверия три: алчность, высокомерие и зависть.",
                commentary="Основы неверия в шиитском исламе.",
                confession='shia'
            ),
            Hadith(
                collection="Аль-Кафи",
                chapter="Книга веры и неверия",
                number=2,
                text_arabic="عن أبي جعفر عليه السلام قال: الإيمان معرفة بالقلب وإقرار باللسان وعمل بالأركان",
                text_russian="От Абу Джафара (мир ему) передано: Вера - это познание сердцем, признание языком и действие органами.",
                commentary="Определение веры в шиизме.",
                confession='shia'
            ),
            Hadith(
                collection="Аль-Кафи",
                chapter="Книга молитвы",
                number=1,
                text_arabic="عن أبي عبد الله عليه السلام قال: الصلاة قربان كل تقي",
                text_russian="От Абу Абдуллаха (мир ему) передано: Молитва - жертвоприношение каждого благочестивого.",
                commentary="Значение молитвы в шиизме.",
                confession='shia'
            ),
        ]
        
        for hadith in extended_hadiths:
            # Проверяем, не существует ли уже такой хадис
            existing = self.db.query(Hadith).filter(
                Hadith.collection == hadith.collection,
                Hadith.number == hadith.number,
                Hadith.confession == hadith.confession
            ).first()
            
            if not existing:
                self.db.add(hadith)
                self.loaded_count += 1
        
        self.db.commit()
        logger.info(f"✅ Загружено {len(extended_hadiths)} хадисов")
    
    def _load_extended_orthodox_data(self):
        """Загружает расширенные православные тексты"""
        logger.info("⛪ Загружаем расширенные православные тексты...")
        
        # Создаем фиктивный документ
        doc = OrthodoxDocument(
            filename="extended_orthodox_sources.txt",
            title="Расширенные православные источники",
            author="Система",
            document_type="Сборник",
            file_path="/app/data/Православие/extended_sources.txt",
            file_size=1024,
            confession='orthodox',
            processed=1,
            processed_at=datetime.utcnow(),
            pages_count=1
        )
        self.db.add(doc)
        self.db.flush()
        
        extended_orthodox_texts = [
            # Библия
            OrthodoxText(
                document_id=doc.id,
                confession='orthodox',
                source_type='Библия',
                book_name='Евангелие от Матфея',
                chapter_number=6,
                verse_number=9,
                original_text='Отче наш, сущий на небесах! да святится имя Твое;',
                translation_ru='Отче наш, сущий на небесах! да святится имя Твое;',
                commentary='Начало молитвы Господней.',
                theme='Молитва'
            ),
            OrthodoxText(
                document_id=doc.id,
                confession='orthodox',
                source_type='Библия',
                book_name='Евангелие от Матфея',
                chapter_number=6,
                verse_number=10,
                original_text='да приидет Царствие Твое; да будет воля Твоя и на земле, как на небе;',
                translation_ru='да приидет Царствие Твое; да будет воля Твоя и на земле, как на небе;',
                commentary='Просьба о пришествии Царства Божия.',
                theme='Молитва'
            ),
            OrthodoxText(
                document_id=doc.id,
                confession='orthodox',
                source_type='Библия',
                book_name='Послание к Евреям',
                chapter_number=11,
                verse_number=1,
                original_text='Вера же есть осуществление ожидаемого и уверенность в невидимом.',
                translation_ru='Вера же есть осуществление ожидаемого и уверенность в невидимом.',
                commentary='Определение веры в христианстве.',
                theme='Вера'
            ),
            OrthodoxText(
                document_id=doc.id,
                confession='orthodox',
                source_type='Библия',
                book_name='Первое послание к Коринфянам',
                chapter_number=13,
                verse_number=4,
                original_text='Любовь долготерпит, милосердствует, любовь не завидует, любовь не превозносится, не гордится,',
                translation_ru='Любовь долготерпит, милосердствует, любовь не завидует, любовь не превозносится, не гордится,',
                commentary='Описание свойств христианской любви.',
                theme='Любовь'
            ),
            OrthodoxText(
                document_id=doc.id,
                confession='orthodox',
                source_type='Библия',
                book_name='Евангелие от Иоанна',
                chapter_number=3,
                verse_number=16,
                original_text='Ибо так возлюбил Бог мир, что отдал Сына Своего Единородного, дабы всякий, верующий в Него, не погиб, но имел жизнь вечную.',
                translation_ru='Ибо так возлюбил Бог мир, что отдал Сына Своего Единородного, дабы всякий, верующий в Него, не погиб, но имел жизнь вечную.',
                commentary='Любовь Божия к миру.',
                theme='Любовь'
            ),
            
            # Святоотеческие труды
            OrthodoxText(
                document_id=doc.id,
                confession='orthodox',
                source_type='Святоотеческие труды',
                book_name='Лествица',
                author='Преподобный Иоанн Лествичник',
                chapter_number=28,
                verse_number=1,
                original_text='Молитва есть возношение ума к Богу.',
                translation_ru='Молитва есть возношение ума к Богу.',
                commentary='Краткое определение молитвы.',
                theme='Молитва'
            ),
            OrthodoxText(
                document_id=doc.id,
                confession='orthodox',
                source_type='Святоотеческие труды',
                book_name='Лествица',
                author='Преподобный Иоанн Лествичник',
                chapter_number=28,
                verse_number=2,
                original_text='Молитва есть матерь и дочь слез.',
                translation_ru='Молитва есть матерь и дочь слез.',
                commentary='Связь молитвы с покаянием.',
                theme='Молитва'
            ),
            OrthodoxText(
                document_id=doc.id,
                confession='orthodox',
                source_type='Святоотеческие труды',
                book_name='О Святом Духе',
                author='Святитель Василий Великий',
                chapter_number=1,
                verse_number=1,
                original_text='Дух Святой есть источник освящения.',
                translation_ru='Дух Святой есть источник освящения.',
                commentary='Роль Святого Духа в освящении.',
                theme='Святой Дух'
            ),
            
            # Догматика
            OrthodoxText(
                document_id=doc.id,
                confession='orthodox',
                source_type='Догматика',
                book_name='Православное догматическое богословие',
                author='Протопресвитер Михаил Помазанский',
                chapter_number=1,
                verse_number=1,
                original_text='Бог есть Дух, и поклоняющиеся Ему должны поклоняться в духе и истине.',
                translation_ru='Бог есть Дух, и поклоняющиеся Ему должны поклоняться в духе и истине.',
                commentary='Природа Бога и поклонения.',
                theme='Бог'
            ),
            OrthodoxText(
                document_id=doc.id,
                confession='orthodox',
                source_type='Догматика',
                book_name='Православное догматическое богословие',
                author='Протопресвитер Михаил Помазанский',
                chapter_number=2,
                verse_number=1,
                original_text='Троица есть единый Бог в трех Лицах.',
                translation_ru='Троица есть единый Бог в трех Лицах.',
                commentary='Догмат о Святой Троице.',
                theme='Троица'
            ),
            
            # Тексты о семье и отношениях
            OrthodoxText(
                document_id=doc.id,
                confession='orthodox',
                source_type='Библия',
                book_name='Евангелие от Матфея',
                chapter_number=18,
                verse_number=21,
                original_text='Тогда Петр приступил к Нему и сказал: Господи! сколько раз прощать брату моему, согрешающему против меня? до семи ли раз?',
                translation_ru='Тогда Петр приступил к Нему и сказал: Господи! сколько раз прощать брату моему, согрешающему против меня? до семи ли раз?',
                commentary='Вопрос о прощении в семье.',
                theme='Прощение'
            ),
            OrthodoxText(
                document_id=doc.id,
                confession='orthodox',
                source_type='Библия',
                book_name='Евангелие от Матфея',
                chapter_number=18,
                verse_number=22,
                original_text='Иисус говорит ему: не говорю тебе: до семи раз, но до седмижды семидесяти раз.',
                translation_ru='Иисус говорит ему: не говорю тебе: до семи раз, но до седмижды семидесяти раз.',
                commentary='Бесконечное прощение.',
                theme='Прощение'
            ),
            OrthodoxText(
                document_id=doc.id,
                confession='orthodox',
                source_type='Библия',
                book_name='Послание к Ефесянам',
                chapter_number=4,
                verse_number=26,
                original_text='Гневаясь, не согрешайте: солнце да не зайдет во гневе вашем.',
                translation_ru='Гневаясь, не согрешайте: солнце да не зайдет во гневе вашем.',
                commentary='О гневе и прощении.',
                theme='Гнев'
            ),
            OrthodoxText(
                document_id=doc.id,
                confession='orthodox',
                source_type='Библия',
                book_name='Послание к Ефесянам',
                chapter_number=4,
                verse_number=32,
                original_text='Но будьте друг ко другу добры, сострадательны, прощайте друг друга, как и Бог во Христе простил вас.',
                translation_ru='Но будьте друг ко другу добры, сострадательны, прощайте друг друга, как и Бог во Христе простил вас.',
                commentary='Призыв к прощению в семье.',
                theme='Прощение'
            ),
        ]
        
        for text in extended_orthodox_texts:
            # Проверяем, не существует ли уже такой текст
            existing = self.db.query(OrthodoxText).filter(
                OrthodoxText.book_name == text.book_name,
                OrthodoxText.chapter_number == text.chapter_number,
                OrthodoxText.verse_number == text.verse_number,
                OrthodoxText.confession == text.confession
            ).first()
            
            if not existing:
                self.db.add(text)
                self.loaded_count += 1
        
        self.db.commit()
        logger.info(f"✅ Загружено {len(extended_orthodox_texts)} православных текстов")
    
    def close(self):
        """Закрывает соединение с базой данных"""
        self.db.close()

def main():
    """Основная функция"""
    loader = ProductionDataLoader()
    try:
        loader.load_extended_sample_data()
        logger.info("🎉 Расширенные данные успешно загружены!")
    except Exception as e:
        logger.error(f"❌ Ошибка загрузки данных: {e}")
    finally:
        loader.close()

if __name__ == "__main__":
    main()
