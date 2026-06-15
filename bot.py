# Transport Jadvali Bot — 12 viloyat va tumanlari
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

# === 12 viloyat va ularning tumanlari (haqiqiy nomlar) ===
REGIONS = {
    "andijon": {
        "name": "Andijon",
        "districts": [
            "Andijon shahri", "Asaka", "Baliqchi", "Bo'ston", "Buloqboshi",
            "Izboskan", "Jalaquduq", "Marhamat", "Oltinko'l", "Paxtaobod",
            "Shahrixon", "Ulug'nor", "Xo'jaobod",
        ],
    },
    "fargona": {
        "name": "Farg'ona",
        "districts": [
            "Farg'ona shahri", "Marg'ilon", "Qo'qon", "Quva", "Rishton",
            "Beshariq", "Bog'dod", "Buvayda", "Dang'ara", "Furqat",
            "Oltiariq", "O'zbekiston", "So'x", "Toshloq", "Uchko'prik",
            "Yozyovon",
        ],
    },
    "namangan": {
        "name": "Namangan",
        "districts": [
            "Namangan shahri", "Chortoq", "Chust", "Kosonsoy", "Mingbuloq",
            "Norin", "Pop", "To'raqo'rg'on", "Uchqo'rg'on", "Uychi",
            "Yangiqo'rg'on",
        ],
    },
    "samarqand": {
        "name": "Samarqand",
        "districts": [
            "Samarqand shahri", "Bulung'ur", "Ishtixon", "Jomboy", "Kattaqo'rg'on",
            "Narpay", "Nurobod", "Oqdaryo", "Pastdarg'om", "Paxtachi",
            "Payariq", "Toyloq", "Urgut",
        ],
    },
    "buxoro": {
        "name": "Buxoro",
        "districts": [
            "Buxoro shahri", "Vobkent", "G'ijduvon", "Jondor", "Kogon",
            "Olot", "Peshku", "Qorako'l", "Qorovulbozor", "Romitan",
            "Shofirkon", "Vobkent",
        ],
    },
    "navoiy": {
        "name": "Navoiy",
        "districts": [
            "Navoiy shahri", "Konimex", "Karmana", "Navbahor", "Nurota",
            "Qiziltepa", "Tomdi", "Uchquduq", "Xatirchi", "Zarafshon",
        ],
    },
    "jizzax": {
        "name": "Jizzax",
        "districts": [
            "Jizzax shahri", "Arnasoy", "Baxmal", "Do'stlik", "Forish",
            "G'allaorol", "Mirzacho'l", "Paxtakor", "Yangiobod", "Zarbdor",
            "Zafarobod", "Zomin",
        ],
    },
    "sirdaryo": {
        "name": "Sirdaryo",
        "districts": [
            "Guliston", "Boyovut", "Mirzaobod", "Oqoltin", "Sardoba",
            "Sayxunobod", "Sirdaryo", "Xovos", "Yangiyer",
        ],
    },
    "surxondaryo": {
        "name": "Surxondaryo",
        "districts": [
            "Termiz", "Angor", "Bandixon", "Boysun", "Denov",
            "Jarqo'rg'on", "Muzrabot", "Oltinsoy", "Qiziriq", "Qumqo'rg'on",
            "Sariosiyo", "Sherobod", "Shurchi", "Uzun",
        ],
    },
    "qashqadaryo": {
        "name": "Qashqadaryo",
        "districts": [
            "Qarshi", "Chiroqchi", "Dehqonobod", "G'uzor", "Kasbi",
            "Kitob", "Koson", "Mirishkor", "Muborak", "Nishon",
            "Qamashi", "Shahrisabz", "Yakkabog'",
        ],
    },
    "xorazm": {
        "name": "Xorazm",
        "districts": [
            "Urganch", "Bog'ot", "Gurlan", "Hazorasp", "Xiva",
            "Xonqa", "Qo'shko'pir", "Shovot", "Yangiariq", "Yangibozor",
        ],
    },
    "toshkent": {
        "name": "Toshkent",
        "districts": [
            "Toshkent shahri", "Bekobod", "Bo'ka", "Chinoz", "Qibray",
            "Ohangaron", "Parkent", "Piskent", "Quyichirchiq", "Yuqorichirchiq",
            "Yangiyul", "Zangiota",
        ],
    },
}

# user_id -> {"region": ..., "district": ...}
user_state = {}


def generate_bus_info(region_key, district):
    """Avtobus raqami, vaqti va narxini generatsiya qilish (demo)."""
    random.seed(region_key + district)  # har bir tuman uchun doimiy natija
    bus_number = f"{random.randint(1, 99):02d}"
    times = ["06:00", "08:30", "11:00", "14:30", "18:00", "20:30"]
    chosen_times = random.sample(times, k=3)
    chosen_times.sort()
    price = random.randint(1800, 2200)
    return bus_number, chosen_times, price


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(">>> /start qabul qilindi", flush=True)
    await update.message.reply_text(
        "Salom! 👋 Men Transport Jadvali botiman.\n\n"
        "Viloyat va tumanlar bo'yicha avtobus jadvalini bilish uchun "
        "/marshrut buyrug'ini yuboring."
    )


async def marshrut(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(">>> /marshrut qabul qilindi", flush=True)
    keyboard = []
    row = []
    for key, data in REGIONS.items():
        row.append(InlineKeyboardButton(data["name"], callback_data=f"region_{key}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Viloyatni tanlang:", reply_markup=reply_markup)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    if data.startswith("region_"):
        region_key = data.replace("region_", "")
        user_state[user_id] = {"region": region_key}

        districts = REGIONS[region_key]["districts"]
        keyboard = []
        row = []
        for district in districts:
            row.append(InlineKeyboardButton(district, callback_data=f"district_{region_key}_{district}"))
            if len(row) == 2:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)

        # Orqaga tugmasi
        keyboard.append([InlineKeyboardButton("⬅️ Viloyatlar", callback_data="back_to_regions")])

        reply_markup = InlineKeyboardMarkup(keyboard)
        region_name = REGIONS[region_key]["name"]
        await query.edit_message_text(
            f"📍 {region_name} viloyati\n\nTumanni tanlang:",
            reply_markup=reply_markup,
        )

    elif data.startswith("district_"):
        # format: district_{region_key}_{district_name}
        rest = data.replace("district_", "")
        region_key, district = rest.split("_", 1)

        region_name = REGIONS[region_key]["name"]
        bus_number, times, price = generate_bus_info(region_key, district)

        times_text = "\n".join(f"🕐 {t}" for t in times)

        text = (
            f"🚌 {region_name} — {district}\n\n"
            f"Avtobus raqami: №{bus_number}\n\n"
            f"Qatnov vaqtlari:\n{times_text}\n\n"
            f"Narxi: {price} so'm\n\n"
            f"Yangi qidiruv uchun /marshrut yuboring."
        )

        keyboard = [[InlineKeyboardButton("⬅️ Tumanlar", callback_data=f"region_{region_key}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(text, reply_markup=reply_markup)

    elif data == "back_to_regions":
        keyboard = []
        row = []
        for key, rdata in REGIONS.items():
            row.append(InlineKeyboardButton(rdata["name"], callback_data=f"region_{key}"))
            if len(row) == 2:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Viloyatni tanlang:", reply_markup=reply_markup)


# === Render uchun web server ===
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
