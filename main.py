import os
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
)

# --- konfigurace z ENV ---
BOT_TOKEN = os.environ["BOT_TOKEN"]
BASE_URL   = os.environ["BASE_URL"]   # např. https://your-service.onrender.com
PORT       = int(os.environ.get("PORT", 5000))

# --- Flask server pro healthcheck (a pro PTB webhook receiver) ---
app = Flask(__name__)

# --- Telegram Bot (python-telegram-bot v20+) ---
bot_app = ApplicationBuilder().token(BOT_TOKEN).build()

# ========== HANDLERY ==========

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("🇨🇿 Čeština", callback_data="lang_cs"),
            InlineKeyboardButton("🌍 English", callback_data="lang_en"),
        ]
    ]
    await update.message.reply_text(
        "☕️ Welcome to Coffee Perk!\n"
        "We’re happy to see you here. 🌟\n"
        "Please choose your language. 🗣️",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

# jazykové menu
async def lang_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    code = update.callback_query.data

    if code == "lang_cs":
        text = "Na co se mě můžeš zeptat:"
        keys = [
            ("🧾 Menu a nabídka",  "menu_cs"),
            ("🕐 Otevírací doba",   "hours_cs"),
            ("📍 Kde nás najdete",  "where_cs"),
            ("📞 Kontakt / Rezervace","contact_cs"),
            ("📦 Předobjednávka",    "preorder_cs"),
            ("😎 Proč k nám?",       "why_cs"),
        ]
    else:
        text = "What can you ask me:"
        keys = [
            ("🧾 Menu & Offer",       "menu_en"),
            ("🕐 Opening Hours",      "hours_en"),
            ("📍 Location",           "where_en"),
            ("📞 Contact / Booking",  "contact_en"),
            ("📦 Pre-order",          "preorder_en"),
            ("😎 Why Visit",          "why_en"),
        ]

    keyboard = [[InlineKeyboardButton(t, cb)] for t, cb in keys]
    await update.callback_query.edit_message_text(
        text, reply_markup=InlineKeyboardMarkup(keyboard)
    )

# texty sekcí
SECTIONS = {
    # české
    "menu_cs":    "🥐 **COFFEE PERK MENU** ☕️\n\n☕ Výběrová káva\n🍳 Snídaně…",
    "hours_cs":   "🕐 **KDY MÁME OTEVŘENO?**\n\n📅 Po–Pá: 7:30–17:00\n…",
    "where_cs":   "📍 **KDE NÁS NAJDETE?**\n\n🏠 Vyskočilova 1100/2…",
    "contact_cs": "📞 **KONTAKTUJTE NÁS**\n\n📬 info@coffeeperk.cz\n…",
    "preorder_cs":"📦 **PŘEDOBJEDNÁVKY**\n\nBrzy pošleme…",
    "why_cs":     "😎 **PROČ K NÁM?**\n\n☕ Protože…",

    # anglické
    "menu_en":    "🥐 **COFFEE PERK MENU** ☕️\n\n☕ Specialty coffee\n…",
    "hours_en":   "🕐 **OPENING HOURS**\n\n📅 Mon–Fri: 7:30–17:00\n…",
    "where_en":   "📍 **LOCATION**\n\n🏠 Vyskočilova 1100/2…",
    "contact_en": "📞 **CONTACT / BOOKING**\n\n📬 info@coffeeperk.cz\n…",
    "preorder_en":"📦 **PRE-ORDER**\n\nComing soon…",
    "why_en":     "😎 **WHY VISIT US?**\n\n☕ Because…",
}

# sekční handler
async def show_section(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    key = update.callback_query.data
    text = SECTIONS.get(key, "❌ Sekce nenalezena.")
    await update.callback_query.edit_message_text(text)

# zaregistrujeme
bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CallbackQueryHandler(lang_select, pattern=r"^lang_"))
bot_app.add_handler(CallbackQueryHandler(show_section, pattern=r"^(menu|hours|where|contact|preorder|why)_"))

# Telegram webhook receiver (Flask)
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, bot_app.bot)
    bot_app._handle_update(update)
    return "OK"

# health-check endpoint (volitelné)
@app.route("/", methods=["GET"])
def ping():
    return "OK", 200

# ========== spouštění ==========
if __name__ == "__main__":
    # rovnou nastavíme webhook při startu
    bot_app.job_queue.run_once(
        lambda _: bot_app.bot.set_webhook(f"{BASE_URL}/{BOT_TOKEN}"),
        when=0
    )
    # spustíme PTB vestavěný webhook-server
    bot_app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=BOT_TOKEN
    )
