import telebot
from flask import Flask
from threading import Thread
from telebot import types
import psycopg2
import os

TOKEN = os.environ.get('TOKEN')
ADMIN_ID = '6367413561'
DATABASE_URL = os.environ.get('DATABASE_URL')

VALID_CODES = {
    "49182": "girl", "73719": "girl", "28405": "girl", "91837": "girl", "56204": "girl",
    "10593": "girl", "84621": "girl", "37048": "girl", "62915": "girl", "05732": "girl",
    "81924": "boy", "37405": "boy", "92058": "boy", "16539": "boy", "74812": "boy",
    "50396": "boy", "28147": "boy", "65930": "boy", "41785": "boy", "09624": "boy",
    "849201": "all", "375912": "all", "620485": "all", "193746": "all", "758204": "all", 
    "300123": "med", "444777": "med", "555888": "med", "TECH255524":  "tech", "PHONE254745": "phone",    
    "TECH26645":  "tech", "PHONE567524": "phone"
}

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
user_states = {}

def get_db():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS sellers (user_id BIGINT PRIMARY KEY, name TEXT, phone TEXT, gender TEXT, registered_code TEXT, total_sales INTEGER DEFAULT 0, total_orders INTEGER DEFAULT 0, total_earned REAL DEFAULT 0.0)')
    cursor.execute('CREATE TABLE IF NOT EXISTS products (id SERIAL PRIMARY KEY, category TEXT, name TEXT, photo_id TEXT, media_type TEXT, price_stock TEXT, price_4_7 TEXT, price_15_22 TEXT, description TEXT)')
    conn.commit()
    cursor.close()
    conn.close()

init_db()

@app.route('/')
def index():
    return "Bot is running!"

@bot.message_handler(commands=['start'])
def start(message):
    if str(message.from_user.id) == ADMIN_ID:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("➕ Иловаи моли нав", "📋 Рӯйхати молҳо")
        markup.add("📊 Ҳисоботи фурӯшандагон", "🏆 Топ-фурӯшандагон")
        markup.add("👥 Идоракунии фурӯшандагон", "🗑 Нест кардани мол")
        markup.add("🔙 Бозгашт ба меню")
        bot.send_message(message.chat.id, "👑 ПАНЕЛИ АДМИН:", reply_markup=markup)
    else:
        user_states[message.chat.id] = {'state': 'waiting_name'}
        bot.send_message(message.chat.id, "Ассалому алайкум! Хуш омадед.\n\nЛутфан, ному насаби худро нависед:")
        
@bot.message_handler(func=lambda message: user_states.get(message.chat.id, {}).get('state') == 'waiting_name')
def get_name(message):
    user_states[message.chat.id]['name'] = message.text
    user_states[message.chat.id]['state'] = 'waiting_phone'
    bot.send_message(message.chat.id, "Ташаккур! Ҳоло рақами телефони худро нависед:")

@bot.message_handler(func=lambda message: user_states.get(message.chat.id, {}).get('state') == 'waiting_phone')
def get_phone(message):
    user_states[message.chat.id]['phone'] = message.text
    user_states[message.chat.id]['state'] = 'waiting_code'
    try:
        bot.send_message(ADMIN_ID, f"🛍️ ДАРХОСТИ НАВ!\n\n👤 Ном: {user_states[message.chat.id]['name']}\n📱 Рақам: {message.text}")
    except:
        pass
    bot.send_message(message.chat.id, "Ташаккур! Дархост қабул шуд.\n\nЛутфан, коди худро ворид кунед:")

