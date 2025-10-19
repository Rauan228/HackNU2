import requests
import json
import sys

# Test the SmartBot API endpoint
base_url = "http://localhost:8000"

# First, let's create a user and get a token
print("Creating test user and getting authentication token...")

# Register a test user
register_data = {
    "email": "test@example.com",
    "password": "testpassword123",
    "full_name": "Test User",
    "user_type": "job_seeker"
}

try:
    # Try to register (might fail if user exists)
    register_response = requests.post(
        f"{base_url}/api/auth/register",
        json=register_data,
        headers={"Content-Type": "application/json"}
    )
    print(f"Register response: {register_response.status_code}")
    if register_response.status_code != 200:
        print(f"Register error: {register_response.text}")
except Exception as e:
    print(f"Register failed (user might exist): {e}")

# Login to get token
login_data = {
    "email": "test@example.com",
    "password": "testpassword123"
}

try:
    login_response = requests.post(
        f"{base_url}/api/auth/login",
        json=login_data,  # Use JSON instead of form data
        headers={"Content-Type": "application/json"}
    )
    
    if login_response.status_code == 200:
        token_data = login_response.json()
        access_token = token_data["access_token"]
        print(f"✓ Got access token: {access_token[:20]}...")
        
        # First, we need to create a job application to test with
        # Let's create a job first
        job_data = {
            "title": "Test Job",
            "company_name": "Test Company",
            "description": "Test job description",
            "requirements": "Test requirements",
            "location": "Test Location",
            "salary_range": "50000-70000",
            "job_type": "full_time",
            "is_active": True
        }
        
        # Create a resume first
        resume_data = {
            "title": "Test Resume",
            "summary": "Test resume content with React experience",
            "skills": "React, JavaScript, Python"  # Changed from list to string
        }
        
        print("\nCreating test resume...")
        resume_response = requests.post(
            f"{base_url}/api/resumes/",
            json=resume_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}"
            }
        )
        
        if resume_response.status_code == 200:
            resume_id = resume_response.json()["id"]
            print(f"✓ Created resume with ID: {resume_id}")
        else:
            print(f"✗ Failed to create resume: {resume_response.text}")
            sys.exit(1)
        
        # Now test the SmartBot API with start-analysis endpoint
        start_analysis_data = {
            "application_id": 93  # Using the newly created application ID
        }
        
        print(f"\nTesting SmartBot start-analysis endpoint...")
        print(f"Request data: {json.dumps(start_analysis_data, indent=2)}")
        
        smartbot_response = requests.post(
            f"{base_url}/api/smartbot/start-analysis",
            json=start_analysis_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}"
            }
        )
        
        print(f"\nResponse status: {smartbot_response.status_code}")
        
        if smartbot_response.status_code == 200:
            response_data = smartbot_response.json()
            print(f"Response data: {json.dumps(response_data, indent=2)}")
            print("✓ SmartBot start-analysis test successful")
            
            # Now test the chat endpoint
            session_id = response_data.get("session_id")
            if session_id:
                chat_data = {
                    "session_id": session_id,
                    "message": "I have 3+ years of React experience"
                }
                
                print(f"\nTesting SmartBot chat endpoint...")
                print(f"Request data: {json.dumps(chat_data, indent=2)}")
                
                chat_response = requests.post(
                    f"{base_url}/api/smartbot/chat",
                    json=chat_data,
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {access_token}"
                    }
                )
                
                print(f"\nChat response status: {chat_response.status_code}")
                
                if chat_response.status_code == 200:
                    chat_response_data = chat_response.json()
                    print(f"Chat response data: {json.dumps(chat_response_data, indent=2)}")
                    print("✓ SmartBot chat test successful")
                else:
                    print(f"Chat response text: {chat_response.text}")
                    print("✗ SmartBot chat test failed")
        else:
            print(f"Response text: {smartbot_response.text}")
            print("✗ SmartBot start-analysis test failed")
            
    else:
        print(f"✗ Login failed: {login_response.status_code} - {login_response.text}")
        
except Exception as e:
    print(f"✗ Authentication failed: {e}")

print("API endpoint test complete.")