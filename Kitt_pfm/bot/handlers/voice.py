"""Voice message handler — Whisper STT."""
import os
import subprocess
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

from Kitt_pfm.services import transaction as trans_svc
from Kitt_pfm.services import category as cat_svc
from Kitt_pfm.services import account as account_svc
from Kitt_pfm.services.nlu import parse_natural_language
from Kitt_pfm.utils.currency import format_jpy
from Kitt_pfm.bot.handlers.text import handle_natural_language

# Load Whisper model once at startup
_model = None

def get_whisper_model():
    global _model
    if _model is None:
        _model = whisper.load_model("base")
    return _model


async def handle_voice(update: Update, context: CallbackContext):
    """Handle voice messages — transcribe and try to parse as transaction."""
    if not WHISPER_AVAILABLE:
        await update.message.reply_text(
            "❌ 語音轉文字功能尚未啟用。\n"
            "請先安裝 whisper：pip install openai-whisper"
        )
        return

    await update.message.reply_text("🎙️ 收到語音，正在轉換文字...")

    # Download voice file
    voice = update.message.voice
    file = await context.bot.get_file(voice.file_id)

    ogg_path = f"/tmp/voice_{voice.file_id}.ogg"
    mp3_path = f"/tmp/voice_{voice.file_id}.mp3"

    await file.download_to_drive(ogg_path)

    # Convert OGG to MP3 using ffmpeg
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", ogg_path, "-ar", "16000", "-ac", "1", mp3_path],
            check=True, capture_output=True
        )
    except subprocess.CalledProcessError as e:
        await update.message.reply_text(f"❌ 音訊轉換失敗：{e}")
        return

    # Transcribe with Whisper
    try:
        model = get_whisper_model()
        result = model.transcribe(mp3_path, language="ja")
        text = result["text"].strip()

        if not text or result.get("language") == "zh":
            result_zh = model.transcribe(mp3_path, language="zh")
            if result_zh["text"].strip():
                text = result_zh["text"]

    except Exception as e:
        await update.message.reply_text(f"❌ 語音轉換失敗：{e}")
        return
    finally:
        for p in [ogg_path, mp3_path]:
            if os.path.exists(p):
                os.remove(p)

    if not text:
        await update.message.reply_text("❌ 無法識別語音內容，請再說一次。")
        return

    # Show transcribed text and ask for confirmation
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ 記帳", callback_data=f"voice_add:{voice.file_id}"),
            InlineKeyboardButton("❌ 取消", callback_data="cancel"),
        ]
    ])

    await update.message.reply_text(
        f"🎙️ 辨識結果：\n「{text}」\n\n"
        f"要嘗試記帳嗎？",
        reply_markup=keyboard
    )

    context.bot_data[f"voice_{voice.file_id}"] = text
