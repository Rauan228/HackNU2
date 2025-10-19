import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from models.chat import SmartBotMessageType, SmartBotMessage
from core.db import get_db
import json

# Test the enum value
print(f"SmartBotMessageType.QUESTION = {SmartBotMessageType.QUESTION!r}")
print(f"SmartBotMessageType.QUESTION.value = {SmartBotMessageType.QUESTION.value!r}")
print(f"type(SmartBotMessageType.QUESTION.value) = {type(SmartBotMessageType.QUESTION.value)}")

# Test creating a SmartBotMessage object
message = SmartBotMessage(
    session_id="test-session",
    message_type=SmartBotMessageType.QUESTION.value,
    content="Test message",
    message_metadata=json.dumps({"test": "data"})
)

print(f"\nSmartBotMessage object created:")
print(f"message.message_type = {message.message_type!r}")
print(f"type(message.message_type) = {type(message.message_type)}")

# Test what happens when we convert to string
print(f"\nString conversion tests:")
print(f"str(SmartBotMessageType.QUESTION) = {str(SmartBotMessageType.QUESTION)!r}")
print(f"repr(SmartBotMessageType.QUESTION) = {repr(SmartBotMessageType.QUESTION)!r}")

# Test JSON serialization
print(f"\nJSON serialization tests:")
try:
    json_with_enum = json.dumps({"type": SmartBotMessageType.QUESTION})
    print(f"json.dumps with enum (should fail): {json_with_enum}")
except Exception as e:
    print(f"json.dumps with enum failed (expected): {e}")

try:
    json_with_value = json.dumps({"type": SmartBotMessageType.QUESTION.value})
    print(f"json.dumps with .value: {json_with_value}")
except Exception as e:
    print(f"json.dumps with .value failed: {e}")

try:
    json_with_str = json.dumps({"type": SmartBotMessageType.QUESTION}, default=str)
    print(f"json.dumps with default=str: {json_with_str}")
except Exception as e:
    print(f"json.dumps with default=str failed: {e}")