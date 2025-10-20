import json
import re
from typing import Dict, List, Any, Optional
import yaml
import os
import openai
from config import OPENAI_API_KEY

class AIStructureAnalyzer:
    """Класс для анализа структуры книги с помощью AI и определения разделов"""
    
    def __init__(self):
        # Настраиваем OpenAI API
        openai.api_key = OPENAI_API_KEY
        
        self.heading_patterns = [
            # Казахские заголовки
            r'^кіріспе\s*$',
            r'^қорытынды\s*$',
            r'^қорытынды\s+сөз\s*$',
            r'^қорытынды\s+сөздер\s*$',
            r'^қорытынды\s+бөлім\s*$',
            r'^қорытынды\s+тарау\s*$',
            r'^алғы\s+сөз\s*$',
            
            # Нумерованные заголовки
            r'^\d+\.\s+.*$',
            r'^\d+\s+.*$',
            r'^глава\s+\d+.*$',
            r'^бөлім\s+\d+.*$',
            r'^тарау\s+\d+.*$',
            
            # Римские цифры
            r'^[IVX]+\.\s+.*$',
            r'^[IVX]+\s+.*$',
            
            # Заголовки с подчеркиванием
            r'^[А-ЯЁ\w\s]+$',  # Заголовки заглавными буквами
            
            # Заголовки с казахскими словами (как на картинке)
            r'.*ата\s+ана.*',
            r'.*неке.*',
            r'.*хадис.*',
            r'.*пайғамбар.*',
            r'.*ислам.*',
            r'.*құран.*',
        ]
        
        self.section_keywords = [
            'кіріспе', 'қорытынды', 'қорытынды сөз', 'қорытынды сөздер',
            'қорытынды бөлім', 'қорытынды тарау', 'глава', 'бөлім', 'тарау',
            'введение', 'заключение', 'вступление', 'заключительное слово'
        ]
    
    def analyze_structure(self, text_data: Dict[str, Any], split_mode: str = "by_headings", num_sections: int = 5) -> Dict[str, Any]:
        """
        Анализирует структуру книги и определяет разделы
        
        Args:
            text_data: Данные о тексте книги
            split_mode: Режим разделения ("by_headings", "by_meaning", "auto", "ai_analysis")
            
        Returns:
            Словарь со структурой книги
        """
        try:
            if split_mode == "by_headings":
                return self._analyze_by_headings(text_data)
            elif split_mode == "by_meaning":
                return self._analyze_by_meaning(text_data)
            elif split_mode == "ai_analysis":
                # AI анализ отключен, используем улучшенный анализ по заголовкам
                return self._analyze_by_headings_improved(text_data)
            elif split_mode == "auto":
                # Пробуем сначала AI анализ, потом по заголовкам, если не получается - по смыслу
                try:
                    structure = self._analyze_with_ai(text_data)
                    if len(structure.get("sections", [])) >= 2:
                        return structure
                except:
                    pass
                
                structure = self._analyze_by_headings(text_data)
                if len(structure.get("sections", [])) < 2:
                    structure = self._analyze_by_meaning(text_data)
                return structure
            else:
                raise ValueError(f"Неподдерживаемый режим разделения: {split_mode}")
                
        except Exception as e:
            raise Exception(f"Ошибка при анализе структуры: {str(e)}")
    
    def _analyze_by_headings(self, text_data: Dict[str, Any]) -> Dict[str, Any]:
        """Анализ структуры по заголовкам"""
        pages = text_data.get("pages", [])
        sections = []
        
        # Ищем заголовки на каждой странице
        for page in pages:
            page_text = page["text"]
            page_number = page["page_number"]
            
            # Разбиваем текст на строки
            lines = page_text.split('\n')
            
            for line in lines:
                line = line.strip()
                if self._is_heading(line):
                    # Определяем тип заголовка
                    heading_type = self._classify_heading(line)
                    
                    sections.append({
                        "name": line,
                        "type": heading_type,
                        "start_page": page_number,
                        "end_page": None,  # Будет определено позже
                        "level": self._get_heading_level(line)
                    })
        
        # Определяем конец каждого раздела
        sections = self._determine_section_endings(sections, len(pages))
        
        # Если разделов мало, пробуем более агрессивный поиск
        if len(sections) < 2:
            sections = self._aggressive_heading_search(pages)
        
        return {
            "title": text_data.get("title", "Неизвестная книга"),
            "author": text_data.get("author", "Неизвестный автор"),
            "total_pages": text_data.get("total_pages", 0),
            "sections": sections,
            "analysis_method": "by_headings"
        }
    
    def _analyze_by_meaning(self, text_data: Dict[str, Any]) -> Dict[str, Any]:
        """Анализ структуры по смыслу (разделение на равные части)"""
        total_pages = text_data.get("total_pages", 1)
        
        # Определяем оптимальное количество разделов
        optimal_sections = self._calculate_optimal_sections(total_pages)
        
        # Разделяем на равные части
        pages_per_section = total_pages // optimal_sections
        remainder = total_pages % optimal_sections
        
        sections = []
        current_page = 1
        
        for i in range(optimal_sections):
            # Добавляем остаток к первым разделам
            section_pages = pages_per_section + (1 if i < remainder else 0)
            
            end_page = min(current_page + section_pages - 1, total_pages)
            
            # Генерируем название раздела
            section_name = self._generate_section_name(i, optimal_sections)
            
            sections.append({
                "name": section_name,
                "type": "auto_generated",
                "start_page": current_page,
                "end_page": end_page,
                "level": 1
            })
            
            current_page = end_page + 1
        
        return {
            "title": text_data.get("title", "Неизвестная книга"),
            "author": text_data.get("author", "Неизвестный автор"),
            "total_pages": total_pages,
            "sections": sections,
            "analysis_method": "by_meaning"
        }
    
    def _is_heading(self, line: str) -> bool:
        """Проверяет, является ли строка заголовком"""
        if not line or len(line.strip()) < 3:
            return False
        
        line = line.strip()
        
        # Исключаем длинные тексты (больше 30 символов - это не заголовок)
        if len(line) > 30:
            return False
        
        # Исключаем тексты с множественными пробелами (это абзацы)
        if '  ' in line or '\t' in line:
            return False
        
        # Исключаем тексты, которые заканчиваются точкой (это предложения)
        if line.endswith('.') and not line.endswith('...'):
            return False
        
        # Исключаем тексты с цифрами в середине (это сноски или номера)
        if re.search(r'\d+', line) and len(line) > 10:
            return False
        
        # Исключаем тексты, которые начинаются с маленькой буквы (это продолжение предложения)
        if line[0].islower():
            return False
        
        # Исключаем тексты с запятыми, двоеточиями (это предложения)
        if ',' in line or ':' in line or ';' in line:
            return False
        
        # Исключаем тексты с кавычками (это цитаты)
        if '"' in line or "'" in line or '«' in line or '»' in line:
            return False
        
        # Исключаем тексты с вопросительными знаками (это вопросы)
        if '?' in line:
            return False
        
        # Исключаем тексты с восклицательными знаками (это восклицания)
        if '!' in line:
            return False
        
        line_lower = line.lower()
        
        # Проверяем по ключевым словам
        for keyword in self.section_keywords:
            if keyword in line_lower:
                return True
        
        # Проверяем по паттернам
        for pattern in self.heading_patterns:
            if re.match(pattern, line, re.IGNORECASE):
                return True
        
        # Проверяем, является ли строка заголовком по стилю
        if self._is_heading_by_style(line):
            return True
        
        return False
    
    def _is_heading_by_style(self, line: str) -> bool:
        """Проверяет заголовок по стилистическим признакам - ОЧЕНЬ СТРОГИЕ ПРАВИЛА"""
        # Только очень короткие строки (менее 25 символов)
        if len(line) >= 25:
            return False
        
        # Строки, состоящие в основном из заглавных букв (минимум 5 символов)
        if len(line) >= 5 and sum(1 for c in line if c.isupper()) / len(line) > 0.8:
            return True
        
        # ОЧЕНЬ СТРОГИЕ ПРАВИЛА для обычных заголовков:
        # 1. Начинается с заглавной буквы
        # 2. Длина от 3 до 20 символов
        # 3. Только буквы и пробелы (БЕЗ цифр и знаков препинания)
        # 4. НЕ заканчивается знаками препинания
        # 5. НЕ содержит вопросительных или восклицательных знаков
        if (line[0].isupper() and 
            len(line) >= 3 and 
            len(line) <= 20 and
            re.match(r'^[А-ЯЁа-яё\s]+$', line) and
            not line.endswith(('.', '!', '?', ':', ';', ',', '"', "'", '«', '»')) and
            '?' not in line and
            '!' not in line and
            ':' not in line and
            ';' not in line and
            ',' not in line):
            return True
        
        return False
    
    def _create_reasonable_structure_from_pages(self, pages: List[Dict], num_sections: int = 5) -> List[Dict]:
        """Создает разумную структуру на основе количества страниц - НАЧИНАЯ С 1-Й СТРАНИЦЫ"""
        total_pages = len(pages)
        
        # Используем переданное количество разделов, но ограничиваем разумными пределами
        num_sections = max(2, min(num_sections, total_pages // 5))  # Минимум 2, максимум 1 раздел на 5 страниц
        
        sections = []
        pages_per_section = total_pages // num_sections
        remainder = total_pages % num_sections
        
        # ВСЕГДА начинаем с 1-й страницы
        current_page = 1
        
        for i in range(num_sections):
            section_pages = pages_per_section + (1 if i < remainder else 0)
            end_page = min(current_page + section_pages - 1, total_pages)
            
            # Создаем осмысленные названия разделов
            if i == 0:
                section_name = "Кіріспе"
            elif i == num_sections - 1:
                section_name = "Қорытынды"
            else:
                section_name = f"Бөлім {i}"
            
            sections.append({
                "name": section_name,
                "type": "section",
                "start_page": current_page,
                "end_page": end_page,
                "level": 1
            })
            
            current_page = end_page + 1
        
        print(f"Создана разумная структура: {num_sections} разделов, начиная с 1-й страницы")
        return sections
    
    def _are_sections_quality_poor(self, sections: List[Dict]) -> bool:
        """Проверяет, являются ли разделы некачественными"""
        if not sections:
            return True
        
        # Проверяем, есть ли разделы с очень маленьким количеством страниц
        small_sections = 0
        for section in sections:
            start_page = section.get("start_page", 1)
            end_page = section.get("end_page", 1)
            pages_count = end_page - start_page + 1
            
            if pages_count < 5:  # Меньше 5 страниц - плохое качество
                small_sections += 1
        
        # Если больше половины разделов маленькие - плохое качество
        return small_sections > len(sections) / 2
    
    def _classify_heading(self, heading: str) -> str:
        """Классифицирует тип заголовка"""
        heading_lower = heading.lower()
        
        if 'кіріспе' in heading_lower:
            return 'introduction'
        elif 'қорытынды' in heading_lower:
            return 'conclusion'
        elif re.match(r'^\d+\.', heading):
            return 'numbered_section'
        elif re.match(r'^[IVX]+\.', heading):
            return 'roman_section'
        else:
            return 'regular_section'
    
    def _get_heading_level(self, heading: str) -> int:
        """Определяет уровень заголовка"""
        if re.match(r'^\d+\.', heading):
            return 1
        elif re.match(r'^\d+\.\d+', heading):
            return 2
        elif re.match(r'^\d+\.\d+\.\d+', heading):
            return 3
        else:
            return 1
    
    def _determine_section_endings(self, sections: List[Dict], total_pages: int) -> List[Dict]:
        """Определяет конец каждого раздела"""
        for i, section in enumerate(sections):
            if i < len(sections) - 1:
                # Конец раздела - страница перед следующим разделом
                section["end_page"] = sections[i + 1]["start_page"] - 1
            else:
                # Последний раздел до конца книги
                section["end_page"] = total_pages
        
        return sections
    
    def _aggressive_heading_search(self, pages: List[Dict]) -> List[Dict]:
        """Более агрессивный поиск заголовков"""
        sections = []
        
        for page in pages:
            page_text = page["text"]
            page_number = page["page_number"]
            
            # Ищем строки, которые могут быть заголовками
            lines = page_text.split('\n')
            
            for line in lines:
                line = line.strip()
                
                # Более мягкие критерии для заголовков
                if (len(line) > 5 and len(line) < 100 and 
                    not line.endswith(('.', '!', '?', ':', ';')) and
                    not line.startswith((' ', '\t'))):
                    
                    # Проверяем, не является ли это обычным текстом
                    if not self._is_regular_text(line):
                        sections.append({
                            "name": line,
                            "type": "potential_heading",
                            "start_page": page_number,
                            "end_page": None,
                            "level": 1
                        })
        
        # Определяем концы разделов
        sections = self._determine_section_endings(sections, len(pages))
        
        return sections
    
    def _is_regular_text(self, line: str) -> bool:
        """Проверяет, является ли строка обычным текстом"""
        # Строки с множественными пробелами
        if '  ' in line:
            return True
        
        # Строки, заканчивающиеся на знаки препинания
        if line.endswith(('.', '!', '?', ':', ';', ',')):
            return True
        
        # Строки с маленькими буквами в начале
        if line and line[0].islower():
            return True
        
        return False
    
    def _calculate_optimal_sections(self, total_pages: int) -> int:
        """Вычисляет оптимальное количество разделов"""
        if total_pages <= 50:
            return 3
        elif total_pages <= 100:
            return 5
        elif total_pages <= 200:
            return 7
        elif total_pages <= 300:
            return 10
        else:
            return min(15, total_pages // 20)
    
    def _generate_section_name(self, index: int, total_sections: int) -> str:
        """Генерирует название для автоматически созданного раздела"""
        if index == 0:
            return "Кіріспе"
        elif index == total_sections - 1:
            return "Қорытынды"
        else:
            return f"{index}. Бөлім"
    
    def save_structure(self, structure: Dict[str, Any], file_path: str):
        """Сохраняет структуру в файл"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(structure, f, ensure_ascii=False, indent=2)
    
    def load_structure(self, file_path: str) -> Dict[str, Any]:
        """Загружает структуру из файла"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _analyze_with_ai(self, text_data: Dict[str, Any]) -> Dict[str, Any]:
        """Анализ структуры с помощью OpenAI"""
        try:
            # Подготавливаем текст для анализа (больше текста для лучшего анализа)
            pages = text_data.get("pages", [])
            total_pages = len(pages)
            sample_text = ""
            
            # Берем больше страниц для анализа, но ограничиваем размер
            for page in pages[:10]:  # Увеличиваем до 10 страниц
                sample_text += f"Страница {page['page_number']}: {page['text']}\n"
                if len(sample_text) > 5000:  # Увеличиваем лимит
                    break
            
            # Создаем улучшенный промпт для OpenAI
            prompt = f"""
Проанализируй структуру этой книги и найди ОСНОВНЫЕ ТЕМАТИЧЕСКИЕ РАЗДЕЛЫ. Текст книги:

{sample_text}

ЗАДАЧА: Найди ОСНОВНЫЕ ТЕМАТИЧЕСКИЕ РАЗДЕЛЫ этой конкретной книги.

КРИТИЧЕСКИ ВАЖНО:
- Найди ОСНОВНЫЕ ТЕМАТИЧЕСКИЕ РАЗДЕЛЫ этой книги (3-8 разделов максимум)
- ИГНОРИРУЙ все мелкие подзаголовки, нумерацию, сноски, цитаты
- Каждый тематический раздел = новый PDF файл
- Раздел включает ВСЕ страницы от этого раздела до следующего тематического раздела
- Создавай ОЧЕНЬ МАЛО разделов (3-8 максимум)
- Каждый раздел должен содержать МНОГО страниц (20-100 страниц)

НАЙДИ РЕАЛЬНЫЕ ТЕМАТИЧЕСКИЕ РАЗДЕЛЫ этой книги, например:
- "Алғы сөз" (если есть)
- "Күнәдан пәк Пайғамбар" (если есть такая тема)
- "Туыстық байланыстар" (если есть такая тема)
- "Кіріспе" (если есть)
- "Қорытынды" (если есть)

Пожалуйста, определи:
1. Название книги
2. Автора (если указан)
3. РЕАЛЬНЫЕ тематические разделы этой книги

Ответь в формате JSON:
{{
    "title": "Название книги",
    "author": "Автор",
    "sections": [
        {{
            "name": "Точное название первого тематического раздела",
            "type": "section",
            "start_page": 1,
            "end_page": 20,
            "level": 1
        }},
        {{
            "name": "Точное название второго тематического раздела",
            "type": "section",
            "start_page": 21,
            "end_page": 50,
            "level": 1
        }}
    ]
}}

Правила:
- Максимум 8 разделов
- Каждый раздел минимум 20 страниц
- Всего страниц в книге: {total_pages}
- Найди РЕАЛЬНЫЕ тематические разделы этой конкретной книги
- НЕ придумывай стандартные названия, найди то что ЕСТЬ в книге
"""
            
            # Отправляем запрос к OpenAI
            print(f"Отправляем запрос к OpenAI с {len(sample_text)} символами текста...")
            client = openai.OpenAI(api_key=OPENAI_API_KEY)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Ты эксперт по анализу структуры книг. Анализируй текст и определяй разделы."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.1
            )
            
            # Парсим ответ
            ai_response = response.choices[0].message.content.strip()
            print(f"Ответ от AI: {ai_response[:500]}...")
            
            # Извлекаем JSON из ответа
            json_start = ai_response.find('{')
            json_end = ai_response.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_str = ai_response[json_start:json_end]
                print(f"Извлеченный JSON: {json_str}")
                structure = json.loads(json_str)
                
                print(f"Структура от AI: {len(structure.get('sections', []))} разделов")
                
                # Валидируем и исправляем структуру
                structure = self._validate_and_fix_ai_structure(structure, total_pages)
                
                print(f"После валидации: {len(structure.get('sections', []))} разделов")
                
                # Добавляем недостающие поля
                structure["total_pages"] = total_pages
                structure["analysis_method"] = "ai_analysis"
                
                return structure
            else:
                print(f"Не удалось найти JSON в ответе: {ai_response}")
                raise Exception("Не удалось извлечь JSON из ответа AI")
                
        except Exception as e:
            print(f"Ошибка AI анализа: {str(e)}")
            # Fallback к улучшенному анализу по заголовкам
            return self._analyze_by_headings_improved(text_data)
    
    def _validate_and_fix_ai_structure(self, structure: Dict[str, Any], total_pages: int) -> Dict[str, Any]:
        """Валидирует и исправляет структуру, полученную от AI"""
        sections = structure.get("sections", [])
        
        if not sections:
            # Если нет разделов, создаем простую структуру
            return {
                "title": structure.get("title", "Неизвестная книга"),
                "author": structure.get("author", "Неизвестный автор"),
                "sections": [
                    {
                        "name": "Кіріспе",
                        "type": "introduction",
                        "start_page": 1,
                        "end_page": max(1, total_pages // 4),
                        "level": 1
                    },
                    {
                        "name": "Негізгі бөлім",
                        "type": "chapter",
                        "start_page": max(2, total_pages // 4 + 1),
                        "end_page": max(3, total_pages * 3 // 4),
                        "level": 1
                    },
                    {
                        "name": "Қорытынды",
                        "type": "conclusion",
                        "start_page": max(4, total_pages * 3 // 4 + 1),
                        "end_page": total_pages,
                        "level": 1
                    }
                ]
            }
        
        # Фильтруем и исправляем разделы
        valid_sections = []
        
        # Ограничиваем количество разделов (максимум 8)
        max_sections = min(8, total_pages // 20)  # Один раздел на каждые 20 страниц
        sections = sections[:max_sections]
        
        for i, section in enumerate(sections):
            start_page = section.get("start_page", 1)
            end_page = section.get("end_page", total_pages)
            
            # Исправляем неправильные диапазоны
            if start_page > end_page:
                start_page, end_page = end_page, start_page
            
            # Убеждаемся, что страницы в допустимых пределах
            start_page = max(1, min(start_page, total_pages))
            end_page = max(start_page, min(end_page, total_pages))
            
            # Проверяем, что раздел содержит достаточно страниц (минимум 10 страниц)
            if end_page - start_page + 1 >= 10:
                valid_sections.append({
                    "name": section.get("name", f"Бөлім {i+1}"),
                    "type": section.get("type", "main_section"),
                    "start_page": start_page,
                    "end_page": end_page,
                    "level": section.get("level", 1)
                })
        
        # Если нет валидных разделов, создаем разумную структуру на основе количества страниц
        if not valid_sections:
            return self._create_reasonable_structure(structure, total_pages)
        
        # Убеждаемся, что все страницы покрыты
        valid_sections = self._ensure_complete_coverage(valid_sections, total_pages)
        
        return {
            "title": structure.get("title", "Неизвестная книга"),
            "author": structure.get("author", "Неизвестный автор"),
            "sections": valid_sections
        }
    
    def _ensure_complete_coverage(self, sections: List[Dict], total_pages: int) -> List[Dict]:
        """Убеждается, что все страницы книги покрыты разделами"""
        if not sections:
            return sections
        
        # Сортируем разделы по start_page
        sections.sort(key=lambda x: x["start_page"])
        
        # Проверяем покрытие
        covered_pages = set()
        for section in sections:
            for page in range(section["start_page"], section["end_page"] + 1):
                covered_pages.add(page)
        
        # Добавляем недостающие страницы
        missing_pages = []
        for page in range(1, total_pages + 1):
            if page not in covered_pages:
                missing_pages.append(page)
        
        # Если есть пропущенные страницы, добавляем их к последнему разделу
        if missing_pages and sections:
            last_section = sections[-1]
            last_section["end_page"] = max(last_section["end_page"], max(missing_pages))
        
        return sections
    
    def _create_reasonable_structure(self, structure: Dict[str, Any], total_pages: int) -> Dict[str, Any]:
        """Создает разумную структуру на основе количества страниц"""
        # Определяем количество разделов на основе размера книги (меньше разделов)
        if total_pages <= 100:
            num_sections = 3
        elif total_pages <= 200:
            num_sections = 4
        elif total_pages <= 300:
            num_sections = 5
        elif total_pages <= 400:
            num_sections = 6
        else:
            num_sections = min(8, total_pages // 60)  # Максимум 8 разделов, один на каждые 60 страниц
        
        # Создаем разделы
        sections = []
        pages_per_section = total_pages // num_sections
        remainder = total_pages % num_sections
        
        current_page = 1
        
        for i in range(num_sections):
            # Добавляем остаток к первым разделам
            section_pages = pages_per_section + (1 if i < remainder else 0)
            end_page = min(current_page + section_pages - 1, total_pages)
            
            # Генерируем название раздела
            if i == 0:
                section_name = "Кіріспе бөлімі"
            elif i == num_sections - 1:
                section_name = "Қорытынды бөлімі"
            else:
                section_name = f"{i}. Негізгі бөлім"
            
            sections.append({
                "name": section_name,
                "type": "introduction" if i == 0 else ("conclusion" if i == num_sections - 1 else "chapter"),
                "start_page": current_page,
                "end_page": end_page,
                "level": 1
            })
            
            current_page = end_page + 1
        
        return {
            "title": structure.get("title", "Неизвестная книга"),
            "author": structure.get("author", "Неизвестный автор"),
            "sections": sections
        }
    
    def _analyze_by_headings_improved(self, text_data: Dict[str, Any]) -> Dict[str, Any]:
        """Улучшенный анализ структуры по заголовкам"""
        pages = text_data.get("pages", [])
        sections = []
        
        print(f"Анализируем {len(pages)} страниц...")
        
        # Ищем заголовки на каждой странице
        for page in pages:
            page_text = page["text"]
            page_number = page["page_number"]
            
            # Разбиваем текст на строки
            lines = page_text.split('\n')
            
            for line in lines:
                line = line.strip()
                if self._is_heading(line):
                    print(f"Найден заголовок на странице {page_number}: {line}")
                    
                    # Определяем тип заголовка
                    heading_type = self._classify_heading(line)
                    
                    sections.append({
                        "name": line,
                        "type": heading_type,
                        "start_page": page_number,
                        "end_page": None,  # Будет определено позже
                        "level": self._get_heading_level(line)
                    })
        
        print(f"Найдено {len(sections)} заголовков")
        
        # Определяем конец каждого раздела
        sections = self._determine_section_endings(sections, len(pages))
        
        # ВСЕГДА создаем разумную структуру с 1-й страницы
        print(f"Создаем разумную структуру с 1-й страницы ({num_sections} разделов)...")
        sections = self._create_reasonable_structure_from_pages(pages, num_sections)
        
        print(f"Итого разделов: {len(sections)}")
        
        return {
            "title": text_data.get("title", "Неизвестная книга"),
            "author": text_data.get("author", "Неизвестный автор"),
            "total_pages": text_data.get("total_pages", len(pages)),
            "sections": sections,
            "analysis_method": "by_headings_improved"
        }
