import telebot
from flask import Flask
from threading import Thread
from telebot import types
import sqlite3

TOKEN = '8944741788:AAE27y2JQD4NZrQN20e1YSe7pjAeikpthG4'
ADMIN_ID = '6367413561' # ID-и худатро нависед!

VALID_CODES = {
    "548271": "girl",
    "939712": "girl",
    "548283": "girl"
‎    "73920": "boy",
‎    "58203": "boy",
‎    "54112": "girl",
‎    "93111": "girl",
‎    "73113": "boy",
‎    "58114": "boy",
‎    "54115": "girl",
‎    "93116": "girl",
‎    "10020": "boy",
‎    "83703": "boy",
‎    "50021": "girl",
‎    "22122": "girl",
‎    "10101": "boy",
‎    "63846": "boy",
‎    "44543": "girl",
‎    "2077": "girl",
‎    "6777": "boy",
‎    "63947": "boy"
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
            category TEXT,
            name TEXT,
            photo_id TEXT,
            price_stock TEXT,
            price_4_7 TEXT,
            price_15_22 TEXT
        )
    ''')
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
    else:
        markup.add(types.KeyboardButton("👕 Либосҳои мардона"), types.KeyboardButton("👞 Пойафзоли мардона"),
                   types.KeyboardButton("🎒 Сумкаҳо"), types.KeyboardButton("🧴 Дигар чизҳо"))
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
@bot.message_handler(commands=['admin', '+'])
def admin_panel(message):
    if str(message.chat.id) != ADMIN_ID:
        return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(types.KeyboardButton("➕ Иловаи моли нав"), types.KeyboardButton("📋 Рӯйхати молҳо"))
    markup.add(types.KeyboardButton("🗑 Нест кардани мол"), types.KeyboardButton("⬅️ Бозгашт"))
    bot.send_message(message.chat.id, "👑 ПАНЕЛИ АДМИН\n\nЛутфан, амалро интихоб кунед:", reply_markup=markup)

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
    bot.send_message(message.chat.id, "📝 Номи молро нависед (танҳо ном, на нарх):")

@bot.message_handler(func=lambda message: str(message.chat.id) == ADMIN_ID and user_states.get(message.chat.id, {}).get('state') == 'admin_name')
def add_product_name(message):
    user_states[message.chat.id]['name'] = message.text
    user_states[message.chat.id]['state'] = 'admin_price_stock'
    bot.send_message(message.chat.id, "💵 Нархи Наличи (Тайёр) бо сомонӣ:")

@bot.message_handler(func=lambda message: str(message.chat.id) == ADMIN_ID and user_states.get(message.chat.id, {}).get('state') == 'admin_price_stock')
def add_product_price_stock(message):
    user_states[message.chat.id]['price_stock'] = message.text
    user_states[message.chat.id]['state'] = 'admin_price_4_7'
    bot.send_message(message.chat.id, "💵 Нархи Под заказ (4-7 рӯз):")

@bot.message_handler(func=lambda message: str(message.chat.id) == ADMIN_ID and user_states.get(message.chat.id, {}).get('state') == 'admin_price_4_7')
def add_product_price_4_7(message):
    user_states[message.chat.id]['price_4_7'] = message.text
    user_states[message.chat.id]['state'] = 'admin_price_15_22'
    bot.send_message(message.chat.id, "💵 Нархи Под заказ (15-22 рӯз):")

@bot.message_handler(func=lambda message: str(message.chat.id) == ADMIN_ID and user_states.get(message.chat.id, {}).get('state') == 'admin_price_15_22')
def add_product_price_15_22(message):
    user_states[message.chat.id]['price_15_22'] = message.text
    d = user_states[message.chat.id]
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO products (category, name, photo_id, price_stock, price_4_7, price_15_22) 
                      VALUES (?, ?, ?, ?, ?, ?)''',
                   (d['category'], d['name'], d['photo_id'], d['price_stock'], d['price_4_7'], d['price_15_22']))
    conn.commit()
    conn.close()
    bot.send_message(message.chat.id, f"✅ Моли «{d['name']}» ба бахши «{d['category']}» илова шуд!")
    user_states[message.chat.id]['state'] = 'authorized'
    admin_panel(message) # Баргашт ба менюи админ

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

@bot.message_handler(func=lambda message: str(message.chat.id) == ADMIN_ID and message.text == "⬅️ Бозгашт")
def back_to_menu(message):
    user_states[message.chat.id]['state'] = 'authorized'
    gender = user_states.get(message.chat.id, {}).get('gender', 'boy')
    show_main_menu(message.chat.id, gender)

# ============ КОРКАРДИ МОЛҲО ============
@bot.message_handler(func=lambda message: user_states.get(message.chat.id, {}).get('state') == 'authorized')
def handle_menu(message):
    text = message.text
    
    if "Сумкаҳо" in text or "Косметика" in text or "Дигар" in text or "Табиӣ" in text or "Либос" in text or "Пойафзол" in text:
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, photo_id, price_stock FROM products WHERE category = ?', (text,))
        products = cursor.fetchall()
        conn.close()
        
        if not products:
            bot.send_message(message.chat.id, "🌿 Дар ин бахш ҳоло молҳо нест. Ба зудӣ илова мешаванд.")
            return
        
        for p in products:
            pid, pname, photo_id, price = p
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(
                types.InlineKeyboardButton(f"🟢 Наличи - {price}с", callback_data=f"order_{pid}_stock"),
                types.InlineKeyboardButton(f"🟡 4-7 рӯз", callback_data=f"order_{pid}_4_7"),
                types.InlineKeyboardButton(f"🔴 15-22 рӯз", callback_data=f"order_{pid}_15_22")
            )
            try:
                # Қоидаи бехатарӣ: кӯшиши фиристодани акс
                bot.send_photo(message.chat.id, photo_id, caption=f"📦 <b>{pname}</b>", reply_markup=markup, parse_mode='HTML')
            except Exception as e:
                # Агар акс хато диҳад, танҳо матнро мефиристад
                print(f"Хато дар акс: {e}")
                bot.send_message(message.chat.id, f"📦 <b>{pname}</b>\n💵 Нархи Наличи: {price}с\n\n(Акс ҳозир дастрас нест, аммо шумо метавонед фармоиш диҳед)", reply_markup=markup, parse_mode='HTML')
        
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
        bot.send_message(message.chat.id, "✅ Фармоиш ба админ равон шуд!")
    except:
        bot.send_message(message.chat.id, "Хато. Аз нав кӯшиш кунед.")
    d['state'] = 'authorized'

@bot.message_handler(commands=['add_sale'])
def admin_add_sale(message):
    if str(message.chat.id) == ADMIN_ID:
        try:
            args = message.text.split()
            sid, comm = int(args[1]), float(args[2])
            conn = sqlite3.connect('shop.db')
            cursor = conn.cursor()
            cursor.execute('UPDATE sellers SET total_orders = total_orders + 1, total_sales = total_sales + 1, total_earned = total_earned + ? WHERE user_id = ?', (comm, sid))
            conn.commit()
            conn.close()
            bot.reply_to(message, f"✅ Фурӯш барои {sid} сабт шуд. Комиссия: {comm}с")
        except:
            bot.reply_to(message, "Хато. Мисол: /add_sale 123456789 50")

def run_bot():
    bot.polling(none_stop=True)

if __name__ == '__main__':
    t = Thread(target=run_bot)
    t.start()
    app.run(host='0.0.0.0', port=8080)