def show_main_menu(chat_id, gender):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    if gender == "med":
        markup.add("🌿 Табиӣ ва Дору", "📊 Ҳисоби ман", "🏆 Рейтинг", "📞 Тамос бо мо")
    elif gender == "girl":
        markup.add("👗 Либосҳои занона", "👟 Пойафзоли занона", "👜 Сумкаҳо", "💄 Косметика", "🌿 Табиӣ ва Дору", "📊 Ҳисоби ман", "🏆 Рейтинг", "📞 Тамос бо мо")
    elif gender == "boy":
        markup.add("👕 Либосҳои мардона", "👞 Пойафзоли мардона", "🎒 Сумкаҳо", "🧴 Дигар чизҳо", "🌿 Табиӣ ва Дору", "📊 Ҳисоби ман", "🏆 Рейтинг", "📞 Тамос бо мо")
    elif gender == "tech":
        markup.add("🔌 Асбобҳои рӯзғор", "📊 Ҳисоби ман", "🏆 Рейтинг", "📞 Тамос бо мо")
    elif gender == "phone":
        markup.add("📱 Телефонҳо", "📊 Ҳисоби ман", "🏆 Рейтинг", "📞 Тамос бо мо")
    else:
        markup.add("👗 Либосҳои занона", "👕 Либосҳои мардона", "👟 Пойафзоли занона", "👞 Пойафзоли мардона", "👜 Сумкаҳо", "💄 Косметика", "🧴 Дигар чизҳо", "🌿 Табиӣ ва Дору", "📊 Ҳисоби ман", "🏆 Рейтинг", "📞 Тамос бо мо")
    bot.send_message(chat_id, "🏠 Менюи асосӣ:", reply_markup=markup)

@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get('state') == 'waiting_code')
def check_code(message):
    entered_code = message.text.strip()
    if entered_code not in VALID_CODES:
        bot.send_message(message.chat.id, "❌ Код хато аст!")
        return

    conn = get_db()
    cursor = conn.cursor()
    
    # 1. Тафтиши он ки ин код аллакай истифода нашудааст
    cursor.execute('SELECT user_id FROM sellers WHERE registered_code = %s', (entered_code,))
    if cursor.fetchone():
        bot.send_message(message.chat.id, "❌ Ин код аллакай истифода шудааст!")
        cursor.close()
        conn.close()
        return
        
    # 2. Тафтиши он ки ин корбар аллакай сабти ном нашудааст (Иловаи нав)
    cursor.execute('SELECT user_id FROM sellers WHERE user_id = %s', (message.chat.id,))
    if cursor.fetchone():
        bot.send_message(message.chat.id, "❌ Шумо аллакай сабти ном шудаед! Барои санҷиши нав, аввал аккаунти худро дар панели Админ нест кунед.")
        cursor.close()
        conn.close()
        return

    # 3. Сабти корбари нав
    gender = VALID_CODES[entered_code]
    user_states[message.chat.id]['state'] = 'authorized'
    user_states[message.chat.id]['gender'] = gender
    
    cursor.execute('INSERT INTO sellers (user_id, name, phone, gender, registered_code) VALUES (%s, %s, %s, %s, %s)', (message.chat.id, user_states[message.chat.id]['name'], user_states[message.chat.id]['phone'], gender, entered_code))
    conn.commit()
    cursor.close()
    conn.close()
    bot.send_message(message.chat.id, "✅ Код қабул шуд!")
    show_main_menu(message.chat.id, gender)

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if str(message.chat.id) != ADMIN_ID:
        return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("➕ Иловаи моли нав", "📋 Рӯйхати молҳо", "📊 Ҳисоботи фурӯшандагон", "🏆 Топ-фурӯшандагон", "👥 Идоракунии фурӯшандагон", "🗑 Нест кардани мол", "⬅️ Бозгашт ба меню")
    bot.send_message(message.chat.id, "👑 ПАНЕЛИ АДМИН:", reply_markup=markup)

