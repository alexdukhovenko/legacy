# 🛠️ Руководство по разработке LEGACY M

## Локальная разработка

### 1. Настройка окружения
```bash
# Клонирование репозитория
git clone <your-repo-url>
cd legacy_m

# Установка зависимостей
pip install -r requirements.txt

# Настройка переменных окружения
cp config.env.example config.env
# Отредактируйте config.env с вашими настройками
```

### 2. Запуск локально
```bash
# Обычный запуск
python3 backend/main.py

# Или с Docker
docker-compose up -d
```

### 3. Тестирование изменений
```bash
# Проверка API
curl http://localhost:8000/api/health

# Тестирование чата
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Тест", "user_id": "test", "confession": "orthodox"}'
```

## Процесс внесения изменений

### 1. Создание ветки для новой функции
```bash
git checkout -b feature/new-functionality
```

### 2. Внесение изменений
- Редактируйте код локально
- Тестируйте изменения
- Убедитесь, что все работает

### 3. Коммит и пуш
```bash
git add .
git commit -m "Описание изменений"
git push origin feature/new-functionality
```

### 4. Создание Pull Request
- Перейдите в GitHub
- Создайте Pull Request
- Проведите code review
- Слейте в main

### 5. Автоматическое развертывание
- Railway автоматически развернет изменения
- Проверьте работу на продакшене

## Структура проекта для разработки

```
legacy_m/
├── backend/                 # Backend код
│   ├── main.py             # Основное приложение
│   ├── simple_ai_agent.py  # AI агент
│   └── confession_agents.py # Агенты конфессий
├── frontend/               # Frontend код
│   └── index.html          # Главная страница
├── database/               # База данных
│   ├── models.py           # Модели данных
│   └── database.py         # Подключение к БД
├── data/                   # Данные (тексты)
├── scripts/                # Скрипты для загрузки данных
├── tests/                  # Тесты (создать)
├── docs/                   # Документация
└── config/                 # Конфигурация
```

## Добавление новых функций

### 1. Новый AI агент
```python
# backend/confession_agents.py
class NewConfessionAgent(BaseConfessionAgent):
    def _get_system_prompt(self) -> str:
        return "Ты агент для новой конфессии..."
    
    def search_relevant_texts(self, question: str, limit: int = 5):
        # Логика поиска
        pass
```

### 2. Новый API endpoint
```python
# backend/main.py
@app.post("/api/new-endpoint")
async def new_endpoint(request: NewRequest):
    # Логика endpoint
    return {"result": "success"}
```

### 3. Новые данные
```bash
# Загрузка новых текстов
python3 scripts/load_new_data.py
```

## Тестирование

### 1. Локальное тестирование
```bash
# Запуск тестов
python -m pytest tests/

# Проверка покрытия
python -m pytest --cov=backend tests/
```

### 2. Тестирование на продакшене
```bash
# Проверка health check
curl https://yourdomain.com/api/health

# Тестирование основных функций
curl -X POST "https://yourdomain.com/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Тест", "user_id": "test", "confession": "orthodox"}'
```

## Мониторинг и логи

### 1. Логи приложения
```bash
# Railway
railway logs

# Docker
docker-compose logs -f backend
```

### 2. Мониторинг производительности
- **Railway Dashboard** - метрики сервера
- **Uptime Robot** - доступность сайта
- **Sentry** - отслеживание ошибок

## Откат изменений

### 1. Откат через Railway
```bash
# Просмотр предыдущих развертываний
railway deployments

# Откат к предыдущей версии
railway rollback <deployment-id>
```

### 2. Откат через Git
```bash
# Откат к предыдущему коммиту
git revert <commit-hash>
git push origin main
```

## Добавление новых конфессий

### 1. Создание агента
```python
class BuddhistAgent(BaseConfessionAgent):
    def _get_system_prompt(self) -> str:
        return "Ты буддийский духовный наставник..."
```

### 2. Добавление в фабрику
```python
class ConfessionAgentFactory:
    @staticmethod
    def create_agent(confession: str, db: Session):
        if confession == 'buddhist':
            return BuddhistAgent(db)
        # ... остальные агенты
```

### 3. Обновление frontend
```html
<!-- Добавить кнопку в интерфейс -->
<button onclick="selectConfession('buddhist')">Буддизм</button>
```

### 4. Загрузка данных
```bash
# Создать скрипт для загрузки буддийских текстов
python3 scripts/load_buddhist_data.py
```

## Работа с базой данных

### 1. Миграции
```python
# Создание новой таблицы
from database.models import Base, engine
Base.metadata.create_all(engine)
```

### 2. Обновление данных
```python
# Скрипт для обновления существующих данных
python3 scripts/update_data.py
```

### 3. Резервное копирование
```bash
# Создание бэкапа
pg_dump $DATABASE_URL > backup.sql

# Восстановление
psql $DATABASE_URL < backup.sql
```

## Полезные команды

### Git
```bash
# Просмотр изменений
git status
git diff

# Отмена изменений
git checkout -- <file>
git reset HEAD <file>

# Просмотр истории
git log --oneline
```

### Docker
```bash
# Пересборка контейнера
docker-compose build --no-cache

# Просмотр логов
docker-compose logs -f

# Остановка всех контейнеров
docker-compose down
```

### Railway
```bash
# Установка CLI
npm install -g @railway/cli

# Логин
railway login

# Подключение к проекту
railway link

# Просмотр логов
railway logs

# Переменные окружения
railway variables
```

## Советы по разработке

### 1. Всегда тестируйте локально
- Убедитесь, что изменения работают
- Проверьте все основные функции
- Протестируйте на разных конфессиях

### 2. Используйте ветки
- Создавайте отдельную ветку для каждой функции
- Не работайте напрямую в main
- Используйте Pull Requests для code review

### 3. Документируйте изменения
- Пишите понятные commit messages
- Обновляйте документацию
- Комментируйте сложный код

### 4. Мониторьте производительность
- Следите за временем ответа API
- Проверяйте использование памяти
- Оптимизируйте медленные запросы

### 5. Безопасность
- Не коммитьте API ключи
- Используйте переменные окружения
- Регулярно обновляйте зависимости
