import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from models.chat import SmartBotMessageType

# Test enum values
print("Testing enum values:")
print(f"SmartBotMessageType.ANSWER = {SmartBotMessageType.ANSWER}")
print(f"SmartBotMessageType.ANSWER.value = {SmartBotMessageType.ANSWER.value}")
print(f"SmartBotMessageType.COMPLETION = {SmartBotMessageType.COMPLETION}")
print(f"SmartBotMessageType.COMPLETION.value = {SmartBotMessageType.COMPLETION.value}")

# Test string representation
print(f"\nString representation:")
print(f"str(SmartBotMessageType.ANSWER) = {str(SmartBotMessageType.ANSWER)}")
print(f"str(SmartBotMessageType.COMPLETION) = {str(SmartBotMessageType.COMPLETION)}")

# Test enum name vs value
print(f"\nEnum name vs value:")
print(f"SmartBotMessageType.ANSWER.name = {SmartBotMessageType.ANSWER.name}")
print(f"SmartBotMessageType.ANSWER.value = {SmartBotMessageType.ANSWER.value}")