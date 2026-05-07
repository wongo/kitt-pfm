-- KITT PFM Database Schema

CREATE TABLE IF NOT EXISTS accounts (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('bank','credit_card','securities','e_money','cash','loan','other')),
    balance REAL DEFAULT 0,
    currency TEXT DEFAULT 'JPY',
    created_at TEXT DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS categories (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    icon TEXT DEFAULT '',
    color TEXT DEFAULT '',
    parent_id TEXT REFERENCES categories(id),
    is_system INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS transactions (
    id TEXT PRIMARY KEY,
    account_id TEXT NOT NULL REFERENCES accounts(id),
    date TEXT NOT NULL,
    amount REAL NOT NULL,
    category_id TEXT REFERENCES categories(id),
    description TEXT DEFAULT '',
    merchant TEXT DEFAULT '',
    notes TEXT DEFAULT '',
    is_confirmed INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS budgets (
    id TEXT PRIMARY KEY,
    category_id TEXT NOT NULL REFERENCES categories(id),
    amount REAL NOT NULL,
    period TEXT DEFAULT 'monthly',
    created_at TEXT DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT
);

INSERT OR IGNORE INTO categories (id, name, icon, is_system) VALUES
    ('cat-dining', '餐飲', '🍜', 1),
    ('cat-shopping', '購物', '🛒', 1),
    ('cat-transport', '交通', '🚃', 1),
    ('cat-entertainment', '娛樂', '🎮', 1),
    ('cat-healthcare', '醫療', '💊', 1),
    ('cat-insurance', '保險', '🏥', 1),
    ('cat-housing', '住房', '🏠', 1),
    ('cat-telecom', '通訊', '📱', 1),
    ('cat-education', '教育', '📚', 1),
    ('cat-investment', '投資', '📈', 1),
    ('cat-income', '收入', '💰', 1),
    ('cat-transfer', '轉帳', '🔄', 1),
    ('cat-other', '其他', '📦', 1);

CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date);
CREATE INDEX IF NOT EXISTS idx_transactions_category ON transactions(category_id);
CREATE INDEX IF NOT EXISTS idx_transactions_account ON transactions(account_id);
