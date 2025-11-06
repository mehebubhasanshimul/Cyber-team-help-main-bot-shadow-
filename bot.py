import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
from flask import Flask, request, abort
import sys
import threading  # ✅ Threading যোগ করা হয়েছে

# --- 🔧 কনফিগারেশন ---
API_TOKEN = os.environ.get('BOT_TOKEN')
WEBHOOK_URL_BASE = os.environ.get('WEBHOOK_URL')  # যেমন: https://your-app-name.onrender.com
WEBHOOK_URL_PATH = f"/{API_TOKEN}"

bot = telebot.TeleBot(API_TOKEN)
server = Flask(__name__)

# --- 🧰 টুলস লিস্ট ---
TOOLS = [
    ("১. FB Fake ID রিপোর্ট", "https://fb-fakeid-report-shadowjoker.vercel.app/"),
    ("২. FB রিকভার ডিজেবল", "https://fb-disable-account-recover-shadowjo.vercel.app/"),
    ("৩. SMS Bomber", "https://shadow-joker-hard-sms-bombar.vercel.app/"),
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

# --- ⏩ Pagination Keyboard ---
def generate_keyboard(page=0):
    markup = InlineKeyboardMarkup()
    start_index = page * PAGE_SIZE
    end_index = start_index + PAGE_SIZE
    current_tools = TOOLS[start_index:end_index]
    
    for name, url in current_tools:
        markup.add(InlineKeyboardButton(name, url=url))
        
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⏪ Back", callback_data=f"page_{page-1}"))
    if end_index < len(TOOLS):
        nav_buttons.append(InlineKeyboardButton("Next ⏩", callback_data=f"page_{page+1}"))
    if nav_buttons:
        markup.row(*nav_buttons)
        
    return markup, page

# --- 🚀 Start Command ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_name = message.from_user.first_name or "Dear"
    welcome_text = (
        f"🤖 *Hello {user_name}*,\n\n"
        f"✅ *Bot READY*\\! নিচে আপনার প্রয়োজনীয় সমস্ত টুলস পেয়ে যাবেন, ব্যবহার শুরু করুন\\.\n\n"
        f"═════════════════\n"
        f"⚔️ **CYBER TEAM HELP**\n"
        f"👤 _CREATE BY SHADOW JOKER_"
    )
    keyboard, page = generate_keyboard(0)
    bot.send_message(
        message.chat.id,
        welcome_text,
        parse_mode="MarkdownV2",
        reply_markup=keyboard
    )

# --- 🔁 Page Navigation ---
@bot.callback_query_handler(func=lambda call: call.data.startswith('page_'))
def callback_query(call):
    try:
        new_page = int(call.data.split('_')[1])
    except:
        bot.answer_callback_query(call.id, "পেজ লোড করার সমস্যা হয়েছে।")
        return
    keyboard, current_page = generate_keyboard(new_page)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=keyboard)
    bot.answer_callback_query(call.id, f"পৃষ্ঠা: {new_page+1}")

# --- 🧠 Webhook রিসিভার ---
@server.route(WEBHOOK_URL_PATH, methods=['POST'])
def webhook():
    print("✅ Webhook called correctly!", file=sys.stdout)
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        # ✅ Thread ব্যবহার করা হয়েছে যাতে রেসপন্স বন্ধ না হয়
        threading.Thread(target=bot.process_new_updates, args=([update],)).start()
        return '!', 200
    else:
        abort(403)

# --- 🌐 মূল রুট (Render GET + Telegram POST fix) ---
@server.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        print("⚙️ POST / received", file=sys.stdout)
        if request.headers.get('content-type') == 'application/json':
            json_string = request.get_data().decode('utf-8')
            update = telebot.types.Update.de_json(json_string)
            threading.Thread(target=bot.process_new_updates, args=([update],)).start()
            return '!', 200
        else:
            abort(403)
    return "✅ Cyber Team Help Bot Webhook Server is running.", 200

# --- 🧩 Webhook Setup Function ---
def set_webhook():
    bot.remove_webhook()
    full_webhook_url = WEBHOOK_URL_BASE + WEBHOOK_URL_PATH
    success = bot.set_webhook(url=full_webhook_url)
    if success:
        print(f"🎯 Webhook successfully set to: {full_webhook_url}", file=sys.stdout)
    else:
        print("❌ Failed to set Webhook!", file=sys.stdout)

# --- 🏁 Run Flask Server ---
if __name__ == "__main__":
    set_webhook()
    port = int(os.environ.get('PORT', 5000))
    server.run(host="0.0.0.0", port=port)
