import yaml
import os
from typing import Dict, Any, List, Tuple
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.colors import Color, black, white, HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping
import json

class PDFDesigner:
    """Класс для создания PDF с различными дизайнами"""
    
    def __init__(self):
        self.designs_dir = "designs"
        self.fonts_dir = "fonts"
        self._load_fonts()
    
    def _load_fonts(self):
        """Загружает шрифты для поддержки казахского языка"""
        try:
            # Пытаемся загрузить шрифты для казахского языка
            font_files = {
                'DejaVuSans': 'DejaVuSans.ttf',
                'DejaVuSerif': 'DejaVuSerif.ttf',
                'Times': 'times.ttf',
                'Arial': 'arial.ttf'
            }
            
            for font_name, font_file in font_files.items():
                font_path = os.path.join(self.fonts_dir, font_file)
                if os.path.exists(font_path):
                    pdfmetrics.registerFont(TTFont(font_name, font_path))
                else:
                    # Используем системные шрифты
                    try:
                        if font_name == 'DejaVuSans':
                            pdfmetrics.registerFont(TTFont('DejaVuSans', '/System/Library/Fonts/Arial.ttf'))
                        elif font_name == 'DejaVuSerif':
                            pdfmetrics.registerFont(TTFont('DejaVuSerif', '/System/Library/Fonts/Times.ttc'))
                    except:
                        pass  # Используем стандартные шрифты
                        
        except Exception as e:
            print(f"Предупреждение: Не удалось загрузить кастомные шрифты: {e}")
    
    def load_design(self, design_name: str) -> Dict[str, Any]:
        """Загружает дизайн из YAML файла"""
        design_file = os.path.join(self.designs_dir, f"{design_name}.yaml")
        
        if not os.path.exists(design_file):
            raise FileNotFoundError(f"Файл дизайна не найден: {design_file}")
        
        with open(design_file, 'r', encoding='utf-8') as f:
            design = yaml.safe_load(f)
        
        return design
    
    def create_pdf(self, 
                   text: str, 
                   title: str, 
                   design_name: str, 
                   output_path: str,
                   page_numbers: bool = True,
                   table_of_contents: bool = False) -> str:
        """
        Создает PDF с заданным дизайном
        
        Args:
            text: Текст для PDF
            title: Заголовок документа
            design_name: Название дизайна
            output_path: Путь для сохранения PDF
            page_numbers: Добавлять ли номера страниц
            table_of_contents: Добавлять ли оглавление
            
        Returns:
            Путь к созданному PDF файлу
        """
        try:
            # Загружаем дизайн
            design = self.load_design(design_name)
            
            # Создаем документ
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=design['margins']['right'] * cm,
                leftMargin=design['margins']['left'] * cm,
                topMargin=design['margins']['top'] * cm,
                bottomMargin=design['margins']['bottom'] * cm
            )
            
            # Создаем стили
            styles = self._create_styles(design)
            
            # Подготавливаем содержимое
            story = []
            
            # Добавляем заголовок
            if title:
                title_style = styles['Title']
                story.append(Paragraph(title, title_style))
                story.append(Spacer(1, 0.5 * inch))
            
            # Разбиваем текст на параграфы
            paragraphs = self._split_text_to_paragraphs(text)
            
            # Добавляем параграфы
            for para_text in paragraphs:
                if para_text.strip():
                    # Определяем стиль параграфа
                    if self._is_heading(para_text):
                        style = styles['Heading1']
                    else:
                        style = styles['Normal']
                    
                    story.append(Paragraph(para_text, style))
                    story.append(Spacer(1, 0.1 * inch))
            
            # Строим PDF
            doc.build(story, onFirstPage=self._add_page_number if page_numbers else None,
                     onLaterPages=self._add_page_number if page_numbers else None)
            
            return output_path
            
        except Exception as e:
            raise Exception(f"Ошибка при создании PDF: {str(e)}")
    
    def _create_styles(self, design: Dict[str, Any]) -> Dict[str, ParagraphStyle]:
        """Создает стили на основе дизайна"""
        styles = {}
        
        # Основной стиль
        styles['Normal'] = ParagraphStyle(
            'Normal',
            fontName=design['fonts']['body'],
            fontSize=design['fonts']['body_size'],
            leading=design['fonts']['body_leading'],
            textColor=HexColor(design['colors']['text']),
            alignment=TA_JUSTIFY,
            spaceAfter=design['spacing']['paragraph'],
            spaceBefore=0
        )
        
        # Заголовок документа
        styles['Title'] = ParagraphStyle(
            'Title',
            fontName=design['fonts']['title'],
            fontSize=design['fonts']['title_size'],
            leading=design['fonts']['title_leading'],
            textColor=HexColor(design['colors']['title']),
            alignment=TA_CENTER,
            spaceAfter=design['spacing']['title'],
            spaceBefore=0
        )
        
        # Заголовки разделов
        styles['Heading1'] = ParagraphStyle(
            'Heading1',
            fontName=design['fonts']['heading'],
            fontSize=design['fonts']['heading_size'],
            leading=design['fonts']['heading_leading'],
            textColor=HexColor(design['colors']['heading']),
            alignment=TA_LEFT,
            spaceAfter=design['spacing']['heading'],
            spaceBefore=design['spacing']['heading_before']
        )
        
        # Подзаголовки
        styles['Heading2'] = ParagraphStyle(
            'Heading2',
            fontName=design['fonts']['heading'],
            fontSize=design['fonts']['heading_size'] - 2,
            leading=design['fonts']['heading_leading'] - 2,
            textColor=HexColor(design['colors']['heading']),
            alignment=TA_LEFT,
            spaceAfter=design['spacing']['heading'] * 0.7,
            spaceBefore=design['spacing']['heading_before'] * 0.7
        )
        
        return styles
    
    def _split_text_to_paragraphs(self, text: str) -> List[str]:
        """Разбивает текст на параграфы"""
        # Разбиваем по двойным переносам строк
        paragraphs = text.split('\n\n')
        
        # Очищаем и фильтруем параграфы
        cleaned_paragraphs = []
        for para in paragraphs:
            para = para.strip()
            if para and len(para) > 10:  # Игнорируем очень короткие параграфы
                cleaned_paragraphs.append(para)
        
        return cleaned_paragraphs
    
    def _is_heading(self, text: str) -> bool:
        """Определяет, является ли текст заголовком"""
        # Простая эвристика для определения заголовков
        if len(text) < 100 and not text.endswith(('.', '!', '?', ':', ';')):
            # Проверяем на наличие цифр в начале (нумерованные заголовки)
            if text.strip() and text.strip()[0].isdigit():
                return True
            
            # Проверяем на заглавные буквы
            if len(text) > 5 and sum(1 for c in text if c.isupper()) / len(text) > 0.5:
                return True
        
        return False
    
    def _add_page_number(self, canvas, doc):
        """Добавляет номер страницы"""
        canvas.saveState()
        canvas.setFont('Helvetica', 9)
        canvas.drawRightString(
            A4[0] - 0.75 * inch,
            0.75 * inch,
            f"Страница {doc.page}"
        )
        canvas.restoreState()
    
    def create_section_pdf(self, 
                          section_data: Dict[str, Any], 
                          text_data: Dict[str, Any], 
                          design_name: str, 
                          output_dir: str) -> str:
        """
        Создает PDF для конкретного раздела
        
        Args:
            section_data: Данные о разделе
            text_data: Данные о тексте книги
            design_name: Название дизайна
            output_dir: Директория для сохранения
            
        Returns:
            Путь к созданному PDF файлу
        """
        try:
            # Извлекаем текст раздела
            section_text = self._extract_section_text(section_data, text_data)
            
            # Создаем безопасное имя файла
            safe_name = self._create_safe_filename(section_data['name'])
            filename = f"{section_data.get('index', 1):02d}_{safe_name}.pdf"
            output_path = os.path.join(output_dir, filename)
            
            # Создаем PDF
            self.create_pdf(
                text=section_text,
                title=section_data['name'],
                design_name=design_name,
                output_path=output_path,
                page_numbers=True
            )
            
            return output_path
            
        except Exception as e:
            raise Exception(f"Ошибка при создании PDF раздела: {str(e)}")
    
    def _extract_section_text(self, section_data: Dict[str, Any], text_data: Dict[str, Any]) -> str:
        """Извлекает текст раздела из данных книги"""
        start_page = section_data['start_page']
        end_page = section_data['end_page']
        
        text_parts = []
        for page in text_data.get('pages', []):
            if start_page <= page['page_number'] <= end_page:
                text_parts.append(page['text'])
        
        return '\n\n'.join(text_parts)
    
    def _create_safe_filename(self, name: str) -> str:
        """Создает безопасное имя файла"""
        import re
        
        # Заменяем небезопасные символы
        safe_name = re.sub(r'[^\w\s-]', '', name)
        safe_name = re.sub(r'[-\s]+', '_', safe_name)
        safe_name = safe_name.strip('_')
        
        # Ограничиваем длину
        if len(safe_name) > 50:
            safe_name = safe_name[:50]
        
        return safe_name
    
    def get_available_designs(self) -> List[Dict[str, str]]:
        """Возвращает список доступных дизайнов"""
        designs = []
        
        if os.path.exists(self.designs_dir):
            for file in os.listdir(self.designs_dir):
                if file.endswith(('.yaml', '.yml')):
                    design_name = os.path.splitext(file)[0]
                    designs.append({
                        'name': design_name,
                        'file': file,
                        'display_name': design_name.replace('_', ' ').title()
                    })
        
        return designs
    
    def validate_design(self, design: Dict[str, Any]) -> bool:
        """Проверяет корректность дизайна"""
        required_fields = [
            'fonts', 'colors', 'margins', 'spacing'
        ]
        
        for field in required_fields:
            if field not in design:
                return False
        
        # Проверяем подполя
        font_fields = ['body', 'title', 'heading', 'body_size', 'title_size', 'heading_size']
        for field in font_fields:
            if field not in design['fonts']:
                return False
        
        color_fields = ['text', 'title', 'heading']
        for field in color_fields:
            if field not in design['colors']:
                return False
        
        margin_fields = ['left', 'right', 'top', 'bottom']
        for field in margin_fields:
            if field not in design['margins']:
                return False
        
        return True
