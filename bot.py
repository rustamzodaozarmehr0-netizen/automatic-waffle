import telebot
from flask import Flask
from threading import Thread
from telebot import types
import sqlite3

TOKEN = '8944741788:AAE27y2JQD4NZrQN20e1YSe7pjAeikpthG4'
ADMIN_ID = '6367413561' # ID-и худатро нависед!

VALID_CODES = {
    "54821": "girl",
    "93712": "girl",
    "10493": "girl",
    "73920": "boy",
    "58203": "boy",
    "91045": "boy",
    "50821": "girl",
    "96712": "girl",
    "14593": "girl",
    "78320": "boy",
    "59203": "boy",
    "98445": "boy"
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
            name TEXT,
            phone TEXT,
            gender TEXT,
            total_sales INTEGER DEFAULT 0,
            total_orders INTEGER DEFAULT 0,
            total_earned REAL DEFAULT 0.0
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
    
    admin_msg = f"🛍️ ДАРХОСТИ НАВ!\n\n👤 Ном: {name}\n📱 Рақам: {phone}\n\nБарои қабул, ба ӯ яке аз кодҳоро диҳед."
    try:
        bot.send_message(ADMIN_ID, admin_msg)
    except Exception as e:
        print(f"Хато: {e}")
        
    bot.send_message(message.chat.id, "Ташаккур! Дархост қабул шуд. Интизор шавед, ба зудӣ код мегиред.\n\nЛутфан, коди худро ворид кунед:")

def show_main_menu(chat_id, gender):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    if gender == "girl":
        btn1 = types.KeyboardButton("👗 Либосҳои занона")
        btn2 = types.KeyboardButton("👟 Пойафзоли занона")
        btn3 = types.KeyboardButton("👜 Сумкаҳо")
        btn4 = types.KeyboardButton("💄 Косметика")
    else:
        btn1 = types.KeyboardButton("👕 Либосҳои мардона")
        btn2 = types.KeyboardButton("👞 Пойафзоли мардона")
        btn3 = types.KeyboardButton("🎒 Сумкаҳо")
        btn4 = types.KeyboardButton("🧴 Дигар чизҳо")
        
    btn_med = types.KeyboardButton("🌿 Табиӣ ва Дору")
    btn_stats = types.KeyboardButton("📊 Ҳисоби ман")
    btn_rating = types.KeyboardButton("🏆 Рейтинг")
    btn_contact = types.KeyboardButton("📞 Тамос бо мо")
    
    markup.add(btn1, btn2, btn3, btn4, btn_med, btn_stats, btn_rating, btn_contact)
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
        bot.send_message(message.chat.id, "❌ Код хато аст ё вуҷуд надорад! Аз нав кӯшиш кунед.")

# --- Коркарди интихоби ҳолати мол (Inline тугмаҳо) ---
@bot.callback_query_handler(func=lambda call: call.data.startswith('order_'))
def handle_order_type(call):
    _, product, order_type = call.data.split('_', 2)
    
    if order_type == 'stock':
        type_text = "🟢 Наличи (Тайёр)"
    elif order_type == '4_7':
        type_text = "🟡 Под заказ (4-7 рӯз)"
    else:
        type_text = "🔴 Под заказ (15-22 рӯз)"
        
    user_states[call.message.chat.id] = {
        'state': 'waiting_order_details',
        'product': product,
        'order_type': type_text
    }
    bot.send_message(call.message.chat.id, f"📦 Мол: {product}\nҲолат: {type_text}\n\nЛутфан, ранг, андоза ва миқдорро нависед (мисол: Сиёҳ, L, 2 дона):")
    bot.answer_callback_query(call.id)

# --- Қабули маълумоти фармоиш ---
@bot.message_handler(func=lambda message: user_states.get(message.chat.id, {}).get('state') == 'waiting_order_details')
def handle_order_details(message):
    details = message.text
    product = user_states[message.chat.id]['product']
    order_type = user_states[message.chat.id]['order_type']
    
    admin_msg = f"🛍️ ФАРМОИШИ НАВ!\n\n👤 Фурӯшанда: {message.from_user.first_name} (ID: {message.chat.id})\n📦 Мол: {product}\n📋 Ҳолат: {order_type}\n🎨 Ранг/Андоза/Миқдор: {details}"
    try:
        bot.send_message(ADMIN_ID, admin_msg)
        bot.send_message(message.chat.id, "✅ Фармоиши шумо ба админ равон карда шуд. Ба зудӣ бо шумо тамос мегиранд.")
    except Exception as e:
        bot.send_message(message.chat.id, "Хато дар фиристодан. Аз нав кӯшиш кунед.")
        
    user_states[message.chat.id]['state'] = 'authorized' 

# --- Коркарди меню ---
@bot.message_handler(func=lambda message: user_states.get(message.chat.id, {}).get('state') == 'authorized')
def handle_menu(message):
    text = message.text
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    # Тугмаҳои инлайн барои ҳолати мол
    if "Либосҳои мардона" in text or "Либосҳои занона" in text or "Пойафзол" in text:
        # Барои намуна, мо танҳо як молро нишон медиҳем
        product_name = "Куртаи зебо"
        markup.add(
            types.InlineKeyboardButton("🟢 Наличи (Тайёр) - 150с", callback_data=f"order_{product_name}_stock"),
            types.InlineKeyboardButton("🟡 Под заказ (4-7 рӯз) - 180с", callback_data=f"order_{product_name}_4_7"),
            types.InlineKeyboardButton("🔴 Под заказ (15-22 рӯз) - 130с", callback_data=f"order_{product_name}_15_22")
        )
        bot.send_message(message.chat.id, f"👕 {product_name}\n\nЛутфан, ҳолати молро интихоб кунед:", reply_markup=markup)
        
    elif "Сумкаҳо" in text:
        bot.send_message(message.chat.id, "🎒 Сумкаҳо\n\n(Дар ин ҷо аксҳо ва нархҳо илова мешаванд)")
    elif "Косметика" in text or "Дигар" in text or "Табиӣ" in text:
        bot.send_message(message.chat.id, "🌿 Табиӣ ва Дору\n\n(Дар ин ҷо чизҳои табиӣ ва доруворӣ илова мешаванд)")
        
    # 🏆 РЕЙТИНГ (Амнияти пурра!)
    elif "Рейтинг" in text:
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()
        cursor.execute('SELECT name, total_sales FROM sellers ORDER BY total_sales DESC LIMIT 5')
        top_sellers = cursor.fetchall()
        conn.close()
        
        if top_sellers:
            text_rating = "🏆 <b>ТОП-5 ФУРӮШАНДАГОНИ МО</b> 🏆\n➖➖➖➖➖➖➖➖➖➖\n"
            for i, (name, sales) in enumerate(top_sellers, 1):
                text_rating += f"{i}. <b>{name}</b> — {sales} фурӯш\n"
            text_rating += "➖➖➖➖➖➖➖➖➖➖\n<i>Барои ба ҷои аввал баромадан бештар фурӯшед!</i>"
            bot.send_message(message.chat.id, text_rating, parse_mode='HTML')
        else:
            bot.send_message(message.chat.id, "Ҳоло рейтинг холӣ аст.")
        
    # 📊 ҲИСОБИ МАН
    elif "Ҳисоби ман" in text:
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()
        cursor.execute('SELECT total_orders, total_sales, total_earned, name FROM sellers WHERE user_id = ?', (message.chat.id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            orders, sales, earned, name = row
            if earned >= 1000:
                rank = "🥇 Тилоӣ (VIP)"
            elif earned >= 500:
                rank = "🥈 Нуқраӣ (Pro)"
            else:
                rank = "🥉 Биринҷӣ (Start)"
                
            stats_text = (
                f"👑 <b>КАБИНЕТИ ФУРӮШАНДА</b> 👑\n"
                f"➖➖➖➖➖➖➖➖➖➖\n"
                f"👤 Фурӯшанда: <b>{name}</b>\n"
                f"🏆 Рутбаи шумо: <b>{rank}</b>\n"
                f"➖➖➖➖➖➖➖➖➖➖\n"
                f"📦 Фармоишҳои қабулшуда: <b>{orders}</b>\n"
                f"🛍 Молҳои фурӯхташуда: <b>{sales} дона</b>\n"
                f"💰 Маблағи коркарда: <b>{earned} сомонӣ</b>\n"
                f"➖➖➖➖➖➖➖➖➖➖\n"
                f"<i>Барои баланд бардоштани рутба бештар фурӯш кунед!</i>"
            )
            bot.send_message(message.chat.id, stats_text, parse_mode='HTML')
        else:
            bot.send_message(message.chat.id, "Ҳисоби шумо ҳоло холӣ аст.")
            
    elif "Тамос" in text:
        bot.send_message(message.chat.id, "📞 Барои тамос:\n\nТелефон: +992 XX XXX XX XX\nTelegram: @flstyle_admin")

# Дастури махсус барои илова кардани фурӯш
@bot.message_handler(commands=['add_sale'])
def admin_add_sale(message):
    if str(message.chat.id) == ADMIN_ID:
        try:
            args = message.text.split()
            seller_id = int(args[1])
            commission = float(args[2]) 
            
            conn = sqlite3.connect('shop.db')
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE sellers 
                SET total_orders = total_orders + 1, 
                    total_sales = total_sales + 1, 
                    total_earned = total_earned + ? 
                WHERE user_id = ?
            ''', (commission, seller_id))
            conn.commit()
            conn.close()
            bot.reply_to(message, f"✅ Фурӯш барои корбар {seller_id} сабт шуд. Комиссия: {commission} сомонӣ.")
        except Exception as e:
            bot.reply_to(message, f"Хато. Намунаи дуруст:\n`/add_sale 123456789 50`", parse_mode='Markdown')

def run_bot():
    bot.polling(none_stop=True)

if __name__ == '__main__':
    t = Thread(target=run_bot)
    t.start()
    app.run(host='0.0.0.0', port=8080)