@bot.message_handler(func=lambda message: str(message.chat.id) == ADMIN_ID and message.text == "👥 Идоракунии фурӯшандагон")
def manage_sellers(message):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, name, phone FROM sellers')
    sellers = cursor.fetchall()
    cursor.close()
    conn.close()
    if not sellers:
        bot.send_message(message.chat.id, "Ҳоло фурӯшандагон нест.")
        return
    markup = types.InlineKeyboardMarkup(row_width=1)
    for s in sellers:
        markup.add(types.InlineKeyboardButton(f"❌ {s[1]} ({s[2]})", callback_data=f"del_seller_{s[0]}"))
    bot.send_message(message.chat.id, "Барои нест кардан, номро пахш кунед:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('del_seller_'))
def delete_seller_callback(call):
    if str(call.message.chat.id) != ADMIN_ID:
        return
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM sellers WHERE user_id = %s', (int(call.data.split('_')[2]),))
    conn.commit()
    cursor.close()
    conn.close()
    bot.answer_callback_query(call.id, "✅ Нест карда шуд!")
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="✅ Фурӯшанда нест карда шуд.", reply_markup=None)

@bot.message_handler(func=lambda message: str(message.chat.id) == ADMIN_ID and message.text == "📊 Ҳисоботи фурӯшандагон")
def admin_seller_report(message):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT name, phone, total_sales, total_earned FROM sellers')
    sellers = cursor.fetchall()
    cursor.close()
    conn.close()
    if not sellers:
        bot.send_message(message.chat.id, "Ҳоло фурӯшандагон нест.")
        return
    text = "📊 <b>ҲИСОБОТ:</b>\n"
    for s in sellers:
        text += f"👤 <b>{s[0]}</b> ({s[1]})\n🛍 {s[2]} фурӯш | 💰 {s[3]}с\n➖➖➖➖\n"
    bot.send_message(message.chat.id, text, parse_mode='HTML')

@bot.message_handler(func=lambda message: str(message.chat.id) == ADMIN_ID and message.text == "🏆 Топ-фурӯшандагон")
def admin_top_sellers(message):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT name, total_sales FROM sellers ORDER BY total_sales DESC LIMIT 5')
    top = cursor.fetchall()
    cursor.close()
    conn.close()
    if top:
        text = "🏆 <b>ТОП-5:</b>\n"
        for i, (n, s) in enumerate(top, 1):
            text += f"{i}. <b>{n}</b> — {s} фурӯш\n"
        bot.send_message(message.chat.id, text, parse_mode='HTML')
    else:
        bot.send_message(message.chat.id, "Рейтинг холӣ аст.")

@bot.message_handler(func=lambda message: str(message.chat.id) == ADMIN_ID and message.text == "➕ Иловаи моли нав")
def add_product_start(message):
    user_states[message.chat.id] = {'state': 'admin_photo'}
    bot.send_message(message.chat.id, "📸 Акс ё видеоро фиристед:")

@bot.message_handler(func=lambda message: str(message.chat.id) == ADMIN_ID and user_states.get(message.chat.id, {}).get('state') == 'admin_photo', content_types=['photo', 'video'])
def add_product_photo(message):
    if message.content_type == 'photo':
        user_states[message.chat.id]['photo_id'] = message.photo[-1].file_id
        user_states[message.chat.id]['media_type'] = 'photo'
    else:
        user_states[message.chat.id]['photo_id'] = message.video.file_id
        user_states[message.chat.id]['media_type'] = 'video'
    user_states[message.chat.id]['state'] = 'admin_category'
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("👕 Либосҳои мардона", "👗 Либосҳои занона", "👞 Пойафзоли мардона", "👟 Пойафзоли занона", "👜 Сумкаҳо", "💄 Косметика", "🌿 Табиӣ ва Дору", "🧴 Дигар чизҳо", "Acбобҳои рӯзғор", "Телефонҳо") 
    bot.send_message(message.chat.id, "📁 Бахшро интихоб кунед:", reply_markup=markup)

@bot.message_handler(func=lambda message: str(message.chat.id) == ADMIN_ID and user_states.get(message.chat.id, {}).get('state') == 'admin_category')
def add_product_category(message):
    user_states[message.chat.id]['category'] = message.text
    user_states[message.chat.id]['state'] = 'admin_name'
    bot.send_message(message.chat.id, "📝 Номи молро нависед:")

