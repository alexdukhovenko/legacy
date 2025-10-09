"""
Упрощенный ИИ-агент для работы с исламскими текстами
Без использования sentence-transformers (для совместимости)
"""

import json
import re
import openai
import os
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from database import QuranVerse, Hadith, Commentary, VectorEmbedding, SystemConfig, OrthodoxText
from backend.confession_agents import ConfessionAgentFactory
import logging

logger = logging.getLogger(__name__)


class SimpleIslamicAIAgent:
    """Упрощенный ИИ-агент для работы с исламскими священными текстами"""
    
    def __init__(self, db: Session):
        self.db = db
        # Настройка OpenAI API
        api_key = os.getenv("OPENAI_API_KEY", "your-openai-api-key-here")
        self.openai_client = openai.OpenAI(api_key=api_key)
    
    def search_relevant_texts(self, query: str, user_confession: str = None, top_k: int = 2) -> List[Dict[str, Any]]:
        """Поиск релевантных текстов с учетом конфессии пользователя"""
        try:
            # Разбиваем запрос на ключевые слова
            keywords = self._extract_keywords(query)
            
            results = []
            
            # Определяем, какие источники искать
            confession_filters = ['common']  # Общие источники всегда доступны
            
            if user_confession:
                confession_filters.append(user_confession)
            
            # Поиск в аятах Корана
            quran_query = self.db.query(QuranVerse)
            if confession_filters:
                # Включаем NULL значения (старые записи без конфессии) + указанные конфессии
                quran_query = quran_query.filter(
                    or_(
                        QuranVerse.confession.in_(confession_filters),
                        QuranVerse.confession.is_(None)
                    )
                )
            
            quran_verses = quran_query.all()
            for verse in quran_verses:
                score = self._calculate_similarity_score(keywords, verse.translation_ru or "")
                if score > 0.1:  # Снижаем порог схожести
                    results.append({
                        'id': verse.id,
                        'source_type': 'quran',
                        'source_id': verse.id,
                        'text_chunk': verse.translation_ru or verse.arabic_text,
                        'similarity_score': score,
                        'content': {
                            'type': 'quran',
                            'surah_number': verse.surah_number,
                            'verse_number': verse.verse_number,
                            'arabic_text': verse.arabic_text,
                            'translation_ru': verse.translation_ru,
                            'theme': verse.theme,
                            'confession': verse.confession
                        }
                    })
            
            # Поиск в хадисах
            hadith_query = self.db.query(Hadith)
            if confession_filters:
                hadith_query = hadith_query.filter(
                    or_(
                        Hadith.confession.in_(confession_filters),
                        Hadith.confession.is_(None)
                    )
                )
            
            hadiths = hadith_query.all()
            for hadith in hadiths:
                score = self._calculate_similarity_score(keywords, hadith.translation_ru or "")
                if score > 0.1:
                    results.append({
                        'id': hadith.id,
                        'source_type': 'hadith',
                        'source_id': hadith.id,
                        'text_chunk': hadith.translation_ru or hadith.arabic_text,
                        'similarity_score': score,
                        'content': {
                            'type': 'hadith',
                            'collection': hadith.collection,
                            'hadith_number': hadith.hadith_number,
                            'arabic_text': hadith.arabic_text,
                            'translation_ru': hadith.translation_ru,
                            'narrator': hadith.narrator,
                            'grade': hadith.grade,
                            'topic': hadith.topic,
                            'confession': hadith.confession
                        }
                    })
            
            # Поиск в комментариях
            commentary_query = self.db.query(Commentary)
            if confession_filters:
                commentary_query = commentary_query.filter(
                    or_(
                        Commentary.confession.in_(confession_filters),
                        Commentary.confession.is_(None)
                    )
                )
            
            commentaries = commentary_query.all()
            for commentary in commentaries:
                score = self._calculate_similarity_score(keywords, commentary.translation_ru or "")
                if score > 0.1:
                    results.append({
                        'id': commentary.id,
                        'source_type': 'commentary',
                        'source_id': commentary.id,
                        'text_chunk': commentary.translation_ru or commentary.arabic_text,
                        'similarity_score': score,
                        'content': {
                            'type': 'commentary',
                            'source': commentary.source,
                            'arabic_text': commentary.arabic_text,
                            'translation_ru': commentary.translation_ru,
                            'confession': commentary.confession
                        }
                    })
            
            # Сортируем по релевантности
            results.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            return results[:top_k]
            
        except Exception as e:
            logger.error(f"❌ Ошибка поиска: {e}")
            return []
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Извлечение ключевых слов из текста"""
        # Убираем знаки препинания и приводим к нижнему регистру
        clean_text = re.sub(r'[^\w\s]', ' ', text.lower())
        words = clean_text.split()
        
        # Фильтруем стоп-слова
        stop_words = {'и', 'в', 'на', 'с', 'по', 'для', 'от', 'до', 'что', 'как', 'где', 'когда', 'почему', 'кто', 'это', 'то', 'а', 'но', 'или', 'если', 'чтобы', 'чтобы', 'чтобы', 'меня', 'мне', 'я', 'ты', 'он', 'она', 'мы', 'вы', 'они', 'все', 'если', 'или', 'но', 'а', 'и', 'в', 'на', 'с', 'по', 'от', 'до', 'из', 'к', 'у', 'о', 'об', 'при', 'без', 'через', 'между', 'среди', 'около', 'возле', 'близ', 'далеко', 'тут', 'там', 'здесь', 'туда', 'сюда', 'оттуда', 'отсюда', 'когда', 'тогда', 'сейчас', 'теперь', 'уже', 'еще', 'только', 'лишь', 'даже', 'тоже', 'также', 'еще', 'уже', 'всегда', 'никогда', 'иногда', 'часто', 'редко', 'очень', 'слишком', 'довольно', 'вполне', 'совсем', 'полностью', 'частично', 'немного', 'много', 'мало', 'больше', 'меньше', 'лучше', 'хуже', 'хорошо', 'плохо', 'да', 'нет', 'не', 'ни', 'быть', 'есть', 'был', 'была', 'было', 'были', 'будет', 'будут', 'могу', 'можешь', 'может', 'можем', 'можете', 'могут', 'хочу', 'хочешь', 'хочет', 'хотим', 'хотите', 'хотят', 'нужно', 'надо', 'должен', 'должна', 'должно', 'должны', 'можно', 'нельзя', 'возможно', 'невозможно', 'хорошо', 'плохо', 'да', 'нет'}
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Добавляем синонимы для лучшего поиска
        synonyms = {
            'пост': ['поститься', 'голодать', 'воздержание', 'рамадан'],
            'намаз': ['молитва', 'салят', 'молиться'],
            'дуа': ['мольба', 'просьба', 'молиться'],
            'прервать': ['остановить', 'прекратить', 'бросить', 'закончить'],
            'соблюдать': ['держать', 'выполнять', 'следовать'],
            'духовник': ['имам', 'мулла', 'священник', 'наставник']
        }
        
        # Добавляем синонимы для найденных ключевых слов
        extended_keywords = keywords.copy()
        for keyword in keywords:
            if keyword in synonyms:
                extended_keywords.extend(synonyms[keyword])
        
        return extended_keywords
    
    def _calculate_similarity_score(self, keywords: List[str], text: str) -> float:
        """Улучшенный расчет схожести на основе ключевых слов"""
        if not text:
            return 0.0
        
        text_lower = text.lower()
        matches = 0
        total_weight = 0
        
        for keyword in keywords:
            total_weight += 1
            if keyword in text_lower:
                matches += 1
            else:
                # Проверяем частичные совпадения
                for word in text_lower.split():
                    if keyword in word or word in keyword:
                        matches += 0.5
                        break
        
        return matches / total_weight if total_weight > 0 else 0.0
    
    def generate_response(self, user_question: str, user_confession: str = None) -> Dict[str, Any]:
        """Генерация ответа на основе найденных текстов с использованием агентов конфессий"""
        try:
            logger.info(f"=== НАЧАЛО ГЕНЕРАЦИИ ОТВЕТА ===")
            logger.info(f"Вопрос: {user_question}")
            logger.info(f"Конфессия: {user_confession}")
            
            # Если указана конфессия, используем специализированного агента
            if user_confession and user_confession in ['sunni', 'shia', 'orthodox']:
                try:
                    logger.info(f"Создаем агент для конфессии: {user_confession}")
                    agent = ConfessionAgentFactory.create_agent(user_confession, self.db)
                    logger.info(f"Агент создан успешно: {type(agent).__name__}")
                    
                    relevant_texts = agent.search_relevant_texts(user_question)
                    logger.info(f"Найдено релевантных текстов: {len(relevant_texts)}")
                    
                    if relevant_texts:
                        logger.info(f"Типы найденных текстов: {[t.get('type', 'unknown') for t in relevant_texts]}")
                    
                    result = agent.generate_response(user_question, relevant_texts)
                    logger.info(f"Ответ от агента: {result.get('response', '')[:100]}...")
                    logger.info(f"Источники от агента: {len(result.get('sources', []))}")
                    
                    # Проверяем, что агент вернул валидный ответ
                    if result and result.get('response'):
                        logger.info(f"Возвращаем ответ от агента {user_confession}")
                        return result
                    else:
                        logger.warning(f"Агент {user_confession} вернул пустой ответ, используем fallback")
                except Exception as e:
                    logger.error(f"Ошибка в агенте конфессии {user_confession}: {e}")
                    import traceback
                    logger.error(f"Traceback: {traceback.format_exc()}")
                    # Fallback на стандартный метод только для исламских конфессий
                    if user_confession in ['sunni', 'shia']:
                        logger.info(f"Fallback для исламской конфессии {user_confession}")
                    else:
                        # Для православия возвращаем специальный ответ
                        logger.info(f"Fallback для православия")
                        return {
                            'response': 'В православных источниках есть информация по этому вопросу, но для полного ответа рекомендую обратиться к священнику.\n\nПриложение: Этот вопрос требует глубокого изучения священных текстов и консультации с духовным наставником.',
                            'sources': [],
                            'confidence': 0.3
                        }
            
            # Стандартный метод для общих вопросов или fallback
            logger.info("Используем стандартный метод")
            return self._generate_standard_response(user_question, user_confession)
            
        except Exception as e:
            logger.error(f"Ошибка при генерации ответа: {e}")
            return {
                'response': 'Извините, произошла ошибка при обработке вашего вопроса.',
                'sources': [],
                'confidence': 0.0
            }
    
    def _generate_standard_response(self, user_question: str, user_confession: str = None) -> Dict[str, Any]:
        """Стандартная генерация ответа (fallback метод)"""
        try:
            # Поиск релевантных текстов с учетом конфессии
            relevant_texts = self.search_relevant_texts(user_question, user_confession, top_k=2)
            
            if not relevant_texts:
                return {
                    'response': 'Извините, я не нашел релевантной информации в доступных источниках для ответа на ваш вопрос. Рекомендую обратиться к знающему духовнику или имаму.',
                    'sources': [],
                    'confidence': 0.0
                }
            
            # Проверяем, что найденные источники действительно релевантны
            # Если максимальный score слишком низкий, считаем вопрос нерелевантным
            max_score = max([text['similarity_score'] for text in relevant_texts]) if relevant_texts else 0
            if max_score < 0.5:  # Повышаем порог релевантности
                return {
                    'response': 'Извините, я не нашел достаточно релевантной информации в священных текстах для ответа на ваш вопрос. Рекомендую обратиться к знающему духовнику или имаму.',
                    'sources': [],
                    'confidence': 0.0
                }
            
            # Дополнительная проверка: если вопрос явно не связан с религией, не отвечаем
            non_religious_keywords = ['крым', 'политика', 'борщ', 'готовить', 'рецепт', 'футбол', 'спорт', 'кино', 'музыка', 'технологии', 'программирование']
            question_lower = user_question.lower()
            if any(keyword in question_lower for keyword in non_religious_keywords):
                return {
                    'response': 'Извините, я духовный наставник и отвечаю только на вопросы, связанные с религией и духовностью. Для других вопросов рекомендую обратиться к соответствующим специалистам.',
                    'sources': [],
                    'confidence': 0.0
                }
            
            # Формируем контекст для OpenAI
            context = self._prepare_context_for_openai(relevant_texts)
            
            # Создаем промпт для OpenAI
            system_prompt = """Ты исламский духовный наставник. Отвечай ТОЛЬКО на исламские вопросы.

