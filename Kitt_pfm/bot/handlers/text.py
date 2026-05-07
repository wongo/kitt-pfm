"""Text message handlers for KITT PFM bot."""
import re
from datetime import date
from telegram import Update
from telegram.ext import CallbackContext

from Kitt_pfm.services import account as account_svc
from Kitt_pfm.services import transaction as trans_svc
from Kitt_pfm.services import budget as budget_svc
from Kitt_pfm.services import category as cat_svc
from Kitt_pfm.services.nlu import parse_natural_language
from Kitt_pfm.utils.currency import format_jpy
from Kitt_pfm.utils.date_utils import format_date_chinese, days_left_in_month

ACCOUNT_TYPE_NAMES = {
    "bank": "🏦 銀行",
    "credit_card": "💳 信用卡",
    "securities": "📈 證券",
    "e_money": "📱 電子貨幣",
    "cash": "💵 現金",
    "loan": "🏦 貸款",
    "other": "📦 其他",
}


async def cmd_start(update: Update, context: CallbackContext):
    """Handle /start command."""
    await update.message.reply_text(
        "KITT PFM 啟動。\n\n"
        "我是你的個人財務管家。可以用自然語言跟我說，或者用指令：\n\n"
        "📝 記帳：\n"
        "• /add [金額] [分類] [內容] — 新增支出\n"
        "• /income [金額] [來源] — 記錄收入\n"
        "• /spend [金額] [項目] — 快速支出\n\n"
        "🔍 查詢：\n"
        "• /bal — 總餘額\n"
        "• /stats — 本月統計\n"
        "• /month — 本月交易\n"
        "• /accounts — 帳戶列表\n\n"
        "💡 自然語言也行：\n"
        '"今天uber eats 2480"\n'
        '"薪水32萬"\n\n'
        "發送語音訊息也可以記帳！\n\n"
        "*輸入 /help 查看所有指令*"
    )


async def cmd_help(update: Update, context: CallbackContext):
    """Handle /help command."""
    await update.message.reply_text(
        "*KITT PFM 指令一覽*\n\n"
        "*記帳*\n"
        "`/add [金額] [分類] [內容]` — 新增支出\n"
        "`/spend [金額] [項目]` — 快速支出\n"
        "`/income [金額] [來源]` — 記錄收入\n\n"
        "*查詢*\n"
        "`/bal` — 總資產\n"
        "`/stats` — 本月支出統計\n"
        "`/month` — 本月交易列表\n"
        "`/budget [分類] [金額]` — 設定/查看預算\n"
        "`/accounts` — 帳戶列表\n"
        "`/categories` — 分類列表\n"
        "`/search [關鍵字]` — 搜尋交易\n\n"
        "*工具*\n"
        "`/account [名稱] [類型] [餘額]` — 新增帳戶\n"
        "`/export` — 匯出月報\n\n"
        "直接傳語音也可以記帳！"
    )


async def cmd_add(update: Update, context: CallbackContext):
    """Handle /add command — add transaction with full details."""
    user_id = str(update.effective_user.id)
    args = context.args

    if not args:
        await update.message.reply_text(
            "格式：/add [金額] [分類] [內容]\n"
            "例如：/add 2480 餐飲 uber eats"
        )
        return

    # Parse: /add 金額 分類 內容
    amount_text = args[0] if len(args) > 0 else ""
    category = args[1] if len(args) > 1 else ""
    description = " ".join(args[2:]) if len(args) > 2 else ""

    # Parse amount
    try:
        amount = float(amount_text.replace(",", ""))
    except ValueError:
        await update.message.reply_text(f"金額格式錯誤：{amount_text}")
        return

    if amount <= 0:
        await update.message.reply_text("金額必須大於 0")
        return

    # Resolve category
    if not category:
        categories = await cat_svc.list_categories(user_id)
        await update.message.reply_text(f"請指定分類。現有分類：\n" + "\n".join(f"{c['name']}" for c in categories[:5]))
        return

    category_id = await cat_svc.get_or_create_category(user_id, category)
    if not category_id:
        await update.message.reply_text(f"無法識別分類：{category}")
        return

    # Get default account
    accounts = await account_svc.list_accounts(user_id)
    if not accounts:
        await update.message.reply_text("請先建立帳戶：/account [名稱] [類型]")
        return

    account_id = accounts[0]["id"]

    # Add transaction
    result = await trans_svc.add_transaction(
        user_id=user_id,
        account_id=account_id,
        amount=-abs(amount),
        category_id=category_id,
        description=description or category,
    )

    if result:
        await update.message.reply_text(
            f"已記帳：{format_jpy(amount)}\n"
            f"分類：{category}\n"
            f"說明：{description or '無'}"
        )
    else:
        await update.message.reply_text("記帳失敗，請稍後再試。")


