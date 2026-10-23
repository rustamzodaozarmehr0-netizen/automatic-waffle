import telebot
from flask import Flask
from threading import Thread
from telebot import types
import sqlite3
import os

# ТОКЕН ВА ID-И ХУДРО ИН ҶО ГУЗОР
TOKEN = '8944741788:AAGGSOQ7tpkeX8uJ-7-6pl_11imx_xgvr5w'
ADMIN_ID = '6367413561' # ID-и худатро нависед!

VALID_CODES = {
    # 👗 Кодҳои духтарон (5 рақама)
    "49182": "girl", "73719": "girl", "28405": "girl", "91837": "girl", "56204": "girl",
    "10593": "girl", "84621": "girl", "37048": "girl", "62915": "girl", "05732": "girl",
    "29483": "girl", "61824": "girl", "75039": "girl", "18347": "girl", "50264": "girl",
    "93821": "girl", "46715": "girl", "82940": "girl", "31576": "girl", "60482": "girl",

    # 👕 Кодҳои писарон (5 рақама)
    "81924": "boy", "37405": "boy", "92058": "boy", "16539": "boy", "74812": "boy",
    "50396": "boy", "28147": "boy", "65930": "boy", "41785": "boy", "09624": "boy",
    "73582": "boy", "14906": "boy", "86231": "boy", "40875": "boy", "59123": "boy",
    "27648": "boy", "95310": "boy", "68427": "boy", "32059": "boy", "81746": "boy",

    # 🌟 Кодҳои махсус - Ҳар ду бахш (6 рақама)
    "849201": "all", "375912": "all", "620485": "all", "193746": "all", "758204": "all", "412869": "all"
}

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
user_states = {}

