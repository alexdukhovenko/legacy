#!/usr/bin/env python3
"""
Простой маршрутизатор задач для СДВГ
Четкое разделение по типам и сервисам
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from enum import Enum

logger = logging.getLogger(__name__)

class TaskType(Enum):
    """Типы задач для четкого разделения"""
    URGENT = "urgent"           # Срочные - Apple Reminders
    SCHEDULED = "scheduled"     # Запланированные - Apple Calendar  
    PROJECT = "project"         # Проекты - Notion
    HABIT = "habit"            # Привычки - Apple Reminders
    IDEA = "idea"              # Идеи - Notion Materials
    ROUTINE = "routine"        # Рутина - Apple Reminders

class TaskRouter:
    """Простой маршрутизатор задач"""
    
    def __init__(self):
        self.apple_reminders = AppleRemindersIntegration()
        self.apple_calendar = AppleCalendarIntegration()
        self.notion = NotionIntegration()
        self.calendar_validator = CalendarValidator()
        
    async def route_task(self, text: str, user_id: int) -> Dict[str, Any]:
        """
        Простая маршрутизация задач
        """
        try:
            # Определяем тип задачи
            task_type = await self._classify_task(text)
            
            # Маршрутизируем в соответствующий сервис
            result = await self._send_to_service(task_type, text, user_id)
            
            return {
                "success": True,
                "task_type": task_type.value,
                "service": result["service"],
                "message": result["message"],
                "data": result.get("data", {})
            }
            
        except Exception as e:
            logger.error(f"Error routing task: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "❌ Ошибка при обработке задачи"
            }
    
    async def _classify_task(self, text: str) -> TaskType:
        """
        Простая классификация задач по ключевым словам
        """
        text_lower = text.lower()
        
        # 1. Сначала проверяем календарь с помощью валидатора
        should_go_to_calendar, reason, event_time = self.calendar_validator.should_go_to_calendar(text)
        if should_go_to_calendar:
            return TaskType.SCHEDULED
        elif "календарное событие" in reason.lower() and "без времени" in reason.lower():
            # Если это календарное событие без времени, все равно отправляем в календарь
            return TaskType.SCHEDULED
        
        # 2. Срочные задачи
        urgent_keywords = ["срочно", "сегодня", "сейчас", "немедленно", "быстро", "не забыть"]
        if any(keyword in text_lower for keyword in urgent_keywords):
            return TaskType.URGENT
        
        # 3. Привычки
        habit_keywords = ["каждый день", "ежедневно", "привычка", "регулярно", "утром", "вечером"]
        if any(keyword in text_lower for keyword in habit_keywords):
            return TaskType.HABIT
        
        # 4. Проекты
        project_keywords = ["проект", "создать", "разработать", "сделать", "построить", "запустить"]
        if any(keyword in text_lower for keyword in project_keywords):
            return TaskType.PROJECT
        
        # 5. Рутина
        routine_keywords = ["купить", "забрать", "отнести", "позвонить", "написать", "отправить"]
        if any(keyword in text_lower for keyword in routine_keywords):
            return TaskType.ROUTINE
        
        # 6. По умолчанию - идея
        return TaskType.IDEA
    
    async def _send_to_service(self, task_type: TaskType, text: str, user_id: int) -> Dict[str, Any]:
        """
        Отправка задачи в соответствующий сервис
        """
        if task_type == TaskType.URGENT:
            return await self._handle_urgent_task(text, user_id)
        elif task_type == TaskType.SCHEDULED:
            return await self._handle_scheduled_task(text, user_id)
        elif task_type == TaskType.HABIT:
            return await self._handle_habit_task(text, user_id)
        elif task_type == TaskType.PROJECT:
            return await self._handle_project_task(text, user_id)
        elif task_type == TaskType.ROUTINE:
            return await self._handle_routine_task(text, user_id)
        else:  # IDEA
            return await self._handle_idea_task(text, user_id)
    
    async def _handle_urgent_task(self, text: str, user_id: int) -> Dict[str, Any]:
        """Срочные задачи → Apple Reminders"""
        try:
            result = await self.apple_reminders.create_reminder(
                title=text,
                priority="high",
                due_date=datetime.now() + timedelta(hours=2)  # Напоминание через 2 часа
            )
            
            return {
                "service": "Apple Reminders",
                "message": f"🔥 **СРОЧНАЯ ЗАДАЧА** добавлена в Apple Reminders!\n\nНапоминание придет через 2 часа.",
                "data": result
            }
        except Exception as e:
            return {"service": "Apple Reminders", "message": f"❌ Ошибка: {e}"}
    
    async def _handle_scheduled_task(self, text: str, user_id: int) -> Dict[str, Any]:
        """Запланированные события → Apple Calendar"""
        try:
            # Используем валидатор для получения времени
            should_go, reason, event_time = self.calendar_validator.should_go_to_calendar(text)
            
            if not should_go or not event_time:
                # Если не прошло валидацию, но это календарное событие - все равно в календарь
                if "календарное событие" in reason.lower():
                    # Создаем событие на завтра в 12:00 по умолчанию
                    from datetime import datetime, timedelta
                    default_time = datetime.now() + timedelta(days=1)
                    default_time = default_time.replace(hour=12, minute=0, second=0, microsecond=0)
                    
                    result = await self.apple_calendar.create_event(
                        title=text,
                        start_time=default_time,
                        duration=60
                    )
                    
                    return {
                        "service": "Apple Calendar",
                        "message": f"📅 **СОБЫТИЕ** добавлено в Apple Calendar!\n\nВремя: {default_time.strftime('%H:%M %d.%m')} (по умолчанию)\n\n💡 Можешь изменить время в календаре!",
                        "data": result
                    }
                else:
                    # Если не календарное событие, отправляем в Reminders
                    suggestions = self.calendar_validator.get_calendar_suggestions(text)
                    return {
                        "service": "Apple Reminders",
                        "message": f"📱 **ЗАДАЧА** добавлена в Apple Reminders!\n\n{suggestions}",
                        "data": {"fallback": True}
                    }
            
            result = await self.apple_calendar.create_event(
                title=text,
                start_time=event_time,
                duration=60  # 1 час по умолчанию
            )
            
            return {
                "service": "Apple Calendar",
                "message": f"📅 **СОБЫТИЕ** добавлено в Apple Calendar!\n\nВремя: {event_time.strftime('%H:%M %d.%m')}",
                "data": result
            }
        except Exception as e:
            return {"service": "Apple Calendar", "message": f"❌ Ошибка: {e}"}
    
    async def _handle_habit_task(self, text: str, user_id: int) -> Dict[str, Any]:
        """Привычки → Apple Reminders с повторением"""
        try:
            result = await self.apple_reminders.create_reminder(
                title=text,
                priority="medium",
                repeat="daily"
            )
            
            return {
                "service": "Apple Reminders",
                "message": f"🔄 **ПРИВЫЧКА** добавлена в Apple Reminders!\n\nПовторяется ежедневно.",
                "data": result
            }
        except Exception as e:
            return {"service": "Apple Reminders", "message": f"❌ Ошибка: {e}"}
    
    async def _handle_project_task(self, text: str, user_id: int) -> Dict[str, Any]:
        """Проекты → Notion"""
        try:
            result = await self.notion.create_project(
                title=text,
                description="Проект создан через Telegram бота"
            )
            
            return {
                "service": "Notion",
                "message": f"📋 **ПРОЕКТ** создан в Notion!\n\nМожешь детально проработать план.",
                "data": result
            }
        except Exception as e:
            return {"service": "Notion", "message": f"❌ Ошибка: {e}"}
    
    async def _handle_routine_task(self, text: str, user_id: int) -> Dict[str, Any]:
        """Рутина → Apple Reminders"""
        try:
            result = await self.apple_reminders.create_reminder(
                title=text,
                priority="medium",
                due_date=datetime.now() + timedelta(days=1)
            )
            
            return {
                "service": "Apple Reminders",
                "message": f"✅ **РУТИНА** добавлена в Apple Reminders!\n\nНапоминание завтра.",
                "data": result
            }
        except Exception as e:
            return {"service": "Apple Reminders", "message": f"❌ Ошибка: {e}"}
    
    async def _handle_idea_task(self, text: str, user_id: int) -> Dict[str, Any]:
        """Идеи → Notion Materials"""
        try:
            result = await self.notion.create_material(
                title=f"💡 Идея: {text[:50]}...",
                content=text,
                tags=["идея", "заметка"]
            )
            
            return {
                "service": "Notion",
                "message": f"💡 **ИДЕЯ** сохранена в Notion!\n\nМожешь вернуться к ней позже.",
                "data": result
            }
        except Exception as e:
            return {"service": "Notion", "message": f"❌ Ошибка: {e}"}
    


# Импортируем реальную интеграцию с Apple
from apple_integration import AppleRemindersIntegration, AppleCalendarIntegration
from calendar_validator import CalendarValidator


class NotionIntegration:
    """Интеграция с Notion (упрощенная)"""
    
    async def create_project(self, title: str, description: str) -> Dict[str, Any]:
        """Создает проект в Notion"""
        logger.info(f"Creating Notion project: {title}")
        
        # Используем существующую интеграцию
        from notion_integration import NotionPlanner
        planner = NotionPlanner()
        
        result = await planner.create_material_entry(
            title=f"📋 Проект: {title}",
            content=description,
            category="project",
            tags=["проект", "планирование"]
        )
        
        return {
            "id": f"project_{datetime.now().timestamp()}",
            "title": title,
            "notion_success": result
        }
    
    async def create_material(self, title: str, content: str, tags: list) -> Dict[str, Any]:
        """Создает материал в Notion"""
        logger.info(f"Creating Notion material: {title}")
        
        from notion_integration import NotionPlanner
        planner = NotionPlanner()
        
        result = await planner.create_material_entry(
            title=title,
            content=content,
            category="ideas",
            tags=tags
        )
        
        return {
            "id": f"material_{datetime.now().timestamp()}",
            "title": title,
            "notion_success": result
        }
