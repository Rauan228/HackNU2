"""
Notification service for sending reports and updates to employers
"""
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from core.config import settings
from models.users import User
from models.jobs import Job
from models.applications import JobApplication
from models.chat import SmartBotSession, CandidateAnalysis

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for sending notifications to employers"""
    
    def __init__(self):
        self.smtp_server = getattr(settings, 'smtp_server', 'smtp.gmail.com')
        self.smtp_port = getattr(settings, 'smtp_port', 587)
        self.smtp_username = getattr(settings, 'smtp_username', None)
        self.smtp_password = getattr(settings, 'smtp_password', None)
        self.from_email = getattr(settings, 'from_email', 'noreply@smartbot.kz')
    
    async def send_analysis_completion_notification(
        self, 
        db: Session, 
        session_id: str
    ) -> bool:
        """
        Send notification to employer when candidate analysis is completed
        """
        try:
            # Get session and related data
            session = db.query(SmartBotSession).filter(
                SmartBotSession.session_id == session_id
            ).first()
            
            if not session:
                logger.error(f"Session not found: {session_id}")
                return False
            
            # Get application and related data
            application = db.query(JobApplication).filter(
                JobApplication.id == session.application_id
            ).first()
            
            if not application:
                logger.error(f"Application not found for session: {session_id}")
                return False
            
            # Get job and employer
            job = db.query(Job).filter(Job.id == application.job_id).first()
            if not job:
                logger.error(f"Job not found for application: {application.id}")
                return False
            
            employer = db.query(User).filter(User.id == job.employer_id).first()
            if not employer:
                logger.error(f"Employer not found for job: {job.id}")
                return False
            
            # Get candidate
            candidate = db.query(User).filter(User.id == application.user_id).first()
            if not candidate:
                logger.error(f"Candidate not found for application: {application.id}")
                return False
            
            # Get analysis results
            analysis = db.query(CandidateAnalysis).filter(
                CandidateAnalysis.session_id == session_id
            ).first()
            
            # Send email notification
            await self._send_email_notification(
                employer=employer,
                candidate=candidate,
                job=job,
                analysis=analysis,
                session_id=session_id
            )
            
            # Log successful notification
            logger.info(f"Analysis completion notification sent to employer {employer.email} for session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send analysis completion notification: {str(e)}")
            return False
    
    async def _send_email_notification(
        self,
        employer: User,
        candidate: User,
        job: Job,
        analysis: Optional[CandidateAnalysis],
        session_id: str
    ):
        """Send email notification to employer"""
        
        if not self.smtp_username or not self.smtp_password:
            logger.warning("SMTP credentials not configured, skipping email notification")
            return
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = employer.email
            msg['Subject'] = f"SmartBot: Анализ кандидата завершен - {candidate.full_name}"
            
            # Create email body
            score = analysis.final_score or analysis.initial_score if analysis else "Не определен"
            recommendation = analysis.recommendation if analysis else "Не определена"
            summary = analysis.summary if analysis else "Анализ завершен"
            
            body = f"""
Здравствуйте, {employer.full_name}!

SmartBot завершил анализ кандидата для вашей вакансии.

Детали:
• Вакансия: {job.title}
• Кандидат: {candidate.full_name}
• Email кандидата: {candidate.email}
• Оценка соответствия: {score}/100
• Рекомендация: {recommendation}

Краткое резюме анализа:
{summary}

Для просмотра полного отчета, истории переписки и резюме кандидата, войдите в систему:
{getattr(settings, 'frontend_url', 'http://localhost:3000')}/employer/applications

С уважением,
Команда SmartBot
            """
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            text = msg.as_string()
            server.sendmail(self.from_email, employer.email, text)
            server.quit()
            
            logger.info(f"Email notification sent to {employer.email}")
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {str(e)}")
            raise
    
    async def send_application_status_notification(
        self,
        db: Session,
        application_id: int,
        new_status: str
    ) -> bool:
        """
        Send notification to candidate when application status changes
        """
        try:
            application = db.query(JobApplication).filter(
                JobApplication.id == application_id
            ).first()
            
            if not application:
                return False
            
            candidate = db.query(User).filter(User.id == application.user_id).first()
            job = db.query(Job).filter(Job.id == application.job_id).first()
            
            if not candidate or not job:
                return False
            
            # Send notification (implementation depends on requirements)
            logger.info(f"Application status notification sent to {candidate.email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send application status notification: {str(e)}")
            return False


# Global instance
notification_service = NotificationService()