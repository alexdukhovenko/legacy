"""
Модели базы данных для LEGACY M
Структура готова для загрузки священных текстов
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class QuranVerse(Base):
    """Таблица для аятов Корана"""
    __tablename__ = "quran_verses"
    
    id = Column(Integer, primary_key=True, index=True)
    surah_number = Column(Integer, nullable=False, index=True)
    verse_number = Column(Integer, nullable=False, index=True)
    arabic_text = Column(Text, nullable=False)
    transliteration = Column(Text, nullable=True)
    translation_ru = Column(Text, nullable=True)
    translation_en = Column(Text, nullable=True)
    commentary = Column(Text, nullable=True)
    theme = Column(String(255), nullable=True, index=True)
    confession = Column(String(50), nullable=True, index=True)  # 'sunni', 'shia', 'common'
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Индексы для быстрого поиска
    __table_args__ = (
        Index('idx_surah_verse', 'surah_number', 'verse_number'),
        Index('idx_theme', 'theme'),
    )


class Hadith(Base):
    """Таблица для хадисов"""
    __tablename__ = "hadiths"
    
    id = Column(Integer, primary_key=True, index=True)
    collection = Column(String(100), nullable=False, index=True)  # Bukhari, Muslim, etc.
    book_number = Column(Integer, nullable=True)
    hadith_number = Column(Integer, nullable=True)
    arabic_text = Column(Text, nullable=False)
    translation_ru = Column(Text, nullable=True)
    translation_en = Column(Text, nullable=True)
    narrator = Column(String(255), nullable=True)
    grade = Column(String(50), nullable=True)  # Sahih, Hasan, etc.
    topic = Column(String(255), nullable=True, index=True)
    commentary = Column(Text, nullable=True)
    confession = Column(String(50), nullable=True, index=True)  # 'sunni', 'shia', 'common'
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Индексы для быстрого поиска
    __table_args__ = (
        Index('idx_collection_number', 'collection', 'hadith_number'),
        Index('idx_topic', 'topic'),
        Index('idx_grade', 'grade'),
    )


class Commentary(Base):
    """Таблица для комментариев и тафсиров"""
    __tablename__ = "commentaries"
    
    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(100), nullable=False, index=True)  # Ibn Kathir, etc.
    verse_id = Column(Integer, ForeignKey('quran_verses.id'), nullable=True)
    hadith_id = Column(Integer, ForeignKey('hadiths.id'), nullable=True)
    arabic_text = Column(Text, nullable=True)
    translation_ru = Column(Text, nullable=True)
    translation_en = Column(Text, nullable=True)
    confession = Column(String(50), nullable=True, index=True)  # 'sunni', 'shia', 'common'
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    verse = relationship("QuranVerse", backref="commentaries")
    hadith = relationship("Hadith", backref="commentaries")


class OrthodoxText(Base):
    """Таблица для православных текстов (Библия, святоотеческие труды, догматика)"""
    __tablename__ = "orthodox_texts"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey('orthodox_documents.id'), nullable=True)  # Связь с документом
    source_type = Column(String(50), nullable=False, index=True)  # 'bible', 'patristic', 'dogmatic', 'liturgical'
    book_name = Column(String(255), nullable=False, index=True)  # Название книги
    author = Column(String(255), nullable=True, index=True)  # Автор (святой отец, богослов)
    chapter_number = Column(Integer, nullable=True, index=True)
    verse_number = Column(Integer, nullable=True, index=True)
    original_text = Column(Text, nullable=True)  # Оригинальный текст (греческий, церковнославянский)
    translation_ru = Column(Text, nullable=False)  # Русский перевод
    commentary = Column(Text, nullable=True)  # Комментарий или толкование
    theme = Column(String(255), nullable=True, index=True)  # Тематика
    confession = Column(String(50), nullable=True, index=True)  # 'orthodox'
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Индексы для быстрого поиска
    __table_args__ = (
        Index('idx_orthodox_book_chapter_verse', 'book_name', 'chapter_number', 'verse_number'),
        Index('idx_orthodox_author', 'author'),
        Index('idx_orthodox_theme', 'theme'),
    )


class OrthodoxDocument(Base):
    """Таблица для православных документов (PDF файлы)"""
    __tablename__ = "orthodox_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False, index=True)
    title = Column(String(255), nullable=False, index=True)
    author = Column(String(255), nullable=True, index=True)
    document_type = Column(String(50), nullable=False, index=True)  # 'dogmatic', 'patristic', 'liturgical', 'catechetical'
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=True)
    pages_count = Column(Integer, nullable=True)
    processed = Column(Integer, default=0)  # 0 = not processed, 1 = processed
    confession = Column(String(50), nullable=True, index=True)  # 'orthodox'
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    
    # Индексы
    __table_args__ = (
        Index('idx_orthodox_document_type', 'document_type'),
        Index('idx_orthodox_processed', 'processed'),
    )


class VectorEmbedding(Base):
    """Таблица для векторных представлений текстов"""
    __tablename__ = "vector_embeddings"
    
    id = Column(Integer, primary_key=True, index=True)
    source_type = Column(String(50), nullable=False)  # 'quran', 'hadith', 'commentary'
    source_id = Column(Integer, nullable=False, index=True)
    text_chunk = Column(Text, nullable=False)
    embedding_vector = Column(Text, nullable=False)  # JSON string of vector
    chunk_index = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Индексы
    __table_args__ = (
        Index('idx_source_type_id', 'source_type', 'source_id'),
    )


class User(Base):
    """Таблица для пользователей с системой аутентификации"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)  # Уникальный логин
    email = Column(String(255), unique=True, nullable=True, index=True)  # Email (опционально)
    phone = Column(String(20), unique=True, nullable=True, index=True)  # Номер телефона (опционально)
    password_hash = Column(String(255), nullable=False)  # Хеш пароля
    name = Column(String(255), nullable=True)  # Имя пользователя (опционально)
    confession = Column(String(50), nullable=True, index=True)  # Конфессия: 'sunni', 'shia', 'orthodox', null
    is_verified = Column(Integer, default=0)  # 1 = verified, 0 = not verified
    is_active = Column(Integer, default=1)  # 1 = active, 0 = inactive
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Индексы
    __table_args__ = (
        Index('idx_username', 'username'),
        Index('idx_email', 'email'),
    )


