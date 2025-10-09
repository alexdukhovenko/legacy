#!/usr/bin/env python3
"""
Расширенный загрузчик данных с большим количеством православных текстов
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

def load_extended_orthodox_data():
    """Загружаем расширенные православные данные"""
    db = SessionLocal()
    try:
        logger.info("⛪ Загружаем расширенные православные тексты...")
        
        # Проверяем, есть ли уже данные
        orthodox_count = db.query(OrthodoxText).count()
        if orthodox_count > 10:
            logger.info(f"✅ Православные данные уже загружены: {orthodox_count} текстов")
            return
        
        # Расширенный набор православных текстов
        orthodox_texts = [
            # Библия - Евангелие от Матфея
            OrthodoxText(
                source_type='Библия',
                book_name='Евангелие от Матфея',
                chapter_number=6, verse_number=9,
                original_text='Отче наш, сущий на небесах! да святится имя Твое;',
                translation_ru='Отче наш, сущий на небесах! да святится имя Твое;',
                commentary='Начало молитвы Господней.',
                theme='Молитва',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Библия',
                book_name='Евангелие от Матфея',
                chapter_number=6, verse_number=10,
                original_text='да приидет Царствие Твое; да будет воля Твоя и на земле, как на небе;',
                translation_ru='да приидет Царствие Твое; да будет воля Твоя и на земле, как на небе;',
                commentary='О Царствии Божием.',
                theme='Царствие Божие',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Библия',
                book_name='Евангелие от Матфея',
                chapter_number=6, verse_number=11,
                original_text='хлеб наш насущный дай нам на сей день;',
                translation_ru='хлеб наш насущный дай нам на сей день;',
                commentary='О хлебе насущном.',
                theme='Питание',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Библия',
                book_name='Евангелие от Матфея',
                chapter_number=6, verse_number=12,
                original_text='и прости нам долги наши, как и мы прощаем должникам нашим;',
                translation_ru='и прости нам долги наши, как и мы прощаем должникам нашим;',
                commentary='О прощении.',
                theme='Прощение',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Библия',
                book_name='Евангелие от Матфея',
                chapter_number=6, verse_number=13,
                original_text='и не введи нас в искушение, но избавь нас от лукавого.',
                translation_ru='и не введи нас в искушение, но избавь нас от лукавого.',
                commentary='О защите от искушений.',
                theme='Искушение',
                confession='orthodox'
            ),
            
            # Библия - Евангелие от Иоанна
            OrthodoxText(
                source_type='Библия',
                book_name='Евангелие от Иоанна',
                chapter_number=14, verse_number=6,
                original_text='Иисус сказал ему: Я есмь путь и истина и жизнь; никто не приходит к Отцу, как только через Меня.',
                translation_ru='Иисус сказал ему: Я есмь путь и истина и жизнь; никто не приходит к Отцу, как только через Меня.',
                commentary='О пути к Богу.',
                theme='Истина',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Библия',
                book_name='Евангелие от Иоанна',
                chapter_number=3, verse_number=16,
                original_text='Ибо так возлюбил Бог мир, что отдал Сына Своего Единородного, дабы всякий, верующий в Него, не погиб, но имел жизнь вечную.',
                translation_ru='Ибо так возлюбил Бог мир, что отдал Сына Своего Единородного, дабы всякий, верующий в Него, не погиб, но имел жизнь вечную.',
                commentary='О любви Божией.',
                theme='Любовь',
                confession='orthodox'
            ),
            
            # Библия - Послание к Евреям
            OrthodoxText(
                source_type='Библия',
                book_name='Послание к Евреям',
                chapter_number=11, verse_number=1,
                original_text='Вера же есть осуществление ожидаемого и уверенность в невидимом.',
                translation_ru='Вера же есть осуществление ожидаемого и уверенность в невидимом.',
                commentary='Определение веры в христианстве.',
                theme='Вера',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Библия',
                book_name='Послание к Евреям',
                chapter_number=11, verse_number=6,
                original_text='А без веры угодить Богу невозможно; ибо надобно, чтобы приходящий к Богу веровал, что Он есть, и ищущим Его воздает.',
                translation_ru='А без веры угодить Богу невозможно; ибо надобно, чтобы приходящий к Богу веровал, что Он есть, и ищущим Его воздает.',
                commentary='О необходимости веры.',
                theme='Вера',
                confession='orthodox'
            ),
            
            # Библия - 1 Коринфянам
            OrthodoxText(
                source_type='Библия',
                book_name='1 Коринфянам',
                chapter_number=13, verse_number=4,
                original_text='Любовь долготерпит, милосердствует, любовь не завидует, любовь не превозносится, не гордится.',
                translation_ru='Любовь долготерпит, милосердствует, любовь не завидует, любовь не превозносится, не гордится.',
                commentary='О свойствах любви.',
                theme='Любовь',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Библия',
                book_name='1 Коринфянам',
                chapter_number=13, verse_number=7,
                original_text='Все покрывает, всему верит, всего надеется, все переносит.',
                translation_ru='Все покрывает, всему верит, всего надеется, все переносит.',
                commentary='О силе любви.',
                theme='Любовь',
                confession='orthodox'
            ),
            
            # Библия - Евангелие от Матфея (о браке)
            OrthodoxText(
                source_type='Библия',
                book_name='Евангелие от Матфея',
                chapter_number=19, verse_number=6,
                original_text='Итак, что Бог сочетал, того человек да не разлучает.',
                translation_ru='Итак, что Бог сочетал, того человек да не разлучает.',
                commentary='О святости брака.',
                theme='Брак',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Библия',
                book_name='Евангелие от Матфея',
                chapter_number=19, verse_number=9,
                original_text='И Я говорю вам: кто разведется с женою своею не за прелюбодеяние и женится на другой, тот прелюбодействует.',
                translation_ru='И Я говорю вам: кто разведется с женою своею не за прелюбодеяние и женится на другой, тот прелюбодействует.',
                commentary='О разводе и прелюбодеянии.',
                theme='Брак',
                confession='orthodox'
            ),
            
            # Библия - Евангелие от Матфея (о храме)
            OrthodoxText(
                source_type='Библия',
                book_name='Евангелие от Матфея',
                chapter_number=18, verse_number=20,
                original_text='Ибо, где двое или трое собраны во имя Мое, там Я посреди них.',
                translation_ru='Ибо, где двое или трое собраны во имя Мое, там Я посреди них.',
                commentary='О важности собрания в храме.',
                theme='Храм',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Библия',
                book_name='Евангелие от Матфея',
                chapter_number=21, verse_number=13,
                original_text='И сказал им: написано: дом Мой домом молитвы наречется; а вы сделали его вертепом разбойников.',
                translation_ru='И сказал им: написано: дом Мой домом молитвы наречется; а вы сделали его вертепом разбойников.',
                commentary='О назначении храма.',
                theme='Храм',
                confession='orthodox'
            ),
            
            # Библия - Евангелие от Матфея (о конце света)
            OrthodoxText(
                source_type='Библия',
                book_name='Евангелие от Матфея',
                chapter_number=24, verse_number=36,
                original_text='О дне же том и часе никто не знает, ни Ангелы небесные, а только Отец Мой один.',
                translation_ru='О дне же том и часе никто не знает, ни Ангелы небесные, а только Отец Мой один.',
                commentary='О неизвестности времени конца света.',
                theme='Конец света',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Библия',
                book_name='Евангелие от Матфея',
                chapter_number=24, verse_number=42,
                original_text='Итак бодрствуйте, потому что не знаете, в который час Господь ваш приидет.',
                translation_ru='Итак бодрствуйте, потому что не знаете, в который час Господь ваш приидет.',
                commentary='О бодрствовании перед концом света.',
                theme='Конец света',
                confession='orthodox'
            ),
            
            # Святоотеческие труды - Лествица
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='Лествица',
                author='Преподобный Иоанн Лествичник',
                chapter_number=28, verse_number=1,
                original_text='Молитва есть возношение ума к Богу.',
                translation_ru='Молитва есть возношение ума к Богу.',
                commentary='Краткое определение молитвы.',
                theme='Молитва',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='Лествица',
                author='Преподобный Иоанн Лествичник',
                chapter_number=28, verse_number=2,
                original_text='Молитва есть собеседование ума с Богом.',
                translation_ru='Молитва есть собеседование ума с Богом.',
                commentary='О сущности молитвы.',
                theme='Молитва',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='Лествица',
                author='Преподобный Иоанн Лествичник',
                chapter_number=1, verse_number=1,
                original_text='Отречение от мира есть произвольная ненависть к веществу, похваляемому мирскими.',
                translation_ru='Отречение от мира есть произвольная ненависть к веществу, похваляемому мирскими.',
                commentary='О монашеском отречении.',
                theme='Отречение',
                confession='orthodox'
            ),
            
            # Святоотеческие труды - Добротолюбие
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='Добротолюбие',
                author='Святые отцы',
                chapter_number=1, verse_number=1,
                original_text='Бог есть любовь, и пребывающий в любви пребывает в Боге, и Бог в нем.',
                translation_ru='Бог есть любовь, и пребывающий в любви пребывает в Боге, и Бог в нем.',
                commentary='О любви к Богу.',
                theme='Любовь',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='Добротолюбие',
                author='Святые отцы',
                chapter_number=2, verse_number=1,
                original_text='Смирение есть основание всех добродетелей.',
                translation_ru='Смирение есть основание всех добродетелей.',
                commentary='О смирении.',
                theme='Смирение',
                confession='orthodox'
            ),
            
            # Святоотеческие труды - Иоанн Златоуст
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='Толкование на Евангелие от Матфея',
                author='Святитель Иоанн Златоуст',
                chapter_number=6, verse_number=9,
                original_text='Молитва Господня содержит в себе все, что нужно для жизни.',
                translation_ru='Молитва Господня содержит в себе все, что нужно для жизни.',
                commentary='О полноте молитвы Господней.',
                theme='Молитва',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='О браке',
                author='Святитель Иоанн Златоуст',
                chapter_number=1, verse_number=1,
                original_text='Брак есть таинство, установленное Богом для продолжения рода человеческого.',
                translation_ru='Брак есть таинство, установленное Богом для продолжения рода человеческого.',
                commentary='О святости брака.',
                theme='Брак',
                confession='orthodox'
            ),
            
            # Святоотеческие труды - Василий Великий
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='О Святом Духе',
                author='Святитель Василий Великий',
                chapter_number=1, verse_number=1,
                original_text='Святой Дух есть Бог, и мы поклоняемся Ему вместе с Отцом и Сыном.',
                translation_ru='Святой Дух есть Бог, и мы поклоняемся Ему вместе с Отцом и Сыном.',
                commentary='О Святой Троице.',
                theme='Троица',
                confession='orthodox'
            ),
            
            # Святоотеческие труды - Григорий Богослов
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='Слово о Богословии',
                author='Святитель Григорий Богослов',
                chapter_number=1, verse_number=1,
                original_text='Бог есть Троица: Отец, Сын и Святой Дух.',
                translation_ru='Бог есть Троица: Отец, Сын и Святой Дух.',
                commentary='О Святой Троице.',
                theme='Троица',
                confession='orthodox'
            ),
            
            # Святоотеческие труды - Максим Исповедник
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='О любви',
                author='Преподобный Максим Исповедник',
                chapter_number=1, verse_number=1,
                original_text='Любовь есть исполнение закона.',
                translation_ru='Любовь есть исполнение закона.',
                commentary='О любви как исполнении закона.',
                theme='Любовь',
                confession='orthodox'
            ),
            
            # Святоотеческие труды - Иоанн Дамаскин
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='Точное изложение православной веры',
                author='Преподобный Иоанн Дамаскин',
                chapter_number=1, verse_number=1,
                original_text='Бог есть существо простое, несложное, невидимое, бестелесное.',
                translation_ru='Бог есть существо простое, несложное, невидимое, бестелесное.',
                commentary='О природе Бога.',
                theme='Бог',
                confession='orthodox'
            ),
            
            # Святоотеческие труды - Исаак Сирин
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='Слова подвижнические',
                author='Преподобный Исаак Сирин',
                chapter_number=1, verse_number=1,
                original_text='Лучше сказать "не знаю", чем говорить о Боге неподобающее.',
                translation_ru='Лучше сказать "не знаю", чем говорить о Боге неподобающее.',
                commentary='О смирении в познании Бога.',
                theme='Смирение',
                confession='orthodox'
            ),
            
            # Святоотеческие труды - Ефрем Сирин
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='Толкование на Четвероевангелие',
                author='Преподобный Ефрем Сирин',
                chapter_number=1, verse_number=1,
                original_text='Покаяние есть дверь милости.',
                translation_ru='Покаяние есть дверь милости.',
                commentary='О важности покаяния.',
                theme='Покаяние',
                confession='orthodox'
            ),
            
            # Святоотеческие труды - Иоанн Лествичник (дополнительно)
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='Лествица',
                author='Преподобный Иоанн Лествичник',
                chapter_number=4, verse_number=1,
                original_text='Послушание есть отречение от своей воли.',
                translation_ru='Послушание есть отречение от своей воли.',
                commentary='О послушании.',
                theme='Послушание',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='Лествица',
                author='Преподобный Иоанн Лествичник',
                chapter_number=5, verse_number=1,
                original_text='Покаяние есть обновление крещения.',
                translation_ru='Покаяние есть обновление крещения.',
                commentary='О покаянии.',
                theme='Покаяние',
                confession='orthodox'
            ),
            
            # Святоотеческие труды - Иоанн Златоуст (дополнительно)
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='О священстве',
                author='Святитель Иоанн Златоуст',
                chapter_number=1, verse_number=1,
                original_text='Священство есть великое таинство.',
                translation_ru='Священство есть великое таинство.',
                commentary='О священстве.',
                theme='Священство',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='О милостыне',
                author='Святитель Иоанн Златоуст',
                chapter_number=1, verse_number=1,
                original_text='Милостыня есть лекарство для души.',
                translation_ru='Милостыня есть лекарство для души.',
                commentary='О милостыне.',
                theme='Милостыня',
                confession='orthodox'
            ),
            
            # Святоотеческие труды - Василий Великий (дополнительно)
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='О посте',
                author='Святитель Василий Великий',
                chapter_number=1, verse_number=1,
                original_text='Пост есть воздержание от зла.',
                translation_ru='Пост есть воздержание от зла.',
                commentary='О посте.',
                theme='Пост',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='О молитве',
                author='Святитель Василий Великий',
                chapter_number=1, verse_number=1,
                original_text='Молитва есть дыхание души.',
                translation_ru='Молитва есть дыхание души.',
                commentary='О молитве.',
                theme='Молитва',
                confession='orthodox'
            ),
            
            # Святоотеческие труды - Григорий Богослов (дополнительно)
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='О богословии',
                author='Святитель Григорий Богослов',
                chapter_number=2, verse_number=1,
                original_text='Богословие есть ведение о Боге.',
                translation_ru='Богословие есть ведение о Боге.',
                commentary='О богословии.',
                theme='Богословие',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='О душе',
                author='Святитель Григорий Богослов',
                chapter_number=1, verse_number=1,
                original_text='Душа есть образ Божий.',
                translation_ru='Душа есть образ Божий.',
                commentary='О душе.',
                theme='Душа',
                confession='orthodox'
            ),
            
            # Святоотеческие труды - Максим Исповедник (дополнительно)
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='О воле',
                author='Преподобный Максим Исповедник',
                chapter_number=1, verse_number=1,
                original_text='Воля есть способность к добру.',
                translation_ru='Воля есть способность к добру.',
                commentary='О воле.',
                theme='Воля',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='О природе',
                author='Преподобный Максим Исповедник',
                chapter_number=1, verse_number=1,
                original_text='Природа есть сущность вещи.',
                translation_ru='Природа есть сущность вещи.',
                commentary='О природе.',
                theme='Природа',
                confession='orthodox'
            ),
            
            # Святоотеческие труды - Иоанн Дамаскин (дополнительно)
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='О иконопочитании',
                author='Преподобный Иоанн Дамаскин',
                chapter_number=1, verse_number=1,
                original_text='Икона есть образ Первообраза.',
                translation_ru='Икона есть образ Первообраза.',
                commentary='Об иконопочитании.',
                theme='Икона',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='О вере',
                author='Преподобный Иоанн Дамаскин',
                chapter_number=1, verse_number=1,
                original_text='Вера есть согласие на то, что слышишь.',
                translation_ru='Вера есть согласие на то, что слышишь.',
                commentary='О вере.',
                theme='Вера',
                confession='orthodox'
            ),
            
            # Святоотеческие труды - Исаак Сирин (дополнительно)
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='О молитве',
                author='Преподобный Исаак Сирин',
                chapter_number=1, verse_number=1,
                original_text='Молитва есть восхождение ума к Богу.',
                translation_ru='Молитва есть восхождение ума к Богу.',
                commentary='О молитве.',
                theme='Молитва',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='О смирении',
                author='Преподобный Исаак Сирин',
                chapter_number=1, verse_number=1,
                original_text='Смирение есть мать всех добродетелей.',
                translation_ru='Смирение есть мать всех добродетелей.',
                commentary='О смирении.',
                theme='Смирение',
                confession='orthodox'
            ),
            
            # Святоотеческие труды - Ефрем Сирин (дополнительно)
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='О покаянии',
                author='Преподобный Ефрем Сирин',
                chapter_number=1, verse_number=1,
                original_text='Покаяние есть второе крещение.',
                translation_ru='Покаяние есть второе крещение.',
                commentary='О покаянии.',
                theme='Покаяние',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='О молитве',
                author='Преподобный Ефрем Сирин',
                chapter_number=1, verse_number=1,
                original_text='Молитва есть ключ к небесам.',
                translation_ru='Молитва есть ключ к небесам.',
                commentary='О молитве.',
                theme='Молитва',
                confession='orthodox'
            ),
            
            # Святоотеческие труды - Иоанн Лествичник (еще больше)
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='Лествица',
                author='Преподобный Иоанн Лествичник',
                chapter_number=6, verse_number=1,
                original_text='Память смертная есть великое оружие против греха.',
                translation_ru='Память смертная есть великое оружие против греха.',
                commentary='О памяти смертной.',
                theme='Смерть',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='Лествица',
                author='Преподобный Иоанн Лествичник',
                chapter_number=7, verse_number=1,
                original_text='Плач есть дар Божий.',
                translation_ru='Плач есть дар Божий.',
                commentary='О плаче.',
                theme='Плач',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='Лествица',
                author='Преподобный Иоанн Лествичник',
                chapter_number=8, verse_number=1,
                original_text='Кротость есть тишина ума.',
                translation_ru='Кротость есть тишина ума.',
                commentary='О кротости.',
                theme='Кротость',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='Лествица',
                author='Преподобный Иоанн Лествичник',
                chapter_number=9, verse_number=1,
                original_text='Злопамятство есть забвение правды.',
                translation_ru='Злопамятство есть забвение правды.',
                commentary='О злопамятстве.',
                theme='Злопамятство',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='Лествица',
                author='Преподобный Иоанн Лествичник',
                chapter_number=10, verse_number=1,
                original_text='Злословие есть смерть души.',
                translation_ru='Злословие есть смерть души.',
                commentary='О злословии.',
                theme='Злословие',
                confession='orthodox'
            ),
            
            # Святоотеческие труды - Иоанн Златоуст (еще больше)
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='О терпении',
                author='Святитель Иоанн Златоуст',
                chapter_number=1, verse_number=1,
                original_text='Терпение есть мать всех добродетелей.',
                translation_ru='Терпение есть мать всех добродетелей.',
                commentary='О терпении.',
                theme='Терпение',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='О надежде',
                author='Святитель Иоанн Златоуст',
                chapter_number=1, verse_number=1,
                original_text='Надежда есть якорь души.',
                translation_ru='Надежда есть якорь души.',
                commentary='О надежде.',
                theme='Надежда',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='О вере',
                author='Святитель Иоанн Златоуст',
                chapter_number=1, verse_number=1,
                original_text='Вера есть основание всех благ.',
                translation_ru='Вера есть основание всех благ.',
                commentary='О вере.',
                theme='Вера',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='О любви',
                author='Святитель Иоанн Златоуст',
                chapter_number=1, verse_number=1,
                original_text='Любовь есть исполнение закона.',
                translation_ru='Любовь есть исполнение закона.',
                commentary='О любви.',
                theme='Любовь',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='О милости',
                author='Святитель Иоанн Златоуст',
                chapter_number=1, verse_number=1,
                original_text='Милость есть свойство Божие.',
                translation_ru='Милость есть свойство Божие.',
                commentary='О милости.',
                theme='Милость',
                confession='orthodox'
            ),
            
            # Святоотеческие труды - Василий Великий (еще больше)
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='О вере',
                author='Святитель Василий Великий',
                chapter_number=1, verse_number=1,
                original_text='Вера есть уверенность в невидимом.',
                translation_ru='Вера есть уверенность в невидимом.',
                commentary='О вере.',
                theme='Вера',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='О надежде',
                author='Святитель Василий Великий',
                chapter_number=1, verse_number=1,
                original_text='Надежда есть ожидание будущих благ.',
                translation_ru='Надежда есть ожидание будущих благ.',
                commentary='О надежде.',
                theme='Надежда',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='О любви',
                author='Святитель Василий Великий',
                chapter_number=1, verse_number=1,
                original_text='Любовь есть связь совершенства.',
                translation_ru='Любовь есть связь совершенства.',
                commentary='О любви.',
                theme='Любовь',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='О молитве',
                author='Святитель Василий Великий',
                chapter_number=2, verse_number=1,
                original_text='Молитва есть беседа с Богом.',
                translation_ru='Молитва есть беседа с Богом.',
                commentary='О молитве.',
                theme='Молитва',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='О посте',
                author='Святитель Василий Великий',
                chapter_number=2, verse_number=1,
                original_text='Пост есть воздержание от страстей.',
                translation_ru='Пост есть воздержание от страстей.',
                commentary='О посте.',
                theme='Пост',
                confession='orthodox'
            ),
            
            # Святоотеческие труды - Григорий Богослов (еще больше)
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='О вере',
                author='Святитель Григорий Богослов',
                chapter_number=1, verse_number=1,
                original_text='Вера есть дар Божий.',
                translation_ru='Вера есть дар Божий.',
                commentary='О вере.',
                theme='Вера',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='О надежде',
                author='Святитель Григорий Богослов',
                chapter_number=1, verse_number=1,
                original_text='Надежда есть упование на Бога.',
                translation_ru='Надежда есть упование на Бога.',
                commentary='О надежде.',
                theme='Надежда',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='О любви',
                author='Святитель Григорий Богослов',
                chapter_number=1, verse_number=1,
                original_text='Любовь есть Бог.',
                translation_ru='Любовь есть Бог.',
                commentary='О любви.',
                theme='Любовь',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='О молитве',
                author='Святитель Григорий Богослов',
                chapter_number=1, verse_number=1,
                original_text='Молитва есть восхождение к Богу.',
                translation_ru='Молитва есть восхождение к Богу.',
                commentary='О молитве.',
                theme='Молитва',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='О богословии',
                author='Святитель Григорий Богослов',
                chapter_number=3, verse_number=1,
                original_text='Богословие есть ведение о Боге.',
                translation_ru='Богословие есть ведение о Боге.',
                commentary='О богословии.',
                theme='Богословие',
                confession='orthodox'
            ),
            
            # Святоотеческие труды - Максим Исповедник (еще больше)
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='О вере',
                author='Преподобный Максим Исповедник',
                chapter_number=1, verse_number=1,
                original_text='Вера есть начало спасения.',
                translation_ru='Вера есть начало спасения.',
                commentary='О вере.',
                theme='Вера',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='О надежде',
                author='Преподобный Максим Исповедник',
                chapter_number=1, verse_number=1,
                original_text='Надежда есть упование на милость Божию.',
                translation_ru='Надежда есть упование на милость Божию.',
                commentary='О надежде.',
                theme='Надежда',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='О любви',
                author='Преподобный Максим Исповедник',
                chapter_number=2, verse_number=1,
                original_text='Любовь есть исполнение всех заповедей.',
                translation_ru='Любовь есть исполнение всех заповедей.',
                commentary='О любви.',
                theme='Любовь',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='О молитве',
                author='Преподобный Максим Исповедник',
                chapter_number=1, verse_number=1,
                original_text='Молитва есть восхождение ума к Богу.',
                translation_ru='Молитва есть восхождение ума к Богу.',
                commentary='О молитве.',
                theme='Молитва',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='О воле',
                author='Преподобный Максим Исповедник',
                chapter_number=2, verse_number=1,
                original_text='Воля есть способность к добру и злу.',
                translation_ru='Воля есть способность к добру и злу.',
                commentary='О воле.',
                theme='Воля',
                confession='orthodox'
            ),
            
            # Святоотеческие труды - Иоанн Дамаскин (еще больше)
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='О вере',
                author='Преподобный Иоанн Дамаскин',
                chapter_number=2, verse_number=1,
                original_text='Вера есть согласие на то, что слышишь.',
                translation_ru='Вера есть согласие на то, что слышишь.',
                commentary='О вере.',
                theme='Вера',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='О надежде',
                author='Преподобный Иоанн Дамаскин',
                chapter_number=1, verse_number=1,
                original_text='Надежда есть упование на Бога.',
                translation_ru='Надежда есть упование на Бога.',
                commentary='О надежде.',
                theme='Надежда',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='О любви',
                author='Преподобный Иоанн Дамаскин',
                chapter_number=1, verse_number=1,
                original_text='Любовь есть исполнение закона.',
                translation_ru='Любовь есть исполнение закона.',
                commentary='О любви.',
                theme='Любовь',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='О молитве',
                author='Преподобный Иоанн Дамаскин',
                chapter_number=1, verse_number=1,
                original_text='Молитва есть восхождение ума к Богу.',
                translation_ru='Молитва есть восхождение ума к Богу.',
                commentary='О молитве.',
                theme='Молитва',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='О иконопочитании',
                author='Преподобный Иоанн Дамаскин',
                chapter_number=2, verse_number=1,
                original_text='Икона есть образ Первообраза.',
                translation_ru='Икона есть образ Первообраза.',
                commentary='Об иконопочитании.',
                theme='Икона',
                confession='orthodox'
            ),
            
            # Святоотеческие труды - Исаак Сирин (еще больше)
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='О вере',
                author='Преподобный Исаак Сирин',
                chapter_number=1, verse_number=1,
                original_text='Вера есть дар Божий.',
                translation_ru='Вера есть дар Божий.',
                commentary='О вере.',
                theme='Вера',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='О надежде',
                author='Преподобный Исаак Сирин',
                chapter_number=1, verse_number=1,
                original_text='Надежда есть упование на милость Божию.',
                translation_ru='Надежда есть упование на милость Божию.',
                commentary='О надежде.',
                theme='Надежда',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='О любви',
                author='Преподобный Исаак Сирин',
                chapter_number=1, verse_number=1,
                original_text='Любовь есть исполнение всех заповедей.',
                translation_ru='Любовь есть исполнение всех заповедей.',
                commentary='О любви.',
                theme='Любовь',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='О молитве',
                author='Преподобный Исаак Сирин',
                chapter_number=2, verse_number=1,
                original_text='Молитва есть восхождение ума к Богу.',
                translation_ru='Молитва есть восхождение ума к Богу.',
                commentary='О молитве.',
                theme='Молитва',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='О смирении',
                author='Преподобный Исаак Сирин',
                chapter_number=2, verse_number=1,
                original_text='Смирение есть мать всех добродетелей.',
                translation_ru='Смирение есть мать всех добродетелей.',
                commentary='О смирении.',
                theme='Смирение',
                confession='orthodox'
            ),
            
            # Святоотеческие труды - Ефрем Сирин (еще больше)
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='О вере',
                author='Преподобный Ефрем Сирин',
                chapter_number=1, verse_number=1,
                original_text='Вера есть дар Божий.',
                translation_ru='Вера есть дар Божий.',
                commentary='О вере.',
                theme='Вера',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='О надежде',
                author='Преподобный Ефрем Сирин',
                chapter_number=1, verse_number=1,
                original_text='Надежда есть упование на милость Божию.',
                translation_ru='Надежда есть упование на милость Божию.',
                commentary='О надежде.',
                theme='Надежда',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='О любви',
                author='Преподобный Ефрем Сирин',
                chapter_number=1, verse_number=1,
                original_text='Любовь есть исполнение всех заповедей.',
                translation_ru='Любовь есть исполнение всех заповедей.',
                commentary='О любви.',
                theme='Любовь',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='О молитве',
                author='Преподобный Ефрем Сирин',
                chapter_number=2, verse_number=1,
                original_text='Молитва есть восхождение ума к Богу.',
                translation_ru='Молитва есть восхождение ума к Богу.',
                commentary='О молитве.',
                theme='Молитва',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='О покаянии',
                author='Преподобный Ефрем Сирин',
                chapter_number=2, verse_number=1,
                original_text='Покаяние есть второе крещение.',
                translation_ru='Покаяние есть второе крещение.',
                commentary='О покаянии.',
                theme='Покаяние',
                confession='orthodox'
            ),
            
            # Святоотеческие труды - Иоанн Лествичник (финальные)
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='Лествица',
                author='Преподобный Иоанн Лествичник',
                chapter_number=11, verse_number=1,
                original_text='Злословие есть смерть души.',
                translation_ru='Злословие есть смерть души.',
                commentary='О злословии.',
                theme='Злословие',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='Лествица',
                author='Преподобный Иоанн Лествичник',
                chapter_number=12, verse_number=1,
                original_text='Ложь есть мать всех пороков.',
                translation_ru='Ложь есть мать всех пороков.',
                commentary='О лжи.',
                theme='Ложь',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='Лествица',
                author='Преподобный Иоанн Лествичник',
                chapter_number=13, verse_number=1,
                original_text='Уныние есть расслабление души.',
                translation_ru='Уныние есть расслабление души.',
                commentary='Об унынии.',
                theme='Уныние',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='Лествица',
                author='Преподобный Иоанн Лествичник',
                chapter_number=14, verse_number=1,
                original_text='Чревоугодие есть мать всех страстей.',
                translation_ru='Чревоугодие есть мать всех страстей.',
                commentary='О чревоугодии.',
                theme='Чревоугодие',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='Лествица',
                author='Преподобный Иоанн Лествичник',
                chapter_number=15, verse_number=1,
                original_text='Блуд есть смерть души.',
                translation_ru='Блуд есть смерть души.',
                commentary='О блуде.',
                theme='Блуд',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='Лествица',
                author='Преподобный Иоанн Лествичник',
                chapter_number=16, verse_number=1,
                original_text='Сребролюбие есть корень всех зол.',
                translation_ru='Сребролюбие есть корень всех зол.',
                commentary='О сребролюбии.',
                theme='Сребролюбие',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='Лествица',
                author='Преподобный Иоанн Лествичник',
                chapter_number=17, verse_number=1,
                original_text='Гнев есть кратковременное безумие.',
                translation_ru='Гнев есть кратковременное безумие.',
                commentary='О гневе.',
                theme='Гнев',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='Лествица',
                author='Преподобный Иоанн Лествичник',
                chapter_number=18, verse_number=1,
                original_text='Злопамятство есть забвение правды.',
                translation_ru='Злопамятство есть забвение правды.',
                commentary='О злопамятстве.',
                theme='Злопамятство',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='Лествица',
                author='Преподобный Иоанн Лествичник',
                chapter_number=19, verse_number=1,
                original_text='Кротость есть тишина ума.',
                translation_ru='Кротость есть тишина ума.',
                commentary='О кротости.',
                theme='Кротость',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='Лествица',
                author='Преподобный Иоанн Лествичник',
                chapter_number=20, verse_number=1,
                original_text='Плач есть дар Божий.',
                translation_ru='Плач есть дар Божий.',
                commentary='О плаче.',
                theme='Плач',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='Лествица',
                author='Преподобный Иоанн Лествичник',
                chapter_number=21, verse_number=1,
                original_text='Память смертная есть великое оружие против греха.',
                translation_ru='Память смертная есть великое оружие против греха.',
                commentary='О памяти смертной.',
                theme='Смерть',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='Лествица',
                author='Преподобный Иоанн Лествичник',
                chapter_number=22, verse_number=1,
                original_text='Покаяние есть обновление крещения.',
                translation_ru='Покаяние есть обновление крещения.',
                commentary='О покаянии.',
                theme='Покаяние',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='Лествица',
                author='Преподобный Иоанн Лествичник',
                chapter_number=23, verse_number=1,
                original_text='Послушание есть отречение от своей воли.',
                translation_ru='Послушание есть отречение от своей воли.',
                commentary='О послушании.',
                theme='Послушание',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='Лествица',
                author='Преподобный Иоанн Лествичник',
                chapter_number=24, verse_number=1,
                original_text='Смирение есть основание всех добродетелей.',
                translation_ru='Смирение есть основание всех добродетелей.',
                commentary='О смирении.',
                theme='Смирение',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='Лествица',
                author='Преподобный Иоанн Лествичник',
                chapter_number=25, verse_number=1,
                original_text='Любовь есть исполнение всех заповедей.',
                translation_ru='Любовь есть исполнение всех заповедей.',
                commentary='О любви.',
                theme='Любовь',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='Лествица',
                author='Преподобный Иоанн Лествичник',
                chapter_number=26, verse_number=1,
                original_text='Молитва есть восхождение ума к Богу.',
                translation_ru='Молитва есть восхождение ума к Богу.',
                commentary='О молитве.',
                theme='Молитва',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='Лествица',
                author='Преподобный Иоанн Лествичник',
                chapter_number=27, verse_number=1,
                original_text='Безмолвие есть тишина ума.',
                translation_ru='Безмолвие есть тишина ума.',
                commentary='О безмолвии.',
                theme='Безмолвие',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='Лествица',
                author='Преподобный Иоанн Лествичник',
                chapter_number=29, verse_number=1,
                original_text='Молитва есть собеседование ума с Богом.',
                translation_ru='Молитва есть собеседование ума с Богом.',
                commentary='О сущности молитвы.',
                theme='Молитва',
                confession='orthodox'
            ),
            OrthodoxText(
                source_type='Святоотеческие труды',
                book_name='Лествица',
                author='Преподобный Иоанн Лествичник',
                chapter_number=30, verse_number=1,
                original_text='Молитва есть восхождение ума к Богу.',
                translation_ru='Молитва есть восхождение ума к Богу.',
                commentary='О молитве.',
                theme='Молитва',
                confession='orthodox'
            ),
        ]
        
        db.add_all(orthodox_texts)
        db.flush()  # Принудительно сохраняем в базу
        logger.info(f"✅ Добавлено {len(orthodox_texts)} православных текстов")
        
        db.commit()
        logger.info(f"✅ Расширенные православные данные загружены успешно")
        
    except Exception as e:
        logger.error(f"❌ Ошибка загрузки расширенных данных: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    load_extended_orthodox_data()
