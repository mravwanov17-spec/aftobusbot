import os
import sys
import threading
import random
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

print(">>> Skript boshlandi...", flush=True)

# === BOT TOKENINI SOZLANMASI ===
# Agar Render/Koyeb-da ishlatayotgan bo'lsangiz, Environment Variable (BOT_TOKEN) qilib kiriting.
# Agar lokal kompyuterda sinab ko'rmoqchi bo'lsangiz, qo'shtirnoq ichiga tokenni yozing.
BOT_TOKEN = "8927571109:AAGBY6QfHYV91J6aI-ZDLtWZBGk3dKHxpg0"

# === 12 viloyat va ularning tumanlari ===
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
            "Shofirkon",
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

def generate_bus_info(region_key, district):
    """Avtobus ma'lumotlarini yaratish."""
    random.seed(region_key + district)
    bus_number = f"{random.randint(1, 99):02d}"
    times = ["06:00", "08:30", "11:00", "14:30", "18:00", "20:30"]
    chosen_times = random.sample(times, k=3)
    chosen_times.sort()
    price = random.randint(1800, 2200)
    return bus_number, chosen_times, price

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salom! 👋 Men Transport Jadvali botiman.\n\n"
        "Viloyat va tumanlar bo'yicha avtobus jadvalini bilish uchun "
        "/marshrut buyrug'ini yuboring."
    )

async def marshrut(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    await update.message.reply_text("📌 Viloyatni tanlang:", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("region_"):
        region_key = data.replace("region_", "")
        districts = REGIONS[region_key]["districts"]
        
        keyboard = []
        row = []
        for district in districts:
            row.append(InlineKeyboardButton(district, callback_data=f"dist_{region_key}_{district}"))
            if len(row) == 2:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)

        keyboard.append([InlineKeyboardButton("⬅️ Viloyatlar ro'yxati", callback_data="back_to_regions")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"📍 {REGIONS[region_key]['name']} viloyati\n\nTumanni tanlang:",
            reply_markup=reply_markup,
        )

    elif data.startswith("dist_"):
        rest = data.replace("dist_", "")
        region_key, district = rest.split("_", 1)

        bus_number, times, price = generate_bus_info(region_key, district)
        times_text = "\n".join(f"🕐 {t}" for t in times)

        text = (
            f"🚌 Yo'nalish: {REGIONS[region_key]['name']} — {district}\n\n"
            f"🔢 Avtobus raqami: №{bus_number}\n\n"
            f"📅 Qatnov vaqtlari:\n{times_text}\n\n"
            f"💵 Yo'l haqki: {price} so'm\n\n"
            f"Yangi qidiruv uchun /marshrut buyrug'ini bosing."
        )

        keyboard = [[InlineKeyboardButton("⬅️ Orqaga (Tumanlar)", callback_data=f"region_{region_key}")]]
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
        await query.edit_message_text("📌 Viloyatni tanlang:", reply_markup=reply_markup)

# === Render / Koyeb uchun Web Server ===
flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "Bot muvaffaqiyatli ishlayapti!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    print(f">>> Flask {port}-portda ishga tushmoqda...", flush=True)
    flask_app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

def main():
    if BOT_TOKEN == "BU_YERGA_TELEGRAM_TOKEN_YOZING" or not BOT_TOKEN:
        print(">>> XATO: Bot token kiritilmagan! Skript to'xtatildi.", flush=True)
        sys.exit(1)

    # Flask serverni alohida Thread-da ochamiz (Render o'chib qolmasligi uchun)
    threading.Thread(target=run_flask, daemon=True).start()

    # Botni ishga tushirish
    print(">>> Telegram Bot yuklanmoqda...", flush=True)
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("marshrut", marshrut))
    app.add_handler(CallbackQueryHandler(button_handler))

    print(">>> Bot muvaffaqiyatli ishga tushdi! (Polling...)", flush=True)
    app.run_polling()

if __name__ == "__main__":
    main()
