import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json

from notion_integration import NotionPlanner
from ai_processor import AIProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PersonalPlanner:
    def __init__(self):
        self.notion = NotionPlanner()
        self.ai_processor = AIProcessor()
        
    async def create_smart_plan(self, text: str, user_preferences: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a smart plan with AI analysis and Notion integration"""
        try:
            # Generate task structure with AI
            task_structure = await self.ai_processor.generate_task_structure(text)
            
            # Enhance with user preferences
            if user_preferences:
                task_structure = self._apply_user_preferences(task_structure, user_preferences)
            
            # Create tasks in Notion
            created_tasks = []
            for task in task_structure.get("tasks", []):
                success = await self.notion.create_task(
                    title=task.get("title", ""),
                    description=task.get("description", ""),
                    priority=task.get("priority", "medium"),
                    category=task.get("category", "general"),
                    estimated_time=task.get("estimated_time", "1 час")
                )
                if success:
                    created_tasks.append(task)
            
            # Create daily plan if requested
            daily_plan = None
            if user_preferences and user_preferences.get("create_daily_plan", False):
                daily_plan = await self._create_daily_plan(created_tasks)
            
            return {
                "success": True,
                "main_goal": task_structure.get("main_goal", ""),
                "tasks_created": len(created_tasks),
                "tasks": created_tasks,
                "categories": task_structure.get("categories", []),
                "timeline": task_structure.get("timeline", ""),
                "daily_plan": daily_plan,
                "notion_integration": True
            }
            
        except Exception as e:
            logger.error(f"Error creating smart plan: {e}")
            return {"success": False, "error": str(e)}
    
    async def create_daily_schedule(self, date: str = None, focus_areas: List[str] = None) -> Dict[str, Any]:
        """Create a daily schedule with time blocking"""
        try:
            if not date:
                date = datetime.now().strftime("%Y-%m-%d")
            
            # Get high priority tasks
            high_priority_tasks = await self.notion.get_tasks_by_priority("high")
            medium_priority_tasks = await self.notion.get_tasks_by_priority("medium")
            
            # Create time blocks
            time_blocks = self._create_time_blocks(high_priority_tasks, medium_priority_tasks, focus_areas)
            
            # Create daily plan in Notion
            daily_plan = await self.notion.create_daily_plan(date, time_blocks)
            
            return {
                "success": True,
                "date": date,
                "time_blocks": time_blocks,
                "total_tasks": len(high_priority_tasks) + len(medium_priority_tasks),
                "notion_created": daily_plan
            }
            
        except Exception as e:
            logger.error(f"Error creating daily schedule: {e}")
            return {"success": False, "error": str(e)}
    
    async def sort_material(self, content: str, title: str = None) -> Dict[str, Any]:
        """Sort and categorize material using AI"""
        try:
            # Use AI to analyze and categorize material
            analysis_prompt = f"""
            Проанализируй следующий материал и определи:
            1. Основную тему/категорию
            2. Ключевые теги
            3. Приоритет важности (high/medium/low)
            4. Рекомендуемые действия
            
            Материал: {content}
            """
            
            # Generate analysis
            analysis = await self.ai_processor.generate_summary(analysis_prompt)
            
            # Extract category and tags
            category = self._extract_category(analysis)
            tags = self._extract_tags(analysis)
            priority = self._extract_priority(analysis)
            
            # Create material entry in Notion
            success = await self.notion.create_material_entry(
                title=title or "Новый материал",
                content=content,
                category=category,
                tags=tags
            )
            
            return {
                "success": success,
                "category": category,
                "tags": tags,
                "priority": priority,
                "analysis": analysis,
                "notion_created": success
            }
            
        except Exception as e:
            logger.error(f"Error sorting material: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_priority_tasks(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get prioritized task list"""
        try:
            # Get tasks by priority
            high_tasks = await self.notion.get_tasks_by_priority("high")
            medium_tasks = await self.notion.get_tasks_by_priority("medium")
            low_tasks = await self.notion.get_tasks_by_priority("low")
            
            # Combine and limit
            all_tasks = high_tasks + medium_tasks + low_tasks
            return all_tasks[:limit]
            
        except Exception as e:
            logger.error(f"Error getting priority tasks: {e}")
            return []
    
    async def update_task_progress(self, task_id: str, status: str) -> bool:
        """Update task progress"""
        try:
            return await self.notion.update_task_status(task_id, status)
        except Exception as e:
            logger.error(f"Error updating task progress: {e}")
            return False
    
    def _apply_user_preferences(self, task_structure: Dict[str, Any], preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Apply user preferences to task structure"""
        try:
            # Adjust priorities based on user preferences
            if preferences.get("focus_areas"):
                focus_areas = preferences["focus_areas"]
                for task in task_structure.get("tasks", []):
                    if any(area.lower() in task.get("category", "").lower() for area in focus_areas):
                        task["priority"] = "high"
            
            # Adjust time estimates based on user working style
            if preferences.get("working_style") == "fast":
                for task in task_structure.get("tasks", []):
                    # Reduce time estimates by 20%
                    current_time = task.get("estimated_time", "1 час")
                    task["estimated_time"] = self._adjust_time_estimate(current_time, 0.8)
            
            return task_structure
            
        except Exception as e:
            logger.error(f"Error applying user preferences: {e}")
            return task_structure
    
    def _create_time_blocks(self, high_tasks: List[Dict], medium_tasks: List[Dict], 
                           focus_areas: List[str] = None) -> List[Dict[str, Any]]:
        """Create time blocks for daily schedule"""
        time_blocks = []
        
        # Morning block (9:00-12:00) - High priority tasks
        morning_tasks = high_tasks[:2]  # Top 2 high priority tasks
        if morning_tasks:
            time_blocks.append({
                "time": "09:00-12:00",
                "title": "🌅 Утренний блок - Высокий приоритет",
                "tasks": morning_tasks,
                "estimated_time": "3 часа"
            })
        
        # Afternoon block (13:00-16:00) - Medium priority tasks
        afternoon_tasks = medium_tasks[:3]  # Top 3 medium priority tasks
        if afternoon_tasks:
            time_blocks.append({
                "time": "13:00-16:00", 
                "title": "☀️ Дневной блок - Средний приоритет",
                "tasks": afternoon_tasks,
                "estimated_time": "3 часа"
            })
        
        # Evening block (17:00-19:00) - Review and planning
        time_blocks.append({
            "time": "17:00-19:00",
            "title": "🌆 Вечерний блок - Обзор и планирование",
            "tasks": [{"title": "Обзор выполненных задач", "estimated_time": "30 мин"},
                     {"title": "Планирование на завтра", "estimated_time": "30 мин"}],
            "estimated_time": "1 час"
        })
        
        return time_blocks
    
    def _extract_category(self, analysis: str) -> str:
        """Extract category from AI analysis"""
        # Simple keyword-based categorization
        if any(word in analysis.lower() for word in ["работа", "проект", "задача"]):
            return "💼 Work"
        elif any(word in analysis.lower() for word in ["учеба", "курс", "изучение"]):
            return "📚 Learning"
        elif any(word in analysis.lower() for word in ["здоровье", "спорт", "фитнес"]):
            return "💪 Health"
        elif any(word in analysis.lower() for word in ["личное", "семья", "отношения"]):
            return "👨‍👩‍👧‍👦 Personal"
        else:
            return "📝 General"
    
    def _extract_tags(self, analysis: str) -> List[str]:
        """Extract tags from AI analysis"""
        # Simple tag extraction
        tags = []
        common_tags = ["важно", "срочно", "проект", "идея", "планирование", "анализ"]
        
        for tag in common_tags:
            if tag in analysis.lower():
                tags.append(tag)
        
        return tags[:5]  # Limit to 5 tags
    
    def _extract_priority(self, analysis: str) -> str:
        """Extract priority from AI analysis"""
        if any(word in analysis.lower() for word in ["важно", "срочно", "критично"]):
            return "high"
        elif any(word in analysis.lower() for word in ["средне", "обычно"]):
            return "medium"
        else:
            return "low"
    
    def _adjust_time_estimate(self, time_str: str, multiplier: float) -> str:
        """Adjust time estimate by multiplier"""
        try:
            # Simple time adjustment
            if "час" in time_str:
                return f"{int(float(time_str.split()[0]) * multiplier)} час"
            elif "мин" in time_str:
                return f"{int(float(time_str.split()[0]) * multiplier)} мин"
            else:
                return time_str
        except:
            return time_str
