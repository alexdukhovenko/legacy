# 🚀 Руководство по развертыванию LEGACY M

## 🌍 **Проблема с доступностью AI API**

OpenAI API может быть недоступен в некоторых регионах. Мы решили эту проблему, добавив поддержку нескольких AI провайдеров с автоматическим fallback.

## 🔧 **Поддерживаемые AI провайдеры:**

1. **OpenAI GPT-4** (основной)
2. **Anthropic Claude** (альтернатива)
3. **Ollama (локальный)** (для регионов без доступа к облачным API)

## 📋 **Варианты развертывания:**

### **Вариант 1: Railway + OpenAI (рекомендуется)**

1. **Настройте Railway:**
   ```bash
   # Переменные окружения в Railway:
   OPENAI_API_KEY=your_openai_key
   ANTHROPIC_API_KEY=your_anthropic_key
   DATABASE_URL=postgresql://...
   ENVIRONMENT=production
   ```

2. **Деплой:**
   - Подключите GitHub репозиторий
   - Railway автоматически соберет и развернет

### **Вариант 2: VPS + Ollama (для заблокированных регионов)**

1. **Арендуйте VPS** (DigitalOcean, AWS, etc.)

2. **Установите Ollama:**
   ```bash
   curl -fsSL https://ollama.ai/install.sh | sh
   ollama pull llama2
   ```

3. **Настройте переменные:**
   ```bash
   export OLLAMA_URL=http://localhost:11434
   export OLLAMA_MODEL=llama2
   export DATABASE_URL=postgresql://...
   ```

4. **Запустите приложение:**
   ```bash
   docker-compose up -d
   ```

### **Вариант 3: Render.com (простой)**

1. **Создайте аккаунт** на render.com
2. **Подключите GitHub** репозиторий
3. **Настройте переменные** окружения
4. **Деплой** автоматический

## 🔑 **Настройка переменных окружения:**

### **Для Railway/Render:**
```
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
DATABASE_URL=postgresql://user:pass@host:port/db
ENVIRONMENT=production
```

### **Для VPS с Ollama:**
```
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama2
DATABASE_URL=postgresql://user:pass@host:port/db
ENVIRONMENT=production
```

## 🌐 **Настройка домена:**

1. **Купите домен** (например, `your-legacy.com`)
2. **Настройте DNS:**
   - A-запись → IP вашего сервера
   - CNAME → ваш-проект.railway.app (для Railway)
3. **SSL сертификат** (автоматически на Railway/Render)

## 📊 **Мониторинг:**

- **Railway:** Встроенные логи и метрики
- **VPS:** `docker logs legacy-m-backend`
- **Health check:** `https://your-domain.com/api/health`

## 🔄 **Обновления:**

После изменений в коде:
```bash
git add .
git commit -m "Update"
git push origin main
```

Railway/Render автоматически пересоберет и развернет.

## 🆘 **Решение проблем:**

### **OpenAI заблокирован:**
- Система автоматически переключится на Anthropic
- Если и он заблокирован → Ollama

### **База данных недоступна:**
- Проверьте `DATABASE_URL`
- Убедитесь, что PostgreSQL запущен

### **Приложение не запускается:**
- Проверьте логи: `railway logs` или `docker logs`
- Убедитесь, что все переменные окружения настроены

## 💰 **Стоимость:**

- **Railway:** $5/месяц (базовый план)
- **Render:** Бесплатный план доступен
- **VPS:** $5-20/месяц в зависимости от провайдера
- **Домен:** $10-15/год

## 🎯 **Рекомендации:**

1. **Для начала:** Railway + OpenAI
2. **Для заблокированных регионов:** VPS + Ollama
3. **Для масштабирования:** AWS/GCP + Kubernetes

---

**Готово!** Ваше приложение будет работать в любом регионе мира! 🌍
