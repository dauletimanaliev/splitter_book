import fitz  # PyMuPDF
import json
import os
from typing import Dict, List, Any
import re

class PDFParser:
    """Класс для извлечения текста из PDF файлов"""
    
    def __init__(self):
        self.supported_formats = ['.pdf', '.docx', '.epub']
    
    def extract_text(self, file_path: str) -> Dict[str, Any]:
        """
        Извлекает текст из PDF файла с сохранением информации о страницах
        
        Args:
            file_path: Путь к PDF файлу
            
        Returns:
            Словарь с извлеченным текстом и метаданными
        """
        try:
            file_extension = os.path.splitext(file_path)[1].lower()
            
            if file_extension == '.pdf':
                return self._extract_from_pdf(file_path)
            elif file_extension == '.docx':
                return self._extract_from_docx(file_path)
            elif file_extension == '.epub':
                return self._extract_from_epub(file_path)
            else:
                raise ValueError(f"Неподдерживаемый формат файла: {file_extension}")
                
        except Exception as e:
            raise Exception(f"Ошибка при извлечении текста: {str(e)}")
    
    def _extract_from_pdf(self, file_path: str) -> Dict[str, Any]:
        """Извлечение текста из PDF файла"""
        doc = fitz.open(file_path)
        
        # Получаем метаданные
        metadata = doc.metadata
        
        pages_data = []
        full_text = ""
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            
            # Извлекаем текст страницы
            page_text = page.get_text()
            
            # Очищаем текст от лишних символов
            cleaned_text = self._clean_text(page_text)
            
            pages_data.append({
                "page_number": page_num + 1,
                "text": cleaned_text,
                "char_count": len(cleaned_text),
                "word_count": len(cleaned_text.split())
            })
            
            full_text += cleaned_text + "\n"
        
        doc.close()
        
        return {
            "title": metadata.get("title", "Неизвестная книга"),
            "author": metadata.get("author", "Неизвестный автор"),
            "total_pages": len(pages_data),
            "total_characters": len(full_text),
            "total_words": len(full_text.split()),
            "pages": pages_data,
            "full_text": full_text
        }
    
    def _extract_from_docx(self, file_path: str) -> Dict[str, Any]:
        """Извлечение текста из DOCX файла"""
        try:
            from docx import Document
            
            doc = Document(file_path)
            
            # Получаем метаданные
            core_props = doc.core_properties
            
            pages_data = []
            full_text = ""
            
            # DOCX не имеет четкого разделения на страницы, 
            # поэтому создаем искусственное разделение по параграфам
            paragraphs = doc.paragraphs
            current_page = 1
            current_page_text = ""
            words_per_page = 300  # Примерное количество слов на страницу
            
            for para in paragraphs:
                para_text = para.text.strip()
                if para_text:
                    current_page_text += para_text + "\n"
                    full_text += para_text + "\n"
                    
                    # Если накопилось достаточно слов, создаем новую страницу
                    if len(current_page_text.split()) >= words_per_page:
                        pages_data.append({
                            "page_number": current_page,
                            "text": current_page_text.strip(),
                            "char_count": len(current_page_text),
                            "word_count": len(current_page_text.split())
                        })
                        current_page += 1
                        current_page_text = ""
            
            # Добавляем последнюю страницу, если есть текст
            if current_page_text.strip():
                pages_data.append({
                    "page_number": current_page,
                    "text": current_page_text.strip(),
                    "char_count": len(current_page_text),
                    "word_count": len(current_page_text.split())
                })
            
            return {
                "title": core_props.title or "Неизвестная книга",
                "author": core_props.author or "Неизвестный автор",
                "total_pages": len(pages_data),
                "total_characters": len(full_text),
                "total_words": len(full_text.split()),
                "pages": pages_data,
                "full_text": full_text
            }
            
        except ImportError:
            raise Exception("Для работы с DOCX файлами установите python-docx: pip install python-docx")
    
    def _extract_from_epub(self, file_path: str) -> Dict[str, Any]:
        """Извлечение текста из EPUB файла"""
        try:
            import zipfile
            import xml.etree.ElementTree as ET
            
            # EPUB - это ZIP архив
            with zipfile.ZipFile(file_path, 'r') as epub:
                # Читаем метаданные
                try:
                    metadata_xml = epub.read('META-INF/container.xml')
                    # Здесь можно добавить более сложную логику для извлечения метаданных
                except:
                    pass
                
                # Получаем список HTML файлов
                html_files = [f for f in epub.namelist() if f.endswith('.html') or f.endswith('.xhtml')]
                
                pages_data = []
                full_text = ""
                current_page = 1
                
                for html_file in html_files:
                    try:
                        html_content = epub.read(html_file).decode('utf-8')
                        
                        # Простое извлечение текста из HTML
                        text = self._extract_text_from_html(html_content)
                        
                        if text.strip():
                            pages_data.append({
                                "page_number": current_page,
                                "text": text.strip(),
                                "char_count": len(text),
                                "word_count": len(text.split())
                            })
                            full_text += text + "\n"
                            current_page += 1
                            
                    except Exception as e:
                        print(f"Ошибка при обработке файла {html_file}: {e}")
                        continue
            
            return {
                "title": "Неизвестная книга",
                "author": "Неизвестный автор",
                "total_pages": len(pages_data),
                "total_characters": len(full_text),
                "total_words": len(full_text.split()),
                "pages": pages_data,
                "full_text": full_text
            }
            
        except Exception as e:
            raise Exception(f"Ошибка при обработке EPUB файла: {str(e)}")
    
    def _extract_text_from_html(self, html_content: str) -> str:
        """Простое извлечение текста из HTML"""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            return soup.get_text()
        except ImportError:
            # Простое извлечение без BeautifulSoup
            import re
            # Удаляем HTML теги
            text = re.sub(r'<[^>]+>', '', html_content)
            # Удаляем лишние пробелы
            text = re.sub(r'\s+', ' ', text)
            return text.strip()
    
    def _clean_text(self, text: str) -> str:
        """Очистка текста от лишних символов и форматирования"""
        # Удаляем лишние пробелы и переносы строк
        text = re.sub(r'\s+', ' ', text)
        
        # Удаляем специальные символы, но оставляем пунктуацию
        text = re.sub(r'[^\w\s\.,!?;:()\-—«»""''№]', '', text)
        
        # Восстанавливаем переносы строк после точек
        text = re.sub(r'\.\s+', '.\n', text)
        
        return text.strip()
    
    def get_page_text(self, text_data: Dict[str, Any], page_number: int) -> str:
        """Получение текста конкретной страницы"""
        for page in text_data.get("pages", []):
            if page["page_number"] == page_number:
                return page["text"]
        return ""
    
    def get_text_range(self, text_data: Dict[str, Any], start_page: int, end_page: int) -> str:
        """Получение текста в диапазоне страниц"""
        text_parts = []
        for page in text_data.get("pages", []):
            if start_page <= page["page_number"] <= end_page:
                text_parts.append(page["text"])
        return "\n".join(text_parts)
