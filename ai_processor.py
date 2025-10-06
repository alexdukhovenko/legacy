import json
import logging
from typing import Dict, List, Any, Optional
import openai
from openai import AsyncOpenAI

from config import OPENAI_API_KEY, OPENAI_MODEL, MAX_TOKENS, TEMPERATURE

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIProcessor:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        
    async def generate_task_structure(self, text: str) -> Dict[str, Any]:
        """Generate structured tasks from text using OpenAI"""
        try:
            prompt = f"""
            Проанализируй следующий текст и создай структурированный план задач в формате JSON.
            Текст: "{text}"
            
            Верни JSON с такой структурой:
            {{
                "main_goal": "основная цель из текста",
                "tasks": [
                    {{
                        "id": 1,
                        "title": "название задачи",
                        "description": "подробное описание",
                        "priority": "high/medium/low",
                        "estimated_time": "оценка времени",
                        "dependencies": [список id зависимых задач],
                        "category": "категория задачи"
                    }}
                ],
                "categories": ["список всех категорий"],
                "timeline": "общая временная оценка проекта"
            }}
            
            Создай детальный план с конкретными, выполнимыми задачами.
            """
            
            response = await self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "Ты эксперт по планированию и структурированию задач. Создавай детальные, практичные планы."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE
            )
            
            result = response.choices[0].message.content
            logger.info("Task structure generated successfully")
            
            # Parse JSON response
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                # If JSON parsing fails, return structured fallback
                return {
                    "main_goal": "Цель извлечена из текста",
                    "tasks": [{"id": 1, "title": "Анализ текста", "description": text[:200], "priority": "medium", "estimated_time": "1 час", "dependencies": [], "category": "Анализ"}],
                    "categories": ["Анализ"],
                    "timeline": "1 день"
                }
                
        except Exception as e:
            logger.error(f"Error generating task structure: {e}")
            return self._create_fallback_structure(text)
    
    async def generate_mindmap_data(self, text: str) -> Dict[str, Any]:
        """Generate mindmap structure from text"""
        try:
            prompt = f"""
            Создай структуру майндмэпа на основе следующего текста в формате JSON:
            Текст: "{text}"
            
            Верни JSON с такой структурой:
            {{
                "central_topic": "центральная тема",
                "main_branches": [
                    {{
                        "id": 1,
                        "name": "название ветки",
                        "color": "#hex_color",
                        "sub_branches": [
                            {{
                                "id": 11,
                                "name": "подветка",
                                "details": "детали"
                            }}
                        ]
                    }}
                ],
                "connections": [
                    {{
                        "from": 1,
                        "to": 2,
                        "type": "type_of_connection"
                    }}
                ]
            }}
            
            Создай визуально привлекательную и логичную структуру майндмэпа.
            """
            
            response = await self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "Ты эксперт по созданию майндмэпов и визуализации информации. Создавай логичные и красивые структуры."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE
            )
            
            result = response.choices[0].message.content
            logger.info("Mindmap data generated successfully")
            
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                return self._create_fallback_mindmap(text)
                
        except Exception as e:
            logger.error(f"Error generating mindmap: {e}")
            return self._create_fallback_mindmap(text)
    
    async def generate_summary(self, text: str) -> str:
        """Generate a concise summary of the text"""
        try:
            prompt = f"""
            Создай краткое резюме следующего текста на русском языке:
            {text}
            
            Резюме должно быть:
            - Кратким (2-3 предложения)
            - Содержать ключевые моменты
            - Быть понятным и структурированным
            """
            
            response = await self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "Ты эксперт по созданию кратких и точных резюме."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return f"Краткое резюме: {text[:200]}..."
    
    def _create_fallback_structure(self, text: str) -> Dict[str, Any]:
        """Create fallback task structure if AI fails"""
        return {
            "main_goal": "Обработка текста",
            "tasks": [
                {
                    "id": 1,
                    "title": "Анализ текста",
                    "description": text[:200] + "..." if len(text) > 200 else text,
                    "priority": "medium",
                    "estimated_time": "30 минут",
                    "dependencies": [],
                    "category": "Анализ"
                }
            ],
            "categories": ["Анализ"],
            "timeline": "1 час"
        }
    
    def _create_fallback_mindmap(self, text: str) -> Dict[str, Any]:
        """Create fallback mindmap if AI fails"""
        return {
            "central_topic": "Основная тема",
            "main_branches": [
                {
                    "id": 1,
                    "name": "Ключевые идеи",
                    "color": "#FF6B6B",
                    "sub_branches": [
                        {
                            "id": 11,
                            "name": "Идея 1",
                            "details": text[:100] + "..." if len(text) > 100 else text
                        }
                    ]
                }
            ],
            "connections": []
        }
