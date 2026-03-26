import os
import json
import asyncio
import aiohttp
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ============================================
# SETTINGS (Keys Railway Variables se aayengi)
# ============================================
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Check if keys exist
if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN":
    raise ValueError("ERROR: TELEGRAM_BOT_TOKEN missing in Railway Variables!")

if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_GEMINI_KEY":
    raise ValueError("ERROR: GEMINI_API_KEY missing in Railway Variables!")

GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_API_KEY}"

PROMPT_TEMPLATE = """Tu ek expert viral video script writer hai jo Hinglish mein likhta hai.

PRODUCT: Trading Journal Template (Excel/Google Sheets)
TARGET: Beginner aur Intermediate stock/crypto traders - India
GOAL: Template direct sell karna - paid product

Ek viral YouTube Short / Instagram Reel script banao jo {topic} angle se Trading Journal Template promote kare.

IMPORTANT RULES:
- Language: Hinglish (Hindi + English mix) - bilkul natural bolchal
- Length: 45-60 seconds (130-160 words max)
- Hook: Pehle 3 second mein trader ka dard ya curiosity trigger karo
- Pain points use karo: "loss track nahi hota", "emotions se trade karte ho", "kab profit hua yaad nahi"
- Solution: Trading Journal Template se sab organized, disciplined trading
- Social proof angle: "successful traders yahi karte hain"
- CTA: End mein "Link bio mein hai" ya "arkcreator.gumroad.com pe available hai" - price BILKUL mat batao
- NEVER generic raho - hamesha trading specific bolo
- Gumroad link: arkcreator.gumroad.com/l/avstxm (description mein use karo)

VIRAL ANGLES (topic se match karo):
- Loss ke baad wapsi story
- Successful trader ka secret
- Ye galti mat karo trading mein
- Kitne % traders fail karte hain aur kyun
- Discipline = profit formula
- Trading journal = trading ka game changer

Return SIRF valid JSON (kuch aur bilkul mat likho, no markdown):
{{
  "hook": "Opening 1-2 lines jo trader scroll rokde - dard ya curiosity",
  "full_script": "Poora 45-60 sec Hinglish script - trading journal promote kare",
  "youtube_title": "YouTube title with emojis (max 60 chars) - trading focused",
  "description": "YouTube description 150 words - trading journal benefits + CTA + link: arkcreator.gumroad.com/l/avstxm (price mat likho)",
  "instagram_caption": "Instagram caption with emojis (max 150 chars) - punchy",
  "hashtags": "#tradingjournal #stockmarket #trading #tradingtips #stocktrading #nifty #sensex #cryptotrading #forextrading #tradingstrategy #tradingpsychology #learntrading #tradinglife #indiatrading #sharemarket",
  "keywords": "trading journal template, stock market journal, trading tracker excel, trade log sheet, trading discipline",
  "thumbnail_text": "Max 5 words - bold thumbnail text for trading video",
  "elevenlabs_script": "Same as full_script but clean - no emojis, no special chars, natural speech"
}}"""

async def call_gemini(topic: str) -> dict:
    payload = {
        "contents": [{
            "parts": [{
                "text": PROMPT_TEMPLATE.format(topic=topic)
            }]
        }],
        "generationConfig": {
            "temperature": 0.9,
            "maxOutputTokens": 1500
        }
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(GEMINI_URL, json=payload) as resp:
            data = await resp.json()
            if "candidates" not in data:
                 raise Exception(f"Gemini API Error: {data}")
            
    raw = data["candidates"][0]["content"]["parts"][0]["text"]
    # Clean JSON
    cleaned = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(cleaned)

def format_message(result: dict) -> str:
    return f"""🔥 *VIRAL VIDEO PACKAGE READY!*

━━━━━━━━━━━━━━━━━━━━
🪝 *VIRAL HOOK:*
{result['hook']}

━━━━━━━━━━━━━━━━━━━━
📝 *FULL SCRIPT:*
{result['full_script']}

━━━━━━━━━━━━━━━━━━━━
🎙️ *ELEVENLABS VOICEOVER:*
_{result['elevenlabs_script']}_

━━━━━━━━━━━━━━━━━━━━
▶️ *YOUTUBE TITLE:*
{result['youtube_title']}

📄 *DESCRIPTION:*
{result['description']}

━━━━━━━━━━━━━━━━━━━━
📸 *INSTAGRAM CAPTION:*
{result['instagram_caption']}

━━━━━━━━━━━━━━━━━━━━
#️⃣ *HASHTAGS:*
{result['hashtags']}

🔑 *KEYWORDS:*
{result['keywords']}

🖼️ *THUMBNAIL TEXT:*
`{result['thumbnail_text']}`

━━━━━━━━━━━━━━━━━━━━
✅ ElevenLabs mein voiceover script paste karo
✅ Pexels se footage lo
✅ VN Editor mein edit karo
✅ Upload karo aur viral ho jao! 🚀"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📈 *Trading Journal Video Bot Active!*\n\n"
        "Main aapke *Trading Journal Template* ke liye "
        "viral Hinglish scripts banata hoon!\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "📌 *Yeh topics try karo:*\n\n"
        "• `loss` - Loss kyun hota hai traders ko\n"
        "• `discipline` - Trading discipline secret\n"
        "• `beginner` - Beginners ke liye tips\n"
        "• `psychology` - Trading psychology\n"
        "• `mistake` - Common trading mistakes\n"
        "• `profit` - Consistent profit formula\n\n"
        "Ya `/video` type karo random script ke liye!\n\n"
        "_Bas ek word type karo - 30 sec mein ready!_ 🚀",
        parse_mode="Markdown"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 *Commands:*\n\n"
        "/start - Bot shuru karo\n"
        "/video - Random viral video script\n"
        "/help - Yeh message\n\n"
        "Ya seedha topic type karo! 💪",
        parse_mode="Markdown"
    )

async def generate_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic = "random viral trading topic - loss recovery, discipline, psychology, beginner mistakes, profit consistency"
    await handle_generation(update, topic)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic = update.message.text.strip()
    await handle_generation(update, topic)

async def handle_generation(update: Update, topic: str):
    loading = await update.message.reply_text(
        "⏳ Viral video script ban raha hai...\n"
        "_30 seconds mein ready hoga!_",
        parse_mode="Markdown"
    )
    
    try:
        result = await call_gemini(topic)
        message = format_message(result)
        await loading.delete()
        
        if len(message) > 4000:
            await update.message.reply_text(message[:4000], parse_mode="Markdown")
        else:
            await update.message.reply_text(message, parse_mode="Markdown")
            
        await update.message.reply_text(
            "🎯 *Next Steps:* ElevenLabs → Pexels → VN Editor → Upload!",
            parse_mode="Markdown"
        )
        
    except Exception as e:
        if loading: await loading.delete()
        await update.message.reply_text(f"❌ Error: {str(e)}")

def main():
    print("🤖 Viral Video Bot starting...")
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("video", generate_video))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("✅ Bot ready! Polling started...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
