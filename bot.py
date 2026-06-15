# Transport Jadvali Bot — 12 viloyat
# requirements.txt: python-telegram-bot, flask

import os
import sys
import threading
import random
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

print(">>> Skript boshlandi", flush=True)

BOT_TOKEN = os.environ.get("BOT_TOKEN")

if BOT_TOKEN:
    print(f">>> BOT_TOKEN topildi, uzunligi: {len(BOT_TOKEN)}", flush=True)
else:
    print(">>> XATO: BOT_TOKEN environment variable topilmadi!", flush=True)

# === 12 viloyat ===
REGIONS = {
    "andijon": "Andijon",
    "fargona": "Farg'ona",
    "namangan": "Namangan",
    "samarqand": "Samarqand",
    "buxoro": "Buxoro",
    "navoiy": "Navoiy",
    "jizzax": "Jizzax",
    "sirdaryo": "Sirdaryo",
    "surxondaryo": "Surxondaryo",
    "qashqadaryo": "Qashqadaryo",
    "xorazm": "Xorazm",
    "toshkent": "Toshkent",
}

user_state = {}


def generate_schedule(origin, destination):
    times = ["06:00", "09:30", "13:00", "17:30", "21:00"]
    lines = []
    for t in times:
        price = random.randint(1800, 2200)
        lines.append(f"🕐 {t} — narx: {price} so'm")
    return lines


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(">>> /start qabul qilindi", flush=True)
    await update.message.reply_text(
        "Salom! 👋 Men Transport Jadvali botiman.\n\n"
        "Avtobus jadvali va narxlarini bilish uchun /marshrut buyrug'ini yuboring."
    )


async def marshrut(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(">>> /marshrut qabul qilindi", flush=True)
    await show_regions(update, "Qayerdan jo'naysiz? Viloyatni tanlang:", prefix="from_")


async def show_regions(update, text, prefix):
    keyboard = []
    row = []
    for key, name in REGIONS.items():
        row.append(InlineKeyboardButton(name, callback_data=f"{prefix}{key}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup)
    else:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    if data.startswith("from_"):
        origin = data.replace("from_", "")
        user_state[user_id] = {"origin": origin}

        keyboard = []
        row = []
        for key, name in REGIONS.items():
            if key == origin:
                continue
            row.append(InlineKeyboardButton(name, callback_data=f"to_{key}"))
            if len(row) == 2:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"📍 Qayerdan: {REGIONS[origin]}\n\nQayerga borasiz?",
            reply_markup=reply_markup,
        )

    elif data.startswith("to_"):
        destination = data.replace("to_", "")
        state = user_state.get(user_id)
        if not state or "origin" not in state:
            await query.edit_message_text("Avval /marshrut buyrug'ini qaytadan yuboring.")
            return

        origin = state["origin"]
        schedule = generate_schedule(origin, destination)

        text = (
            f"🚌 {REGIONS[origin]} → {REGIONS[destination]}\n\n"
            + "\n".join(schedule)
            + "\n\nYangi qidiruv uchun /marshrut yuboring."
        )
        await query.edit_message_text(text)
        user_state.pop(user_id, None)


# === Render uchun web server (faqat "service is alive" ko'rsatish uchun) ===
flask_app = Flask(__name__)


@flask_app.route("/")
def home():
    return "Bot ishlayapti!"


def run_flask():
    port = int(os.environ.get("PORT", 10000))
    print(f">>> Flask {port}-portda ishga tushyapti", flush=True)
    flask_app.run(host="0.0.0.0", port=port)


def main():
    if not BOT_TOKEN:
        print(">>> BOT_TOKEN yo'qligi sababli to'xtatildi", flush=True)
        sys.exit(1)

    # Flask alohida thread'da, bot asosiy thread'da ishlaydi
    threading.Thread(target=run_flask, daemon=True).start()

    print(">>> Telegram Application yaratilmoqda...", flush=True)
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("marshrut", marshrut))
    app.add_handler(CallbackQueryHandler(button_handler))

    print(">>> Bot ishga tushdi, polling boshlandi...", flush=True)
    app.run_polling()


if __name__ == "__main__":
    main()