class UserSession(Base):
    """Таблица для сессий пользователей"""
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)  # Ссылка на users.id
    session_id = Column(String(255), unique=True, nullable=False, index=True)
    confession = Column(String(50), nullable=False, index=True)  # 'sunni', 'shia', 'orthodox'
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Integer, default=1)  # 1 = active, 0 = inactive
    
    # Связи
    user = relationship("User", backref="sessions")


class ChatMessage(Base):
    """Таблица для сообщений чата"""
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), ForeignKey('user_sessions.session_id'), nullable=False)
    message_type = Column(String(20), nullable=False)  # 'user' or 'ai'
    content = Column(Text, nullable=False)
    sources = Column(Text, nullable=True)  # JSON string of source references
    confidence_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    session = relationship("UserSession", backref="messages")


class UserToken(Base):
    """Таблица для JWT токенов пользователей"""
    __tablename__ = "user_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    token_hash = Column(String(255), nullable=False, index=True)  # Хеш JWT токена
    token_type = Column(String(20), nullable=False, default='access')  # 'access', 'refresh'
    expires_at = Column(DateTime, nullable=False)
    is_revoked = Column(Integer, default=0)  # 1 = revoked, 0 = active
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    user = relationship("User", backref="tokens")
    
    # Индексы
    __table_args__ = (
        Index('idx_token_hash', 'token_hash'),
        Index('idx_user_token_type', 'user_id', 'token_type'),
    )


class UserLog(Base):
    """Таблица для логов активности пользователей"""
    __tablename__ = "user_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    action = Column(String(100), nullable=False, index=True)  # 'login', 'logout', 'chat', 'error', etc.
    details = Column(Text, nullable=True)  # Детали действия
    ip_address = Column(String(45), nullable=True)  # IPv4 или IPv6
    user_agent = Column(Text, nullable=True)  # User-Agent браузера
    session_id = Column(String(255), nullable=True, index=True)
    error_code = Column(String(50), nullable=True, index=True)  # Код ошибки если есть
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    user = relationship("User", backref="logs")
    
    # Индексы
    __table_args__ = (
        Index('idx_user_action', 'user_id', 'action'),
        Index('idx_user_created', 'user_id', 'created_at'),
        Index('idx_error_code', 'error_code'),
    )


class UserChatHistory(Base):
    """Таблица для истории чатов пользователей с контекстом"""
    __tablename__ = "user_chat_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    session_id = Column(String(255), nullable=False, index=True)
    confession = Column(String(50), nullable=False, index=True)  # Конфессия для этого чата
    message_sequence = Column(Integer, nullable=False, default=0)  # Порядок сообщений в сессии
    user_message = Column(Text, nullable=False)  # Сообщение пользователя
    ai_response = Column(Text, nullable=True)  # Ответ AI
    ai_sources = Column(Text, nullable=True)  # JSON источников AI
    context_summary = Column(Text, nullable=True)  # Краткое резюме контекста
    processing_time = Column(Float, nullable=True)  # Время обработки в секундах
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    user = relationship("User", backref="chat_history")
    
    # Индексы
    __table_args__ = (
        Index('idx_user_session', 'user_id', 'session_id'),
        Index('idx_user_confession', 'user_id', 'confession'),
        Index('idx_session_sequence', 'session_id', 'message_sequence'),
    )


class SystemConfig(Base):
    """Таблица для системных настроек"""
    __tablename__ = "system_config"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
