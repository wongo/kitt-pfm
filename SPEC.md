# KITT PFM — Personal Finance Manager

## 1. Concept & Vision

KITT PFM is a privacy-first, locally-running personal finance manager controlled entirely through Telegram. Unlike cloud-based services (MoneyForward), all data stays on your machine. The interface is KITT — cold, precise, slightly sarcastic, and efficient. You talk to KITT in natural language (Chinese, Japanese, or English), and KITT handles the rest.

**Tagline:** "Your finances. Your machine. Your KITT."

## 2. Design Language

**Personality:** KITT — calm, precise, dry wit, competent
**Interface:** Telegram (voice, text, photo)
**Database:** SQLite (local file, portable)
**Language:** Python 3.11+

## 3. Core Features

### 3.1 Text Commands
- `/start` — Welcome message + quick tutorial
- `/add <amount> <category> [note]` — Add expense (e.g., `/add 890 餐飲 松屋`)
- `/income <amount> [source]` — Record income
- `/balance` or `/bal` — Show total balance across all accounts
- `/budget [category] [amount]` — Set or check budget
- `/stats` — This month's spending by category
- `/month` — This month's transaction list
- `/accounts` — List all accounts
- `/account <name> <type> [balance]` — Add account
- `/categories` or `/cat` — List categories
- `/search <query>` — Search transactions
- `/help` — Show all commands
- `/export` — Export this month's data as CSV

### 3.2 Natural Language Processing
KITT understands casual说话:
- "今天uber eats 2480" → Add expense
- "記一筆 餐飲 松屋 890" → Structured add
- "薪水32萬" → Income entry
- "這個月餐飲花了多少" → Query
- "我的總資產" → Balance check

### 3.3 Voice Input
- Send voice message → Whisper STT → Parse → Confirm → Record
- Supports: Chinese, Japanese, English
- Flow: Record → Transcribe → Extract (amount, category, merchant, date) → Confirm → Save

### 3.4 Receipt OCR (Phase 2)
- Send photo → Tesseract OCR → Extract (merchant, date, total, line items)
- Confirm → Save

## 4. Data Model

### Account
- id (UUID)
- name (string)
- type (enum: bank, credit_card, securities, e_money, cash, loan, other)
- balance (decimal)
- currency (default: JPY)
- created_at (datetime)

### Transaction  
- id (UUID)
- account_id (FK)
- date (date)
- amount (decimal, negative=expense, positive=income)
- category_id (FK)
- description (string)
- merchant (string, optional)
- notes (string, optional)
- is_confirmed (bool)
- created_at (datetime)

### Category
- id (UUID)
- name (string, unique)
- icon (emoji)
- color (hex, optional)
- parent_id (FK, optional) — for subcategories
- is_system (bool) — system categories can't be deleted
- created_at (datetime)

### Budget
- id (UUID)
- category_id (FK)
- amount (decimal, monthly limit)
- period (enum: monthly, weekly, yearly)
- created_at (datetime)

### Settings
- key (string, PK)
- value (JSON)

## 5. Default Categories

| Icon | Name (ZH) | Name (EN) | Name (JA) |
|------|-----------|-----------|-----------|
| 🍜 | 餐飲 | Dining | 餐饮 |
| 🛒 | 購物 | Shopping | 购物 |
| 🚃 | 交通 | Transport | 交通 |
| 🎮 | 娛樂 | Entertainment | 娯楽 |
| 💊 | 醫療 | Healthcare | 医療 |
| 🏥 | 保險 | Insurance | 保険 |
| 🏠 | 住房 | Housing | 住居 |
| 📱 | 通訊 | Telecom | 通信 |
| 📚 | 教育 | Education | 教育 |
| 📈 | 投資 | Investment | 投資 |
| 💰 | 收入 | Income | 収入 |
| 🔄 | 轉帳 | Transfer | 振替 |
| 📦 | 其他 | Other | その他 |

## 6. Project Structure

```
kitt-pfm/
├── SPEC.md
├── README.md
├── requirements.txt
├── .env.example
├── kitt_pfm/
│   ├── __init__.py
│   ├── main.py              # Entry point
│   ├── config.py            # Env configuration
│   ├── bot/
│   │   ├── __init__.py
│   │   ├── app.py           # Telegram bot instance
│   │   ├── handlers/
│   │   │   ├── __init__.py
│   │   │   ├── text.py      # Text command handlers
│   │   │   ├── voice.py     # Voice message handler
│   │   │   └── photo.py     # Photo/receipt handler
│   │   └── keyboards.py    # Inline keyboards
│   ├── db/
│   │   ├── __init__.py
│   │   ├── database.py      # SQLite connection
│   │   ├── schema.sql       # DDL
│   │   └── models.py        # Data classes
│   ├── services/
│   │   ├── __init__.py
│   │   ├── transaction.py   # Transaction CRUD
│   │   ├── account.py      # Account CRUD
│   │   ├── budget.py       # Budget logic
│   │   ├── category.py     # Category management
│   │   ├── nlu.py          # Natural language parser
│   │   └── stt.py          # Speech-to-text (Whisper)
│   └── utils/
│       ├── __init__.py
│       ├── currency.py      # Currency formatting
│       └── date_utils.py   # Date parsing
├── tests/
│   └── test_nlu.py
└── data/
    └── kitt_pfm.db         # SQLite database file
```

## 7. Technology Stack

- **Language:** Python 3.11+
- **Telegram Bot:** python-telegram-bot v20+
- **Database:** SQLite + aiosqlite (async)
- **STT:** OpenAI Whisper (local, via subprocess or API)
- **OCR:** pytesseract + Pillow (local)
- **NLP:** Rule-based parser (Phase 1), upgradeable to LLM later
- **Config:** python-dotenv
- **Testing:** pytest

## 8. Environment Variables

```
TELEGRAM_BOT_TOKEN=        # From @BotFather
WHISPER_MODEL=base         # tiny, base, small, medium, large
TZ=Asia/Tokyo              # Timezone
DATA_DIR=./data            # Where SQLite DB lives
LOG_LEVEL=INFO             # DEBUG, INFO, WARNING, ERROR
```

## 9. Non-Goals (Out of Scope for MVP)

- Multi-user support (SQLite is single-user by nature)
- Cloud deployment
- Automatic bank sync
- Mobile app
- Web UI
- Budget alerts via push notifications (Telegram already does this)

## 10. Open Source Considerations

The architecture is designed to be modular so future contributors can:
- Swap SQLite → PostgreSQL for multi-user
- Replace Whisper → any STT API
- Replace python-telegram-bot → Node.js or Rust bot
- Add a web UI on top of the service layer

All business logic lives in `services/` — the Telegram bot is just one interface.
