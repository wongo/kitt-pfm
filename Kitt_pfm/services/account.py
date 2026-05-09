"""Account service."""
import uuid
import aiosqlite
from Kitt_pfm.config import DB_PATH

ACCOUNT_TYPES = {
    "bank": "🏦 銀行",
    "credit_card": "💳 信用卡",
    "securities": "📈 證券",
    "e_money": "📱 電子貨幣",
    "cash": "💵 現金",
    "loan": "🏦 貸款",
    "other": "📦 其他",
}

async def get_all_accounts():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        rows = await db.execute("SELECT * FROM accounts ORDER BY created_at DESC")
        return await rows.fetchall()

async def get_account_by_id(acc_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM accounts WHERE id = ?", (acc_id,))
        return await cursor.fetchone()

async def create_account(name: str, acc_type: str, balance: float = 0, currency: str = "JPY") -> str:
    acc_id = f"acc-{uuid.uuid4().hex[:8]}"
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO accounts (id, name, type, balance, currency) VALUES (?, ?, ?, ?, ?)",
            (acc_id, name, acc_type, balance, currency)
        )
        await db.commit()
    return acc_id

async def update_balance(acc_id: str, new_balance: float):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE accounts SET balance = ? WHERE id = ?", (new_balance, acc_id))
        await db.commit()

async def get_total_balance():
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT SUM(balance) FROM accounts WHERE type != 'loan'")
        row = await cursor.fetchone()
        return row[0] or 0

async def delete_account(acc_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM transactions WHERE account_id = ?", (acc_id,))
        await db.execute("DELETE FROM accounts WHERE id = ?", (acc_id,))
        await db.commit()

async def list_accounts(user_id: str):
    """List all accounts for a user."""
    return await get_all_accounts()
