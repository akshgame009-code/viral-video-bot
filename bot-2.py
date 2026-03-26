import os
import json
import asyncio
import aiohttp
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ============================================
# SETTINGS
# ============================================
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

PROMPT_TEMPLATE = """Tu ek A-Grade Viral Ghostwriter hai. 
PRODUCT: 'AKSH.AI Trading Journal'. TOPIC: {topic}
Return ONLY valid JSON:
{{
  "hook": "Viral Hook",
  "full_script": "Hinglish script",
  "thumbnail_text": "Bold text",
  "elevenlabs_script": "Voiceover script",
  "image_prompt": "Cinematic trading background dark neon 16:9",
  "insta_caption": "Caption with hashtags"
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
            data = await resp.json()
            return json.loads(data['choices'][0]['message']['content'])

async def get_pexels_videos():
    headers = {"Authorization": PEXELS_API_KEY}
    url = "https://api.pexels.com/videos/search?query=trading&per_page=2&orientation=portrait"
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            return [v['video_files'][0]['link'] for v in resp.json().get('videos', [])]
    except: pass
    return []

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic = update.message.text.strip()
    loading = await update.message.reply_text("⏳ *Processing your Viral Package...*")
    
    try:
        res = await call_ai(topic)
        videos = await get_pexels_videos()
        # Image URL with fixed dimensions
        img_url = f"https://image.pollinations.ai/prompt/{res['image_prompt'].replace(' ', '%20')}?width=1280&height=720&nologo=true"

        await loading.delete()

        # 1. Send Thumbnail Image
        try:
            await update.message.reply_photo(photo=img_url, caption=f"🖼️ *Thumbnail Base*\nText: `{res['thumbnail_text']}`")
        except:
            await update.message.reply_text(f"🖼️ [Download Thumbnail]({img_url})", parse_mode="Markdown")

        # 2. Send Script
        msg = f"🔥 *HOOK:* {res['hook']}\n\n📝 *SCRIPT:* {res['full_script']}\n\n🎙️ *VOICEOVER:* `{res['elevenlabs_script']}`\n\n📸 *CAPTION:* {res['insta_caption']}"
        await update.message.reply_text(msg)

        # 3. Send Videos
        if videos:
            await update.message.reply_text("🎬 *Reel Footage:*")
            for v in videos:
                try:
                    await update.message.reply_video(video=v)
                except:
                    await update.message.reply_text(f"🔗 [Video Link]({v})", parse_mode="Markdown")

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", lambda u,c: u.message.reply_text("Studio Active!")))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__": main()
