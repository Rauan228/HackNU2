import json
import uuid
import asyncio
import logging
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
    
    async def start_analysis_session(self, db: Session, application: JobApplication) -> SmartBotSession:
        """Start a new SmartBot analysis session for an application"""
        
        # Create new SmartBot session
        session = SmartBotSession(
            session_id=str(uuid.uuid4()),
            application_id=application.id,
            status=SmartBotSessionStatus.ACTIVE
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
            
            # Build full questions list (fallback to discrepancies if empty)
            questions: List[Dict[str, Any]] = analysis_result.get("questions") or self._build_questions_from_discrepancies(analysis_result.get("discrepancies", []))
            
            # Save initial analysis
            candidate_analysis = CandidateAnalysis(
                session_id=session.session_id,
                relevance_score=analysis_result.get("initial_score", 50),
                initial_score=analysis_result.get("initial_score", 50),
                strengths=json.dumps(analysis_result.get("strengths", []), ensure_ascii=False),
                weaknesses=json.dumps(analysis_result.get("concerns", []), ensure_ascii=False),
                clarifications_received=json.dumps({"items": []}, ensure_ascii=False),
                summary="Первичный анализ завершен",
                status=AnalysisStatus.IN_PROGRESS.value,
                questions_asked=1 if questions else 0,
                recommendation=analysis_result.get("recommendation")
            )
            db.add(candidate_analysis)
            db.commit()
            db.refresh(candidate_analysis)
            
            # Save analysis categories
            for discrepancy in analysis_result.get("discrepancies", []):
                category = AnalysisCategory(
                    analysis_id=candidate_analysis.id,
                    category=discrepancy.get("category", "общее"),
                    status="mismatch",
                    score=self._calculate_category_score(discrepancy.get("severity", "medium")),
                    details=discrepancy.get("issue", "")
                )
                db.add(category)
            
            # Create initial bot message
            if questions:
                first_question = questions[0]
                remaining_questions = questions[1:]
                welcome_message = f"Спасибо за отклик на вакансию! Я SmartBot и помогу работодателю лучше понять ваш профиль. {first_question['question']}"
                
                bot_message = SmartBotMessage(
                    session_id=session.session_id,
                    message_type=SmartBotMessageType.QUESTION.value,
                    content=welcome_message,
                    message_metadata=json.dumps({
                        "question_category": first_question.get("category"),
                        "question_reason": first_question.get("reason"),
                        "remaining_questions": remaining_questions
                    }, ensure_ascii=False)
                )
                db.add(bot_message)
            else:
                # No questions needed
                session.status = SmartBotSessionStatus.COMPLETED
                welcome_message = "Спасибо за отклик! Ваш профиль хорошо соответствует требованиям вакансии."
                
                bot_message = SmartBotMessage(
                    session_id=session.session_id,
                    message_type=SmartBotMessageType.INFO.value,
                    content=welcome_message,
                    message_metadata=None
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
            message_type=SmartBotMessageType.ANSWER.value,
            content=user_message,
            message_metadata=None
        )
        db.add(user_msg)
        
        # Get conversation history
        messages = db.query(SmartBotMessage).filter(
            SmartBotMessage.session_id == session_id
        ).order_by(SmartBotMessage.created_at).all()
        
        # Get last bot message to check for remaining questions
        last_bot_message = None
        for msg in reversed(messages):
            if msg.message_type == SmartBotMessageType.QUESTION.value:
                last_bot_message = msg
                break
        
        remaining_questions = []
        metadata = {}
        if last_bot_message and last_bot_message.message_metadata:
            try:
                metadata = json.loads(last_bot_message.message_metadata)
                remaining_questions = metadata.get("remaining_questions", [])
            except Exception:
                metadata = {}

        # Store candidate answer and increment counters
        analysis = db.query(CandidateAnalysis).filter(
            CandidateAnalysis.session_id == session_id
        ).first()

        if analysis:
            # Normalize existing clarifications into dict with items list
            items: List[Dict[str, Any]] = []
            try:
                clar_data = analysis.clarifications_received
                if isinstance(clar_data, str):
                    clar_obj = json.loads(clar_data)
                else:
                    clar_obj = clar_data or {}
                if isinstance(clar_obj, dict):
                    items = clar_obj.get("items", []) or []
                elif isinstance(clar_obj, list):
                    items = clar_obj
            except Exception:
                items = []

            answer_entry = {
                "question_category": metadata.get("question_category"),
                "question_reason": metadata.get("question_reason"),
                "answer": user_message
            }
            items.append(answer_entry)
            analysis.clarifications_received = json.dumps({"items": items}, ensure_ascii=False)
            analysis.questions_answered = (analysis.questions_answered or 0) + 1

            # Update category status/details based on clarification
            if metadata.get("question_category"):
                cat = db.query(AnalysisCategory).filter(
                    AnalysisCategory.analysis_id == analysis.id,
                    AnalysisCategory.category == metadata.get("question_category")
                ).first()
                if cat:
                    # Mark as clarified and append candidate answer
                    cat.status = "clarified"
                    try:
                        cat.details = (cat.details or "") + (" | Ответ кандидата: " + user_message)
                    except Exception:
                        cat.details = (cat.details or "")

        # If there are remaining questions, ask the next one
        if remaining_questions:
            next_question = remaining_questions[0]
            new_remaining = remaining_questions[1:]

            bot_message = SmartBotMessage(
                session_id=session_id,
                message_type=SmartBotMessageType.QUESTION.value,
                content=next_question.get("question", "Уточните, пожалуйста."),
                message_metadata=json.dumps({
                    "question_category": next_question.get("category"),
                    "question_reason": next_question.get("reason"),
                    "remaining_questions": new_remaining
                }, ensure_ascii=False)
            )
            db.add(bot_message)

            # Keep session active and increment asked counter
            if analysis:
                analysis.questions_asked = (analysis.questions_asked or 0) + 1
            session.status = SmartBotSessionStatus.ACTIVE
            db.commit()
            
            return {
                "message": bot_message.content,
                "session_status": session.status,
                "is_completed": False
            }

        # No remaining questions: finalize analysis
        final_analysis = await self._finalize_analysis(db, session_id)

        bot_response = "Спасибо за ответы! Анализ завершен. Работодатель получит подробную информацию о вашем профиле."

        bot_message = SmartBotMessage(
            session_id=session_id,
            message_type=SmartBotMessageType.COMPLETION.value,
            content=bot_response,
            message_metadata=None
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
            analysis.status = AnalysisStatus.COMPLETED.value
            analysis.recommendation = final_analysis.get("recommendation", analysis.recommendation)
            analysis.analysis_completed = True

        db.commit()

        # Send notification to employer about completed analysis
        try:
            from services.notification_service import notification_service
            await notification_service.send_analysis_completion_notification(db, session_id)
        except Exception as e:
            logging.error(f"Failed to send notification: {str(e)}")

        return {
            "message": bot_response,
            "session_status": session.status,
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
            "name": user.full_name or "Не указано",
            "email": user.email or "Не указан",
            "phone": user.phone or "Не указан",
            "city": resume.location or "Не указан",
            "skills": resume.skills or "Не указаны",
            "experience": resume.experience or "Не указан",
            "education": resume.education or "Не указано",
            "summary": resume.summary or "Не указано"
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
        """Call OpenAI API for analysis with retry mechanism"""
        import logging
        from openai import AsyncOpenAI
        
        logger = logging.getLogger(__name__)
        max_retries = 3
        
        client = AsyncOpenAI(api_key=settings.openai_api_key)
        
        for attempt in range(max_retries):
            try:
                response = await client.chat.completions.create(
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
                logger.warning(f"OpenAI API error (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    continue
                raise e
        
        # If all retries failed, fallback to demo analysis
        logger.error("All OpenAI retry attempts failed, using fallback analysis")
        raise Exception("OpenAI API unavailable after retries")
    
    def _parse_analysis_response(self, response: str) -> Dict[str, Any]:
        """Parse OpenAI response and structure the result with improved error handling"""
        logger = logging.getLogger(__name__)
        
        try:
            # Try to extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_str = response[json_start:json_end]
                analysis = json.loads(json_str)
                
                # Validate required fields and provide defaults
                result = {
                    "initial_score": analysis.get("initial_score", 50),
                    "discrepancies": analysis.get("discrepancies", []),
                    "questions": analysis.get("questions", []),
                    "strengths": analysis.get("strengths", []),
                    "concerns": analysis.get("concerns", []),
                    "recommendation": analysis.get("recommendation", "consider")
                }
                
                # Validate score range
                if not isinstance(result["initial_score"], (int, float)) or not (0 <= result["initial_score"] <= 100):
                    logger.warning(f"Invalid initial_score: {result['initial_score']}, using default 50")
                    result["initial_score"] = 50
                
                # Validate recommendation values
                valid_recommendations = ["recommend", "consider", "reject"]
                if result["recommendation"] not in valid_recommendations:
                    logger.warning(f"Invalid recommendation: {result['recommendation']}, using 'consider'")
                    result["recommendation"] = "consider"
                
                return result
            else:
                logger.error("No valid JSON found in OpenAI response")
                return self._get_demo_analysis()
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            logger.debug(f"Failed to parse response: {response[:200]}...")
            return self._get_demo_analysis()
        except Exception as e:
            logger.error(f"Unexpected error parsing analysis response: {e}")
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
                },
                {
                    "category": "образование",
                    "issue": "Не указано соответствующее высшее образование",
                    "severity": "low"
                }
            ],
            "questions": [
                {
                    "category": "город",
                    "question": "Вижу, что вы из другого города. Готовы ли вы рассмотреть переезд или удаленную работу?",
                    "reason": "Уточнить готовность к переезду"
                },
                {
                    "category": "образование",
                    "question": "Пожалуйста, уточните уровень вашего образования и профиль, чтобы понять соответствие требованиям вакансии.",
                    "reason": "Проверить соответствие образования"
                }
            ],
            "strengths": ["Подходящий опыт работы", "Релевантные навыки"],
            "concerns": ["Несоответствие по локации", "Неясность по образованию"],
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
            f"{msg.message_type}: {msg.content}" 
            for msg in messages if msg.message_type and msg.content
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
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=settings.openai_api_key)
            
            response = await client.chat.completions.create(
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
                parsed_result = json.loads(json_str)
                return parsed_result
            
        except Exception as e:
            logging.error(f"Error in final analysis: {e}")
            # Continue to fallback analysis
        
        # Fallback analysis
        fallback_score = analysis.initial_score if analysis else 50
        
        # Simple analysis based on conversation length and content
        answer_count = len([
            msg for msg in messages 
            if msg.message_type == SmartBotMessageType.ANSWER.value
        ])
        
        if answer_count == 0:
            summary = "Кандидат не предоставил информацию о своих навыках, которые могут быть релевантны для этой позиции."
            final_score = 0.0
        elif answer_count < 3:
            summary = "Кандидат предоставил ограниченную информацию. Требуется дополнительная проверка."
            final_score = max(fallback_score - 20, 30)
        else:
            summary = "Кандидат прошел собеседование с ботом. Анализ завершен."
            final_score = fallback_score
        
        return {
            "final_score": final_score,
            "summary": summary,
            "recommendation": "consider"
        }


# Create service instance
application_analyzer = ApplicationAnalyzer()