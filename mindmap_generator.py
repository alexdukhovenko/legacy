import json
import logging
from typing import Dict, Any
import os

from config import OUTPUT_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MindmapGenerator:
    def __init__(self):
        self.colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F']
        
    def generate_mindmap_image(self, mindmap_data: Dict[str, Any]) -> str:
        """Generate mindmap as text file (simplified version)"""
        try:
            # Create text-based mindmap
            filename = f"{OUTPUT_DIR}/mindmap_{hash(str(mindmap_data)) % 10000}.txt"
            text_mindmap = self.generate_mindmap_text(mindmap_data)
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(text_mindmap)
            
            logger.info(f"Mindmap saved: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error generating mindmap: {e}")
            return None
    
    
    def generate_mindmap_text(self, mindmap_data: Dict[str, Any]) -> str:
        """Generate text representation of mindmap"""
        try:
            text = f"🧠 МАЙНДМЭП\n\n"
            text += f"🎯 Центральная тема: {mindmap_data.get('central_topic', 'Не указана')}\n\n"
            
            main_branches = mindmap_data.get('main_branches', [])
            for i, branch in enumerate(main_branches, 1):
                text += f"📌 {i}. {branch.get('name', f'Ветка {i}')}\n"
                
                sub_branches = branch.get('sub_branches', [])
                for j, sub_branch in enumerate(sub_branches, 1):
                    text += f"   └─ {j}. {sub_branch.get('name', f'Подветка {j}')}\n"
                    details = sub_branch.get('details', '')
                    if details:
                        text += f"      💡 {details}\n"
                text += "\n"
            
            return text
            
        except Exception as e:
            logger.error(f"Error generating mindmap text: {e}")
            return "Ошибка при создании текстового майндмэпа"
