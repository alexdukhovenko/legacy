"""
Настройка подключения к базе данных
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os
from .models import Base

# Путь к базе данных
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./legacy_m.db")

# Проверяем DATABASE_URL
if DATABASE_URL and ("postgresql://" in DATABASE_URL or "postgres://" in DATABASE_URL):
    print(f"✅ Используем PostgreSQL: {DATABASE_URL[:20]}...")
    # Убеждаемся, что используем правильный формат
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        print(f"✅ Исправлен формат URL: {DATABASE_URL[:20]}...")
else:
    print(f"⚠️ Используем SQLite: {DATABASE_URL}")

# Создание движка базы данных
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    poolclass=StaticPool if "sqlite" in DATABASE_URL else None,
    echo=False  # Установите True для отладки SQL запросов
)

# Создание фабрики сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables():
    """Создание всех таблиц в базе данных"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency для получения сессии базы данных"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_database():
    """Инициализация базы данных с начальными данными"""
    # Создаем таблицы только если их нет
    try:
        # Проверяем, существует ли база данных
        from .models import User
        db = SessionLocal()
        db.query(User).first()  # Попытка выполнить запрос
        db.close()
        print("✅ База данных уже инициализирована")
    except Exception:
        # База данных не существует, создаем таблицы
        print("📊 Инициализация базы данных...")
        create_tables()
        print("✅ База данных инициализирована с базовыми настройками")
    
    # Здесь можно добавить начальные настройки системы
    db = SessionLocal()
    try:
        # Проверяем, есть ли уже настройки
        from .models import SystemConfig
        
        existing_config = db.query(SystemConfig).first()
        if not existing_config:
            # Добавляем базовые настройки системы
            configs = [
                SystemConfig(
                    key="ai_model_name",
                    value="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
                    description="Модель для создания эмбеддингов"
                ),
                SystemConfig(
                    key="max_response_length",
                    value="500",
                    description="Максимальная длина ответа ИИ"
                ),
                SystemConfig(
                    key="similarity_threshold",
                    value="0.7",
                    description="Порог схожести для поиска релевантных текстов"
                ),
                SystemConfig(
                    key="system_prompt",
                    value="Ты исламский духовный наставник. Отвечай только на основе предоставленных священных текстов. Всегда указывай источники. Рекомендуй обратиться к живому духовнику для важных вопросов.",
                    description="Системный промпт для ИИ"
                )
            ]
            
            for config in configs:
                db.add(config)
            
            db.commit()
            print("✅ База данных инициализирована с базовыми настройками")
        else:
            print("✅ База данных уже инициализирована")
            
    except Exception as e:
        print(f"❌ Ошибка при инициализации базы данных: {e}")
        db.rollback()
    finally:
        db.close()