def init_db():
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sellers (
            user_id INTEGER PRIMARY KEY,
            name TEXT, phone TEXT, gender TEXT,
            total_sales INTEGER DEFAULT 0,
            total_orders INTEGER DEFAULT 0,
            total_earned REAL DEFAULT 0.0
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT, name TEXT, photo_id TEXT,
            price_stock TEXT, price_4_7 TEXT, price_15_22 TEXT
        )
    ''')
    try:
        cursor.execute('ALTER TABLE products ADD COLUMN description TEXT')
    except:
        pass
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return "Bot is running!"

@bot.message_handler(commands=['start'])
def start(message):
    user_states[message.chat.id] = {'state': 'waiting_name'}
    bot.send_message(message.chat.id, "Ассалому алайкум! Хуш омадед ба FL STYLE.\n\nЛутфан, ному насаби худро нависед:")

@bot.message_handler(func=lambda message: user_states.get(message.chat.id, {}).get('state') == 'waiting_name')
def get_name(message):
    user_states[message.chat.id]['name'] = message.text
    user_states[message.chat.id]['state'] = 'waiting_phone'
    bot.send_message(message.chat.id, "Ташаккур! Ҳоло рақами телефони худро нависед:")

@bot.message_handler(func=lambda message: user_states.get(message.chat.id, {}).get('state') == 'waiting_phone')
def get_phone(message):
    user_states[message.chat.id]['phone'] = message.text
    user_states[message.chat.id]['state'] = 'waiting_code'
    name = user_states[message.chat.id]['name']
    phone = user_states[message.chat.id]['phone']
    try:
        bot.send_message(ADMIN_ID, f"🛍️ ДАРХОСТИ НАВ!\n\n👤 Ном: {name}\n📱 Рақам: {phone}")
    except Exception as e:
        print(f"Хато: {e}")
    bot.send_message(message.chat.id, "Ташаккур! Дархост қабул шуд.\n\nЛутфан, коди худро ворид кунед:")

def show_main_menu(chat_id, gender):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    if gender == "girl":
        markup.add(types.KeyboardButton("👗 Либосҳои занона"), types.KeyboardButton("👟 Пойафзоли занона"),
                   types.KeyboardButton("👜 Сумкаҳо"), types.KeyboardButton("💄 Косметика"))
    elif gender == "boy":
        markup.add(types.KeyboardButton("👕 Либосҳои мардона"), types.KeyboardButton("👞 Пойафзоли мардона"),
                   types.KeyboardButton("🎒 Сумкаҳо"), types.KeyboardButton("🧴 Дигар чизҳо"))
    else: # "all" (Ҳар ду бахш)
        markup.add(types.KeyboardButton("👗 Либосҳои занона"), types.KeyboardButton("👕 Либосҳои мардона"))
        markup.add(types.KeyboardButton("👟 Пойафзоли занона"), types.KeyboardButton("👞 Пойафзоли мардона"))
        markup.add(types.KeyboardButton("👜 Сумкаҳо"), types.KeyboardButton("💄 Косметика"), types.KeyboardButton("🧴 Дигар чизҳо"))
        
    markup.add(types.KeyboardButton("🌿 Табиӣ ва Дору"), types.KeyboardButton("📊 Ҳисоби ман"),
               types.KeyboardButton("🏆 Рейтинг"), types.KeyboardButton("📞 Тамос бо мо"))
    bot.send_message(chat_id, "🏠 Менюи асосӣ\n\nЛутфан, аз меню интихоб кунед:", reply_markup=markup)

@bot.message_handler(func=lambda message: user_states.get(message.chat.id, {}).get('state') == 'waiting_code')
def check_code(message):
    entered_code = message.text.strip()
    if entered_code in VALID_CODES:
        gender = VALID_CODES[entered_code]
        name = user_states[message.chat.id]['name']
        phone = user_states[message.chat.id]['phone']
        user_states[message.chat.id]['state'] = 'authorized'
        user_states[message.chat.id]['gender'] = gender
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()
        cursor.execute('INSERT OR IGNORE INTO sellers (user_id, name, phone, gender) VALUES (?, ?, ?, ?)', 
                       (message.chat.id, name, phone, gender))
        conn.commit()
        conn.close()
        bot.send_message(message.chat.id, "✅ Код қабул шуд! Хуш омадед.")
        show_main_menu(message.chat.id, gender)
    else:
        bot.send_message(message.chat.id, "❌ Код хато аст! Аз нав кӯшиш кунед.")

# ============ ПАНЕЛИ АДМИН ============
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if str(message.chat.id) != ADMIN_ID:
        return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(types.KeyboardButton("➕ Иловаи моли нав"), types.KeyboardButton("📋 Рӯйхати молҳо"))
    markup.add(types.KeyboardButton("📊 Ҳисоботи фурӯшандагон"), types.KeyboardButton("🏆 Топ-фурӯшандагон"))
    markup.add(types.KeyboardButton("🗑 Нест кардани мол"), types.KeyboardButton("⬅️ Бозгашт ба меню"))
    bot.send_message(message.chat.id, "👑 ПАНЕЛИ АДМИН\n\nЛутфан, амалро интихоб кунед:", reply_markup=markup)

@bot.message_handler(func=lambda message: str(message.chat.id) == ADMIN_ID and message.text == "📊 Ҳисоботи фурӯшандагон")
def admin_seller_report(message):
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name, phone, total_sales, total_earned FROM sellers')
    sellers = cursor.fetchall()
    conn.close()
    if not sellers:
        bot.send_message(message.chat.id, "Ҳоло фурӯшандагон нест.")
        return
    report_text = "📊 <b>ҲИСОБОТИ ҲАМАИ ФУРӮШАНДАГОН</b>\n➖➖➖➖➖➖➖➖➖➖\n"
    for s in sellers:
        report_text += f"👤 <b>{s[0]}</b> ({s[1]})\n🛍 Фурӯш: {s[2]} дона\n💰 Комиссия: {s[3]} сомонӣ\n➖➖➖➖➖➖➖➖➖➖\n"
    bot.send_message(message.chat.id, report_text, parse_mode='HTML')

@bot.message_handler(func=lambda message: str(message.chat.id) == ADMIN_ID and message.text == "🏆 Топ-фурӯшандагон")
def admin_top_sellers(message):
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name, total_sales FROM sellers ORDER BY total_sales DESC LIMIT 5')
    top = cursor.fetchall()
    conn.close()
    if top:
        t = "🏆 <b>ТОП-5 ФУРӮШАНДАГОНИ МАҒОЗА</b>\n➖➖➖➖➖➖➖➖➖➖\n"
        for i, (n, s) in enumerate(top, 1):
            t += f"{i}. <b>{n}</b> — {s} фурӯш\n"
        t += "➖➖➖➖➖➖➖➖➖➖"
        bot.send_message(message.chat.id, t, parse_mode='HTML')
    else:
        bot.send_message(message.chat.id, "Рейтинг холӣ аст.")

@bot.message_handler(func=lambda message: str(message.chat.id) == ADMIN_ID and message.text == "➕ Иловаи моли нав")
def add_product_start(message):
    user_states[message.chat.id] = {'state': 'admin_photo'}
    bot.send_message(message.chat.id, "📸 Лутфан, акси молро фиристед (танҳо як акс):")

@bot.message_handler(func=lambda message: str(message.chat.id) == ADMIN_ID and user_states.get(message.chat.id, {}).get('state') == 'admin_photo', content_types=['photo'])
def add_product_photo(message):
    user_states[message.chat.id]['photo_id'] = message.photo[-1].file_id
    user_states[message.chat.id]['state'] = 'admin_category'
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("👕 Либосҳои мардона", "👗 Либосҳои занона", "👞 Пойафзоли мардона", "👟 Пойафзоли занона", "👜 Сумкаҳо", "💄 Косметика", "🌿 Табиӣ ва Дору", "🧴 Дигар чизҳо")
    bot.send_message(message.chat.id, "📁 Ба кадом бахш илова кунем?", reply_markup=markup)

@bot.message_handler(func=lambda message: str(message.chat.id) == ADMIN_ID and user_states.get(message.chat.id, {}).get('state') == 'admin_category')
def add_product_category(message):
    user_states[message.chat.id]['category'] = message.text
    user_states[message.chat.id]['state'] = 'admin_name'
    bot.send_message(message.chat.id, "📝 Номи молро нависед:")

@bot.message_handler(func=lambda message: str(message.chat.id) == ADMIN_ID and user_states.get(message.chat.id, {}).get('state') == 'admin_name')
def add_product_name(message):
    user_states[message.chat.id]['name'] = message.text
    user_states[message.chat.id]['state'] = 'admin_description'
    bot.send_message(message.chat.id, "📄 Тавсифи молро нависед (барои чӣ, таркиб, чӣ тавр истифода мешавад):")

@bot.message_handler(func=lambda message: str(message.chat.id) == ADMIN_ID and user_states.get(message.chat.id, {}).get('state') == 'admin_description')
def add_product_description(message):
    user_states[message.chat.id]['description'] = message.text
    user_states[message.chat.id]['state'] = 'admin_price_stock'
    bot.send_message(message.chat.id, "💵 Нархи Наличи (Тайёр) бо сомонӣ (ё `-` агар нест):")

@bot.message_handler(func=lambda message: str(message.chat.id) == ADMIN_ID and user_states.get(message.chat.id, {}).get('state') == 'admin_price_stock')
def add_product_price_stock(message):
    user_states[message.chat.id]['price_stock'] = message.text
    user_states[message.chat.id]['state'] = 'admin_price_4_7'
    bot.send_message(message.chat.id, "💵 Нархи Под заказ (4-7 рӯз) (ё `-` агар нест):")

@bot.message_handler(func=lambda message: str(message.chat.id) == ADMIN_ID and user_states.get(message.chat.id, {}).get('state') == 'admin_price_4_7')
def add_product_price_4_7(message):
    user_states[message.chat.id]['price_4_7'] = message.text
    user_states[message.chat.id]['state'] = 'admin_price_15_22'
    bot.send_message(message.chat.id, "💵 Нархи Под заказ (15-22 рӯз) (ё `-` агар нест):")

@bot.message_handler(func=lambda message: str(message.chat.id) == ADMIN_ID and user_states.get(message.chat.id, {}).get('state') == 'admin_price_15_22')
def add_product_price_15_22(message):
    user_states[message.chat.id]['price_15_22'] = message.text
    d = user_states[message.chat.id]
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO products (category, name, photo_id, price_stock, price_4_7, price_15_22, description) 
                      VALUES (?, ?, ?, ?, ?, ?, ?)''',
                   (d['category'], d['name'], d['photo_id'], d['price_stock'], d['price_4_7'], d['price_15_22'], d['description']))
    conn.commit()
    conn.close()
    bot.send_message(message.chat.id, f"✅ Моли «{d['name']}» ба бахши «{d['category']}» илова шуд!")
    user_states[message.chat.id]['state'] = 'authorized'
    admin_panel(message)

