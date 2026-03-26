import os
import json
import asyncio
import aiohttp
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ============================================
# SETTINGS
# ============================================
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Sabse stable URL Gemini 1.5 Flash ke liye
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_API_KEY}"
# ============================================

PROMPT_TEMPLATE = """Tu ek expert viral video script writer hai jo Hinglish mein likhta hai.
PRODUCT: Trading Journal Template
TOPIC: {topic}

Return SIRF valid JSON (no markdown):
{{
  "hook": "Opening lines",
  "full_script": "Poora Hinglish script",
  "youtube_title": "YouTube title",
  "description": "YouTube description",
  "instagram_caption": "Instagram caption",
  "hashtags": "#trading #journal",
  "keywords": "trading tips",
  "thumbnail_text": "Bold text",
  "elevenlabs_script": "Clean voiceover script"
}}"""

async def call_gemini(topic: str) -> dict:
    payload = {
        "contents": [{
            "parts": [{
                "text": PROMPT_TEMPLATE.format(topic=topic)
            }]
        }]
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(GEMINI_URL, json=payload, timeout=30) as resp:
            if resp.status == 200:
                data = await resp.json()
                raw = data["candidates"][0]["content"]["parts"][0]["text"]
                cleaned = raw.replace("```json", "").replace("```", "").strip()
                return json.loads(cleaned)
            else:
                err_msg = await resp.text()
                raise Exception(f"Google API Error {resp.status}: {err_msg}")

def format_message(result: dict) -> str:
    return f"""🔥 *VIRAL VIDEO PACKAGE READY!*

━━━━━━━━━━━━━━━━━━━━
🪝 *HOOK:* {result['hook']}

📝 *SCRIPT:* {result['full_script']}

🎙️ *VOICEOVER:* _{result['elevenlabs_script']}_

▶️ *TITLE:* {result['youtube_title']}
📸 *INSTA:* {result['instagram_caption']}
#️⃣ *TAGS:* {result['hashtags']}
━━━━━━━━━━━━━━━━━━━━
🚀 Upload karo aur viral ho jao!"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📈 *Trading Journal Bot Live!*\nKoi bhi topic likho (e.g. `loss`) script ke liye.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic = update.message.text.strip()
    loading = await update.message.reply_text("⏳ Generating script...")
    
    try:
        result = await call_gemini(topic)
        message = format_message(result)
        await loading.delete()
        await update.message.reply_text(message, parse_mode="Markdown")
    except Exception as e:
        if loading: await loading.delete()
        await update.message.reply_text(f"❌ Error: {str(e)}")

def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
