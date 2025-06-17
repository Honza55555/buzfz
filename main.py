import os
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
)

# —— načtení ENV proměnných ——
BOT_TOKEN = os.environ["BOT_TOKEN"]
BASE_URL   = os.environ["BASE_URL"]   # např. https://tvuj-servis.onrender.com
PORT       = int(os.environ.get("PORT", 5000))

# —— Flask server + PTB webhook receiver ——
app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False  # aby se JSON nedeformoval

# —— vytvoření Telegram-aplikace ——
application = ApplicationBuilder().token(BOT_TOKEN).build()

# ——— HANDLERY ———

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[
        InlineKeyboardButton("🇨🇿 Čeština", callback_data="lang_cs"),
        InlineKeyboardButton("🌍 English", callback_data="lang_en"),
    ]]
    await update.message.reply_text(
        "☕️ Welcome to Coffee Perk!\n"
        "We’re happy to see you here. 🌟\n"
        "Please choose your language. 🗣️",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

async def lang_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    code = update.callback_query.data

    if code == "lang_cs":
        text = "Na co se mě můžeš zeptat:"
        opts = [
            ("🧾 Menu a nabídka",   "menu_cs"),
            ("🕐 Otevírací doba",    "hours_cs"),
            ("📍 Kde nás najdete",   "where_cs"),
            ("📞 Kontakt / Rezervace","contact_cs"),
            ("📦 Předobjednávka",     "preorder_cs"),
            ("😎 Proč k nám?",        "why_cs"),
        ]
    else:
        text = "What can you ask me:"
        opts = [
            ("🧾 Menu & Offer",       "menu_en"),
            ("🕐 Opening Hours",      "hours_en"),
            ("📍 Location",           "where_en"),
            ("📞 Contact / Booking",  "contact_en"),
            ("📦 Pre-order",          "preorder_en"),
            ("😎 Why Visit",          "why_en"),
        ]

    kb = [[InlineKeyboardButton(t, c)] for t, c in opts]
    await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb))

# všechny texty
SECTIONS = {
    "menu_cs":    "🥐 **COFFEE PERK MENU** ☕️\n\n☕ Výběr kávy…",
    "hours_cs":   "🕐 **KDY MÁME OTEVŘENO?**\n\n📅 Po–Pá: 7:30–17:00\n…",
    "where_cs":   "📍 **KDE NÁS NAJDETE?**\n\n🏠 Vyskočilova 1100/2…",
    "contact_cs": "📞 **KONTAKTUJTE NÁS**\n\n📬 info@coffeeperk.cz…",
    "preorder_cs":"📦 **PŘEDOBJEDNÁVKY**\n\nBrzy spustíme…",
    "why_cs":     "😎 **PROČ K NÁM?**\n\n☕ Protože…",

    "menu_en":    "🥐 **COFFEE PERK MENU** ☕️\n\n☕ Specialty coffee…",
    "hours_en":   "🕐 **OPENING HOURS**\n\n📅 Mon–Fri: 7:30–17:00\n…",
    "where_en":   "📍 **LOCATION**\n\n🏠 Vyskočilova 1100/2…",
    "contact_en": "📞 **CONTACT / BOOKING**\n\n📬 info@coffeeperk.cz…",
    "preorder_en":"📦 **PRE-ORDER**\n\nComing soon…",
    "why_en":     "😎 **WHY VISIT US?**\n\n☕ Because…",
}

async def show_section(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    key = update.callback_query.data
    text = SECTIONS.get(key, "❌ Sekce neexistuje.")
    await update.callback_query.edit_message_text(text)

# registrace handlerů
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(lang_select, pattern=r"^lang_"))
application.add_handler(CallbackQueryHandler(show_section, pattern=r"^(menu|hours|where|contact|preorder|why)_"))

# webhook endpoint pro PTB
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)
    application._handle_update(update)
    return "OK"

# health‐check
@app.route("/", methods=["GET"])
def healthcheck():
    return "OK", 200

# ——— spuštění ———
if __name__ == "__main__":
    # synchronně nastavíme u Telegramu webhook
    application.bot.set_webhook(f"{BASE_URL}/{BOT_TOKEN}")

    # spustíme vestavěný webhook server
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=BOT_TOKEN
    )
