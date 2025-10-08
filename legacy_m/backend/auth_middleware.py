"""
Middleware для проверки аутентификации пользователей
"""

import logging
from typing import Optional
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from database.database import SessionLocal
from database.models import User
from backend.auth_system import auth_system

logger = logging.getLogger(__name__)

# Схема безопасности для JWT токенов
security = HTTPBearer()


def get_db():
    """Получение сессии базы данных"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Получение текущего аутентифицированного пользователя"""
    try:
        token = credentials.credentials
        user = auth_system.get_current_user(token)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Недействительный токен аутентификации",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user
        
    except Exception as e:
        logger.error(f"❌ Ошибка аутентификации: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ошибка аутентификации",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[User]:
    """Получение текущего пользователя (опционально)"""
    try:
        if not credentials:
            return None
        
        token = credentials.credentials
        user = auth_system.get_current_user(token)
        return user
        
    except Exception as e:
        logger.warning(f"⚠️ Ошибка опциональной аутентификации: {e}")
        return None


def require_auth():
    """Декоратор для обязательной аутентификации"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Проверка будет выполнена через Depends(get_current_user)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def log_user_action(user_id: int, action: str, details: str, ip_address: str = None, user_agent: str = None):
    """Логирование действия пользователя"""
    try:
        auth_system._log_user_action(user_id, action, details, ip_address, user_agent)
    except Exception as e:
        logger.error(f"❌ Ошибка логирования действия: {e}")


def get_client_ip(request) -> str:
    """Получение IP адреса клиента"""
    try:
        # Проверяем заголовки прокси
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Если нет заголовков прокси, используем прямой IP
        if hasattr(request, 'client') and request.client:
            return request.client.host
        
        return "unknown"
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения IP: {e}")
        return "unknown"


def get_user_agent(request) -> str:
    """Получение User-Agent клиента"""
    try:
        return request.headers.get("User-Agent", "unknown")
    except Exception as e:
        logger.error(f"❌ Ошибка получения User-Agent: {e}")
        return "unknown"
