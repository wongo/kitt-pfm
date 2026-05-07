"""Callback query handler — confirmations and selections."""
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from Kitt_pfm.services import transaction as trans_svc
from Kitt_pfm.services import category as cat_svc
from Kitt_pfm.services import account as account_svc
from Kitt_pfm.services.nlu import parse_natural_language
from Kitt_pfm.utils.currency import format_jpy

async def handle_callback(update: Update, context: CallbackContext):
    """Handle all inline button callbacks."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    if not data:
        return
    
    if data == "cancel":
        await query.edit_message_text("❌ 已取消。")
        return
    
    if data == "back":
        await query.edit_message_text("↩️ 已返回。")
        return
    
    parts = data.split(":", 1)
    action = parts[0]
    payload = parts[1] if len(parts) > 1 else ""
    
    # add_cat:{cat_id}:{amount}:{description}
    if action == "add_cat":
        subparts = payload.split(":", 2)
        if len(subparts) < 3:
            await query.edit_message_text("❌ 資料格式錯誤。")
            return
        cat_id, amount_str, description = subparts
        
        try:
            amount = float(amount_str)
        except ValueError:
            await query.edit_message_text("❌ 金額格式錯誤。")
            return
        
        accounts = await account_svc.get_all_accounts()
        if not accounts:
            await query.edit_message_text("❌ 請先建立帳戶：/account 三井住友銀行 bank 100000")
            return
        
        await trans_svc.add_transaction(
            account_id=accounts[0]["id"],
            amount=amount,
            category_id=cat_id,
            description=description,
        )
        
        cat = await cat_svc.get_category_by_id(cat_id)
        icon = cat["icon"] if cat else "📦"
        name = cat["name"] if cat else "其他"
        
        await query.edit_message_text(
            f"✅ 已記錄\n\n"
            f"{icon} 分類：{name}\n"
            f"💰 金額：{format_jpy(amount)}\n"
            f"📝 說明：{description or '（無）'}"
        )
        return
    
    # voice_add:{file_id}
    if action == "voice_add":
        file_id = payload
        text = context.bot_data.get(f"voice_{file_id}", "")
        
        if not text:
            await query.edit_message_text("❌ 找不到語音內容，請重新傳送。")
            return
        
        parsed = await parse_natural_language(text)
        
        if not parsed.get("amount"):
            await query.edit_message_text(
                f"❌ 無法從「{text}」中理解金額。\n"
                f"請用文字描述：/add [金額] [分類] [內容]"
            )
            return
        
        accounts = await account_svc.get_all_accounts()
        if not accounts:
            await query.edit_message_text("❌ 請先建立帳戶：/account 三井住友銀行 bank 100000")
            return
        
        cat_id = None
        if parsed.get("category"):
            cat = await cat_svc.get_category_by_name(parsed["category"])
            if cat:
                cat_id = cat["id"]
        
        if not cat_id:
            cat = await cat_svc.get_category_by_name("其他")
            cat_id = cat["id"] if cat else None
        
        await trans_svc.add_transaction(
            account_id=accounts[0]["id"],
            amount=parsed["amount"],
            category_id=cat_id,
            description=text,
            trans_date=parsed["date"].isoformat() if parsed.get("date") else None,
        )
        
        cat = await cat_svc.get_category_by_id(cat_id)
        icon = cat["icon"] if cat else "📦"
        name = cat["name"] if cat else "其他"
        
        await query.edit_message_text(
            f"✅ 語音已記帳\n\n"
            f"🎙️ 原文：{text}\n\n"
            f"{icon} 分類：{name}\n"
            f"💰 金額：{format_jpy(parsed['amount'])}"
        )
        return
    
    # receipt_add:{file_id}
    if action == "receipt_add":
        file_id = payload
        ocr_text = context.bot_data.get(f"receipt_{file_id}", "")
        
        if not ocr_text:
            await query.edit_message_text("❌ 找不到圖片內容，請重新傳送。")
            return
        
        amounts = re.findall(r'[¥￥]?([\d,]+)', ocr_text)
        
        if not amounts:
            await query.edit_message_text(
                "❌ 無法從收據中讀取金額。\n"
                "請用手動記帳：/add [金額] [分類] [內容]"
            )
            return
        
        amount = max(float(a.replace(",", "")) for a in amounts)
        
        accounts = await account_svc.get_all_accounts()
        if not accounts:
            await query.edit_message_text("❌ 請先建立帳戶：/account 三井住友銀行 bank 100000")
            return
        
        parsed = await parse_natural_language(ocr_text)
        cat_id = None
        if parsed.get("category"):
            cat = await cat_svc.get_category_by_name(parsed["category"])
            if cat:
                cat_id = cat["id"]
        
        if not cat_id:
            cat = await cat_svc.get_category_by_name("其他")
            cat_id = cat["id"] if cat else None
        
        lines = [l.strip() for l in ocr_text.split("\n") if l.strip()]
        merchant = lines[0][:50] if lines else ""
        
        await trans_svc.add_transaction(
            account_id=accounts[0]["id"],
            amount=-abs(amount),
            category_id=cat_id,
            description=merchant,
            notes=ocr_text[:200],
        )
        
        cat = await cat_svc.get_category_by_id(cat_id)
        icon = cat["icon"] if cat else "📦"
        name = cat["name"] if cat else "其他"
        
        await query.edit_message_text(
            f"✅ 收據已記帳\n\n"
            f"🧾 商家：{merchant}\n"
            f"{icon} 分類：{name}\n"
            f"💰 金額：{format_jpy(-abs(amount))}"
        )
        return
    
    await query.edit_message_text(f"未知的操作：{action}")
