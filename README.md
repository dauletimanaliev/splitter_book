# AI Book Splitter & Designer

🚀 **Демо приложения:** [https://dauletimanaliev.github.io/splitter_book/](https://dauletimanaliev.github.io/splitter_book/)

## Описание

AI Book Splitter & Designer - это веб-приложение для автоматического разделения длинных PDF книг на смысловые разделы с красивым дизайном.

## Основные возможности

- 📚 **Загрузка книг:** Поддержка PDF, DOCX, EPUB форматов
- 🤖 **AI анализ структуры:** Автоматическое определение разделов по заголовкам или смыслу
- 🎨 **Красивые дизайны:** 3 готовых шаблона оформления (Classic Islamic, Modern Minimal, Dark Gold)
- ✂️ **Разделение на части:** Каждый раздел сохраняется как отдельный PDF файл
- 💾 **Сохранение текста:** Оригинальный текст не изменяется, применяется только визуальное оформление
- 🔢 **Выбор разделов:** Пользователь может выбрать количество разделов от 5 до 50

## Архитектура

```
project/
├── backend/                 # Python FastAPI сервер
│   ├── main.py             # Основное приложение
│   ├── parser.py           # Извлечение текста из файлов
│   ├── ai_structure.py     # АІ анализ структуры
│   ├── designer.py         # Создание PDF с дизайном
│   ├── splitter.py         # Логика разделения
│   ├── designs/            # YAML шаблоны дизайна
│   └── requirements.txt    # Python зависимости
├── frontend/               # React приложение
│   ├── src/
│   │   ├── components/     # React компоненты
│   │   ├── services/       # АРІ сервисы
│   │   └── App.js          # Главный компонент
│   └── package.json        # Node.js зависимости
└── output/                 # Готовые PDF файлы
```

## Быстрый старт

### Локальная разработка

1. **Клонируйте репозиторий:**
   ```bash
   git clone https://github.com/dauletimanaliev/splitter_book.git
   cd splitter_book
   ```

2. **Запустите backend:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python main.py
   ```

3. **Запустите frontend:**
   ```bash
   cd frontend
   npm install
   npm start
   ```

4. **Откройте приложение:** http://localhost:3000

### Docker (Продакшен)

```bash
docker-compose up -d
```

## API Endpoints

- `POST /upload` - Загрузка файла
- `POST /analyze` - Анализ структуры книги
- `POST /generate` - Генерация PDF файлов
- `GET /designs` - Получение списка дизайнов

## Конфигурация

Создайте файл `backend/.env`:
```
OPENAI_API_KEY=your_openai_api_key_here
```

## Технологии

- **Frontend:** React.js, Styled Components
- **Backend:** Python, FastAPI, PyMuPDF, ReportLab
- **AI:** OpenAI GPT-3.5-turbo
- **Deployment:** Docker, Nginx, GitHub Pages

## Лицензия

MIT License

---

**Примечание:** Для полной функциональности требуется OpenAI API ключ.