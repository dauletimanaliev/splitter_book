# 🧠 AI Book Splitter & Designer

Система для автоматического разделения длинных PDF книг на смысловые разделы с красивым дизайном.

## 🎯 Основные возможности

- **Загрузка книг**: Поддержка PDF, DOCX, EPUB форматов
- **AI анализ структуры**: Автоматическое определение разделов по заголовкам или смыслу
- **Красивые дизайны**: 3 готовых шаблона оформления (Classic Islamic, Modern Minimal, Dark Gold)
- **Разделение на части**: Каждый раздел сохраняется как отдельный PDF файл
- **Сохранение текста**: Оригинальный текст не изменяется, применяется только визуальное оформление

## 🏗️ Архитектура

```
project/
├── backend/                # Python FastAPI сервер
│   ├── main.py             # Основное приложение
│   ├── parser.py           # Извлечение текста из файлов
│   ├── ai_structure.py     # AI анализ структуры
│   ├── designer.py         # Создание PDF с дизайном
│   ├── splitter.py         # Логика разделения
│   ├── designs/            # YAML шаблоны дизайна
│   └── requirements.txt    # Python зависимости
├── frontend/               # React приложение
│   ├── src/
│   │   ├── components/     # React компоненты
│   │   ├── services/       # API сервисы
│   │   └── App.js         # Главный компонент
│   └── package.json       # Node.js зависимости
└── output/                # Готовые PDF файлы
```

## 🚀 Быстрый старт

### 1. Установка Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Запуск Backend

```bash
cd backend
python main.py
```

Сервер будет доступен по адресу: http://localhost:8000

### 3. Установка Frontend

```bash
cd frontend
npm install
```

### 4. Запуск Frontend

```bash
cd frontend
npm start
```

Приложение будет доступно по адресу: http://localhost:3000

## 📖 Как использовать

1. **Загрузка книги**: Перетащите PDF, DOCX или EPUB файл в интерфейс
2. **Анализ структуры**: Выберите метод анализа (по заголовкам, по смыслу, автоматический)
3. **Выбор дизайна**: Выберите один из трех дизайнов
4. **Генерация PDF**: Нажмите "Начать генерацию" и дождитесь завершения
5. **Скачивание**: Скачайте готовые PDF файлы по разделам

## 🎨 Доступные дизайны

### Classic Islamic
- Традиционный исламский дизайн
- Золотые акценты
- Элегантная типографика
- Подходит для религиозных книг

### Modern Minimal
- Современный минималистичный стиль
- Чистые линии
- Профессиональный вид
- Подходит для деловых документов

### Dark Gold
- Премиальный темный дизайн
- Золотые элементы
- Высокий контраст
- Подходит для особых изданий

## 🔧 API Endpoints

### Основные маршруты

- `POST /upload` - Загрузка книги
- `POST /analyze` - Анализ структуры
- `POST /generate` - Генерация PDF
- `GET /designs` - Список дизайнов
- `GET /download/{book_id}/{filename}` - Скачивание PDF

### Пример запроса

```bash
# Загрузка файла
curl -X POST "http://localhost:8000/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@book.pdf"

# Анализ структуры
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{"book_id": "123", "split_mode": "by_headings"}'

# Генерация PDF
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{"book_id": "123", "design": "classic_islamic"}'
```

## 📁 Структура проекта

### Backend модули

- **main.py**: FastAPI приложение с маршрутами
- **parser.py**: Извлечение текста из PDF/DOCX/EPUB
- **ai_structure.py**: AI анализ для определения разделов
- **designer.py**: Создание PDF с применением дизайна
- **splitter.py**: Логика разделения на файлы

### Frontend компоненты

- **FileUpload**: Загрузка файлов с drag & drop
- **StructureAnalysis**: Анализ и предпросмотр структуры
- **DesignSelection**: Выбор дизайна с превью
- **PDFGeneration**: Генерация и скачивание PDF

## ⚙️ Конфигурация

### Переменные окружения

Создайте файл `.env` в папке backend:

```env
# API настройки
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# Пути к файлам
UPLOAD_DIR=uploads
OUTPUT_DIR=output
TEMP_DIR=temp

# Максимальный размер файла (в байтах)
MAX_FILE_SIZE=52428800  # 50MB

# Поддерживаемые форматы
ALLOWED_EXTENSIONS=pdf,docx,epub
```

### Настройка дизайнов

Дизайны настраиваются в YAML файлах в папке `backend/designs/`:

```yaml
fonts:
  body: "Times-Roman"
  title: "Times-Bold"
  body_size: 12
  title_size: 18

colors:
  text: "#2C2C2C"
  title: "#8B4513"
  heading: "#B8860B"

margins:
  left: 2.5
  right: 2.5
  top: 2.0
  bottom: 2.0
```

## 🐛 Устранение неполадок

### Частые проблемы

1. **Ошибка загрузки файла**
   - Проверьте размер файла (максимум 50MB)
   - Убедитесь, что формат поддерживается (PDF, DOCX, EPUB)

2. **Ошибка анализа структуры**
   - Проверьте, что в книге есть заголовки
   - Попробуйте другой метод анализа

3. **Ошибка генерации PDF**
   - Убедитесь, что выбран дизайн
   - Проверьте свободное место на диске

### Логи

Логи приложения сохраняются в:
- Backend: консоль и файлы в папке `logs/`
- Frontend: консоль браузера (F12)

## 🔮 Планы развития

- [ ] Поддержка больше форматов (TXT, RTF)
- [ ] Дополнительные дизайны
- [ ] Авторизация пользователей
- [ ] История проектов
- [ ] Batch обработка нескольких книг
- [ ] Интеграция с облачными хранилищами
- [ ] API для внешних приложений

## 📄 Лицензия

MIT License - см. файл LICENSE

## 🤝 Вклад в проект

1. Fork репозитория
2. Создайте feature branch (`git checkout -b feature/amazing-feature`)
3. Commit изменения (`git commit -m 'Add amazing feature'`)
4. Push в branch (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📞 Поддержка

Если у вас есть вопросы или проблемы:

1. Проверьте раздел "Устранение неполадок"
2. Создайте Issue в GitHub
3. Опишите проблему подробно с логами

---

**AI Book Splitter & Designer** - делаем книги красивыми и удобными для чтения! 📚✨