@bot.message_handler(func=lambda message: str(message.chat.id) == ADMIN_ID and message.text == "📋 Рӯйхати молҳо")
def list_products(message):
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, category, name, price_stock FROM products')
    rows = cursor.fetchall()
    conn.close()
    if not rows:
        bot.send_message(message.chat.id, "Ҳоло молҳо нест.")
        return
    text = "📋 <b>Рӯйхати молҳо:</b>\n\n"
    for r in rows:
        text += f"#{r[0]} | {r[1]} | {r[2]} | {r[3]}с\n"
    bot.send_message(message.chat.id, text, parse_mode='HTML')

@bot.message_handler(func=lambda message: str(message.chat.id) == ADMIN_ID and message.text == "🗑 Нест кардани мол")
def delete_product_prompt(message):
    bot.send_message(message.chat.id, "Рақами молро нависед (мисол: 1):")
    user_states[message.chat.id] = {'state': 'admin_delete'}

@bot.message_handler(func=lambda message: str(message.chat.id) == ADMIN_ID and user_states.get(message.chat.id, {}).get('state') == 'admin_delete')
def delete_product(message):
    try:
        pid = int(message.text)
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM products WHERE id = ?', (pid,))
        conn.commit()
        conn.close()
        bot.send_message(message.chat.id, f"✅ Моли #{pid} нест карда шуд.")
    except:
        bot.send_message(message.chat.id, "Хато. Рақамро нависед.")
    user_states[message.chat.id]['state'] = 'authorized'
    admin_panel(message)