async def cmd_spend(update: Update, context: CallbackContext):
    """Handle /spend — quick expense entry."""
    user_id = str(update.effective_user.id)
    args = context.args

    if not args:
        await update.message.reply_text("格式：/spend [金額] [項目]\n例如：/spend 500 午餐")
        return

    try:
        amount = float(args[0].replace(",", ""))
    except ValueError:
        await update.message.reply_text(f"金額格式錯誤：{args[0]}")
        return

    description = " ".join(args[1:]) if len(args) > 1 else ""

    accounts = await account_svc.list_accounts(user_id)
    if not accounts:
        await update.message.reply_text("請先建立帳戶：/account [名稱] [類型]")
        return

    account_id = accounts[0]["id"]
    category_id = await cat_svc.get_or_create_category(user_id, "其他")

    result = await trans_svc.add_transaction(
        user_id=user_id,
        account_id=account_id,
        amount=-abs(amount),
        category_id=category_id,
        description=description,
    )

    if result:
        await update.message.reply_text(f"已記支出：{format_jpy(amount)} - {description or '其他'}")
    else:
        await update.message.reply_text("記帳失敗。")


async def cmd_income(update: Update, context: CallbackContext):
    """Handle /income — record income."""
    user_id = str(update.effective_user.id)
    args = context.args

    if not args:
        await update.message.reply_text("格式：/income [金額] [來源]\n例如：/income 300000 薪水")
        return

    try:
        amount = float(args[0].replace(",", ""))
    except ValueError:
        await update.message.reply_text(f"金額格式錯誤：{args[0]}")
        return

    description = " ".join(args[1:]) if len(args) > 1 else "收入"

    accounts = await account_svc.list_accounts(user_id)
    if not accounts:
        await update.message.reply_text("請先建立帳戶：/account [名稱] [類型]")
        return

    account_id = accounts[0]["id"]
    category_id = await cat_svc.get_or_create_category(user_id, "收入")

    result = await trans_svc.add_transaction(
        user_id=user_id,
        account_id=account_id,
        amount=abs(amount),
        category_id=category_id,
        description=description,
    )

    if result:
        await update.message.reply_text(f"已記收入：{format_jpy(amount)} - {description}")
    else:
        await update.message.reply_text("記帳失敗。")


async def cmd_balance(update: Update, context: CallbackContext):
    """Handle /balance — show account balances."""
    user_id = str(update.effective_user.id)
    accounts = await account_svc.list_accounts(user_id)

    if not accounts:
        await update.message.reply_text("尚無帳戶。輸入 /account [名稱] [類型] 新增。")
        return

    lines = ["*帳戶餘額：*\n"]
    total = 0.0
    for acc in accounts:
        lines.append(f"{acc['name']}：{format_jpy(acc['balance'])}")
        total += acc["balance"]

    lines.append(f"\n*總計：{format_jpy(total)}*")
    await update.message.reply_text("\n".join(lines))


async def cmd_stats(update: Update, context: CallbackContext):
    """Handle /stats — show monthly statistics."""
    user_id = str(update.effective_user.id)
    today = date.today()
    stats = await trans_svc.get_monthly_stats(user_id, today.year, today.month)

    if not stats:
        await update.message.reply_text("本月尚無記錄。")
        return

    lines = [f"*本月統計（{today.month}月）*\n"]
    lines.append(f"總支出：{format_jpy(stats.get('total_expense', 0))}")
    lines.append(f"總收入：{format_jpy(stats.get('total_income', 0))}")
    lines.append(f"記錄筆數：{stats.get('count', 0)}")

    by_cat = stats.get("by_category", [])
    if by_cat:
        lines.append("\n*支出明細：*")
        for cat_name, amount in sorted(by_cat, key=lambda x: x[1], reverse=True)[:5]:
            lines.append(f"  {cat_name}：{format_jpy(amount)}")

    days_left = days_left_in_month(today)
    daily_avg = stats.get("total_expense", 0) / (30 - days_left) if days_left < 30 else stats.get("total_expense", 0)
    lines.append(f"\n日均支出：{format_jpy(daily_avg)}")
    lines.append(f"本月剩餘：{days_left} 天")

    await update.message.reply_text("\n".join(lines))


async def cmd_month(update: Update, context: CallbackContext):
    """Handle /month — show this month's transactions."""
    user_id = str(update.effective_user.id)
    today = date.today()
    transactions = await trans_svc.list_transactions(user_id, year=today.year, month=today.month)

    if not transactions:
        await update.message.reply_text("本月尚無記錄。")
        return

    lines = [f"*本月記帳（{today.month}月）*\n"]
    for tx in transactions[:20]:
        sign = "+" if tx["amount"] > 0 else ""
        lines.append(
            f"{tx['date']}  {sign}{format_jpy(tx['amount'])}  {tx.get('category_name', '')}  {tx.get('description', '')}"
        )

    if len(transactions) > 20:
        lines.append(f"\n...還有 {len(transactions) - 20} 筆")

    await update.message.reply_text("\n".join(lines))


async def cmd_accounts(update: Update, context: CallbackContext):
    """Handle /accounts — list all accounts."""
    user_id = str(update.effective_user.id)
    accounts = await account_svc.list_accounts(user_id)

    if not accounts:
        await update.message.reply_text("尚無帳戶。\n格式：/account [名稱] [類型]\n類型：bank, credit_card, cash, e_money, securities")
        return

    lines = ["*帳戶列表：*\n"]
    for acc in accounts:
        type_name = ACCOUNT_TYPE_NAMES.get(acc["type"], acc["type"])
        lines.append(f"• {acc['name']}（{type_name}）：{format_jpy(acc['balance'])}")

    await update.message.reply_text("\n".join(lines))


