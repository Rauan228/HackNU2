#!/usr/bin/env python3
"""
Test the actual SmartBot chat API endpoint to reproduce the 500 error
"""

import sys
import os
import requests
import json
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from core.db import SessionLocal
from sqlalchemy import text

async def test_smartbot_api():
    """Test the SmartBot API endpoint directly"""
    
    print("🧪 Testing SmartBot Chat API Endpoint")
    print("=" * 50)
    
    # First, let's create a test session and application in the database
    db = SessionLocal()
    
    try:
        # Create test user if not exists
        user_result = db.execute(text("""
            INSERT INTO users (email, full_name, hashed_password, user_type, is_active)
            VALUES ('test@example.com', 'Test User', 'hashed_password', 'job_seeker', true)
            ON CONFLICT (email) DO UPDATE SET email = EXCLUDED.email
            RETURNING id
        """))
        user_id = user_result.fetchone()[0]
        
        # Create test job if not exists
        job_result = db.execute(text("""
            INSERT INTO jobs (title, description, requirements, location, salary_min, salary_max, employer_id, is_active)
            VALUES ('Test Job', 'Test Description', 'Test Requirements', 'Test Location', 50000, 100000, :user_id, true)
            ON CONFLICT DO NOTHING
            RETURNING id
        """), {"user_id": user_id})
        
        job_row = job_result.fetchone()
        if job_row:
            job_id = job_row[0]
        else:
            # Get existing job
            existing_job = db.execute(text("SELECT id FROM jobs LIMIT 1")).fetchone()
            job_id = existing_job[0] if existing_job else None
        
        if not job_id:
            print("❌ No job found to test with")
            return False
        
        # Create test resume if not exists
        resume_result = db.execute(text("""
            INSERT INTO resumes (user_id, title, summary, skills, experience, education)
            VALUES (:user_id, 'Test Resume', 'Test Summary', 'Python, JavaScript', 'Test Experience', 'Test Education')
            ON CONFLICT DO NOTHING
            RETURNING id
        """), {"user_id": user_id})
        
        resume_row = resume_result.fetchone()
        if resume_row:
            resume_id = resume_row[0]
        else:
            # Get existing resume
            existing_resume = db.execute(text("SELECT id FROM resumes WHERE user_id = :user_id LIMIT 1"), {"user_id": user_id}).fetchone()
            resume_id = existing_resume[0] if existing_resume else None
        
        if not resume_id:
            print("❌ No resume found to test with")
            return False
        
        # Create test application
        app_result = db.execute(text("""
            INSERT INTO job_applications (job_id, user_id, resume_id, cover_letter, status)
            VALUES (:job_id, :user_id, :resume_id, 'Test cover letter', 'pending')
            RETURNING id
        """), {"job_id": job_id, "user_id": user_id, "resume_id": resume_id})
        
        application_id = app_result.fetchone()[0]
        
        # Create test SmartBot session
        session_uuid = str(__import__('uuid').uuid4())
        session_result = db.execute(text("""
            INSERT INTO smartbot_sessions (session_id, application_id, status)
            VALUES (:session_id, :app_id, 'active')
            RETURNING id, session_id
        """), {"session_id": session_uuid, "app_id": application_id})
        
        session_row = session_result.fetchone()
        session_id = session_row[1]  # session_id is the UUID string
        
        db.commit()
        
        print(f"✅ Test data created:")
        print(f"   User ID: {user_id}")
        print(f"   Application ID: {application_id}")
        print(f"   Session ID: {session_id}")
        
        # Now test the API endpoint
        print(f"\n🌐 Testing API endpoint...")
        
        # First, get a token (simulate login)
        login_data = {
            "username": "test@example.com",
            "password": "password"  # This won't work, but let's see what happens
        }
        
        # For now, let's test the endpoint directly using the backend
        print("🔧 Testing backend function directly...")
        
        # Import the application analyzer
        from services.application_analyzer import application_analyzer
        
        # Test the process_candidate_response function
        test_message = "я работал с React 3+ года"
        
        print(f"📤 Sending message: '{test_message}'")
        
        result = await application_analyzer.process_candidate_response(
            db=db, 
            session_id=session_uuid,  # Use the UUID string directly
            user_message=test_message
        )
        
        print(f"✅ Response received: {result}")
        
        # Check if messages were inserted correctly
        messages = db.execute(text("""
            SELECT id, message_type, content, message_metadata
            FROM smartbot_messages 
            WHERE session_id = :session_id
            ORDER BY created_at
        """), {"session_id": session_uuid}).fetchall()
        
        print(f"\n📋 Messages in database:")
        for msg in messages:
            print(f"   ID: {msg[0]}, Type: {msg[1]}, Content: {msg[2][:50]}..., Metadata: {msg[3]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing SmartBot API: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        db.rollback()
        return False
    
    finally:
        # Clean up test data
        try:
            db.execute(text("DELETE FROM smartbot_messages WHERE session_id = :session_id"), {"session_id": session_uuid})
            db.execute(text("DELETE FROM smartbot_sessions WHERE session_id = :session_id"), {"session_id": session_uuid})
            db.execute(text("DELETE FROM job_applications WHERE id = :app_id"), {"app_id": application_id})
            db.commit()
        except:
            pass
        db.close()

if __name__ == "__main__":
    import asyncio
    success = asyncio.run(test_smartbot_api())
    sys.exit(0 if success else 1)