@bot.message_handler(func=lambda message: str(message.chat.id) == ADMIN_ID and message.text == "⬅️ Бозгашт ба меню")
def back_to_menu_admin(message):
    user_states[message.chat.id]['state'] = 'authorized'
    gender = user_states.get(message.chat.id, {}).get('gender', 'boy')
    show_main_menu(message.chat.id, gender)

# ============ КОРКАРДИ МОЛҲО ============
def show_products_page(chat_id, category, page):
    items_per_page = 5
    offset = (page - 1) * items_per_page
    
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM products WHERE category = ?', (category,))
    total_items = cursor.fetchone()[0]
    cursor.execute('SELECT id, name, price_stock FROM products WHERE category = ? LIMIT ? OFFSET ?', 
                   (category, items_per_page, offset))
    products = cursor.fetchall()
    conn.close()
    
    if total_items == 0:
        bot.send_message(chat_id, "🌿 Дар ин бахш ҳоло молҳо нест. Ба зудӣ илова мешаванд.")
        return
    total_pages = (total_items + items_per_page - 1) // items_per_page
    markup = types.InlineKeyboardMarkup(row_width=1)
    for p in products:
        markup.add(types.InlineKeyboardButton(f"{p[1]} - {p[2]}с", callback_data=f"view_{p[0]}"))
    nav_buttons = []
    if page > 1:
        nav_buttons.append(types.InlineKeyboardButton("⬅️ Қаблӣ", callback_data=f"page_{page-1}"))
    if page < total_pages:
        nav_buttons.append(types.InlineKeyboardButton("Баъдӣ ➡️", callback_data=f"page_{page+1}"))
    if nav_buttons:
        markup.row(*nav_buttons)
    bot.send_message(chat_id, f"📁 <b>{category}</b>\nСаҳифаи {page} аз {total_pages}\n\nЛутфан, моли дилхоҳро интихоб кунед:", reply_markup=markup, parse_mode='HTML')

