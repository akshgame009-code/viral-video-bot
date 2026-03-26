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

PROMPT_TEMPLATE = """Tu ek A-Grade Viral Ghostwriter hai. 
PRODUCT: 'AKSH.AI Trading Journal'.
TOPIC: {topic}

Return ONLY valid JSON:
{{
  "hook": "Psychological Viral Hook",
  "full_script": "High-retention Hinglish script with 'Bro' and 'Bhai'",
  "youtube_title": "Clickbait Title with Emoji",
  "description": "Short description + Link: arkcreator.gumroad.com/l/avstxm",
  "instagram_caption": "Viral Caption + 15 Hashtags",
  "thumbnail_text": "Shocking text (Max 4 words)",
  "elevenlabs_script": "Clean voiceover script",
  "image_prompt": "Cinematic trading background, professional candlestick charts, dark aesthetic, neon glowing blue and red lines, 8k resolution, photorealistic, 16:9 ratio"
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
                return json.loads(data['choices'][0]['message']['content'])
            else:
                raise Exception(f"Groq AI Error: {resp.status}")

async def get_pexels_videos(query: str):
    headers = {"Authorization": PEXELS_API_KEY}
    # Optimized search query for trading
    search_url = f"https://api.pexels.com/videos/search?query=trading stock market&per_page=2&orientation=portrait"
    
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return [v['video_files'][0]['link'] for v in data.get('videos', [])]
    except:
        pass
    return []

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic = update.message.text.strip()
    loading = await update.message.reply_text("⏳ *Generating Viral Content Package...*")
    
    try:
        # 1. AI Script & Image Prompt mangwana
        result = await call_ai(topic)
        
        # 2. Pexels Videos dhundna
        video_urls = await get_pexels_videos(topic)
        
        # 3. AI Thumbnail Image URL (Pollinations AI)
        image_url = f"https://pollinations.ai/p/{result['image_prompt'].replace(' ', '%20')}?width=1280&height=720&seed=42"

        # 4. Response bhejna
        await loading.delete()
        
        # A. Sabse pehle Thumbnail Photo
        await update.message.reply_photo(
            photo=image_url, 
            caption=f"🖼️ *Thumbnail Background*\nText to use: `{result['thumbnail_text']}`"
        )
        
        # B. Script Details
        msg = (
            f"🔥 *HOOK (Start the Video):*\n{result['hook']}\n\n"
            f"📝 *FULL SCRIPT:*\n{result['full_script']}\n\n"
            f"🎙️ *VOICEOVER SCRIPT:*\n`{result['elevenlabs_script']}`\n\n"
            f"📸 *INSTA CAPTION:*\n{result['instagram_caption']}\n\n"
            f"🚀 *LINK:* arkcreator.gumroad.com/l/avstxm"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")
        
        # C. Reels Video Footage
        if video_urls:
            await update.message.reply_text("🎬 *Portrait Video Footage for Reel:*")
            for v_url in video_urls:
                await update.message.reply_video(video=v_url)
                
    except Exception as e:
        await update.message.reply_text(f"❌ *Error:* {str(e)}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 *Trading Studio Bot Active!*\nTopic bhejo aur full content ready-made pao!")

def main():
    if not TELEGRAM_BOT_TOKEN: return
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ Studio Bot Running...")
    app.run_polling()

if __name__ == "__main__":
    main()
