"""
Система аутентификации для LEGACY M
Включает регистрацию, вход, JWT токены и хеширование паролей
"""

import os
import hashlib
import secrets
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import bcrypt
import jwt
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database.models import User, UserToken, UserLog, UserSession
from database.database import SessionLocal

logger = logging.getLogger(__name__)

# Конфигурация JWT
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "legacy-m-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


class AuthSystem:
    """Система аутентификации пользователей"""
    
    def __init__(self):
        self.db = SessionLocal()
    
    def hash_password(self, password: str) -> str:
        """Хеширование пароля с помощью bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Проверка пароля"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def create_access_token(self, user_id: int, username: str) -> str:
        """Создание JWT токена доступа"""
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {
            "user_id": user_id,
            "username": username,
            "exp": expire,
            "type": "access"
        }
        return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    def create_refresh_token(self, user_id: int, username: str) -> str:
        """Создание JWT refresh токена"""
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        payload = {
            "user_id": user_id,
            "username": username,
            "exp": expire,
            "type": "refresh"
        }
        return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Проверка JWT токена"""
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("JWT токен истек")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Недействительный JWT токен")
            return None
    
    def register_user(self, username: str, password: str, email: str = None, name: str = None, phone: str = None) -> Dict[str, Any]:
        """Регистрация нового пользователя"""
        try:
            # Проверяем, существует ли пользователь
            existing_user = self.db.query(User).filter(User.username == username).first()
            if existing_user:
                return {
                    "success": False,
                    "error": "Пользователь с таким логином уже существует"
                }
            
            if email:
                existing_email = self.db.query(User).filter(User.email == email).first()
                if existing_email:
                    return {
                        "success": False,
                        "error": "Пользователь с таким email уже существует"
                    }
            
            # Хешируем пароль
            password_hash = self.hash_password(password)
            
            # Создаем пользователя
            user = User(
                username=username,
                email=email,
                phone=phone,
                password_hash=password_hash,
                name=name,
                is_verified=0,
                is_active=1
            )
            
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            
            # Логируем регистрацию
            self._log_user_action(user.id, "register", f"Пользователь {username} зарегистрирован")
            
            logger.info(f"✅ Пользователь {username} успешно зарегистрирован")
            
            return {
                "success": True,
                "user_id": user.id,
                "username": user.username,
                "message": "Пользователь успешно зарегистрирован"
            }
            
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"❌ Ошибка регистрации: {e}")
            return {
                "success": False,
                "error": "Ошибка при создании пользователя"
            }
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Неожиданная ошибка регистрации: {e}")
            return {
                "success": False,
                "error": "Внутренняя ошибка сервера"
            }
    
    def login_user(self, username: str, password: str, ip_address: str = None, user_agent: str = None) -> Dict[str, Any]:
        """Вход пользователя в систему"""
        try:
            # Находим пользователя
            user = self.db.query(User).filter(User.username == username).first()
            if not user:
                self._log_user_action(None, "login_failed", f"Попытка входа с несуществующим логином: {username}", ip_address, user_agent)
                return {
                    "success": False,
                    "error": "Неверный логин или пароль"
                }
            
            # Проверяем пароль
            if not self.verify_password(password, user.password_hash):
                self._log_user_action(user.id, "login_failed", "Неверный пароль", ip_address, user_agent)
                return {
                    "success": False,
                    "error": "Неверный логин или пароль"
                }
            
            # Проверяем активность пользователя
            if not user.is_active:
                self._log_user_action(user.id, "login_failed", "Попытка входа неактивного пользователя", ip_address, user_agent)
                return {
                    "success": False,
                    "error": "Аккаунт заблокирован"
                }
            
            # Создаем токены
            access_token = self.create_access_token(user.id, user.username)
            refresh_token = self.create_refresh_token(user.id, user.username)
            
            # Сохраняем токены в базе
            self._save_token(user.id, access_token, "access", timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
            self._save_token(user.id, refresh_token, "refresh", timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
            
            # Обновляем время последнего входа
            user.last_login = datetime.utcnow()
            user.last_activity = datetime.utcnow()
            self.db.commit()
            
            # Логируем успешный вход
            self._log_user_action(user.id, "login", "Успешный вход в систему", ip_address, user_agent)
            
            logger.info(f"✅ Пользователь {username} успешно вошел в систему")
            
            return {
                "success": True,
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "name": user.name,
                    "email": user.email,
                    "confession": user.confession,
                    "is_verified": bool(user.is_verified)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка входа: {e}")
            return {
                "success": False,
                "error": "Внутренняя ошибка сервера"
            }
    
    def get_current_user(self, token: str) -> Optional[User]:
        """Получение текущего пользователя по токену"""
        try:
            payload = self.verify_token(token)
            if not payload:
                return None
            
            user_id = payload.get("user_id")
            if not user_id:
                return None
            
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user or not user.is_active:
                return None
            
            return user
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения пользователя: {e}")
            return None
    
    def logout_user(self, token: str) -> bool:
        """Выход пользователя из системы"""
        try:
            payload = self.verify_token(token)
            if not payload:
                return False
            
            user_id = payload.get("user_id")
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            
            # Отзываем токен
            token_record = self.db.query(UserToken).filter(
                UserToken.user_id == user_id,
                UserToken.token_hash == token_hash
            ).first()
            
            if token_record:
                token_record.is_revoked = 1
                self.db.commit()
                
                # Логируем выход
                self._log_user_action(user_id, "logout", "Выход из системы")
                logger.info(f"✅ Пользователь {user_id} вышел из системы")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Ошибка выхода: {e}")
            return False
    
    def _save_token(self, user_id: int, token: str, token_type: str, expires_in: timedelta):
        """Сохранение токена в базе данных"""
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        expires_at = datetime.utcnow() + expires_in
        
        token_record = UserToken(
            user_id=user_id,
            token_hash=token_hash,
            token_type=token_type,
            expires_at=expires_at
        )
        
        self.db.add(token_record)
        self.db.commit()
    
    def _log_user_action(self, user_id: Optional[int], action: str, details: str, ip_address: str = None, user_agent: str = None):
        """Логирование действий пользователя"""
        try:
            # Для неудачных попыток входа используем user_id=0
            effective_user_id = user_id if user_id is not None else 0
            
            log_entry = UserLog(
                user_id=effective_user_id,
                action=action,
                details=details,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            self.db.add(log_entry)
            self.db.commit()
            
        except Exception as e:
            logger.error(f"❌ Ошибка логирования: {e}")
            self.db.rollback()
    
    def create_user_session(self, user_id: int, confession: str) -> str:
        """Создание новой сессии пользователя"""
        try:
            session_id = secrets.token_urlsafe(32)
            
            session = UserSession(
                user_id=user_id,
                session_id=session_id,
                confession=confession
            )
            
            self.db.add(session)
            self.db.commit()
            
            logger.info(f"✅ Создана сессия {session_id} для пользователя {user_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания сессии: {e}")
            return None
    
    def get_user_session(self, session_id: str) -> Optional[UserSession]:
        """Получение сессии пользователя"""
        try:
            return self.db.query(UserSession).filter(
                UserSession.session_id == session_id,
                UserSession.is_active == 1
            ).first()
        except Exception as e:
            logger.error(f"❌ Ошибка получения сессии: {e}")
            return None
    
    def close(self):
        """Закрытие соединения с базой данных"""
        self.db.close()


# Глобальный экземпляр системы аутентификации
auth_system = AuthSystem()