@bot.message_handler(func=lambda message: str(message.chat.id) == ADMIN_ID and user_states.get(message.chat.id, {}).get('state') == 'admin_name')
def add_product_name(message):
    user_states[message.chat.id]['name'] = message.text
    user_states[message.chat.id]['state'] = 'admin_description'
    bot.send_message(message.chat.id, "📄 Тавсифи молро нависед:")

@bot.message_handler(func=lambda message: str(message.chat.id) == ADMIN_ID and user_states.get(message.chat.id, {}).get('state') == 'admin_description')
def add_product_description(message):
    user_states[message.chat.id]['description'] = message.text
    user_states[message.chat.id]['state'] = 'admin_price_stock'
    bot.send_message(message.chat.id, "💵 Нархи Наличи (ё `-`):")

@bot.message_handler(func=lambda message: str(message.chat.id) == ADMIN_ID and user_states.get(message.chat.id, {}).get('state') == 'admin_price_stock')
def add_product_price_stock(message):
    user_states[message.chat.id]['price_stock'] = message.text
    user_states[message.chat.id]['state'] = 'admin_price_4_7'
    bot.send_message(message.chat.id, "💵 Нархи 4-7 рӯз (ё `-`):")

@bot.message_handler(func=lambda message: str(message.chat.id) == ADMIN_ID and user_states.get(message.chat.id, {}).get('state') == 'admin_price_4_7')
def add_product_price_4_7(message):
    user_states[message.chat.id]['price_4_7'] = message.text
    user_states[message.chat.id]['state'] = 'admin_price_15_22'
    bot.send_message(message.chat.id, "💵 Нархи 15-22 рӯз (ё `-`):")

@bot.message_handler(func=lambda message: str(message.chat.id) == ADMIN_ID and user_states.get(message.chat.id, {}).get('state') == 'admin_price_15_22')
def add_product_price_15_22(message):
    user_states[message.chat.id]['price_15_22'] = message.text
    d = user_states[message.chat.id]
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO products (category, name, photo_id, media_type, price_stock, price_4_7, price_15_22, description) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', (d['category'], d['name'], d['photo_id'], d['media_type'], d['price_stock'], d['price_4_7'], d['price_15_22'], d['description']))
    conn.commit()
    cursor.close()
    conn.close()
    bot.send_message(message.chat.id, "✅ Мол илова шуд!")
    user_states[message.chat.id]['state'] = 'authorized'
    admin_panel(message)

@bot.message_handler(func=lambda message: str(message.chat.id) == ADMIN_ID and message.text == "📋 Рӯйхати молҳо")
def list_products(message):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, category, name, price_stock FROM products')
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    if not rows:
        bot.send_message(message.chat.id, "Ҳоло молҳо нест.")
        return
    text = "📋 <b>Молҳо:</b>\n"
    for r in rows:
        text += f"#{r[0]} | {r[1]} | {r[2]} | {r[3]}с\n"
    bot.send_message(message.chat.id, text, parse_mode='HTML')

@bot.message_handler(func=lambda message: str(message.chat.id) == ADMIN_ID and message.text == "🗑 Нест кардани мол")
def delete_product_prompt(message):
    bot.send_message(message.chat.id, "Рақами молро нависед:")
    user_states[message.chat.id] = {'state': 'admin_delete'}

@bot.message_handler(func=lambda message: str(message.chat.id) == ADMIN_ID and user_states.get(message.chat.id, {}).get('state') == 'admin_delete')
def delete_product(message):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM products WHERE id = %s', (int(message.text),))
        conn.commit()
        cursor.close()
        conn.close()
        bot.send_message(message.chat.id, "✅ Нест карда шуд.")
    except:
        bot.send_message(message.chat.id, "Хато.")
    user_states[message.chat.id]['state'] = 'authorized'
    admin_panel(message)

@bot.message_handler(func=lambda message: str(message.chat.id) == ADMIN_ID and message.text == "⬅️ Бозгашт ба меню")
def back_to_menu_admin(message):
    user_states[message.chat.id]['state'] = 'authorized'
    show_main_menu(message.chat.id, user_states.get(message.chat.id, {}).get('gender', 'boy'))

def show_products_page(chat_id, category, page):
    items_per_page = 5
    offset = (page - 1) * items_per_page
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM products WHERE category = %s', (category,))
    total_items = cursor.fetchone()[0]
    cursor.execute('SELECT id, name, price_stock FROM products WHERE category = %s LIMIT %s OFFSET %s', (category, items_per_page, offset))
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    if total_items == 0:
        bot.send_message(chat_id, "🌿 Молҳо нест.")
        return
    total_pages = (total_items + items_per_page - 1) // items_per_page
    markup = types.InlineKeyboardMarkup(row_width=1)
    for p in products:
        markup.add(types.InlineKeyboardButton(f"{p[1]} - {p[2]}с", callback_data=f"view_{p[0]}"))
    nav = []
    if page > 1:
        nav.append(types.InlineKeyboardButton("⬅️ Қаблӣ", callback_data=f"page_{page-1}"))
    if page < total_pages:
        nav.append(types.InlineKeyboardButton("Баъдӣ ➡️", callback_data=f"page_{page+1}"))
    if nav:
        markup.row(*nav)
    bot.send_message(chat_id, f"📁 <b>{category}</b> (Саҳифаи {page} аз {total_pages})", reply_markup=markup, parse_mode='HTML')

@bot.message_handler(func=lambda message: user_states.get(message.chat.id, {}).get('state') == 'authorized')
def handle_menu(message):
    text = message.text
    ug = user_states.get(message.chat.id, {}).get('gender')
    if ug == "med" and not ("Табиӣ" in text or "Ҳисоб" in text or "Рейтинг" in text or "Тамос" in text):
        bot.send_message(message.chat.id, "❌ Танҳо бахши Табиӣ.")
        return
    if any(x in text for x in ["Сумкаҳо", "Косметика", "Дигар", "Табиӣ", "Либос", "Пойафзол", "Асбобҳои рӯзғор", "Телефонҳо",]):
        user_states[message.chat.id]['current_cat'] = text
        show_products_page(message.chat.id, text, 1)
    elif "Рейтинг" in text:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT name, total_sales FROM sellers ORDER BY total_sales DESC LIMIT 5')
        top = cursor.fetchall()
        cursor.close()
        conn.close()
        if top:
            t = "🏆 <b>ТОП-5:</b>\n"
            for i, (n, s) in enumerate(top, 1):
                t += f"{i}. <b>{n}</b> — {s} фурӯш\n"
            bot.send_message(message.chat.id, t, parse_mode='HTML')
        else:
            bot.send_message(message.chat.id, "Рейтинг холӣ аст.")
    elif "Ҳисоби ман" in text:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT total_orders, total_sales, total_earned, name FROM sellers WHERE user_id = %s', (message.chat.id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        if row:
            o, s, e, n = row
            rank = "🥇 Тилоӣ" if e >= 1000 else "🥈 Нуқраӣ" if e >= 500 else "🥉 Биринҷӣ"
            bot.send_message(message.chat.id, f"👑 <b>КАБИНЕТ</b>\n👤 {n}\n🏆 {rank}\n📦 {o} | 🛍 {s} | 💰 {e}с", parse_mode='HTML')
        else:
            bot.send_message(message.chat.id, "Ҳисоб холӣ аст.")
    elif "Тамос" in text:
        bot.send_message(message.chat.id, "📞 +992 02-332-19-19\nTelegram: @Rustamzoda6789")

