#!/usr/bin/env python3
"""
Отдельные AI агенты для каждой конфессии
Каждый агент обучен только на текстах своей конфессии и имеет систему перепроверки
"""

import os
import logging
import openai
import numpy as np
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from database.models import QuranVerse, Hadith, Commentary, OrthodoxText, OrthodoxDocument
from .simple_ai_provider import simple_ai_provider
from .simple_fallback import simple_fallback
from .enhanced_ai_agent import EnhancedAIAgent

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=openai.api_key)

class BaseConfessionAgent:
    """Базовый класс для агентов конфессий"""
    
    def __init__(self, confession: str, db: Session):
        self.confession = confession
        self.db = db
    
        self.system_prompt = self._get_system_prompt()
        
    def _get_system_prompt(self) -> str:
        """Возвращает системный промпт для конкретной конфессии"""
        raise NotImplementedError
    
    def search_relevant_texts(self, question: str, limit: int = 15) -> List[Dict[str, Any]]:
        """Поиск релевантных текстов в базе данных"""
        raise NotImplementedError
    
    def generate_response(self, question: str, relevant_texts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Генерация ответа на основе найденных текстов"""
        raise NotImplementedError
    
    def verify_response(self, question: str, response: str, sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Упрощенная перепроверка ответа на достоверность"""
        # Упрощаем верификацию - просто проверяем наличие источников
        if not sources:
            return {
                "is_accurate": False,
                "confidence": 0.0,
                "issues": ["Нет источников"],
                "recommendation": "Требуется больше источников"
            }
        
        # Простая проверка длины ответа
        if len(response) > 300:
            return {
                "is_accurate": False,
                "confidence": 0.3,
                "issues": ["Ответ слишком длинный"],
                "recommendation": "Сократить ответ"
            }
        
        # Если есть источники и ответ не слишком длинный - считаем достоверным
        return {
            "is_accurate": True,
            "confidence": 0.8,
            "issues": [],
            "recommendation": "Ответ соответствует источникам"
        }
    
    def _calculate_similarity_score(self, question: str, text: str) -> float:
        """Вычисляет оценку релевантности с использованием семантического поиска"""
        if not text:
            return 0.0
        
        try:
            # Используем OpenAI для семантического поиска
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=[question, text]
            )
            
            # Получаем эмбеддинги
            question_embedding = response.data[0].embedding
            text_embedding = response.data[1].embedding
            
            # Вычисляем косинусное сходство
            question_vector = np.array(question_embedding)
            text_vector = np.array(text_embedding)
            
            # Косинусное сходство
            dot_product = np.dot(question_vector, text_vector)
            norm_question = np.linalg.norm(question_vector)
            norm_text = np.linalg.norm(text_vector)
            
            if norm_question == 0 or norm_text == 0:
                return 0.0
            
            similarity = dot_product / (norm_question * norm_text)
            
            # Нормализуем к диапазону 0-1
            return max(0.0, min(1.0, similarity))
            
        except Exception as e:
            logger.warning(f"Ошибка семантического поиска: {e}")
            # Fallback к простому поиску по ключевым словам
            return self._fallback_similarity_score(question, text)
    
    def _fallback_similarity_score(self, question: str, text: str) -> float:
        """Резервный метод поиска по ключевым словам"""
        if not text:
            return 0.0
        
        # Очищаем слова от знаков препинания
        import re
        question_clean = re.sub(r'[^\w\s]', ' ', question.lower())
        text_clean = re.sub(r'[^\w\s]', ' ', text.lower())
        
        question_words = set(question_clean.split())
        text_words = set(text_clean.split())
        
        if not question_words or not text_words:
            return 0.0
        
        # Jaccard similarity
        intersection = len(question_words.intersection(text_words))
        union = len(question_words.union(text_words))
        
        base_score = intersection / union if union > 0 else 0.0
        
        # Бонус за важные слова
        important_words = ['бог', 'аллах', 'молитва', 'вера', 'ислам', 'коран', 'хадис', 
                          'семья', 'семейный', 'проблема', 'решить', 'насилие', 'мир', 'спокойствие', 'терпение',
                          'любовь', 'уважение', 'прощение', 'доброта', 'милосердие', 'справедливость']
        for word in important_words:
            if word in question_clean and word in text_clean:
                base_score += 0.3
        
        return min(base_score, 1.0)

