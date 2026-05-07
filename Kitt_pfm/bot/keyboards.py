"""Inline keyboards for Telegram bot."""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def confirmation_keyboard(confirm_data: str, cancel_data: str = "cancel"):
    """Yes/No confirmation keyboard."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ 確認", callback_data=f"confirm:{confirm_data}"),
            InlineKeyboardButton("❌ 取消", callback_data=cancel_data),
        ]
    ])

def category_selection_keyboard(categories: list, prefix: str = "cat") -> InlineKeyboardMarkup:
    """Category selection keyboard."""
    buttons = []
    row = []
    for i, cat in enumerate(categories):
        icon = cat.get("icon", "")
        name = cat.get("name", "")
        cat_id = cat.get("id", "")
        row.append(
            InlineKeyboardButton(f"{icon} {name}", callback_data=f"{prefix}:{cat_id}")
        )
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton("❌ 取消", callback_data="cancel")])
    return InlineKeyboardMarkup(buttons)

def back_keyboard():
    """Back button."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("← 返回", callback_data="back")]
    ])

def account_selection_keyboard(accounts: list) -> InlineKeyboardMarkup:
    """Account selection keyboard."""
    buttons = []
    for acc in accounts:
        name = acc.get("name", "")
        acc_id = acc.get("id", "")
        buttons.append([InlineKeyboardButton(name, callback_data=f"acc:{acc_id}")])
    buttons.append([InlineKeyboardButton("❌ 取消", callback_data="cancel")])
    return InlineKeyboardMarkup(buttons)
