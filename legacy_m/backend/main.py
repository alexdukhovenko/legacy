"""
Основной файл FastAPI приложения для LEGACY M
"""

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uuid
import json
import logging
from datetime import datetime

import sys
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.env')
if os.path.exists(env_file):
    load_dotenv(env_file)

# Загружаем переменные окружения для продакшена
production_env = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.production.env')
if os.path.exists(production_env):
    load_dotenv(production_env)

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db, init_database, User, UserSession, ChatMessage
from database.models import QuranVerse, Hadith
from backend.simple_ai_agent import SimpleIslamicAIAgent
from backend.auth_routes import auth_router
from backend.auth_middleware import get_current_user, get_current_user_optional
from backend.auth_system import auth_system

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создание FastAPI приложения
app = FastAPI(
    title="LEGACY M - Исламский ИИ-Наставник",
    description="Цифровая платформа духовного наставничества на основе священных текстов",
    version="1.0.0"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене ограничить конкретными доменами
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение статических файлов
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

# Подключение роутеров аутентификации
app.include_router(auth_router)

# Модели Pydantic
class UserRequest(BaseModel):
    user_id: Optional[str] = None  # Если не указан, создается новый

class UserResponse(BaseModel):
    user_id: str
    created: bool  # True если пользователь создан, False если уже существовал

class ChatRequest(BaseModel):
    message: str
    confession: str  # 'sunni', 'shia', 'orthodox'

class ChatResponse(BaseModel):
    response: str
    sources: List[Dict[str, Any]]
    confidence: float
    session_id: str

class SessionResponse(BaseModel):
    session_id: str
    confession: str
    created_at: datetime

class ConfessionRequest(BaseModel):
    user_id: str
    confession: str  # 'sunni', 'shia', 'orthodox'

class ConfessionResponse(BaseModel):
    success: bool
    message: str
    confession: str

class ChatHistoryResponse(BaseModel):
    messages: List[Dict[str, Any]]
    confession: str

# Инициализация базы данных при запуске
@app.on_event("startup")
async def startup_event():
    """Инициализация при запуске приложения"""
    try:
        init_database()
        logger.info("✅ LEGACY M запущен успешно")
    except Exception as e:
        logger.error(f"❌ Ошибка запуска: {e}")

# API эндпоинты
@app.get("/chat", response_class=HTMLResponse)
async def chat_redirect():
    """Перенаправление на чат"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta http-equiv="refresh" content="0; url=/frontend/index.html">
        <title>Перенаправление...</title>
    </head>
    <body>
        <p>Перенаправление на чат...</p>
        <script>window.location.href = '/frontend/index.html';</script>
    </body>
    </html>
    """

@app.get("/", response_class=HTMLResponse)
@app.head("/")
async def read_root():
    """Главная страница"""
    return """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>LEGACY M - Исламский ИИ-Наставник</title>
        <style>
            body {
                font-family: 'Inter', sans-serif;
                background: linear-gradient(135deg, #2c1810 0%, #3d2817 25%, #4a2c1a 50%, #5d3a1f 75%, #6b4224 100%);
                color: #f4e4bc;
                margin: 0;
                padding: 0;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .container {
                text-align: center;
                max-width: 800px;
                padding: 2rem;
            }
            h1 {
                font-size: 3rem;
                color: #d4af37;
                margin-bottom: 1rem;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
            }
            p {
                font-size: 1.2rem;
                line-height: 1.6;
                margin-bottom: 2rem;
            }
            .api-link {
                display: inline-block;
                background: rgba(212, 175, 55, 0.8);
                color: #2c1810;
                padding: 15px 30px;
                text-decoration: none;
                border-radius: 25px;
                font-weight: 600;
                margin: 10px;
                transition: all 0.3s ease;
            }
            .api-link:hover {
                background: #d4af37;
                transform: scale(1.05);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>LEGACY M</h1>
            <p>Исламский ИИ-Наставник</p>
            <p>Цифровая платформа духовного наставничества на основе священных текстов</p>
            <a href="/docs" class="api-link">API Документация</a>
            <a href="/chat" class="api-link">Чат</a>
        </div>
    </body>
    </html>
    """

@app.post("/api/user", response_model=UserResponse)
async def create_or_get_user(request: UserRequest, db: Session = Depends(get_db)):
    """Создание или получение пользователя"""
    try:
        # В новой системе аутентификации пользователи создаются через /api/auth/register
        # Этот endpoint больше не используется
        raise HTTPException(status_code=410, detail="Этот endpoint устарел. Используйте /api/auth/register")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Ошибка создания/получения пользователя: {e}")
        raise HTTPException(status_code=500, detail="Ошибка работы с пользователем")

@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_ai(
    request: ChatRequest, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Чат с ИИ-наставником для конкретной конфессии (требует аутентификации)"""
    try:
        # Используем аутентифицированного пользователя
        user = current_user
        
        # Получаем или создаем сессию для конкретной конфессии
        session = db.query(UserSession).filter(
            UserSession.user_id == user.id,  # user.id уже Integer
            UserSession.confession == request.confession,
            UserSession.is_active == 1
        ).first()
        
        if not session:
            # Создаем новую сессию для этой конфессии
            session_id = auth_system.create_user_session(user.id, request.confession)
            if not session_id:
                raise HTTPException(status_code=500, detail="Ошибка создания сессии")
            logger.info(f"✅ Создана новая сессия для пользователя {user.id} и конфессии {request.confession}")
        else:
            session_id = session.session_id
        
        # Сохраняем сообщение пользователя
        user_message = ChatMessage(
            session_id=session_id,
            message_type="user",
            content=request.message
        )
        db.add(user_message)
        
        # Создаем ИИ-агента и получаем ответ с учетом конфессии
        logger.info(f"🤖 Создаем AI агента для конфессии: {request.confession}")
        ai_agent = SimpleIslamicAIAgent(db)
        logger.info(f"✅ AI агент создан успешно")
        
        logger.info(f"💬 Генерируем ответ на вопрос: {request.message[:50]}...")
        ai_response = ai_agent.generate_response(request.message, request.confession)
        logger.info(f"✅ Ответ получен: {ai_response.get('response', '')[:100]}...")
        
        # Постобработка: принудительно сокращаем длинные ответы
        if len(ai_response['response']) > 800:
            short_response = ai_response['response'][:600] + "..."
            if "Приложение:" not in short_response:
                short_response += "\n\nПриложение: Этот вопрос требует глубокого изучения священных текстов. Рекомендую обратиться к знающему духовнику для получения полного ответа."
            ai_response['response'] = short_response
            logger.info(f"🔄 API: ПРИНУДИТЕЛЬНО сократил ответ до 600 символов")
        
        # Сохраняем ответ ИИ
        ai_message = ChatMessage(
            session_id=session_id,
            message_type="ai",
            content=ai_response['response'],
            sources=json.dumps(ai_response['sources'], ensure_ascii=False) if ai_response['sources'] else None,
            confidence_score=ai_response['confidence']
        )
        db.add(ai_message)
        
        # Обновляем активность сессии (если она существует)
        if session:
            session.last_activity = datetime.utcnow()
        user.last_activity = datetime.utcnow()
        
        db.commit()
        
        return ChatResponse(
            response=ai_response['response'],
            sources=ai_response['sources'],
            confidence=ai_response['confidence'],
            session_id=session_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Ошибка в чате: {e}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        return ChatResponse(
            response="Извините, произошла ошибка. Попробуйте еще раз.",
            sources=[],
            confidence=0.0,
            session_id="error"
        )

@app.get("/api/user/{user_id}/chat/{confession}", response_model=ChatHistoryResponse)
async def get_user_chat_history(user_id: str, confession: str, db: Session = Depends(get_db)):
    """Получение истории чата пользователя с конкретным агентом"""
    try:
        # Проверяем, существует ли пользователь
        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        # Получаем сессию для конкретной конфессии
        session = db.query(UserSession).filter(
            UserSession.user_id == user.id,
            UserSession.confession == confession,
            UserSession.is_active == 1
        ).first()
        
        if not session:
            return ChatHistoryResponse(messages=[], confession=confession)
        
        # Получаем сообщения сессии
        messages = db.query(ChatMessage).filter(
            ChatMessage.session_id == session.session_id
        ).order_by(ChatMessage.created_at.asc()).all()
        
        return ChatHistoryResponse(
            messages=[
                {
                    "id": msg.id,
                    "type": msg.message_type,
                    "content": msg.content,
                    "sources": json.loads(msg.sources) if msg.sources else None,
                    "confidence": msg.confidence_score,
                    "created_at": msg.created_at.isoformat()
                }
                for msg in messages
            ],
            confession=confession
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Ошибка получения истории чата: {e}")
        raise HTTPException(status_code=500, detail="Ошибка получения истории чата")

@app.get("/api/user/{user_id}/sessions")
async def get_user_sessions(user_id: str, db: Session = Depends(get_db)):
    """Получение всех активных сессий пользователя"""
    try:
        # Проверяем, существует ли пользователь
        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        # Получаем все активные сессии пользователя
        sessions = db.query(UserSession).filter(
            UserSession.user_id == user.id,
            UserSession.is_active == 1
        ).order_by(UserSession.last_activity.desc()).all()
        
        return {
            "user_id": user_id,
            "sessions": [
                {
                    "session_id": session.session_id,
                    "confession": session.confession,
                    "created_at": session.created_at.isoformat(),
                    "last_activity": session.last_activity.isoformat()
                }
                for session in sessions
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Ошибка получения сессий пользователя: {e}")
        raise HTTPException(status_code=500, detail="Ошибка получения сессий")

@app.get("/api/user/{user_id}/info")
async def get_user_info(user_id: str, db: Session = Depends(get_db)):
    """Получение информации о пользователе"""
    try:
        # Проверяем, существует ли пользователь
        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        # Получаем количество активных сессий
        active_sessions = db.query(UserSession).filter(
            UserSession.user_id == user.id,
            UserSession.is_active == 1
        ).count()
        
        return {
            "user_id": str(user.id),
            "name": user.name,
            "confession": user.confession,
            "created_at": user.created_at.isoformat(),
            "last_activity": user.last_activity.isoformat(),
            "active_sessions": active_sessions,
            "is_active": bool(user.is_active)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Ошибка получения информации о пользователе: {e}")
        raise HTTPException(status_code=500, detail="Ошибка получения информации о пользователе")


@app.get("/api/verse/{verse_type}/{verse_id}")
async def get_verse_details(verse_type: str, verse_id: int, db: Session = Depends(get_db)):
    """Получить полный текст аята или хадиса"""
    if verse_type == "quran":
        verse = db.query(QuranVerse).filter(QuranVerse.id == verse_id).first()
        if verse:
            return {
                "type": "quran",
                "surah_number": verse.surah_number,
                "verse_number": verse.verse_number,
                "arabic_text": verse.arabic_text,
                "translation_ru": verse.translation_ru,
                "translation_en": verse.translation_en,
                "commentary": verse.commentary,
                "theme": verse.theme
            }
    elif verse_type == "hadith":
        hadith = db.query(Hadith).filter(Hadith.id == verse_id).first()
        if hadith:
            return {
                "type": "hadith",
                "collection": hadith.collection,
                "book_number": hadith.book_number,
                "hadith_number": hadith.hadith_number,
                "arabic_text": hadith.arabic_text,
                "translation_ru": hadith.translation_ru,
                "translation_en": hadith.translation_en,
                "narrator": hadith.narrator,
                "grade": hadith.grade,
                "topic": hadith.topic,
                "commentary": hadith.commentary
            }
    
    return {"error": "Verse not found"}

@app.get("/api/health")
@app.head("/api/health")
async def health_check():
    """Проверка здоровья API"""
    return {"status": "healthy", "service": "LEGACY M"}

# Запуск приложения
if __name__ == "__main__":
    import uvicorn
    
    # Получаем настройки из переменных окружения
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", os.getenv("$PORT", 8000)))
    workers = int(os.getenv("WORKERS", 1))
    environment = os.getenv("ENVIRONMENT", "development")
    
    if environment == "production":
        # Настройки для продакшена - используем uvicorn без workers
        uvicorn.run(
            app, 
            host=host, 
            port=port, 
            access_log=True,
            log_level="info"
        )
    else:
        # Настройки для разработки
        uvicorn.run(
            app, 
            host=host, 
            port=port, 
            reload=True,
            log_level="debug"
        )