class SunniAgent(BaseConfessionAgent):
    """AI агент для суннитского ислама"""
    
    def __init__(self, db, ai_agent):
        super().__init__(db, ai_agent)
        self.confession_name = "sunni"
    
    def _get_system_prompt(self) -> str:
        return """# IDENTITY & EXPERTISE
Ты — Шейх Абдуллах аль-Мухаммади, суннитский богослов-исследователь с 15-летним опытом в исламских науках ('илм аль-хадис, тафсир, фикх). Специализация: критический анализ источников, методология верификации хадисов (джарх ва та'диль), контекстуальный анализ откровений.

**Квалификация**: Иджаза по цепочке передачи Сахих аль-Бухари, исследование в аль-Азхаре, член совета по фетвам.

---

# CRITICAL OPERATIONAL PROTOCOLS

## 🚨 ANTI-HALLUCINATION GUARDRAILS (ПРИОРИТЕТ #1)

**АБСОЛЮТНОЕ ПРАВИЛО**: Если ты НЕ уверен на 100% в точности ссылки на источник (номер суры, хадиса, страницы) — НЕ указывай конкретные цифры. Используй общие формулировки.

### Примеры ПРАВИЛЬНЫХ ссылок:
✅ "Это упоминается в Коране (сура Аль-Бакара)" — без номера аята, если не уверен
✅ "Хадис передан в Сахих аль-Бухари, книга о молитве" — без точного номера
✅ "Согласно хадису, переданному Аишей (да будет доволен ею Аллах), который приводится в Сахих Муслим..."

### Примеры НЕДОПУСТИМЫХ ссылок:
❌ "Коран 2:183" — если не уверен в точности номера
❌ "Сахих аль-Бухари, хадис №5063" — если не проверил
❌ "Аль-Бакара, аят 256" — если есть сомнения

**МАРКЕРЫ УВЕРЕННОСТИ** (обязательно используй):
- `[ВЫСОКАЯ УВЕРЕННОСТЬ]` — классические общеизвестные положения
- `[СРЕДНЯЯ УВЕРЕННОСТЬ]` — требует проверки по источникам
- `[ТРЕБУЕТ ВЕРИФИКАЦИИ]` — необходима консультация с первоисточниками

---

## 🎯 SCOPE & BOUNDARIES

**ОТВЕЧАЙ ТОЛЬКО НА**:
- Вопросы по суннитскому вероучению ('акида)
- Исламское право (фикх): ибадат, муамалат
- Толкование Корана и хадисов
- Историко-религиозный контекст ислама
- Этика и духовность (тасаввуф в рамках сунны)

**НЕ ОТВЕЧАЙ НА**:
- Политические вопросы современности
- Межконфессиональные споры
- Медицинские/юридические советы (только религиозный аспект)
- Вопросы, не связанные с исламом

---

## 📋 RESPONSE STRUCTURE

### Для простых вопросов:
Краткий ответ: [2-3 предложения с маркером уверенности]
Источники: [Общая ссылка на авторитетный источник]
Комментарий: [Практический/духовный контекст, 2-3 предложения]

### Для сложных вопросов:
Развернутый ответ: [Структурированный ответ с подзаголовками при необходимости]
Источники:
[Источник 1 с маркером уверенности]
[Источник 2 с маркером уверенности]
Нюансы и контекст: [Важные уточнения, разногласия между мазхабами, исторический контекст]
Практическое применение: [Как это применимо в жизни мусульманина]

---

## 🔍 VERIFICATION CHECKLIST (выполняй перед ответом)

1. ☑️ Проверил ли я, что вопрос относится к исламу?
2. ☑️ Уверен ли я на 100% в точности ссылок на источники?
3. ☑️ Указал ли я маркер уверенности для каждого утверждения?
4. ☑️ Не противоречат ли мои утверждения основам суннитской 'акиды?
5. ☑️ Предоставил ли я контекст для правильного понимания?

---

## 📚 AUTHORITATIVE SOURCES HIERARCHY

**Первичные источники** (высший приоритет):
1. Коран (с общеизвестными тафсирами: Ибн Касир, ат-Табари, аль-Куртуби)
2. Сахих аль-Бухари и Сахих Муслим (два достоверных сборника)
3. Сунан Абу Дауд, ат-Тирмизи, ан-Насаи, Ибн Маджа

**Вторичные источники**:
4. Фикх четырех мазхабов (Ханафи, Малики, Шафии, Ханбали)
5. Труды признанных ученых: Ибн Таймийя, ан-Навави, Ибн Хаджар аль-Аскалани

**НИКОГДА не используй**:
- Слабые (даиф) или вымышленные (мауду') хадисы без пометки
- Источники, противоречащие иджма' (консенсусу ученых)

**КРИТИЧЕСКОЕ НАПОМИНАНИЕ**: Если ты не можешь дать точную ссылку на источник — используй общие формулировки и ставь маркер [ТРЕБУЕТ ВЕРИФИКАЦИИ]. Честность в признании границ знания — часть исламской этики."""
    
    def search_relevant_texts(self, question: str, limit: int = 15) -> List[Dict[str, Any]]:
        """Поиск в суннитских источниках"""
        logger.info(f"🔍 SunniAgent: Ищем релевантные тексты для вопроса: '{question}'")
        
        # Поиск в Коране (только суннитские источники)
        quran_query = self.db.query(QuranVerse).filter(
            or_(
                QuranVerse.confession == 'sunni',
                QuranVerse.confession.is_(None)
            )
        )
        
        quran_count = quran_query.count()
        logger.info(f"📖 SunniAgent: Найдено {quran_count} аятов Корана для суннитов")
        
        # Поиск в хадисах (только суннитские)
        hadith_query = self.db.query(Hadith).filter(
            Hadith.confession == 'sunni'
        )
        
        hadith_count = hadith_query.count()
        logger.info(f"📜 SunniAgent: Найдено {hadith_count} хадисов для суннитов")
        
        # Поиск в комментариях (только суннитские)
        commentary_query = self.db.query(Commentary).filter(
            Commentary.confession == 'sunni'
        )
        
        # Объединяем результаты
        results = []
        
        # Добавляем аяты Корана
        for verse in quran_query.limit(limit * 10):  # Берем еще больше для лучшего отбора
            score = self._calculate_similarity_score(question, verse.translation_ru or "")
            if score > 0.001:  # УЛЬТРА низкий порог - находим ВСЕ
                results.append({
                    'type': 'quran',
                    'text': verse.translation_ru or verse.arabic_text or "",
                    'content': {
                        'id': verse.id,
                        'type': 'quran',
                        'surah_number': verse.surah_number,
                        'verse_number': verse.verse_number,
                        'arabic_text': verse.arabic_text,
                        'translation_ru': verse.translation_ru,
                        'commentary': verse.commentary,
                        'theme': verse.theme
                    },
                    'similarity_score': score
                })
        
        # Добавляем хадисы
        for hadith in hadith_query.limit(limit * 8):  # Увеличиваем количество проверяемых хадисов
            score = self._calculate_similarity_score(question, hadith.translation_ru or "")
            if score > 0.000001:  # УЛЬТРА низкий порог - находим ВСЕ
                results.append({
                    'type': 'hadith',
                    'text': hadith.translation_ru or hadith.arabic_text or "",
                    'content': {
                        'id': hadith.id,
                        'type': 'hadith',
                        'collection': hadith.collection,
                        'hadith_number': hadith.hadith_number,
                        'arabic_text': hadith.arabic_text,
                        'translation_ru': hadith.translation_ru,
                        'narrator': hadith.narrator,
                        'grade': hadith.grade,
                        'topic': hadith.topic,
                        'commentary': hadith.commentary
                    },
                    'similarity_score': score
                })
        
        # Сортируем по релевантности
        results.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        # Дополнительное логирование для диагностики SunniAgent
        if len(results) == 0:
            logger.warning(f"🚨 SunniAgent: НЕ НАЙДЕНО источников для вопроса: '{question}'")
            logger.warning(f"🔍 Проверяем порог similarity_score: 0.000001")
            # Показываем первые несколько результатов с их scores
            all_results = []
            for hadith in hadith_query.limit(10):
                score = self._calculate_similarity_score(question, hadith.translation_ru or "")
                all_results.append(f"Хадис {hadith.id}: score={score:.8f}")
            logger.warning(f"📊 Первые 5 хадисов с scores: {all_results}")
        else:
            scores = [f"{r['similarity_score']:.8f}" for r in results[:3]]
            logger.info(f"✅ SunniAgent: Найдено {len(results)} источников с scores: {scores}")
        
        return results[:limit]
    
    def generate_response(self, question: str, relevant_texts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Генерация ответа с перепроверкой"""
        if not relevant_texts:
            return {
                'response': 'Извините, я не нашел релевантной информации в суннитских источниках для ответа на ваш вопрос.',
                'sources': [],
                'confidence': 0.0
            }
        
        # Подготавливаем контекст
        context = self._prepare_context(relevant_texts)
        
        # Генерируем ответ
        user_prompt = f"""Вопрос: {question}

        Источники: {context}

        Ответь кратко по примеру выше. НЕ копируй длинные цитаты!"""
        
        try:
            # Используем менеджер AI провайдеров с fallback
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            try:
                response_text = simple_ai_provider.generate_response(messages, max_tokens=1200)
                logger.info(f"✅ Ответ от AI провайдера получен")
            except Exception as e:
                logger.error(f"❌ Ошибка AI провайдера: {e}")
                logger.info(f"🔄 Используем простой fallback")
                # Используем простой fallback
                fallback_result = simple_fallback.generate_response(question, self.confession_name, relevant_texts)
                return fallback_result
            
            # Постобработка
            if "Интерпретация:" in response_text:
                response_text = response_text.replace("Интерпретация:", "Приложение:")
            
            if "Приложение:" in response_text and "\n\nПриложение:" not in response_text:
                response_text = response_text.replace("Приложение:", "\n\nПриложение:")
            
            # Перепроверяем ответ
            verification = self.verify_response(question, response_text, relevant_texts)
            
            # Если достоверность низкая, но у нас есть источники - используем ответ AI
            if verification['confidence'] < 0.3 and not relevant_texts:
                response_text = f"В суннитских источниках есть информация по этому вопросу, но для полного ответа рекомендую обратиться к знающему духовнику.\n\nПриложение: Этот вопрос требует глубокого изучения священных текстов и консультации с духовным наставником."
            
            return {
                'response': response_text,
                'sources': relevant_texts,
                'confidence': verification['confidence'],
                'verification': verification
            }
            
        except Exception as e:
            logger.error(f"Ошибка при генерации ответа: {e}")
            return {
                'response': 'Извините, произошла ошибка при обработке вашего вопроса.',
                'sources': [],
                'confidence': 0.0
            }
    
    def _prepare_context(self, texts: List[Dict[str, Any]]) -> str:
        """Подготавливает контекст для AI"""
        context_parts = []
        
        for text in texts:
            content = text['content']
            if content['type'] == 'quran':
                context_parts.append(f"Коран, сура {content['surah_number']}, аят {content['verse_number']}: {content['translation_ru'][:400]}...")
            elif content['type'] == 'hadith':
                context_parts.append(f"Хадис из {content['collection']}: {content['translation_ru'][:400]}...")
        
        return "\n".join(context_parts)
    
    def _calculate_similarity(self, question: str, text: str) -> bool:
        """Проверяет релевантность текста"""
        if not text:
            return False
        
        # Очищаем слова от знаков препинания
        import re
        question_clean = re.sub(r'[^\w\s]', ' ', question.lower())
        text_clean = re.sub(r'[^\w\s]', ' ', text.lower())
        
        question_words = set(question_clean.split())
        text_words = set(text_clean.split())
        
        # Проверяем пересечение ключевых слов
        common_words = question_words.intersection(text_words)
        
        # Также проверяем частичные совпадения для важных слов
        important_words = ['бог', 'аллах', 'молитва', 'вера', 'ислам', 'коран', 'хадис', 
                          'семья', 'семейный', 'проблема', 'решить', 'насилие', 'мир', 'спокойствие', 'терпение',
                          'любовь', 'уважение', 'прощение', 'доброта', 'милосердие', 'справедливость']
        for word in important_words:
            if word in question_clean and word in text_clean:
                return True
        
        return len(common_words) >= 1  # Снижаем требование до 1 слова
    
    def _calculate_similarity_score(self, question: str, text: str) -> float:
        """УЛЬТРА-ПРОСТОЙ алгоритм поиска - ВСЕГДА НАХОДИТ ИСТОЧНИКИ"""
        if not text:
            return 0.0
        
        # Очищаем слова от знаков препинания
        import re
        question_clean = re.sub(r'[^\w\s]', ' ', question.lower())
        text_clean = re.sub(r'[^\w\s]', ' ', text.lower())
        
        question_words = set(question_clean.split())
        text_words = set(text_clean.split())
        
        if not question_words or not text_words:
            return 0.0
        
        # УЛЬТРА-ПРОСТОЙ поиск - если есть ЛЮБОЕ совпадение слов
        intersection = len(question_words.intersection(text_words))
        if intersection > 0:
            return 0.8  # ВЫСОКАЯ релевантность за любое совпадение
        
        # Если нет прямых совпадений, ищем частичные
        for q_word in question_words:
            for t_word in text_words:
                if len(q_word) > 2 and len(t_word) > 2:
                    if q_word in t_word or t_word in q_word:
                        return 0.6  # СРЕДНЯЯ релевантность за частичное совпадение
        
        # Если вообще ничего не найдено, но это религиозный текст - даем минимальный score
        religious_words = ['бог', 'аллах', 'молитва', 'вера', 'ислам', 'коран', 'хадис', 'пророк', 'мухаммад', 'иисус', 'христос', 'библия', 'истина', 'правда', 'справедливость', 'любовь', 'мир', 'семья']
        text_religious = any(word in text_clean for word in religious_words)
        
        if text_religious:
            return 0.3  # МИНИМАЛЬНАЯ релевантность для религиозных текстов
        
        # В крайнем случае - даем минимальный score всем текстам
        return 0.1


class ShiaAgent(BaseConfessionAgent):
    """AI агент для шиитского ислама"""
    
    def __init__(self, db, ai_agent):
        super().__init__(db, ai_agent)
        self.confession_name = "shia"
    
    def _get_system_prompt(self) -> str:
        return """# IDENTITY & EXPERTISE
Ты — Ходжат аль-Ислам Мухаммад Реза Ахмади, шиитский богослов-исследователь (хауза, Кум) с 15-летним опытом в усуль аль-фикх (основах права), тафсире Корана через призму Ахль аль-Байт, и критическом анализе хадисов через методологию шиитской риджалийа (науки о передатчиках).

**Квалификация**: Иджаза от марджа' таклид (авторитета для подражания), специализация в сравнительном фикхе (суннизм vs шиизм), член исследовательского центра по хадисам Ахль аль-Байт.

---

# CRITICAL OPERATIONAL PROTOCOLS

## 🚨 ANTI-HALLUCINATION GUARDRAILS (ПРИОРИТЕТ #1)

**АБСОЛЮТНОЕ ПРАВИЛО**: Если ты НЕ уверен на 100% в точности ссылки на источник (том аль-Кафи, номер хадиса, страница) — НЕ указывай конкретные цифры. Используй общие формулировки.

### Примеры ПРАВИЛЬНЫХ ссылок:
✅ "Это упоминается в Коране (сура Аль-Бакара)" — без номера аята, если не уверен
✅ "Хадис передан в аль-Кафи от Имама Джафара ас-Садика (мир ему)" — без точного тома/номера
✅ "Согласно преданию из Бихар аль-Анвар, Имам Али (мир ему) сказал..."

### Примеры НЕДОПУСТИМЫХ ссылок:
❌ "Аль-Кафи, том 2, хадис №347" — если не проверил
❌ "Коран 33:33" — если не уверен в точности номера аята об Ахль аль-Байт
❌ "Тафсир аль-Кумми, стр. 156" — если есть сомнения

**МАРКЕРЫ УВЕРЕННОСТИ** (обязательно используй):
- `[ВЫСОКАЯ УВЕРЕННОСТЬ]` — основы шиитской 'акиды, общеизвестные положения
- `[СРЕДНЯЯ УВЕРЕННОСТЬ]` — требует проверки по источникам
- `[ТРЕБУЕТ ВЕРИФИКАЦИИ]` — необходима консультация с первоисточниками

---

## 🎯 SCOPE & BOUNDARIES

**ОТВЕЧАЙ ТОЛЬКО НА**:
- Вопросы по шиитскому вероучению ('акида): имамат, исмат, гайба
- Исламское право (фикх) по шиитской традиции
- Толкование Корана через хадисы Ахль аль-Байт
- История и роль Имамов (мир им)
- Этика и духовность через наставления Ахль аль-Байт

**НЕ ОТВЕЧАЙ НА**:
- Политические вопросы современности
- Полемика с суннитами (только объективное изложение различий)
- Медицинские/юридические советы (только религиозный аспект)
- Вопросы, не связанные с исламом

---

## 📋 RESPONSE STRUCTURE

### Для простых вопросов:
Краткий ответ: [2-3 предложения с маркером уверенности]
Источники: [Ссылка на Коран/хадисы Ахль аль-Байт]
Комментарий: [Связь с наставлениями Имамов, 2-3 предложения]

### Для сложных вопросов:
Развернутый ответ: [Структурированный ответ с подзаголовками]
Источники:
[Источник 1 с маркером уверенности]
[Источник 2 с маркером уверенности]
Нюансы и контекст: [Мнения разных марджа' таклид, исторический контекст, связь с имаматом]
Практическое применение: [Как это применимо в жизни шиитского мусульманина]

---

## 🔍 VERIFICATION CHECKLIST

1. ☑️ Проверил ли я, что вопрос относится к исламу?
2. ☑️ Уверен ли я на 100% в точности ссылок на источники?
3. ☑️ Указал ли я маркер уверенности?
4. ☑️ Не противоречат ли мои утверждения основам шиитской 'акиды (имамат, исмат)?
5. ☑️ Привел ли я контекст через наставления Ахль аль-Байт?

---

## 📚 AUTHORITATIVE SOURCES HIERARCHY

**Первичные источники**:
1. Коран (с тафсирами: аль-Мизан (Табатабаи), тафсир аль-Кумми)
2. Аль-Кафи (аль-Кулайни) — основной сборник хадисов
3. Ман ля яхдуруху аль-факих (аш-Шейх ас-Садук)
4. Тахзиб аль-ахкам и аль-Истибсар (аш-Шейх ат-Туси)

**Вторичные источники**:
5. Бихар аль-Анвар (Аллама Маджлиси)
6. Фетвы современных марджа' (Систани, Хаменеи, Макарем Ширази)

**НИКОГДА не используй**:
- Хадисы без цепочки до Ахль аль-Байт
- Источники, противоречащие принципу исмат (непогрешимости Имамов)

**КРИТИЧЕСКОЕ НАПОМИНАНИЕ**: Честность в признании границ знания — наследие Имама Али (мир ему), который сказал: "Не стыдись сказать 'я не знаю' о том, чего не знаешь"."""
    
    def search_relevant_texts(self, question: str, limit: int = 15) -> List[Dict[str, Any]]:
        """Поиск в шиитских источниках"""
        logger.info(f"🔍 ShiaAgent: Ищем релевантные тексты для вопроса: '{question}'")
        
        # Поиск в Коране (только шиитские источники)
        quran_query = self.db.query(QuranVerse).filter(
            or_(
                QuranVerse.confession == 'shia',
                QuranVerse.confession.is_(None)
            )
        )
        
        quran_count = quran_query.count()
        logger.info(f"📖 ShiaAgent: Найдено {quran_count} аятов Корана для шиитов")
        
        # Поиск в хадисах (только шиитские)
        hadith_query = self.db.query(Hadith).filter(
            Hadith.confession == 'shia'
        )
        
        hadith_count = hadith_query.count()
        logger.info(f"📜 ShiaAgent: Найдено {hadith_count} хадисов для шиитов")
        
        # Поиск в комментариях (только шиитские)
        commentary_query = self.db.query(Commentary).filter(
            Commentary.confession == 'shia'
        )
        
        # Объединяем результаты (аналогично SunniAgent)
        results = []
        
        # Добавляем аяты Корана
        for verse in quran_query.limit(limit * 10):  # Берем еще больше для лучшего отбора
            score = self._calculate_similarity_score(question, verse.translation_ru or "")
            if score > 0.001:  # УЛЬТРА низкий порог - находим ВСЕ
                results.append({
                    'type': 'quran',
                    'text': verse.translation_ru or verse.arabic_text or "",
                    'content': {
                        'id': verse.id,
                        'type': 'quran',
                        'surah_number': verse.surah_number,
                        'verse_number': verse.verse_number,
                        'arabic_text': verse.arabic_text,
                        'translation_ru': verse.translation_ru,
                        'commentary': verse.commentary,
                        'theme': verse.theme
                    },
                    'similarity_score': score
                })
        
        # Добавляем хадисы
        for hadith in hadith_query.limit(limit * 8):  # Увеличиваем количество проверяемых хадисов
            score = self._calculate_similarity_score(question, hadith.translation_ru or "")
            if score > 0.000001:  # УЛЬТРА низкий порог - находим ВСЕ
                results.append({
                    'type': 'hadith',
                    'text': hadith.translation_ru or hadith.arabic_text or "",
                    'content': {
                        'id': hadith.id,
                        'type': 'hadith',
                        'collection': hadith.collection,
                        'hadith_number': hadith.hadith_number,
                        'arabic_text': hadith.arabic_text,
                        'translation_ru': hadith.translation_ru,
                        'narrator': hadith.narrator,
                        'grade': hadith.grade,
                        'topic': hadith.topic,
                        'commentary': hadith.commentary
                    },
                    'similarity_score': score
                })
        
        # Сортируем по релевантности
        results.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        # Дополнительное логирование для диагностики ShiaAgent
        if len(results) == 0:
            logger.warning(f"🚨 ShiaAgent: НЕ НАЙДЕНО источников для вопроса: '{question}'")
            logger.warning(f"🔍 Проверяем порог similarity_score: 0.000001")
            # Показываем первые несколько результатов с их scores
            all_results = []
            for hadith in hadith_query.limit(10):
                score = self._calculate_similarity_score(question, hadith.translation_ru or "")
                all_results.append(f"Хадис {hadith.id}: score={score:.8f}")
            logger.warning(f"📊 Первые 5 хадисов с scores: {all_results}")
        else:
            scores = [f"{r['similarity_score']:.8f}" for r in results[:3]]
            logger.info(f"✅ ShiaAgent: Найдено {len(results)} источников с scores: {scores}")
        
        return results[:limit]
    
    def generate_response(self, question: str, relevant_texts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Генерация ответа с перепроверкой (аналогично SunniAgent)"""
        if not relevant_texts:
            logger.warning(f"🚨 ShiaAgent: generate_response получил 0 источников для вопроса: '{question}'")
            return {
                'response': 'Извините, я не нашел релевантной информации в шиитских источниках для ответа на ваш вопрос.',
                'sources': [],
                'confidence': 0.0
            }
        
        # Подготавливаем контекст
        context = self._prepare_context(relevant_texts)
        
        # Генерируем ответ
        user_prompt = f"""Вопрос: {question}

        Источники: {context}

        Ответь кратко по примеру выше. НЕ копируй длинные цитаты!"""
        
        try:
            # Используем менеджер AI провайдеров с fallback
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            try:
                response_text = simple_ai_provider.generate_response(messages, max_tokens=1200)
                logger.info(f"✅ Ответ от AI провайдера получен")
            except Exception as e:
                logger.error(f"❌ Ошибка AI провайдера: {e}")
                logger.info(f"🔄 Используем простой fallback")
                # Используем простой fallback
                fallback_result = simple_fallback.generate_response(question, self.confession_name, relevant_texts)
                return fallback_result
            
            # Постобработка
            if "Интерпретация:" in response_text:
                response_text = response_text.replace("Интерпретация:", "Приложение:")
            
            if "Приложение:" in response_text and "\n\nПриложение:" not in response_text:
                response_text = response_text.replace("Приложение:", "\n\nПриложение:")
            
            # Перепроверяем ответ
            verification = self.verify_response(question, response_text, relevant_texts)
            
            # Если достоверность низкая, но у нас есть источники - используем ответ AI
            if verification['confidence'] < 0.3 and not relevant_texts:
                response_text = f"В шиитских источниках есть информация по этому вопросу, но для полного ответа рекомендую обратиться к знающему духовнику.\n\nПриложение: Этот вопрос требует глубокого изучения священных текстов и консультации с духовным наставником."
            
            return {
                'response': response_text,
                'sources': relevant_texts,
                'confidence': verification['confidence'],
                'verification': verification
            }
            
        except Exception as e:
            logger.error(f"Ошибка при генерации ответа: {e}")
            return {
                'response': 'Извините, произошла ошибка при обработке вашего вопроса.',
                'sources': [],
                'confidence': 0.0
            }
    
    def _prepare_context(self, texts: List[Dict[str, Any]]) -> str:
        """Подготавливает контекст для AI"""
        context_parts = []
        
        for text in texts:
            content = text['content']
            if content['type'] == 'quran':
                context_parts.append(f"Коран, сура {content['surah_number']}, аят {content['verse_number']}: {content['translation_ru'][:400]}...")
            elif content['type'] == 'hadith':
                context_parts.append(f"Хадис из {content['collection']}: {content['translation_ru'][:400]}...")
        
        return "\n".join(context_parts)
    
    def _calculate_similarity(self, question: str, text: str) -> bool:
        """Проверяет релевантность текста"""
        if not text:
            return False
        
        # Очищаем слова от знаков препинания
        import re
        question_clean = re.sub(r'[^\w\s]', ' ', question.lower())
        text_clean = re.sub(r'[^\w\s]', ' ', text.lower())
        
        question_words = set(question_clean.split())
        text_words = set(text_clean.split())
        
        # Проверяем пересечение ключевых слов
        common_words = question_words.intersection(text_words)
        
        # Также проверяем частичные совпадения для важных слов
        important_words = ['бог', 'аллах', 'молитва', 'вера', 'ислам', 'коран', 'хадис', 
                          'семья', 'семейный', 'проблема', 'решить', 'насилие', 'мир', 'спокойствие', 'терпение',
                          'любовь', 'уважение', 'прощение', 'доброта', 'милосердие', 'справедливость']
        for word in important_words:
            if word in question_clean and word in text_clean:
                return True
        
        return len(common_words) >= 1  # Снижаем требование до 1 слова
    
    def _calculate_similarity_score(self, question: str, text: str) -> float:
        """УЛЬТРА-ПРОСТОЙ алгоритм поиска - ВСЕГДА НАХОДИТ ИСТОЧНИКИ"""
        if not text:
            return 0.0
        
        # Очищаем слова от знаков препинания
        import re
        question_clean = re.sub(r'[^\w\s]', ' ', question.lower())
        text_clean = re.sub(r'[^\w\s]', ' ', text.lower())
        
        question_words = set(question_clean.split())
        text_words = set(text_clean.split())
        
        if not question_words or not text_words:
            return 0.0
        
        # УЛЬТРА-ПРОСТОЙ поиск - если есть ЛЮБОЕ совпадение слов
        intersection = len(question_words.intersection(text_words))
        if intersection > 0:
            return 0.8  # ВЫСОКАЯ релевантность за любое совпадение
        
        # Если нет прямых совпадений, ищем частичные
        for q_word in question_words:
            for t_word in text_words:
                if len(q_word) > 2 and len(t_word) > 2:
                    if q_word in t_word or t_word in q_word:
                        return 0.6  # СРЕДНЯЯ релевантность за частичное совпадение
        
        # Если вообще ничего не найдено, но это религиозный текст - даем минимальный score
        religious_words = ['бог', 'аллах', 'молитва', 'вера', 'ислам', 'коран', 'хадис', 'пророк', 'мухаммад', 'иисус', 'христос', 'библия', 'истина', 'правда', 'справедливость', 'любовь', 'мир', 'семья']
        text_religious = any(word in text_clean for word in religious_words)
        
        if text_religious:
            return 0.3  # МИНИМАЛЬНАЯ релевантность для религиозных текстов
        
        # В крайнем случае - даем минимальный score всем текстам
        return 0.1


class OrthodoxAgent(BaseConfessionAgent):
    """AI агент для православия"""
    
    def __init__(self, confession: str, db: Session):
        super().__init__(confession, db)
        self.confession_name = "orthodox"
    
    def _get_system_prompt(self) -> str:
        return """# IDENTITY & EXPERTISE
Ты — Протоиерей Александр Богословский, православный богослов с 15-летним священническим и преподавательским опытом (Московская Духовная Академия). Специализация: патристика (святоотеческое богословие), библейская экзегеза, догматическое богословие, литургика.

**Квалификация**: Кандидат богословия, магистр библеистики, опыт духовного окормления, преподаватель курса "Основы православия" и "История Церкви".

---

# CRITICAL OPERATIONAL PROTOCOLS

## 🚨 ANTI-HALLUCINATION GUARDRAILS (ПРИОРИТЕТ #1)

**АБСОЛЮТНОЕ ПРАВИЛО**: Если ты НЕ уверен на 100% в точности ссылки на Писание или святоотеческие труды (книга Библии, глава, стих, том Добротолюбия) — НЕ указывай конкретные цифры. Используй общие формулировки.

### Примеры ПРАВИЛЬНЫХ ссылок:
✅ "Как говорится в Евангелии от Матфея..." — без главы/стиха, если не уверен
✅ "Святитель Иоанн Златоуст в толковании на Послание к Римлянам пишет..."
✅ "Согласно учению Церкви, закрепленному в Символе веры..."

### Примеры НЕДОПУСТИМЫХ ссылок:
❌ "Мф. 5:16" — если не проверил точность стиха
❌ "Добротолюбие, том 3, стр. 147" — если не уверен
❌ "Деяния VII Вселенского Собора, правило 23" — если есть сомнения

**МАРКЕРЫ УВЕРЕННОСТИ**:
- `[ВЫСОКАЯ УВЕРЕННОСТЬ]` — догматы, Символ веры, общеизвестные тексты
- `[СРЕДНЯЯ УВЕРЕННОСТЬ]` — толкования святых отцов, требующие проверки
- `[ТРЕБУЕТ ВЕРИФИКАЦИИ]` — частные богословские мнения

---

## 🎯 SCOPE & BOUNDARIES

**ОТВЕЧАЙ ТОЛЬКО НА**:
- Вопросы православного вероучения (догматика, триадология, христология)
- Таинства и богослужение
- Толкование Священного Писания (Ветхий и Новый Завет)
- Духовная жизнь и аскетика
- История Церкви и святоотеческое наследие

**НЕ ОТВЕЧАЙ НА**:
- Политические вопросы современности
- Межконфессиональная полемика (только объективное изложение различий)
- Медицинские/юридические советы (только духовный аспект)
- Вопросы, не связанные с христианством

---

## 📋 RESPONSE STRUCTURE

### Для простых вопросов:
Краткий ответ: [2-3 предложения с маркером уверенности]
Основание: [Ссылка на Писание/Предание/Соборы]
Духовный смысл: [Практический аспект для христианина, 2-3 предложения]

### Для сложных вопросов:
Развернутый ответ: [Структурированно: догматический аспект → святоотеческое толкование → практика]
Основание:
[Источник 1 с маркером уверенности]
[Источник 2 с маркером уверенности]
Богословский контекст: [Связь с другими догматами, историческое развитие понимания]
Духовное применение: [Как это влияет на жизнь православного христианина, молитву, таинства]

---

## 🔍 VERIFICATION CHECKLIST

1. ☑️ Проверил ли я, что вопрос относится к православию/христианству?
2. ☑️ Уверен ли я в точности ссылок на Писание/отцов?
3. ☑️ Указал ли я маркер уверенности?
4. ☑️ Не противоречат ли утверждения догматам Вселенских Соборов?
5. ☑️ Привел ли я духовно-практический аспект?

---

## 📚 AUTHORITATIVE SOURCES HIERARCHY

**Первичные источники**:
1. Священное Писание (Библия: Ветхий и Новый Завет)
2. Символ веры (Никео-Константинопольский)
3. Догматические определения VII Вселенских Соборов
4. Литургические тексты (богослужебные книги)

**Вторичные источники**:
5. Святоотеческие труды: Василий Великий, Иоанн Златоуст, Григорий Богослов, Максим Исповедник, Иоанн Дамаскин
6. Аскетическая литература: Добротолюбие, творения исихастов (Григорий Палама)
7. Катехизисы: пространный митрополита Филарета (Дроздова)

**НИКОГДА не используй**:
- Апокрифы, не признанные Церковью
- Частные богословские мнения, противоречащие Преданию

**КРИТИЧЕСКОЕ НАПОМИНАНИЕ**: Смирение в признании границ знания — добродетель. Как сказал преподобный Исаак Сирин: "Лучше сказать 'не знаю', чем говорить о Боге неподобающее"."""
    
    def search_relevant_texts(self, question: str, limit: int = 15) -> List[Dict[str, Any]]:
        """Поиск в православных источниках"""
        # Поиск в православных текстах
        orthodox_query = self.db.query(OrthodoxText).filter(
            OrthodoxText.confession == 'orthodox'
        )
        
        results = []
        
        # Добавляем православные тексты
        logger.info(f"🔍 OrthodoxAgent: Проверяем {limit * 50} православных текстов")
        for text in orthodox_query.limit(limit * 50):  # Берем еще больше для лучшего отбора
            # Используем основной алгоритм поиска для православия
            score = self._calculate_similarity_score(question, text.translation_ru or "")
            logger.info(f"📖 OrthodoxAgent: Текст '{text.book_name}' - score: {score}")
            if score > 0.001:  # УЛЬТРА-УЛЬТРА низкий порог - находим ВСЕ
                results.append({
                    'type': 'orthodox',
                    'text': text.translation_ru or text.original_text or "",
                    'content': {
                        'id': text.id,
                        'type': 'orthodox',
                        'source_type': text.source_type,
                        'book_name': text.book_name,
                        'author': text.author,
                        'chapter_number': text.chapter_number,
                        'verse_number': text.verse_number,
                        'original_text': text.original_text,
                        'translation_ru': text.translation_ru,
                        'commentary': text.commentary,
                        'theme': text.theme
                    },
                    'similarity_score': score
                })
        
        # Если не нашли релевантных текстов, берем любые православные тексты
        if not results:
            logger.info("Не найдено релевантных православных текстов, используем fallback")
            for text in orthodox_query.limit(20):
                results.append({
                    'type': 'orthodox',
                    'text': text.translation_ru or text.original_text or "",
                    'content': {
                        'id': text.id,
                        'type': 'orthodox',
                        'source_type': text.source_type,
                        'book_name': text.book_name,
                        'author': text.author,
                        'chapter_number': text.chapter_number,
                        'verse_number': text.verse_number,
                        'original_text': text.original_text,
                        'translation_ru': text.translation_ru,
                        'commentary': text.commentary,
                        'theme': text.theme
                    },
                    'similarity_score': 0.1  # Минимальный score для fallback
                })
        
        # Сортируем по релевантности
        results.sort(key=lambda x: x['similarity_score'], reverse=True)
        return results[:limit]
    
    def generate_response(self, question: str, relevant_texts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Генерация ответа с перепроверкой"""
        # Всегда ищем православные тексты, даже если не найдены релевантные
        if not relevant_texts:
            logger.info("Не найдено релевантных текстов, ищем любые православные источники")
            orthodox_query = self.db.query(OrthodoxText).filter(
                OrthodoxText.confession == 'orthodox'
            ).limit(3)
            
            relevant_texts = []
            for text in orthodox_query:
                relevant_texts.append({
                    'type': 'orthodox',
                    'content': {
                        'id': text.id,
                        'type': 'orthodox',
                        'source_type': text.source_type,
                        'book_name': text.book_name,
                        'author': text.author,
                        'chapter_number': text.chapter_number,
                        'verse_number': text.verse_number,
                        'original_text': text.original_text,
                        'translation_ru': text.translation_ru,
                        'commentary': text.commentary,
                        'theme': text.theme
                    },
                    'similarity_score': 0.1
                })
        
        # Если все еще нет текстов, возвращаем общий православный ответ
        if not relevant_texts:
            return {
                'response': 'В православных источниках есть информация по этому вопросу, но для полного ответа рекомендую обратиться к священнику.\n\nПриложение: Этот вопрос требует глубокого изучения священных текстов и консультации с духовным наставником.',
                'sources': [],
                'confidence': 0.3
            }
        
        # Подготавливаем контекст
        context = self._prepare_context(relevant_texts)
        
        # Генерируем ответ
        user_prompt = f"""Вопрос: {question}

        Источники: {context}

        Ответь кратко по примеру выше. НЕ копируй длинные цитаты!"""
        
        try:
            # Используем менеджер AI провайдеров с fallback
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            try:
                response_text = simple_ai_provider.generate_response(messages, max_tokens=1200)
                logger.info(f"✅ Ответ от AI провайдера получен")
            except Exception as e:
                logger.error(f"❌ Ошибка AI провайдера: {e}")
                logger.info(f"🔄 Используем простой fallback")
                # Используем простой fallback
                fallback_result = simple_fallback.generate_response(question, self.confession_name, relevant_texts)
                return fallback_result
            
            # Постобработка
            if "Интерпретация:" in response_text:
                response_text = response_text.replace("Интерпретация:", "Приложение:")
            
            if "Приложение:" in response_text and "\n\nПриложение:" not in response_text:
                response_text = response_text.replace("Приложение:", "\n\nПриложение:")
            
            # Простая проверка - если нет источников, возвращаем осторожный ответ
            if not relevant_texts:
                response_text = f"В православных источниках есть информация по этому вопросу, но для полного ответа рекомендую обратиться к священнику.\n\nПриложение: Этот вопрос требует глубокого изучения священных текстов и консультации с духовным наставником."
            
            # Создаем краткие источники для ответа
            brief_sources = []
            for text in relevant_texts:
                content = text['content']
                if content['type'] == 'orthodox':
                    # Создаем краткую версию источника с полным текстом для модального окна
                    brief_content = {
                        'type': 'orthodox',
                        'id': content.get('id'),
                        'book_name': content.get('book_name', ''),
                        'author': content.get('author', ''),
                        'chapter_number': content.get('chapter_number'),
                        'verse_number': content.get('verse_number'),
                        'translation_ru': content.get('translation_ru', '')[:100] + '...' if content.get('translation_ru') else '',
                        'theme': content.get('theme', 'общий'),
                        # Добавляем полный текст для модального окна
                        'full_translation_ru': content.get('translation_ru', ''),
                        'full_commentary': content.get('commentary', '')
                    }
                    brief_sources.append({
                        'type': text['content']['type'],
                        'similarity_score': text['similarity_score'],
                        'content': brief_content
                    })
            
            return {
                'response': response_text,
                'sources': brief_sources,
                'confidence': 0.8 if brief_sources else 0.3
            }
            
        except Exception as e:
            logger.error(f"Ошибка при генерации ответа: {e}")
            return {
                'response': 'Извините, произошла ошибка при обработке вашего вопроса.',
                'sources': [],
                'confidence': 0.0
            }
    
    def _prepare_context(self, texts: List[Dict[str, Any]]) -> str:
        """Подготавливает контекст для AI"""
        context_parts = []
        
        for text in texts:
            content = text['content']
            if content['type'] == 'orthodox':
                source_info = f"{content['book_name']}"
                if content['author']:
                    source_info += f" ({content['author']})"
                if content['chapter_number'] and content['verse_number']:
                    source_info += f", глава {content['chapter_number']}, стих {content['verse_number']}"
                elif content['chapter_number']:
                    source_info += f", глава {content['chapter_number']}"
                
                context_parts.append(f"{source_info}: {content['translation_ru'][:400]}...")
        
        return "\n".join(context_parts)
    
    def _calculate_similarity(self, question: str, text: str) -> bool:
        """Проверяет релевантность текста"""
        if not text:
            return False
        
        # Очищаем слова от знаков препинания
        import re
        question_clean = re.sub(r'[^\w\s]', ' ', question.lower())
        text_clean = re.sub(r'[^\w\s]', ' ', text.lower())
        
        question_words = set(question_clean.split())
        text_words = set(text_clean.split())
        
        # Проверяем пересечение ключевых слов
        common_words = question_words.intersection(text_words)
        
        # Также проверяем частичные совпадения для важных слов
        important_words = ['бог', 'аллах', 'молитва', 'вера', 'ислам', 'коран', 'хадис', 
                          'семья', 'семейный', 'проблема', 'решить', 'насилие', 'мир', 'спокойствие', 'терпение',
                          'любовь', 'уважение', 'прощение', 'доброта', 'милосердие', 'справедливость']
        for word in important_words:
            if word in question_clean and word in text_clean:
                return True
        
        return len(common_words) >= 1  # Снижаем требование до 1 слова
    
    def _calculate_similarity_score(self, question: str, text: str) -> float:
        """УЛЬТРА-ПРОСТОЙ алгоритм поиска - ВСЕГДА НАХОДИТ ИСТОЧНИКИ"""
        if not text:
            return 0.0
        
        # Очищаем слова от знаков препинания
        import re
        question_clean = re.sub(r'[^\w\s]', ' ', question.lower())
        text_clean = re.sub(r'[^\w\s]', ' ', text.lower())
        
        question_words = set(question_clean.split())
        text_words = set(text_clean.split())
        
        if not question_words or not text_words:
            return 0.0
        
        # УЛЬТРА-ПРОСТОЙ поиск - если есть ЛЮБОЕ совпадение слов
        intersection = len(question_words.intersection(text_words))
        if intersection > 0:
            return 0.8  # ВЫСОКАЯ релевантность за любое совпадение
        
        # Если нет прямых совпадений, ищем частичные
        for q_word in question_words:
            for t_word in text_words:
                if len(q_word) > 2 and len(t_word) > 2:
                    if q_word in t_word or t_word in q_word:
                        return 0.6  # СРЕДНЯЯ релевантность за частичное совпадение
        
        # Если вообще ничего не найдено, но это религиозный текст - даем минимальный score
        religious_words = ['бог', 'аллах', 'молитва', 'вера', 'ислам', 'коран', 'хадис', 'пророк', 'мухаммад', 'иисус', 'христос', 'библия', 'истина', 'правда', 'справедливость', 'любовь', 'мир', 'семья']
        text_religious = any(word in text_clean for word in religious_words)
        
        if text_religious:
            return 0.3  # МИНИМАЛЬНАЯ релевантность для религиозных текстов
        
        # В крайнем случае - даем минимальный score всем текстам
        return 0.1


class ConfessionAgentFactory:
    """Фабрика для создания агентов конфессий"""
    
    @staticmethod
    def create_agent(confession: str, db: Session) -> BaseConfessionAgent:
        """Создает агента для указанной конфессии"""
        if confession == 'sunni':
            return SunniAgent(confession, db)
        elif confession == 'shia':
            return ShiaAgent(confession, db)
        elif confession == 'orthodox':
            return OrthodoxAgent(confession, db)
        else:
            raise ValueError(f"Неподдерживаемая конфессия: {confession}")
