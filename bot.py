import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask, request, abort, send_from_directory
import os, sys, threading

# --- 🔧 CONFIGURATION ---
API_TOKEN = os.environ.get('BOT_TOKEN')
WEBHOOK_URL_BASE = os.environ.get('WEBHOOK_URL')  # যেমন: https://your-app-name.onrender.com
WEBHOOK_URL_PATH = f"/{API_TOKEN}"

WEB_URL = "https://shadow-image-hosting-bot-1.onrender.com"
GROUP_LINK = "https://t.me/+DLEo8TQ1PjIzYzFl"
WELCOME_IMAGE = "https://iili.io/KOUGVeI.md.jpg"
CREDIT = "© SHADOW JOKER"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

bot = telebot.TeleBot(API_TOKEN, threaded=True)
server = Flask(__name__)

# --- 🧰 TOOLS LIST ---
TOOLS = [
    ("১. FB Fake ID রিপোর্ট", "https://fb-fakeid-report-shadowjoker.vercel.app/"),
    ("২. FB রিকভার ডিজেবল", "https://fb-disable-account-recover-shadowjo.vercel.app/"),
    ("৩. SMS Bomber", "https://shadow-joker-hard-sms-bms.vercel.app/"),
    ("৪. ফেইক NID মেকার", "https://bangladesh-fake-nid-maker-shadow-jo.vercel.app/"),
    ("৫. IP Info Bot", "https://t.me/IP_INFO_SHADOW_BOT"),
    ("৬. আবহাওয়া তথ্য বট", "https://t.me/wether_info_shadow_bot"),
    ("৭. নাম্বার থেকে NID", "http://bangladeshi-number-to-nid-tool-cht.vercel.app"),
    ("৮. IMEI ট্র্যাকার", "https://imei-to-device-info-shadow.vercel.app/"),
    ("৯. ইমেজ হোস্টিং বট", "https://t.me/shadow_free_image_hosting_bot"),
    ("১০. Free Fire ID Info", "https://ff-id-info-cyber-team-hlep.vercel.app/"),
    ("১১. বার্থডে কপি", "https://birthday-online-copy-shadow-joker.vercel.app/"),
    ("১২. লাইভ লোকেশন", "https://number-to-live-location-cyber-team.vercel.app/"),
    ("১৩. ওয়েব ক্লোনার", "https://cyber-team-help-web-cloner-shadow.vercel.app/"),
    ("১৪. টুলস কালেকশন (Drive)", "https://drive.google.com/folderview?id=1tgkKt4lSpXD3GnMQRgUb4bbtlmpP9XOE"),
    ("১৫. AI টুলস", "https://shadow-joker-all-ai.vercel.app/"),
    ("১৬. Deface Website", "https://shadow-deface-website.vercel.app/"),
    ("১৭. Root Wifi Hack", "https://shadow-root-phone-wifi-hack.vercel.app/"),
    ("১৮. CTH টুল জোন", "https://shadow-cth-tool-joker.vercel.app/"),
]
PAGE_SIZE = 6

# --- Pagination Keyboard ---
def generate_keyboard(page=0):
    markup = InlineKeyboardMarkup()
    start_index = page * PAGE_SIZE
    end_index = start_index + PAGE_SIZE
    for name, url in TOOLS[start_index:end_index]:
        markup.add(InlineKeyboardButton(name, url=url))
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⏪ Back", callback_data=f"page_{page-1}"))
    if end_index < len(TOOLS):
        nav_buttons.append(InlineKeyboardButton("Next ⏩", callback_data=f"page_{page+1}"))
    if nav_buttons:
        markup.row(*nav_buttons)
    return markup

# --- Start Command ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_name = message.from_user.first_name or "Dear"

    welcome_caption = f"""
<b>🤖 Hello {user_name}</b>

✅ <b>Bot READY!</b>
নিচে আপনার প্রয়োজনীয় টুলস পাবেন 👇

🔹 <a href='{WEB_URL}'>Use Website</a>
🔹 <a href='{GROUP_LINK}'>Join Our Group</a>

<i>{CREDIT}</i>
"""
    keyboard = generate_keyboard(0)
    bot.send_photo(message.chat.id, WELCOME_IMAGE, caption=welcome_caption, parse_mode="HTML", reply_markup=keyboard)

# --- Page Navigation ---
@bot.callback_query_handler(func=lambda call: call.data.startswith('page_'))
def callback_query(call):
    try:
        new_page = int(call.data.split('_')[1])
        keyboard = generate_keyboard(new_page)
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=keyboard)
        bot.answer_callback_query(call.id, f"পৃষ্ঠা: {new_page+1}")
    except Exception as e:
        print("Callback error:", e, file=sys.stderr)
        bot.answer_callback_query(call.id, "Error loading page.")

# --- Image Upload Handler ---
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    photo_file_id = message.photo[-1].file_id
    file_info = bot.get_file(photo_file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    filename = os.path.basename(file_info.file_path)
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    with open(save_path, "wb") as f:
        f.write(downloaded_file)
    public_url = f"{WEB_URL}/{UPLOAD_FOLDER}/{filename}"
    bot.reply_to(message, f"✅ Uploaded Successfully!\n\n📸 Hosted Link:\n{public_url}\n\n{CREDIT}")

# --- Webhook Handler ---
@server.route(WEBHOOK_URL_PATH, methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_str = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_str)
        threading.Thread(target=bot.process_new_updates, args=([update],)).start()
        return 'ok', 200
    else:
        abort(403)

# --- Serve Uploaded Files ---
@server.route(f'/{UPLOAD_FOLDER}/<filename>', methods=['GET'])
def serve_upload(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# --- Root Route (Status Check) ---
@server.route('/', methods=['GET','POST'])
def index():
    if request.method == 'POST':
        return 'ok', 200
    return f"<h3>🤖 Cyber Team Help Bot is running... {CREDIT}</h3>"

# --- Set Webhook ---
def set_webhook():
    bot.remove_webhook()
    full_url = WEBHOOK_URL_BASE + WEBHOOK_URL_PATH
    ok = bot.set_webhook(url=full_url)
    print(f"🎯 Webhook Set: {full_url}" if ok else "❌ Webhook Failed", file=sys.stdout)

# --- Run Server ---
if __name__ == "__main__":
    set_webhook()
    port = int(os.environ.get("PORT", 5000))
    server.run(host="0.0.0.0", port=port)