@bot.message_handler(func=lambda message: user_states.get(message.chat.id, {}).get('state') == 'authorized')
def handle_menu(message):
    text = message.text
    if "Сумкаҳо" in text or "Косметика" in text or "Дигар" in text or "Табиӣ" in text or "Либос" in text or "Пойафзол" in text:
        user_states[message.chat.id]['current_cat'] = text
        user_states[message.chat.id]['current_page'] = 1
        show_products_page(message.chat.id, text, 1)
    elif "Рейтинг" in text:
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()
        cursor.execute('SELECT name, total_sales FROM sellers ORDER BY total_sales DESC LIMIT 5')
        top = cursor.fetchall()
        conn.close()
        if top:
            t = "🏆 <b>ТОП-5 ФУРӮШАНДАГОН</b>\n\n"
            for i, (n, s) in enumerate(top, 1):
                t += f"{i}. <b>{n}</b> — {s} фурӯш\n"
            bot.send_message(message.chat.id, t, parse_mode='HTML')
        else:
            bot.send_message(message.chat.id, "Рейтинг холӣ аст.")
    elif "Ҳисоби ман" in text:
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()
        cursor.execute('SELECT total_orders, total_sales, total_earned, name FROM sellers WHERE user_id = ?', (message.chat.id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            o, s, e, n = row
            rank = "🥇 Тилоӣ" if e >= 1000 else "🥈 Нуқраӣ" if e >= 500 else "🥉 Биринҷӣ"
            bot.send_message(message.chat.id, 
                f"👑 <b>КАБИНЕТИ ФУРӮШАНДА</b>\n➖➖➖➖➖\n👤 {n}\n🏆 {rank}\n📦 Фармоиш: {o}\n🛍 Фурӯш: {s}\n💰 Комиссия: {e}с", 
                parse_mode='HTML')
        else:
            bot.send_message(message.chat.id, "Ҳисоб холӣ аст.")
    elif "Тамос" in text:
        bot.send_message(message.chat.id, "📞 Телефон: +992 02-332-19-19\nTelegram: @Rustamzoda6789")

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
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name, photo_id, price_stock, price_4_7, price_15_22, description FROM products WHERE id = ?', (pid,))
    p = cursor.fetchone()
    conn.close()
    
    if not p:
        bot.answer_callback_query(call.id, "Мол нест карда шуд!")
        return
        
    pname, photo_id, p_stock, p_4_7, p_15_22, p_desc = p
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    if p_stock and p_stock != '-':
        markup.add(types.InlineKeyboardButton(f"🟢 Наличи - {p_stock}с", callback_data=f"order_{pid}_stock"))
    if p_4_7 and p_4_7 != '-':
        markup.add(types.InlineKeyboardButton(f"🟡 4-7 рӯз - {p_4_7}с", callback_data=f"order_{pid}_4_7"))
    if p_15_22 and p_15_22 != '-':
        markup.add(types.InlineKeyboardButton(f"🔴 15-22 рӯз - {p_15_22}с", callback_data=f"order_{pid}_15_22"))

    caption = f"📦 <b>{pname}</b>"
    if p_desc and p_desc != '-':
        caption += f"\n\n📝 {p_desc}"
    
    try:
        bot.send_photo(call.message.chat.id, photo_id, caption=caption, reply_markup=markup, parse_mode='HTML')
    except Exception as e:
        bot.send_message(call.message.chat.id, caption + "\n\n(Акс ҳозир дастрас нест)", reply_markup=markup, parse_mode='HTML')
    
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('order_'))
def handle_order_type(call):
    _, pid, otype = call.data.split('_', 2)
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name, price_stock, price_4_7, price_15_22 FROM products WHERE id = ?', (pid,))
    p = cursor.fetchone()
    conn.close()
    
    if not p:
        bot.answer_callback_query(call.id, "Мол нест карда шуд!")
        return
    
    if otype == 'stock':
        ttext, price = "🟢 Наличи (Тайёр)", p[1]
    elif otype == '4_7':
        ttext, price = "🟡 4-7 рӯз", p[2]
    else:
        ttext, price = "🔴 15-22 рӯз", p[3]
    
    user_states[call.message.chat.id] = {'state': 'waiting_order_details', 'product': p[0], 'order_type': ttext, 'price': price}
    bot.send_message(call.message.chat.id, f"📦 {p[0]}\n📋 {ttext}\n💵 {price}с\n\nРанг, андоза, миқдорро нависед:")
    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda message: user_states.get(message.chat.id, {}).get('state') == 'waiting_order_details')
def handle_order_details(message):
    d = user_states[message.chat.id]
    try:
        bot.send_message(ADMIN_ID, 
            f"🛍️ <b>ФАРМОИШИ НАВ!</b>\n\n👤 {message.from_user.first_name} (ID: {message.chat.id})\n📦 {d['product']}\n📋 {d['order_type']}\n💵 {d['price']}с\n🎨 {message.text}",
            parse_mode='HTML')
        bot.send_message(message
