#!/usr/bin/env python3
"""
Debug bulk insert behavior
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy.orm import Session
from sqlalchemy import text, event
from core.db import get_db
from models.chat import SmartBotMessage, SmartBotMessageType

def debug_bulk_insert():
    """Debug what happens during bulk insert"""
    
    db = next(get_db())
    
    # Add event listener to capture SQL
    @event.listens_for(db.bind, "before_cursor_execute")
    def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        if "smartbot_messages" in statement:
            print(f"🔍 SQL Statement: {statement}")
            print(f"🔍 Parameters: {parameters}")
    
    try:
        print("🔍 Testing bulk insert behavior...")
        
        # Create messages like in the application
        messages = []
        
        # User message
        user_msg = SmartBotMessage(
            session_id="debug-session",
            message_type=SmartBotMessageType.ANSWER.value,
            content="Test user message"
        )
        messages.append(user_msg)
        print(f"User message_type: {user_msg.message_type!r}")
        
        # Bot message  
        bot_msg = SmartBotMessage(
            session_id="debug-session",
            message_type=SmartBotMessageType.COMPLETION.value,
            content="Test bot message"
        )
        messages.append(bot_msg)
        print(f"Bot message_type: {bot_msg.message_type!r}")
        
        # Add all at once (this triggers bulk insert)
        print("\n=== Adding messages with add_all ===")
        db.add_all(messages)
        
        print("\n=== Flushing to database ===")
        db.flush()
        
        print("\n✅ Bulk insert completed")
        db.rollback()  # Don't actually save
        
    except Exception as e:
        print(f"❌ Bulk insert failed: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    
    finally:
        db.close()

if __name__ == "__main__":
    debug_bulk_insert()