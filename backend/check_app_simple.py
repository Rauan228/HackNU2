from core.db import SessionLocal
from sqlalchemy import text

db = SessionLocal()

# Check if application 141 exists
result = db.execute(text("SELECT id, job_id, user_id, status FROM job_applications WHERE id = 141"))
app = result.fetchone()
print(f"Application 141 exists: {app is not None}")
if app:
    print(f"Application details: id={app[0]}, job_id={app[1]}, user_id={app[2]}, status={app[3]}")

# Check SmartBot sessions for application 141
result = db.execute(text("SELECT session_id, status FROM smartbot_sessions WHERE application_id = 141"))
sessions = result.fetchall()
print(f"Sessions for app 141: {len(sessions)}")

if sessions:
    session = sessions[0]
    print(f"Session details: session_id={session[0]}, status={session[1]}")
    
    # Check if analysis exists for this session
    result = db.execute(text("SELECT status, final_score FROM candidate_analyses WHERE session_id = :session_id"), {"session_id": session[0]})
    analysis = result.fetchone()
    if analysis:
        print(f"Analysis exists: status={analysis[0]}, final_score={analysis[1]}")
    else:
        print("No analysis found for this session")

db.close()