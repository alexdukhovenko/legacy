"""
Пакет для работы с базой данных LEGACY M
"""

from .database import get_db, create_tables, init_database
from .models import (
    QuranVerse, 
    Hadith, 
    Commentary, 
    VectorEmbedding, 
    User,
    UserSession, 
    ChatMessage, 
    SystemConfig,
    OrthodoxText,
    OrthodoxDocument
)

__all__ = [
    "get_db",
    "create_tables", 
    "init_database",
    "QuranVerse",
    "Hadith", 
    "Commentary",
    "VectorEmbedding",
    "User",
    "UserSession",
    "ChatMessage",
    "SystemConfig",
    "OrthodoxText",
    "OrthodoxDocument"
]
