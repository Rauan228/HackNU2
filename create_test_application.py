import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, text
from backend.core.config import settings

# Create database connection
engine = create_engine(settings.database_url)

print("Creating test job application...")

try:
    with engine.connect() as conn:
        # First, get the test user ID
        result = conn.execute(text("SELECT id FROM users WHERE email = 'test@example.com'"))
        user = result.fetchone()
        
        if not user:
            print("✗ Test user not found")
            sys.exit(1)
            
        user_id = user.id
        print(f"Found test user with ID: {user_id}")
        
        # Get the latest resume for this user
        result = conn.execute(text("SELECT id FROM resumes WHERE user_id = :user_id ORDER BY created_at DESC LIMIT 1"), {"user_id": user_id})
        resume = result.fetchone()
        
        if not resume:
            print("✗ No resume found for test user")
            sys.exit(1)
            
        resume_id = resume.id
        print(f"Found resume with ID: {resume_id}")
        
        # Get any active job
        result = conn.execute(text("SELECT id FROM jobs WHERE is_active = true LIMIT 1"))
        job = result.fetchone()
        
        if not job:
            print("Creating a test job...")
            # Create a test job first
            conn.execute(
                text("""
                    INSERT INTO jobs (title, company_name, description, requirements, location, 
                                    salary_range, job_type, is_active, employer_id, created_at, updated_at)
                    VALUES (:title, :company, :desc, :req, :loc, :salary, :type, true, 1, NOW(), NOW())
                    RETURNING id
                """),
                {
                    "title": "Test Software Developer",
                    "company": "Test Company",
                    "desc": "Test job description for React developer",
                    "req": "React, JavaScript, Python experience required",
                    "loc": "Remote",
                    "salary": "50000-70000",
                    "type": "full_time"
                }
            )
            result = conn.execute(text("SELECT id FROM jobs WHERE title = 'Test Software Developer' ORDER BY created_at DESC LIMIT 1"))
            job = result.fetchone()
            
        job_id = job.id
        print(f"Using job with ID: {job_id}")
        
        # Check if application already exists
        result = conn.execute(
            text("SELECT id FROM job_applications WHERE user_id = :user_id AND job_id = :job_id"),
            {"user_id": user_id, "job_id": job_id}
        )
        existing_app = result.fetchone()
        
        if existing_app:
            app_id = existing_app.id
            print(f"✓ Application already exists with ID: {app_id}")
        else:
            # Create the job application
            result = conn.execute(
                text("""
                    INSERT INTO job_applications (user_id, job_id, resume_id, cover_letter, status, created_at, updated_at)
                    VALUES (:user_id, :job_id, :resume_id, :cover_letter, 'pending', NOW(), NOW())
                    RETURNING id
                """),
                {
                    "user_id": user_id,
                    "job_id": job_id,
                    "resume_id": resume_id,
                    "cover_letter": "Test cover letter for React developer position"
                }
            )
            app = result.fetchone()
            app_id = app.id
            print(f"✓ Created job application with ID: {app_id}")
        
        conn.commit()
        print(f"✓ Test application ready. Use application_id: {app_id}")
            
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("Test application creation complete.")