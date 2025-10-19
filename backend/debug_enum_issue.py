#!/usr/bin/env python3
"""
Debug the enum serialization issue
"""

import json
from models.chat import SmartBotMessage, SmartBotMessageType
from core.db import SessionLocal

def debug_enum_serialization():
    """Debug how the enum is being serialized"""
    
    print("=== Enum Value Tests ===")
    print(f"SmartBotMessageType.QUESTION = {SmartBotMessageType.QUESTION!r}")
    print(f"SmartBotMessageType.QUESTION.value = {SmartBotMessageType.QUESTION.value!r}")
    print(f"SmartBotMessageType.QUESTION.name = {SmartBotMessageType.QUESTION.name!r}")
    print(f"str(SmartBotMessageType.QUESTION) = {str(SmartBotMessageType.QUESTION)!r}")
    
    print("\n=== Creating SmartBotMessage Object ===")
    msg = SmartBotMessage(
        session_id="test-session",
        message_type=SmartBotMessageType.QUESTION,
        content="Test message"
    )
    
    print(f"msg.message_type = {msg.message_type!r}")
    print(f"type(msg.message_type) = {type(msg.message_type)}")
    
    # Test JSON serialization
    print("\n=== JSON Serialization Test ===")
    try:
        json_str = json.dumps({"message_type": SmartBotMessageType.QUESTION}, default=str)
        print(f"JSON with default=str: {json_str}")
    except Exception as e:
        print(f"JSON serialization error: {e}")
    
    # Test what happens when we convert to dict
    print("\n=== Dict Conversion Test ===")
    msg_dict = {
        "session_id": msg.session_id,
        "message_type": msg.message_type,
        "content": msg.content
    }
    print(f"Dict representation: {msg_dict}")
    
    # Test SQLAlchemy column type
    print("\n=== SQLAlchemy Column Info ===")
    from sqlalchemy import inspect
    mapper = inspect(SmartBotMessage)
    message_type_col = mapper.columns['message_type']
    print(f"Column type: {message_type_col.type}")
    print(f"Column type class: {type(message_type_col.type)}")

if __name__ == "__main__":
    debug_enum_serialization()