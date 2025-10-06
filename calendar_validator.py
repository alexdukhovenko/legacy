#!/usr/bin/env python3
"""
Простая система проверки для календаря
Четкие правила - никакой засорки
"""

import re
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

class CalendarValidator:
    """Простая валидация для календарных событий"""
    
    def __init__(self):
        # Четкие ключевые слова для календаря
        self.calendar_keywords = {
            "встречи": ["встреча", "встретиться", "встретиться с", "свидание", "деловая встреча"],
            "звонки": ["звонок", "позвонить", "созвон", "телефонный звонок", "видеозвонок"],
            "события": ["событие", "мероприятие", "конференция", "семинар", "презентация"],
            "приемы": ["прием", "прием у врача", "стоматолог", "врач", "медицинский прием"],
            "время": ["в", "на", "завтра в", "сегодня в", "в понедельник", "в среду", "в пятницу"]
        }
        
        # Слова, которые НЕ должны попадать в календарь
        self.not_calendar_keywords = [
            "купить", "забрать", "отнести", "сделать", "создать", "написать", 
            "отправить", "прочитать", "изучить", "выучить", "запомнить",
            "подумать", "решить", "выбрать", "найти", "поискать"
        ]
        
        # Паттерны времени
        self.time_patterns = [
            r'(\d{1,2}):(\d{2})',  # 15:30, 9:00
            r'(\d{1,2})\.(\d{2})',  # 15.30, 9.00
            r'в (\d{1,2})',  # в 15, в 9
            r'на (\d{1,2})',  # на 15, на 9
        ]
    
    def should_go_to_calendar(self, text: str) -> Tuple[bool, str, Optional[datetime]]:
        """
        Простая проверка: должно ли событие попасть в календарь
        
        Returns:
            (should_go, reason, event_time)
        """
        text_lower = text.lower()
        
        # 1. Проверяем, есть ли четкие календарные ключевые слова
        calendar_score = 0
        found_keywords = []
        
        for category, keywords in self.calendar_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    calendar_score += 1
                    found_keywords.append(keyword)
        
        # 2. Проверяем, есть ли слова, которые НЕ должны быть в календаре
        not_calendar_score = 0
        for keyword in self.not_calendar_keywords:
            if keyword in text_lower:
                not_calendar_score += 1
        
        # 3. Проверяем наличие времени
        has_time = self._extract_time(text) is not None
        
        # 4. Принимаем решение по простым правилам
        
        # Правило 1: Если есть четкие календарные слова И время - точно в календарь
        if calendar_score > 0 and has_time:
            event_time = self._extract_time(text)
            return True, f"Календарное событие с временем: {', '.join(found_keywords)}", event_time
        
        # Правило 2: Если есть только календарные слова без времени - спрашиваем время
        if calendar_score > 0 and not has_time:
            return False, f"Календарное событие без времени: {', '.join(found_keywords)}. Нужно указать время!", None
        
        # Правило 3: Если есть только время без календарных слов - не в календарь
        if has_time and calendar_score == 0:
            return False, "Есть время, но не похоже на календарное событие", None
        
        # Правило 4: Если есть слова "не для календаря" - точно не в календарь
        if not_calendar_score > 0:
            return False, "Это задача, а не календарное событие", None
        
        # Правило 5: По умолчанию - не в календарь
        return False, "Не похоже на календарное событие", None
    
    def _extract_time(self, text: str) -> Optional[datetime]:
        """Извлекает время из текста"""
        text_lower = text.lower()
        
        # Ищем время в разных форматах
        for pattern in self.time_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    hour = int(match.group(1))
                    minute = int(match.group(2)) if len(match.groups()) > 1 else 0
                    
                    # Валидация времени
                    if 0 <= hour <= 23 and 0 <= minute <= 59:
                        # Определяем дату
                        event_date = self._determine_date(text_lower)
                        return event_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
                except (ValueError, IndexError):
                    continue
        
        return None
    
    def _determine_date(self, text_lower: str) -> datetime:
        """Определяет дату события"""
        now = datetime.now()
        
        # Сегодня
        if any(word in text_lower for word in ["сегодня", "сейчас"]):
            return now
        
        # Завтра
        if "завтра" in text_lower:
            return now + timedelta(days=1)
        
        # Дни недели
        weekdays = {
            "понедельник": 0, "вторник": 1, "среда": 2, "четверг": 3,
            "пятница": 4, "суббота": 5, "воскресенье": 6
        }
        
        for day, day_num in weekdays.items():
            if day in text_lower:
                # Находим следующий день недели
                days_ahead = day_num - now.weekday()
                if days_ahead <= 0:  # Если день уже прошел на этой неделе
                    days_ahead += 7
                return now + timedelta(days=days_ahead)
        
        # По умолчанию - завтра
        return now + timedelta(days=1)
    
    def get_calendar_suggestions(self, text: str) -> str:
        """Возвращает предложения по улучшению для календаря"""
        text_lower = text.lower()
        suggestions = []
        
        # Проверяем наличие времени
        if not self._extract_time(text):
            suggestions.append("• Добавь время: 'встреча завтра в 15:00'")
        
        # Проверяем четкость события
        if not any(keyword in text_lower for keyword in 
                  ["встреча", "звонок", "событие", "прием", "мероприятие"]):
            suggestions.append("• Уточни тип события: 'встреча', 'звонок', 'событие'")
        
        if suggestions:
            return "💡 **Для календаря лучше:**\n" + "\n".join(suggestions)
        
        return "✅ Готово для календаря!"


# Тест валидатора
def test_calendar_validator():
    """Тестирует валидатор календаря"""
    validator = CalendarValidator()
    
    test_cases = [
        "Встреча завтра в 15:00",
        "Звонок в 10:30",
        "Купить молоко",
        "Создать сайт",
        "Прием у врача в понедельник в 14:00",
        "Презентация в среду",
        "Написать отчет",
        "Событие завтра в 18:00",
        "Встретиться с клиентом в пятницу в 11:00"
    ]
    
    print("🧪 Тестируем валидатор календаря:\n")
    
    for text in test_cases:
        should_go, reason, event_time = validator.should_go_to_calendar(text)
        suggestions = validator.get_calendar_suggestions(text)
        
        status = "📅 КАЛЕНДАРЬ" if should_go else "❌ НЕ КАЛЕНДАРЬ"
        time_str = f" ({event_time.strftime('%H:%M %d.%m')})" if event_time else ""
        
        print(f"{status}: {text}{time_str}")
        print(f"   Причина: {reason}")
        if not should_go and "время" in reason.lower():
            print(f"   {suggestions}")
        print()

if __name__ == "__main__":
    test_calendar_validator()
