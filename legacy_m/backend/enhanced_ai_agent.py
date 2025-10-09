#!/usr/bin/env python3
"""
Улучшенный AI агент с качественным анализом и ответами
"""

import os
import logging
import time
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
import openai
from openai import OpenAI

# Импорты моделей
from database.models import QuranVerse, Hadith, Commentary, OrthodoxText, OrthodoxDocument

logger = logging.getLogger(__name__)

# Инициализация OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class EnhancedAIAgent:
    """Улучшенный AI агент с качественным анализом"""
    
    def __init__(self, confession: str, db: Session):
        self.confession = confession
        self.db = db
        self.confession_name = confession
        
    def generate_quality_response(self, question: str) -> Dict[str, Any]:
        """Генерирует качественный ответ с анализом источников"""
        start_time = time.time()
        
        try:
            logger.info(f"🤖 Начинаем качественный анализ для {self.confession}")
            
            # Шаг 1: Глубокий поиск релевантных текстов
            relevant_texts = self._deep_search_relevant_texts(question)
            logger.info(f"📚 Найдено {len(relevant_texts)} релевантных текстов")
            
            # Шаг 2: Анализ и ранжирование источников
            analyzed_texts = self._analyze_and_rank_sources(question, relevant_texts)
            logger.info(f"🎯 Отобрано {len(analyzed_texts)} лучших источников")
            
            # Шаг 3: Генерация контекста
            context = self._build_rich_context(analyzed_texts)
            
            # Шаг 4: Генерация ответа с GPT-4
            response = self._generate_thoughtful_response(question, context, analyzed_texts)
            
            # Шаг 5: Постобработка и валидация
            final_response = self._postprocess_response(response, analyzed_texts)
            
            processing_time = time.time() - start_time
            logger.info(f"⏱️ Время обработки: {processing_time:.2f} секунд")
            
            return final_response
            
        except Exception as e:
            logger.error(f"❌ Ошибка в качественном анализе: {e}")
            return self._fallback_response(question)
    
    def _deep_search_relevant_texts(self, question: str) -> List[Dict[str, Any]]:
        """Глубокий поиск релевантных текстов с множественными стратегиями"""
        results = []
        
        # Стратегия 1: Семантический поиск
        semantic_results = self._semantic_search(question)
        results.extend(semantic_results)
        
        # Стратегия 2: Ключевые слова
        keyword_results = self._keyword_search(question)
        results.extend(keyword_results)
        
        # Стратегия 3: Тематический поиск
        thematic_results = self._thematic_search(question)
        results.extend(thematic_results)
        
        # Удаляем дубликаты
        unique_results = self._remove_duplicates(results)
        
        return unique_results
    
    def _semantic_search(self, question: str) -> List[Dict[str, Any]]:
        """Семантический поиск с использованием OpenAI embeddings"""
        try:
            # Получаем embedding для вопроса
            question_embedding = self._get_embedding(question)
            
            # Ищем в соответствующих таблицах
            if self.confession == 'orthodox':
                texts = self.db.query(OrthodoxText).filter(
                    OrthodoxText.confession == 'orthodox'
                ).limit(50).all()
            elif self.confession == 'sunni':
                quran_verses = self.db.query(QuranVerse).filter(
                    or_(QuranVerse.confession == 'sunni', QuranVerse.confession.is_(None))
                ).limit(30).all()
                hadiths = self.db.query(Hadith).filter(
                    Hadith.confession == 'sunni'
                ).limit(20).all()
                texts = list(quran_verses) + list(hadiths)
            elif self.confession == 'shia':
                quran_verses = self.db.query(QuranVerse).filter(
                    or_(QuranVerse.confession == 'shia', QuranVerse.confession.is_(None))
                ).limit(30).all()
                hadiths = self.db.query(Hadith).filter(
                    Hadith.confession == 'shia'
                ).limit(20).all()
                texts = list(quran_verses) + list(hadiths)
            else:
                texts = []
            
            results = []
            for text in texts:
                text_content = self._extract_text_content(text)
                if text_content:
                    text_embedding = self._get_embedding(text_content)
                    similarity = self._cosine_similarity(question_embedding, text_embedding)
                    
                    if similarity > 0.1:  # Порог для семантического поиска
                        results.append({
                            'text': text,
                            'content': text_content,
                            'similarity': similarity,
                            'type': 'semantic'
                        })
            
            return results
            
        except Exception as e:
            logger.warning(f"Ошибка семантического поиска: {e}")
            return []
    
    def _keyword_search(self, question: str) -> List[Dict[str, Any]]:
        """Поиск по ключевым словам"""
        keywords = self._extract_keywords(question)
        results = []
        
        if self.confession == 'orthodox':
            texts = self.db.query(OrthodoxText).filter(
                OrthodoxText.confession == 'orthodox'
            ).limit(30).all()
        elif self.confession == 'sunni':
            quran_verses = self.db.query(QuranVerse).filter(
                or_(QuranVerse.confession == 'sunni', QuranVerse.confession.is_(None))
            ).limit(20).all()
            hadiths = self.db.query(Hadith).filter(
                Hadith.confession == 'sunni'
            ).limit(15).all()
            texts = list(quran_verses) + list(hadiths)
        elif self.confession == 'shia':
            quran_verses = self.db.query(QuranVerse).filter(
                or_(QuranVerse.confession == 'shia', QuranVerse.confession.is_(None))
            ).limit(20).all()
            hadiths = self.db.query(Hadith).filter(
                Hadith.confession == 'shia'
            ).limit(15).all()
            texts = list(quran_verses) + list(hadiths)
        else:
            texts = []
        
        for text in texts:
            text_content = self._extract_text_content(text)
            if text_content:
                score = self._calculate_keyword_score(keywords, text_content)
                if score > 0.1:
                    results.append({
                        'text': text,
                        'content': text_content,
                        'similarity': score,
                        'type': 'keyword'
                    })
        
        return results
    
    def _thematic_search(self, question: str) -> List[Dict[str, Any]]:
        """Тематический поиск по концепциям"""
        themes = self._identify_themes(question)
        results = []
        
        # Словарь тематических связей
        theme_keywords = {
            'молитва': ['молитва', 'молиться', 'дуа', 'намаз', 'салят', 'богослужение', 'моление'],
            'грех': ['грех', 'грешить', 'покаяние', 'прощение', 'искупление', 'вина'],
            'семья': ['семья', 'родители', 'дети', 'брат', 'сестра', 'родственники', 'близкие'],
            'любовь': ['любовь', 'любить', 'милосердие', 'сострадание', 'доброта', 'забота'],
            'вера': ['вера', 'верить', 'доверие', 'уверенность', 'убеждение', 'верование'],
            'страдание': ['страдание', 'боль', 'скорбь', 'горе', 'трудности', 'проблемы'],
            'гнев': ['гнев', 'злость', 'ярость', 'раздражение', 'недовольство', 'ссора'],
            'прощение': ['прощение', 'прощать', 'милость', 'снисхождение', 'терпение']
        }
        
        if self.confession == 'orthodox':
            texts = self.db.query(OrthodoxText).filter(
                OrthodoxText.confession == 'orthodox'
            ).limit(20).all()
        elif self.confession == 'sunni':
            quran_verses = self.db.query(QuranVerse).filter(
                or_(QuranVerse.confession == 'sunni', QuranVerse.confession.is_(None))
            ).limit(15).all()
            hadiths = self.db.query(Hadith).filter(
                Hadith.confession == 'sunni'
            ).limit(10).all()
            texts = list(quran_verses) + list(hadiths)
        elif self.confession == 'shia':
            quran_verses = self.db.query(QuranVerse).filter(
                or_(QuranVerse.confession == 'shia', QuranVerse.confession.is_(None))
            ).limit(15).all()
            hadiths = self.db.query(Hadith).filter(
                Hadith.confession == 'shia'
            ).limit(10).all()
            texts = list(quran_verses) + list(hadiths)
        else:
            texts = []
        
        for text in texts:
            text_content = self._extract_text_content(text)
            if text_content:
                score = self._calculate_thematic_score(themes, theme_keywords, text_content)
                if score > 0.1:
                    results.append({
                        'text': text,
                        'content': text_content,
                        'similarity': score,
                        'type': 'thematic'
                    })
        
        return results
    
    def _analyze_and_rank_sources(self, question: str, texts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Анализирует и ранжирует источники"""
        # Группируем по типам
        semantic_texts = [t for t in texts if t['type'] == 'semantic']
        keyword_texts = [t for t in texts if t['type'] == 'keyword']
        thematic_texts = [t for t in texts if t['type'] == 'thematic']
        
        # Взвешиваем результаты
        weighted_results = []
        
        # Семантические результаты получают высший приоритет
        for text in semantic_texts:
            weighted_results.append({
                **text,
                'weighted_score': text['similarity'] * 1.0
            })
        
        # Ключевые слова - средний приоритет
        for text in keyword_texts:
            weighted_results.append({
                **text,
                'weighted_score': text['similarity'] * 0.7
            })
        
        # Тематические - низкий приоритет
        for text in thematic_texts:
            weighted_results.append({
                **text,
                'weighted_score': text['similarity'] * 0.5
            })
        
        # Сортируем по взвешенному score
        weighted_results.sort(key=lambda x: x['weighted_score'], reverse=True)
        
        # Возвращаем топ-5 результатов
        return weighted_results[:5]
    
    def _build_rich_context(self, texts: List[Dict[str, Any]]) -> str:
        """Строит богатый контекст из источников"""
        context_parts = []
        
        for i, text_data in enumerate(texts, 1):
            text = text_data['text']
            content = text_data['content']
            
            if hasattr(text, 'surah_number'):  # Коран
                context_parts.append(f"Источник {i}: Коран, сура {text.surah_number}, аят {text.verse_number}\n{content}")
            elif hasattr(text, 'collection'):  # Хадис
                context_parts.append(f"Источник {i}: Хадис из {text.collection}\n{content}")
            elif hasattr(text, 'book_name'):  # Православный текст
                context_parts.append(f"Источник {i}: {text.book_name}\n{content}")
            else:
                context_parts.append(f"Источник {i}: {content}")
        
        return "\n\n".join(context_parts)
    
    def _generate_thoughtful_response(self, question: str, context: str, sources: List[Dict[str, Any]]) -> str:
        """Генерирует вдумчивый ответ с использованием GPT-4"""
        
        system_prompt = self._get_enhanced_system_prompt()
        
        user_prompt = f"""Вопрос: {question}

Релевантные источники:
{context}

Инструкции:
1. Проанализируй вопрос и найденные источники
2. Дай краткий, но содержательный ответ (1-2 предложения)
3. Добавь практическое приложение (1-2 предложения)
4. Ссылайся на конкретные источники
5. НЕ копируй длинные цитаты
6. Будь человечным и понимающим

Формат ответа:
[Краткий ответ с упоминанием источника]

Приложение: [Практический совет]"""
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=400,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Ошибка генерации ответа: {e}")
            return self._fallback_response(question)
    
    def _get_enhanced_system_prompt(self) -> str:
        """Возвращает улучшенный системный промпт"""
        if self.confession == 'orthodox':
            return """Ты православный духовный наставник. Отвечай на вопросы с позиции православного христианства.

ПРАВИЛА:
- Используй ТОЛЬКО православные источники
- Будь кратким, но содержательным
- Давай практические советы
- Ссылайся на конкретные источники
- НЕ копируй длинные цитаты
- Будь понимающим и мудрым"""
        
        elif self.confession == 'sunni':
            return """Ты суннитский исламский духовный наставник. Отвечай на вопросы с позиции суннитского ислама.

ПРАВИЛА:
- Используй ТОЛЬКО суннитские источники (Коран, хадисы)
- Будь кратким, но содержательным
- Давай практические советы
- Ссылайся на конкретные источники
- НЕ копируй длинные цитаты
- Будь понимающим и мудрым"""
        
        elif self.confession == 'shia':
            return """Ты шиитский исламский духовный наставник. Отвечай на вопросы с позиции шиитского ислама.

ПРАВИЛА:
- Используй ТОЛЬКО шиитские источники (Коран, хадисы из аль-Кафи)
- Будь кратким, но содержательным
- Давай практические советы
- Ссылайся на конкретные источники
- НЕ копируй длинные цитаты
- Будь понимающим и мудрым"""
        
        return "Ты духовный наставник. Отвечай мудро и понимающе."
    
    def _postprocess_response(self, response: str, sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Постобработка ответа"""
        # Заменяем "Интерпретация:" на "Приложение:"
        if "Интерпретация:" in response:
            response = response.replace("Интерпретация:", "Приложение:")
        
        # Добавляем пустую строку перед "Приложение:"
        if "Приложение:" in response and "\n\nПриложение:" not in response:
            response = response.replace("Приложение:", "\n\nПриложение:")
        
        # Подготавливаем источники
        brief_sources = []
        for source_data in sources:
            text = source_data['text']
            if hasattr(text, 'surah_number'):  # Коран
                brief_sources.append({
                    'type': 'quran',
                    'surah': text.surah_number,
                    'verse': text.verse_number,
                    'text': text.translation_ru or text.arabic_text or "",
                    'full_text': text.translation_ru or text.arabic_text or ""
                })
            elif hasattr(text, 'collection'):  # Хадис
                brief_sources.append({
                    'type': 'hadith',
                    'collection': text.collection,
                    'number': getattr(text, 'hadith_number', getattr(text, 'number', '')),
                    'text': text.translation_ru or text.arabic_text or "",
                    'full_text': text.translation_ru or text.arabic_text or ""
                })
            elif hasattr(text, 'book_name'):  # Православный текст
                brief_sources.append({
                    'type': 'orthodox',
                    'book': text.book_name,
                    'author': getattr(text, 'author', ''),
                    'text': text.translation_ru or text.original_text or "",
                    'full_text': text.translation_ru or text.original_text or ""
                })
        
        return {
            'response': response,
            'sources': brief_sources,
            'confidence': min(len(sources) * 0.2, 1.0)
        }
    
    def _fallback_response(self, question: str) -> Dict[str, Any]:
        """Fallback ответ при ошибках"""
        if self.confession == 'orthodox':
            return {
                'response': 'В православных источниках есть информация по этому вопросу, но для полного ответа рекомендую обратиться к священнику.\n\nПриложение: Этот вопрос требует глубокого изучения священных текстов и консультации с духовным наставником.',
                'sources': [],
                'confidence': 0.3
            }
        elif self.confession == 'sunni':
            return {
                'response': 'Извините, я не нашел релевантной информации в суннитских источниках для ответа на ваш вопрос.\n\nПриложение: Для более глубокого изучения рекомендую обратиться к местному имаму или ученому.',
                'sources': [],
                'confidence': 0.3
            }
        elif self.confession == 'shia':
            return {
                'response': 'Извините, я не нашел релевантной информации в шиитских источниках для ответа на ваш вопрос.\n\nПриложение: Для более глубокого изучения рекомендую обратиться к местному аятолле или ученому.',
                'sources': [],
                'confidence': 0.3
            }
        else:
            return {
                'response': 'Извините, произошла ошибка при обработке вашего вопроса.',
                'sources': [],
                'confidence': 0.0
            }
    
    # Вспомогательные методы
    def _get_embedding(self, text: str) -> List[float]:
        """Получает embedding для текста"""
        try:
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Ошибка получения embedding: {e}")
            return []
    
    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Вычисляет косинусное сходство"""
        if not a or not b or len(a) != len(b):
            return 0.0
        
        import numpy as np
        a_np = np.array(a)
        b_np = np.array(b)
        
        dot_product = np.dot(a_np, b_np)
        norm_a = np.linalg.norm(a_np)
        norm_b = np.linalg.norm(b_np)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return dot_product / (norm_a * norm_b)
    
    def _extract_text_content(self, text) -> str:
        """Извлекает текстовое содержимое из объекта"""
        if hasattr(text, 'translation_ru') and text.translation_ru:
            return text.translation_ru
        elif hasattr(text, 'arabic_text') and text.arabic_text:
            return text.arabic_text
        elif hasattr(text, 'original_text') and text.original_text:
            return text.original_text
        elif hasattr(text, 'text_russian') and text.text_russian:
            return text.text_russian
        else:
            return ""
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Извлекает ключевые слова из текста"""
        import re
        # Убираем знаки препинания и приводим к нижнему регистру
        clean_text = re.sub(r'[^\w\s]', ' ', text.lower())
        words = clean_text.split()
        
        # Фильтруем короткие слова и стоп-слова
        stop_words = {'и', 'в', 'на', 'с', 'по', 'для', 'от', 'до', 'из', 'к', 'у', 'о', 'об', 'что', 'как', 'где', 'когда', 'почему', 'зачем', 'кто', 'чей', 'чья', 'чье', 'моя', 'мой', 'мое', 'твой', 'твоя', 'твое', 'его', 'ее', 'их', 'наш', 'наша', 'наше', 'ваш', 'ваша', 'ваше'}
        
        keywords = [word for word in words if len(word) > 2 and word not in stop_words]
        return keywords[:10]  # Берем топ-10 ключевых слов
    
    def _calculate_keyword_score(self, keywords: List[str], text: str) -> float:
        """Вычисляет score на основе ключевых слов"""
        if not keywords:
            return 0.0
        
        text_lower = text.lower()
        matches = sum(1 for keyword in keywords if keyword in text_lower)
        return matches / len(keywords)
    
    def _identify_themes(self, question: str) -> List[str]:
        """Определяет темы в вопросе"""
        question_lower = question.lower()
        themes = []
        
        theme_keywords = {
            'молитва': ['молитва', 'молиться', 'дуа', 'намаз', 'салят'],
            'грех': ['грех', 'грешить', 'покаяние', 'прощение'],
            'семья': ['семья', 'родители', 'дети', 'брат', 'сестра'],
            'любовь': ['любовь', 'любить', 'милосердие', 'сострадание'],
            'вера': ['вера', 'верить', 'доверие', 'уверенность'],
            'страдание': ['страдание', 'боль', 'скорбь', 'горе'],
            'гнев': ['гнев', 'злость', 'ярость', 'раздражение'],
            'прощение': ['прощение', 'прощать', 'милость', 'терпение']
        }
        
        for theme, keywords in theme_keywords.items():
            if any(keyword in question_lower for keyword in keywords):
                themes.append(theme)
        
        return themes
    
    def _calculate_thematic_score(self, themes: List[str], theme_keywords: Dict[str, List[str]], text: str) -> float:
        """Вычисляет тематический score"""
        if not themes:
            return 0.0
        
        text_lower = text.lower()
        score = 0.0
        
        for theme in themes:
            if theme in theme_keywords:
                for keyword in theme_keywords[theme]:
                    if keyword in text_lower:
                        score += 0.1
        
        return min(score, 1.0)
    
    def _remove_duplicates(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Удаляет дубликаты из результатов"""
        seen = set()
        unique_results = []
        
        for result in results:
            text_id = getattr(result['text'], 'id', None)
            if text_id and text_id not in seen:
                seen.add(text_id)
                unique_results.append(result)
        
        return unique_results
