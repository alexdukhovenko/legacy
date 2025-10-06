import logging
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json

from config import NOTION_API_KEY, NOTION_DATABASE_ID

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotionPlanner:
    def __init__(self):
        self.api_key = NOTION_API_KEY
        self.database_id = NOTION_DATABASE_ID
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        
    async def create_task(self, title: str, description: str = "", priority: str = "medium", 
                         category: str = "general", due_date: str = None, 
                         estimated_time: str = "1 час") -> bool:
        """Create a new task in Notion database"""
        try:
            # Prepare task data
            task_data = {
                "parent": {"database_id": self.database_id},
                "properties": {
                    "Name": {
                        "title": [{"text": {"content": title}}]
                    },
                    "Description": {
                        "rich_text": [{"text": {"content": description}}]
                    },
                    "Priority": {
                        "select": {"name": self._get_priority_emoji(priority)}
                    },
                    "Category": {
                        "select": {"name": category}
                    },
                    "Status": {
                        "select": {"name": "Not started"}
                    },
                    "Estimated Time": {
                        "rich_text": [{"text": {"content": estimated_time}}]
                    }
                }
            }
            
            # Add due date if provided
            if due_date:
                task_data["properties"]["Due Date"] = {
                    "date": {"start": due_date}
                }
            
            # Create task
            response = requests.post(
                "https://api.notion.com/v1/pages",
                headers=self.headers,
                json=task_data
            )
            
            if response.status_code == 200:
                logger.info(f"Task created: {title}")
                return True
            else:
                logger.error(f"Failed to create task: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            return False
    
    async def create_daily_plan(self, date: str, tasks: List[Dict[str, Any]]) -> bool:
        """Create a daily plan with scheduled tasks"""
        try:
            # Create daily plan page
            plan_data = {
                "parent": {"database_id": self.database_id},
                "properties": {
                    "Name": {
                        "title": [{"text": {"content": f"📅 План на {date}"}}]
                    },
                    "Description": {
                        "rich_text": [{"text": {"content": f"Ежедневный план на {date}"}}]
                    },
                    "Category": {
                        "select": {"name": "📅 Daily Plan"}
                    },
                    "Status": {
                        "select": {"name": "Not started"}
                    },
                    "Priority": {
                        "select": {"name": "🔴 High"}
                    },
                    "Due Date": {
                        "date": {"start": date}
                    }
                },
                "children": []
            }
            
            # Add tasks as children
            for task in tasks:
                task_block = {
                    "object": "block",
                    "type": "to_do",
                    "to_do": {
                        "rich_text": [{"text": {"content": f"{task.get('title', '')} - {task.get('estimated_time', '')}"}}],
                        "checked": False
                    }
                }
                plan_data["children"].append(task_block)
            
            # Create plan
            response = requests.post(
                "https://api.notion.com/v1/pages",
                headers=self.headers,
                json=plan_data
            )
            
            if response.status_code == 200:
                logger.info(f"Daily plan created for {date}")
                return True
            else:
                logger.error(f"Failed to create daily plan: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating daily plan: {e}")
            return False
    
    async def get_tasks_by_priority(self, priority: str = None) -> List[Dict[str, Any]]:
        """Get tasks filtered by priority"""
        try:
            # Build filter
            filter_data = {
                "filter": {
                    "property": "Status",
                    "select": {"equals": "📋 To Do"}
                }
            }
            
            if priority:
                filter_data["filter"] = {
                    "and": [
                        {"property": "Status", "select": {"equals": "📋 To Do"}},
                        {"property": "Priority", "select": {"equals": self._get_priority_emoji(priority)}}
                    ]
                }
            
            # Query database
            response = requests.post(
                f"https://api.notion.com/v1/databases/{self.database_id}/query",
                headers=self.headers,
                json=filter_data
            )
            
            if response.status_code == 200:
                data = response.json()
                tasks = []
                for page in data.get("results", []):
                    task = self._parse_notion_page(page)
                    tasks.append(task)
                return tasks
            else:
                logger.error(f"Failed to get tasks: {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting tasks: {e}")
            return []
    
    async def update_task_status(self, task_id: str, status: str) -> bool:
        """Update task status"""
        try:
            update_data = {
                "properties": {
                    "Status": {
                        "select": {"name": status}
                    }
                }
            }
            
            response = requests.patch(
                f"https://api.notion.com/v1/pages/{task_id}",
                headers=self.headers,
                json=update_data
            )
            
            if response.status_code == 200:
                logger.info(f"Task {task_id} status updated to {status}")
                return True
            else:
                logger.error(f"Failed to update task: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating task: {e}")
            return False
    
    async def create_material_entry(self, title: str, content: str, category: str, 
                                  tags: List[str] = None) -> bool:
        """Create a material entry for sorting and organization"""
        try:
            material_data = {
                "parent": {"database_id": self.database_id},
                "properties": {
                    "Name": {
                        "title": [{"text": {"content": title}}]
                    },
                    "Description": {
                        "rich_text": [{"text": {"content": content}}]
                    },
                    "Category": {
                        "select": {"name": category}
                    },
                    "Type": {
                        "select": {"name": "📚 Material"}
                    },
                    "Status": {
                        "select": {"name": "📋 To Review"}
                    },
                    "Priority": {
                        "select": {"name": "🟡 Medium"}
                    }
                }
            }
            
            # Add tags if provided
            if tags:
                material_data["properties"]["Tags"] = {
                    "multi_select": [{"name": tag} for tag in tags]
                }
            
            response = requests.post(
                "https://api.notion.com/v1/pages",
                headers=self.headers,
                json=material_data
            )
            
            if response.status_code == 200:
                logger.info(f"Material created: {title}")
                return True
            else:
                logger.error(f"Failed to create material: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating material: {e}")
            return False
    
    def _get_priority_emoji(self, priority: str) -> str:
        """Convert priority to emoji"""
        priority_map = {
            "high": "🔴 High",
            "medium": "🟡 Medium", 
            "low": "🟢 Low"
        }
        return priority_map.get(priority.lower(), "🟡 Medium")
    
    def _parse_notion_page(self, page: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Notion page data"""
        properties = page.get("properties", {})
        
        task = {
            "id": page.get("id"),
            "title": self._get_property_text(properties.get("Name", {})),
            "description": self._get_property_text(properties.get("Description", {})),
            "priority": self._get_property_select(properties.get("Priority", {})),
            "category": self._get_property_select(properties.get("Category", {})),
            "status": self._get_property_select(properties.get("Status", {})),
            "due_date": self._get_property_date(properties.get("Due Date", {})),
            "estimated_time": self._get_property_text(properties.get("Estimated Time", {}))
        }
        
        return task
    
    def _get_property_text(self, property_data: Dict[str, Any]) -> str:
        """Extract text from Notion property"""
        if "title" in property_data:
            return "".join([text.get("text", {}).get("content", "") for text in property_data["title"]])
        elif "rich_text" in property_data:
            return "".join([text.get("text", {}).get("content", "") for text in property_data["rich_text"]])
        return ""
    
    def _get_property_select(self, property_data: Dict[str, Any]) -> str:
        """Extract select value from Notion property"""
        if "select" in property_data and property_data["select"]:
            return property_data["select"].get("name", "")
        return ""
    
    def _get_property_date(self, property_data: Dict[str, Any]) -> str:
        """Extract date from Notion property"""
        if "date" in property_data and property_data["date"]:
            return property_data["date"].get("start", "")
        return ""
