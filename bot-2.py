import os
import json
import asyncio
import aiohttp
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ============================================
# SETTINGS (Railway Variables se uthayega)
# ============================================
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY")

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
# ============================================

PROMPT_TEMPLATE = """Tu ek expert viral video script writer hai jo Hinglish mein likhta hai.
PRODUCT: Trading Journal Template (Excel/Google Sheets)
TOPIC: {topic}

Return ONLY valid JSON:
{{
  "hook": "Opening viral lines",
  "full_script": "45-60 sec Hinglish script",
  "youtube_title": "YouTube title with emojis",
  "description": "YouTube description + link: arkcreator.gumroad.com/l/avstxm",
  "instagram_caption": "Insta caption with hashtags",
  "hashtags": "#trading #journal #stockmarket",
  "thumbnail_text": "Bold text",
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
                raise Exception(f"AI Error: {resp.status}")

async def get_pexels_videos(query: str):
    """Pexels se hamesha trading videos nikalne ke liye optimized function"""
    if not PEXELS_API_KEY:
        return "ERROR_NO_KEY", []

    headers = {"Authorization": PEXELS_API_KEY}
    # Query ko simple rakha hai taaki videos pakka milein
    search_query = "trading charts stock market"
    url = f"https://api.pexels.com/videos/search?query={search_query}&per_page=3&orientation=portrait"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            # Sirf un links ko lena jo MP4 format mein hon
            video_links = [v['video_files'][0]['link'] for v in data.get('videos', [])]
            return "SUCCESS", video_links
        else:
            return f"ERROR_{response.status_code}", []
    except Exception as e:
        return f"EXCEPTION_{str(e)}", []

def format_message(result: dict) -> str:
    return f"""🔥 *VIRAL SCRIPT READY!*

🪝 *HOOK:* {result['hook']}

📝 *SCRIPT:* {result['full_script']}

🎙️ *VOICEOVER:* _{result['elevenlabs_script']}_

🖼️ *THUMBNAIL:* {result['thumbnail_text']}

🚀 *Link:* arkcreator.gumroad.com/l/avstxm"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📈 *Trading Bot Active!* Topic likho, main script aur video footage dono dunga.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic = update.message.text.strip()
    loading = await update.message.reply_text("⏳ *AI is working...*")
    
    try:
        # 1. AI Scripting
        result = await call_ai(topic)
        
        # 2. Footage Fetching
        status, video_urls = await get_pexels_videos(topic)
        
        # 3. Message Send
        await loading.delete()
        await update.message.reply_text(format_message(result), parse_mode="Markdown")
        
        # 4. Video Send Logic & Debugging
        if status == "SUCCESS" and video_urls:
            await update.message.reply_text("🎬 *Download these Footage:*")
            for url in video_urls:
                try:
                    await update.message.reply_video(video=url)
                except:
                    await update.message.reply_text(f"🔗 [Video Link]({url})", parse_mode="Markdown")
        elif "ERROR_401" in status:
            await update.message.reply_text("❌ *Pexels Key Error:* Railway Variables mein PEXELS_API_KEY check karo, wo galat hai.")
        elif "ERROR_NO_KEY" in status:
            await update.message.reply_text("❌ *Missing Key:* Railway mein PEXELS_API_KEY variable nahi mila.")
        else:
            await update.message.reply_text("⚠️ No footage found for this topic.")
            
    except Exception as e:
        await update.message.reply_text(f"❌ *System Error:* {str(e)}")

def main():
    if not TELEGRAM_BOT_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN missing!")
        return

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("✅ Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
