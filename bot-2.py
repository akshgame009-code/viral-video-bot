import os
import json
import asyncio
import aiohttp
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ============================================
# SETTINGS (Railway Variables se Keys load hongi)
# ============================================
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
# ============================================

PROMPT_TEMPLATE = """Tu ek expert viral video script writer hai jo Hinglish mein likhta hai.

PRODUCT: Trading Journal Template (Excel/Google Sheets)
TOPIC: {topic}

Return SIRF valid JSON (no markdown, no extra text):
{{
  "hook": "Opening 1-2 lines jo trader scroll rokde",
  "full_script": "Poora 45-60 sec Hinglish script",
  "youtube_title": "YouTube title with emojis",
  "description": "YouTube description + link: arkcreator.gumroad.com/l/avstxm",
  "instagram_caption": "Instagram caption with emojis",
  "hashtags": "#tradingjournal #stockmarket #trading",
  "keywords": "trading journal template, stock market journal",
  "thumbnail_text": "Max 5 words bold text",
  "elevenlabs_script": "Clean script for voiceover"
}}"""

async def call_gemini(topic: str) -> dict:
    payload = {
        "contents": [{
            "parts": [{
                "text": PROMPT_TEMPLATE.format(topic=topic)
            }]
        }]
    }
    
    # In 3 URLs mein se jo bhi kaam karega, bot use use karega
    urls = [
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_API_KEY}",
        f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}",
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
    ]
    
    async with aiohttp.ClientSession() as session:
        last_error = ""
        for url in urls:
            try:
                async with session.post(url, json=payload, timeout=30) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        raw = data["candidates"][0]["content"]["parts"][0]["text"]
                        # Markdown code blocks saaf karna
                        cleaned = raw.replace("```json", "").replace("```", "").strip()
                        return json.loads(cleaned)
                    else:
                        err_resp = await resp.text()
                        last_error = f"URL Failed ({url}): {err_resp}"
                        continue # Agla URL try karein
            except Exception as e:
                last_error = f"Error: {str(e)}"
                continue
                
        raise Exception(f"Sare Models fail ho gaye. Check API Key or Region. Last Error: {last_error}")

def format_message(result: dict) -> str:
    return f"""🔥 *VIRAL VIDEO PACKAGE READY!*

━━━━━━━━━━━━━━━━━━━━
🪝 *VIRAL HOOK:*
{result['hook']}

📝 *FULL SCRIPT:*
{result['full_script']}

🎙️ *ELEVENLABS VOICEOVER:*
_{result['elevenlabs_script']}_

▶️ *YOUTUBE TITLE:*
{result['youtube_title']}

📄 *DESCRIPTION:*
{result['description']}

📸 *INSTAGRAM CAPTION:*
{result['instagram_caption']}

#️⃣ *HASHTAGS:*
{result['hashtags']}

🔑 *KEYWORDS:*
{result['keywords']}

🖼️ *THUMBNAIL TEXT:*
`{result['thumbnail_text']}`

━━━━━━━━━━━━━━━━━━━━
✅ ElevenLabs → Pexels → VN Editor → Upload! 🚀"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📈 *Trading Journal Video Bot Active!*\n\n"
        "Koi bhi trading topic likho, main viral script bana dunga!\n"
        "Example: `loss recovery`, `discipline`, `beginner mistakes`"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic = update.message.text.strip()
    loading = await update.message.reply_text("⏳ *Viral script generate ho raha hai...*")
    
    try:
        result = await call_gemini(topic)
        message = format_message(result)
        await loading.delete()
        await update.message.reply_text(message, parse_mode="Markdown")
        
    except Exception as e:
        if loading: await loading.delete()
        await update.message.reply_text(f"❌ Error: {str(e)}")

def main():
    print("🤖 Starting Bot...")
    if not TELEGRAM_BOT_TOKEN or not GEMINI_API_KEY:
        print("❌ Error: Railway Variables mein API Keys nahi mili!")
        return

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("✅ Bot is Live on Railway!")
    app.run_polling()

if __name__ == "__main__":
    main()
