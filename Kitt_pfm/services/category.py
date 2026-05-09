"""Category service."""
import uuid
import aiosqlite
from Kitt_pfm.config import DB_PATH

async def get_all_categories():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        rows = await db.execute("SELECT * FROM categories ORDER BY is_system DESC, name")
        return await rows.fetchall()

async def get_category_by_name(name: str):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM categories WHERE name LIKE ?",
            (f"%{name}%",)
        )
        return await cursor.fetchone()

async def get_category_by_id(cat_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM categories WHERE id = ?", (cat_id,))
        return await cursor.fetchone()

async def create_category(name: str, icon: str = "") -> str:
    cat_id = f"cat-{uuid.uuid4().hex[:8]}"
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO categories (id, name, icon, is_system) VALUES (?, ?, ?, 0)",
            (cat_id, name, icon)
        )
        await db.commit()
    return cat_id

async def get_or_create_category(user_id: str, name: str) -> str:
    """Get existing category by name or create new one."""
    # First try to find existing
    existing = await get_category_by_name(name)
    if existing:
        return existing["id"]
    
    # Create new with default icon
    return await create_category(name, "")

async def list_categories(user_id: str):
    """List all categories (system + user)."""
    return await get_all_categories()
