"""
KITT PFM API Server
FastAPI backend serving data from PostgreSQL on Render
"""
import os
import uuid
from datetime import date
from typing import Optional
from collections import defaultdict

import asyncpg
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ── Database ─────────────────────────────────────────────────────────
DATABASE_URL = os.environ.get("DATABASE_URL")
# Fallback for local dev
LOCAL_DB = "/Users/nickwengsoocii/kitt-pfm/data/kitt_pfm.db"

pool = None

async def get_pool():
    global pool
    if pool is None:
        if DATABASE_URL:
            pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=5)
        else:
            raise RuntimeError("DATABASE_URL not set")
    return pool

# ── Pydantic models ───────────────────────────────────────────────────
class TransactionOut(BaseModel):
    id: str
    date: str
    amount: float
    currency: str
    category_id: Optional[str]
    category_name: Optional[str]
    category_icon: Optional[str]
    description: str
    merchant: str

class CategorySummary(BaseModel):
    category_id: str
    category_name: str
    category_icon: str
    total: float
    count: int

class MonthSummary(BaseModel):
    year: int
    month: int
    total: float
    by_category: list[CategorySummary]
    transactions: list[TransactionOut]

class TransactionCreate(BaseModel):
    date: str
    amount: float
    category_id: str
    description: str
    merchant: str = ""

# ── App ───────────────────────────────────────────────────────────────
app = FastAPI(title="KITT PFM API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    global pool
    if DATABASE_URL:
        pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=5)

@app.on_event("shutdown")
async def shutdown():
    global pool
    if pool:
        pool.close()

# ── Routes ────────────────────────────────────────────────────────────
@app.get("/api/health")
def health():
    return {"status": "ok", "kitt": "online", "db": "postgres"}

@app.get("/api/transactions", response_model=list[TransactionOut])
async def list_transactions(limit: int = 50, offset: int = 0):
    p = await get_pool()
    async with p.acquire() as conn:
        rows = await conn.fetch("""
            SELECT t.*, c.name as cat_name, c.icon as cat_icon
            FROM transactions t
            LEFT JOIN categories c ON t.category_id = c.id
            ORDER BY t.date DESC, t.created_at DESC
            LIMIT $1 OFFSET $2
        """, limit, offset)
        return [
            TransactionOut(
                id=r["id"],
                date=r["date"],
                amount=abs(r["amount"]),
                currency="JPY",
                category_id=r["category_id"],
                category_name=r.get("cat_name"),
                category_icon=r.get("cat_icon"),
                description=r["description"] or "",
                merchant=r["merchant"] or "",
            )
            for r in rows
        ]

@app.get("/api/summary/{year}/{month}", response_model=MonthSummary)
async def month_summary(year: int, month: int):
    p = await get_pool()
    start = f"{year}-{month:02d}-01"
    if month == 12:
        end = f"{year+1}-01-01"
    else:
        end = f"{year}-{month+1:02d}-01"

    async with p.acquire() as conn:
        rows = await conn.fetch("""
            SELECT t.*, c.name as cat_name, c.icon as cat_icon
            FROM transactions t
            LEFT JOIN categories c ON t.category_id = c.id
            WHERE t.date >= $1 AND t.date < $2
            ORDER BY t.date DESC
        """, start, end)

        transactions = [
            TransactionOut(
                id=r["id"],
                date=r["date"],
                amount=abs(r["amount"]),
                currency="JPY",
                category_id=r["category_id"],
                category_name=r.get("cat_name"),
                category_icon=r.get("cat_icon"),
                description=r["description"] or "",
                merchant=r["merchant"] or "",
            )
            for r in rows
        ]

        by_cat = defaultdict(lambda: {"total": 0.0, "count": 0, "name": "", "icon": ""})
        total = 0.0
        for r in rows:
            cat_id = r["category_id"] or "other"
            by_cat[cat_id]["total"] += abs(r["amount"])
            by_cat[cat_id]["count"] += 1
            by_cat[cat_id]["name"] = r["cat_name"] or "其他"
            by_cat[cat_id]["icon"] = r["cat_icon"] or "📦"
            total += abs(r["amount"])

        categories = [
            CategorySummary(
                category_id=cat_id,
                category_name=data["name"],
                category_icon=data["icon"],
                total=round(data["total"], 2),
                count=data["count"],
            )
            for cat_id, data in sorted(by_cat.items(), key=lambda x: -x[1]["total"])
        ]

        return MonthSummary(
            year=year, month=month,
            total=round(total, 2),
            by_category=categories,
            transactions=transactions,
        )

