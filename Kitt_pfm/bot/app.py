"""Telegram Bot application setup."""
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from Kitt_pfm.bot.handlers.text import (
    cmd_start, cmd_help, cmd_add, cmd_spend, cmd_income,
    cmd_balance, cmd_stats, cmd_month, cmd_accounts, cmd_account,
    cmd_budget, cmd_categories, cmd_search, handle_natural_language,
)
from Kitt_pfm.bot.handlers.voice import handle_voice
from Kitt_pfm.bot.handlers.photo import handle_photo
from Kitt_pfm.bot.handlers.callback import handle_callback

def create_app(token: str):
    """Build and configure the Telegram bot application."""
    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("add", cmd_add))
    app.add_handler(CommandHandler("spend", cmd_spend))
    app.add_handler(CommandHandler("income", cmd_income))
    app.add_handler(CommandHandler(["balance", "bal"], cmd_balance))
    app.add_handler(CommandHandler("stats", cmd_stats))
    app.add_handler(CommandHandler("month", cmd_month))
    app.add_handler(CommandHandler(["accounts", "acc"], cmd_accounts))
    app.add_handler(CommandHandler("account", cmd_account))
    app.add_handler(CommandHandler(["budget", "bgt"], cmd_budget))
    app.add_handler(CommandHandler(["categories", "cat"], cmd_categories))
    app.add_handler(CommandHandler("search", cmd_search))

    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_natural_language))

    return app
