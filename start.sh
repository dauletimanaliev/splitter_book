#!/bin/bash

# AI Book Splitter & Designer - Startup Script
# Скрипт для запуска всего приложения

echo "🧠 AI Book Splitter & Designer - Запуск приложения"
echo "=================================================="

# Проверяем наличие Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не найден. Установите Python 3.8+ и попробуйте снова."
    exit 1
fi

# Проверяем наличие Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js не найден. Установите Node.js 16+ и попробуйте снова."
    exit 1
fi

# Создаем необходимые директории
echo "📁 Создание директорий..."
mkdir -p backend/uploads
mkdir -p backend/output
mkdir -p backend/temp
mkdir -p backend/logs
mkdir -p backend/fonts

# Устанавливаем Python зависимости
echo "🐍 Установка Python зависимостей..."
cd backend
if [ ! -d "venv" ]; then
    echo "Создание виртуального окружения..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt

# Запускаем backend в фоне
echo "🚀 Запуск backend сервера..."
python main.py &
BACKEND_PID=$!

# Ждем запуска backend
sleep 5

# Устанавливаем Node.js зависимости
echo "📦 Установка Node.js зависимостей..."
cd ../frontend
if [ ! -d "node_modules" ]; then
    npm install
fi

# Запускаем frontend
echo "🎨 Запуск frontend приложения..."
npm start &
FRONTEND_PID=$!

echo ""
echo "✅ Приложение запущено!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Для остановки нажмите Ctrl+C"

# Функция для корректного завершения
cleanup() {
    echo ""
    echo "🛑 Остановка приложения..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Приложение остановлено"
    exit 0
}

# Обработчик сигнала для корректного завершения
trap cleanup SIGINT SIGTERM

# Ждем завершения процессов
wait
