"""Transaction service."""
import uuid
import aiosqlite
from datetime import date
from Kitt_pfm.config import DB_PATH

async def add_transaction(
    account_id: str,
    amount: float,
    category_id: str,
    description: str = "",
    merchant: str = "",
    notes: str = "",
    trans_date: str = None,
    is_confirmed: bool = True,
) -> str:
    trans_id = f"txn-{uuid.uuid4().hex[:8]}"
    if trans_date is None:
        trans_date = date.today().isoformat()
    
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT INTO transactions 
               (id, account_id, date, amount, category_id, description, merchant, notes, is_confirmed)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (trans_id, account_id, trans_date, amount, category_id, description, merchant, notes, 1 if is_confirmed else 0)
        )
        await db.commit()
    return trans_id

async def get_transactions(limit: int = 50, offset: int = 0, category_id: str = None, account_id: str = None, start_date: str = None, end_date: str = None):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        query = "SELECT t.*, c.name as category_name, c.icon as category_icon FROM transactions t LEFT JOIN categories c ON t.category_id = c.id WHERE 1=1"
        params = []
        if category_id:
            query += " AND t.category_id = ?"
            params.append(category_id)
        if account_id:
            query += " AND t.account_id = ?"
            params.append(account_id)
        if start_date:
            query += " AND t.date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND t.date <= ?"
            params.append(end_date)
        query += " ORDER BY t.date DESC, t.created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        rows = await db.execute(query, params)
        return await rows.fetchall()

async def get_month_transactions(year: int = None, month: int = None):
    if year is None:
        today = date.today()
        year, month = today.year, today.month
    start = f"{year}-{month:02d}-01"
    if month == 12:
        end = f"{year+1}-01-01"
    else:
        end = f"{year}-{month+1:02d}-01"
    return await get_transactions(limit=500, start_date=start, end_date=end)

async def delete_transaction(trans_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM transactions WHERE id = ?", (trans_id,))
        await db.commit()

async def get_spending_by_category(year: int = None, month: int = None):
    if year is None:
        today = date.today()
        year, month = today.year, today.month
    start = f"{year}-{month:02d}-01"
    if month == 12:
        end = f"{year+1}-01-01"
    else:
        end = f"{year}-{month+1:02d}-01"
    
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        rows = await db.execute(
            """SELECT c.id, c.name, c.icon, SUM(t.amount) as total
               FROM transactions t
               JOIN categories c ON t.category_id = c.id
               WHERE t.amount < 0 AND t.date >= ? AND t.date < ?
               GROUP BY c.id ORDER BY total ASC""",
            (start, end)
        )
        return await rows.fetchall()

async def search_transactions(query: str, limit: int = 20):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        pattern = f"%{query}%"
        rows = await db.execute(
            """SELECT t.*, c.name as category_name, c.icon as category_icon
               FROM transactions t
               LEFT JOIN categories c ON t.category_id = c.id
               WHERE t.description LIKE ? OR t.merchant LIKE ?
               ORDER BY t.date DESC LIMIT ?""",
            (pattern, pattern, limit)
        )
        return await rows.fetchall()

async def get_month_income(year: int = None, month: int = None):
    if year is None:
        today = date.today()
        year, month = today.year, today.month
    start = f"{year}-{month:02d}-01"
    if month == 12:
        end = f"{year+1}-01-01"
    else:
        end = f"{year}-{month+1:02d}-01"
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT SUM(amount) FROM transactions WHERE amount > 0 AND date >= ? AND date < ?",
            (start, end)
        )
        row = await cursor.fetchone()
        return row[0] or 0

async def get_month_expense(year: int = None, month: int = None):
    if year is None:
        today = date.today()
        year, month = today.year, today.month
    start = f"{year}-{month:02d}-01"
    if month == 12:
        end = f"{year+1}-01-01"
    else:
        end = f"{year}-{month+1:02d}-01"
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT SUM(amount) FROM transactions WHERE amount < 0 AND date >= ? AND date < ?",
            (start, end)
        )
        row = await cursor.fetchone()
        return abs(row[0]) or 0
