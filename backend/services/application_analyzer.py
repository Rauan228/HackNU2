import openai
import json
import uuid
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from core.config import settings
from models.jobs import Job
from models.resumes import Resume
from models.users import User
from models.applications import JobApplication
from models.chat import (
    SmartBotSession, SmartBotMessage, SmartBotSessionStatus, 
    SmartBotMessageType, CandidateAnalysis, AnalysisCategory, AnalysisStatus
)


class ApplicationAnalyzer:
    """AI-powered analyzer for job applications and candidate evaluation"""
    
    def __init__(self):
        self.openai_available = bool(settings.openai_api_key)
        if self.openai_available:
            openai.api_key = settings.openai_api_key
    
    async def start_analysis_session(self, db: Session, application: JobApplication) -> SmartBotSession:
        """Start a new SmartBot analysis session for an application"""
        
        # Create new SmartBot session
        session = SmartBotSession(
            session_id=str(uuid.uuid4()),
            application_id=application.id,
            status=SmartBotSessionStatus.ANALYZING
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        
        # Get related data
        job = db.query(Job).filter(Job.id == application.job_id).first()
        resume = db.query(Resume).filter(Resume.id == application.resume_id).first()
        user = db.query(User).filter(User.id == application.user_id).first()
        
        if not all([job, resume, user]):
            session.status = SmartBotSessionStatus.ERROR
            db.commit()
            raise ValueError("Missing required data for analysis")
        
        # Perform initial analysis
        try:
            analysis_result = await self._analyze_application(job, resume, user)
            
            # Save initial analysis
            candidate_analysis = CandidateAnalysis(
                session_id=session.session_id,
                initial_score=analysis_result.get("initial_score", 50),
                strengths=json.dumps(analysis_result.get("strengths", []), ensure_ascii=False),
                weaknesses=json.dumps(analysis_result.get("concerns", []), ensure_ascii=False),
                summary="Первичный анализ завершен",
                status=AnalysisStatus.IN_PROGRESS
            )
            db.add(candidate_analysis)
            
            # Save analysis categories
            for discrepancy in analysis_result.get("discrepancies", []):
                category = AnalysisCategory(
                    analysis_id=candidate_analysis.id,
                    category_name=discrepancy.get("category", "общее"),
                    status="mismatch",
                    score=self._calculate_category_score(discrepancy.get("severity", "medium")),
                    details=discrepancy.get("issue", "")
                )
                db.add(category)
            
            # Create initial bot message
            if analysis_result.get("questions"):
                first_question = analysis_result["questions"][0]
                welcome_message = f"Спасибо за отклик на вакансию! Я SmartBot и помогу работодателю лучше понять ваш профиль. {first_question['question']}"
                
                bot_message = SmartBotMessage(
                    session_id=session.session_id,
                    message_type=SmartBotMessageType.QUESTION,
                    content=welcome_message,
                    metadata=json.dumps({
                        "question_category": first_question.get("category"),
                        "question_reason": first_question.get("reason"),
                        "remaining_questions": analysis_result["questions"][1:]
                    }, ensure_ascii=False)
                )
                db.add(bot_message)
            else:
                # No questions needed
                session.status = SmartBotSessionStatus.COMPLETED
                welcome_message = "Спасибо за отклик! Ваш профиль хорошо соответствует требованиям вакансии."
                
                bot_message = SmartBotMessage(
                    session_id=session.session_id,
                    message_type=SmartBotMessageType.INFO,
                    content=welcome_message
                )
                db.add(bot_message)
            
            db.commit()
            db.refresh(session)
            
            return session
            
        except Exception as e:
            session.status = SmartBotSessionStatus.ERROR
            db.commit()
            raise e
    
    async def process_candidate_response(self, db: Session, session_id: str, user_message: str) -> Dict[str, Any]:
        """Process candidate's response and generate next question or complete analysis"""
        
        session = db.query(SmartBotSession).filter(SmartBotSession.session_id == session_id).first()
        if not session:
            raise ValueError("Session not found")
        
        # Save user message
        user_msg = SmartBotMessage(
            session_id=session_id,
            message_type=SmartBotMessageType.ANSWER,
            content=user_message
        )
        db.add(user_msg)
        
        # Get conversation history
        messages = db.query(SmartBotMessage).filter(
            SmartBotMessage.session_id == session_id
        ).order_by(SmartBotMessage.created_at).all()
        
        # Get last bot message to check for remaining questions
        last_bot_message = None
        for msg in reversed(messages):
            if msg.message_type == SmartBotMessageType.QUESTION:
                last_bot_message = msg
                break
        
        remaining_questions = []
        if last_bot_message and last_bot_message.metadata:
            try:
                metadata = json.loads(last_bot_message.metadata)
                remaining_questions = metadata.get("remaining_questions", [])
            except:
                pass
        
        # Determine next action
        if remaining_questions:
            # Ask next question
            next_question = remaining_questions[0]
            remaining_questions = remaining_questions[1:]
            
            bot_response = next_question["question"]
            
            bot_message = SmartBotMessage(
                session_id=session_id,
                message_type=SmartBotMessageType.QUESTION,
                content=bot_response,
                metadata=json.dumps({
                    "question_category": next_question.get("category"),
                    "question_reason": next_question.get("reason"),
                    "remaining_questions": remaining_questions
                }, ensure_ascii=False)
            )
            db.add(bot_message)
            
        else:
            # Complete analysis
            final_analysis = await self._finalize_analysis(db, session_id)
            
            bot_response = "Спасибо за ответы! Анализ завершен. Работодатель получит подробную информацию о вашем профиле."
            
            bot_message = SmartBotMessage(
                session_id=session_id,
                message_type=SmartBotMessageType.COMPLETION,
                content=bot_response
            )
            db.add(bot_message)
            
            # Update session status
            session.status = SmartBotSessionStatus.COMPLETED
            
            # Update analysis with final results
            analysis = db.query(CandidateAnalysis).filter(
                CandidateAnalysis.session_id == session_id
            ).first()
            
            if analysis:
                analysis.final_score = final_analysis.get("final_score", analysis.initial_score)
                analysis.summary = final_analysis.get("summary", "Анализ завершен")
                analysis.status = AnalysisStatus.COMPLETED
        
        db.commit()
        
        return {
            "message": bot_response,
            "session_status": session.status.value,
            "is_completed": session.status == SmartBotSessionStatus.COMPLETED
        }
    
    async def _analyze_application(self, job: Job, resume: Resume, user: User) -> Dict[str, Any]:
        """Analyze job application and identify discrepancies"""
        
        if not self.openai_available:
            return self._get_demo_analysis()
        
        # Prepare data for analysis
        job_data = self._extract_job_requirements(job)
        candidate_data = self._extract_candidate_profile(resume, user)
        
        # Generate analysis prompt
        analysis_prompt = self._create_analysis_prompt(job_data, candidate_data)
        
        try:
            # Call OpenAI API for analysis
            response = await self._call_openai_analysis(analysis_prompt)
            
            # Parse and structure the response
            analysis_result = self._parse_analysis_response(response)
            
            return analysis_result
            
        except Exception as e:
            print(f"Error in SmartBot analysis: {e}")
            return self._get_demo_analysis()
    
    def _extract_job_requirements(self, job: Job) -> Dict[str, Any]:
        """Extract structured requirements from job posting"""
        return {
            "title": job.title,
            "description": job.description,
            "requirements": job.requirements,
            "location": job.location,
            "salary_min": job.salary_min,
            "salary_max": job.salary_max,
            "employment_type": job.employment_type,
            "experience_level": job.experience_level,
            "company": job.company_name
        }
    
    def _extract_candidate_profile(self, resume: Resume, user: User) -> Dict[str, Any]:
        """Extract structured profile from candidate resume and user data"""
        return {
            "name": f"{user.first_name} {user.last_name}",
            "email": user.email,
            "phone": user.phone,
            "city": user.city,
            "skills": resume.skills,
            "experience": resume.experience,
            "education": resume.education,
            "summary": resume.summary
        }
    
    def _create_analysis_prompt(self, job_data: Dict, candidate_data: Dict) -> str:
        """Create comprehensive analysis prompt for OpenAI"""
        
        prompt = f"""
Ты SmartBot - умный помощник для анализа откликов на вакансии. Твоя задача проанализировать соответствие кандидата требованиям вакансии и выявить несоответствия, которые требуют уточнения.

ВАКАНСИЯ:
Должность: {job_data['title']}
Компания: {job_data['company']}
Локация: {job_data['location']}
Тип занятости: {job_data['employment_type']}
Уровень опыта: {job_data['experience_level']}
Зарплата: {job_data['salary_min']} - {job_data['salary_max']}
Описание: {job_data['description']}
Требования: {job_data['requirements']}

КАНДИДАТ:
Имя: {candidate_data['name']}
Город: {candidate_data['city']}
Навыки: {candidate_data['skills']}
Опыт работы: {candidate_data['experience']}
Образование: {candidate_data['education']}
О себе: {candidate_data['summary']}

ЗАДАЧА:
Проанализируй соответствие кандидата вакансии и определи:
1. Ключевые несоответствия между требованиями и профилем кандидата
2. Вопросы, которые нужно задать для уточнения (максимум 3-4 вопроса)
3. Предварительную оценку релевантности (0-100%)
4. Категории для анализа (город, опыт, навыки, зарплата, образование)

Верни результат в JSON формате:
{{
    "initial_score": число от 0 до 100,
    "discrepancies": [
        {{
            "category": "город|опыт|навыки|зарплата|образование|другое",
            "issue": "описание несоответствия",
            "severity": "high|medium|low"
        }}
    ],
    "questions": [
        {{
            "category": "категория вопроса",
            "question": "текст вопроса на русском языке",
            "reason": "почему этот вопрос важен"
        }}
    ],
    "strengths": ["список сильных сторон кандидата"],
    "concerns": ["список проблемных моментов"],
    "recommendation": "recommend|consider|reject"
}}

Помни: вопросы должны быть дружелюбными, профессиональными и понятными. Избегай давления и формальностей.
"""
        return prompt
    
    async def _call_openai_analysis(self, prompt: str) -> str:
        """Call OpenAI API for analysis"""
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Ты SmartBot - профессиональный HR-аналитик, который помогает работодателям оценивать кандидатов."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"OpenAI API error: {e}")
            raise e
    
    def _parse_analysis_response(self, response: str) -> Dict[str, Any]:
        """Parse OpenAI response and structure the result"""
        try:
            # Try to extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_str = response[json_start:json_end]
                analysis = json.loads(json_str)
                
                # Validate and structure the response
                return {
                    "initial_score": analysis.get("initial_score", 50),
                    "discrepancies": analysis.get("discrepancies", []),
                    "questions": analysis.get("questions", []),
                    "strengths": analysis.get("strengths", []),
                    "concerns": analysis.get("concerns", []),
                    "recommendation": analysis.get("recommendation", "consider")
                }
            else:
                raise ValueError("No valid JSON found in response")
                
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            return self._get_demo_analysis()
    
    def _get_demo_analysis(self) -> Dict[str, Any]:
        """Fallback demo analysis when OpenAI is not available"""
        return {
            "initial_score": 75,
            "discrepancies": [
                {
                    "category": "город",
                    "issue": "Кандидат из другого города",
                    "severity": "medium"
                }
            ],
            "questions": [
                {
                    "category": "город",
                    "question": "Вижу, что вы из другого города. Готовы ли вы рассмотреть переезд или удаленную работу?",
                    "reason": "Уточнить готовность к переезду"
                }
            ],
            "strengths": ["Подходящий опыт работы", "Релевантные навыки"],
            "concerns": ["Несоответствие по локации"],
            "recommendation": "consider"
        }
    
    def _calculate_category_score(self, severity: str) -> int:
        """Calculate score based on severity"""
        severity_scores = {
            "low": 80,
            "medium": 60,
            "high": 30
        }
        return severity_scores.get(severity, 60)
    
    async def _finalize_analysis(self, db: Session, session_id: str) -> Dict[str, Any]:
        """Generate final analysis based on complete conversation"""
        
        # Get conversation history
        messages = db.query(SmartBotMessage).filter(
            SmartBotMessage.session_id == session_id
        ).order_by(SmartBotMessage.created_at).all()
        
        # Get initial analysis
        analysis = db.query(CandidateAnalysis).filter(
            CandidateAnalysis.session_id == session_id
        ).first()
        
        if not self.openai_available:
            return {
                "final_score": analysis.initial_score if analysis else 75,
                "summary": "Кандидат прошел собеседование с ботом. Анализ завершен.",
                "recommendation": "consider"
            }
        
        # Prepare conversation for analysis
        conversation_text = "\n".join([
            f"{msg.message_type.value}: {msg.content}" 
            for msg in messages
        ])
        
        prompt = f"""
На основе полного разговора с кандидатом, создай финальный анализ для работодателя.

ПЕРВИЧНАЯ ОЦЕНКА: {analysis.initial_score if analysis else 50}

ПОЛНАЯ БЕСЕДА:
{conversation_text}

Создай финальный отчет в JSON формате:
{{
    "final_score": число от 0 до 100,
    "recommendation": "recommend|consider|reject",
    "summary": "краткое резюме на русском для работодателя (2-3 предложения)",
    "key_insights": ["ключевые выводы о кандидате"],
    "resolved_concerns": ["какие вопросы были решены"],
    "remaining_concerns": ["что остается проблемным"]
}}
"""
        
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Ты SmartBot - создаешь финальные отчеты для работодателей."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.5
            )
            
            result = response.choices[0].message.content
            
            # Parse JSON response
            json_start = result.find('{')
            json_end = result.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_str = result[json_start:json_end]
                return json.loads(json_str)
            
        except Exception as e:
            print(f"Error in final analysis: {e}")
        
        # Fallback analysis
        return {
            "final_score": analysis.initial_score if analysis else 75,
            "summary": "Кандидат прошел собеседование с ботом. Требуется дополнительная проверка.",
            "recommendation": "consider"
        }


# Create service instance
application_analyzer = ApplicationAnalyzer()