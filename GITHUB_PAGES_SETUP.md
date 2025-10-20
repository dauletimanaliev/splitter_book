# 🔧 Настройка GitHub Pages

## Проблема
GitHub Pages показывает README.md вместо приложения.

## Решение

### 1. Настройте GitHub Pages в репозитории:

1. Перейдите в ваш репозиторий: https://github.com/dauletimanaliev/splitter_book
2. Нажмите **Settings** (вкладка справа)
3. Прокрутите вниз до раздела **Pages** (в левом меню)
4. В разделе **Source** выберите **Deploy from a branch**
5. В **Branch** выберите **gh-pages**
6. В **Folder** выберите **/ (root)**
7. Нажмите **Save**

### 2. Подождите 5-10 минут
GitHub Pages может потребовать время для обновления.

### 3. Проверьте сайт
Откройте: https://dauletimanaliev.github.io/splitter_book/

## Что исправлено:

✅ **Удалены лишние файлы** из ветки gh-pages
✅ **Добавлен .nojekyll** файл
✅ **Обновлен README** с правильными ссылками
✅ **Оставлены только файлы фронтенда**

## Структура gh-pages ветки:

```
gh-pages/
├── .nojekyll          # Отключает Jekyll
├── index.html         # Главная страница приложения
├── manifest.json      # Манифест PWA
├── asset-manifest.json # Манифест ресурсов
├── static/            # Статические файлы
│   ├── css/          # CSS стили
│   └── js/           # JavaScript файлы
└── README.md         # Описание с ссылкой на приложение
```

## Если не работает:

1. **Очистите кэш браузера** (Ctrl+F5)
2. **Проверьте URL** - должен быть `dauletimanaliev.github.io/splitter_book/`
3. **Подождите 10-15 минут** - GitHub Pages может обновляться медленно
4. **Проверьте настройки** - убедитесь что выбрана ветка gh-pages

## Альтернативный способ:

Если GitHub Pages не работает, можно использовать:
- **Netlify** - перетащите папку `frontend/build` на netlify.com
- **Vercel** - подключите репозиторий к vercel.com
- **GitHub Codespaces** - запустите локально в браузере

---

**После настройки GitHub Pages приложение будет доступно по ссылке!** 🚀
