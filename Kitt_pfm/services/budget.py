"""Budget service."""
import uuid
import aiosqlite
from Kitt_pfm.config import DB_PATH

async def get_budget(category_id: str = None):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        if category_id:
            cursor = await db.execute(
                "SELECT b.*, c.name as category_name, c.icon as category_icon FROM budgets b JOIN categories c ON b.category_id = c.id WHERE b.category_id = ?",
                (category_id,)
            )
            return await cursor.fetchone()
        else:
            cursor = await db.execute(
                "SELECT b.*, c.name as category_name, c.icon as category_icon FROM budgets b JOIN categories c ON b.category_id = c.id"
            )
            return await cursor.fetchall()

async def set_budget(category_id: str, amount: float, period: str = "monthly") -> str:
    budget_id = f"bgt-{uuid.uuid4().hex[:8]}"
    async with aiosqlite.connect(DB_PATH) as db:
        existing = await db.execute("SELECT id FROM budgets WHERE category_id = ?", (category_id,))
        row = await existing.fetchone()
        if row:
            await db.execute("UPDATE budgets SET amount = ?, period = ? WHERE category_id = ?", (amount, period, category_id))
            await db.commit()
            return row[0]
        else:
            await db.execute(
                "INSERT INTO budgets (id, category_id, amount, period) VALUES (?, ?, ?, ?)",
                (budget_id, category_id, amount, period)
            )
            await db.commit()
            return budget_id

async def delete_budget(category_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM budgets WHERE category_id = ?", (category_id,))
        await db.commit()
