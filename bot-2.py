import os
import json
import asyncio
import aiohttp
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ============================================
# SETTINGS (Railway Variables)
# ============================================
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY")

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
# ============================================

PROMPT_TEMPLATE = """Tu ek expert viral video script writer hai jo Hinglish mein likhta hai.
PRODUCT: Trading Journal Template (Excel/Google Sheets)
TOPIC: {topic}

Return ONLY valid JSON (no markdown):
{{
  "hook": "Opening viral lines",
  "full_script": "45-60 sec Hinglish script",
  "youtube_title": "YouTube title with emojis",
  "description": "YouTube description + link: arkcreator.gumroad.com/l/avstxm",
  "instagram_caption": "Insta caption with hashtags",
  "hashtags": "#trading #journal #stockmarket",
  "keywords": "trading tips, stock market",
  "thumbnail_text": "Bold text (Max 5 words)",
  "elevenlabs_script": "Clean script for voiceover"
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

async def get_pexels_videos(query: str):
    """Pexels se portrait trading videos nikalne ke liye"""
    headers = {"Authorization": PEXELS_API_KEY}
    # Search query ko refine karna (trading keyword add karke)
    search_query = f"{query} trading stock market"
    url = f"https://api.pexels.com/videos/search?query={search_query}&per_page=3&orientation=portrait"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            # Sabse high quality link nikalna (Hing-res)
            video_links = [v['video_files'][0]['link'] for v in data.get('videos', [])]
            return video_links
    except Exception as e:
        print(f"Pexels Error: {e}")
    return []

def format_message(result: dict) -> str:
    return f"""🔥 *VIRAL VIDEO PACKAGE READY!*

━━━━━━━━━━━━━━━━━━━━
🪝 *HOOK (Stop the Scroll):*
{result['hook']}

📝 *FULL SCRIPT (Hinglish):*
{result['full_script']}

🎙️ *ELEVENLABS VOICEOVER:*
_{result['elevenlabs_script']}_

▶️ *YOUTUBE TITLE:*
{result['youtube_title']}

📸 *INSTAGRAM CAPTION:*
{result['instagram_caption']}

🖼️ *THUMBNAIL TEXT:*
`{result['thumbnail_text']}`

━━━━━━━━━━━━━━━━━━━━
✅ ElevenLabs se voice nikalo aur niche diye gaye footage use karo! 🚀"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📈 *Trading Video Engine Active!*\n\n"
        "Topic likho (e.g. `discipline`, `loss recovery`) "
        "main script aur video footage dono bhej dunga!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic = update.message.text.strip()
    loading = await update.message.reply_text("⏳ *Processing: AI Writing & Finding Footage...*")
    
    try:
        # 1. AI se script mangwana
        result = await call_ai(topic)
        
        # 2. Pexels se portrait videos dhundhna
        video_urls = await get_pexels_videos(topic)
        
        # 3. Message format karke bhejna
        message = format_message(result)
        await loading.delete()
        await update.message.reply_text(message, parse_mode="Markdown")
        
        # 4. Videos bhejna agar mile toh
        if video_urls:
            await update.message.reply_text("🎬 *Download these Footage for your Reel:*")
            for url in video_urls:
                await update.message.reply_video(video=url, caption="Stock Footage (9:16)")
        else:
            await update.message.reply_text("⚠️ No matching footage found, but script is ready!")
            
    except Exception as e:
        if loading: await loading.delete()
        await update.message.reply_text(f"❌ Error: {str(e)}")

def main():
    print("🤖 Starting Bot...")
    if not TELEGRAM_BOT_TOKEN or not GROQ_API_KEY or not PEXELS_API_KEY:
        print("❌ Error: Railway Variables (Token/Groq/Pexels) missing!")
        return

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("✅ Bot is Live on Railway!")
    app.run_polling()

if __name__ == "__main__":
    main()
