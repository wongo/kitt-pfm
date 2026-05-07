"""Photo/receipt handler — OpenRouter Vision OCR."""
import os
import base64
import httpx
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from Kitt_pfm.services import transaction as trans_svc
from Kitt_pfm.services import category as cat_svc


async def handle_photo(update: Update, context: CallbackContext):
    """Handle photo messages — OCR via OpenRouter (Gemini Vision)."""
    await update.message.reply_text("🧾 收到圖片，正在分析收據...")

    # Download photo
    photo = update.message.photo[-1]  # Highest resolution
    file = await context.bot.get_file(photo.file_id)

    img_path = f"/tmp/receipt_{photo.file_id}.jpg"
    await file.download_to_drive(img_path)

    try:
        # Encode image as base64
        with open(img_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode()

        api_key = os.environ.get("OPENROUTER_API_KEY", "") or os.environ.get("AUXILIARY_VISION_API_KEY", "")
        if not api_key:
            await update.message.reply_text("❌ 未設定視覺 API Key，請聯繫管理員。")
            return

        # Call OpenRouter Gemini Vision
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "google/gemini-2.5-flash",
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{img_b64}"
                                    },
                                },
                                {
                                    "type": "text",
                                    "text": (
                                        "請閱讀這張收據，擷取所有消費項目：\n"
                                        "1. 列出每個項目的名稱、數量、單價（幣別為日幣 JPY）\n"
                                        "2. 列出小計和總金額\n"
                                        "3. 如果有日期，標註消費日期\n"
                                        "4. 用 Markdown 格式回覆，條列清晰"
                                    ),
                                },
                            ],
                        }
                    ],
                },
            )
            resp.raise_for_status()
            result = resp.json()

        # Extract text from response
        choices = result.get("choices", [{}])
        raw_text = choices[0].get("message", {}).get("content", "") if choices else ""

        if not raw_text.strip():
            await update.message.reply_text(
                "❌ 無法從圖片中讀取文字，請稍後再試。"
            )
            return

    except Exception as e:
        await update.message.reply_text(f"❌ 圖片分析失敗：{e}")
        return
    finally:
        if os.path.exists(img_path):
            os.remove(img_path)

    # Store result for confirmation
    context.bot_data[f"receipt_{photo.file_id}"] = raw_text

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ 記帳", callback_data=f"receipt_add:{photo.file_id}"),
            InlineKeyboardButton("❌ 取消", callback_data="cancel"),
        ]
    ])

    # Show preview (first 400 chars)
    preview = raw_text.strip()[:400]

    await update.message.reply_text(
        f"🧾 辨識結果：\n\n{preview}\n\n要確認記帳嗎？",
        reply_markup=keyboard,
    )
