import telebot
import requests
import json

# === Konfiguratsiya ===
BOT_TOKEN = "8035496121:AAFllT7uo-we6QRreYZPj7v6beDqQS4wBmg"
ADMIN_ID = 7824942822
REQUIRED_LINK = "https://t.me/+XGxJdz3kyAkyZDYy"
bot = telebot.TeleBot(BOT_TOKEN)

# === Start komandasi ===
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if not is_subscribed(user_id):
        bot.send_message(user_id, f"❗ Чтобы использовать бота, подпишитесь на канал:", reply_markup=subscribe_markup())
        return
    bot.send_message(user_id, "👋 Привет! Пришлите ссылку на Instagram 📎")

# === Obuna markup ===
def subscribe_markup():
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("✅ Подписаться", url=REQUIRED_LINK))
    return markup

# === Obuna tekshiruvi (faqat ishoning, 100% aniqlik emas) ===
def is_subscribed(user_id):
    try:
        return True  # Invite link orqali aniqlashni Telegram API qo‘llamaydi, shuning uchun doimo True
    except:
        return False

# === Instagram yuklab olish ===
@bot.message_handler(func=lambda msg: True)
def handle_msg(msg):
    user_id = msg.from_user.id

    if not is_subscribed(user_id):
        bot.send_message(user_id, f"⚠️ Подпишитесь сначала: {REQUIRED_LINK}", reply_markup=subscribe_markup())
        return

    if "instagram.com" in msg.text:
        bot.send_message(user_id, "⏳ Загружаю видео...")
        try:
            r = requests.get(f"https://savefrom.app/api/download?url={msg.text}")
            data = r.json()
            video_url = data["links"][0]["url"]
            bot.send_video(user_id, video_url)
        except:
            bot.send_message(user_id, "❌ Не удалось загрузить. Попробуйте другой линк.")
    elif msg.text == "/admin" and msg.from_user.id == ADMIN_ID:
        admin_panel(msg.chat.id)
    else:
        save_user(user_id)
        bot.send_message(user_id, "📥 Просто отправьте Instagram ссылку.")

# === Admin panel ===
def admin_panel(chat_id):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📊 Статистика", "📋 Список пользователей")
    bot.send_message(chat_id, "🔧 Админ панель:", reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text in ["📊 Статистика", "📋 Список пользователей"])
def handle_admin(msg):
    if msg.from_user.id != ADMIN_ID:
        return
    with open("users.json", "r") as f:
        users = json.load(f)
    if msg.text == "📊 Статистика":
        bot.send_message(msg.chat.id, f"👥 Пользователей: {len(users)}")
    else:
        ids = "\n".join([str(u) for u in users])
        bot.send_message(msg.chat.id, f"🧾 Список:\n{ids}")

# === Foydalanuvchini yozib borish ===
def save_user(user_id):
    try:
        with open("users.json", "r") as f:
            users = json.load(f)
    except:
        users = []
    if user_id not in users:
        users.append(user_id)
        with open("users.json", "w") as f:
            json.dump(users, f)

bot.polling()
