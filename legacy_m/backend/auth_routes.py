"""
API эндпоинты для аутентификации пользователей
"""

import logging
from typing import Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, Request, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from database.database import get_db
from database.models import User
from backend.auth_system import auth_system
from backend.auth_middleware import get_current_user, get_client_ip, get_user_agent, log_user_action

logger = logging.getLogger(__name__)

# Роутер для аутентификации
auth_router = APIRouter(prefix="/api/auth", tags=["authentication"])


# Pydantic модели для запросов
class RegisterRequest(BaseModel):
    username: str
    password: str
    email: str = None
    phone: str = None
    name: str = None
    
    class Config:
        # Разрешаем None значения
        from_attributes = True


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]


class UserResponse(BaseModel):
    id: int
    username: str
    name: str = None
    email: str = None
    phone: str = None
    confession: str = None
    is_verified: bool
    created_at: str
    last_activity: str
    
    class Config:
        # Разрешаем None значения для всех полей
        from_attributes = True


@auth_router.post("/register", response_model=Dict[str, Any])
async def register_user(
    request: RegisterRequest,
    http_request: Request,
    db: Session = Depends(get_db)
):
    """Регистрация нового пользователя"""
    try:
        # Валидация данных
        if len(request.username) < 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Логин должен содержать минимум 3 символа"
            )
        
        if len(request.password) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пароль должен содержать минимум 6 символов"
            )
        
        # Получаем IP и User-Agent для логирования
        ip_address = get_client_ip(http_request)
        user_agent = get_user_agent(http_request)
        
        # Регистрируем пользователя
        result = auth_system.register_user(
            username=request.username,
            password=request.password,
            email=request.email,
            phone=request.phone,
            name=request.name
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        logger.info(f"✅ Новый пользователь зарегистрирован: {request.username}")
        
        return {
            "success": True,
            "message": "Пользователь успешно зарегистрирован",
            "user_id": result["user_id"],
            "username": result["username"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Ошибка регистрации: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@auth_router.post("/login", response_model=TokenResponse)
async def login_user(
    request: LoginRequest,
    http_request: Request,
    db: Session = Depends(get_db)
):
    """Вход пользователя в систему"""
    try:
        # Получаем IP и User-Agent для логирования
        ip_address = get_client_ip(http_request)
        user_agent = get_user_agent(http_request)
        
        # Выполняем вход
        result = auth_system.login_user(
            username=request.username,
            password=request.password,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=result["error"]
            )
        
        logger.info(f"✅ Пользователь вошел в систему: {request.username}")
        
        return TokenResponse(
            access_token=result["access_token"],
            refresh_token=result["refresh_token"],
            token_type="bearer",
            user=result["user"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Ошибка входа: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@auth_router.post("/logout")
async def logout_user(
    current_user: User = Depends(get_current_user),
    http_request: Request = None
):
    """Выход пользователя из системы"""
    try:
        # Получаем токен из заголовков
        authorization = http_request.headers.get("Authorization")
        if authorization and authorization.startswith("Bearer "):
            token = authorization.split(" ")[1]
            success = auth_system.logout_user(token)
            
            if success:
                logger.info(f"✅ Пользователь вышел из системы: {current_user.username}")
                return {"success": True, "message": "Успешный выход из системы"}
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ошибка при выходе из системы"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Токен не найден"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Ошибка выхода: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@auth_router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Получение информации о текущем пользователе"""
    try:
        return UserResponse(
            id=current_user.id,
            username=current_user.username,
            name=current_user.name or "",
            email=current_user.email or "",
            phone=current_user.phone or "",
            confession=current_user.confession or "",
            is_verified=bool(current_user.is_verified),
            created_at=current_user.created_at.isoformat(),
            last_activity=current_user.last_activity.isoformat()
        )
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения информации о пользователе: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@auth_router.post("/refresh")
async def refresh_token(
    refresh_token: str,
    current_user: User = Depends(get_current_user)
):
    """Обновление access токена"""
    try:
        # Проверяем refresh токен
        payload = auth_system.verify_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Недействительный refresh токен"
            )
        
        # Создаем новый access токен
        new_access_token = auth_system.create_access_token(current_user.id, current_user.username)
        
        # Сохраняем новый токен
        auth_system._save_token(
            current_user.id, 
            new_access_token, 
            "access", 
            timedelta(minutes=30)
        )
        
        logger.info(f"✅ Токен обновлен для пользователя: {current_user.username}")
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Ошибка обновления токена: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@auth_router.put("/profile")
async def update_user_profile(
    name: str = None,
    confession: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Обновление профиля пользователя"""
    try:
        # Валидация конфессии
        if confession and confession not in ['sunni', 'shia', 'orthodox']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неверная конфессия. Доступные: sunni, shia, orthodox"
            )
        
        # Обновляем данные
        if name is not None:
            current_user.name = name
        if confession is not None:
            current_user.confession = confession
        
        current_user.last_activity = datetime.utcnow()
        
        db.commit()
        db.refresh(current_user)
        
        # Логируем обновление профиля
        log_user_action(
            current_user.id, 
            "profile_update", 
            f"Обновлен профиль: name={name}, confession={confession}"
        )
        
        logger.info(f"✅ Профиль обновлен для пользователя: {current_user.username}")
        
        return {
            "success": True,
            "message": "Профиль успешно обновлен",
            "user": {
                "id": current_user.id,
                "username": current_user.username,
                "name": current_user.name,
                "confession": current_user.confession
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Ошибка обновления профиля: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )
