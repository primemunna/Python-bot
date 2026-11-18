import os
import json
import time
import telebot
from telebot import types

# --- CONFIGURATIONS ---
TOKEN = "9232633516:AAEW0RsVNRsoMiT4Enzu43PESoNxsC4Wn0s"
ADMIN_ID = 9118052534
UPI_ID = "8016922924@ibl"

bot = telebot.TeleBot(TOKEN)

# --- DATABASE MANAGEMENT (JSON BASED) ---
DB_FILE = "database.json"

def init_db():
    if not os.path.exists(DB_FILE):
        data = {
            "users": {},
            "free_products": [],
            "paid_products": [],
            "raffles": [],
            "payments": [],
            "history": {}
        }
        with open(DB_FILE, "w") as f:
            json.dump(data, f, indent=4)

def load_data():
    init_db()
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Multi-language dictionary
LANGS = {
    "English": {
        "welcome": "Welcome to the Bot! Choose an option below:",
        "free_prod": "🎁 Free Products",
        "paid_prod": "💎 Paid Products",
        "raffle_stat": "📊 Raffle Status",
        "pur_hist": "🛍️ Purchase History",
        "raf_hist": "📜 Raffle History",
        "wallet": "👛 Wallet",
        "dev": "👨‍💻 Developer",
        "lang": "🌐 Language",
        "help": "🛠️ Help & Support",
        "leaderboard": "🏆 Raffle Leaderboard"
    },
    "Bengali": {
        "welcome": "বটে স্বাগতম! নিচের অপশনগুলো থেকে বেছে নিন:",
        "free_prod": "🎁 ফ্রি প্রোডাক্টস",
        "paid_prod": "💎 পেইড প্রোডাক্টস",
        "raffle_stat": "📊 র‍্যাফেল স্ট্যাটাস",
        "pur_hist": "🛍️ কেনাকাটার ইতিহাস",
        "raf_hist": "📜 র‍্যাফেল ইতিহাস",
        "wallet": "👛 ওয়ালেট",
        "dev": "👨‍💻 ডেভেলপার",
        "lang": "🌐 ভাষা পরিবর্তন",
        "help": "🛠️ হেল্প ও সাপোর্ট",
        "leaderboard": "🏆 র‍্যাফেল লিডারবোর্ড"
    },
    "Hindi": {
        "welcome": "बॉट में आपका स्वागत है! नीचे दिए गए विकल्पों में से चुनें:",
        "free_prod": "🎁 फ्री प्रोडक्ट्स",
        "paid_prod": "💎 पेड प्रोडक्ट्स",
        "raffle_stat": "📊 रैffle स्टेटस",
        "pur_hist": "🛍️ खरीदी इतिहास",
        "raf_hist": "📜 रैffle इतिहास",
        "wallet": "👛 वॉलेट",
        "dev": "👨‍💻 डेवलपर",
        "lang": "🌐 भाषा बदलें",
        "help": "🛠️ सहायता",
        "leaderboard": "🏆 रैffle लीडरबोर्ड"
    }
}

def get_lang_text(user_id, key):
    db = load_data()
    user_lang = db["users"].get(str(user_id), {}).get("lang", "English")
    return LANGS.get(user_lang, LANGS["English"]).get(key, key)

# --- MAIN MENU KEYBOARD ---
def main_menu(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    b1 = types.KeyboardButton(get_lang_text(user_id, "free_prod"))
    b2 = types.KeyboardButton(get_lang_text(user_id, "paid_prod"))
    b3 = types.KeyboardButton(get_lang_text(user_id, "raffle_stat"))
    b4 = types.KeyboardButton(get_lang_text(user_id, "pur_hist"))
    b5 = types.KeyboardButton(get_lang_text(user_id, "raf_hist"))
    b6 = types.KeyboardButton(get_lang_text(user_id, "wallet"))
    b7 = types.KeyboardButton(get_lang_text(user_id, "dev"))
    b8 = types.KeyboardButton(get_lang_text(user_id, "lang"))
    b9 = types.KeyboardButton(get_lang_text(user_id, "help"))
    b10 = types.KeyboardButton(get_lang_text(user_id, "leaderboard"))
    markup.add(b1, b2, b3, b4, b5, b6, b7, b8, b9, b10)
    if user_id == ADMIN_ID:
        markup.add(types.KeyboardButton("👑 /admin"))
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.from_user.id)
    db = load_data()
    if uid not in db["users"]:
        db["users"][uid] = {
            "rs": 0.0, 
            "coin": 0, 
            "lang": "English", 
            "purchases": [], 
            "raffles_joined": 0
        }
        save_data(db)
    
    bot.send_message(
        message.chat.id, 
        get_lang_text(message.from_user.id, "welcome"), 
        reply_markup=main_menu(message.from_user.id)
    )

# --- LANGUAGE CHANGE ---
@bot.message_handler(func=lambda m: m.text in ["🌐 Language", "🌐 ভাষা পরিবর্তন", "🌐 भाषा बदलें"])
def change_lang_menu(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("English", callback_data="lang_English"))
    markup.add(types.InlineKeyboardButton("Bengali (বাংলা)", callback_data="lang_Bengali"))
    markup.add(types.InlineKeyboardButton("Hindi (हिन्दी)", callback_data="lang_Hindi"))
    bot.send_message(message.chat.id, "Select your language / আপনার ভাষা নির্বাচন করুন:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
def set_language(call):
    lang = call.data.split("_")[1]
    uid = str(call.from_user.id)
    db = load_data()
    if uid in db["users"]:
        db["users"][uid]["lang"] = lang
        save_data(db)
    bot.answer_callback_query(call.id, f"Language changed to {lang}")
    bot.send_message(call.message.chat.id, get_lang_text(call.from_user.id, "welcome"), reply_markup=main_menu(call.from_user.id))

# --- DEVELOPER & HELP ---
@bot.message_handler(func=lambda m: m.text in ["👨‍💻 Developer", "👨‍💻 ডেভেলপার", "👨‍💻 डेवलपर"])
def developer_info(message):
    bot.send_message(message.chat.id, "Developer Contact:\n@ai_brain_box_2")

@bot.message_handler(func=lambda m: m.text in ["🛠️ Help & Support", "🛠️ হেল্প ও সাপোর্ট", "🛠️ सहायता"])
def help_support(message):
    bot.send_message(message.chat.id, "For any help contact Developer: @ai_brain_box_2")

# --- WALLET & ADD MONEY ---
@bot.message_handler(func=lambda m: m.text in ["👛 Wallet", "👛 ওয়ালেট", "👛 वॉलेट"])
def wallet_menu(message):
    uid = str(message.from_user.id)
    db = load_data()
    user = db["users"].get(uid, {"rs": 0.0, "coin": 0})
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("➕ Add Rs.", callback_data="add_rs"))
    
    text = f"👛 **Your Wallet:**\n\nRs. Balance: ₹{user['rs']}\n🪙 Coin Balance: {user['coin']}"
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "add_rs")
def ask_amount(call):
    msg = bot.send_message(call.message.chat.id, "Enter amount in Rs. you want to add:")
    bot.register_next_step_handler(msg, process_add_amount)

def process_add_amount(message):
    try:
        amount = float(message.text)
        uid = str(message.from_user.id)
        
        # Send QR Code and details
        qr_caption = (
            f"💳 **Payment Gateway**\n\n"
            f"UPI ID: `{UPI_ID}`\n"
            f"Amount: ₹{amount}\n\n"
            f"⚠️ *Please pay within 10 minutes and send the payment screenshot here!*"
        )
        
        # Temporary save payment request
        db = load_data()
        pay_id = str(int(time.time()))
        db["payments"].append({
            "pay_id": pay_id,
            "uid": uid,
            "username": message.from_user.username or "No Username",
            "name": message.from_user.first_name,
            "amount": amount,
            "time": time.time(),
            "status": "pending"
        })
        save_data(db)
        
        sent_msg = bot.send_message(message.chat.id, qr_caption, parse_mode="Markdown")
        
        # Timer simulation (10 mins expiry notice)
        time.sleep(1) # Logic placeholder, real timers run via async in production, here we use timestamp verification on upload.
        
        msg = bot.send_message(message.chat.id, "Now upload the payment screenshot image:")
        bot.register_next_step_handler(msg, lambda m: handle_payment_screenshot(m, amount, pay_id))
    except ValueError:
        bot.send_message(message.chat.id, "Invalid amount. Please try again from Wallet.")

def handle_payment_screenshot(message, amount, pay_id):
    if not message.photo:
        bot.send_message(message.chat.id, "Please upload an image screenshot!")
        return
    
    db = load_data()
    # Check 10 min timeout
    for p in db["payments"]:
        if p["pay_id"] == pay_id:
            if time.time() - p["time"] > 600:
                bot.send_message(message.chat.id, "❌ QR Code expired! 10 minutes time limit exceeded.")
                return

    photo_id = message.photo[-1].file_id
    uid = str(message.from_user.id)
    
    # Forward to Admin
    admin_caption = (
        f"🔔 **New Payment Request!**\n\n"
        f"User ID: `{uid}`\n"
        f"Name: {message.from_user.first_name}\n"
        f"Amount: ₹{amount}\n"
        f"Pay ID: {pay_id}"
    )
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✅ Approve", callback_data=f"app_{pay_id}"),
        types.InlineKeyboardButton("❌ Reject", callback_data=f"rej_{pay_id}")
    )
    bot.send_photo(ADMIN_ID, photo_id, caption=admin_caption, parse_mode="Markdown", reply_markup=markup)
    bot.send_message(message.chat.id, "✅ Payment screenshot submitted to admin for verification!")

# --- FREE PRODUCTS ---
@bot.message_handler(func=lambda m: m.text in ["🎁 Free Products", "🎁 ফ্রি প্রোডাক্টস", "🎁 फ्री प्रोडक्ट्स"])
def free_products_menu(message):
    db = load_data()
    products = db["free_products"]
    if not products:
        bot.send_message(message.chat.id, "No free products available right now.")
        return
    
    markup = types.InlineKeyboardMarkup()
    for idx, p in enumerate(products):
        markup.add(types.InlineKeyboardButton(p['title'], callback_data=f"free_prod_{idx}"))
    bot.send_message(message.chat.id, "Select a Free Product:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("free_prod_"))
def free_product_detail(call):
    idx = int(call.data.split("_")[2])
    db = load_data()
    p = db["free_products"][idx]
    
    uid = str(call.from_user.id)
    user_coin = db["users"][uid]["coin"]
    
    text = f"🎁 **{p['title']}**\n\n{p['desc']}\n\n🪙 Coin Price: {p['coin_price']}\nYour Coins: {user_coin}"
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🪙 Earn Coin", callback_data=f"earn_coin_{idx}"))
    markup.add(types.InlineKeyboardButton("🛒 Buy Now", callback_data=f"buy_free_{idx}"))
    
    bot.send_message(call.message.chat.id, text, parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("earn_coin_"))
def earn_coin_action(call):
    uid = str(call.from_user.id)
    db = load_data()
    db["users"][uid]["coin"] += 5  # Earn 5 coins per click
    save_data(db)
    
    # Raffle status activated check
    bot.answer_callback_query(call.id, "🎉 +5 Coins Earned! Raffle status activated!")
    bot.send_message(call.message.chat.id, "You earned 5 coins! Raffle button is now active.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_free_"))
def buy_free_product(call):
    idx = int(call.data.split("_")[2])
    uid = str(call.from_user.id)
    db = load_data()
    p = db["free_products"][idx]
    
    user_coin = db["users"][uid]["coin"]
    price = p["coin_price"]
    
    if user_coin < price:
        bot.answer_callback_query(call.id, "❌ Not enough coins!", show_alert=True)
        return
    
    db["users"][uid]["coin"] -= price
    remaining_coins = db["users"][uid]["coin"]
    
    # Save to history
    db["users"][uid]["purchases"].append({"type": "free", "name": p['title'], "file": p['file']})
    
    # Add to raffle history ledger
    db["raffles"].append({
        "username": call.from_user.username or "None",
        "name": call.from_user.first_name,
        "link": f"t.me/{call.from_user.username}" if call.from_user.username else "No Link",
        "time": time.ctime()
    })
    save_data(db)
    
    text = (
        f"✅ **Purchase Successful!**\n\n"
        f"Product: {p['title']}\n"
        f"Price: {price} 🪙\n"
        f"Remaining Balance: {remaining_coins} 🪙\n\n"
        f"📁 **File:** `{p['file']}`"
    )
    markup = types.InlineKeyboardMarkup()
    if p['tutorial']:
        markup.add(types.InlineKeyboardButton("📺 Tutorial Video", url=p['tutorial']))
    
    bot.send_message(call.message.chat.id, text, parse_mode="Markdown", reply_markup=markup)

