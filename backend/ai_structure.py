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
        ]
        
        self.section_keywords = [
            'кіріспе', 'қорытынды', 'қорытынды сөз', 'қорытынды сөздер',
            'қорытынды бөлім', 'қорытынды тарау', 'глава', 'бөлім', 'тарау',
            'введение', 'заключение', 'вступление', 'заключительное слово'
        ]
    
    def analyze_structure(self, text_data: Dict[str, Any], split_mode: str = "by_headings") -> Dict[str, Any]:
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
                return self._analyze_with_ai(text_data)
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
        
        line_lower = line.lower().strip()
        
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
        """Проверяет заголовок по стилистическим признакам"""
        # Короткие строки (менее 50 символов)
        if len(line) < 50:
            # Строки, состоящие в основном из заглавных букв
            if len(line) > 5 and sum(1 for c in line if c.isupper()) / len(line) > 0.7:
                return True
            
            # Строки без знаков препинания в конце
            if not line.endswith(('.', '!', '?', ':', ';')):
                return True
        
        return False
    
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
            # Подготавливаем текст для анализа (первые 3000 символов)
            pages = text_data.get("pages", [])
            sample_text = ""
            
            for page in pages[:5]:  # Берем первые 5 страниц для анализа
                sample_text += page["text"] + "\n"
                if len(sample_text) > 3000:
                    break
            
            # Создаем промпт для OpenAI
            prompt = f"""
Проанализируй структуру этой книги и определи основные разделы. Текст книги:

{sample_text}

Пожалуйста, определи:
1. Название книги
2. Автора (если указан)
3. Основные разделы/главы с их названиями и номерами страниц

Ответь в формате JSON:
{{
    "title": "Название книги",
    "author": "Автор",
    "sections": [
        {{
            "name": "Название раздела",
            "type": "introduction|chapter|conclusion",
            "start_page": 1,
            "end_page": 10,
            "level": 1
        }}
    ]
}}

Если не можешь определить точные номера страниц, используй примерные значения.
"""
            
            # Отправляем запрос к OpenAI
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Ты эксперт по анализу структуры книг. Анализируй текст и определяй разделы."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            # Парсим ответ
            ai_response = response.choices[0].message.content.strip()
            
            # Извлекаем JSON из ответа
            json_start = ai_response.find('{')
            json_end = ai_response.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_str = ai_response[json_start:json_end]
                structure = json.loads(json_str)
                
                # Добавляем недостающие поля
                structure["total_pages"] = text_data.get("total_pages", 0)
                structure["analysis_method"] = "ai_analysis"
                
                return structure
            else:
                raise Exception("Не удалось извлечь JSON из ответа AI")
                
        except Exception as e:
            print(f"Ошибка AI анализа: {str(e)}")
            # Fallback к обычному анализу
            return self._analyze_by_headings(text_data)
