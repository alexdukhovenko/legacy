#!/bin/bash

# Скрипт для быстрого развертывания LEGACY M

set -e  # Остановка при ошибке

echo "🚀 LEGACY M - Скрипт развертывания"
echo "=================================="

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для вывода сообщений
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверка наличия необходимых инструментов
check_requirements() {
    print_status "Проверка требований..."
    
    if ! command -v git &> /dev/null; then
        print_error "Git не установлен. Установите Git и попробуйте снова."
        exit 1
    fi
    
    if ! command -v docker &> /dev/null; then
        print_warning "Docker не установлен. Рекомендуется установить Docker для локального тестирования."
    fi
    
    print_success "Все требования выполнены"
}

# Инициализация Git репозитория
init_git() {
    print_status "Инициализация Git репозитория..."
    
    if [ ! -d ".git" ]; then
        git init
        print_success "Git репозиторий инициализирован"
    else
        print_status "Git репозиторий уже существует"
    fi
    
    # Создание .gitignore если не существует
    if [ ! -f ".gitignore" ]; then
        cat > .gitignore << EOF
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Project specific
*.db
*.sqlite
*.sqlite3
logs/
*.log
config.env
.env.local
.env.production

# Data files
data/
quran/
EOF
        print_success ".gitignore создан"
    fi
}

# Создание конфигурационного файла
create_config() {
    print_status "Создание конфигурационного файла..."
    
    if [ ! -f "config.env" ]; then
        cat > config.env << EOF
# Development Environment Variables
ENVIRONMENT=development
DEBUG=true

# Database (SQLite для разработки)
DATABASE_URL=sqlite:///./legacy_m.db

# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here

# Server Settings
HOST=0.0.0.0
PORT=8000
WORKERS=1

# Logging
LOG_LEVEL=DEBUG
EOF
        print_success "config.env создан"
        print_warning "Не забудьте добавить ваш OpenAI API ключ в config.env"
    else
        print_status "config.env уже существует"
    fi
}

# Установка зависимостей
install_dependencies() {
    print_status "Установка зависимостей..."
    
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        print_success "Зависимости установлены"
    else
        print_error "requirements.txt не найден"
        exit 1
    fi
}

# Тестирование локального запуска
test_local() {
    print_status "Тестирование локального запуска..."
    
    # Проверка, что порт 8000 свободен
    if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
        print_warning "Порт 8000 занят. Остановите другие процессы или измените порт в config.env"
        return 1
    fi
    
    print_success "Порт 8000 свободен"
    return 0
}

# Создание README
create_readme() {
    print_status "Создание README.md..."
    
    if [ ! -f "README.md" ]; then
        cat > README.md << EOF
# 🕌 LEGACY M - Исламский ИИ-Наставник

Цифровая платформа духовного наставничества на основе священных текстов.

## 🚀 Быстрый старт

### Локальная разработка
\`\`\`bash
# Установка зависимостей
pip install -r requirements.txt

# Настройка переменных окружения
cp config.env.example config.env
# Добавьте ваш OpenAI API ключ в config.env

# Запуск приложения
python3 backend/main.py
\`\`\`

### Развертывание с Docker
\`\`\`bash
# Запуск с Docker Compose
docker-compose up -d

# Проверка статуса
docker-compose ps
\`\`\`

## 📖 Документация

- [Руководство по развертыванию](DEPLOYMENT.md)
- [Руководство по разработке](DEVELOPMENT.md)

## 🔧 Технологии

- **Backend**: FastAPI, Python 3.11
- **Frontend**: HTML, CSS, JavaScript
- **База данных**: SQLite (dev), PostgreSQL (prod)
- **AI**: OpenAI GPT-4
- **Развертывание**: Docker, Railway

## 📝 Лицензия

MIT License
EOF
        print_success "README.md создан"
    else
        print_status "README.md уже существует"
    fi
}

# Основная функция
main() {
    echo "Выберите действие:"
    echo "1) Подготовка к развертыванию"
    echo "2) Локальное тестирование"
    echo "3) Создание GitHub репозитория"
    echo "4) Развертывание на Railway"
    echo "5) Полная настройка"
    
    read -p "Введите номер (1-5): " choice
    
    case $choice in
        1)
            check_requirements
            init_git
            create_config
            install_dependencies
            create_readme
            print_success "Проект подготовлен к развертыванию!"
            ;;
        2)
            test_local
            if [ $? -eq 0 ]; then
                print_success "Готово к локальному тестированию!"
                print_status "Запустите: python3 backend/main.py"
            fi
            ;;
        3)
            print_status "Создание GitHub репозитория..."
            print_warning "Создайте репозиторий на GitHub.com и выполните:"
            echo "git remote add origin https://github.com/yourusername/legacy-m.git"
            echo "git add ."
            echo "git commit -m 'Initial commit'"
            echo "git push -u origin main"
            ;;
        4)
            print_status "Развертывание на Railway..."
            print_warning "1. Зарегистрируйтесь на railway.app"
            print_warning "2. Подключите GitHub репозиторий"
            print_warning "3. Настройте переменные окружения"
            print_warning "4. Railway автоматически развернет проект"
            ;;
        5)
            check_requirements
            init_git
            create_config
            install_dependencies
            create_readme
            test_local
            print_success "Полная настройка завершена!"
            print_status "Следующие шаги:"
            echo "1. Добавьте OpenAI API ключ в config.env"
            echo "2. Создайте GitHub репозиторий"
            echo "3. Разверните на Railway"
            ;;
        *)
            print_error "Неверный выбор"
            exit 1
            ;;
    esac
}

# Запуск скрипта
main "$@"
