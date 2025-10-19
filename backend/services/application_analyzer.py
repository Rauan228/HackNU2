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
from models.chat import SmartBotSession, SmartBotMessage, SmartBotSessionStatus, SmartBotMessageType, CandidateAnalysis, AnalysisCategory, AnalysisStatus
from services.ws_manager import ws_manager

class ApplicationAnalyzer:

    def __init__(self):
        self.openai_available = bool(settings.openai_api_key)

    async def start_analysis_session(self, db: Session, application: JobApplication) -> SmartBotSession:
        session = SmartBotSession(session_id=str(uuid.uuid4()), application_id=application.id, status=SmartBotSessionStatus.ACTIVE)
        db.add(session)
        db.commit()
        db.refresh(session)
        job = db.query(Job).filter(Job.id == application.job_id).first()
        resume = db.query(Resume).filter(Resume.id == application.resume_id).first()
        user = db.query(User).filter(User.id == application.user_id).first()
        if not all([job, resume, user]):
            session.status = SmartBotSessionStatus.ERROR
            db.commit()
            raise ValueError('Missing required data for analysis')
        try:
            analysis_result = await self._analyze_application(job, resume, user)
            questions: List[Dict[str, Any]] = analysis_result.get('questions') or self._build_questions_from_discrepancies(analysis_result.get('discrepancies', []))
            candidate_analysis = CandidateAnalysis(session_id=session.session_id, relevance_score=analysis_result.get('initial_score', 50), initial_score=analysis_result.get('initial_score', 50), strengths=json.dumps(analysis_result.get('strengths', []), ensure_ascii=False), weaknesses=json.dumps(analysis_result.get('concerns', []), ensure_ascii=False), clarifications_received=json.dumps({'items': []}, ensure_ascii=False), summary='Первичный анализ завершен', status=AnalysisStatus.IN_PROGRESS.value, questions_asked=1 if questions else 0, recommendation=analysis_result.get('recommendation'))
            db.add(candidate_analysis)
            db.commit()
            db.refresh(candidate_analysis)
            for discrepancy in analysis_result.get('discrepancies', []):
                category = AnalysisCategory(analysis_id=candidate_analysis.id, category=discrepancy.get('category', 'общее'), status='mismatch', score=self._calculate_category_score(discrepancy.get('severity', 'medium')), details=discrepancy.get('issue', ''))
                db.add(category)
            if questions:
                first_question = questions[0]
                remaining_questions = questions[1:]
                welcome_message = f"Спасибо за отклик на вакансию! Я SmartBot и помогу работодателю лучше понять ваш профиль. {first_question['question']}"
                bot_message = SmartBotMessage(session_id=session.session_id, message_type=SmartBotMessageType.QUESTION.value, content=welcome_message, message_metadata=json.dumps({'question_category': first_question.get('category'), 'question_reason': first_question.get('reason'), 'remaining_questions': remaining_questions}, ensure_ascii=False))
                db.add(bot_message)
            else:
                session.status = SmartBotSessionStatus.COMPLETED
                welcome_message = 'Спасибо за отклик! Ваш профиль хорошо соответствует требованиям вакансии.'
                bot_message = SmartBotMessage(session_id=session.session_id, message_type=SmartBotMessageType.INFO.value, content=welcome_message, message_metadata=None)
                db.add(bot_message)
            db.commit()
            db.refresh(session)
            try:
                await ws_manager.broadcast_session(session.session_id, {'event': 'chat_message', 'session_id': session.session_id, 'message': {'role': 'bot', 'type': bot_message.message_type, 'content': bot_message.content}, 'session_status': session.status})
            except Exception as e:
                logging.error(f'WS broadcast failed (initial message): {e}')
            return session
        except Exception as e:
            session.status = SmartBotSessionStatus.ERROR
            db.commit()
            raise e

    async def process_candidate_response(self, db: Session, session_id: str, user_message: str) -> Dict[str, Any]:
        session = db.query(SmartBotSession).filter(SmartBotSession.session_id == session_id).first()
        if not session:
            raise ValueError('Session not found')
        user_msg = SmartBotMessage(session_id=session_id, message_type=SmartBotMessageType.ANSWER.value, content=user_message, message_metadata=None)
        db.add(user_msg)
        try:
            await ws_manager.broadcast_session(session_id, {'event': 'chat_message', 'session_id': session_id, 'message': {'role': 'candidate', 'type': user_msg.message_type, 'content': user_message}})
        except Exception as e:
            logging.error(f'WS broadcast failed (candidate message): {e}')
        messages = db.query(SmartBotMessage).filter(SmartBotMessage.session_id == session_id).order_by(SmartBotMessage.created_at).all()
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
                remaining_questions = metadata.get('remaining_questions', [])
            except Exception:
                metadata = {}
        analysis = db.query(CandidateAnalysis).filter(CandidateAnalysis.session_id == session_id).first()
        if analysis:
            items: List[Dict[str, Any]] = []
            try:
                clar_data = analysis.clarifications_received
                if isinstance(clar_data, str):
                    clar_obj = json.loads(clar_data)
                else:
                    clar_obj = clar_data or {}
                if isinstance(clar_obj, dict):
                    items = clar_obj.get('items', []) or []
                elif isinstance(clar_obj, list):
                    items = clar_obj
            except Exception:
                items = []
            answer_entry = {'question_category': metadata.get('question_category'), 'question_reason': metadata.get('question_reason'), 'answer': user_message}
            items.append(answer_entry)
            analysis.clarifications_received = json.dumps({'items': items}, ensure_ascii=False)
            analysis.questions_answered = (analysis.questions_answered or 0) + 1
            if metadata.get('question_category'):
                cat = db.query(AnalysisCategory).filter(AnalysisCategory.analysis_id == analysis.id, AnalysisCategory.category == metadata.get('question_category')).first()
                if cat:
                    cat.status = 'clarified'
                    try:
                        cat.details = (cat.details or '') + (' | Ответ кандидата: ' + user_message)
                    except Exception:
                        cat.details = cat.details or ''
        if remaining_questions:
            next_question = remaining_questions[0]
            new_remaining = remaining_questions[1:]
            bot_message = SmartBotMessage(session_id=session_id, message_type=SmartBotMessageType.QUESTION.value, content=next_question.get('question', 'Уточните, пожалуйста.'), message_metadata=json.dumps({'question_category': next_question.get('category'), 'question_reason': next_question.get('reason'), 'remaining_questions': new_remaining}, ensure_ascii=False))
            db.add(bot_message)
            if analysis:
                analysis.questions_asked = (analysis.questions_asked or 0) + 1
            session.status = SmartBotSessionStatus.ACTIVE
            db.commit()
            try:
                await ws_manager.broadcast_session(session_id, {'event': 'chat_message', 'session_id': session_id, 'message': {'role': 'bot', 'type': bot_message.message_type, 'content': bot_message.content}, 'session_status': session.status})
            except Exception as e:
                logging.error(f'WS broadcast failed (bot question): {e}')
            return {'message': bot_message.content, 'session_status': session.status, 'is_completed': False}
        final_analysis = await self._finalize_analysis(db, session_id)
        bot_response = 'Спасибо за ответы! Анализ завершен. Работодатель получит подробную информацию о вашем профиле.'
        bot_message = SmartBotMessage(session_id=session_id, message_type=SmartBotMessageType.COMPLETION.value, content=bot_response, message_metadata=None)
        db.add(bot_message)
        session.status = SmartBotSessionStatus.COMPLETED
        analysis = db.query(CandidateAnalysis).filter(CandidateAnalysis.session_id == session_id).first()
        if analysis:
            analysis.final_score = final_analysis.get('final_score', analysis.initial_score)
            analysis.summary = final_analysis.get('summary', 'Анализ завершен')
            analysis.status = AnalysisStatus.COMPLETED.value
            analysis.recommendation = final_analysis.get('recommendation', analysis.recommendation)
            analysis.analysis_completed = True
        db.commit()
        try:
            await ws_manager.broadcast_session(session_id, {'event': 'chat_message', 'session_id': session_id, 'message': {'role': 'bot', 'type': bot_message.message_type, 'content': bot_message.content}, 'session_status': session.status})
            await ws_manager.broadcast_session(session_id, {'event': 'session_completed', 'session_id': session_id, 'final': {'final_score': analysis.final_score if analysis else None, 'recommendation': analysis.recommendation if analysis else None, 'summary': analysis.summary if analysis else None}})
        except Exception as e:
            logging.error(f'WS broadcast failed (completion): {e}')
        try:
            from services.notification_service import notification_service
            await notification_service.send_analysis_completion_notification(db, session_id)
        except Exception as e:
            logging.error(f'Failed to send notification: {str(e)}')
        return {'message': bot_response, 'session_status': session.status, 'is_completed': session.status == SmartBotSessionStatus.COMPLETED}

    async def _analyze_application(self, job: Job, resume: Resume, user: User) -> Dict[str, Any]:
        if not self.openai_available:
            return self._get_demo_analysis()
        job_data = self._extract_job_requirements(job)
        candidate_data = self._extract_candidate_profile(resume, user)
        analysis_prompt = self._create_analysis_prompt(job_data, candidate_data)
        try:
            response = await self._call_openai_analysis(analysis_prompt)
            analysis_result = self._parse_analysis_response(response)
            return analysis_result
        except Exception as e:
            print(f'Error in SmartBot analysis: {e}')
            return self._get_demo_analysis()

    def _extract_job_requirements(self, job: Job) -> Dict[str, Any]:
        return {'title': job.title, 'description': job.description, 'requirements': job.requirements, 'location': job.location, 'salary_min': job.salary_min, 'salary_max': job.salary_max, 'employment_type': job.employment_type, 'experience_level': job.experience_level, 'company': job.company_name}

    def _extract_candidate_profile(self, resume: Resume, user: User) -> Dict[str, Any]:
        return {'name': user.full_name or 'Не указано', 'email': user.email or 'Не указан', 'phone': user.phone or 'Не указан', 'city': resume.location or 'Не указан', 'skills': resume.skills or 'Не указаны', 'experience': resume.experience or 'Не указан', 'education': resume.education or 'Не указано', 'summary': resume.summary or 'Не указано'}

    def _create_analysis_prompt(self, job_data: Dict, candidate_data: Dict) -> str:
        prompt = f"""\nТы SmartBot - умный помощник для анализа откликов на вакансии. Твоя задача проанализировать соответствие кандидата требованиям вакансии и выявить несоответствия, которые требуют уточнения.\nВАКАНСИЯ:\nДолжность: {job_data['title']}\nКомпания: {job_data['company']}\nЛокация: {job_data['location']}\nТип занятости: {job_data['employment_type']}\nУровень опыта: {job_data['experience_level']}\nЗарплата: {job_data['salary_min']} - {job_data['salary_max']}\nОписание: {job_data['description']}\nТребования: {job_data['requirements']}\nКАНДИДАТ:\nИмя: {candidate_data['name']}\nГород: {candidate_data['city']}\nНавыки: {candidate_data['skills']}\nОпыт работы: {candidate_data['experience']}\nОбразование: {candidate_data['education']}\nО себе: {candidate_data['summary']}\nЗАДАЧА:\nПроанализируй соответствие кандидата вакансии и определи:\n1. Ключевые несоответствия между требованиями и профилем кандидата\n2. Вопросы, которые нужно задать для уточнения (максимум 3-4 вопроса)\n3. Предварительную оценку релевантности (0-100%)\n4. Категории для анализа (город, опыт, навыки, зарплата, образование)\nВерни результат в JSON формате:\n{{\n    "initial_score": число от 0 до 100,\n    "discrepancies": [\n        {{\n            "category": "город|опыт|навыки|зарплата|образование|другое",\n            "issue": "описание несоответствия",\n            "severity": "high|medium|low"\n        }}\n    ],\n    "questions": [\n        {{\n            "category": "категория вопроса",\n            "question": "текст вопроса на русском языке",\n            "reason": "почему этот вопрос важен"\n        }}\n    ],\n    "strengths": ["список сильных сторон кандидата"],\n    "concerns": ["список проблемных моментов"],\n    "recommendation": "recommend|consider|reject"\n}}\nПомни: вопросы должны быть дружелюбными, профессиональными и понятными. Избегай давления и формальностей.\n"""
        return prompt

    async def _call_openai_analysis(self, prompt: str) -> str:
        import logging
        from openai import AsyncOpenAI
        logger = logging.getLogger(__name__)
        max_retries = 3
        client = AsyncOpenAI(api_key=settings.openai_api_key)
        for attempt in range(max_retries):
            try:
                response = await client.chat.completions.create(model='gpt-4', messages=[{'role': 'system', 'content': 'Ты SmartBot - профессиональный HR-аналитик, который помогает работодателям оценивать кандидатов.'}, {'role': 'user', 'content': prompt}], max_tokens=2000, temperature=0.7)
                return response.choices[0].message.content
            except Exception as e:
                logger.warning(f'OpenAI API error (attempt {attempt + 1}/{max_retries}): {e}')
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                raise e
        logger.error('All OpenAI retry attempts failed, using fallback analysis')
        raise Exception('OpenAI API unavailable after retries')

    def _parse_analysis_response(self, response: str) -> Dict[str, Any]:
        logger = logging.getLogger(__name__)
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end != -1:
                json_str = response[json_start:json_end]
                analysis = json.loads(json_str)
                result = {'initial_score': analysis.get('initial_score', 50), 'discrepancies': analysis.get('discrepancies', []), 'questions': analysis.get('questions', []), 'strengths': analysis.get('strengths', []), 'concerns': analysis.get('concerns', []), 'recommendation': analysis.get('recommendation', 'consider')}
                if not isinstance(result['initial_score'], (int, float)) or not 0 <= result['initial_score'] <= 100:
                    logger.warning(f"Invalid initial_score: {result['initial_score']}, using default 50")
                    result['initial_score'] = 50
                valid_recommendations = ['recommend', 'consider', 'reject']
                if result['recommendation'] not in valid_recommendations:
                    logger.warning(f"Invalid recommendation: {result['recommendation']}, using 'consider'")
                    result['recommendation'] = 'consider'
                return result
            else:
                logger.error('No valid JSON found in OpenAI response')
                return self._get_demo_analysis()
        except json.JSONDecodeError as e:
            logger.error(f'JSON parsing error: {e}')
            logger.debug(f'Failed to parse response: {response[:200]}...')
            return self._get_demo_analysis()
        except Exception as e:
            logger.error(f'Unexpected error parsing analysis response: {e}')
            return self._get_demo_analysis()

    def _get_demo_analysis(self) -> Dict[str, Any]:
        return {'initial_score': 75, 'discrepancies': [{'category': 'город', 'issue': 'Кандидат из другого города', 'severity': 'medium'}, {'category': 'образование', 'issue': 'Не указано соответствующее высшее образование', 'severity': 'low'}], 'questions': [{'category': 'город', 'question': 'Вижу, что вы из другого города. Готовы ли вы рассмотреть переезд или удаленную работу?', 'reason': 'Уточнить готовность к переезду'}, {'category': 'образование', 'question': 'Пожалуйста, уточните уровень вашего образования и профиль, чтобы понять соответствие требованиям вакансии.', 'reason': 'Проверить соответствие образования'}], 'strengths': ['Подходящий опыт работы', 'Релевантные навыки'], 'concerns': ['Несоответствие по локации', 'Неясность по образованию'], 'recommendation': 'consider'}

    def _calculate_category_score(self, severity: str) -> int:
        severity_scores = {'low': 80, 'medium': 60, 'high': 30}
        return severity_scores.get(severity, 60)

    async def _finalize_analysis(self, db: Session, session_id: str) -> Dict[str, Any]:
        messages = db.query(SmartBotMessage).filter(SmartBotMessage.session_id == session_id).order_by(SmartBotMessage.created_at).all()
        analysis = db.query(CandidateAnalysis).filter(CandidateAnalysis.session_id == session_id).first()
        if not self.openai_available:
            return {'final_score': analysis.initial_score if analysis else 75, 'summary': 'Кандидат прошел собеседование с ботом. Анализ завершен.', 'recommendation': 'consider'}
        conversation_text = '\n'.join([f'{msg.message_type}: {msg.content}' for msg in messages if msg.message_type and msg.content])
        prompt = f'\nНа основе полного разговора с кандидатом, создай финальный анализ для работодателя.\nПЕРВИЧНАЯ ОЦЕНКА: {(analysis.initial_score if analysis else 50)}\nПОЛНАЯ БЕСЕДА:\n{conversation_text}\nСоздай финальный отчет в JSON формате:\n{{\n    "final_score": число от 0 до 100,\n    "recommendation": "recommend|consider|reject",\n    "summary": "краткое резюме на русском для работодателя (2-3 предложения)",\n    "key_insights": ["ключевые выводы о кандидате"],\n    "resolved_concerns": ["какие вопросы были решены"],\n    "remaining_concerns": ["что остается проблемным"]\n}}\n'
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=settings.openai_api_key)
            response = await client.chat.completions.create(model='gpt-4', messages=[{'role': 'system', 'content': 'Ты SmartBot - создаешь финальные отчеты для работодателей.'}, {'role': 'user', 'content': prompt}], max_tokens=1000, temperature=0.5)
            result = response.choices[0].message.content
            json_start = result.find('{')
            json_end = result.rfind('}') + 1
            if json_start != -1 and json_end != -1:
                json_str = result[json_start:json_end]
                parsed_result = json.loads(json_str)
                return parsed_result
        except Exception as e:
            logging.error(f'Error in final analysis: {e}')
        fallback_score = analysis.initial_score if analysis else 50
        answer_count = len([msg for msg in messages if msg.message_type == SmartBotMessageType.ANSWER.value])
        if answer_count == 0:
            summary = 'Кандидат не предоставил информацию о своих навыках, которые могут быть релевантны для этой позиции.'
            final_score = 0.0
        elif answer_count < 3:
            summary = 'Кандидат предоставил ограниченную информацию. Требуется дополнительная проверка.'
            final_score = max(fallback_score - 20, 30)
        else:
            summary = 'Кандидат прошел собеседование с ботом. Анализ завершен.'
            final_score = fallback_score
        return {'final_score': final_score, 'summary': summary, 'recommendation': 'consider'}
application_analyzer = ApplicationAnalyzer()