@bot.callback_query_handler(func=lambda call: call.data.startswith('page_'))
def handle_pagination(call):
    page = int(call.data.split('_')[1])
    cat = user_states.get(call.message.chat.id, {}).get('current_cat')
    if cat:
        show_products_page(call.message.chat.id, cat, page)
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('view_'))
def view_product(call):
    pid = call.data.split('_')[1]
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT name, photo_id, media_type, price_stock, price_4_7, price_15_22, description FROM products WHERE id = %s', (pid,))
    p = cursor.fetchone()
    cursor.close()
    conn.close()
    if not p:
        bot.answer_callback_query(call.id, "Мол нест!")
        return
    pname, mid, mt, ps, p4, p15, pd = p
    markup = types.InlineKeyboardMarkup(row_width=1)
    if ps and ps != '-': markup.add(types.InlineKeyboardButton(f"🟢 Наличи - {ps}с", callback_data=f"order_{pid}_stock"))
    if p4 and p4 != '-': markup.add(types.InlineKeyboardButton(f"🟡 4-7 рӯз - {p4}с", callback_data=f"order_{pid}_4_7"))
    if p15 and p15 != '-': markup.add(types.InlineKeyboardButton(f"🔴 15-22 рӯз - {p15}с", callback_data=f"order_{pid}_15_22"))
    cap = f"📦 <b>{pname}</b>"
    if pd and pd != '-': cap += f"\n📝 {pd}"
    try:
        if mt == 'video':
            bot.send_video(call.message.chat.id, mid, caption=cap, reply_markup=markup, parse_mode='HTML')
        else:
            bot.send_photo(call.message.chat.id, mid, caption=cap, reply_markup=markup, parse_mode='HTML')
    except:
        bot.send_message(call.message.chat.id, cap + "\n(Медиа нест)", reply_markup=markup, parse_mode='HTML')
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('order_'))
def handle_order_type(call):
    _, pid, otype = call.data.split('_', 2)
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT name, price_stock, price_4_7, price_15_22 FROM products WHERE id = %s', (pid,))
    p = cursor.fetchone()
    cursor.close()
    conn.close()
    if not p:
        return
    if otype == 'stock': ttext, price = "🟢 Наличи", p[1]
    elif otype == '4_7': ttext, price = "🟡 4-7 рӯз", p[2]
    else: ttext, price = "🔴 15-22 рӯз", p[3]
    user_states[call.message.chat.id] = {'state': 'waiting_order_details', 'product': p[0], 'order_type': ttext, 'price': price}
    bot.send_message(call.message.chat.id, f"📦 {p[0]}\n📋 {ttext}\n💵 {price}с\n\nРанг, андоза, миқдорро нависед:")
    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda message: user_states.get(message.chat.id, {}).get('state') == 'waiting_order_details')
def handle_order_details(message):
    d = user_states[message.chat.id]
    try:
        bot.send_message(ADMIN_ID, f"🛍️ <b>ФАРМОИШИ НАВ!</b>\n\n👤 {message.from_user.first_name}\n📦 {d['product']}\n📋 {d['order_type']}\n💵 {d['price']}с\n🎨 {message.text}", parse_mode='HTML')
        bot.send_message(message.chat.id, "✅ Фармоиш равон шуд!")
    except:
        pass
    d['state'] = 'authorized'

@bot.message_handler(commands=['add_sale'])
def admin_add_sale(message):
    if str(message.chat.id) == ADMIN_ID:
        try:
            args = message.text.split()
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute('UPDATE sellers SET total_orders = total_orders + 1, total_sales = total_sales + 1, total_earned = total_earned + %s WHERE user_id = %s', (float(args[2]), int(args[1])))
            conn.commit()
            cursor.close()
            conn.close()
            bot.reply_to(message, "✅ Сабт шуд.")
        except:
            bot.reply_to(message, "Хато. Мисол: /add_sale 123456789 50")

def run_bot():
    bot.polling(none_stop=True)

if __name__ == '__main__':
    t = Thread(target=run_bot)
    t.start()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