ФОРМАТ ОТВЕТА (СТРОГО):
1. Краткий ответ (1-2 предложения) с упоминанием источника
2. Пустая строка
3. "Приложение:" + человечный комментарий (1-2 предложения)

ПРИМЕР:
"В Коране, сура 2, аят 255 говорится о важности молитвы.

Приложение: Молитва укрепляет веру и объединяет семью."

ПРАВИЛА:
- НЕ копируй длинные цитаты из источников
- НЕ пиши толкования ас-Саади
- БУДЬ КРАТКИМ (максимум 100 слов)
- НЕ отвечай на неисламские вопросы"""

            user_prompt = f"""Вопрос: {user_question}

Источники: {context}

Ответь кратко по примеру выше. НЕ копируй длинные цитаты!"""

            # Запрос к OpenAI
            response = self.openai_client.chat.completions.create(
                model="gpt-5",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_output_tokens=1500,  # Значительно увеличиваем для полного ответа
                temperature=0.3  # Более детерминированные ответы
            )
            
            ai_response = response.choices[0].message.content.strip()
            logger.info(f"🔍 Полный ответ от OpenAI: {ai_response}")
            
            # Постобработка: заменяем "Интерпретация:" на "Приложение:" и добавляем абзац
            if "Интерпретация:" in ai_response:
                ai_response = ai_response.replace("Интерпретация:", "Приложение:")
                logger.info(f"🔄 Заменил 'Интерпретация:' на 'Приложение:'")
            
            # Добавляем абзац перед "Приложение:" если его нет
            if "Приложение:" in ai_response:
                parts = ai_response.split("Приложение:", 1)
                if len(parts) == 2:
                    main_part = parts[0].rstrip()
                    appendix_part = parts[1]
                    # Проверяем, есть ли уже абзац перед "Приложение:"
                    if not main_part.endswith("\n\n"):
                        ai_response = f"{main_part}\n\nПриложение:{appendix_part}"
                        logger.info(f"🔄 Добавил абзац перед 'Приложение:'")
                    else:
                        ai_response = f"{main_part}Приложение:{appendix_part}"
                        logger.info(f"🔄 Абзац уже есть перед 'Приложение:'")
            
            # Постобработка: принудительно сокращаем длинные ответы
            logger.info(f"🔍 Длина ответа: {len(ai_response)} символов")
            
            # Принудительно сокращаем любой ответ длиннее 300 символов
            if len(ai_response) > 300:
                # Берем первые 200 символов
                short_response = ai_response[:200] + "..."
                
                # Добавляем "Приложение:" если его нет
                if "Приложение:" not in short_response:
                    short_response += "\n\nПриложение: Этот вопрос требует глубокого изучения священных текстов. Рекомендую обратиться к знающему духовнику для получения полного ответа."
                
                ai_response = short_response
                logger.info(f"🔄 ПРИНУДИТЕЛЬНО сократил ответ до 200 символов")
            
            # Создаем краткие источники для ответа
            brief_sources = []
            for text in relevant_texts:
                content = text['content']
                if content['type'] == 'quran':
                    # Создаем краткую версию источника с полным текстом для модального окна
                    brief_content = {
                        'type': 'quran',
                        'id': content.get('id'),
                        'surah_number': content['surah_number'],
                        'verse_number': content['verse_number'],
                        'arabic_text': content.get('arabic_text', '')[:50] + '...' if content.get('arabic_text') else '',
                        'translation_ru': content.get('translation_ru', '')[:100] + '...' if content.get('translation_ru') else '',
                        'theme': content.get('theme', 'общий'),
                        # Добавляем полный текст для модального окна
                        'full_arabic_text': content.get('arabic_text', ''),
                        'full_translation_ru': content.get('translation_ru', ''),
                        'full_commentary': content.get('commentary', '')
                    }
                    brief_sources.append({
                        'type': text['content']['type'],
                        'similarity_score': text['similarity_score'],
                        'content': brief_content
                    })
            
            return {
                'response': ai_response,
                'sources': brief_sources,
                'confidence': max([text['similarity_score'] for text in relevant_texts]) if relevant_texts else 0.0
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка генерации ответа: {e}")
            # Fallback на простой ответ
            return self._generate_simple_fallback(user_question, relevant_texts)
    
    def _prepare_context_for_openai(self, texts: List[Dict]) -> str:
        """Подготовка контекста для OpenAI с ограничением длины"""
        context_parts = []
        
        for text in texts:
            content = text['content']
            
            if content['type'] == 'quran':
                # Ограничиваем длину перевода до 150 символов для краткости
                translation = content.get('translation_ru', '')
                if len(translation) > 150:
                    translation = translation[:150] + "..."
                
                confession_info = f" ({content.get('confession', 'общий')})" if content.get('confession') else ""
                context_parts.append(
                    f"Коран{confession_info}, сура {content['surah_number']}, аят {content['verse_number']}: "
                    f"{translation}"
                )
                
            elif content['type'] == 'hadith':
                translation = content.get('translation_ru', '')
                if len(translation) > 150:
                    translation = translation[:150] + "..."
                
                confession_info = f" ({content.get('confession', 'общий')})" if content.get('confession') else ""
                context_parts.append(
                    f"Хадис{confession_info}, сборник {content.get('collection', 'неизвестен')}, "
                    f"номер {content.get('hadith_number', 'неизвестен')}: {translation}"
                )
                
            elif content['type'] == 'commentary':
                translation = content.get('translation_ru', '')
                if len(translation) > 150:
                    translation = translation[:150] + "..."
                
                confession_info = f" ({content.get('confession', 'общий')})" if content.get('confession') else ""
                context_parts.append(
                    f"Комментарий{confession_info}, источник {content.get('source', 'неизвестен')}: "
                    f"{translation}"
                )
        
        return "\n\n".join(context_parts)
    
    def _generate_simple_fallback(self, question: str, texts: List[Dict]) -> Dict[str, Any]:
        """Простой fallback ответ без OpenAI"""
        if not texts:
            return {
                'response': 'Извините, я не нашел релевантной информации в доступных источниках для ответа на ваш вопрос. Рекомендую обратиться к знающему духовнику или имаму.',
                'sources': [],
                'confidence': 0.0
            }
        
        # Берем первый найденный текст
        first_text = texts[0]['content']
        if first_text['type'] == 'quran':
            response = f"В Коране, сура {first_text['surah_number']}, аят {first_text['verse_number']} говорится: {first_text['translation_ru']}"
        
        return {
            'response': response,
            'sources': [{
                'type': text['content']['type'],
                'similarity_score': text['similarity_score'],
                'content': text['content']
            } for text in texts],
            'confidence': max([text['similarity_score'] for text in texts]) if texts else 0.0
        }
    
    def _form_response(self, question: str, texts: List[Dict]) -> str:
        """Формирование ответа на основе контекста"""
        try:
            response_parts = [
                "На основе священных текстов:",
                ""
            ]
            
            for text in texts:
                content = text['content']
                if content['type'] == 'quran':
                    response_parts.append(f"Коран, сура {content['surah_number']}, аят {content['verse_number']}:")
                    response_parts.append(f"{content['translation_ru']}")
                    if content.get('arabic_text'):
                        response_parts.append(f"Арабский текст: {content['arabic_text']}")
                    response_parts.append("")
            
            response_parts.extend([
                "Важно отметить, что для глубокого понимания и личного духовного руководства рекомендуется обратиться к знающему духовнику или имаму в вашей местной мечети."
            ])
            
            return "\n".join(response_parts)
            
        except Exception as e:
            logger.error(f"❌ Ошибка формирования ответа: {e}")
            return "Не удалось сформировать ответ. Рекомендую обратиться к духовнику."
    
    def add_text_to_database(self, text: str, source_type: str, source_id: int, chunk_size: int = 512):
        """Добавление текста в базу данных (упрощенная версия без эмбеддингов)"""
        try:
            # Просто сохраняем текст как есть
            vector_embedding = VectorEmbedding(
                source_type=source_type,
                source_id=source_id,
                text_chunk=text,
                embedding_vector="",  # Пустой для упрощенной версии
                chunk_index=0
            )
            
            self.db.add(vector_embedding)
            self.db.commit()
            logger.info(f"✅ Добавлен текст для {source_type}:{source_id}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка добавления текста: {e}")
            self.db.rollback()
