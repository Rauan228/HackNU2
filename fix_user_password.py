import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, text
from backend.core.config import settings
from backend.core.security import get_password_hash

# Create database connection
engine = create_engine(settings.database_url)

print("Fixing user password hash...")

try:
    with engine.connect() as conn:
        # Check current user data
        result = conn.execute(text("SELECT id, email, hashed_password FROM users WHERE email = 'test@example.com'"))
        user = result.fetchone()
        
        if user:
            print(f"Found user: {user.email}")
            print(f"Current hash: {user.hashed_password}")
            
            # Generate a proper hash for the password
            new_hash = get_password_hash("testpassword123")
            print(f"New hash: {new_hash}")
            
            # Update the user's password hash
            conn.execute(
                text("UPDATE users SET hashed_password = :hash WHERE email = :email"),
                {"hash": new_hash, "email": "test@example.com"}
            )
            conn.commit()
            print("✓ Password hash updated successfully")
        else:
            print("User not found, creating new user...")
            
            # Create the user with proper hash
            new_hash = get_password_hash("testpassword123")
            conn.execute(
                text("""
                    INSERT INTO users (email, hashed_password, full_name, user_type, is_active, created_at, updated_at)
                    VALUES (:email, :hash, :name, :user_type, true, NOW(), NOW())
                """),
                {
                    "email": "test@example.com",
                    "hash": new_hash,
                    "name": "Test User",
                    "user_type": "job_seeker"
                }
            )
            conn.commit()
            print("✓ User created successfully")
            
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("Password fix complete.")