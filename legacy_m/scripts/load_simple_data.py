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
            # Суннитские аяты
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
                surah_number=112, verse_number=1,
                arabic_text="قُلْ هُوَ اللَّهُ أَحَدٌ",
                translation_ru="Скажи: «Он - Аллах Единый»",
                commentary="Сура о единобожии.",
                confession='sunni'
            ),
            QuranVerse(
                surah_number=2, verse_number=255,
                arabic_text="اللَّهُ لَا إِلَٰهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ",
                translation_ru="Аллах - нет божества, кроме Него, Живого, Поддерживающего жизнь.",
                commentary="Аят аль-Курси - о величии Аллаха.",
                confession='sunni'
            ),
            # Шиитские аяты
            QuranVerse(
                surah_number=1, verse_number=1,
                arabic_text="بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ",
                translation_ru="Во имя Аллаха, Милостивого, Милосердного!",
                commentary="Начало каждой суры Корана.",
                confession='shia'
            ),
            QuranVerse(
                surah_number=33, verse_number=33,
                arabic_text="إِنَّمَا يُرِيدُ اللَّهُ لِيُذْهِبَ عَنكُمُ الرِّجْسَ أَهْلَ الْبَيْتِ وَيُطَهِّرَكُمْ تَطْهِيرًا",
                translation_ru="Аллах желает только удалить скверну от вас, о люди дома, и очистить вас полностью.",
                commentary="Аят о чистоте Ахль аль-Байт.",
                confession='shia'
            ),
            QuranVerse(
                surah_number=5, verse_number=55,
                arabic_text="إِنَّمَا وَلِيُّكُمُ اللَّهُ وَرَسُولُهُ وَالَّذِينَ آمَنُوا الَّذِينَ يُقِيمُونَ الصَّلَاةَ وَيُؤْتُونَ الزَّكَاةَ وَهُمْ رَاكِعُونَ",
                translation_ru="Воистину, вашим покровителем является только Аллах, Его Посланник и верующие, которые совершают намаз, выплачивают закят и преклоняются.",
                commentary="Аят о вилайе (покровительстве).",
                confession='shia'
            )
        ]
        db.add_all(quran_verses)
        
        # Загружаем хадисы
        logger.info("📜 Загружаем хадисы...")
        hadiths = [
            # Суннитские хадисы
            Hadith(
                collection="Бухари",
                hadith_number=1,
                arabic_text="إنما الأعمال بالنيات",
                translation_ru="Поистине, дела (оцениваются) только по намерениям.",
                commentary="Один из самых важных хадисов в исламе.",
                confession='sunni'
            ),
            Hadith(
                collection="Бухари",
                hadith_number=2,
                arabic_text="من حسن إسلام المرء تركه ما لا يعنيه",
                translation_ru="Признаком хорошего ислама человека является то, что он оставляет то, что его не касается.",
                commentary="О важности невмешательства в чужие дела.",
                confession='sunni'
            ),
            Hadith(
                collection="Муслим",
                hadith_number=1,
                arabic_text="لا يؤمن أحدكم حتى يحب لأخيه ما يحب لنفسه",
                translation_ru="Не уверует никто из вас, пока не будет желать своему брату того же, чего желает себе.",
                commentary="О любви к ближнему.",
                confession='sunni'
            ),
            # Шиитские хадисы
            Hadith(
                collection="Аль-Кафи",
                hadith_number=1,
                arabic_text="عن أبي عبد الله عليه السلام قال: دعائم الكفر ثلاثة: الحرص والاستكبار والحسد",
                translation_ru="От Абу Абдуллаха (мир ему) передано: Столпов неверия три: алчность, высокомерие и зависть.",
                commentary="Основы неверия в шиитском исламе.",
                confession='shia'
            ),
            Hadith(
                collection="Аль-Кафи",
                hadith_number=2,
                arabic_text="عن الإمام الصادق عليه السلام: إن الله عز وجل خلق العقل فقال له: أقبل فأقبل، وقال له: أدبر فأدبر",
                translation_ru="От Имама Садыка (мир ему): Поистине, Аллах создал разум и сказал ему: 'Приди', и он пришел, и сказал: 'Уйди', и он ушел.",
                commentary="О важности разума в исламе.",
                confession='shia'
            ),
            Hadith(
                collection="Аль-Кафи",
                hadith_number=3,
                arabic_text="عن الإمام علي عليه السلام: الناس ثلاثة: عالم رباني، ومتعلم على سبيل نجاة، وهمج رعاع",
                translation_ru="От Имама Али (мир ему): Люди делятся на три категории: божественный ученый, ученик на пути спасения, и невежественная толпа.",
                commentary="О категориях людей по знаниям.",
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
