import os
import json
from typing import Dict, List, Any, Optional
from designer import PDFDesigner

class PDFSplitter:
    """Класс для разделения PDF на разделы и генерации отдельных файлов"""
    
    def __init__(self):
        self.designer = PDFDesigner()
        self.output_dir = "output"
    
    def split_and_generate(self, 
                          book_id: str, 
                          text_data: Dict[str, Any], 
                          structure: Dict[str, Any], 
                          design: str) -> List[Dict[str, str]]:
        """
        Разделяет книгу на разделы и генерирует отдельные PDF файлы
        
        Args:
            book_id: ID книги
            text_data: Данные о тексте книги
            structure: Структура разделов
            design: Название дизайна
            
        Returns:
            Список созданных файлов с метаданными
        """
        try:
            # Создаем директорию для выходных файлов
            book_output_dir = os.path.join(self.output_dir, book_id)
            os.makedirs(book_output_dir, exist_ok=True)
            
            sections = structure.get('sections', [])
            if not sections:
                raise ValueError("Не найдены разделы для разделения")
            
            generated_files = []
            
            # Генерируем PDF для каждого раздела
            for index, section in enumerate(sections, 1):
                try:
                    # Добавляем индекс к данным раздела
                    section_with_index = section.copy()
                    section_with_index['index'] = index
                    
                    # Создаем PDF раздела
                    pdf_path = self.designer.create_section_pdf(
                        section_data=section_with_index,
                        text_data=text_data,
                        design_name=design,
                        output_dir=book_output_dir
                    )
                    
                    # Получаем только имя файла для API ответа
                    filename = os.path.basename(pdf_path)
                    
                    generated_files.append({
                        'title': section['name'],
                        'file': f"output/{book_id}/{filename}",
                        'filename': filename,
                        'start_page': section['start_page'],
                        'end_page': section['end_page'],
                        'pages_count': section['end_page'] - section['start_page'] + 1,
                        'index': index
                    })
                    
                except Exception as e:
                    print(f"Ошибка при создании PDF для раздела '{section['name']}': {e}")
                    continue
            
            if not generated_files:
                raise Exception("Не удалось создать ни одного PDF файла")
            
            # Сохраняем метаданные о созданных файлах
            metadata = {
                'book_id': book_id,
                'book_title': structure.get('title', 'Неизвестная книга'),
                'book_author': structure.get('author', 'Неизвестный автор'),
                'design_used': design,
                'total_sections': len(generated_files),
                'generated_files': generated_files,
                'generation_timestamp': self._get_timestamp()
            }
            
            metadata_file = os.path.join(book_output_dir, 'metadata.json')
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            return generated_files
            
        except Exception as e:
            raise Exception(f"Ошибка при разделении PDF: {str(e)}")
    
    def split_by_pages(self, 
                      book_id: str, 
                      text_data: Dict[str, Any], 
                      pages_per_section: int, 
                      design: str) -> List[Dict[str, str]]:
        """
        Разделяет книгу на равные части по количеству страниц
        
        Args:
            book_id: ID книги
            text_data: Данные о тексте книги
            pages_per_section: Количество страниц в разделе
            design: Название дизайна
            
        Returns:
            Список созданных файлов
        """
        try:
            total_pages = text_data.get('total_pages', 0)
            if total_pages == 0:
                raise ValueError("Не найдены страницы в данных книги")
            
            # Создаем искусственную структуру
            sections = []
            current_page = 1
            section_index = 1
            
            while current_page <= total_pages:
                end_page = min(current_page + pages_per_section - 1, total_pages)
                
                section = {
                    'name': f"Бөлім {section_index}",
                    'type': 'page_based',
                    'start_page': current_page,
                    'end_page': end_page,
                    'level': 1
                }
                
                sections.append(section)
                current_page = end_page + 1
                section_index += 1
            
            # Создаем структуру
            structure = {
                'title': text_data.get('title', 'Неизвестная книга'),
                'author': text_data.get('author', 'Неизвестный автор'),
                'total_pages': total_pages,
                'sections': sections,
                'analysis_method': 'page_based'
            }
            
            # Генерируем PDF файлы
            return self.split_and_generate(book_id, text_data, structure, design)
            
        except Exception as e:
            raise Exception(f"Ошибка при разделении по страницам: {str(e)}")
    
    def split_by_custom_sections(self, 
                                book_id: str, 
                                text_data: Dict[str, Any], 
                                custom_sections: List[Dict[str, Any]], 
                                design: str) -> List[Dict[str, str]]:
        """
        Разделяет книгу по пользовательским разделам
        
        Args:
            book_id: ID книги
            text_data: Данные о тексте книги
            custom_sections: Пользовательские разделы
            design: Название дизайна
            
        Returns:
            Список созданных файлов
        """
        try:
            # Валидируем пользовательские разделы
            validated_sections = self._validate_custom_sections(custom_sections, text_data)
            
            # Создаем структуру
            structure = {
                'title': text_data.get('title', 'Неизвестная книга'),
                'author': text_data.get('author', 'Неизвестный автор'),
                'total_pages': text_data.get('total_pages', 0),
                'sections': validated_sections,
                'analysis_method': 'custom'
            }
            
            # Генерируем PDF файлы
            return self.split_and_generate(book_id, text_data, structure, design)
            
        except Exception as e:
            raise Exception(f"Ошибка при разделении по пользовательским разделам: {str(e)}")
    
    def _validate_custom_sections(self, sections: List[Dict[str, Any]], text_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Валидирует пользовательские разделы"""
        total_pages = text_data.get('total_pages', 0)
        validated_sections = []
        
        for section in sections:
            # Проверяем обязательные поля
            if 'name' not in section or 'start_page' not in section or 'end_page' not in section:
                continue
            
            # Проверяем корректность страниц
            start_page = int(section['start_page'])
            end_page = int(section['end_page'])
            
            if start_page < 1 or end_page > total_pages or start_page > end_page:
                continue
            
            # Добавляем недостающие поля
            validated_section = {
                'name': section['name'],
                'type': section.get('type', 'custom'),
                'start_page': start_page,
                'end_page': end_page,
                'level': section.get('level', 1)
            }
            
            validated_sections.append(validated_section)
        
        return validated_sections
    
    def get_section_preview(self, 
                           text_data: Dict[str, Any], 
                           section: Dict[str, Any], 
                           preview_length: int = 500) -> str:
        """
        Получает превью раздела
        
        Args:
            text_data: Данные о тексте книги
            section: Данные о разделе
            preview_length: Длина превью в символах
            
        Returns:
            Текст превью
        """
        try:
            # Извлекаем текст раздела
            section_text = self._extract_section_text(section, text_data)
            
            # Обрезаем до нужной длины
            if len(section_text) > preview_length:
                section_text = section_text[:preview_length] + "..."
            
            return section_text
            
        except Exception as e:
            return f"Ошибка при получении превью: {str(e)}"
    
    def _extract_section_text(self, section: Dict[str, Any], text_data: Dict[str, Any]) -> str:
        """Извлекает текст раздела"""
        start_page = section['start_page']
        end_page = section['end_page']
        
        text_parts = []
        for page in text_data.get('pages', []):
            if start_page <= page['page_number'] <= end_page:
                text_parts.append(page['text'])
        
        return '\n\n'.join(text_parts)
    
    def get_generation_status(self, book_id: str) -> Dict[str, Any]:
        """Получает статус генерации для книги"""
        book_output_dir = os.path.join(self.output_dir, book_id)
        metadata_file = os.path.join(book_output_dir, 'metadata.json')
        
        if not os.path.exists(metadata_file):
            return {
                'status': 'not_found',
                'message': 'Генерация не найдена'
            }
        
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # Проверяем, существуют ли все файлы
            existing_files = []
            missing_files = []
            
            for file_info in metadata.get('generated_files', []):
                file_path = os.path.join(self.output_dir, book_id, file_info['filename'])
                if os.path.exists(file_path):
                    existing_files.append(file_info)
                else:
                    missing_files.append(file_info)
            
            return {
                'status': 'completed' if not missing_files else 'partial',
                'book_id': book_id,
                'total_files': len(metadata.get('generated_files', [])),
                'existing_files': len(existing_files),
                'missing_files': len(missing_files),
                'design_used': metadata.get('design_used'),
                'generation_timestamp': metadata.get('generation_timestamp'),
                'files': existing_files
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Ошибка при чтении метаданных: {str(e)}'
            }
    
    def cleanup_generation(self, book_id: str) -> bool:
        """Удаляет все файлы генерации для книги"""
        try:
            book_output_dir = os.path.join(self.output_dir, book_id)
            
            if os.path.exists(book_output_dir):
                import shutil
                shutil.rmtree(book_output_dir)
                return True
            
            return False
            
        except Exception as e:
            print(f"Ошибка при очистке файлов: {e}")
            return False
    
    def _get_timestamp(self) -> str:
        """Получает текущую временную метку"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_available_generations(self) -> List[Dict[str, Any]]:
        """Получает список всех доступных генераций"""
        generations = []
        
        if not os.path.exists(self.output_dir):
            return generations
        
        for book_id in os.listdir(self.output_dir):
            book_dir = os.path.join(self.output_dir, book_id)
            if os.path.isdir(book_dir):
                status = self.get_generation_status(book_id)
                if status['status'] in ['completed', 'partial']:
                    generations.append({
                        'book_id': book_id,
                        'status': status['status'],
                        'total_files': status['total_files'],
                        'design_used': status.get('design_used'),
                        'generation_timestamp': status.get('generation_timestamp')
                    })
        
        # Сортируем по времени генерации (новые сначала)
        generations.sort(key=lambda x: x.get('generation_timestamp', ''), reverse=True)
        
        return generations
