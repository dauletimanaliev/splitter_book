from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
import os
import uuid
from typing import List, Dict, Any
import json

from parser import PDFParser
from ai_structure import AIStructureAnalyzer
from splitter import PDFSplitter
from designer import PDFDesigner

app = FastAPI(title="AI Book Splitter & Designer", version="1.0.0")

# Pydantic модели для валидации данных
class AnalyzeRequest(BaseModel):
    book_id: str
    split_mode: str = "by_headings"

class GenerateRequest(BaseModel):
    book_id: str
    design: str = "classic_islamic"

# CORS middleware для работы с frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Создаем необходимые директории
os.makedirs("uploads", exist_ok=True)
os.makedirs("output", exist_ok=True)
os.makedirs("temp", exist_ok=True)

# Инициализация компонентов
pdf_parser = PDFParser()
ai_analyzer = AIStructureAnalyzer()
pdf_splitter = PDFSplitter()
pdf_designer = PDFDesigner()

@app.get("/")
async def root():
    return {"message": "AI Book Splitter & Designer API"}

@app.post("/upload")
async def upload_book(file: UploadFile = File(...)):
    """Загрузка книги (PDF, DOCX, EPUB)"""
    try:
        # Проверяем расширение файла
        allowed_extensions = ['.pdf', '.docx', '.epub']
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Неподдерживаемый формат файла. Поддерживаются: {', '.join(allowed_extensions)}"
            )
        
        # Генерируем уникальный ID для книги
        book_id = str(uuid.uuid4())
        
        # Сохраняем файл
        file_path = f"uploads/{book_id}{file_extension}"
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Извлекаем текст и структуру
        text_data = pdf_parser.extract_text(file_path)
        
        # Сохраняем извлеченный текст
        text_file = f"temp/{book_id}_text.json"
        with open(text_file, "w", encoding="utf-8") as f:
            json.dump(text_data, f, ensure_ascii=False, indent=2)
        
        return {
            "status": "success",
            "book_id": book_id,
            "filename": file.filename,
            "pages_count": len(text_data.get("pages", [])),
            "message": "Книга успешно загружена и обработана"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при загрузке файла: {str(e)}")

@app.post("/analyze")
async def analyze_structure(request: AnalyzeRequest):
    """Анализ структуры книги и определение разделов"""
    try:
        book_id = request.book_id
        split_mode = request.split_mode
        
        text_file = f"temp/{book_id}_text.json"
        
        if not os.path.exists(text_file):
            raise HTTPException(status_code=404, detail="Файл не найден. Сначала загрузите книгу.")
        
        # Загружаем текст
        with open(text_file, "r", encoding="utf-8") as f:
            text_data = json.load(f)
        
        # Анализируем структуру с помощью AI
        structure = ai_analyzer.analyze_structure(text_data, split_mode)
        
        # Сохраняем структуру
        structure_file = f"temp/{book_id}_structure.json"
        with open(structure_file, "w", encoding="utf-8") as f:
            json.dump(structure, f, ensure_ascii=False, indent=2)
        
        return {
            "status": "success",
            "book_id": book_id,
            "structure": structure,
            "sections_count": len(structure.get("sections", []))
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при анализе структуры: {str(e)}")

@app.post("/generate")
async def generate_pdfs(request: GenerateRequest):
    """Генерация PDF файлов по разделам с выбранным дизайном"""
    try:
        book_id = request.book_id
        design = request.design
        
        # Проверяем наличие необходимых файлов
        text_file = f"temp/{book_id}_text.json"
        structure_file = f"temp/{book_id}_structure.json"
        
        if not os.path.exists(text_file) or not os.path.exists(structure_file):
            raise HTTPException(
                status_code=404, 
                detail="Не найдены файлы анализа. Сначала загрузите книгу и проанализируйте структуру."
            )
        
        # Загружаем данные
        with open(text_file, "r", encoding="utf-8") as f:
            text_data = json.load(f)
        
        with open(structure_file, "r", encoding="utf-8") as f:
            structure = json.load(f)
        
        # Генерируем PDF файлы
        output_files = pdf_splitter.split_and_generate(
            book_id=book_id,
            text_data=text_data,
            structure=structure,
            design=design
        )
        
        return {
            "status": "success",
            "book_id": book_id,
            "design": design,
            "parts": output_files,
            "total_sections": len(output_files)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при генерации PDF: {str(e)}")

@app.get("/download/{book_id}/{filename}")
async def download_pdf(book_id: str, filename: str):
    """Скачивание готового PDF файла"""
    file_path = f"output/{book_id}/{filename}"
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Файл не найден")
    
    from fastapi.responses import FileResponse
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/pdf"
    )

@app.get("/designs")
async def get_available_designs():
    """Получение списка доступных дизайнов"""
    designs_dir = "designs"
    designs = []
    
    if os.path.exists(designs_dir):
        for file in os.listdir(designs_dir):
            if file.endswith('.yaml') or file.endswith('.yml'):
                design_name = os.path.splitext(file)[0]
                designs.append({
                    "name": design_name,
                    "file": file,
                    "display_name": design_name.replace("_", " ").title()
                })
    
    return {
        "status": "success",
        "designs": designs
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
