#!/usr/bin/env python3
"""
Создание таблиц SmartBot в базе данных
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.core.db import engine, Base
from backend.models.chat import SmartBotSession, SmartBotMessage, CandidateAnalysis, AnalysisCategory
from backend.models.applications import JobApplication
from backend.models.users import User
from backend.models.jobs import Job
from backend.models.resumes import Resume

def create_smartbot_tables():
    """Создает таблицы SmartBot"""
    try:
        print("🚀 Создание таблиц SmartBot...")
        
        # Создаем все таблицы
        Base.metadata.create_all(bind=engine)
        
        print("✅ Таблицы SmartBot успешно созданы!")
        
    except Exception as e:
        print(f"❌ Ошибка при создании таблиц: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = create_smartbot_tables()
    sys.exit(0 if success else 1)