@app.get("/api/categories")
async def list_categories():
    p = await get_pool()
    async with p.acquire() as conn:
        rows = await conn.fetch("SELECT id, name, icon FROM categories ORDER BY name")
        return [{"id": r["id"], "name": r["name"], "icon": r["icon"]} for r in rows]

@app.post("/api/transactions")
async def create_transaction(tx: TransactionCreate):
    p = await get_pool()
    async with p.acquire() as conn:
        # Check category
        cat = await conn.fetchrow("SELECT id FROM categories WHERE id = $1", tx.category_id)
        if not cat:
            raise HTTPException(status_code=400, detail=f"Category '{tx.category_id}' not found")

        # Get first account
        acc = await conn.fetchrow("SELECT id FROM accounts LIMIT 1")
        if not acc:
            raise HTTPException(status_code=400, detail="No account found")

        tx_id = f"tx-{uuid.uuid4().hex[:8]}"
        await conn.execute("""
            INSERT INTO transactions (id, account_id, date, amount, category_id, description, merchant, created_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, NOW())
        """, tx_id, acc["id"], tx.date, -abs(tx.amount), tx.category_id, tx.description, tx.merchant)
        return {"id": tx_id, "status": "created"}

@app.delete("/api/transactions/{tx_id}")
async def delete_transaction(tx_id: str):
    p = await get_pool()
    async with p.acquire() as conn:
        result = await conn.execute("DELETE FROM transactions WHERE id = $1", tx_id)
        if result == "DELETE 0":
            raise HTTPException(status_code=404, detail="Transaction not found")
        return {"status": "deleted"}

@app.get("/api/accounts")
async def list_accounts():
    p = await get_pool()
    async with p.acquire() as conn:
        rows = await conn.fetch("SELECT id, name, type, balance, currency FROM accounts")
        return [dict(r) for r in rows]

class AccountTypeSummary(BaseModel):
    type: str
    total: float
    accounts: list[dict]

class AssetsSummary(BaseModel):
    total_assets: float
    total_debt: float
    net_worth: float
    by_type: list[AccountTypeSummary]
    accounts: list[dict]

@app.get("/api/assets", response_model=AssetsSummary)
async def assets_summary():
    p = await get_pool()
    async with p.acquire() as conn:
        rows = await conn.fetch("SELECT id, name, type, balance, currency FROM accounts ORDER BY type, name")

        by_type = defaultdict(lambda: {"total": 0.0, "accounts": []})
        total_assets = 0.0
        total_debt = 0.0

        for acc in rows:
            t = acc["type"]
            bal = acc["balance"] or 0.0
            by_type[t]["total"] += bal
            by_type[t]["accounts"].append(dict(acc))
            if t in ("bank", "securities", "e_money", "cash", "other"):
                total_assets += bal
            elif t in ("credit_card", "loan"):
                total_debt += abs(bal)

        return AssetsSummary(
            total_assets=round(total_assets, 2),
            total_debt=round(total_debt, 2),
            net_worth=round(total_assets - total_debt, 2),
            by_type=[
                AccountTypeSummary(type=t, total=round(d["total"], 2), accounts=d["accounts"])
                for t, d in sorted(by_type.items())
            ],
            accounts=[dict(r) for r in rows],
        )

@app.post("/api/accounts")
async def create_account(name: str, type: str, balance: float = 0.0, currency: str = "JPY"):
    p = await get_pool()
    async with p.acquire() as conn:
        acc_id = f"acc-{uuid.uuid4().hex[:8]}"
        await conn.execute(
            "INSERT INTO accounts (id, name, type, balance, currency, created_at) VALUES ($1, $2, $3, $4, $5, NOW())",
            acc_id, name, type, balance, currency
        )
        return {"id": acc_id, "status": "created"}

@app.put("/api/accounts/{acc_id}")
async def update_account(acc_id: str, name: str = None, balance: float = None):
    p = await get_pool()
    async with p.acquire() as conn:
        if name is not None:
            await conn.execute("UPDATE accounts SET name = $1 WHERE id = $2", name, acc_id)
        if balance is not None:
            await conn.execute("UPDATE accounts SET balance = $1 WHERE id = $2", balance, acc_id)
        return {"status": "updated"}

@app.delete("/api/accounts/{acc_id}")
async def delete_account(acc_id: str):
    p = await get_pool()
    async with p.acquire() as conn:
        await conn.execute("DELETE FROM accounts WHERE id = $1", acc_id)
        return {"status": "deleted"}

# ── Budget ───────────────────────────────────────────────────────────
class BudgetSummary(BaseModel):
    category_id: str
    category_name: str
    category_icon: str
    budget_amount: float
    actual_amount: float
    remaining: float
    percentage: float

