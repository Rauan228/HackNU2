import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

import enum
import json

# Define the enum exactly as it is in the models
class SmartBotMessageType(str, enum.Enum):
    BOT = "bot"
    USER = "user"
    SYSTEM = "system"
    QUESTION = "question"
    INFO = "info"
    ANSWER = "answer"
    COMPLETION = "completion"

# Test the enum value
print(f"SmartBotMessageType.QUESTION = {SmartBotMessageType.QUESTION!r}")
print(f"SmartBotMessageType.QUESTION.value = {SmartBotMessageType.QUESTION.value!r}")
print(f"type(SmartBotMessageType.QUESTION.value) = {type(SmartBotMessageType.QUESTION.value)}")

# Test what happens when we convert to string
print(f"\nString conversion tests:")
print(f"str(SmartBotMessageType.QUESTION) = {str(SmartBotMessageType.QUESTION)!r}")
print(f"repr(SmartBotMessageType.QUESTION) = {repr(SmartBotMessageType.QUESTION)!r}")

# Test JSON serialization
print(f"\nJSON serialization tests:")
try:
    json_with_enum = json.dumps({"type": SmartBotMessageType.QUESTION})
    print(f"json.dumps with enum (should work since it's str enum): {json_with_enum}")
except Exception as e:
    print(f"json.dumps with enum failed: {e}")

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

# Test what happens if we accidentally use the enum without .value
print(f"\nTesting potential issue:")
print(f"SmartBotMessageType.QUESTION (without .value) = {SmartBotMessageType.QUESTION}")
print(f"Is it equal to 'question'? {SmartBotMessageType.QUESTION == 'question'}")
print(f"Is it equal to 'QUESTION'? {SmartBotMessageType.QUESTION == 'QUESTION'}")

# Test if there's any way it could become uppercase
print(f"\nUppercase tests:")
print(f"SmartBotMessageType.QUESTION.name = {SmartBotMessageType.QUESTION.name}")
print(f"SmartBotMessageType.QUESTION.name.upper() = {SmartBotMessageType.QUESTION.name.upper()}")