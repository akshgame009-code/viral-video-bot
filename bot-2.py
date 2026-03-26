import os
import json
import asyncio
import aiohttp
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ============================================
# SETTINGS (Railway Variables)
# ============================================
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY") 
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
# ============================================

PROMPT_TEMPLATE = """Tu ek expert viral video script writer hai jo Hinglish mein likhta hai.
PRODUCT: Trading Journal Template
TOPIC: {topic}

Return ONLY valid JSON:
{{
  "hook": "Opening viral lines",
  "full_script": "45-60 sec Hinglish script",
  "youtube_title": "YouTube title with emojis",
  "description": "YouTube description + link: arkcreator.gumroad.com/l/avstxm",
  "instagram_caption": "Insta caption",
  "hashtags": "#trading #journal",
  "keywords": "trading",
  "thumbnail_text": "Bold text",
  "elevenlabs_script": "Clean voiceover"
}}"""

async def call_ai(topic: str) -> dict:
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": PROMPT_TEMPLATE.format(topic=topic)}],
        "response_format": {"type": "json_object"}
    }
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    
    async with aiohttp.ClientSession() as session:
        async with session.post(GROQ_URL, json=payload, headers=headers) as resp:
            if resp.status == 200:
                data = await resp.json()
                content = data['choices'][0]['message']['content']
                return json.loads(content)
            else:
                raise Exception(f"AI Error: {await resp.text()}")

def format_message(result: dict) -> str:
    return f"🔥 *VIRAL SCRIPT READY!*\n\n*HOOK:* {result['hook']}\n\n*SCRIPT:* {result['full_script']}\n\n*VOICEOVER:* {result['elevenlabs_script']}\n\n🚀 *Upload & Go Viral!*"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📈 Bot Live! Type a topic.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic = update.message.text.strip()
    loading = await update.message.reply_text("⏳ Writing script...")
    try:
        result = await call_ai(topic)
        await loading.delete()
        await update.message.reply_text(format_message(result), parse_mode="Markdown")
    except Exception as e:
        await loading.edit_text(f"❌ Error: {str(e)}")

def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
