# KITT PFM

> Your finances. Your machine. Your KITT.

A privacy-first, locally-running personal finance manager controlled through Telegram.

## Quick Start

```bash
# 1. Clone and install
cd kitt-pfm
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
# Edit .env — add your Telegram bot token from @BotFather

# 3. Run
python -m kitt_pfm.main
```

## First Use

1. Open Telegram and start a chat with your bot
2. Send `/start`
3. Add your first account: `/account 三井住友銀行 bank 1234567`
4. Start recording expenses!

## Features

- **Text input:** `/add 890 餐飲 松屋`
- **Natural language:** "今天uber eats 2480"
- **Voice:** Just send a voice message
- **Receipt scan:** Send a photo
- **Query:** `/stats`, `/bal`, `/budget`

## Requirements

- Python 3.11+
- ffmpeg (for voice processing)
- Telegram bot token ([get from @BotFather](https://t.me/BotFather))

## Project Structure

```
kitt-pfm/
├── kitt_pfm/          # Main package
│   ├── bot/           # Telegram bot handlers
│   ├── db/            # Database layer
│   ├── services/      # Business logic (Telegram-agnostic)
│   └── utils/         # Helpers
├── tests/             # Tests
└── data/              # SQLite DB (gitignored)
```

## Architecture

```
┌─────────────────────────────────────┐
│           Telegram Chat            │
│  (text / voice / photo messages)    │
└─────────────────┬───────────────────┘
                  │
        ┌─────────▼─────────┐
        │   Bot Handlers    │
        │  (python-telegram │
        │      -bot)        │
        └─────┬─────────┬───┘
              │         │
    ┌─────────▼──┐   ┌──▼────────┐
    │  Services  │   │  Services │
    │  (NLU/STT) │   │ (CRUD)    │
    └─────┬──────┘   └─────┬─────┘
          │                │
    ┌─────▼────────────────▼─────┐
    │      Database Layer        │
    │      (SQLite + aiosqlite)  │
    └────────────────────────────┘
```

## License

MIT

---

*Built with KITT energy.*
