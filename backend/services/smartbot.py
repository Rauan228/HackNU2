import uuid
from typing import Optional, List
from sqlalchemy.orm import Session
from core.config import settings
from models.chat import AIChatSession, AIChatMessage, MessageRole
from schemas.chat import ChatResponse


class SmartBotService:
    def __init__(self):
        pass
    
    def get_or_create_session(self, db: Session, session_id: Optional[str] = None, user_id: Optional[int] = None) -> AIChatSession:
        if session_id:
            session = db.query(AIChatSession).filter(AIChatSession.session_id == session_id).first()
            if session:
                return session
        
        # Create new session
        new_session_id = str(uuid.uuid4())
        session = AIChatSession(session_id=new_session_id, user_id=user_id)
        db.add(session)
        db.commit()
        db.refresh(session)
        return session
    
    def get_demo_response(self, message: str) -> str:
        """Demo responses when OpenAI API is not available"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['привет', 'hello', 'hi', 'здравствуй']):
            return "Привет! Я SmartBot - ваш помощник по поиску работы. Я могу помочь вам найти подходящие вакансии, составить резюме или ответить на вопросы о карьере. Чем могу помочь?"
        
        elif any(word in message_lower for word in ['работа', 'вакансия', 'job', 'vacancy']):
            return "Отлично! Я помогу вам с поиском работы. Расскажите мне о ваших навыках, опыте и предпочтениях по должности. Какую работу вы ищете?"
        
        elif any(word in message_lower for word in ['резюме', 'cv', 'resume']):
            return "Я помогу вам создать эффективное резюме! Для начала расскажите о вашем образовании, опыте работы и ключевых навыках. Также важно указать желаемую должность."
        
        elif any(word in message_lower for word in ['зарплата', 'salary', 'деньги', 'money']):
            return "Вопросы о зарплате важны при поиске работы. Рекомендую изучить рынок для вашей специальности, учесть ваш опыт и навыки. Готов помочь с анализом предложений!"
        
        elif any(word in message_lower for word in ['собеседование', 'interview']):
            return "Подготовка к собеседованию - ключ к успеху! Изучите компанию, подготовьте ответы на типичные вопросы, продумайте свои вопросы работодателю. Хотите потренироваться?"
        
        elif any(word in message_lower for word in ['навыки', 'skills', 'умения']):
            return "Развитие навыков очень важно для карьерного роста! Расскажите о ваших текущих навыках, и я подскажу, какие стоит развивать для вашей сферы деятельности."
        
        elif any(word in message_lower for word in ['спасибо', 'thanks', 'thank you']):
            return "Пожалуйста! Рад был помочь. Если у вас есть еще вопросы о карьере или поиске работы, обращайтесь в любое время!"
        
        else:
            return "Интересный вопрос! Как SmartBot, я специализируюсь на помощи с поиском работы, составлением резюме и карьерными вопросами. Можете переформулировать ваш вопрос в контексте карьеры?"
    
    async def get_openai_response(self, messages: List[dict]) -> str:
        """Get response from OpenAI API"""
        if not settings.openai_api_key:
            return self.get_demo_response(messages[-1].get("content", ""))
        
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=settings.openai_api_key)
            
            system_message = {
                "role": "system",
                "content": """Вы SmartBot - умный помощник по поиску работы и карьерному развитию. 
                Ваша задача помогать пользователям с:
                - Поиском подходящих вакансий
                - Составлением и улучшением резюме
                - Подготовкой к собеседованиям
                - Карьерными советами
                - Развитием профессиональных навыков
                
                Отвечайте дружелюбно, профессионально и по существу. 
                Если вопрос не связан с карьерой, вежливо перенаправьте разговор на профессиональные темы."""
            }
            
            full_messages = [system_message] + messages
            
            response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=full_messages,
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return "Извините, произошла ошибка при обработке вашего запроса. Попробуйте еще раз."
    
    async def chat(self, db: Session, message: str, session_id: Optional[str] = None, user_id: Optional[int] = None) -> ChatResponse:
        # Get or create session
        session = self.get_or_create_session(db, session_id, user_id)
        
        # Save user message
        user_message = AIChatMessage(
            session_id=session.session_id,
            role=MessageRole.USER,
            content=message
        )
        db.add(user_message)
        db.commit()
        
        # Get conversation history
        messages = db.query(AIChatMessage).filter(
            AIChatMessage.session_id == session.session_id
        ).order_by(AIChatMessage.created_at).all()
        
        # Prepare messages for AI (limit to last 10 messages to avoid token limits)
        conversation_messages = []
        for msg in messages[-10:]:
            conversation_messages.append({
                "role": msg.role.value,
                "content": msg.content
            })
        
        # Get AI response
        if self.openai_available:
            try:
                ai_response = await self.get_openai_response(conversation_messages)
            except Exception:
                ai_response = self.get_demo_response(message)
        else:
            ai_response = self.get_demo_response(message)
        
        # Save AI response
        assistant_message = AIChatMessage(
            session_id=session.session_id,
            role=MessageRole.ASSISTANT,
            content=ai_response
        )
        db.add(assistant_message)
        db.commit()
        
        return ChatResponse(
            message=ai_response,
            session_id=session.session_id
        )


smartbot_service = SmartBotService()