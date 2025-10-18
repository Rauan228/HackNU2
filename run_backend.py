#!/usr/bin/env python3
"""
Скрипт для запуска backend сервера HackNU SmartBot
"""
import sys
import os

# Добавляем backend директорию в Python path
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_dir)

if __name__ == "__main__":
    import uvicorn
    from main import app
    
    print("🚀 Запуск HackNU SmartBot Backend...")
    print("📡 Сервер будет доступен по адресу: http://localhost:8000")
    print("📚 API документация: http://localhost:8000/docs")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )