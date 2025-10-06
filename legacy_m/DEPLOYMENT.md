# 🚀 Развертывание LEGACY M

## Локальное развертывание с Docker

### 1. Клонирование и настройка
```bash
git clone <your-repo-url>
cd legacy_m
```

### 2. Настройка переменных окружения
```bash
# Скопируйте и отредактируйте файл конфигурации
cp config.production.env .env
# Добавьте ваш OpenAI API ключ
```

### 3. Запуск с Docker Compose
```bash
docker-compose up -d
```

### 4. Проверка
- Backend: http://localhost:8000
- API Health: http://localhost:8000/api/health

## Развертывание на хостинге

### Вариант 1: Railway (Рекомендуется)

1. **Подготовка:**
   - Зарегистрируйтесь на [Railway.app](https://railway.app)
   - Подключите GitHub репозиторий

2. **Настройка переменных окружения:**
   ```
   DATABASE_URL=postgresql://user:pass@host:port/db
   OPENAI_API_KEY=your_key_here
   ENVIRONMENT=production
   ```

3. **Развертывание:**
   - Railway автоматически обнаружит Dockerfile
   - Приложение будет развернуто автоматически

### Вариант 2: Render

1. **Подготовка:**
   - Зарегистрируйтесь на [Render.com](https://render.com)
   - Подключите GitHub репозиторий

2. **Создание сервисов:**
   - PostgreSQL Database
   - Web Service (Python)

3. **Настройка:**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python backend/main.py`

### Вариант 3: DigitalOcean

1. **Создание Droplet:**
   - Ubuntu 22.04 LTS
   - Минимум 2GB RAM

2. **Установка Docker:**
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   ```

3. **Развертывание:**
   ```bash
   git clone <your-repo>
   cd legacy_m
   docker-compose up -d
   ```

## Настройка домена

### 1. Покупка домена
- Рекомендуемые регистраторы: Namecheap, GoDaddy, Cloudflare
- Выберите домен (например: `legacy-m.com`)

### 2. Настройка DNS
- A-запись: `@` → IP адрес сервера
- CNAME: `www` → `yourdomain.com`

### 3. SSL сертификат
- **Let's Encrypt** (бесплатно)
- **Cloudflare** (бесплатно с CDN)

## Мониторинг и логи

### Логи приложения
```bash
# Docker
docker-compose logs -f backend

# Системные логи
tail -f /var/log/nginx/access.log
```

### Мониторинг
- **Uptime Robot** - мониторинг доступности
- **Sentry** - отслеживание ошибок
- **Google Analytics** - аналитика

## Безопасность

### 1. Firewall
```bash
# UFW (Ubuntu)
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

### 2. Nginx (рекомендуется)
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Резервное копирование

### База данных
```bash
# PostgreSQL
pg_dump -h localhost -U legacy_user legacy_m > backup.sql

# Восстановление
psql -h localhost -U legacy_user legacy_m < backup.sql
```

### Файлы приложения
```bash
# Создание архива
tar -czf legacy_m_backup.tar.gz /path/to/app

# Восстановление
tar -xzf legacy_m_backup.tar.gz
```

## Масштабирование

### Горизонтальное масштабирование
- Load Balancer (Nginx, HAProxy)
- Несколько инстансов приложения
- Shared database

### Вертикальное масштабирование
- Увеличение RAM/CPU сервера
- Оптимизация кода
- Кэширование (Redis)

## Стоимость

### Минимальная конфигурация:
- **Домен**: $10-15/год
- **Хостинг**: $5-10/месяц
- **SSL**: Бесплатно (Let's Encrypt)
- **Итого**: ~$70-135/год

### Рекомендуемая конфигурация:
- **Домен**: $10-15/год
- **Хостинг**: $20-50/месяц
- **CDN**: $5-20/месяц
- **Мониторинг**: $10-30/месяц
- **Итого**: ~$540-1140/год
