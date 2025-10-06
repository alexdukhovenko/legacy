#!/usr/bin/env python3
"""
Умный агент для автоматической классификации и обработки сообщений
"""

import logging
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from ai_processor import AIProcessor
from notion_integration import NotionPlanner
from mindmap_generator import MindmapGenerator

logger = logging.getLogger(__name__)

class SmartAgent:
    def __init__(self):
        self.ai_processor = AIProcessor()
        self.notion_planner = NotionPlanner()
        self.mindmap_generator = MindmapGenerator()
        
    async def analyze_and_process(self, text: str, user_id: int) -> Dict[str, Any]:
        """
        Анализирует текст и автоматически определяет тип обработки
        """
        try:
            # Анализируем тип сообщения
            analysis = await self._analyze_message_type(text)
            
            # Обрабатываем в зависимости от типа
            result = await self._process_by_type(text, analysis, user_id)
            
            return {
                "success": True,
                "type": analysis["type"],
                "confidence": analysis["confidence"],
                "result": result,
                "message": self._generate_response_message(analysis, result)
            }
            
        except Exception as e:
            logger.error(f"Error in smart agent: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "❌ Произошла ошибка при обработке сообщения"
            }
    
    async def _analyze_message_type(self, text: str) -> Dict[str, Any]:
        """
        Анализирует тип сообщения с помощью AI
        """
        prompt = f"""
Проанализируй следующее сообщение и определи его тип:

"{text}"

Определи тип сообщения из следующих категорий:
1. "immediate_task" - срочная задача на сегодня (слова: сегодня, срочно, нужно сделать, не забыть)
2. "weekly_task" - задача на неделю (слова: на неделе, в течение недели, планирую)
3. "long_term_task" - долгосрочная задача (слова: в будущем, когда-нибудь, в перспективе)
4. "roadmap" - дорожная карта/план проекта (слова: план, стратегия, этапы, проект)
5. "thoughts" - просто мысли/идеи для структурирования (общие размышления)
6. "chain_task" - задача, которая порождает цепочку других задач
7. "expand_task" - запрос на детальное развертывание задачи (слова: разверни, детально, план, стратегия, как сделать)

Также определи:
- Уровень срочности (1-10)
- Приоритет (high/medium/low)
- Категорию (work/learning/health/personal/general)
- Нужна ли дорожная карта (true/false)
- Количество подзадач (если есть)

Ответь в формате JSON:
{{
    "type": "тип_сообщения",
    "confidence": 0.95,
    "urgency": 8,
    "priority": "high",
    "category": "work",
    "needs_roadmap": true,
    "subtasks_count": 3,
    "reasoning": "объяснение решения"
}}
"""
        
        try:
            response = await self.ai_processor.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500
            )
            
            analysis_text = response.choices[0].message.content.strip()
            
            # Парсим JSON ответ
            if analysis_text.startswith("```json"):
                analysis_text = analysis_text[7:-3]
            elif analysis_text.startswith("```"):
                analysis_text = analysis_text[3:-3]
            
            analysis = json.loads(analysis_text)
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing message type: {e}")
            # Fallback анализ
            return {
                "type": "thoughts",
                "confidence": 0.5,
                "urgency": 5,
                "priority": "medium",
                "category": "general",
                "needs_roadmap": False,
                "subtasks_count": 0,
                "reasoning": "Ошибка анализа, используется fallback"
            }
    
    async def _process_by_type(self, text: str, analysis: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """
        Обрабатывает сообщение в зависимости от его типа
        """
        message_type = analysis["type"]
        
        if message_type == "immediate_task":
            return await self._process_immediate_task(text, analysis, user_id)
        elif message_type == "weekly_task":
            return await self._process_weekly_task(text, analysis, user_id)
        elif message_type == "long_term_task":
            return await self._process_long_term_task(text, analysis, user_id)
        elif message_type == "roadmap":
            return await self._process_roadmap(text, analysis, user_id)
        elif message_type == "chain_task":
            return await self._process_chain_task(text, analysis, user_id)
        elif message_type == "expand_task":
            return await self._process_expand_task(text, analysis, user_id)
        else:  # thoughts
            return await self._process_thoughts(text, analysis, user_id)
    
    async def _process_immediate_task(self, text: str, analysis: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """
        Обрабатывает срочную задачу на сегодня
        """
        try:
            # Создаем задачу в Notion с высоким приоритетом
            task_result = await self.notion_planner.create_task(
                title=f"🔥 СРОЧНО: {text[:50]}...",
                description=text,
                priority="high",
                category=analysis["category"],
                due_date=datetime.now().strftime("%Y-%m-%d"),
                estimated_time="1 час"
            )
            
            return {
                "action": "immediate_task_created",
                "notion_success": task_result,
                "priority": "high",
                "due_date": "сегодня"
            }
            
        except Exception as e:
            logger.error(f"Error processing immediate task: {e}")
            return {"action": "error", "error": str(e)}
    
    async def _process_weekly_task(self, text: str, analysis: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """
        Обрабатывает задачу на неделю
        """
        try:
            # Создаем задачу в Notion со средним приоритетом
            due_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
            
            task_result = await self.notion_planner.create_task(
                title=f"📅 НЕДЕЛЯ: {text[:50]}...",
                description=text,
                priority=analysis["priority"],
                category=analysis["category"],
                due_date=due_date,
                estimated_time="2-3 часа"
            )
            
            return {
                "action": "weekly_task_created",
                "notion_success": task_result,
                "priority": analysis["priority"],
                "due_date": "на неделе"
            }
            
        except Exception as e:
            logger.error(f"Error processing weekly task: {e}")
            return {"action": "error", "error": str(e)}
    
    async def _process_long_term_task(self, text: str, analysis: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """
        Обрабатывает долгосрочную задачу
        """
        try:
            # Создаем задачу в Notion с низким приоритетом
            task_result = await self.notion_planner.create_task(
                title=f"📚 ДОЛГОСРОЧНО: {text[:50]}...",
                description=text,
                priority="low",
                category=analysis["category"],
                estimated_time="неопределенно"
            )
            
            return {
                "action": "long_term_task_created",
                "notion_success": task_result,
                "priority": "low",
                "due_date": "без срока"
            }
            
        except Exception as e:
            logger.error(f"Error processing long term task: {e}")
            return {"action": "error", "error": str(e)}
    
    async def _process_roadmap(self, text: str, analysis: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """
        Обрабатывает дорожную карту
        """
        try:
            # Генерируем структурированный план
            task_structure = await self.ai_processor.generate_task_structure(text)
            
            # Создаем дорожную карту в файле
            roadmap_file = await self._create_roadmap_file(text, task_structure, user_id)
            
            # Создаем основные задачи в Notion
            tasks_created = 0
            for task in task_structure.get("tasks", [])[:5]:  # Первые 5 задач
                await self.notion_planner.create_task(
                    title=task.get("title", ""),
                    description=task.get("description", ""),
                    priority=task.get("priority", "medium"),
                    category=analysis["category"],
                    estimated_time=task.get("estimated_time", "1 час")
                )
                tasks_created += 1
            
            return {
                "action": "roadmap_created",
                "file_path": roadmap_file,
                "tasks_created": tasks_created,
                "total_tasks": len(task_structure.get("tasks", []))
            }
            
        except Exception as e:
            logger.error(f"Error processing roadmap: {e}")
            return {"action": "error", "error": str(e)}
    
    async def _process_chain_task(self, text: str, analysis: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """
        Обрабатывает задачу, которая порождает цепочку
        """
        try:
            # Генерируем цепочку задач
            chain_prompt = f"""
Создай цепочку задач для: "{text}"

Определи основные этапы и подзадачи. Ответь в формате JSON:
{{
    "main_task": "главная задача",
    "chain": [
        {{"step": 1, "task": "первая задача", "priority": "high", "estimated_time": "1 час"}},
        {{"step": 2, "task": "вторая задача", "priority": "medium", "estimated_time": "2 часа"}},
        {{"step": 3, "task": "третья задача", "priority": "medium", "estimated_time": "1 час"}}
    ]
}}
"""
            
            response = await self.ai_processor.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": chain_prompt}],
                temperature=0.3,
                max_tokens=800
            )
            
            chain_text = response.choices[0].message.content.strip()
            if chain_text.startswith("```json"):
                chain_text = chain_text[7:-3]
            elif chain_text.startswith("```"):
                chain_text = chain_text[3:-3]
            
            chain_data = json.loads(chain_text)
            
            # Создаем задачи в Notion
            tasks_created = 0
            for task in chain_data.get("chain", []):
                await self.notion_planner.create_task(
                    title=f"🔗 Шаг {task['step']}: {task['task']}",
                    description=f"Часть цепочки: {chain_data.get('main_task', '')}",
                    priority=task.get("priority", "medium"),
                    category=analysis["category"],
                    estimated_time=task.get("estimated_time", "1 час")
                )
                tasks_created += 1
            
            return {
                "action": "chain_tasks_created",
                "main_task": chain_data.get("main_task", ""),
                "tasks_created": tasks_created,
                "chain_length": len(chain_data.get("chain", []))
            }
            
        except Exception as e:
            logger.error(f"Error processing chain task: {e}")
            return {"action": "error", "error": str(e)}
    
    async def _process_expand_task(self, text: str, analysis: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """
        Обрабатывает расширение задачи в детальный план
        """
        try:
            # Создаем детальный план
            detailed_plan = await self._create_detailed_plan(text, analysis)
            
            if not detailed_plan:
                return {"action": "error", "error": "Не удалось создать детальный план"}
            
            # Создаем основной план в Notion как материал
            plan_result = await self.notion_planner.create_material_entry(
                title=f"📋 Детальный план: {text[:50]}...",
                content=self._format_detailed_plan(detailed_plan),
                category=analysis["category"],
                tags=["детальный_план", "стратегия", "развернутая_задача"]
            )
            
            # Создаем подзадачи в Notion
            tasks_created = 0
            for phase in detailed_plan.get("phases", []):
                for subtask in phase.get("subtasks", []):
                    task_result = await self.notion_planner.create_task(
                        title=f"{phase['name']}: {subtask['title']}",
                        description=subtask['description'],
                        priority=subtask.get('priority', 'medium'),
                        category=analysis["category"],
                        estimated_time=subtask.get('estimated_time', '1 час')
                    )
                    if task_result:
                        tasks_created += 1
            
            return {
                "action": "detailed_plan_created",
                "plan_created": plan_result,
                "tasks_created": tasks_created,
                "phases_count": len(detailed_plan.get("phases", [])),
                "plan_data": detailed_plan
            }
            
        except Exception as e:
            logger.error(f"Error processing expand task: {e}")
            return {"action": "error", "error": str(e)}

    async def _process_thoughts(self, text: str, analysis: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """
        Обрабатывает обычные мысли/идеи
        """
        try:
            # Генерируем структурированный ответ
            task_structure = await self.ai_processor.generate_task_structure(text)
            
            # Создаем материал в Notion
            material_result = await self.notion_planner.create_material_entry(
                title=f"💭 Мысли: {text[:50]}...",
                content=text,
                category=analysis["category"],
                tags=["мысли", "идеи"]
            )
            
            return {
                "action": "thoughts_structured",
                "material_created": material_result,
                "tasks_found": len(task_structure.get("tasks", [])),
                "structure": task_structure
            }
            
        except Exception as e:
            logger.error(f"Error processing thoughts: {e}")
            return {"action": "error", "error": str(e)}
    
    async def _create_roadmap_file(self, text: str, task_structure: Dict[str, Any], user_id: int) -> str:
        """
        Создает файл дорожной карты
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"roadmap_{user_id}_{timestamp}.md"
            filepath = os.path.join("outputs", filename)
            
            # Создаем содержимое файла
            content = f"""# Дорожная карта
*Создано: {datetime.now().strftime("%Y-%m-%d %H:%M")}*

## Исходный текст
{text}

## Основная цель
{task_structure.get('main_goal', 'Не указана')}

## Задачи
"""
            
            for i, task in enumerate(task_structure.get("tasks", []), 1):
                priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(task.get("priority", "medium"), "🟡")
                content += f"""
### {i}. {priority_emoji} {task.get('title', f'Задача {i}')}
- **Описание:** {task.get('description', '')}
- **Время:** {task.get('estimated_time', 'Не указано')}
- **Категория:** {task.get('category', 'Общее')}
"""
            
            if task_structure.get("timeline"):
                content += f"\n## Временные рамки\n{task_structure['timeline']}\n"
            
            # Сохраняем файл
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return filepath
            
        except Exception as e:
            logger.error(f"Error creating roadmap file: {e}")
            return ""
    
    async def _create_detailed_plan(self, text: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Создает детальный план из задачи
        """
        try:
            expansion_prompt = f"""
            Разверни следующую задачу в детальный план с стратегией, этапами и временными рамками.

            Задача: "{text}"

            Создай структурированный план, который включает:
            1. Цель и ожидаемый результат
            2. Стратегию достижения
            3. Детальные этапы с подзадачами
            4. Временные рамки для каждого этапа
            5. Необходимые ресурсы
            6. Потенциальные риски и способы их минимизации
            7. Критерии успеха

            Формат ответа JSON:
            {{
                "goal": "четкая_цель_и_ожидаемый_результат",
                "strategy": "общая_стратегия_достижения_цели",
                "phases": [
                    {{
                        "name": "название_этапа",
                        "description": "описание_этапа",
                        "duration": "временные_рамки",
                        "subtasks": [
                            {{
                                "title": "название_подзадачи",
                                "description": "описание_подзадачи",
                                "estimated_time": "оценка_времени",
                                "priority": "high/medium/low"
                            }}
                        ]
                    }}
                ],
                "resources": ["список_необходимых_ресурсов"],
                "risks": [
                    {{
                        "risk": "описание_риска",
                        "mitigation": "способ_минимизации"
                    }}
                ],
                "success_criteria": ["критерии_успешного_завершения"]
            }}
            """
            
            response = await self.ai_processor.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": expansion_prompt}],
                temperature=0.3,
                max_tokens=1500
            )
            
            expansion_text = response.choices[0].message.content.strip()
            
            # Парсим JSON ответ
            if expansion_text.startswith("```json"):
                expansion_text = expansion_text[7:-3]
            elif expansion_text.startswith("```"):
                expansion_text = expansion_text[3:-3]
            
            expansion_data = json.loads(expansion_text)
            return expansion_data
            
        except Exception as e:
            logger.error(f"Error creating detailed plan: {e}")
            return None
    
    def _format_detailed_plan(self, plan_data: Dict[str, Any]) -> str:
        """
        Форматирует детальный план для отображения
        """
        if not plan_data:
            return "План не создан"
        
        content = f"""**Цель:** {plan_data.get('goal', 'Не указана')}

**Стратегия:** {plan_data.get('strategy', 'Не указана')}

**Этапы:**
{self._format_phases(plan_data.get('phases', []))}

**Ресурсы:** {', '.join(plan_data.get('resources', []))}

**Риски и способы минимизации:**
{self._format_risks(plan_data.get('risks', []))}

**Критерии успеха:**
{self._format_success_criteria(plan_data.get('success_criteria', []))}
"""
        return content
    
    def _format_phases(self, phases: list) -> str:
        """Format phases for display"""
        if not phases:
            return "Этапы не определены"
        
        formatted = ""
        for i, phase in enumerate(phases, 1):
            formatted += f"\n**{i}. {phase.get('name', 'Без названия')}** ({phase.get('duration', 'Без временных рамок')})\n"
            formatted += f"{phase.get('description', 'Без описания')}\n"
            
            subtasks = phase.get('subtasks', [])
            if subtasks:
                formatted += "Подзадачи:\n"
                for j, subtask in enumerate(subtasks, 1):
                    formatted += f"  {j}. {subtask.get('title', 'Без названия')} ({subtask.get('estimated_time', 'Без оценки времени')})\n"
        
        return formatted

    def _format_risks(self, risks: list) -> str:
        """Format risks for display"""
        if not risks:
            return "Риски не определены"
        
        formatted = ""
        for i, risk in enumerate(risks, 1):
            formatted += f"{i}. **{risk.get('risk', 'Не указан')}**\n"
            formatted += f"   Способ минимизации: {risk.get('mitigation', 'Не указан')}\n"
        
        return formatted

    def _format_success_criteria(self, criteria: list) -> str:
        """Format success criteria for display"""
        if not criteria:
            return "Критерии успеха не определены"
        
        formatted = ""
        for i, criterion in enumerate(criteria, 1):
            formatted += f"{i}. {criterion}\n"
        
        return formatted
    
    def _generate_response_message(self, analysis: Dict[str, Any], result: Dict[str, Any]) -> str:
        """
        Генерирует ответное сообщение пользователю
        """
        message_type = analysis["type"]
        action = result.get("action", "")
        
        if message_type == "immediate_task":
            return f"🔥 **СРОЧНАЯ ЗАДАЧА СОЗДАНА!**\n\nЗадача добавлена в Notion с высоким приоритетом на сегодня. Не забудь выполнить!"
        
        elif message_type == "weekly_task":
            return f"📅 **ЗАДАЧА НА НЕДЕЛЮ СОЗДАНА!**\n\nЗадача добавлена в Notion со сроком выполнения на неделю."
        
        elif message_type == "long_term_task":
            return f"📚 **ДОЛГОСРОЧНАЯ ЗАДАЧА СОЗДАНА!**\n\nЗадача добавлена в Notion без срока выполнения. Можешь вернуться к ней позже."
        
        elif message_type == "roadmap":
            tasks_created = result.get("tasks_created", 0)
            total_tasks = result.get("total_tasks", 0)
            return f"🗺️ **ДОРОЖНАЯ КАРТА СОЗДАНА!**\n\nСоздано {tasks_created} из {total_tasks} задач в Notion. Дорожная карта сохранена в файл."
        
        elif message_type == "chain_task":
            tasks_created = result.get("tasks_created", 0)
            chain_length = result.get("chain_length", 0)
            main_task = result.get("main_task", "")
            return f"🔗 **ЦЕПОЧКА ЗАДАЧ СОЗДАНА!**\n\nГлавная задача: {main_task}\nСоздано {tasks_created} задач в цепочке. Все задачи добавлены в Notion."
        
        elif message_type == "expand_task":
            tasks_created = result.get("tasks_created", 0)
            phases_count = result.get("phases_count", 0)
            return f"📋 **ДЕТАЛЬНЫЙ ПЛАН СОЗДАН!**\n\nЗадача развернута в {phases_count} этапов с {tasks_created} подзадачами. План сохранен в Notion как материал, все подзадачи добавлены в задачи."
        
        else:  # thoughts
            tasks_found = result.get("tasks_found", 0)
            if tasks_found > 0:
                return f"💭 **МЫСЛИ СТРУКТУРИРОВАНЫ!**\n\nНайдено {tasks_found} задач в твоих мыслях. Материал сохранен в Notion."
            else:
                return f"💭 **МЫСЛИ ЗАПИСАНЫ!**\n\nТвои мысли сохранены в Notion как материал для дальнейшего анализа."
