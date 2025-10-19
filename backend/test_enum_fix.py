import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from sqlalchemy.orm import Session
from sqlalchemy import text
from core.db import get_db
from models.chat import SmartBotMessageType

def test_enum_fix():
    db = next(get_db())
    try:
        print('🔍 Testing SmartBotMessageType enum serialization...')
        test_enums = [SmartBotMessageType.QUESTION, SmartBotMessageType.ANSWER, SmartBotMessageType.USER, SmartBotMessageType.BOT, SmartBotMessageType.SYSTEM, SmartBotMessageType.INFO, SmartBotMessageType.COMPLETION]
        for enum_val in test_enums:
            print(f"✅ {enum_val.name} -> value: '{enum_val.value}' (type: {type(enum_val.value)})")
        print('\n🔍 Testing direct SQL insertion...')
        for enum_val in test_enums:
            try:
                result = db.execute(text('SELECT CAST(:enum_value AS smartbotmessagetype)'), {'enum_value': enum_val.value})
                fetched_value = result.fetchone()[0]
                print(f"✅ SQL test for {enum_val.name}: '{enum_val.value}' -> '{fetched_value}'")
            except Exception as e:
                print(f"❌ SQL test failed for {enum_val.name} ('{enum_val.value}'): {e}")
                return False
        print('\n✅ All enum tests passed - the fix is working correctly!')
        return True
    except Exception as e:
        print(f'❌ Test failed with error: {e}')
        return False
    finally:
        db.close()
if __name__ == '__main__':
    success = test_enum_fix()
    sys.exit(0 if success else 1)
