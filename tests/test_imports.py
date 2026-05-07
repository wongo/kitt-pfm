"""Quick import test — run this to verify all modules load correctly."""
import sys
sys.path.insert(0, ".")

print("Testing imports...")

try:
    from Kitt_pfm.config import TELEGRAM_BOT_TOKEN, DB_PATH, WHISPER_MODEL
    print(f"✅ config: DB_PATH={DB_PATH}")
except Exception as e:
    print(f"❌ config: {e}")

try:
    from Kitt_pfm.db.database import init_db_sync
    print("✅ database")
except Exception as e:
    print(f"❌ database: {e}")

try:
    from Kitt_pfm.services.category import get_all_categories
    print("✅ services.category")
except Exception as e:
    print(f"❌ services.category: {e}")

try:
    from Kitt_pfm.services.account import create_account
    print("✅ services.account")
except Exception as e:
    print(f"❌ services.account: {e}")

try:
    from Kitt_pfm.services.transaction import add_transaction
    print("✅ services.transaction")
except Exception as e:
    print(f"❌ services.transaction: {e}")

try:
    from Kitt_pfm.services.nlu import parse_natural_language
    print("✅ services.nlu")
except Exception as e:
    print(f"❌ services.nlu: {e}")

try:
    from Kitt_pfm.utils.currency import format_jpy
    print("✅ utils.currency")
except Exception as e:
    print(f"❌ utils.currency: {e}")

try:
    from Kitt_pfm.utils.date_utils import format_date_chinese
    print("✅ utils.date_utils")
except Exception as e:
    print(f"❌ utils.date_utils: {e}")

try:
    from Kitt_pfm.bot.keyboards import confirmation_keyboard
    print("✅ bot.keyboards")
except Exception as e:
    print(f"❌ bot.keyboards: {e}")

print("\nAll import tests complete.")
