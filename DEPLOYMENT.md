# 🚀 Развертывание AI Book Splitter & Designer

## 📋 Предварительные требования

1. **Git** установлен на вашем компьютере
2. **GitHub аккаунт** для загрузки кода
3. **OpenAI API ключ** для AI анализа
4. **Docker** (опционально, для контейнерного развертывания)

## 🔧 Локальная установка

### 1. Клонирование репозитория
```bash
git clone https://github.com/your-username/ai-book-splitter.git
cd ai-book-splitter
```

### 2. Настройка Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Настройка OpenAI API
Создайте файл `backend/config.py`:
```python
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = "ваш-openai-api-ключ"
# ... остальные настройки
```

### 4. Запуск Backend
```bash
cd backend
python main.py
```

### 5. Настройка Frontend
```bash
cd frontend
npm install
```

### 6. Запуск Frontend
```bash
cd frontend
npm start
```

## 🐳 Docker развертывание

### 1. Настройка переменных окружения
Скопируйте `env.example` в `.env` и настройте:
```bash
cp env.example .env
# Отредактируйте .env файл, добавив ваш OpenAI API ключ
```

### 2. Запуск с Docker Compose
```bash
docker-compose up -d
```

### 3. Проверка работы
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API документация: http://localhost:8000/docs

## ☁️ Развертывание на сервере

### 1. Подготовка сервера
```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. Клонирование и настройка
```bash
git clone https://github.com/your-username/ai-book-splitter.git
cd ai-book-splitter
cp env.example .env
# Настройте .env файл
```

### 3. Запуск
```bash
docker-compose up -d
```

### 4. Настройка Nginx (опционально)
```bash
sudo cp nginx.conf /etc/nginx/sites-available/ai-book-splitter
sudo ln -s /etc/nginx/sites-available/ai-book-splitter /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 🔐 Безопасность

### 1. Настройка SSL сертификатов
```bash
# Установка Certbot
sudo apt install certbot python3-certbot-nginx

# Получение SSL сертификата
sudo certbot --nginx -d your-domain.com
```

### 2. Настройка файрвола
```bash
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

### 3. Регулярные обновления
```bash
# Обновление приложения
git pull origin main
docker-compose down
docker-compose up -d --build
```

## 📊 Мониторинг

### 1. Логи приложения
```bash
# Просмотр логов
docker-compose logs -f

# Логи конкретного сервиса
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 2. Мониторинг ресурсов
```bash
# Использование ресурсов
docker stats

# Место на диске
df -h
```

## 🛠️ Устранение неполадок

### 1. Проблемы с OpenAI API
- Проверьте правильность API ключа
- Убедитесь, что у вас есть кредиты на аккаунте
- Проверьте лимиты API

### 2. Проблемы с Docker
```bash
# Перезапуск контейнеров
docker-compose restart

# Полная пересборка
docker-compose down
docker-compose up -d --build
```

### 3. Проблемы с портами
```bash
# Проверка занятых портов
sudo netstat -tulpn | grep :8000
sudo netstat -tulpn | grep :3000

# Освобождение портов
sudo fuser -k 8000/tcp
sudo fuser -k 3000/tcp
```

## 📈 Масштабирование

### 1. Горизонтальное масштабирование
```yaml
# В docker-compose.yml
services:
  backend:
    deploy:
      replicas: 3
```

### 2. Настройка балансировщика нагрузки
```nginx
upstream backend {
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}
```

## 🔄 Резервное копирование

### 1. Резервное копирование данных
```bash
# Создание бэкапа
tar -czf backup-$(date +%Y%m%d).tar.gz uploads/ output/ temp/

# Восстановление
tar -xzf backup-20231201.tar.gz
```

### 2. Автоматическое резервное копирование
```bash
# Добавление в crontab
0 2 * * * cd /path/to/ai-book-splitter && tar -czf backup-$(date +\%Y\%m\%d).tar.gz uploads/ output/ temp/
```

---

**Готово!** Ваше приложение AI Book Splitter & Designer развернуто и готово к использованию! 🎉
