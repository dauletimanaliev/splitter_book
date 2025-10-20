# 🔧 Настройка приложения

## Быстрый старт

### 1. Клонирование репозитория
```bash
git clone https://github.com/dauletimanaliev/splitter_book.git
cd splitter_book
```

### 2. Настройка Backend

```bash
cd backend

# Создайте виртуальное окружение
python3 -m venv venv

# Активируйте виртуальное окружение
# macOS/Linux:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# Установите зависимости
pip install -r requirements.txt

# Создайте файл .env с вашим API ключом
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env

# Запустите backend
python main.py
```

### 3. Настройка Frontend

```bash
cd frontend

# Установите зависимости
npm install

# Запустите frontend
npm start
```

### 4. Откройте приложение
- Frontend: http://localhost:3000/splitter_book
- Backend API: http://localhost:8000

## 🔑 Получение OpenAI API ключа

1. Перейдите на https://platform.openai.com/api-keys
2. Войдите в свой аккаунт OpenAI
3. Нажмите "Create new secret key"
4. Скопируйте ключ
5. Добавьте в файл `backend/.env`:
   ```
   OPENAI_API_KEY=sk-proj-your-key-here
   ```

## 📁 Структура проекта

```
splitter_book/
├── backend/                 # Python FastAPI сервер
│   ├── .env                # Ваши API ключи (НЕ загружается в git)
│   ├── config.py           # Конфигурация
│   ├── main.py             # Основное приложение
│   └── requirements.txt    # Python зависимости
├── frontend/               # React приложение
│   ├── src/               # Исходный код
│   └── package.json       # Node.js зависимости
└── README.md              # Документация
```

## ⚠️ Важные замечания

- **НЕ загружайте** файл `.env` в git - он содержит ваши API ключи
- **Создайте** файл `.env` в папке `backend/` с вашим OpenAI API ключом
- **Backend должен работать** на порту 8000
- **Frontend должен работать** на порту 3000

## 🐛 Решение проблем

### Backend не запускается
```bash
# Проверьте что виртуальное окружение активировано
source venv/bin/activate

# Установите зависимости
pip install -r requirements.txt

# Проверьте что .env файл создан
ls -la backend/.env
```

### Frontend не запускается
```bash
# Установите зависимости
npm install

# Очистите кэш
npm start -- --reset-cache
```

### API ошибки
- Убедитесь что backend запущен на http://localhost:8000
- Проверьте что OpenAI API ключ правильный
- Проверьте что файл `.env` создан в папке `backend/`

## 🚀 Готово!

После настройки вы сможете:
- Загружать PDF книги
- Выбирать количество разделов (5-50)
- Использовать AI анализ структуры
- Генерировать красивые PDF файлы