async def cmd_account(update: Update, context: CallbackContext):
    """Handle /account — create or show account."""
    user_id = str(update.effective_user.id)
    args = context.args

    if not args:
        await cmd_accounts(update, context)
        return

    name = args[0]
    acc_type = args[1] if len(args) > 1 else "bank"
    balance = float(args[2].replace(",", "")) if len(args) > 2 else 0.0

    result = await account_svc.create_account(user_id, name, acc_type, balance)
    if result:
        await update.message.reply_text(f"已建立帳戶：{name}（{ACCOUNT_TYPE_NAMES.get(acc_type, acc_type)}）")
    else:
        await update.message.reply_text("建立帳戶失敗。")


async def cmd_budget(update: Update, context: CallbackContext):
    """Handle /budget — set or view budget."""
    user_id = str(update.effective_user.id)
    args = context.args

    if not args:
        budgets = await budget_svc.get_budgets(user_id)
        if not budgets:
            await update.message.reply_text("尚無設定預算。\n格式：/budget [分類] [金額]\n例如：/budget 餐飲 30000")
            return

        lines = ["*本月預算：*\n"]
        for bgt in budgets:
            lines.append(f"  {bgt['category_name']}：{format_jpy(bgt['amount'])}（已用 {format_jpy(bgt.get('spent', 0))}）")
        await update.message.reply_text("\n".join(lines))
        return

    if len(args) < 2:
        await update.message.reply_text("格式：/budget [分類] [金額]\n例如：/budget 餐飲 30000")
        return

    category_name = args[0]
    try:
        amount = float(args[1].replace(",", ""))
    except ValueError:
        await update.message.reply_text(f"金額格式錯誤：{args[1]}")
        return

    category_id = await cat_svc.get_or_create_category(user_id, category_name)
    result = await budget_svc.set_budget(user_id, category_id, amount)
    if result:
        await update.message.reply_text(f"已設定預算：{category_name} {format_jpy(amount)}/月")
    else:
        await update.message.reply_text("設定失敗。")


async def cmd_categories(update: Update, context: CallbackContext):
    """Handle /categories — list categories."""
    user_id = str(update.effective_user.id)
    categories = await cat_svc.list_categories(user_id)

    lines = ["*分類一覽：*\n"]
    for cat in categories:
        lines.append(f"  {cat['icon']} {cat['name']}")

    await update.message.reply_text("\n".join(lines))


async def cmd_search(update: Update, context: CallbackContext):
    """Handle /search — search transactions."""
    user_id = str(update.effective_user.id)
    args = context.args

    if not args:
        await update.message.reply_text("格式：/search [關鍵字]\n例如：/search uber")
        return

    keyword = " ".join(args)
    transactions = await trans_svc.search_transactions(user_id, keyword)

    if not transactions:
        await update.message.reply_text(f"找不到包含「{keyword}」的記錄。")
        return

    lines = [f"*搜尋「{keyword}」結果：*\n"]
    for tx in transactions[:15]:
        sign = "+" if tx["amount"] > 0 else ""
        lines.append(
            f"{tx['date']}  {sign}{format_jpy(tx['amount'])}  {tx.get('category_name', '')}  {tx.get('description', '')}"
        )

    await update.message.reply_text("\n".join(lines))


async def handle_natural_language(update: Update, context: CallbackContext):
    """Handle free-form text input using NLU."""
    user_id = str(update.effective_user.id)
    text = update.message.text.strip()

    result = parse_natural_language(text)

    if not result.get("amount"):
        await update.message.reply_text(
            f"無法解析：{text}\n\n"
            "可用指令：\n"
            "• /spend [金額] [項目] — 記支出\n"
            "• /income [金額] [來源] — 記收入\n"
            "• /add [金額] [分類] [內容] — 詳細記帳"
        )
        return

    amount = result["amount"]
    category_name = result.get("category", "其他")
    description = result.get("description", "")
    tx_type = result.get("type", "expense")

    # Get or create account
    accounts = await account_svc.list_accounts(user_id)
    if not accounts:
        await update.message.reply_text("請先建立帳戶：/account [名稱] [類型]")
        return

    account_id = accounts[0]["id"]
    category_id = await cat_svc.get_or_create_category(user_id, category_name)

    final_amount = -abs(amount) if tx_type == "expense" else abs(amount)

    tx_result = await trans_svc.add_transaction(
        user_id=user_id,
        account_id=account_id,
        amount=final_amount,
        category_id=category_id,
        description=description,
    )

    if tx_result:
        sign = "" if tx_type == "expense" else "+"
        await update.message.reply_text(
            f"已記帳！\n"
            f"{sign}{format_jpy(amount)}  {category_name}\n"
            f"說明：{description or '無'}"
        )
    else:
        await update.message.reply_text("記帳失敗，請稍後再試。")