# --- PAID PRODUCTS ---
@bot.message_handler(func=lambda m: m.text in ["💎 Paid Products", "💎 পেইড প্রোডাক্টস", "💎 पेड प्रोडक्ट्स"])
def paid_products_menu(message):
    db = load_data()
    products = db["paid_products"]
    if not products:
        bot.send_message(message.chat.id, "No paid products available.")
        return
    
    markup = types.InlineKeyboardMarkup()
    for idx, p in enumerate(products):
        markup.add(types.InlineKeyboardButton(p['title'], callback_data=f"paid_prod_{idx}"))
    bot.send_message(message.chat.id, "Select a Paid Product:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("paid_prod_"))
def paid_product_detail(call):
    idx = int(call.data.split("_")[2])
    db = load_data()
    p = db["paid_products"][idx]
    
    uid = str(call.from_user.id)
    user_rs = db["users"][uid]["rs"]
    
    text = f"💎 **{p['title']}**\n\n{p['desc']}\n\n💵 Price: ₹{p['rs_price']}\nYour Rs. Balance: ₹{user_rs}"
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🛒 Buy Now", callback_data=f"buy_paid_{idx}"))
    
    if p['image']:
        bot.send_photo(call.message.chat.id, p['image'], caption=text, parse_mode="Markdown", reply_markup=markup)
    else:
        bot.send_message(call.message.chat.id, text, parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_paid_"))
def buy_paid_product(call):
    idx = int(call.data.split("_")[2])
    uid = str(call.from_user.id)
    db = load_data()
    p = db["paid_products"][idx]
    
    user_rs = db["users"][uid]["rs"]
    price = p["rs_price"]
    
    if user_rs < price:
        bot.answer_callback_query(call.id, "❌ Insufficient Rs. Balance in Wallet!", show_alert=True)
        return
    
    db["users"][uid]["rs"] -= price
    remaining_rs = db["users"][uid]["rs"]
    
    db["users"][uid]["purchases"].append({"type": "paid", "name": p['title'], "file": p['file']})
    save_data(db)
    
    text = (
        f"✅ **Purchase Successful!**\n\n"
        f"Product: {p['title']}\n"
        f"Price: ₹{price}\n"
        f"Remaining Balance: ₹{remaining_rs}\n\n"
        f"📁 **File:** `{p['file']}`"
    )
    markup = types.InlineKeyboardMarkup()
    if p['tutorial']:
        markup.add(types.InlineKeyboardButton("📺 Tutorial Video", url=p['tutorial']))
    
    bot.send_message(call.message.chat.id, text, parse_mode="Markdown", reply_markup=markup)

# --- RAFFLE STATUS & HISTORY ---
@bot.message_handler(func=lambda m: m.text in ["📊 Raffle Status", "📊 র‍্যাফেল স্ট্যাটাস", "📊 रैffle स्टेटस"])
def raffle_status(message):
    db = load_data()
    total_raffles = len(db["raffles"])
    total_coins = sum([u["coin"] for u in db["users"].values()])
    
    text = (
        f"📊 **Raffle Status Dashboard**\n\n"
        f"Total Raffles Participated: {total_raffles}\n"
        f"Total 🪙 Coins in System: {total_coins}\n"
        f"Per Raffle Cost: 1 🪙"
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text in ["📜 Raffle History", "📜 র‍্যাফেল ইতিহাস", "📜 रैffle इतिहास"])
def raffle_history(message):
    db = load_data()
    raffles = db["raffles"]
    if not raffles:
        bot.send_message(message.chat.id, "No raffle history found.")
        return
    
    text = "📜 **Raffle History:**\n\n"
    for r in raffles[-10:]:  # Last 10
        text += f"👤 {r['name']} (@{r['username']})\n🔗 {r['link']}\n⏱ {r['time']}\n-------------------\n"
    bot.send_message(message.chat.id, text)

# --- PURCHASE HISTORY ---
@bot.message_handler(func=lambda m: m.text in ["🛍️ Purchase History", "🛍️ কেনাকাটার ইতিহাস", "🛍️ खरीदी इतिहास"])
def purchase_history_menu(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("🎁 Free Purchases", callback_data="hist_free"),
        types.InlineKeyboardButton("💎 Paid Purchases", callback_data="hist_paid")
    )
    bot.send_message(message.chat.id, "Select purchase category:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in ["hist_free", "hist_paid"])
def show_purchase_history(call):
    uid = str(call.from_user.id)
    db = load_data()
    purchases = db["users"].get(uid, {}).get("purchases", [])
    
    p_type = "free" if call.data == "hist_free" else "paid"
    filtered = [p for p in purchases if p["type"] == p_type]
    
    if not filtered:
        bot.answer_callback_query(call.id, "No items found in history!")
        return
    
    text = f"🛍️ **Your {p_type.capitalize()} Purchases:**\n\n"
    for item in filtered:
        text += f"📦 {item['name']}\n📁 File: `{item['file']}`\n\n"
    bot.send_message(call.message.chat.id, text, parse_mode="Markdown")

# --- LEADERBOARD ---
@bot.message_handler(func=lambda m: m.text in ["🏆 Raffle Leaderboard", "🏆 র‍্যাফেল লিডারবোর্ড", "🏆 रैffle लीडरबोर्ड"])
def leaderboard(message):
    db = load_data()
    users = db["users"]
    
    sorted_users = sorted(users.items(), key=lambda x: x[1]['coin'], reverse=True)[:5]
    
    text = "🏆 **Raffle & Coin Leaderboard (Top 5):**\n\n"
    rank = 1
    for uid, data in sorted_users:
        text += f"{rank}. User ID: `{uid}` | 🪙 Coins: {data['coin']}\n"
        rank += 1
        
    my_uid = str(message.from_user.id)
    my_coins = users.get(my_uid, {}).get("coin", 0)
    text += f"\n👉 **Your Coins:** {my_coins}"
    
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

# --- ADMIN PANEL ---
@bot.message_handler(func=lambda m: m.text == "👑 /admin")
def admin_panel(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "Unauthorized access!")
        return
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("➕ Add Product"),
        types.KeyboardButton("📦 Manage Products"),
        types.KeyboardButton("📊 Dashboard"),
        types.KeyboardButton("👥 Users & Balance"),
        types.KeyboardButton("💳 Payment Requests"),
        types.KeyboardButton("📢 Send Notification"),
        types.KeyboardButton("🔙 Exit Admin")
    )
    bot.send_message(message.chat.id, "👑 Welcome to Admin Panel:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🔙 Exit Admin")
def exit_admin(message):
    bot.send_message(message.chat.id, "Exited Admin Panel.", reply_markup=main_menu(message.from_user.id))

# ADMIN DASHBOARD
@bot.message_handler(func=lambda m: m.text == "📊 Dashboard")
def admin_dashboard(message):
    if message.from_user.id != ADMIN_ID: return
    db = load_data()
    total_users = len(db["users"])
    total_files = sum([len(u["purchases"]) for u in db["users"].values()])
    total_coins = sum([u["coin"] for u in db["users"].values()])
    
    text = (
        f"📊 **Admin Dashboard:**\n\n"
        f"👥 Total Users: {total_users}\n"
        f"📦 Total Files Bought: {total_files}\n"
        f"🪙 Total Coins in Circulation: {total_coins}"
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

# PAYMENT APPROVAL ADMIN CALLBACKS
@bot.callback_query_handler(func=lambda call: call.data.startswith(("app_", "rej_")))
def handle_payment_approval(call):
    if call.from_user.id != ADMIN_ID: return
    action, pay_id = call.data.split("_")
    db = load_data()
    
    target_payment = None
    for p in db["payments"]:
        if p["pay_id"] == pay_id:
            target_payment = p
            break
            
    if not target_payment:
        bot.answer_callback_query(call.id, "Payment record not found!")
        return
        
    uid = target_payment["uid"]
    amount = target_payment["amount"]
    
    if action == "app":
        db["users"][uid]["rs"] += amount
        target_payment["status"] = "approved"
        save_data(db)
        bot.send_message(uid, f"✅ Your payment of ₹{amount} has been approved and added to your wallet!")
        bot.edit_message_caption(caption=call.message.caption + "\n\n✅ **APPROVED**", chat_id=call.message.chat.id, message_id=call.message.message_id)
    else:
        target_payment["status"] = "rejected"
        save_data(db)
        bot.send_message(uid, f"❌ Your payment of ₹{amount} was rejected by Admin.")
        bot.edit_message_caption(caption=call.message.caption + "\n\n❌ **REJECTED**", chat_id=call.message.chat.id, message_id=call.message.message_id)
        
    bot.answer_callback_query(call.id, "Action completed successfully!")

# ADD PRODUCT STEP-BY-STEP WIZARD (State handled simply)
temp_product_storage = {}

@bot.message_handler(func=lambda m: m.text == "➕ Add Product")
def admin_add_product(message):
    if message.from_user.id != ADMIN_ID: return
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("🎁 Free Coin Product", callback_data="add_type_free"),
        types.InlineKeyboardButton("💎 Paid Rs. Product", callback_data="add_type_paid")
    )
    bot.send_message(message.chat.id, "Select product type to add:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("add_type_"))
def set_prod_type(call):
    p_type = call.data.split("_")[2]
    temp_product_storage[call.from_user.id] = {"type": p_type}
    msg = bot.send_message(call.message.chat.id, "Enter Product Title:")
    bot.register_next_step_handler(msg, get_prod_title)

def get_prod_title(message):
    uid = message.from_user.id
    temp_product_storage[uid]["title"] = message.text
    msg = bot.send_message(message.chat.id, "Enter Product Description:")
    bot.register_next_step_handler(msg, get_prod_desc)

def get_prod_desc(message):
    uid = message.from_user.id
    temp_product_storage[uid]["desc"] = message.text
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Skip Image", callback_data="skip_image"))
    bot.send_message(message.chat.id, "Upload Product Image (or click Skip):", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "skip_image")
def skip_image(call):
    uid = call.from_user.id
    temp_product_storage[uid]["image"] = None
    ask_price_or_coins(call.message)

@bot.message_handler(content_types=['photo'])
def get_prod_image(message):
    uid = message.from_user.id
    if uid in temp_product_storage and "image" not in temp_product_storage[uid]:
        temp_product_storage[uid]["image"] = message.photo[-1].file_id
        ask_price_or_coins(message)

def ask_price_or_coins(message):
    uid = message.chat.id if hasattr(message, 'chat') else message.from_user.id
    p_type = temp_product_storage[uid]["type"]
    prompt = "Enter Coin Price (e.g. 50):" if p_type == "free" else "Enter Rs. Price (e.g. 100):"
    msg = bot.send_message(uid, prompt)
    bot.register_next_step_handler(msg, get_prod_cost)

def get_prod_cost(message):
    uid = message.from_user.id
    try:
        val = float(message.text)
        p_type = temp_product_storage[uid]["type"]
        if p_type == "free":
            temp_product_storage[uid]["coin_price"] = int(val)
        else:
            temp_product_storage[uid]["rs_price"] = val
            
        msg = bot.send_message(message.chat.id, "Enter Downloadable File Name / Link:")
        bot.register_next_step_handler(msg, get_prod_file)
    except ValueError:
        bot.send_message(message.chat.id, "Invalid number. Try again.")

def get_prod_file(message):
    uid = message.from_user.id
    temp_product_storage[uid]["file"] = message.text
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Skip Tutorial", callback_data="skip_tutorial"))
    bot.send_message(message.chat.id, "Enter Tutorial Video URL (or click Skip):", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "skip_tutorial")
def skip_tutorial(call):
    uid = call.from_user.id
    temp_product_storage[uid]["tutorial"] = None
    finalize_product(call.message)

@bot.message_handler(func=lambda m: m.from_user.id in temp_product_storage and "tutorial" not in temp_product_storage[m.from_user.id])
def get_prod_tutorial(message):
    uid = message.from_user.id
    temp_product_storage[uid]["tutorial"] = message.text
    finalize_product(message)

def finalize_product(message):
    uid = message.from_user.id if hasattr(message, 'from_user') else message.chat.id
    p_data = temp_product_storage.get(uid)
    
    db = load_data()
    if p_data["type"] == "free":
        db["free_products"].append(p_data)
    else:
        db["paid_products"].append(p_data)
    save_data(db)
    
    bot.send_message(uid, "✅ Product Added Successfully!")
    del temp_product_storage[uid]

# BROADCAST NOTIFICATION ADMIN
@bot.message_handler(func=lambda m: m.text == "📢 Send Notification")
def admin_broadcast(message):
    if message.from_user.id != ADMIN_ID: return
    msg = bot.send_message(message.chat.id, "Enter the notification message text to broadcast:")
    bot.register_next_step_handler(msg, process_broadcast)

def process_broadcast(message):
    text = message.text
    db = load_data()
    users = db["users"].keys()
    
    success = 0
    fail = 0
    
    for uid in users:
        try:
            bot.send_message(uid, f"📢 **Announcement:**\n\n{text}", parse_mode="Markdown")
            success += 1
        except Exception:
            fail += 1
            
    bot.send_message(message.chat.id, f"✅ Broadcast Complete!\n\nTotal Sent: {success}\nTotal Failed: {fail}")

# PAYMENT REQUESTS LIST ADMIN
@bot.message_handler(func=lambda m: m.text == "💳 Payment Requests")
def admin_payment_requests(message):
    if message.from_user.id != ADMIN_ID: return
    db = load_data()
    pending = [p for p in db["payments"] if p["status"] == "pending"]
    if not pending:
        bot.send_message(message.chat.id, "No pending payment requests.")
        return
    
    for p in pending:
        text = f"Payment ID: {p['pay_id']}\nUser: {p['name']} (`{p['uid']}`)\nAmount: ₹{p['amount']}"
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("✅ Approve", callback_data=f"app_{p['pay_id']}"),
            types.InlineKeyboardButton("❌ Reject", callback_data=f"rej_{p['pay_id']}")
        )
        bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=markup)

# --- RUN BOT ---
if __name__ == "__main__":
    init_db()
    print("Bot is running smoothly...")
    bot.infinity_polling()