class BudgetsData(BaseModel):
    budgets: list[BudgetSummary]
    total_budget: float
    total_actual: float

@app.get("/api/budgets/{year}/{month}", response_model=BudgetsData)
async def get_budgets(year: int, month: int):
    p = await get_pool()
    start = f"{year}-{month:02d}-01"
    if month == 12:
        end = f"{year+1}-01-01"
    else:
        end = f"{year}-{month+1:02d}-01"

    async with p.acquire() as conn:
        budget_rows = await conn.fetch("""
            SELECT b.id, b.category_id, b.amount as budget_amount,
                   c.name as cat_name, c.icon as cat_icon
            FROM budgets b
            LEFT JOIN categories c ON b.category_id = c.id
            WHERE b.period = 'monthly'
        """)

        actual_rows = await conn.fetch("""
            SELECT category_id, SUM(ABS(amount)) as actual
            FROM transactions
            WHERE date >= $1 AND date < $2 AND amount < 0
            GROUP BY category_id
        """, start, end)
        actual_map = {r["category_id"]: r["actual"] for r in actual_rows}

        summaries = []
        total_budget = 0.0
        total_actual = 0.0

        for b in budget_rows:
            actual = actual_map.get(b["category_id"], 0.0)
            remaining = b["budget_amount"] - actual
            pct = (actual / b["budget_amount"] * 100) if b["budget_amount"] > 0 else 0.0
            summaries.append(BudgetSummary(
                category_id=b["category_id"],
                category_name=b["cat_name"] or "其他",
                category_icon=b["cat_icon"] or "📦",
                budget_amount=b["budget_amount"],
                actual_amount=round(actual, 2),
                remaining=round(remaining, 2),
                percentage=round(pct, 1),
            ))
            total_budget += b["budget_amount"]
            total_actual += actual

        return BudgetsData(
            budgets=summaries,
            total_budget=round(total_budget, 2),
            total_actual=round(total_actual, 2),
        )

@app.post("/api/budgets")
async def create_budget(category_id: str, amount: float, period: str = "monthly"):
    p = await get_pool()
    async with p.acquire() as conn:
        budget_id = f"bud-{uuid.uuid4().hex[:8]}"
        await conn.execute(
            "INSERT INTO budgets (id, category_id, amount, period) VALUES ($1, $2, $3, $4)",
            budget_id, category_id, amount, period
        )
        return {"id": budget_id, "status": "created"}

@app.delete("/api/budgets/{budget_id}")
async def delete_budget(budget_id: str):
    p = await get_pool()
    async with p.acquire() as conn:
        await conn.execute("DELETE FROM budgets WHERE id = $1", budget_id)
        return {"status": "deleted"}

# ── Fixed Costs ──────────────────────────────────────────────────────
class FixedCost(BaseModel):
    id: str
    name: str
    amount: float
    category_id: str
    category_name: str
    category_icon: str
    due_day: int

@app.get("/api/fixed-costs", response_model=list[FixedCost])
async def get_fixed_costs():
    p = await get_pool()
    async with p.acquire() as conn:
        rows = await conn.fetch("""
            SELECT fc.id, fc.name, fc.amount, fc.category_id,
                   c.name as cat_name, c.icon as cat_icon, fc.due_day
            FROM fixed_costs fc
            LEFT JOIN categories c ON fc.category_id = c.id
            ORDER BY fc.due_day
        """)
        return [
            FixedCost(
                id=r["id"], name=r["name"], amount=r["amount"],
                category_id=r["category_id"], category_name=r["cat_name"] or "",
                category_icon=r["cat_icon"] or "📦", due_day=r["due_day"]
            )
            for r in rows
        ]

@app.post("/api/fixed-costs")
async def create_fixed_cost(name: str, amount: float, category_id: str, due_day: int):
    p = await get_pool()
    async with p.acquire() as conn:
        fc_id = f"fc-{uuid.uuid4().hex[:8]}"
        await conn.execute(
            "INSERT INTO fixed_costs (id, name, amount, category_id, due_day) VALUES ($1, $2, $3, $4, $5)",
            fc_id, name, amount, category_id, due_day
        )
        return {"id": fc_id, "status": "created"}

@app.delete("/api/fixed-costs/{fc_id}")
async def delete_fixed_cost(fc_id: str):
    p = await get_pool()
    async with p.acquire() as conn:
        await conn.execute("DELETE FROM fixed_costs WHERE id = $1", fc_id)
        return {"status": "deleted"}

# ── Main ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8765))
    uvicorn.run(app, host="0.0.0.0", port=port, reload=False)
