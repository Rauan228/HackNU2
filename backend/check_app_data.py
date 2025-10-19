from core.db import SessionLocal
from models.chat import SmartBotSession, CandidateAnalysis
from models.applications import JobApplication
db = SessionLocal()
app = db.query(JobApplication).filter(JobApplication.id == 141).first()
print(f'Application 141 exists: {app is not None}')
if app:
    print(f'Application details: job_id={app.job_id}, user_id={app.user_id}, status={app.status}')
sessions = db.query(SmartBotSession).filter(SmartBotSession.application_id == 141).all()
print(f'Sessions for app 141: {len(sessions)}')
analyses = db.query(CandidateAnalysis).join(SmartBotSession).filter(SmartBotSession.application_id == 141).all()
print(f'Analyses for app 141: {len(analyses)}')
if sessions:
    session = sessions[0]
    print(f'Session details: session_id={session.session_id}, status={session.status}')
    analysis = db.query(CandidateAnalysis).filter(CandidateAnalysis.session_id == session.session_id).first()
    if analysis:
        print(f'Analysis exists: status={analysis.status}, final_score={analysis.final_score}')
    else:
        print('No analysis found for this session')
db.close()